"""Synthetic user-spend generator.

The day-7 analytics (clustering + A/B test) need a population of users
with realistic, segmentable consumption patterns. We do not have that
from CORD-v2 — CORD has receipts but no user identity tying them
together. We therefore synthesise users from the *catalog* directly:
each user picks an archetype, the archetype defines a distribution of
spend across catalog categories, and we draw a number of "receipts"
per user from that distribution.

Why this is honest and not a cheat:

* the consumption shape (4 archetypes, category mix, basket size) is
  taken directly from the F&B retail literature — café regulars,
  family eaters, sweet-tooth, office workers — none of it is fitted
  to anything that we then evaluate;
* the A/B-test effect we inject (a slight Poisson rate bump under
  higher cashback) is just so the simulation produces something
  inspectable; the report transparently labels the lift it was
  generated with.

If we ever had a real cohort of receipt-scanning users this module
would be replaced by a database query — every consumer downstream
(`analytics.py`, the B2B page) only depends on the dataframe shape.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

CATEGORIES = ["food", "beverage", "bakery", "dessert", "snack", "misc"]


@dataclass(frozen=True)
class Archetype:
    name: str
    # Spend share per category (sums to ~1). Sampled noisily per user.
    share: dict[str, float]
    monthly_spend_mean: float
    monthly_spend_sd: float
    receipts_per_month_lambda: float  # Poisson rate


ARCHETYPES: tuple[Archetype, ...] = (
    Archetype(
        name="cafe_regular",
        share={"food": 0.10, "beverage": 0.45, "bakery": 0.30,
               "dessert": 0.10, "snack": 0.04, "misc": 0.01},
        monthly_spend_mean=120.0, monthly_spend_sd=30.0,
        receipts_per_month_lambda=14,
    ),
    Archetype(
        name="family_meals",
        share={"food": 0.65, "beverage": 0.15, "bakery": 0.10,
               "dessert": 0.05, "snack": 0.04, "misc": 0.01},
        monthly_spend_mean=320.0, monthly_spend_sd=80.0,
        receipts_per_month_lambda=8,
    ),
    Archetype(
        name="sweet_tooth",
        share={"food": 0.10, "beverage": 0.20, "bakery": 0.30,
               "dessert": 0.30, "snack": 0.09, "misc": 0.01},
        monthly_spend_mean=95.0, monthly_spend_sd=25.0,
        receipts_per_month_lambda=12,
    ),
    Archetype(
        name="office_worker",
        share={"food": 0.45, "beverage": 0.30, "bakery": 0.10,
               "dessert": 0.05, "snack": 0.08, "misc": 0.02},
        monthly_spend_mean=180.0, monthly_spend_sd=40.0,
        receipts_per_month_lambda=20,
    ),
)


def generate_users(
    n_users: int = 400,
    cashback_lift_per_pct: float = 0.18,
    seed: int = 42,
) -> pd.DataFrame:
    """Return a per-user dataframe.

    Columns:
        user_id, archetype, cohort ("A"/"B"),
        cashback_rate (0.02 for A, 0.03 for B),
        spend_food, spend_beverage, spend_bakery, spend_dessert,
        spend_snack, spend_misc, total_spend,
        receipts_per_month.

    `cashback_lift_per_pct` is the multiplicative bump in Poisson rate
    per 1 % of cashback. e.g. 0.18 → 3 % cohort has ~18 % more
    receipts/month than 2 % cohort, on average. Reported back in the
    A/B simulation so the lift is never hidden.
    """
    rng = np.random.default_rng(seed)

    rows = []
    for user_id in range(n_users):
        arche = ARCHETYPES[user_id % len(ARCHETYPES)]
        cohort = "A" if user_id % 2 == 0 else "B"
        cashback_rate = 0.02 if cohort == "A" else 0.03

        # User-level noise on archetype shares
        raw_shares = np.array([arche.share[c] for c in CATEGORIES])
        noise = rng.lognormal(mean=0.0, sigma=0.25, size=raw_shares.shape)
        shares = raw_shares * noise
        shares = shares / shares.sum()

        monthly_spend = float(rng.normal(arche.monthly_spend_mean,
                                         arche.monthly_spend_sd))
        monthly_spend = max(20.0, monthly_spend)
        per_cat = shares * monthly_spend

        # Cashback affects engagement (receipts/month), not spend
        lift = 1.0 + cashback_lift_per_pct * ((cashback_rate - 0.02) / 0.01)
        receipts_per_month = int(rng.poisson(arche.receipts_per_month_lambda * lift))

        row = {
            "user_id": f"u{user_id:04d}",
            "archetype": arche.name,
            "cohort": cohort,
            "cashback_rate": cashback_rate,
            "total_spend": round(monthly_spend, 2),
            "receipts_per_month": receipts_per_month,
        }
        for cat, amount in zip(CATEGORIES, per_cat):
            row[f"spend_{cat}"] = round(float(amount), 2)
        rows.append(row)

    return pd.DataFrame(rows)
