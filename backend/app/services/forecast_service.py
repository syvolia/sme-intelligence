from __future__ import annotations

import json
import threading
from datetime import timedelta

import mlflow
import mlflow.pyfunc
import pandas as pd
from fastapi import HTTPException
from mlflow.tracking import MlflowClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.forecast import (
    DemandForecastPoint,
    DemandForecastResponse,
    DemandHistoryPoint,
    ForecastMetrics,
)
from src.features.demand_features import (  # noqa: E402 (mounted at /ml)
    FEATURE_COLS,
    feature_row_from_history,
)


def _t(name: str) -> str:
    """Return a schema-qualified table name based on the warehouse flag."""
    return (
        f"{settings.warehouse_schema}.{name}"
        if settings.warehouse_enabled
        else f"public.{name}"
    )


_CACHE: dict = {}
_CACHE_LOCK = threading.Lock()


def _load_champion():
    with _CACHE_LOCK:
        if _CACHE.get("model") is not None:
            return _CACHE["model"], _CACHE["encodings"], _CACHE["metrics"]

        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        uri = (
            f"models:/{settings.mlflow_demand_model_name}"
            f"@{settings.mlflow_champion_alias}"
        )

        try:
            model = mlflow.pyfunc.load_model(uri)
        except Exception as e:  # noqa: BLE001
            raise HTTPException(
                status_code=503,
                detail=(
                    "Demand model not available. Train it first:\n"
                    "  docker compose run --rm ml python -m src.training.train_demand\n"
                    f"Underlying error: {e}"
                ),
            )

        client = MlflowClient()
        mv = client.get_model_version_by_alias(
            settings.mlflow_demand_model_name, settings.mlflow_champion_alias
        )

        enc_path = client.download_artifacts(
            mv.run_id, "model/artifacts/encodings.json"
        )
        with open(enc_path) as f:
            encodings = json.load(f)

        run = client.get_run(mv.run_id)
        metrics = {
            "mae": float(run.data.metrics.get("mae", 0.0)),
            "rmse": float(run.data.metrics.get("rmse", 0.0)),
            "mape": float(run.data.metrics.get("mape", 0.0)),
        }

        _CACHE["model"] = model
        _CACHE["encodings"] = encodings
        _CACHE["metrics"] = metrics

        return model, encodings, metrics


def _load_history(
    db: Session, product_id: str, branch_id: str, history_days: int
) -> pd.DataFrame:
    """
    Return a full daily series (zero-filled) for (product, branch) over the
    last `history_days` days, anchored on the latest sale date.
    """
    if settings.warehouse_enabled:
        sql = f"""
        SELECT f.sale_date::date AS date, SUM(f.quantity)::float AS units
        FROM {_t('fact_sales')} f
        JOIN {_t('dim_product')}  p ON p.product_key  = f.product_key
        JOIN {_t('dim_location')} l ON l.location_key = f.location_key
        WHERE f.status <> 'cancelled'
          AND l.branch_id = :branch_id
          AND p.product_id = :product_id
        GROUP BY 1
        ORDER BY 1
        """
    else:
        sql = """
        SELECT DATE(s.sale_date) AS date, SUM(si.quantity)::float AS units
        FROM sale_items si
        JOIN sales s ON s.id = si.sale_id
        WHERE s.status <> 'cancelled'
          AND s.branch_id = :branch_id
          AND si.product_id = :product_id
        GROUP BY 1
        ORDER BY 1
        """

    raw = pd.read_sql(
        text(sql), db.bind, params={"branch_id": branch_id, "product_id": product_id}
    )
    raw["date"] = pd.to_datetime(raw["date"])

    if settings.warehouse_enabled:
        last = db.execute(
            text(f"SELECT MAX(sale_date)::date FROM {_t('fact_sales')}")
        ).scalar()
    else:
        last = db.execute(
            text("SELECT MAX(sale_date)::date FROM sales")
        ).scalar()

    start = last - timedelta(days=history_days)
    idx = pd.date_range(start, last, freq="D")

    series = raw.set_index("date").reindex(idx, fill_value=0.0)
    series.index.name = "date"
    return series.reset_index().rename(columns={"index": "date"})


def _product_meta(db: Session, product_id: str, branch_id: str):
    if settings.warehouse_enabled:
        sql = f"""
        SELECT p.name AS product,
               COALESCE(p.category, '') AS category,
               l.branch_name AS location
        FROM {_t('dim_product')}  p
        CROSS JOIN {_t('dim_location')} l
        WHERE p.product_id = :pid AND l.branch_id = :bid
        """
    else:
        sql = """
        SELECT p.name AS product,
               COALESCE(p.category, '') AS category,
               b.name AS location
        FROM products p
        CROSS JOIN branches b
        WHERE p.id = :pid AND b.id = :bid
        """

    row = db.execute(
        text(sql), {"pid": product_id, "bid": branch_id}
    ).mappings().first()

    if row is None:
        raise HTTPException(status_code=404, detail="Product or branch not found.")
    return row


def get_demand_forecast(
    db: Session,
    product_id: str,
    location_id: str,
    horizon_days: int = 30,
    history_days: int = 60,
) -> DemandForecastResponse:
    model, encodings, metrics = _load_champion()

    meta = _product_meta(db, product_id, location_id)
    history_df = _load_history(db, product_id, location_id, history_days)

    units = history_df["units"].tolist()
    last_date = history_df["date"].iloc[-1]

    history_points = [
        DemandHistoryPoint(
            date=row.date.date().isoformat(), value=round(float(row.units), 2)
        )
        for row in history_df.itertuples()
    ]

    forecast_points: list[DemandForecastPoint] = []
    rolling = list(units)

    for step in range(1, horizon_days + 1):
        target = last_date + timedelta(days=step)

        feature_row = feature_row_from_history(
            history_units=rolling,
            target=target,
            product_id=product_id,
            branch_id=location_id,
            category=meta["category"],
            encodings=encodings,
        )

        X = pd.DataFrame([feature_row])[FEATURE_COLS]
        preds = model.predict(X).iloc[0]

        value = max(0.0, float(preds["q50"]))
        lower = max(0.0, float(preds["q10"]))
        upper = max(value, float(preds["q90"]))

        forecast_points.append(
            DemandForecastPoint(
                date=target.date().isoformat(),
                value=round(value, 2),
                lower=round(lower, 2),
                upper=round(upper, 2),
            )
        )

        rolling.append(value)

    return DemandForecastResponse(
        product_id=product_id,
        product=meta["product"],
        location_id=location_id,
        location=meta["location"],
        horizon_days=horizon_days,
        history=history_points,
        forecast=forecast_points,
        metrics=ForecastMetrics(
            model=settings.mlflow_demand_model_name,
            mae=round(metrics["mae"], 3),
            rmse=round(metrics["rmse"], 3),
            mape=round(metrics["mape"], 4),
        ),
    )