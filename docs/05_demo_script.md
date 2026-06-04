# Demo video script — 3 min Loom

**Target:** 3 min recording (hard cap 4 min). Audience: bootcamp
evaluators who *did* watch the PPT, so do **not** re-explain the
business model. The video's job is to show that the thing actually
works.

**Tooling:**
- Recorder: Loom (free) or OS screen recorder
- Resolution: 1080p, microphone enabled, webcam optional (a small
  PIP face circle in a corner is friendly but not required)
- Speak in English (matches README/UI)

**Pre-flight checklist (do once, before pressing record):**
- [ ] HF Spaces is **warm** — open the URL 60 s before recording so
      the first OCR/LLM call is not a cold start
      https://huggingface.co/spaces/alexgl77/receipt-to-cashback
- [ ] Browser zoom 110% so text reads on the recording
- [ ] Close Slack/email notifications
- [ ] Pick the sample to demo *in advance* — CORD sample #1 is the
      best one because it triggers the **drift guard** (good
      narrative payoff)
- [ ] Have the GitHub repo open in a second tab for the code section

---

## Script (timed)

### 00:00 — 00:15  ·  Intro (15 s)

> "Hi, this is the demo for *Receipt-to-Cashback*, the Capstone
> project I built for the Developers Institute GenAI bootcamp 2026.
> The slides covered the why and the architecture — this is the *it
> works* part."

**Screen:** start on the deployed HF Spaces URL, Upload Receipt page.

---

### 00:15 — 01:20  ·  Live demo, upload flow + drift guard (65 s)

> "I'm picking sample #1 from the sidebar — it's a real receipt from
> Indonesia in the CORD-v2 dataset. I'm picking this one deliberately
> because it triggers a defensive behaviour I'll explain in a second."

**Action:** sidebar → Sample receipt → "CORD sample #1". Pause for
the progress bar.

> "While Gemini structures the items: EasyOCR already extracted the
> raw text, Gemini Flash Lite is converting it into JSON of items
> with prices and a total, then FAISS will match each item against
> our 110-SKU catalog using a multilingual sentence-transformer."

**Wait for result.** When the metric appears with the **warning
banner**:

> "Two things to notice. First — the cashback amount on the right.
> Second — that warning panel. Here's the idea: in any receipt,
> the sum of the items should equal the printed total at the
> bottom. But OCR and LLM aren't perfect — sometimes they
> double-count items, sometimes they misread a digit on the total.
> So we do a simple sanity check: we compare *sum of items*
> against *printed total*. If they disagree by more than 10%,
> we trust the printed total and scale the cashback down. If they
> disagree by more than 50%, we refuse to pay and ask for another
> photo. That's what just fired here."

**Action:** scroll down to the line-by-line breakdown, then expand
"Show Gemini extraction JSON".

> "The line breakdown shows what FAISS classified each item as.
> Below, the raw JSON Gemini returned — every field validated by a
> strict Pydantic schema. If Gemini returns malformed output, the
> extractor retries once with the validation error in the prompt."

---

### 01:20 — 01:50  ·  B2B Analytics page (30 s)

**Action:** sidebar → Navigation → B2B Analytics.

> "Buyer-side view — what a brand or research firm would see if they
> bought our data. Top: a synthetic population of 400 users. Middle:
> A/B test between 2% and 3% cashback — Welch's t-test recovers a
> ~29% lift in receipts per user per month at 3%, p-value below
> 0.05. Bottom: K-Means clustering of users by category-spend
> shares, projected with PCA — four clean clusters matching the
> four archetypes we generated."

**Action:** scroll to show the cluster scatter + cluster centres
table.

---

### 01:50 — 02:05  ·  Ethics page (15 s)

**Action:** sidebar → Ethics.

> "Under this business model — paying users for the right to sell
> their consumption data — ethics belongs *in the app*, not buried
> in the repo. Seven sections cover consent, privacy risk in receipt
> data, OCR bias against non-Latin scripts, and the LLM
> hallucination policy that the drift guard implements."

---

### 02:05 — 02:45  ·  Code highlights (40 s)

**Action:** switch tab to GitHub repo, open `src/cashback_engine.py`.

> "The CashbackEngine uses the Strategy pattern — `FlatStrategy(0.02)`
> versus `FlatStrategy(0.03)` is a one-line swap that powers the A/B
> simulation without touching the engine. The two-tier drift guard
> we just saw lives in this file. 13 unit tests cover all the
> market-research semantics."

**Action:** open `src/llm_extractor.py`, scroll to the few-shot
prompt template.

> "The LLM extractor uses a few-shot prompt with two CORD-style
> examples and a strict Pydantic schema. If the JSON is malformed,
> it retries once with the error injected into the prompt."

**Action:** open `src/vector_store.py`.

> "FAISS index over the catalog, queried in under a millisecond per
> item. We changed the embedding mid-build from English-only MiniLM
> to the multilingual variant — that's what fixed the Indonesian
> item rejection."

---

### 02:45 — 03:00  ·  Close (15 s)

**Action:** back to the deployed app, Upload Receipt page.

> "Live at the URL on the slides, source on GitHub — both linked in
> the README. That's the demo. Thanks."

---

## Editing notes

- Cut any silence longer than 1 s between sentences.
- If you flub a line, **don't restart** — just cut in Loom's editor.
  A re-take adds 20 minutes to your day for marginal polish.
- The first 5 seconds are the only ones most reviewers will fully
  watch attentively. Lead with what they need: "this is the demo for
  X, here's what works."

## Recovery plans if something breaks on the day

| What breaks | What to do |
|---|---|
| HF Spaces is cold and OCR takes 30+ s on the first sample | Keep talking — the "while Gemini structures" paragraph is long enough to cover it. |
| Gemini API rate-limited | Show the cached extraction JSON from a previous run (the app caches by image hash — a second upload of the same image is instant). |
| HF Spaces is *down* | Run `streamlit run app/streamlit_app.py` locally and demo on `localhost:8501`. The recording doesn't have to be on the deployed URL. |
| OCR misreads everything on the chosen sample | Sample #2 or #3 are the fallback. #2 (PKT AYAM) is short and clean; #3 has fewer items than #1. |
| Drift guard doesn't fire on the demo sample | Drop the drift-guard section and use the extra 30 seconds for code highlights. The drift guard is in the PPT anyway. |
