"""Day-7 analytics: K-Means clustering + A/B-test of cashback rates.

Two pure-Python functions used by both the day-7 notebook and the
Streamlit B2B page. They take a user dataframe (see
`synthetic_users.generate_users`) and return typed result objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

CATEGORY_COLS: Sequence[str] = (
    "spend_food", "spend_beverage", "spend_bakery",
    "spend_dessert", "spend_snack", "spend_misc",
)


# --- clustering -------------------------------------------------------------


@dataclass
class ClusteringResult:
    labels: np.ndarray              # cluster label per user
    centers_original: pd.DataFrame  # cluster center in original feature space
    coords_2d: np.ndarray           # PCA projection for plotting
    inertia: float
    n_clusters: int


def cluster_users(users: pd.DataFrame, n_clusters: int = 4,
                  seed: int = 42) -> ClusteringResult:
    """K-Means over per-category spend shares.

    We cluster on **shares** (each user normalised to sum-to-1), not
    absolute spend, so a cafe-regular spending $80 and one spending
    $200 land in the same cluster.
    """
    X = users[list(CATEGORY_COLS)].values.astype(float)
    totals = X.sum(axis=1, keepdims=True)
    totals[totals == 0] = 1.0
    X_shares = X / totals

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X_shares)

    km = KMeans(n_clusters=n_clusters, n_init=10, random_state=seed)
    labels = km.fit_predict(Xs)

    centers_shares = scaler.inverse_transform(km.cluster_centers_)
    centers_df = pd.DataFrame(centers_shares, columns=list(CATEGORY_COLS))
    centers_df.insert(0, "cluster", range(n_clusters))

    pca = PCA(n_components=2, random_state=seed)
    coords = pca.fit_transform(Xs)

    return ClusteringResult(
        labels=labels,
        centers_original=centers_df,
        coords_2d=coords,
        inertia=float(km.inertia_),
        n_clusters=n_clusters,
    )


# --- A/B test ---------------------------------------------------------------


@dataclass
class ABTestResult:
    metric: str
    mean_a: float
    mean_b: float
    lift_abs: float
    lift_pct: float
    n_a: int
    n_b: int
    t_stat: float
    p_value: float
    significant_at_05: bool

    def as_dict(self) -> dict:
        return {
            "metric": self.metric,
            "mean_a (2% cashback)": round(self.mean_a, 3),
            "mean_b (3% cashback)": round(self.mean_b, 3),
            "lift_abs": round(self.lift_abs, 3),
            "lift_pct": f"{self.lift_pct:.1%}",
            "n_a": self.n_a, "n_b": self.n_b,
            "t_stat": round(self.t_stat, 3),
            "p_value": round(self.p_value, 4),
            "significant_at_alpha_0.05": self.significant_at_05,
        }


def ab_test(
    users: pd.DataFrame,
    metric: str = "receipts_per_month",
) -> ABTestResult:
    """Welch's t-test between cohort A (2%) and cohort B (3%).

    We use Welch's because the two cohorts can have different variances
    (the higher-engagement group naturally has a fatter tail).
    """
    a = users.loc[users["cohort"] == "A", metric].astype(float)
    b = users.loc[users["cohort"] == "B", metric].astype(float)
    mean_a, mean_b = float(a.mean()), float(b.mean())
    lift_abs = mean_b - mean_a
    lift_pct = (lift_abs / mean_a) if mean_a else 0.0

    t_stat, p_value = stats.ttest_ind(b, a, equal_var=False)
    return ABTestResult(
        metric=metric,
        mean_a=mean_a, mean_b=mean_b,
        lift_abs=lift_abs, lift_pct=lift_pct,
        n_a=len(a), n_b=len(b),
        t_stat=float(t_stat), p_value=float(p_value),
        significant_at_05=bool(p_value < 0.05),
    )
