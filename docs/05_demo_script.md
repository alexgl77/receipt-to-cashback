# Demo video script — 2:00 target

Tight version. The Gemini Vision call returns fast enough that we
don't need filler — every line below is needed. Hard cap 3 min per
brief; we aim for 2:00 to leave editing slack.

## Before pressing record

1. Open https://alexgl77-receipt-to-cashback.hf.space and leave it
   loaded for 60 s — warms the model on the Space.
2. Browser zoom 110%, notifications off.
3. Second tab open: https://github.com/alexgl77/receipt-to-cashback
4. This script visible on a second monitor / phone / VSCode panel —
   NOT in a Chrome tab Loom will record.
5. Loom: Window mode, Mic on, Camera optional. Pick the Chrome window.

---

## Block 1 · 0:00 → 0:08 (8 s)

**Screen:** Upload Receipt page, empty.

**Say:**
> "Hi, this is the demo for Receipt-to-Cashback, my Capstone for
> the GenAI bootcamp 2026."

---

## Block 2 · 0:08 → 0:55 (47 s)

**Action:** Sidebar → **Sample index** → **CORD sample #1**.

**Say (while it processes):**
> "Picking a real Indonesian restaurant receipt from CORD-v2.
> Gemini 2.5 Flash Vision reads the image directly and returns
> structured JSON. FAISS matches each item to our 110-SKU catalog
> with multilingual embeddings. Cashback is computed on the grand
> total. Stack: Gemini, FAISS, sentence-transformers, scikit-learn,
> Pydantic, Streamlit."

**When the cashback number appears:**
> "1.6 million Rupiah total, about 100 dollars. Cashback at 2
> percent: 32,000 IDR. 100 percent of items classified. Line
> breakdown on the right."

---

## Block 3 · 0:55 → 1:15 (20 s)

**Action:** Sidebar → **B2B Analytics**.

**Say:**
> "Buyer-side view. A/B test: 3 percent cashback drives a 29
> percent lift in receipts per user, p below 0.05. K-Means
> clusters users into four spend segments."

---

## Block 4 · 1:15 → 1:23 (8 s)

**Action:** Sidebar → **Ethics**.

**Say:**
> "Ethics in the app: consent, privacy, OCR bias, hallucination
> policy."

---

## Block 5 · 1:23 → 1:50 (27 s)

**Action:** Switch to the GitHub tab.

**Open `src/vision_extractor.py`:**
> "Vision extractor: one Gemini call, image to JSON."

**Open `src/cashback_engine.py`:**
> "CashbackEngine: strategy pattern, pays on grand total."

**Open `src/vector_store.py`:**
> "FAISS, multilingual, sub-millisecond per query."

---

## Block 6 · 1:50 → 2:00 (10 s)

**Action:** Back to the deployed app.

**Say:**
> "Live URL and source on the slides. Thanks."

---

## Recovery plans if something breaks live

| Problem | What to do |
|---|---|
| HF cold start, first response 40+ s | Keep talking — the stack line in Block 2 is built for that |
| Gemini rate-limited | Re-upload same image — cached by hash, instant |
| HF Space down | `./.venv/Scripts/streamlit run app/streamlit_app.py` and demo on `localhost:8501` |
| OCR misread on sample #1 | Samples #2 and #3 are tested fallbacks |

## Editing notes

- Cut silence > 1 s in Loom editor.
- If you flub, don't restart — trim.
- After recording: Loom Settings → Visibility → **Public**.
