"""
Shared feature engineering for demand forecasting.

Used both by the training script and by the backend at inference time so
that training and serving see the exact same feature semantics.
"""
from __future__ import annotations

import pandas as pd


FEATURE_COLS = [
    "lag_1", "lag_7", "lag_14", "lag_28",
    "roll_mean_7", "roll_mean_14", "roll_mean_28", "roll_std_7",
    "dow", "dom", "month", "is_weekend",
    "product_code", "branch_code", "category_code",
]
TARGET_COL = "units"


def build_lag_features(panel: pd.DataFrame) -> pd.DataFrame:
    """
    panel must be sorted by [branch_id, product_id, date] and contain columns:
      date, branch_id, product_id, units
    Returns the same frame with lag/rolling/calendar columns added.
    """
    df = panel.copy()
    g = df.groupby(["branch_id", "product_id"], group_keys=False, sort=False)

    for lag in (1, 7, 14, 28):
        df[f"lag_{lag}"] = g["units"].shift(lag)

    for window in (7, 14, 28):
        df[f"roll_mean_{window}"] = g["units"].transform(
            lambda s: s.shift(1).rolling(window, min_periods=1).mean()
        )

    df["roll_std_7"] = g["units"].transform(
        lambda s: s.shift(1).rolling(7, min_periods=2).std()
    ).fillna(0.0)

    df["dow"] = df["date"].dt.dayofweek
    df["dom"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["is_weekend"] = (df["dow"] >= 5).astype(int)

    return df


def encode_frame(
    df: pd.DataFrame,
    product_map: dict[str, int],
    branch_map: dict[str, int],
    category_map: dict[str, int],
) -> pd.DataFrame:
    df = df.copy()
    df["product_code"] = df["product_id"].map(product_map).fillna(-1).astype(int)
    df["branch_code"] = df["branch_id"].map(branch_map).fillna(-1).astype(int)
    df["category_code"] = (
        df["category"].fillna("").map(category_map).fillna(-1).astype(int)
    )
    return df


def feature_row_from_history(
    history_units: list[float],
    target,
    product_id: str,
    branch_id: str,
    category: str | None,
    encodings: dict,
) -> dict:
    """
    Build a single encoded feature row for `target` (a pandas Timestamp)
    given the chronological list of units observed/predicted so far.
    """
    n = len(history_units)

    def lag(k: int) -> float:
        if n >= k:
            return float(history_units[-k])
        return float(sum(history_units) / n) if n else 0.0

    def roll_mean(k: int) -> float:
        window = history_units[-k:] if n else []
        return float(sum(window) / len(window)) if window else 0.0

    def roll_std(k: int) -> float:
        window = history_units[-k:] if n else []
        if len(window) < 2:
            return 0.0
        m = sum(window) / len(window)
        return float((sum((x - m) ** 2 for x in window) / (len(window) - 1)) ** 0.5)

    return {
        "lag_1": lag(1),
        "lag_7": lag(7),
        "lag_14": lag(14),
        "lag_28": lag(28),
        "roll_mean_7": roll_mean(7),
        "roll_mean_14": roll_mean(14),
        "roll_mean_28": roll_mean(28),
        "roll_std_7": roll_std(7),
        "dow": int(target.weekday()),
        "dom": int(target.day),
        "month": int(target.month),
        "is_weekend": int(target.weekday() >= 5),
        "product_code": int(encodings["product_map"].get(product_id, -1)),
        "branch_code": int(encodings["branch_map"].get(branch_id, -1)),
        "category_code": int(encodings["category_map"].get(category or "", -1)),
    }