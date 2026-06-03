# Pre-submission checklist — Demo Day 2026-06-11

The brief asks for four deliverable links on the platform submission form:

1. Deployed project URL
2. Deployed portfolio URL (GitHub Pages or similar)
3. 2-minute video presenting the project (Loom)
4. GitHub repo URL

Plus the in-room presentation. This checklist is what to verify *before*
hitting Submit.

---

## A. Code & repo

- [ ] `main` branch is green: tests pass (`python -m unittest tests.test_cashback_engine -v` → 7/7)
- [ ] No `.env` file in the repo (`git check-ignore -v .env` returns the gitignore line)
- [ ] No leaked API keys anywhere (`git grep -E "AQ\\.[A-Za-z0-9_-]+"` returns nothing)
- [ ] README's "Live demo" section has the HF Spaces URL filled in
- [ ] README's "Demo video" section has the Loom URL filled in
- [ ] At least 4 feature branches visible on GitHub (proves use of branches per brief)
- [ ] LICENSE file present (MIT)
- [ ] Latest commit on `main` is meaningful, not "wip" / "fix typo"

## B. Deployed app (HF Spaces)

- [ ] Space loads at the public URL without auth
- [ ] **Upload Receipt** page works with `CORD sample #1` end-to-end (~15-25 s on cold start)
- [ ] **B2B Analytics** page renders charts (sub-second; no Gemini call)
- [ ] **Ethics** page renders the markdown
- [ ] **About this project** page renders
- [ ] No `KeyError: GEMINI_API_KEY` in Space logs (means the secret is set)
- [ ] Space `README.md` (the one HF Spaces sees) is the project README, not a placeholder

## C. Demo video (Loom)

- [ ] Video is ≤ 3 minutes (brief says 2 min; we have headroom up to 4)
- [ ] First 10 seconds say what the project is and the live URL
- [ ] Shows the Upload → result flow end-to-end on a real sample
- [ ] Shows the B2B page
- [ ] Shows the Ethics tab (even if briefly)
- [ ] Audio is clear (re-record if there are audible cuts or breath gaps)
- [ ] Video is **public** (Loom default is org-private; toggle to public)
- [ ] URL pasted into README

## D. Presentation (PPT)

- [ ] Built from `presentation/PPT_OUTLINE.md` on the bootcamp template
- [ ] 8 slides, total speech ≤ 4 minutes when rehearsed twice
- [ ] QR codes on slide 1 actually resolve to the live URL + GitHub
- [ ] Screenshots on slide 5 are current (post-day-7 design, not the older mockup)
- [ ] Slide 6 (Honest challenges) names the 3 pivots concretely
- [ ] Slide 7 (Ethics) names at least 2 risks beyond "privacy"
- [ ] Slide 8 thanks Yossi by name
- [ ] PPT exported to PDF as a backup (in case the projector hates PowerPoint)
- [ ] PPT file committed to `presentation/` in the repo

## E. Project board (Trello)

- [ ] Trello board created from `docs/06_trello_cards.md`
- [ ] Link sent to Yossi via Slack
- [ ] At least one card per day, with day-1 to day-9 cards in **Done**
- [ ] One card per remaining day in **Doing** / **Backlog**

## F. Portfolio (optional but in the brief)

The brief asks for "a link to your deployed portfolio (can be GitHub Page)".
A minimum that satisfies this is your GitHub profile README. If your
`alexgl77/alexgl77` repo exists with a profile README, link that. If it
doesn't, **don't block the submission** — pin this Capstone repo to
your profile and link the profile URL.

- [ ] GitHub profile URL ready: https://github.com/alexgl77
- [ ] This Capstone repo pinned on the profile (Settings → Pin)
- [ ] (Optional, nice-to-have) Personal README repo created

## G. Day-of-demo rehearsal

- [ ] Full rehearsal #1: PPT only, with stopwatch. Target ≤ 4 min.
- [ ] Full rehearsal #2: PPT + video + Q&A simulation. Target ≤ 10 min.
- [ ] Practiced one answer per likely jury question:
  - "Why did you change the business model?"
  - "Why FAISS instead of just SQL LIKE?"
  - "How would you handle thousands of receipts/minute?"
  - "What is k-anonymity and why does it matter here?"
  - "Why no CNN if the brief mentions deep learning?"

## H. Backup plans (don't get caught)

- [ ] **App backup:** `streamlit run app/streamlit_app.py` works locally
      (in case HF Spaces is down on demo day)
- [ ] **Sample receipts backup:** at least 3 CORD samples cached locally
      so the demo doesn't need internet to pull from HF Hub
- [ ] **Gemini backup:** local `.env` has a working key; if the Space's
      secret breaks, switch to local demo
- [ ] **PPT backup:** PDF on USB drive

---

## Submission form fields (what to paste)

| Form field | Value |
|---|---|
| Deployed project URL | `https://huggingface.co/spaces/alexgl77/receipt-to-cashback` |
| Deployed portfolio URL | `https://github.com/alexgl77` (or your personal README) |
| Video link | Your Loom URL |
| GitHub repo link | `https://github.com/alexgl77/receipt-to-cashback` |

Only hit Submit once every box above is ticked.
