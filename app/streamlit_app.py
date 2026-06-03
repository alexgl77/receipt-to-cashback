"""Receipt-to-Cashback — Streamlit MVP.

Wraps the OCR -> LLM -> FAISS -> CashbackEngine spine into a two-page
web app. Business model exposed in the UI: market-research data
acquisition (flat cashback per receipt, value extracted from the data
itself).

Run locally:
    streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import sys
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image

# Make sibling `src/` importable when Streamlit launches us as a script.
APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

import streamlit as st

import numpy as np
import pandas as pd

from src.analytics import CATEGORY_COLS, ab_test, cluster_users
from src.cashback_engine import (
    CashbackEngine,
    CashbackResult,
    FlatStrategy,
    TieredStrategy,
)
from src.llm_extractor import LLMExtractionError, LLMExtractor, ReceiptExtraction
from src.matcher import MatchedLineItem, match_extraction
from src.ocr_pipeline import OCRPipeline
from src.synthetic_users import ARCHETYPES, generate_users
from src.vector_store import CatalogIndex


# ----- expensive resources loaded once per session -------------------------


@st.cache_resource(show_spinner="Loading OCR model… (first time only)")
def get_ocr() -> OCRPipeline:
    return OCRPipeline()


@st.cache_resource(show_spinner="Connecting to Gemini…")
def get_llm() -> LLMExtractor:
    return LLMExtractor()


@st.cache_resource(show_spinner="Embedding catalog into FAISS (multilingual)…")
def get_index() -> CatalogIndex:
    return CatalogIndex.from_csv(ROOT / "data" / "catalog.csv")


@st.cache_resource(show_spinner="Loading sample CORD receipts…")
def get_sample_receipts() -> list[Image.Image]:
    """Pull a handful of CORD-v2 receipts so the demo works without an upload."""
    from datasets import load_dataset

    ds = load_dataset("naver-clova-ix/cord-v2", split="train")
    return [ds[i]["image"] for i in (0, 7, 50)]


# ----- pipeline runner ------------------------------------------------------


STRATEGY_CHOICES = {
    "Flat 2% (default)": FlatStrategy(0.02),
    "Flat 3%": FlatStrategy(0.03),
    "Tiered (food 2.5%, bev 2%, misc 0%)": TieredStrategy(),
}


@st.cache_data(show_spinner=False)
def cached_ocr_text(image_bytes: bytes) -> str:
    """Cache OCR by raw image bytes so repeated demo uploads are instant."""
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    return get_ocr().read_text(image)


@st.cache_data(show_spinner=False)
def cached_extraction(ocr_text: str) -> ReceiptExtraction:
    return get_llm().extract(ocr_text)


def run_spine(image: Image.Image, strategy_label: str) -> tuple[
    str,
    ReceiptExtraction,
    list[MatchedLineItem],
    CashbackResult,
]:
    index = get_index()
    engine = CashbackEngine(STRATEGY_CHOICES[strategy_label])

    progress = st.progress(0, text="Running OCR…")
    buf = BytesIO()
    image.save(buf, format="PNG")
    ocr_text = cached_ocr_text(buf.getvalue())

    progress.progress(40, text="Asking Gemini to structure items…")
    extraction = cached_extraction(ocr_text)

    progress.progress(80, text="Matching items against catalog (FAISS)…")
    matched = match_extraction(extraction, index)

    progress.progress(95, text="Computing cashback…")
    result = engine.compute(matched, declared_total=extraction.total)
    progress.progress(100, text="Done.")
    progress.empty()

    return ocr_text, extraction, matched, result


# ----- pages ----------------------------------------------------------------


def page_upload() -> None:
    st.title("Receipt-to-Cashback")
    st.caption(
        "A market-research app: scan a receipt, we pay you flat cashback in "
        "exchange for the itemised consumption data, which we anonymise and "
        "sell in aggregate. Built as the Capstone project for the Developers "
        "Institute GenAI & ML bootcamp 2026."
    )

    with st.sidebar:
        st.subheader("Settings")
        strategy_label = st.radio(
            "Cashback strategy",
            list(STRATEGY_CHOICES.keys()),
            help=(
                "All strategies pay cashback on every priced line — the "
                "catalog only changes the category label, not eligibility. "
                "Tiered strategy uses different rates per category; misc "
                "items (plastic bags, packaging) pay 0% because they have "
                "no data value."
            ),
        )
        st.divider()
        st.subheader("Try a sample receipt")
        st.caption(
            "If you don't have a receipt photo handy, pick one from the "
            "public CORD-v2 dataset (1000 real receipts, Naver Clova 2019)."
        )
        try:
            samples = get_sample_receipts()
        except Exception as exc:  # noqa: BLE001 — surface anything to UI
            samples = []
            st.warning(f"Could not load samples: {exc}")
        sample_choice = st.selectbox(
            "Sample index",
            options=[None, *range(len(samples))],
            format_func=lambda i: "— select —" if i is None else f"CORD sample #{i + 1}",
        )

    uploaded = st.file_uploader(
        "Drop a receipt image here (JPG/PNG)", type=["jpg", "jpeg", "png"]
    )

    image: Image.Image | None = None
    if uploaded is not None:
        image = Image.open(BytesIO(uploaded.read())).convert("RGB")
    elif sample_choice is not None and samples:
        image = samples[sample_choice]

    if image is None:
        st.info("Upload a receipt or pick a sample from the sidebar to start.")
        return

    col_left, col_right = st.columns([1, 1], gap="large")
    with col_left:
        st.image(image, caption="Receipt", use_container_width=True)
    with col_right:
        try:
            ocr_text, extraction, matched, result = run_spine(image, strategy_label)
        except LLMExtractionError as exc:
            st.error(
                "We couldn't reliably structure this receipt. The OCR text "
                "may be too noisy or the model is being unusually creative "
                "today. Try a different photo."
            )
            with st.expander("Technical detail"):
                st.code(str(exc))
            return

        st.metric(
            label=f"Cashback (strategy: {result.strategy})",
            value=f"{result.total_cashback:,.2f} {extraction.currency or ''}".strip(),
            delta=f"{result.effective_rate:.1%} effective rate",
        )
        cat_share = result.categorized_share
        st.caption(
            f"Total spend: {result.total_spend:,.2f} "
            f"{extraction.currency or ''}".strip()
            + f"  ·  Categorised data share: {cat_share:.0%}"
            + (f"  ·  Merchant: {extraction.merchant}" if extraction.merchant else "")
            + (f"  ·  Date: {extraction.date}" if extraction.date else "")
        )
        if result.total_was_corrected:
            st.warning(
                f"**Total-drift guard fired.** The sum of line totals "
                f"({result.line_sum:,.0f} {extraction.currency or ''}) "
                f"disagrees with the receipt's declared grand total "
                f"({result.declared_total:,.0f} {extraction.currency or ''}) "
                f"by {result.drift_pct:+.0%}. To avoid over-paying we "
                f"trust the declared total. The line table below shows "
                f"the unscaled per-line numbers; the cashback metric "
                f"above is scaled to match the grand total."
            )

        st.markdown("**Line-by-line breakdown**")
        st.dataframe(
            [
                {
                    "Item (from receipt)": ln.item_name,
                    "Category": ln.category,
                    "Matched SKU": ln.matched_sku,
                    "Spend": round(ln.line_total, 2),
                    "Rate": f"{ln.rate * 100:.2f}%",
                    "Cashback": round(ln.cashback, 2),
                }
                for ln in result.lines
            ],
            hide_index=True,
            use_container_width=True,
        )
        st.caption(
            "Every priced line earns cashback. Uncategorised lines still pay "
            "out — they are simply less valuable to the data buyer on the "
            "other side."
        )

        with st.expander("Show raw OCR text"):
            st.code(ocr_text)
        with st.expander("Show Gemini extraction JSON"):
            st.json(extraction.model_dump())


@st.cache_data(show_spinner=False)
def get_simulated_users(n_users: int) -> pd.DataFrame:
    return generate_users(n_users=n_users)


def page_b2b() -> None:
    st.title("B2B Analytics")
    st.caption(
        "What our customers (brands, retailers, market-research firms) "
        "see when they buy our data. Built on a synthetic user population "
        "so the demo is reproducible — the same code works on a real "
        "user table."
    )

    with st.sidebar:
        st.subheader("Simulation parameters")
        n_users = st.slider(
            "Synthetic user population", 100, 1000, 400, step=100
        )

    users = get_simulated_users(n_users)

    # Headline numbers ------------------------------------------------------
    total_spend = users["total_spend"].sum()
    total_receipts = users["receipts_per_month"].sum()
    avg_basket = total_spend / total_receipts if total_receipts else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Users", f"{len(users):,}")
    c2.metric("Monthly spend (USD)", f"{total_spend:,.0f}")
    c3.metric("Receipts / month", f"{total_receipts:,}")
    c4.metric("Avg basket", f"{avg_basket:,.2f}")

    # A/B test --------------------------------------------------------------
    st.markdown("### A/B test — does a higher cashback rate buy more data?")
    st.caption(
        "Cohort A is paid 2% cashback, cohort B is paid 3%. Engagement is "
        "measured as receipts uploaded per user per month. Welch's t-test "
        "because the cohorts can have different variances."
    )
    ab = ab_test(users, metric="receipts_per_month")
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Cohort A (2%)", f"{ab.mean_a:.2f}", help="Mean receipts/user/month")
    a2.metric("Cohort B (3%)", f"{ab.mean_b:.2f}", help="Mean receipts/user/month")
    a3.metric("Lift", f"{ab.lift_pct:.1%}",
              delta=f"+{ab.lift_abs:.2f} rec/user/mo")
    a4.metric(
        "p-value",
        f"{ab.p_value:.4f}",
        delta="significant @ α=0.05" if ab.significant_at_05 else "not significant",
        delta_color="normal" if ab.significant_at_05 else "off",
    )
    st.caption(
        "Interpretation: paying 1 extra percentage point of cashback brings "
        f"in {ab.lift_pct:.0%} more data per user. Whether that is worth it "
        "depends on the price per data point our buyers are paying."
    )

    # Clustering ------------------------------------------------------------
    st.markdown("### User segmentation — K-Means on category-spend shares")
    st.caption(
        "Each user is represented by the fraction of their spend in each "
        "of the 6 catalog categories. K-Means groups them into segments "
        "that brands can target. PCA is used only for the 2D plot."
    )
    cluster_n = st.slider("Number of clusters (K)", 2, 6, 4)
    cr = cluster_users(users, n_clusters=cluster_n)

    plot_df = pd.DataFrame({
        "pc1": cr.coords_2d[:, 0],
        "pc2": cr.coords_2d[:, 1],
        "cluster": cr.labels.astype(str),
        "archetype": users["archetype"].values,
    })

    chart_col, table_col = st.columns([1.4, 1], gap="large")
    with chart_col:
        st.scatter_chart(plot_df, x="pc1", y="pc2", color="cluster",
                         height=380)
    with table_col:
        st.markdown("**Cluster centres** (avg USD/month per category)")
        st.dataframe(
            cr.centers_original.round(1),
            hide_index=True, use_container_width=True,
        )

    # Aggregated market view -----------------------------------------------
    st.markdown("### Aggregated market view")
    st.caption(
        "What our data buyers actually pay for: total monthly spend by "
        "category, plus the cluster-level breakdown that lets them target "
        "campaigns."
    )
    cat_totals = users[list(CATEGORY_COLS)].sum().rename(
        lambda c: c.removeprefix("spend_")
    ).sort_values(ascending=False)
    st.bar_chart(cat_totals, height=240)

    with st.expander("Show synthetic user table"):
        st.dataframe(users, use_container_width=True)


def page_ethics() -> None:
    st.title("Ethics")
    st.caption(
        "Under the market-research business model this is the central "
        "section of the project. The full document is in "
        "[`docs/04_ethics.md`](https://github.com/alexgl77/receipt-to-cashback/blob/main/docs/04_ethics.md)."
    )
    ethics_path = ROOT / "docs" / "04_ethics.md"
    if not ethics_path.exists():
        st.warning("Ethics document not found in this deployment.")
        return
    body = ethics_path.read_text(encoding="utf-8")
    # Hide the H1 because Streamlit's st.title already shows one
    if body.startswith("# Ethics"):
        body = body.split("\n", 1)[1]
    st.markdown(body)


def page_about() -> None:
    st.title("About this project")
    st.markdown(
        """
