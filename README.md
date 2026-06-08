---
title: Receipt-to-Cashback
emoji: "🧾"
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# Receipt-to-Cashback

> A market-research data-acquisition app. A user scans a receipt; we pay flat cashback in exchange for the itemised consumption data, which is anonymised, classified and (in the business model) sold in aggregate to brands, retailers and research firms.

**Author:** Alex Goldbaum
**Bootcamp:** GenAI & Machine Learning 2026 — Developers Institute (Capstone Project)
**Demo Day:** 2026-06-11

[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org)
[![Framework](https://img.shields.io/badge/framework-streamlit-FF4B4B.svg)](https://streamlit.io)
[![LLM](https://img.shields.io/badge/LLM-Gemini%202.5%20Flash%20Lite-4285F4.svg)](https://ai.google.dev)
[![Tests](https://img.shields.io/badge/tests-7%20passing-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Live demo

- **Deployed app:** https://alexgl77-receipt-to-cashback.hf.space
- **Demo video (2:53):** https://www.loom.com/share/b10268c4694f4a8f8cf5e7292aef7a21
- **Source code:** https://github.com/alexgl77/receipt-to-cashback

---

## What this project does (one paragraph)

A user takes a picture of a paper receipt and uploads it to a Streamlit app. **EasyOCR** (CRAFT detector + CRNN recogniser) extracts the raw text. **Gemini 2.5 Flash Lite**, prompted with few-shot examples and constrained by a strict Pydantic schema, turns that text into a clean list of items, prices, currency and total. Each item is then embedded with a **multilingual sentence-transformer** (`paraphrase-multilingual-MiniLM-L12-v2`) and matched against a 110-SKU F&B catalog using **FAISS** — the catalog **classifies** the spend (food / beverage / bakery / …) so the data we hold is enriched, but every priced line earns cashback regardless of whether it classifies. A small OOP `CashbackEngine` applies a flat or tiered strategy and returns the amount. A separate **B2B Analytics** page shows aggregated views over a synthetic 400-user population — **K-Means clustering** of users by spend pattern and a **Welch's t-test A/B-simulation** of two cashback rates. An **Ethics** page surfaces the central design risks. Dataset: **CORD-v2** (public, 1000 annotated receipts, Naver Clova 2019).

---

## The pipeline

```
              ┌──────────────────────┐
              │  user uploads photo  │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  EasyOCR             │   raw text, top-to-bottom
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Gemini 2.5 Flash    │   few-shot + Pydantic schema
              │  Lite extractor      │   → ReceiptExtraction
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  FAISS (multilingual │   each item → catalog SKU
              │  embeddings)         │   → MatchedLineItem[]
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  CashbackEngine      │   strategy pattern
              │  (FlatStrategy /     │   → CashbackResult
              │   TieredStrategy)    │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Streamlit UI        │
              └──────────────────────┘
```

Full architectural rationale: [`docs/02_architecture.md`](docs/02_architecture.md).

---

## How brief requirements map to the project

| Brief requirement | Where it's covered |
|---|---|
| Python with OOP, functions, loops | [`src/`](src/) — `OCRPipeline`, `LLMExtractor`, `CatalogIndex`, `CashbackEngine` |
| Data wrangling (pandas / matplotlib / seaborn) | [`notebooks/01_eda.ipynb`](notebooks/01_eda.ipynb), [`notebooks/07_clustering_ab.ipynb`](notebooks/07_clustering_ab.ipynb) |
| Classification (supervised ML) | [`src/cashback_engine.py`](src/cashback_engine.py) `accepted` flag; LogReg validity classifier (optional, day 7+ buffer) |
| Clustering (unsupervised) | [`src/analytics.py`](src/analytics.py) `cluster_users` (K-Means, K=4) |
| A/B testing / stats | [`src/analytics.py`](src/analytics.py) `ab_test` (Welch's t-test) |
| Deep learning (CNN) | MobileNetV2 transfer learning, optional quality gate (day 8+ buffer) |
| NLP — tokenisation, vectorisation | OCR text preprocessing, sentence-transformer embeddings |
| Pre-trained model | Gemini 2.5 Flash Lite (extraction) + multilingual sentence-transformer (matching) + EasyOCR (text) |
| Vector DB | [`src/vector_store.py`](src/vector_store.py) — FAISS IndexFlatIP over 110-SKU catalog |
| Prompt engineering | [`src/llm_extractor.py`](src/llm_extractor.py) — few-shot prompts + strict Pydantic schema + retry path |
| Accessible interface | [`app/streamlit_app.py`](app/streamlit_app.py) — 4-page Streamlit app |
| Ethics reflection | [`docs/04_ethics.md`](docs/04_ethics.md) — central section under the market-research model |

---

## Tech stack

| Layer | Tool | Bootcamp source |
|---|---|---|
| OCR | EasyOCR (CRAFT detector + CRNN recogniser) | Week 7 |
| LLM extraction | Gemini 2.5 Flash Lite + few-shot + Pydantic | Week 9 |
| Vector search | FAISS + `paraphrase-multilingual-MiniLM-L12-v2` | Week 8 |
| Clustering | scikit-learn KMeans (with PCA for the 2D plot) | Week 5 |
| A/B stats | scipy.stats (Welch's t-test) | Week 5 |
| Image (optional) | PyTorch + torchvision MobileNetV2 | Week 6 |
| Data wrangling | pandas, matplotlib, seaborn | Week 3–4 |
| Web app | Streamlit | Self-taught (gap from bootcamp) |
| Code style | Python 3.13 + dataclasses + type hints + Pydantic | Week 1–2 |

---

## Run locally

```bash
git clone git@github.com:alexgl77/receipt-to-cashback.git
cd receipt-to-cashback
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
cp .env.example .env            # then put your GEMINI_API_KEY in it
streamlit run app/streamlit_app.py
```

Get a Gemini API key (free tier): https://aistudio.google.com/app/apikey

---

## Run tests

```bash
python -m unittest tests.test_cashback_engine -v
```

7 unit tests on the `CashbackEngine` business logic — strategy pattern, market-research semantics, categorised-share calculation.

---

## Repository structure

```
.
├── README.md                       (this file)
├── app.py                          (HF Spaces entry point — wraps app/streamlit_app.py)
├── requirements.txt
├── .env.example
├── data/
│   ├── README.md                   (dataset + catalog provenance)
│   └── catalog.csv                 (110-SKU F&B catalog)
├── docs/
│   ├── 00_simple_explanation.md    (daily build log in plain language)
│   ├── 01_proposal.md              (scope sent to instructor)
│   ├── 02_architecture.md          (pipeline rationale)
│   ├── 04_ethics.md                (central section under the new model)
│   ├── 06_trello_cards.md          (project-board card template)
│   └── 07_deploy_guide.md          (HF Spaces deploy steps)
├── notebooks/
│   ├── 01_eda.ipynb                (CORD-v2 + catalog EDA)
│   ├── 03_ocr_pipeline.ipynb       (EasyOCR benchmark on 20 receipts)
│   ├── 04_llm_extraction.ipynb     (Gemini prompts + schema validation)
│   ├── 05_faiss_cashback.ipynb     (spine end-to-end)
│   └── 07_clustering_ab.ipynb      (K-Means + A/B test)
├── src/
│   ├── ocr_pipeline.py             (OCRPipeline class)
│   ├── llm_extractor.py            (LLMExtractor + Pydantic schema)
│   ├── vector_store.py             (CatalogIndex over FAISS)
│   ├── matcher.py                  (line item → SKU joiner)
│   ├── cashback_engine.py          (Engine + Flat/Tiered strategies)
│   ├── analytics.py                (cluster_users + ab_test)
│   └── synthetic_users.py          (synthetic user-spend generator)
├── app/
│   └── streamlit_app.py            (4 pages: Upload · B2B · Ethics · About)
└── tests/
    └── test_cashback_engine.py     (7 unit tests, all passing)
```

---

## Daily build log (in plain language)

[`docs/00_simple_explanation.md`](docs/00_simple_explanation.md) is the source of truth for the demo and PPT — one entry per build day explaining **what we did, what it does in the app, where it comes from in the bootcamp, and one key code snippet**. Written for an audience that doesn't read code.

---

## Ethics

This project's business model — paying users for the right to sell their consumption data in aggregate — makes ethics the *central* design constraint, not a final-page disclaimer. See [`docs/04_ethics.md`](docs/04_ethics.md) for:

- Informed consent (what the user is actually selling)
- Privacy risk in receipt data (pharmacy, alcohol, geo + time)
- OCR bias against non-Latin scripts and thermal-paper receipts
- LLM hallucination — under-paying vs over-paying asymmetry
- K-anonymity floor for the data-sale side
- What we are *not* claiming

The Ethics page is also surfaced in the deployed app so demo viewers see it without leaving the URL.

---

## Acknowledgements

- **Yossi Eikelman** — instructor at Developers Institute, whose mid-build feedback ("spine first, garnish after") set the priority order that made delivery on time possible.
- **Naver Clova** — for releasing CORD-v2 under CC BY 4.0.
- **Hugging Face** — for hosting both the multilingual sentence-transformer used by FAISS and (likely) the Space serving the deployed app.
- **Google AI Studio** — for the Gemini API free tier.

---

## License

MIT — see [LICENSE](LICENSE).
