"""Compute cashback from extracted receipt items.

**Business model recap (what the math reflects):**

We are a market-research company. We pay users a flat cashback on
every valid purchase in exchange for their itemised consumption data,
which we then anonymise and sell in aggregate. The cashback is the
*price we pay for the data*, not a partner-funded rebate.

**Math rule (kept simple, after a day-12 design fix):**

Cashback is paid on the **grand total** the receipt prints — that's
what the user actually spent, and that's what they expect cashback
on. Items are extracted for the *data product* (we sell category
breakdowns to brands), not to compute the payout.

This sidesteps the trap of treating the gap between subtotal and
grand total (service charge + tax + rounding, normal on every
restaurant receipt) as a bug.

**Sanity guard — kept, but narrow:** if the LLM clearly hallucinated
items (line sum more than 2× the grand total) or could not read the
grand total at all, we refuse to pay and flag the receipt for review.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.matcher import MatchedLineItem

# If line_sum / declared_total exceeds this, something is very wrong
# (LLM duplicated many items, or grand-total was misread as a tiny
# number). Refuse cashback for review.
HALLUCINATION_RATIO = 2.0


class CashbackStrategy(Protocol):
    name: str

    def rate_for(self, m: MatchedLineItem) -> float: ...


class FlatStrategy:
    """Single flat rate applied to the grand-total spend."""

    def __init__(self, flat_rate: float = 0.02) -> None:
        self.flat_rate = flat_rate
        self.name = f"flat_{flat_rate * 100:g}pct"

    def rate_for(self, m: MatchedLineItem) -> float:
        return self.flat_rate


class TieredStrategy:
    """Per-category rate, used for the day-7 A/B simulation.

    The rate is read off each matched line's catalog category.
    When the total-level cashback is what we pay out, this becomes
    a weighted average across categories at the line level (handled
    in `CashbackEngine.compute` below).
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
    total_spend: float            # what the user paid (= grand total when known)
    total_cashback: float         # 0 if requires_review
    strategy: str
    line_sum: float               # subtotal: raw sum of line_totals
    declared_total: float | None  # grand total the model extracted from the receipt
    requires_review: bool = False  # True when we can't trust the receipt at all

    @property
    def effective_rate(self) -> float:
        return self.total_cashback / self.total_spend if self.total_spend else 0.0

    @property
    def categorized_share(self) -> float:
        """Fraction of *subtotal* spend that was confidently mapped to
        a catalog category. Used by data buyers to value the receipt."""
        if not self.line_sum:
            return 0.0
        cat_spend = sum(ln.line_total for ln in self.lines if ln.categorized)
        return cat_spend / self.line_sum


class CashbackEngine:
    """Compute cashback off the **grand total** (what the user spent).

    Rules:
        * Cashback amount = grand-total × effective rate. The effective
          rate is the line-weighted average of the strategy's per-line
          rates (so TieredStrategy still works correctly — food earns
          food's rate even when paid against the grand total).
        * If `declared_total` is missing, we fall back to the sum of
          line items (best guess) and flag review.
        * If line_sum > declared_total × HALLUCINATION_RATIO (2×), the
          LLM probably duplicated items or the grand total was misread
          as a tiny number. We refuse to pay and flag review.
        * Lines without a `line_total` contribute nothing — we do not
          invent prices.
    """

    def __init__(self, strategy: CashbackStrategy | None = None) -> None:
        self.strategy = strategy or FlatStrategy()

    def compute(
        self,
        matched: list[MatchedLineItem],
        declared_total: float | None = None,
    ) -> CashbackResult:
        line_records: list[tuple[MatchedLineItem, float, float]] = []
        line_sum = 0.0
        weighted_cb_at_line_rates = 0.0

        for m in matched:
            price = m.line_total or 0.0
            rate = self.strategy.rate_for(m) if price > 0 else 0.0
            line_records.append((m, price, rate))
            line_sum += price
            weighted_cb_at_line_rates += price * rate

        # --- Decide what "total_spend" is -----------------------------------
        requires_review = False
        if declared_total and declared_total > 0:
            total_spend = declared_total
            # Sanity: catastrophic line-sum vs declared mismatch implies
            # the LLM hallucinated items or misread the grand total.
            if line_sum > 0 and line_sum / declared_total > HALLUCINATION_RATIO:
                requires_review = True
        elif line_sum > 0:
            # No grand total available — best guess is the subtotal.
            total_spend = line_sum
        else:
            # Nothing to pay on.
            total_spend = 0.0
            requires_review = True

        # --- Compute aggregate cashback -------------------------------------
        if requires_review:
            total_cashback = 0.0
            effective_rate_for_lines = 0.0
        else:
            # Per-line effective rate as a line-weighted average, applied
            # to the grand total. If declared_total > line_sum (the
            # normal case: service + tax + rounding push it up), the
            # gap is paid at the same average rate the items would have
            # earned. This lets a TieredStrategy keep its meaning.
            effective_rate_for_lines = (
                weighted_cb_at_line_rates / line_sum if line_sum else 0.0
            )
            total_cashback = total_spend * effective_rate_for_lines

        # --- Build per-line view (informational; uses line totals as-is) ---
        lines: list[LineCashback] = []
        for m, price, rate in line_records:
            cashback = 0.0 if requires_review else price * rate
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

        return CashbackResult(
            lines=lines,
            total_spend=total_spend,
            total_cashback=total_cashback,
            strategy=self.strategy.name,
            line_sum=line_sum,
            declared_total=declared_total,
            requires_review=requires_review,
        )