**Receipt-to-Cashback** is the Capstone project for the Developers Institute
**GenAI & Machine Learning Bootcamp 2026**.

### Business model

We are a **market-research data acquisition platform**. Users scan a receipt;
we pay them a flat cashback in exchange for their itemised consumption data,
which we anonymise and sell in aggregate to brands, retailers and research
firms.

The cashback is *the price we pay for the data*, not a partner rebate. That
means:

* **Every priced line earns cashback**, even items we can't classify.
* The catalog exists to **enrich** the data we sell (food / beverage / …),
  not to gate eligibility.
* Higher cashback rates buy us more users — which lets us sell richer data.
  That is the day-7 A/B-test question.

### Pipeline (in plain English)

1. **OCR** — read the text out of the receipt image (EasyOCR).
2. **Structuring** — ask Gemini 2.5 Flash Lite to turn that text into a
   clean list of items, prices and totals, validated against a strict
   Pydantic schema.
3. **Classification** — embed each item with multilingual
   sentence-transformers and find the closest product in our 110-SKU
   catalog using FAISS.
4. **Cashback** — apply the chosen strategy and show the result.

### Ethics

This model lives or dies by **consent, anonymisation and the user's
right to know what is sold**. See
[`docs/04_ethics.md`](https://github.com/alexgl77/receipt-to-cashback/blob/main/docs/04_ethics.md)
for the full discussion.

### Sources

* Full daily build log in plain language:
  [`docs/00_simple_explanation.md`](https://github.com/alexgl77/receipt-to-cashback/blob/main/docs/00_simple_explanation.md)
* Source code: https://github.com/alexgl77/receipt-to-cashback
"""
    )


# ----- main -----------------------------------------------------------------


def main() -> None:
    st.set_page_config(
        page_title="Receipt-to-Cashback",
        page_icon=None,
        layout="wide",
    )
    page = st.sidebar.radio(
        "Navigation",
        ["Upload Receipt", "B2B Analytics", "Ethics", "About this project"],
    )
    if page == "Upload Receipt":
        page_upload()
    elif page == "B2B Analytics":
        page_b2b()
    elif page == "Ethics":
        page_ethics()
    else:
        page_about()


if __name__ == "__main__":
    main()
