"""Unit tests for the CashbackEngine — pays on the grand total.

After the day-12 design fix, the engine pays cashback on the receipt's
**grand total** (what the user actually spent, including service +
tax). Items are extracted for the data product, not to compute the
payout. These tests pin that contract down.
"""

from __future__ import annotations

import unittest

from src.cashback_engine import (
    CashbackEngine,
    FlatStrategy,
    TieredStrategy,
    HALLUCINATION_RATIO,
)
from src.llm_extractor import LineItem
from src.matcher import MatchedLineItem
from src.vector_store import Match


def _matched(name, line_total, sku, category="food", rate=0.05, score=0.9, accepted=True):
    return MatchedLineItem(
        item=LineItem(name=name, quantity=1, unit_price=line_total, line_total=line_total),
        match=Match(
            sku=sku, name=name, category=category, subcategory="x",
            typical_price_usd=line_total, cashback_rate=rate, score=score,
        ),
        accepted=accepted,
    )


class TestFlatStrategyOnGrandTotal(unittest.TestCase):
    def test_pays_on_grand_total_when_declared(self):
        """Items sum to 1346, grand total 1591 (service + tax + rounding).
        Cashback at 2% should be on 1591, not on 1346."""
        engine = CashbackEngine(FlatStrategy(0.02))
        matched = [
            _matched("Item A", 1000.0, "X1", "food"),
            _matched("Item B",  346.0, "X2", "beverage"),
        ]
        result = engine.compute(matched, declared_total=1591.0)
        self.assertAlmostEqual(result.total_spend, 1591.0)
        self.assertAlmostEqual(result.total_cashback, 1591.0 * 0.02, places=4)
        self.assertEqual(result.line_sum, 1346.0)
        self.assertFalse(result.requires_review)

    def test_falls_back_to_line_sum_when_no_declared_total(self):
        engine = CashbackEngine(FlatStrategy(0.02))
        matched = [_matched("Item", 100.0, "X")]
        result = engine.compute(matched, declared_total=None)
        self.assertAlmostEqual(result.total_spend, 100.0)
        self.assertAlmostEqual(result.total_cashback, 2.0)

    def test_no_items_no_total_means_review(self):
        engine = CashbackEngine(FlatStrategy(0.02))
        result = engine.compute([], declared_total=None)
        self.assertTrue(result.requires_review)
        self.assertEqual(result.total_cashback, 0.0)

    def test_hallucination_ratio_triggers_review(self):
        """If line_sum is more than 2× grand total, the LLM probably
        duplicated items (or the grand total was misread). Refuse."""
        engine = CashbackEngine(FlatStrategy(0.02))
        matched = [_matched("Item", 2600.0, "X")]  # absurdly large
        result = engine.compute(matched, declared_total=1000.0)
        self.assertTrue(result.requires_review)
        self.assertEqual(result.total_cashback, 0.0)

    def test_within_ratio_does_not_review(self):
        """line_sum 1.5× declared total → still within ratio, pay
        normally on the declared total."""
        engine = CashbackEngine(FlatStrategy(0.02))
        matched = [_matched("Item", 1500.0, "X")]
        result = engine.compute(matched, declared_total=1000.0)
        self.assertFalse(result.requires_review)
        self.assertAlmostEqual(result.total_cashback, 20.0)


class TestTieredStrategyOnGrandTotal(unittest.TestCase):
    def test_tiered_uses_line_weighted_average(self):
        """Item food (rate 2.5%) for 60 + beverage (rate 2%) for 40.
        Weighted line rate = (60*0.025 + 40*0.02) / 100 = 0.023.
        Declared grand total = 110 (with tax). Cashback = 110 * 0.023 = 2.53."""
        engine = CashbackEngine(TieredStrategy())
        matched = [
            _matched("Pizza", 60.0, "FOOD1", "food"),
            _matched("Coke",  40.0, "BEV1",  "beverage"),
        ]
        result = engine.compute(matched, declared_total=110.0)
        self.assertAlmostEqual(result.total_cashback, 110.0 * 0.023, places=4)

    def test_misc_pulls_average_down(self):
        engine = CashbackEngine(TieredStrategy())
        matched = [
            _matched("Pizza",      80.0, "FOOD1", "food"),       # 2.5%
            _matched("Bag",         5.0, "MISC1", "misc"),       # 0%
        ]
        result = engine.compute(matched, declared_total=85.0)
        # weighted rate = (80*0.025 + 5*0) / 85 = 0.0235
        self.assertAlmostEqual(result.total_cashback, 85.0 * (80*0.025 + 5*0) / 85, places=4)


class TestPerLineView(unittest.TestCase):
    def test_per_line_breakdown_uses_line_totals_not_scaled(self):
        engine = CashbackEngine(FlatStrategy(0.02))
        matched = [
            _matched("Item A", 1000.0, "X1", "food"),
            _matched("Item B",  346.0, "X2", "beverage"),
        ]
        result = engine.compute(matched, declared_total=1591.0)
        # Per-line cashback stays based on each line's own price
        # (informational view, sums to less than total_cashback because
        # the grand-total gap goes into total_cashback only).
        per_line_sum = sum(ln.cashback for ln in result.lines)
        self.assertAlmostEqual(per_line_sum, 1346.0 * 0.02, places=4)
        self.assertGreater(result.total_cashback, per_line_sum)

    def test_categorized_share(self):
        engine = CashbackEngine(FlatStrategy(0.02))
        matched = [
            _matched("Iced Tea", 10.0, "BEV", accepted=True),
            _matched("OP CODE",   5.0, "X",   accepted=False),
        ]
        result = engine.compute(matched, declared_total=15.0)
        self.assertAlmostEqual(result.categorized_share, 10 / 15)


if __name__ == "__main__":
    unittest.main()
