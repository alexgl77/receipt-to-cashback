# PPT outline — Demo Day 2026-06-11

Source of truth: the generated **[`Receipt-to-Cashback.pptx`](Receipt-to-Cashback.pptx)**
in this folder. This doc is the speaker notes + the design rationale.

**Structure mirrors the bootcamp brief exactly (5 sections, 7 slides total):**

| Brief section | Slides |
|---|---|
| 1. Project Overview | 1 (Title), 2 (Overview) |
| 2. Tools & Technologies | 4 |
| 3. Solution & Benefits | 3 (Pipeline), 5 (Numbers) |
| 4. Challenges Faced | 6 |
| 5. Future Steps (optional) | 7 |

**Ethics is NOT a PPT slide** — the project brief asks for an ethics
*reflection*, which lives in [`docs/04_ethics.md`](../docs/04_ethics.md)
and as a tab inside the deployed Streamlit app. Pulling it into the
4-minute presentation would be padding.

**Total speaker time: ~3 min 45 s** (target 4 min). Trim or expand
during rehearsal.

---

## Slide 1 — Title (15 s)

**On screen:**
- "Receipt-to-Cashback" big
- "Scan a receipt. Get paid for the data." subline
- "Alex Goldbaum · GenAI & ML Bootcamp 2026 · Demo Day 11/06/2026"
- GitHub + HF Spaces URLs (replace with QR codes when you upload to Slides)

**Speaker:**
> "Hi, I'm Alex. I built *Receipt-to-Cashback*. One-line pitch: a user
> scans a receipt, we pay flat cashback, and we sell the consumption
> data in aggregate. Live URL and code on screen."

---

## Slide 2 — Project Overview (35 s)

**On screen — two columns:**

| The problem | What we built |
|---|---|
| Market research today buys self-reported surveys or slow shopper panels. Loyalty programs see one retailer at a time. **Nobody has the cross-merchant, item-level picture.** | A market-research data-acquisition app. Users scan a receipt; we pay flat cashback in exchange for the itemised consumption data, anonymised and sold in aggregate. Target users: consumers wanting any-merchant cashback; brands and research firms as data buyers. |

**Speaker:**
> "Market research today buys self-reported surveys or shopper panels
> that take months to recruit. Loyalty programs see one retailer at a
> time. Nobody has the cross-merchant, item-level picture of what
> consumers actually buy. We get it by paying the consumer directly
> for the photo of any receipt. The cashback is the price of the data;
> the value is selling the consumption picture in aggregate."

---

## Slide 3 — Solution & Pipeline (45 s)

**On screen:** the 5-stage pipeline in monospace + a one-liner about latency.

```
1. EasyOCR              -> raw text from the receipt photo
2. Gemini 2.5 Flash Lite -> structured JSON (items, prices, total)
                           with few-shot prompts + Pydantic schema
3. FAISS + multilingual  -> match each item against the 110-SKU catalog
   sentence-transformer    classify spend by category
4. CashbackEngine        -> apply strategy (Flat / Tiered)
                           + two-tier drift guard
5. Streamlit UI          -> upload page, B2B analytics, Ethics tab
```

**Speaker:**
> "Five stages. EasyOCR pulls raw text. Gemini Flash Lite with
> few-shot prompts and a strict Pydantic schema turns the noisy text
> into structured items. FAISS with multilingual embeddings matches
> each item to the catalog — multilingual matters because real
> receipts mix English, Indonesian and Korean. A small CashbackEngine
> applies the strategy. Streamlit wraps it. End-to-end on a real
> receipt: about 8 seconds."

---

## Slide 4 — Tools & Technologies (30 s)

**On screen:** the tools table from the .pptx with Layer / Tool / Source columns. Every row sources back to a bootcamp week — except Streamlit, marked **SELF-TAUGHT**.

**Speaker:**
> "Almost the entire stack comes directly from bootcamp weeks. OCR is
> week 7, the LLM extractor is week 9, FAISS is week 8, clustering
> and A/B stats are weeks 4 and 5. The Python OOP scaffolding is
> weeks 1–2. Streamlit is the one self-taught piece — the bootcamp
> doesn't cover it."

---

## Slide 5 — What works — by the numbers (35 s)

