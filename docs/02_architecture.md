# Architecture

## High-level flow

```
                  ┌─────────────────────┐
                  │  User uploads photo │
                  └──────────┬──────────┘
                             │
                             ▼
     ┌──────────────────────────────────────────────┐
     │  [1] CNN classifier (MobileNetV2 fine-tuned) │
     │      → is it a receipt? what type of store?  │
     └──────────────────────┬───────────────────────┘
                            │
                  (if it's a receipt)
                            │
                            ▼
     ┌──────────────────────────────────────────────┐
     │  [2] OCR (TrOCR / Donut, pre-trained)        │
     │      → raw text from the receipt image       │
     └──────────────────────┬───────────────────────┘
                            │
                            ▼
     ┌──────────────────────────────────────────────┐
     │  [3] LLM extractor (Gemini 2.0 Flash)        │
     │      few-shot prompts + Pydantic schema      │
     │      → {items, prices, date, total}          │
     └──────────────────────┬───────────────────────┘
                            │
                            ▼
     ┌──────────────────────────────────────────────┐
     │  [4] FAISS vector search                     │
     │      embed each item → nearest catalog match │
     └──────────────────────┬───────────────────────┘
                            │
                            ▼
     ┌──────────────────────────────────────────────┐
     │  [5] CashbackEngine (Python OOP)             │
     │      → applies rules → cashback amount       │
     └──────────────────────┬───────────────────────┘
                            │
                            ▼
     ┌──────────────────────────────────────────────┐
     │  [6] Streamlit dashboard                     │
     │      user history + analytics + B2B view     │
     └──────────────────────────────────────────────┘
                            │
                            ▼
     ┌──────────────────────────────────────────────┐
     │  [7] Analytics layer (offline)               │
     │      K-Means clustering + A/B test           │
     │      LogisticRegression (validity check)     │
     └──────────────────────────────────────────────┘
```

---

## Why each component exists

| Step | Why | Alternative we considered | Why we picked this |
|---|---|---|---|
| [1] CNN | Filter spam/non-receipts before paying for OCR + LLM; categorise the store for analytics | Skip the CNN, send everything to OCR | Adds cost and noise; CNN is also the most natural place to cover the "Deep Learning" requirement of the brief |
| [2] OCR | Receipt text is in pixels, we need characters | Train an OCR from scratch | Pre-trained TrOCR/Donut covers the "pre-trained model" requirement and works out of the box |
| [3] LLM | Receipt text is messy (line breaks, prices on the right, taxes, totals); regex won't generalise across formats | Regex / rules | LLM with few-shot generalises across receipt formats; also covers prompt engineering requirement |
| [4] FAISS | The catalog has ~100 products and OCR text doesn't match perfectly ("CocaCola 1.5L" vs "COCA COLA 1500ML"); semantic search handles this | SQL LIKE / fuzzy string match | Vector search covers the brief requirement; sentence-transformers gives much better recall on messy text |
| [5] CashbackEngine | The "business logic" — easier to test and modify than embedding rules in the UI | Hardcode rules in the Streamlit page | OOP separation lets us unit-test rules independently |
| [6] Streamlit | The brief explicitly asks for an accessible interface | Gradio | Streamlit is more flexible for multi-page dashboards |
| [7] Analytics | Covers clustering + A/B testing requirements; also gives the "B2B narrative" | Skip and stay B2C only | Without these we don't cover the stats/clustering parts of the brief |

---

## Data flow per receipt

```
photo.jpg
  → CNN classifier              → {is_receipt: bool, store_type: "supermarket"}
  → OCR                         → "TOTAL 12.350\nCOCA COLA 1.5L 1.890\n..."
  → LLM (few-shot, JSON schema) → {items: [{name:"Coca Cola 1.5L", price:1890}, ...], total:12350, date:"...", store:"..."}
  → FAISS match                 → [{item:"Coca Cola 1.5L", matched_to:"COCA_COLA_15L", category:"beverage"}, ...]
  → CashbackEngine.compute      → {cashback: 312, breakdown: {...}}
  → DB write + UI update
```

---

## Branch strategy

| Branch | Component |
|---|---|
| `main` | Always deployable |
| `feat/ocr-pipeline` | Step [2] |
| `feat/llm-extractor` | Step [3] |
| `feat/cnn-classifier` | Step [1] |
| `feat/faiss-matcher` | Step [4] |
| `feat/cashback-engine` | Step [5] |
| `feat/streamlit-app` | Step [6] |
| `feat/analytics` | Step [7] |

Each branch merges to `main` once it works end-to-end. This explicitly satisfies the brief's requirement of using branches.
