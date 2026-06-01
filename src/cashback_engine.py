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
    total_spend: float
    total_cashback: float
    strategy: str

    @property
    def effective_rate(self) -> float:
        return self.total_cashback / self.total_spend if self.total_spend else 0.0

    @property
    def categorized_share(self) -> float:
        """Fraction of spend that was confidently mapped to a catalog category.

        This is the metric that matters for the data-sale side of the
        business — uncategorised spend is paid out but worth less.
        """
        if not self.total_spend:
            return 0.0
        cat_spend = sum(ln.line_total for ln in self.lines if ln.categorized)
        return cat_spend / self.total_spend


class CashbackEngine:
    """Compute cashback per line and aggregate it.

    Rules:
        * every priced line earns cashback (market-research model);
        * `MatchedLineItem.accepted` controls classification, not
          eligibility — uncategorised lines still pay out at the
          strategy's base rate, they are just labelled "uncategorized";
        * lines without a `line_total` (LLM could not read a price)
          contribute nothing — we do not invent prices.
    """

    def __init__(self, strategy: CashbackStrategy | None = None) -> None:
        self.strategy = strategy or FlatStrategy()

    def compute(self, matched: list[MatchedLineItem]) -> CashbackResult:
        lines: list[LineCashback] = []
        total_spend = 0.0
        total_cashback = 0.0

        for m in matched:
            price = m.line_total or 0.0
            rate = self.strategy.rate_for(m) if price > 0 else 0.0
            cashback = price * rate
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
            total_spend += price
            total_cashback += cashback

        return CashbackResult(
            lines=lines,
            total_spend=total_spend,
            total_cashback=total_cashback,
            strategy=self.strategy.name,
        )
