# PPT outline — Demo Day 2026-06-11

This is the **slide-by-slide content** for the Capstone presentation.
Paste each block into the bootcamp's PowerPoint template (one slide
per `## Slide N` section).

**Hard constraints from the brief:**
- Total presentation time ≤ 10 min (PPT 4 min + video 4 min + Q&A 2 min)
- This PPT is 8 slides → ~30 seconds per slide → strict.
- Anything that can be a visual (logo, chart, screenshot) **must** be a
  visual, not a bullet list. Text on slides should be a phrase, the
  rest is spoken.

---

## Slide 1 — Title

**Visible on slide:**

> # Receipt-to-Cashback
>
> *Scan a receipt. Get paid for the data.*
>
> Alex Goldbaum · GenAI & ML Bootcamp 2026 · Developers Institute
> Demo Day · 2026-06-11
>
> [QR code → live HF Spaces URL] · [QR code → GitHub repo]

**Speaker (15 s):**

> "Hi, I'm Alex. I built *Receipt-to-Cashback*. The one-line pitch is:
> a user scans a receipt, we pay them a small flat cashback, and we
> sell the itemised consumption data in aggregate. Live URL and code
> are in the QR codes."

---

## Slide 2 — The problem we're solving

**Visible on slide (left half = problem, right half = market):**

- Market-research firms pay millions for consumption panels — but
  panels are slow, expensive, and self-reported.
- Loyalty-card data exists only inside one retailer.
- **Nobody has the raw, cross-merchant, per-item picture of what
  consumers actually buy.**
- We do — by paying the consumer directly for their receipts.

**Speaker (30 s):**

> "Market research today buys self-reported surveys, or shopper panels
> that take months to recruit. Loyalty programs see one retailer at a
> time. Nobody has the **cross-merchant, item-level picture** of what
> consumers actually buy. We get it by paying the consumer directly
> for the photo of any receipt — flat cashback, no partnerships
> needed, anonymised and sold in aggregate to brands and research
> firms."

---

## Slide 3 — The pipeline (one diagram)

**Visible on slide:**

A single big diagram, ASCII or boxes (export from
`docs/02_architecture.md`):

```
photo  →  EasyOCR  →  Gemini 2.5 Flash Lite (JSON, Pydantic)
                  →  FAISS (multilingual embeddings, 110-SKU catalog)
                  →  CashbackEngine (flat / tiered strategy)
                  →  cashback number + structured data record
```

**Speaker (45 s):**

> "Five stages. EasyOCR pulls the raw text from the receipt photo.
> Gemini Flash Lite, with few-shot prompts and a strict Pydantic
> schema, turns that noisy text into structured items, prices and
> total. FAISS with a *multilingual* sentence-transformer matches
> each item against a 110-SKU food-and-beverage catalog — multilingual
> matters because real receipts are in Indonesian, Korean, Spanish.
> A small OOP CashbackEngine applies a flat or tiered strategy, and
> we get a cashback number plus a clean data record. Streamlit wraps
> it."

---

## Slide 4 — Tools (with bootcamp attribution)

**Visible on slide (2-column table):**

| Layer | Tool | Where I learned it |
|---|---|---|
| OCR | EasyOCR | Week 7 |
| LLM extraction | Gemini 2.5 Flash Lite + few-shot + Pydantic | Week 9 (prompt eng.) |
| Vector matching | FAISS + multilingual sentence-transformer | Week 8 (RAG / Vector DB) |
| Clustering | scikit-learn K-Means | Week 4-5 |
| A/B stats | scipy Welch's t-test | Week 5 |
| Web UI | Streamlit | **Self-taught** |
| Code | Python OOP + Pydantic + dataclasses | Week 1-2 |

**Speaker (30 s):**

> "Most of the stack is directly from bootcamp weeks. Streamlit is
> the only self-taught piece — the bootcamp doesn't cover it. The
> business logic is plain Python OOP, the LLM is the Gemini free
> tier, the vector DB is FAISS on CPU. No heavy infra."

---

## Slide 5 — What works (the spine demo, in numbers)

**Visible on slide:**

- End-to-end latency: ~8 s on a typical receipt (CORD-v2)
- Items extracted: average 5 per receipt, up to 30+
- 7 unit tests on the cashback engine, **all passing**
- Live URL: `huggingface.co/spaces/alexgl77/receipt-to-cashback`