**On screen:** metrics table. End-to-end latency, OCR recall, classification rate, unit tests, drift guard tiers, A/B test result, K-Means cluster count, live URL.

**Speaker:**
> "End-to-end about 8 seconds per receipt on CPU. OCR recovers 85
> percent of ground-truth items on average — 100 percent on 16 of 20
> in the benchmark. The CashbackEngine has 13 unit tests, all
> passing. The drift guard has two tiers — scale at 10 percent,
> refuse at 50 percent. On the synthetic 400-user A/B simulation, 3
> percent cashback delivered 29 percent more receipts per user per
> month than 2 percent, p-value below 0.05. K-Means cleanly recovers
> the four user archetypes we generated. Live URL on the slide."

(Optionally: cut to the Loom video here, then return to slide 6 after.)

---

## Slide 6 — Challenges Faced (50 s)

**On screen:** table with 4 rows. Problem → Fix.

**Speaker:**
> "Four problems we caught during the build, not at the demo. One:
> the original partner-rebate business model gated cashback to items
> with brand agreements, which left most real receipts empty.
> Pivoted to market-research; every priced line now pays.
>
> Two: the English-only embedding rejected an Indonesian item, PKT
> AYAM, paquete de pollo. Swapped to a multilingual model.
>
> Three: latency was 40-plus seconds. Flash Lite plus an image-hash
> cache brought it to 8.
>
> Four — caught at rehearsal — on a receipt with quantities like
> '3 x Bbk Panggang' the LLM double-counted items, inflating spend 70
> percent. The next rehearsal showed the inverse: it dropped the
> leading million reading 1,591,600 as 591,600, which silently
> under-paid the user. We built a two-tier drift guard: scale to the
> declared total at 10 percent drift, refuse cashback entirely at 50
> percent. Better an angry user re-uploading than a quietly
> under-paid one."

---

## Slide 7 — Future Steps & Thanks (20 s)

**On screen — two columns:**

| Two more weeks | Thanks |
|---|---|
| Real users (not synthetic) · Postgres warehouse · Image redaction · K-anonymity at sale time · MCP "spend search" agent · CNN quality gate · Multilingual OCR (Hebrew, Arabic) | Yossi Eikelman (instructor, the "spine first, garnish after" feedback) · DI cohort 2026 · Naver Clova (CORD-v2 dataset) · Google AI Studio (Gemini free tier) · Hugging Face (sentence-transformer + Space hosting) |

Bottom line: links to GitHub + HF Spaces.

**Speaker:**
> "Two more weeks would buy us real users, a Postgres warehouse,
> image-level redaction, k-anonymity at the sale boundary, and the
> MCP agent that couldn't fit. Thanks to Yossi — the spine-first
> feedback is what made on-time delivery possible — to the cohort,
> and to Naver Clova for releasing CORD. Code and live URL on the
> slide. Happy to take questions."

---

## Total time

| Slide | Speaker | Cumulative |
|---|---|---|
| 1 — Title | 15 s | 0:15 |
| 2 — Overview | 35 s | 0:50 |
| 3 — Pipeline | 45 s | 1:35 |
| 4 — Tools | 30 s | 2:05 |
| 5 — Numbers | 35 s | 2:40 |
| 6 — Challenges | 50 s | 3:30 |
| 7 — Future + Thanks | 20 s | **3:50** |

Inside the 4-minute hard cap, with 10 s buffer.

---

## How to take this into Google Slides

1. Open the bootcamp template in Google Slides.
2. File → Open → Upload → pick `presentation/Receipt-to-Cashback.pptx`.
3. Google Slides will import all 7 slides with text + tables intact.
4. Apply the bootcamp template's master theme (Slide → Apply layout / Change theme).
5. Replace the placeholder URL strings on slides 1 and 7 with QR codes (e.g. https://qr.io).
6. Add a screenshot to slide 5 (the Upload Receipt page showing a successful run + drift-guard banner if you have a good capture).
7. Rehearse twice with a stopwatch.

## Visuals still to drop in

- [ ] QR code → HF Spaces live URL (slides 1 + 7)
- [ ] QR code → GitHub repo (slides 1 + 7)
- [ ] Screenshot: Upload Receipt page with a result (slide 5)
- [ ] Optional architecture diagram from `docs/02_architecture.md` exported to PNG (slide 3, replaces the monospace block)
