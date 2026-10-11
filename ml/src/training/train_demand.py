"""
Train the demand forecasting model and register it in MLflow.

Local (logs to DagsHub-hosted MLflow):
    docker compose run --rm ml python -m src.training.train_demand

The DagsHub repo is configured via env vars — see DAGSHUB_OWNER / DAGSHUB_REPO
below. Defaults match the portfolio deployment.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import dagshub
import mlflow
import numpy as np
import pandas as pd
import xgboost as xgb
from mlflow.tracking import MlflowClient
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sqlalchemy import create_engine

from src.features.demand_features import (
    FEATURE_COLS,
    TARGET_COL,
    build_lag_features,
    encode_frame,
)
from src.models.demand_forecaster import DemandForecaster


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MODEL_NAME = os.environ.get("MLFLOW_DEMAND_MODEL_NAME", "demand_forecast_xgboost")
EXPERIMENT = "demand_forecasting"
CHAMPION_ALIAS = "champion"

# DagsHub repo that hosts the MLflow tracking server
DAGSHUB_OWNER = os.environ.get("DAGSHUB_OWNER", "syvoliamary")
DAGSHUB_REPO = os.environ.get("DAGSHUB_REPO", "sme-intelligence")

VAL_DAYS = 30


# ---------------------------------------------------------------------------
# MLflow / DagsHub setup
# ---------------------------------------------------------------------------
def _configure_mlflow() -> str:
    """
    Point MLflow at the right tracking URI.

    Priority:
      1. MLFLOW_TRACKING_URI env var (used on Render / CI)
      2. DagsHub-hosted MLflow for the configured repo (default)
    """
    explicit_uri = os.environ.get("MLFLOW_TRACKING_URI")
    if explicit_uri:
        mlflow.set_tracking_uri(explicit_uri)
        return explicit_uri

    dagshub.init(
        repo_owner=DAGSHUB_OWNER,
        repo_name=DAGSHUB_REPO,
        mlflow=True,
    )
    return mlflow.get_tracking_uri()


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_daily_demand(engine) -> pd.DataFrame:
    sql = """
    SELECT
        DATE(s.sale_date)         AS date,
        s.branch_id::text         AS branch_id,
        si.product_id::text       AS product_id,
        SUM(si.quantity)::float   AS units
    FROM sale_items si
    JOIN sales s ON s.id = si.sale_id
    WHERE s.status <> 'cancelled'
    GROUP BY 1, 2, 3
    ORDER BY 1
    """
    df = pd.read_sql(sql, engine)
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_product_meta(engine) -> pd.DataFrame:
    sql = """
    SELECT id::text AS product_id,
           COALESCE(category, '') AS category,
           cost_price::float AS cost_price,
           sell_price::float AS sell_price,
           lead_time_days
    FROM products
    """
    return pd.read_sql(sql, engine)


def build_full_panel(demand: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    """Reindex to a full daily panel per (branch, product); missing = 0 units."""
    start, end = demand["date"].min(), demand["date"].max()
    all_dates = pd.date_range(start, end, freq="D")

    combos = demand[["branch_id", "product_id"]].drop_duplicates()
    grid = combos.merge(pd.DataFrame({"date": all_dates}), how="cross")

    panel = grid.merge(
        demand, on=["branch_id", "product_id", "date"], how="left"
    )
    panel["units"] = panel["units"].fillna(0.0)
    panel = panel.merge(meta, on="product_id", how="left")

    return panel.sort_values(
        ["branch_id", "product_id", "date"]
    ).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    tracking_uri = _configure_mlflow()
    print(f"→ MLflow tracking URI: {tracking_uri}")

    mlflow.set_experiment(EXPERIMENT)

    db_url = os.environ["DATABASE_URL"]
    engine = create_engine(db_url)

    print("→ loading daily demand from OLTP")
    demand = load_daily_demand(engine)
    print(f"  raw demand rows: {len(demand):,}")

    print("→ loading product metadata")
    meta = load_product_meta(engine)

    print("→ building full daily panel")
    panel = build_full_panel(demand, meta)
    print(f"  panel rows: {len(panel):,}")

    print("→ building lag / rolling / calendar features")
    features = build_lag_features(panel)
    features = features.dropna(subset=["lag_28"]).reset_index(drop=True)
    print(f"  feature rows: {len(features):,}")

    # Stable encodings ------------------------------------------------------
    product_map = {
        pid: i for i, pid in enumerate(sorted(features["product_id"].unique()))
    }
    branch_map = {
        bid: i for i, bid in enumerate(sorted(features["branch_id"].unique()))
    }
    category_map = {
        c: i
        for i, c in enumerate(sorted(features["category"].fillna("").unique()))
    }
    encoded = encode_frame(features, product_map, branch_map, category_map)

    # Train / val split -----------------------------------------------------
    cutoff = encoded["date"].max() - pd.Timedelta(days=VAL_DAYS)
    train = encoded[encoded["date"] < cutoff]
    val = encoded[encoded["date"] >= cutoff]
    print(f"→ train rows: {len(train):,}   val rows: {len(val):,}")

    X_train, y_train = train[FEATURE_COLS], train[TARGET_COL]
    X_val, y_val = val[FEATURE_COLS], val[TARGET_COL]

    params = dict(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        tree_method="hist",
        random_state=42,
        n_jobs=-1,
    )

    with mlflow.start_run() as run:
        mlflow.log_params({"model_family": "xgboost_quantile", **params})
        mlflow.log_param("val_days", VAL_DAYS)
        mlflow.log_param("train_rows", len(train))
        mlflow.log_param("val_rows", len(val))

        # ---- Train three quantile boosters ---------------------------------
        models: dict[str, xgb.XGBRegressor] = {}
        for name, alpha in (("q10", 0.1), ("q50", 0.5), ("q90", 0.9)):
            print(f"→ training {name} (alpha={alpha})")
            m = xgb.XGBRegressor(
                objective="reg:quantileerror",
                quantile_alpha=alpha,
                **params,
            )
            m.fit(X_train, y_train)
            models[name] = m

        # ---- Metrics on the median model -----------------------------------
        y_pred = models["q50"].predict(X_val)
        mae = float(mean_absolute_error(y_val, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_val, y_pred)))
        mask = y_val > 0
        mape = (
            float(np.mean(np.abs((y_val[mask] - y_pred[mask]) / y_val[mask])))
            if mask.any()
            else 0.0
        )
        print(f"→ val   MAE={mae:.4f}   RMSE={rmse:.4f}   MAPE={mape:.4f}")
        mlflow.log_metrics({"mae": mae, "rmse": rmse, "mape": mape})

        # ---- Persist + log model -------------------------------------------
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            artifacts: dict[str, str] = {}
            for name, m in models.items():
                p = tmp_path / f"{name}.json"
                m.save_model(str(p))
                artifacts[name] = str(p)

            enc_path = tmp_path / "encodings.json"
            enc_path.write_text(
                json.dumps(
                    {
                        "product_map": product_map,
                        "branch_map": branch_map,
                        "category_map": category_map,
                        "feature_cols": FEATURE_COLS,
                    }
                )
            )
            artifacts["encodings"] = str(enc_path)

            print("→ logging model to MLflow")
            mlflow.pyfunc.log_model(
                artifact_path="model",
                python_model=DemandForecaster(),
                artifacts=artifacts,
                registered_model_name=MODEL_NAME,
                pip_requirements=[
                    "mlflow==2.16.2",
                    "xgboost==2.1.1",
                    "scikit-learn==1.5.2",
                    "pandas==2.2.3",
                    "numpy==1.26.4",
                ],
            )

        # ---- Promote latest version to champion ----------------------------
        client = MlflowClient()
        versions = client.search_model_versions(f"name='{MODEL_NAME}'")
        latest = max(versions, key=lambda v: int(v.version))
        client.set_registered_model_alias(MODEL_NAME, CHAMPION_ALIAS, latest.version)
        print(f"→ promoted version {latest.version} → alias '{CHAMPION_ALIAS}'")
        print(f"→ run id: {run.info.run_id}")
        print(f"→ view at: {tracking_uri}/#/experiments/{run.info.experiment_id}/runs/{run.info.run_id}")


if __name__ == "__main__":
    main()