> Demo on the next slide / in the video.

**Speaker (30 s):**

> "End-to-end runs in about eight seconds on a real CORD-v2 receipt.
> The cashback engine has seven unit tests, all passing. Live at this
> URL. The video walks through it."

---

## Slide 6 — Honest challenges (and what we did)

**Visible on slide (3 mini-panels):**

| Problem found mid-build | What we did |
|---|---|
| Original business model (partner-rebate) rejected legitimate items | **Pivoted** to market-research model: every priced line earns cashback, catalog becomes a classifier |
| English-only embedding rejected Indonesian item "PKT AYAM" | **Swapped** for `paraphrase-multilingual-MiniLM-L12-v2` |
| End-to-end latency was 40+ s on the first run | **Switched** to Gemini Flash Lite + cached OCR/LLM by image hash → 8 s |

**Speaker (40 s):**

> "Three problems we caught during the build, not the demo. First,
> the original business model — partner-rebate — gated cashback to
> items we had agreements for, which meant most real receipts came
> back empty. We pivoted to market-research, where we pay the user
> for the data itself. Every priced line now earns cashback.
>
> Second, the English-only embedding model rejected Indonesian items.
> We swapped to a multilingual model and it classifies correctly.
>
> Third, latency was 40-plus seconds. Switching the LLM to Flash Lite
> and caching by image hash brought it down to 8."

---

## Slide 7 — Ethics is the center of the project, not a footnote

**Visible on slide:**

- This business sells consumption data. That puts privacy at the
  centre, not at the end.
- Risks we surface in the app and the repo:
  - Informed consent (what is the user actually selling?)
  - OCR bias against non-Latin scripts
  - LLM hallucination — under-paying is worse than over-paying
  - k-anonymity floor before any data is sold
  - Toxic category cross-joins (baby formula × alcohol)
- Full discussion: [`docs/04_ethics.md`](../docs/04_ethics.md), and
  also a tab inside the deployed app.

**Speaker (40 s):**

> "Under the market-research model, ethics is the project, not a
> footnote. The ethics doc covers consent, privacy risk, OCR bias
> against non-Latin scripts — which structurally disadvantages users
> in certain regions — and the asymmetry between the LLM
> hallucinating an extra item (we overpay, which is fine) versus
> dropping a real one (the user gets underpaid, which is not). The
> doc lives in the repo *and* as a tab inside the app."

---

## Slide 8 — Future steps + thanks

**Visible on slide:**

- **If we had two more weeks:** real users (not synthetic), Postgres
  warehouse, redaction step on raw images, k-anonymity check at sale
  time, MCP agent that answers "how much did I spend on coffee in
  May?"
- Thanks: **Yossi Eikelman** (instructor), **DI cohort**,
  **Naver Clova** (CORD-v2 dataset)
- **Repo:** github.com/alexgl77/receipt-to-cashback
- **Live:** huggingface.co/spaces/alexgl77/receipt-to-cashback

**Speaker (20 s):**

> "If we had two more weeks: real users, Postgres warehouse,
> image-level redaction, k-anonymity at the sale boundary, and the
> MCP agent we couldn't fit in time. Thanks to Yossi, the cohort,
> and Naver Clova for releasing CORD. Happy to take questions."

---

## Total time check

| Slide | Speaker time |
|---|---|
| 1 — Title | 15 s |
| 2 — Problem | 30 s |
| 3 — Pipeline | 45 s |
| 4 — Tools | 30 s |
| 5 — Numbers | 30 s |
| 6 — Challenges | 40 s |
| 7 — Ethics | 40 s |
| 8 — Future + thanks | 20 s |
| **PPT total** | **250 s = 4 min 10 s** |

Slightly over the 4-minute target; trim ~10 s from slide 6 or 7
during rehearsal. The video (next file) covers the remaining 4
minutes; Q&A is the remaining 2.

---

## Visuals you still need to make/grab

- [ ] QR code → HF Spaces URL (use any free QR generator)
- [ ] QR code → GitHub repo URL
- [ ] Screenshot of the Upload Receipt page with a sample result
- [ ] Screenshot of the B2B Analytics page (clusters + A/B numbers)
- [ ] Screenshot of the Ethics page
- [ ] Export the architecture diagram from `docs/02_architecture.md`
      as a clean image for slide 3
