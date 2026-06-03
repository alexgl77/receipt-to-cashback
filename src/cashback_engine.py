"""Compute cashback from extracted receipt items.

**Business model (this is what the math reflects):**

We are a market-research company. We pay users a flat cashback on
every valid purchase in exchange for their itemised consumption data,
which we then anonymise and sell in aggregate. The cashback is the
*price we pay for the data*, not a partner-funded rebate. Therefore:

* every line with a printed price earns cashback, regardless of
  whether we can map it to a catalog SKU;
* the catalog exists to **classify** the spend (food / beverage /
  bakery / …) so the data we sell is enriched and segmentable, not
  to gate eligibility.

Two strategies are exposed so day 7 can A/B-test cashback rates
(e.g. 2 % vs 3 %) — both are *flat across the receipt*; the only
question is what flat rate maximises user acquisition without burning
margin.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.matcher import MatchedLineItem


class CashbackStrategy(Protocol):
    name: str

    def rate_for(self, m: MatchedLineItem) -> float: ...


class FlatStrategy:
    """Single flat rate applied to every priced line on the receipt.

    This is the default. It reflects the market-research model: we pay
    per receipt scanned, not per partner SKU.
    """

    def __init__(self, flat_rate: float = 0.02) -> None:
        self.flat_rate = flat_rate
        self.name = f"flat_{flat_rate * 100:g}pct"

    def rate_for(self, m: MatchedLineItem) -> float:
        return self.flat_rate


class TieredStrategy:
    """Flat rate that varies by inferred category (food vs beverage vs …).

    Used in the day-7 A/B test to check whether category-aware
    incentives drive different basket composition. Falls back to a
    base rate when the matcher could not classify the line.
    """

    def __init__(
        self,
        rates_by_category: dict[str, float] | None = None,
        base_rate: float = 0.02,
    ) -> None:
        self.rates_by_category = rates_by_category or {
            "food": 0.025,
            "beverage": 0.02,
            "bakery": 0.025,
            "dessert": 0.02,
            "snack": 0.015,
            "misc": 0.0,  # plastic bags etc. — no data value, no payout
        }
        self.base_rate = base_rate
        self.name = "tiered"

    def rate_for(self, m: MatchedLineItem) -> float:
        if not m.accepted:
            return self.base_rate
        return self.rates_by_category.get(m.match.category, self.base_rate)


@dataclass
class LineCashback:
    item_name: str
    matched_sku: str
    category: str            # "food", "beverage", … or "uncategorized"
    line_total: float
    rate: float
    cashback: float
    categorized: bool        # True if FAISS matched with confidence


@dataclass
class CashbackResult:
    lines: list[LineCashback]
    total_spend: float            # what we actually pay cashback on
    total_cashback: float
    strategy: str
    line_sum: float               # raw sum of line_totals (may differ from total_spend if total_was_corrected)
    declared_total: float | None  # the grand total the LLM extracted from the receipt
    total_was_corrected: bool     # True if we trusted declared_total over line_sum due to >10% drift
    drift_pct: float | None       # signed (line_sum - declared) / declared

    @property
    def effective_rate(self) -> float:
        return self.total_cashback / self.total_spend if self.total_spend else 0.0

    @property
    def categorized_share(self) -> float:
        """Fraction of spend that was confidently mapped to a catalog category.

        Based on `line_sum` (the unscaled raw line totals), not the
        possibly-corrected `total_spend`. Otherwise a correction would
        silently change the categorisation quality reported to buyers.
        """
        if not self.line_sum:
            return 0.0
        cat_spend = sum(ln.line_total for ln in self.lines if ln.categorized)
        return cat_spend / self.line_sum


class CashbackEngine:
    """Compute cashback per line and aggregate it.

    Rules:
        * every priced line earns cashback (market-research model);
        * `MatchedLineItem.accepted` controls classification, not
          eligibility — uncategorised lines still pay out at the
          strategy's base rate, they are just labelled "uncategorized";
        * lines without a `line_total` (LLM could not read a price)
          contribute nothing — we do not invent prices.

    **Total-drift guard:** if the receipt-level `declared_total` is
    given and disagrees with the sum of line totals by more than
    `drift_tolerance` (default 10%), we trust the declared total and
    scale cashback to match. Without this, an LLM that duplicates an
    item or counts the subtotal as a line item silently makes us
    over-pay — see day-10.5 rehearsal incident on CORD train[0]
    (line_sum = 2.72M IDR vs grand total 1.59M IDR, ~70% over).
    Documented as a real case in `docs/04_ethics.md`.
    """

    def __init__(
        self,
        strategy: CashbackStrategy | None = None,
        drift_tolerance: float = 0.10,
    ) -> None:
        self.strategy = strategy or FlatStrategy()
        self.drift_tolerance = drift_tolerance

    def compute(
        self,
        matched: list[MatchedLineItem],
        declared_total: float | None = None,
    ) -> CashbackResult:
        # First pass: per-line numbers at the raw line totals.
        line_records: list[tuple[MatchedLineItem, float, float]] = []
        line_sum = 0.0
        for m in matched:
            price = m.line_total or 0.0
            rate = self.strategy.rate_for(m) if price > 0 else 0.0
            line_records.append((m, price, rate))
            line_sum += price

        # Drift guard: if declared_total is present and the line sum
        # disagrees by more than the tolerance, scale cashback so the
        # effective spend is the declared total. We do NOT rewrite each
        # line's printed total — the user can still inspect the raw
        # extraction — we only correct the *aggregate* cashback.
        drift_pct: float | None = None
        total_was_corrected = False
        scale = 1.0
        if declared_total and declared_total > 0 and line_sum > 0:
            drift_pct = (line_sum - declared_total) / declared_total
            if abs(drift_pct) > self.drift_tolerance:
                scale = declared_total / line_sum
                total_was_corrected = True

        # Second pass: write LineCashback rows with the (possibly scaled) cashback.
        lines: list[LineCashback] = []
        total_cashback = 0.0
        for m, price, rate in line_records:
            cashback = price * rate * scale
            category = m.match.category if m.accepted else "uncategorized"
            sku = m.match.sku if m.accepted else "—"

            lines.append(LineCashback(
                item_name=m.item.name,
                matched_sku=sku,
                category=category,
                line_total=price,
                rate=rate,
                cashback=cashback,
                categorized=m.accepted,
            ))
            total_cashback += cashback

        total_spend = declared_total if total_was_corrected else line_sum

        return CashbackResult(
            lines=lines,
            total_spend=total_spend,
            total_cashback=total_cashback,
            strategy=self.strategy.name,
            line_sum=line_sum,
            declared_total=declared_total,
            total_was_corrected=total_was_corrected,
            drift_pct=drift_pct,
        )
