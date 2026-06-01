"""Receipt-to-Cashback — Streamlit MVP.

Wraps the day 1–5 spine (OCR → LLM → FAISS → CashbackEngine) into a
two-page web app:

* **Upload Receipt** — the actual product flow.
* **About this project** — a short, non-technical description plus a
  link to the simple-explanation log for the demo audience.

Run locally with:

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

from src.cashback_engine import (
    CashbackEngine,
    CashbackResult,
    FlatStrategy,
    PerSkuStrategy,
)
from src.llm_extractor import LLMExtractionError, LLMExtractor, ReceiptExtraction
from src.matcher import MatchedLineItem, match_extraction
from src.ocr_pipeline import OCRPipeline
from src.vector_store import CatalogIndex


# ----- expensive resources loaded once per session -------------------------


@st.cache_resource(show_spinner="Loading OCR model… (first time only)")
def get_ocr() -> OCRPipeline:
    return OCRPipeline()


@st.cache_resource(show_spinner="Connecting to Gemini…")
def get_llm() -> LLMExtractor:
    return LLMExtractor()


@st.cache_resource(show_spinner="Embedding catalog into FAISS…")
def get_index() -> CatalogIndex:
    return CatalogIndex.from_csv(ROOT / "data" / "catalog.csv")


@st.cache_resource(show_spinner="Loading sample CORD receipts…")
def get_sample_receipts() -> list[Image.Image]:
    """Pull a handful of CORD-v2 receipts so the demo works without an upload."""
    from datasets import load_dataset

    ds = load_dataset("naver-clova-ix/cord-v2", split="train")
    return [ds[i]["image"] for i in (0, 7, 50)]


# ----- pipeline runner ------------------------------------------------------


def run_spine(image: Image.Image, strategy_name: str) -> tuple[
    str,
    ReceiptExtraction,
    list[MatchedLineItem],
    CashbackResult,
]:
    ocr = get_ocr()
    llm = get_llm()
    index = get_index()
    strategy = (
        FlatStrategy(flat_rate=0.04) if strategy_name == "Flat 4%" else PerSkuStrategy()
    )
    engine = CashbackEngine(strategy)

    progress = st.progress(0, text="Running OCR…")
    ocr_text = ocr.read_text(image)

    progress.progress(40, text="Asking Gemini to structure items…")
    extraction = llm.extract(ocr_text)

    progress.progress(80, text="Matching items against catalog (FAISS)…")
    matched = match_extraction(extraction, index)

    progress.progress(95, text="Computing cashback…")
    result = engine.compute(matched)
    progress.progress(100, text="Done.")
    progress.empty()

    return ocr_text, extraction, matched, result


# ----- pages ----------------------------------------------------------------


def page_upload() -> None:
    st.title("Receipt-to-Cashback")
    st.caption(
        "Upload a receipt photo. We'll OCR it, parse it with Gemini, match "
        "items against our 110-SKU catalog, and tell you how much cashback "
        "you earned. Built as the Capstone project for the Developers "
        "Institute GenAI & ML bootcamp 2026."
    )

    with st.sidebar:
        st.subheader("Settings")
        strategy = st.radio(
            "Cashback strategy",
            ["Per-SKU rates", "Flat 4%"],
            help=(
                "Per-SKU uses the per-product rate stored in the catalog "
                "(0–5%). Flat 4% gives a uniform 4% on every accepted item."
            ),
        )
        st.divider()
        st.subheader("Try a sample receipt")
        st.caption(
            "If you don't have a receipt photo handy, pick one from the "
            "public CORD-v2 dataset."
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
            ocr_text, extraction, matched, result = run_spine(image, strategy)
        except LLMExtractionError as exc:
            st.error(
                "We couldn't reliably structure this receipt. The text the "
                "OCR returned may be too noisy, or the model is being "
                "unusually creative today. Try a different photo."
            )
            with st.expander("Technical detail"):
                st.code(str(exc))
            return

        st.metric(
            label=f"Cashback (strategy: {result.strategy})",
            value=f"{result.total_cashback:,.2f} {extraction.currency or ''}".strip(),
            delta=f"{result.effective_rate:.1%} effective rate",
        )
        st.caption(
            f"Total spend: {result.total_spend:,.2f} "
            f"{extraction.currency or ''}".strip()
            + (f"  ·  Merchant: {extraction.merchant}" if extraction.merchant else "")
            + (f"  ·  Date: {extraction.date}" if extraction.date else "")
        )

        st.markdown("**Line-by-line breakdown**")
        st.dataframe(
            [
                {
                    "Item (from receipt)": ln.item_name,
                    "Matched SKU": ln.matched_sku,
                    "Spend": round(ln.line_total, 2),
                    "Rate": f"{ln.rate * 100:.1f}%",
                    "Cashback": round(ln.cashback, 2),
                    "Accepted": "yes" if ln.accepted else "no",
                }
                for ln in result.lines
            ],
            hide_index=True,
            use_container_width=True,
        )

        with st.expander("Show raw OCR text"):
            st.code(ocr_text)
        with st.expander("Show Gemini extraction JSON"):
            st.json(extraction.model_dump())


def page_about() -> None:
    st.title("About this project")
    st.markdown(
        """
**Receipt-to-Cashback** is the Capstone project for the Developers Institute
**GenAI & Machine Learning Bootcamp 2026**.

The app demonstrates a full GenAI pipeline applied to a real-world product
idea — turning a receipt photo into a structured cashback reward — using
nothing but pre-trained models stitched together with a small amount of
business logic.

**Pipeline (in plain English):**

1. **OCR** — read the text out of the receipt image (EasyOCR).
2. **Structuring** — ask Gemini 2.5 Flash to turn that text into a clean
   list of items, prices and totals, validated against a strict schema.
3. **Matching** — embed each item with sentence-transformers and find
   the closest product in our 110-SKU catalog using FAISS.
4. **Cashback** — apply category-aware reward rules and show the result.

The full daily build log, in non-technical language, lives in
[`docs/00_simple_explanation.md`](https://github.com/alexgl77/receipt-to-cashback/blob/main/docs/00_simple_explanation.md).

**Source:** https://github.com/alexgl77/receipt-to-cashback
"""
    )


# ----- main -----------------------------------------------------------------


def main() -> None:
    st.set_page_config(
        page_title="Receipt-to-Cashback",
        page_icon=None,
        layout="wide",
    )
    page = st.sidebar.radio("Navigation", ["Upload Receipt", "About this project"])
    if page == "Upload Receipt":
        page_upload()
    else:
        page_about()


if __name__ == "__main__":
    main()
