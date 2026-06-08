# Demo video script — 3 min Loom

Ready to read out loud while screen-recording. Each block has the
on-screen action + the line to say. Total: 3 min.

## Before pressing record

1. Open https://alexgl77-receipt-to-cashback.hf.space and leave it
   loaded for 60 s — warms up the model on the Space.
2. Browser zoom 110%, notifications off.
3. Have a second tab open at https://github.com/alexgl77/receipt-to-cashback
4. Mic on (webcam optional — a PIP circle in a corner is fine).
5. Speak in English (matches the UI).

---

## Block 1 · 0:00 → 0:15 (15 s)

**Screen:** Upload Receipt page, empty, nothing uploaded yet.

**Say:**
> "Hi, this is the demo for *Receipt-to-Cashback*, my Capstone
> project for the Developers Institute GenAI bootcamp 2026. The
> slides covered the why and the architecture — this is the part
> that shows it actually works."

---

## Block 2 · 0:15 → 1:20 (65 s)

**Action:** Sidebar → **Sample index** dropdown → pick **CORD
sample #1**. Progress bar appears.

**Say (while it's processing):**
> "I'm picking a real receipt from CORD-v2, a public dataset of a
> thousand receipts from Indonesian restaurants. Behind the scenes,
> Gemini 2.5 Flash Vision takes the image directly and returns
> structured JSON — items, prices, currency, grand total — all
> validated against a strict Pydantic schema. Then FAISS matches
> each item against our 110-SKU catalog using multilingual
> embeddings. The cashback is computed on the grand total."

**Wait (~25–30 s)** until the big cashback number appears.

**Say (once the number is visible):**
> "Total spend: 1.59 million Indonesian Rupiah, roughly 100 US
> dollars. Cashback: 2 percent flat on the grand total — about
> 32,000 IDR. Category coverage: 100 percent. On the right, line
> by line: every item, its category, the matched SKU, the spend,
> the cashback."

**Action:** Scroll down. Expand **Show Gemini Vision extraction
JSON**.

**Say:**
> "This is the raw JSON Gemini returned. Items, quantities, prices,
> currency, total — every field schema-validated by Pydantic. If the
> model returns malformed output, the extractor retries once with
> the validation error injected into the prompt."

---

## Block 3 · 1:20 → 1:50 (30 s)

**Action:** Sidebar → **B2B Analytics**.

**Say:**
> "This is the buyer side — what a brand or research firm would see
> if they bought our data. Top: a synthetic population of 400 users.
> Middle: an A/B test between 2 and 3 percent cashback. Welch's
> t-test recovers a 29 percent lift in receipts per user per month
> at 3 percent, p-value below 0.05. Bottom: K-Means clustering of
> users by category-spend shares, projected with PCA — four clean
> segments matching the four archetypes we generated."

**Action:** Scroll to show the cluster scatter chart.

---

## Block 4 · 1:50 → 2:05 (15 s)

**Action:** Sidebar → **Ethics**.

**Say:**
> "Because the business model is paying users for the right to sell
> their consumption data, ethics lives in the app, not buried in
> the repo. Seven sections: consent, privacy risk in receipt data,
> OCR bias against non-Latin scripts, the hallucination policy, and
> what we explicitly do not claim."

---

## Block 5 · 2:05 → 2:45 (40 s)

**Action:** Switch to the GitHub tab → open `src/vision_extractor.py`.

**Say:**
> "The Vision extractor — one Gemini multimodal call replaces what
> used to be EasyOCR plus a text-only LLM. The prompt tells the
> model to deduplicate items, treat the price next to a quantity
> as the line total, and read the grand total carefully."

**Action:** Open `src/cashback_engine.py`.

**Say:**
> "The CashbackEngine pays on the grand total — what the user
> actually spent — and uses the Strategy pattern, so swapping
> flat 2 percent for flat 3 percent or for tiered rates is a
> one-line change. Nine unit tests cover all the math."

**Action:** Open `src/vector_store.py`.

**Say:**
> "FAISS index over the 110-SKU catalog, queried in under a
> millisecond per item, using a multilingual sentence-transformer
> so Indonesian and Korean item names classify correctly."

---

## Block 6 · 2:45 → 3:00 (15 s)

**Action:** Back to the deployed app (Upload Receipt with the result
still on screen).

**Say:**
> "Live at the URL on the slides, source on GitHub — both linked in
> the README. That's the demo. Thanks."

---

## Recovery plans if something breaks live

| Problem | What to do |
|---|---|
| HF cold start, first response 40+ s | Keep talking — the "behind the scenes" paragraph in Block 2 is long enough to cover it. |
| Gemini API rate-limited | The app caches by image hash — re-upload the same image and the second call is instant. |
| HF Space down | Run locally: `./.venv/Scripts/streamlit run app/streamlit_app.py` on `localhost:8501`. The video doesn't have to be on the deployed URL. |
| OCR misread on the chosen sample | Samples #2 and #3 are fallbacks. |

## Editing notes

- Cut any silence > 1 s between sentences.
- If you flub a line, don't restart — use Loom's editor to trim. A
  re-take adds 20 minutes for marginal polish.
- The first 5 seconds are the only ones most reviewers will fully
  watch attentively. Lead with what they need: "this is the demo
  for X, here's what works."
