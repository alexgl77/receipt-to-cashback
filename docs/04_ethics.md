# Ethics

The business model of *Receipt-to-Cashback* is **paying users for the
right to sell their itemised consumption data in aggregate**. Every
design and technical decision in this repo has to be defended against
that statement. The honest list:

---

## 1. Informed consent — what the user is actually selling

The reward (a few percent cashback) is the most visible part of the
deal; the value the platform extracts (an itemised record of what,
where and when the user buys) is the *unstated* part. A consent banner
that says "we may use your data to improve the service" is *not*
informed consent for monetisation.

**What we would require before any production launch:**

- A plain-language summary at signup describing *exactly* what
  categories of buyers receive the data (research firms, brand
  marketing, retail chains) and what they can infer from it.
- A separate opt-in for **identifiable** data versus **anonymised
  aggregate** data, with the cashback rate honest about which one the
  user opted into.
- One-tap data export and deletion. The right to be forgotten is not
  optional — if the user revokes consent, their per-receipt records
  are deleted from the warehouse, not just from the user-facing app.

---

## 2. Privacy risk — what receipt data exposes

A receipt looks innocuous but reveals a lot when aggregated:

- **Medication purchases** infer chronic conditions, mental-health
  treatment, pregnancy and family planning.
- **Time-of-day plus merchant** reconstructs commute and routine.
- **Alcohol and tobacco lines** are sensitive in many jurisdictions
  (employment, insurance).
- **Receipt photos** retain the merchant address and sometimes the
  user's name/loyalty number in the header, which the OCR captures
  but our pipeline currently drops only by accident, not by design.

**Mitigations the current code already implements:**

- The Pydantic `ReceiptExtraction` schema only persists `items`,
  `total`, `currency`, `merchant`, `date` — never the cardholder
  details that sometimes appear at the top of a receipt.
- Free-text loyalty numbers do not survive the LLM extractor.

**What we would still need before a real launch:**

- An explicit redaction step that scans both the OCR text *and* the
  uploaded image for cardholder data, addresses and identifiers, and
  redacts both before either persists.
- A k-anonymity check at sale time: no slice we sell can be a
  population of fewer than *k* users (typical k=50). This stops
  buyers from re-identifying users by intersecting our slices with
  external data they already hold.

---

## 3. OCR bias

EasyOCR's detector and recogniser were trained predominantly on
Latin-script text. The multilingual sentence-transformer we switched
to in day 6.5 covers downstream classification, but it cannot rescue
an OCR step that did not see the characters.

**Consequences:**

- Receipts in scripts the OCR was not trained on (Arabic, Thai,
  Burmese, Khmer) are likely to be silently dropped or cashback
  refunded at zero, which structurally **disadvantages users in those
  regions**.
- Thermal-paper receipts in any script age poorly. Lower-income
  users are over-represented among holders of receipts that have
  been carried in a wallet for days — they are systematically
  *more* likely to fail OCR than receipts from a salaried customer
  who scans them the same day.

**Mitigation:**

- Per-language quality metrics published in the public model card.
- A floor on cashback (e.g. fixed minimum per accepted upload)
  rather than a pure per-line model, to make the OCR-failure tax
  flatter across cohorts.

---

## 4. LLM hallucination — under-paying vs over-paying

Gemini's structured output reduces but does not eliminate the risk of
hallucinating a line item, a price or a total. Two error modes have
different ethical weight:

| Failure | Who bears the cost | Severity |
|---|---|---|
| LLM invents an item that wasn't on the receipt | The platform overpays cashback | Acceptable; we eat the cost. |
| LLM drops a line that *was* on the receipt | The user is silently underpaid | **Not acceptable.** |

**Update (day 10.5):** the over-paying variant of this failure
mode actually showed up during rehearsal. CORD train[0] has items
with quantities ("3 x Bbk Panggang", "2 x Tahu Goreng", "3 x Free
Ice Tea") and a couple of items that appear twice in the OCR; the
LLM extractor counted some of them double, returning a `line_sum`
of ~2.72 M IDR against a declared Grand Total of ~1.59 M IDR — a
70 % over-count. At 2 % cashback that's an extra ~22,000 IDR paid
out per receipt.

The first fix shipped a **drift guard**: `CashbackEngine` takes the
receipt's declared `total` and, when `|line_sum − declared| /
declared > 10 %`, scales the cashback to match the declared total
and surfaces a yellow warning in the UI.

**Update (day 10.6):** the *next* rehearsal exposed the inverse
failure. The LLM dropped the leading million when reading
"1,591,600" and returned a declared total of 591,600 IDR — while
the line sum stayed at ~2.62 M IDR (still inflated by duplicates).
The drift guard, trusting the declared total, silently
**under-paid** the user by ~20,000 IDR. *This is the not-acceptable
case the section above warns about.*

The second fix splits the guard into two tiers:

* **Moderate drift (10–50 %):** trust the declared total, scale
  cashback, show a yellow warning. As before.
* **Extreme drift (> 50 %):** refuse to pay any cashback. Surface
  a red error explaining that the receipt is held for review.
  Better an angry user re-uploading than a silently under-paid
  one — and the data we collect on disputed receipts becomes a
  training signal for the OCR/LLM pipeline.

This is also the policy under which the platform can be **audited
honestly**: a regulator can verify that no cashback is ever paid
when our own validation says we don't know the right number.

---

## 5. Selling data ≠ selling demographics

The pitch ("we sell aggregated consumption data") is socially closer
to grocery-loyalty data than to ad-tech tracking. Where it crosses
into uncomfortable territory:

- **Combining categories that look harmless individually**: a brand
  buying "users who bought baby formula in Q2 + alcoholic beverages
  in the same quarter" can infer high-risk household behaviour that
  the user did not consent to surface.
- **Geo + time + spend** is a tracking primitive in disguise.

**Policy guard-rails we would adopt:**

- Forbid joining sales-side queries across categories deemed
  sensitive (pharma, alcohol, tobacco, baby/family planning) without
  case-by-case review.
- Forbid selling at temporal/geographic resolutions finer than
  monthly + city-level — the cell sizes must stay above the
  k-anonymity floor.

---

## 6. Who can audit us

A platform that sells consumption data needs to be **auditable** by
someone other than the founders. Concretely:

- An external DPA (data protection authority) review of the data
  sale flow once per year.
- A public *transparency report*: number of receipts processed,
  number of buyers, categories of data sold, deletion requests
  honoured.
- A bug-bounty programme that explicitly rewards privacy-leak
  findings, not just availability bugs.

---

## 7. What we are *not* claiming

- We are not claiming that the EasyOCR + Gemini + FAISS pipeline is
  more accurate than a state-of-the-art document-understanding
  model. It is the right complexity for a 10-day capstone build.
- We are not claiming the cashback rates in the A/B simulation are
  empirically grounded; they are explicitly synthetic, generated
  with a known multiplicative lift, and the simulation is honest
  about that in `src/synthetic_users.py`.
- We are not claiming that this README + a privacy-policy page would
  make the product legally compliant in any jurisdiction; it would
  need a real DPIA (data-protection impact assessment) before launch.

---

## TL;DR

The honest one-liner: *the cashback is a small payment for the right
to sell a detailed picture of someone's monthly consumption to people
they will never meet*. Build the consent flow, the redaction step and
the k-anonymity check before you build anything else, or do not ship.
