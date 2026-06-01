# Receipt-to-Cashback — Final Project (Developers Institute Capstone)

> Upload a photo of a receipt → the app validates it, extracts items with OCR + an LLM, matches them against a product catalog with a vector database, and computes a cashback reward.

**Author:** Alex Goldbaum · **Bootcamp:** GenAI & Machine Learning 2026, Developers Institute
**Demo Day:** 2026-06-11

---

## ⚠️ Status

Work in progress. This README is a skeleton — final version will be completed on day 8 of the build.

---

## What this project does (in one paragraph)

A user takes a picture of a paper receipt and uploads it to a Streamlit app. A convolutional neural network (CNN) trained on top of MobileNetV2 first checks the image is a real receipt and classifies the type of store (supermarket, pharmacy, restaurant, gas station, other). An OCR model (TrOCR or Donut) extracts the raw text from the receipt. Gemini 2.0 Flash, prompted with few-shot examples, turns that text into a clean JSON of items, prices, date and total. Each item is then matched against a generic international product catalog (~100 SKUs) using FAISS vector search. A simple OOP `CashbackEngine` applies business rules per category and returns the cashback amount to the user. A separate "B2B view" page shows aggregated analytics on top of simulated receipt history — k-means clustering of users, and an A/B-test simulation of two cashback strategies. Dataset for training, evaluation and demo: SROIE 2019 (public, ~1000 annotated receipts).

---

## Live demo

- **Deployed app:** _(URL added on day 8)_
- **Demo video (3 min):** _(Loom link added on day 9)_

---

## Tech stack

| Layer | Tool | Where it comes from in the bootcamp |
|---|---|---|
| Image classification (CNN) | PyTorch + torchvision MobileNetV2 (transfer learning) | Week 6 — Deep Learning |
| OCR | TrOCR / Donut (pre-trained) | Week 7 — LLM & Gen AI |
| Structured extraction (LLM) | Gemini 2.0 Flash + few-shot prompts | Week 9 — Prompt Engineering |
| Vector search | FAISS + sentence-transformers | Week 8 — NLP & RAG |
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
