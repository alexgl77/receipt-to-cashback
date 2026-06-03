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
- [ ] Browser zoom 110% so text reads on the recording
- [ ] Close Slack/email notifications
- [ ] Have 2 boletas ready to upload: one CORD sample (use
      the sidebar's "CORD sample #1") and one of the photos in
      `data/receipts/` if any
- [ ] Have the GitHub repo open in a second tab for the code section

---

## Script (timed)

### 00:00 — 00:15  ·  Intro (15 s)

> "Hi, this is the demo for *Receipt-to-Cashback*, the Capstone
> project I built for the Developers Institute GenAI bootcamp 2026.
> The slides have already covered the why and the pipeline — this is
> the *it works* part."

**Screen:** start on the deployed HF Spaces URL, Upload Receipt page.

---

### 00:15 — 01:15  ·  Live demo, upload flow (60 s)

> "I'm going to pick a sample receipt from the sidebar — this is one
> of CORD-v2's real photos from Indonesia."

**Action:** sidebar → Sample receipt → "CORD sample #1". Pause for
the progress bar.

> "While Gemini structures the items, what's happening is: EasyOCR
> already pulled the raw text, Gemini Flash Lite is now turning that
> into a JSON of items with prices and total, then FAISS will match
> each item against our 110-SKU catalog using a multilingual
> embedding."

**Wait for result.** When the metric appears:

> "There it is — 8 seconds end-to-end. Cashback is shown on the
> right, the line-by-line breakdown shows each item, the catalog
> category, the matched SKU, the rate and the dollar amount."

**Action:** scroll down to the table, then expand "Show Gemini
extraction JSON".

> "This is the structured JSON Gemini returned. Items, quantities,
> prices, currency, total. Schema-validated by Pydantic — if Gemini
> hallucinates a malformed payload, the app retries with a corrected
> prompt instead of crashing."

---

### 01:15 — 01:45  ·  B2B Analytics page (30 s)

**Action:** sidebar → Navigation → B2B Analytics.

> "This is the buyer-side view — what a brand or research firm would
> see when they buy data from us. Top: a synthetic 400-user
> population. Middle: an A/B test between 2% and 3% cashback —
> Welch's t-test recovers a ~29% lift in receipts per user per month
> at 3%, p-value below 0.05. Bottom: K-Means clustering of users by
> their category-spend shares, projected with PCA — four clean
> clusters matching the archetypes we generated from."

**Action:** scroll to show the cluster scatter + cluster centres
table.

---

### 01:45 — 02:00  ·  Ethics page (15 s)

**Action:** sidebar → Ethics.

> "Under this business model, ethics is in the app, not buried in the
> repo. Seven sections cover consent, privacy risk in receipt data,
> OCR bias against non-Latin scripts, and what we explicitly do *not*
> claim."

---

### 02:00 — 02:45  ·  Code highlights (45 s)

**Action:** switch tab to GitHub repo, open `src/cashback_engine.py`.

> "The CashbackEngine uses the Strategy pattern, so the day-7 A/B
> test swaps `FlatStrategy(0.02)` for `FlatStrategy(0.03)` without
> touching the engine. Seven unit tests cover the market-research
> semantics — including 'uncategorised lines still earn cashback'
> which is a feature not a bug."

**Action:** open `src/llm_extractor.py`, scroll to the prompt
template.

> "The LLM extractor uses a few-shot prompt with two CORD-style
> examples, then a strict Pydantic schema validates Gemini's
> response. If the JSON is malformed it retries once with the
> error injected into the prompt."

**Action:** open `src/vector_store.py`.

> "FAISS index over the catalog, built once at startup, queried in
> under a millisecond per item. We changed the embedding model
> mid-build from English-only MiniLM to the multilingual variant —
> that's what fixed the Indonesian-item rejection."

---

### 02:45 — 03:00  ·  Close (15 s)

**Action:** back to the deployed app, Upload Receipt page.

> "Live at the URL on the slides, source on GitHub. Both linked in
> the README. That's the demo — thanks."

---

## Editing notes

- Cut any silence longer than 1 s between sentences.
- If you flub a line, **don't restart** — just cut in Loom's editor.
  A re-take adds 20 minutes to your day for marginal polish.
- The first 5 seconds are the only ones most reviewers will fully
  watch attentively. Lead with what they need: "this is the demo for
  X, here's what works".

## Recovery plans if something breaks on the day

| What breaks | What to do |
|---|---|
| HF Spaces is cold and OCR takes 30+ s | Keep talking — the script's "while Gemini structures" line is long enough to cover it. |
| Gemini API rate-limited | Show the cached extraction JSON from a previous run (the app caches by image hash — second upload of the same image is instant). |
| HF Spaces is *down* | Run `streamlit run app/streamlit_app.py` locally and demo on `localhost:8501`. The recording doesn't have to be on the deployed URL. |
| OCR misreads everything on the chosen sample | Pick "CORD sample #2" or "#3" — they have different content. |
