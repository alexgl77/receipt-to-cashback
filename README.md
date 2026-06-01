# Receipt-to-Cashback — Final Project (Developers Institute Capstone)

> A market-research data acquisition app. Users scan a receipt → we pay them flat cashback in exchange for the itemised consumption data, which is anonymised, classified and (in the business model) sold in aggregate to brands and retailers.

**Author:** Alex Goldbaum · **Bootcamp:** GenAI & Machine Learning 2026, Developers Institute
**Demo Day:** 2026-06-11

---

## ⚠️ Status

Work in progress. This README is a skeleton — final version will be completed on day 8 of the build.

---

## What this project does (in one paragraph)

A user takes a picture of a paper receipt and uploads it to a Streamlit app. An OCR model (EasyOCR) extracts the raw text. Gemini 2.5 Flash Lite, prompted with few-shot examples and constrained by a strict Pydantic schema, turns that text into a clean list of items, prices, currency and total. Each item is then embedded with a multilingual sentence-transformer and matched against a 110-SKU F&B catalog using FAISS — the catalog **classifies** the spend (food / beverage / bakery / …) so that the data we hold is enriched, but every priced line earns cashback regardless of whether it classifies. A small OOP `CashbackEngine` applies a flat or tiered strategy and returns the amount to the user. A separate "B2B view" page shows aggregated analytics on top of simulated receipt history — K-Means clustering of users by spend pattern, and an A/B-test simulation of two cashback rates. Dataset for training, evaluation and demo: CORD-v2 (public, 1000 annotated receipts, Naver Clova 2019). A short ethics section discusses informed consent, anonymisation, and the risk profile of monetising aggregated consumption data.

---

## Live demo

- **Deployed app:** _(URL added on day 8)_
- **Demo video (3 min):** _(Loom link added on day 9)_

---

## Tech stack

| Layer | Tool | Where it comes from in the bootcamp |
|---|---|---|
| Image classification (CNN) | PyTorch + torchvision MobileNetV2 (transfer learning, optional quality gate) | Week 6 — Deep Learning |
| OCR | EasyOCR (CRAFT detector + CRNN recognizer) | Week 7 — LLM & Gen AI |
| Structured extraction (LLM) | Gemini 2.5 Flash Lite + few-shot + Pydantic strict schema | Week 9 — Prompt Engineering |
| Vector search | FAISS + multilingual sentence-transformers (`paraphrase-multilingual-MiniLM-L12-v2`) | Week 8 — NLP & RAG |
| Classical ML | scikit-learn (LogisticRegression, KMeans) | Week 5 — ML |
| Stats (A/B test) | scipy.stats | Week 5 — Stats for ML |
| Data wrangling & viz | pandas, matplotlib, seaborn | Week 3-4 — Data Analysis |
| Web app | Streamlit | Self-taught (gap from bootcamp) |
| Code | Python OOP, functions | Week 1-2 — Python & OOP |

---

## Repository structure

```
final project/
├── docs/         # Simple explanation, proposal, architecture, ethics
├── data/         # Catalog + receipts (gitignored)
├── notebooks/    # EDA, training, experiments
├── src/          # Production code (OOP modules)
├── app/          # Streamlit app
├── tests/        # Unit tests
└── presentation/ # PPT + demo video
```

---

## How to run locally

_(Detailed instructions added on day 6 once the app is functional.)_

```bash
pip install -r requirements.txt
cp .env.example .env  # then add your GEMINI_API_KEY
streamlit run app/streamlit_app.py
```

---

## Project board

[Trello link added on day 1]

---

## Ethics

Receipt data exposes sensitive consumption habits (medication, alcohol, location patterns). See [docs/04_ethics.md](docs/04_ethics.md) for the full discussion on privacy, informed consent, OCR bias and the risks of monetising aggregated consumption data.

---

## License

MIT — see [LICENSE](LICENSE).
