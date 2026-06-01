# Data

## Receipts dataset — CORD-v2

- **Source:** [`naver-clova-ix/cord-v2`](https://huggingface.co/datasets/naver-clova-ix/cord-v2) on Hugging Face
- **Why this one (not SROIE):** SROIE 2019 only annotates 4 fields (company, date, address, total) — no line items, no product names. CORD-v2 ships JSON ground truth that includes each line item's name, quantity and price, which is exactly what we need to evaluate the OCR → LLM → FAISS matching pipeline.
- **Splits:** train (800) · validation (100) · test (100) — 1000 receipts total
- **Format:** each example has an `image` (PIL PNG) and a `ground_truth` (JSON string with `gt_parse.menu[]` items)
- **Domain:** restaurants, bakeries, cafés, small markets — mostly South-East Asian (Indonesia/Korea), items in a mix of English and transliterated Indonesian/Korean
- **License:** CC BY 4.0
- **Storage:** the dataset is cached at `~/.cache/huggingface/hub/datasets--naver-clova-ix--cord-v2/` — **not committed to this repo**. Re-download with `load_dataset("naver-clova-ix/cord-v2")` from the `datasets` library.

### Example ground-truth structure

```json
{
  "gt_parse": {
    "menu": [
      {"nm": "Nasi Campur Bali", "cnt": "1 x", "price": "75,000"},
      {"nm": "Ice Lemon Tea",   "cnt": "1 x", "price": "24,000"}
    ],
    "total": {"total_price": "261,000"}
  }
}
```

## Product catalog — `catalog.csv`

- **What:** 110 generic Food & Beverage SKUs covering the categories that appear in CORD-v2 (beverages, food, bakery, dessert, snack, packaging)
- **Why generic F&B (not retail brands like Coca-Cola/Lay's):** CORD-v2 receipts are dominated by restaurant/café/bakery items in English + transliterated Indonesian ("Nasi Putih", "TWIST DONUT", "ICED TEA"). A retail brand catalog wouldn't match. A semantic FAISS lookup over generic F&B labels does match — e.g. "Nasi Putih" (Indonesian for "white rice") → `White Rice`, "TWIST DONUT" → `Donut`.
- **Schema:**
  - `sku` — unique identifier (e.g. `BEV001`, `FOOD025`)
  - `name` — display name, used as the text to embed for FAISS
  - `category` — `beverage` · `food` · `bakery` · `dessert` · `snack` · `misc`
  - `subcategory` — finer grouping (e.g. `coffee`, `pizza`, `donut`)
  - `typical_price_usd` — for the A/B-test simulation
  - `cashback_rate` — default reward per SKU, used by `CashbackEngine`; zero for alcohol and packaging (regulatory / non-rewardable items)

### Quick stats

| Category | Count |
|---|---|
| food | 50 |
| beverage | 26 |
| bakery | 16 |
| dessert | 8 |
| snack | 5 |
| misc | 5 |
| **Total** | **110** |

Price range: $0.10 – $18.00 USD.
Cashback rates: 0%, 2%, 3%, 4%, 5%.
