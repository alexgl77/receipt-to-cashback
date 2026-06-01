"""Unit tests for the CashbackEngine.

Why this file exists: the brief asks for a `tests/` folder and at least
one passing test. The CashbackEngine is the right thing to unit-test
because it's pure logic (no network, no models) and it's where a bug
would silently corrupt the user-visible number.
"""

from __future__ import annotations

import unittest

from src.cashback_engine import (
    CashbackEngine,
    FlatStrategy,
    PerSkuStrategy,
)
from src.llm_extractor import LineItem
from src.matcher import MatchedLineItem
from src.vector_store import Match


def _matched(name, line_total, sku, rate, score, accepted=True) -> MatchedLineItem:
    return MatchedLineItem(
        item=LineItem(name=name, quantity=1, unit_price=line_total, line_total=line_total),
        match=Match(
            sku=sku, name=name, category="food", subcategory="x",
            typical_price_usd=line_total, cashback_rate=rate, score=score,
        ),
        accepted=accepted,
    )


class TestPerSkuStrategy(unittest.TestCase):
    def test_sums_per_line_cashback(self):
        engine = CashbackEngine(PerSkuStrategy())
        matched = [
            _matched("Iced Tea",     10.0, "BEV003", 0.03, 0.9),
            _matched("Margherita",   20.0, "FOOD011", 0.05, 0.95),
        ]
        result = engine.compute(matched)
        self.assertAlmostEqual(result.total_spend, 30.0)
        # 10 * 3% + 20 * 5% = 0.30 + 1.00 = 1.30
        self.assertAlmostEqual(result.total_cashback, 1.30, places=5)
        self.assertEqual(result.strategy, "per_sku")

    def test_rejected_match_contributes_zero(self):
        engine = CashbackEngine(PerSkuStrategy())
        matched = [
            _matched("Iced Tea",     10.0, "BEV003", 0.03, 0.9, accepted=True),
            _matched("OP CODE 12",    5.0, "MISC001", 0.00, 0.20, accepted=False),
        ]
        result = engine.compute(matched)
        # the rejected line still counts toward total spend
        self.assertAlmostEqual(result.total_spend, 15.0)
        # but only the accepted line earns cashback
        self.assertAlmostEqual(result.total_cashback, 0.30, places=5)

    def test_missing_price_is_treated_as_zero(self):
        engine = CashbackEngine(PerSkuStrategy())
        matched = [
            MatchedLineItem(
                item=LineItem(name="No Price", quantity=1, unit_price=None, line_total=None),
                match=Match(sku="X", name="X", category="food", subcategory="x",
                            typical_price_usd=0, cashback_rate=0.05, score=0.9),
                accepted=True,
            )
        ]
        result = engine.compute(matched)
        self.assertEqual(result.total_spend, 0.0)
        self.assertEqual(result.total_cashback, 0.0)


class TestFlatStrategy(unittest.TestCase):
    def test_flat_rate_applies_to_all_accepted(self):
        engine = CashbackEngine(FlatStrategy(flat_rate=0.04))
        matched = [
            _matched("Iced Tea",     10.0, "BEV003", 0.03, 0.9),
            _matched("Margherita",   20.0, "FOOD011", 0.05, 0.95),
        ]
        result = engine.compute(matched)
        # 30 spend * 4% flat = 1.20 (note: PerSku would have been 1.30)
        self.assertAlmostEqual(result.total_cashback, 1.20, places=5)
        self.assertEqual(result.strategy, "flat_4pct")

    def test_effective_rate_reflects_strategy(self):
        engine = CashbackEngine(FlatStrategy(flat_rate=0.02))
        matched = [_matched("Iced Tea", 50.0, "BEV003", 0.03, 0.9)]
        result = engine.compute(matched)
        self.assertAlmostEqual(result.effective_rate, 0.02, places=5)


if __name__ == "__main__":
    unittest.main()
