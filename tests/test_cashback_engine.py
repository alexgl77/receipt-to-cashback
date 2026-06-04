"""Unit tests for the CashbackEngine under the market-research model.

Business model assumptions encoded in these tests:

* every priced line earns cashback regardless of FAISS confidence;
* `accepted=False` only changes the category label, not the payout
  (except under TieredStrategy where the misc/uncategorised tier
  earns the base rate);
* lines without a price contribute nothing.
"""

from __future__ import annotations

import unittest

from src.cashback_engine import (
    CashbackEngine,
    FlatStrategy,
    TieredStrategy,
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


class TestFlatStrategy(unittest.TestCase):
    def test_pays_flat_rate_on_every_line(self):
        engine = CashbackEngine(FlatStrategy(0.02))
        matched = [
            _matched("Iced Tea",   10.0, "BEV003", "beverage"),
            _matched("Margherita", 20.0, "FOOD011", "food"),
        ]
        result = engine.compute(matched)
        self.assertAlmostEqual(result.total_spend, 30.0)
        self.assertAlmostEqual(result.total_cashback, 0.60, places=5)
        self.assertEqual(result.strategy, "flat_2pct")

    def test_uncategorised_lines_still_earn_cashback(self):
        """Core of the market-research model: data has value even when
        the line doesn't classify, so the user still gets paid."""
        engine = CashbackEngine(FlatStrategy(0.03))
        matched = [
            _matched("Iced Tea",   10.0, "BEV003", "beverage", accepted=True),
            _matched("PKT AYAM",    5.0, "FOOD021", "food", accepted=False),
        ]
        result = engine.compute(matched)
        # Both lines pay out at 3 %; one is "food", the other is "uncategorized"
        self.assertAlmostEqual(result.total_spend, 15.0)
        self.assertAlmostEqual(result.total_cashback, 0.45, places=5)
        categories = [ln.category for ln in result.lines]
        self.assertEqual(categories, ["beverage", "uncategorized"])

    def test_missing_price_is_zero(self):
        engine = CashbackEngine(FlatStrategy(0.02))
        matched = [MatchedLineItem(
            item=LineItem(name="No Price", quantity=1, unit_price=None, line_total=None),
            match=Match(sku="X", name="X", category="food", subcategory="x",
                        typical_price_usd=0, cashback_rate=0.05, score=0.9),
            accepted=True,
        )]
        result = engine.compute(matched)
        self.assertEqual(result.total_spend, 0.0)
        self.assertEqual(result.total_cashback, 0.0)

    def test_categorised_share(self):
        engine = CashbackEngine(FlatStrategy(0.02))
        matched = [
            _matched("Iced Tea",   10.0, "BEV003", "beverage", accepted=True),
            _matched("OP CODE",     5.0, "X",      "food",     accepted=False),
        ]
        result = engine.compute(matched)
        # 10 of 15 spend is categorised
        self.assertAlmostEqual(result.categorized_share, 10 / 15)


class TestTotalDriftGuard(unittest.TestCase):
    """Day-10.5 fix: the LLM sometimes double-counts items, inflating
    line_sum vs the declared grand total. Engine must trust the
    declared total when drift > tolerance."""

    def test_no_drift_no_correction(self):
        engine = CashbackEngine(FlatStrategy(0.02), drift_tolerance=0.10)
        matched = [_matched("A", 10.0, "X"), _matched("B", 20.0, "Y")]
        result = engine.compute(matched, declared_total=30.0)
        self.assertFalse(result.total_was_corrected)
        self.assertEqual(result.total_spend, 30.0)
        self.assertAlmostEqual(result.total_cashback, 0.60)

    def test_small_drift_under_tolerance_no_correction(self):
        engine = CashbackEngine(FlatStrategy(0.02), drift_tolerance=0.10)
        matched = [_matched("A", 10.0, "X"), _matched("B", 20.0, "Y")]
        # line_sum=30, declared=32 -> 6% drift, under 10% tolerance
        result = engine.compute(matched, declared_total=32.0)
        self.assertFalse(result.total_was_corrected)
        self.assertEqual(result.total_spend, 30.0)

    def test_moderate_drift_triggers_correction(self):
        """Between 10% (tolerance) and 50% (extreme) — scale to declared."""
        engine = CashbackEngine(FlatStrategy(0.02), drift_tolerance=0.10,
                                extreme_drift_threshold=0.50)
        matched = [_matched("A", 100.0, "X")]
        # line_sum=100, declared=80 -> +25% drift, between 10% and 50%
        result = engine.compute(matched, declared_total=80.0)
        self.assertTrue(result.total_was_corrected)
        self.assertFalse(result.requires_review)
        self.assertAlmostEqual(result.total_spend, 80.0)
        # Cashback scaled: 100 * 0.02 * (80/100) = 1.60
        self.assertAlmostEqual(result.total_cashback, 1.60)

    def test_no_declared_total_no_correction(self):
        engine = CashbackEngine(FlatStrategy(0.02))
        matched = [_matched("A", 10.0, "X")]
        result = engine.compute(matched, declared_total=None)
        self.assertFalse(result.total_was_corrected)
        self.assertIsNone(result.drift_pct)

    def test_extreme_drift_refuses_cashback(self):
        """Day-10.6 case: LLM dropped the leading million when reading
        '1,591,600' and returned 591_600. line_sum is also inflated
        by duplicates. Neither number is trustworthy → refuse payment."""
        engine = CashbackEngine(
            FlatStrategy(0.02),
            drift_tolerance=0.10,
            extreme_drift_threshold=0.50,
        )
        matched = [_matched("Bbk", 2_619_000.0, "FOOD026")]
        result = engine.compute(matched, declared_total=591_600.0)
        self.assertTrue(result.requires_review)
        self.assertFalse(result.total_was_corrected)
        self.assertEqual(result.total_cashback, 0.0)
        self.assertEqual(result.total_spend, 0.0)

    def test_negative_extreme_drift_also_refuses(self):
        """Sum much *smaller* than declared (LLM dropped lines) also
        triggers refusal — we shouldn't silently underpay either."""
        engine = CashbackEngine(FlatStrategy(0.02))
        matched = [_matched("A", 10.0, "X")]
        result = engine.compute(matched, declared_total=100.0)
        # drift = (10 - 100) / 100 = -90% → extreme
        self.assertTrue(result.requires_review)
        self.assertEqual(result.total_cashback, 0.0)


class TestTieredStrategy(unittest.TestCase):
    def test_food_and_beverage_get_their_tier_rate(self):
        engine = CashbackEngine(TieredStrategy())
        matched = [
            _matched("Iced Tea",   10.0, "BEV003", "beverage"),   # 2.0%
            _matched("Margherita", 20.0, "FOOD011", "food"),       # 2.5%
        ]
        result = engine.compute(matched)
        # 10 * 0.02 + 20 * 0.025 = 0.20 + 0.50 = 0.70
        self.assertAlmostEqual(result.total_cashback, 0.70, places=5)

    def test_misc_category_zeroes_out(self):
        engine = CashbackEngine(TieredStrategy())
        matched = [
            _matched("Plastic Bag",  1.0, "MISC001", "misc"),
            _matched("Iced Tea",    10.0, "BEV003",  "beverage"),
        ]
        result = engine.compute(matched)
        self.assertAlmostEqual(result.total_cashback, 0.20, places=5)

    def test_uncategorised_gets_base_rate(self):
        engine = CashbackEngine(TieredStrategy(base_rate=0.02))
        matched = [_matched("AYAM", 10.0, "X", "food", accepted=False)]
        result = engine.compute(matched)
        self.assertAlmostEqual(result.total_cashback, 0.20, places=5)


if __name__ == "__main__":
    unittest.main()
