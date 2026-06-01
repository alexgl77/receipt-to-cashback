"""Compute cashback from matched line items.

Step [5] of the spine — the last bit of business logic before the UI:
    image -> OCR -> LLM JSON -> FAISS match -> [CASHBACK] -> Streamlit

Two cashback strategies are supported. The strategy is a constructor
argument so day 7 can A/B-test them without touching the engine code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

from src.matcher import MatchedLineItem

StrategyName = Literal["per_sku", "flat"]


class CashbackStrategy(Protocol):
    name: str

    def rate_for(self, m: MatchedLineItem) -> float: ...


class PerSkuStrategy:
    """Use the per-SKU rate stored in the catalog row that FAISS picked."""

    name = "per_sku"

    def rate_for(self, m: MatchedLineItem) -> float:
        return m.match.cashback_rate if m.accepted else 0.0


class FlatStrategy:
    """Flat percentage for any accepted match, zero for the rest."""

    def __init__(self, flat_rate: float = 0.03) -> None:
        self.flat_rate = flat_rate
        self.name = f"flat_{int(flat_rate * 100)}pct"

    def rate_for(self, m: MatchedLineItem) -> float:
        return self.flat_rate if m.accepted else 0.0


@dataclass
class LineCashback:
    item_name: str
    matched_sku: str
    line_total: float
    rate: float
    cashback: float
    accepted: bool


@dataclass
class CashbackResult:
    lines: list[LineCashback]
    total_spend: float
    total_cashback: float
    strategy: str

    @property
    def effective_rate(self) -> float:
        return self.total_cashback / self.total_spend if self.total_spend else 0.0


class CashbackEngine:
    """Compute cashback per line and aggregate it.

    Lines without a `line_total` (LLM couldn't read the price) contribute
    nothing; we don't guess prices. Lines below the matcher's score
    threshold contribute nothing either, even if they have a price.
    """

    def __init__(self, strategy: CashbackStrategy | None = None) -> None:
        self.strategy = strategy or PerSkuStrategy()

    def compute(self, matched: list[MatchedLineItem]) -> CashbackResult:
        lines: list[LineCashback] = []
        total_spend = 0.0
        total_cashback = 0.0

        for m in matched:
            price = m.line_total or 0.0
            rate = self.strategy.rate_for(m) if price > 0 else 0.0
            cashback = price * rate

            lines.append(LineCashback(
                item_name=m.item.name,
                matched_sku=m.match.sku,
                line_total=price,
                rate=rate,
                cashback=cashback,
                accepted=m.accepted,
            ))
            total_spend += price
            total_cashback += cashback

        return CashbackResult(
            lines=lines,
            total_spend=total_spend,
            total_cashback=total_cashback,
            strategy=self.strategy.name,
        )
