# Final Project Proposal — Receipt-to-Cashback

> Borrador para enviar a Yossi vía el Final Project Proposal Form. Copia y pega los campos que el formulario pida.

---

## Project name

**Receipt-to-Cashback** — A GenAI-powered cashback app that turns paper receipts into structured purchase data.

---

## One-line description

Upload a photo of a receipt, get cashback. The app validates the image with a CNN, extracts text with OCR, structures it with an LLM, matches items against a product catalog using vector search, and computes the reward.

---

## Motivation

Cashback apps already exist (Fintonic, Beruby, Rappi rewards), but most rely on credit card data or partnership APIs with merchants. There is no easy way for a small player to bootstrap a cashback product *without* those partnerships. This project explores whether a **pure computer-vision + LLM pipeline** can replace the merchant-API dependency by directly reading the receipt the user already has.

The business value, if it works, is twofold:
1. **B2C:** users get cashback on any purchase, anywhere.
2. **B2B:** the aggregated, anonymised consumption data is valuable to market-research firms — but this raises serious ethical questions (covered in the ethics doc).

---

## Target users

- **Primary:** consumers who want to maximise rewards across all their purchases, not just where their bank/app has partnerships.
- **Secondary:** market-research firms interested in real (not survey-based) consumption patterns.

---

## Problem it solves

Current cashback ecosystems are fragmented. A user must check whether their merchant is in their bank's program, their delivery app's program, etc. A receipt-based system is universal: if the user got a printed (or digital) receipt, they get the reward.

---

## What I will build (functional scope)

A Streamlit web app with:

1. **Upload page:** user takes/uploads a photo of a receipt.
2. **Processing pipeline:**
   - CNN classifier (MobileNetV2 fine-tuned) → "is this a receipt? what type of store?"
   - OCR (TrOCR/Donut, pre-trained) → raw text.
   - LLM extractor (Gemini 2.0 Flash with few-shot prompts) → structured JSON {items, prices, date, total}.
   - FAISS vector search → match each item line against a generic catalog of ~100 international products.
   - Python `CashbackEngine` (OOP) → applies business rules and returns the cashback amount.
3. **User dashboard:** receipt history, total cashback, breakdown by category.
4. **B2B analytics page:** k-means clustering of (simulated) users by spending pattern + A/B-test simulation of two cashback strategies (fixed % vs category-based %).
5. **Ethics section** in the README and the app itself.

---

## Technologies and where they come from in the bootcamp

| Notion required by the brief | How I cover it | Bootcamp source |
|---|---|---|
| Python OOP, functions, loops | `Receipt`, `Catalog`, `CashbackEngine`, `OCRPipeline` classes | Week 1-2 |
| Data wrangling (pandas, matplotlib, seaborn) | EDA notebook + analytics dashboard | Week 3-4 |
| Stats / ML (classification) | LogisticRegression: "valid receipt vs duplicate/suspect" | Week 5 |
| Clustering | K-Means on user spending vectors | Week 4-5 |
| A/B testing | Simulated A/B + t-test or chi-squared | Week 5 stats |
| Deep learning (CNN) | MobileNetV2 with transfer learning, multi-class image classifier | Week 6 Day 2 |
| NLP (tokenize, vectorize) | Preprocessing of OCR output before matching | Week 8 Day 1 |
| Pre-trained model | TrOCR/Donut (vision) + Gemini 2.0 Flash (LLM) | Week 7-8 |
| Vector DB | FAISS over sentence-transformer embeddings of the catalog | Week 8 Day 2 |
| Prompt engineering | Few-shot + chain-of-thought for JSON extraction | Week 9 |
| Streamlit/Gradio | Streamlit app | Self-taught |
| Ethical reflection | Dedicated `docs/04_ethics.md` + section in app | Transversal |

**Coverage: 10 out of 10 points from the brief.**

---

## Dataset

- **Training / evaluation / demo:** SROIE 2019 (Scanned Receipts OCR and Information Extraction) — public benchmark with hundreds of annotated receipts, used as the single source of truth for both development and demonstration. Keeps the project reproducible and avoids the noise of one-off real photos.
- **Catalog:** synthetic, ~100 generic international products (Coca-Cola, Pepsi, Lay's, Colgate, Heinz, etc.) with categories and brands. Chosen for coherence with SROIE's English-language receipts so the FAISS semantic match is meaningful in the demo.

---

## Deliverables

- [ ] Public GitHub repo with branches (one per major component) and a template-style README
- [ ] Deployed Streamlit app with a public URL (Streamlit Cloud or Hugging Face Spaces)
- [ ] Loom video (3 min) of the demo
- [ ] PPT using the bootcamp template
- [ ] Trello board kept up to date
- [ ] Unit test for the `CashbackEngine`

---

## Timeline (10 days, demo on 2026-06-11)

| Day | Date | Focus |
|---|---|---|
| 1 | 06-01 | Proposal + repo + Trello + dataset download |
| 2 | 06-02 | EDA + synthetic catalog |
| 3 | 06-03 | OCR pipeline |
| 4 | 06-04 | LLM extractor + few-shot prompts |
| 5 | 06-05 | CNN training + FAISS matcher + deploy decision |
| 6 | 06-06 | CashbackEngine + Streamlit MVP |
| 7 | 06-07 | Clustering, A/B, validity classifier, B2B view |
| 8 | 06-08 | Deploy + final README + ethics |
| 9 | 06-09 | PPT + Loom video + rehearsal |
| 10 | 06-10 | Buffer + submit |
| 11 | 06-11 | **Demo Day** |

---

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| OCR on thermal-paper receipts is unreliable | Train and evaluate on the cleaner SROIE dataset first; real Chilean receipts are for the final demo only |
| LLM returns invalid JSON | Pydantic schema + retry with corrected prompt |
| CNN takes too long to train | Transfer learning, freeze backbone, fine-tune only the classification head; use Colab if needed |
| Deployment runs out of memory | LLM via API (not local), small OCR model, fallback to Hugging Face Spaces |
| Scope creep | The Week 10 agentic AI bonus is added only if everything else is done by day 8 |
