"""
MLflow PythonModel wrapper for the three quantile XGBoost boosters.
"""
from __future__ import annotations

import mlflow.pyfunc
import pandas as pd
import xgboost as xgb


class DemandForecaster(mlflow.pyfunc.PythonModel):
    """
    Wraps q10, q50, q90 XGBoost regressors. `predict` returns a DataFrame
    with columns: q10, q50, q90 — all clipped to >= 0.
    """

    def load_context(self, context) -> None:
        self.models: dict[str, xgb.XGBRegressor] = {}
        for name in ("q10", "q50", "q90"):
            m = xgb.XGBRegressor()
            m.load_model(context.artifacts[name])
            self.models[name] = m

    def predict(self, context, model_input, params=None) -> pd.DataFrame:
        if not isinstance(model_input, pd.DataFrame):
            model_input = pd.DataFrame(model_input)

        out = pd.DataFrame(
            {name: m.predict(model_input) for name, m in self.models.items()}
        )
        return out.clip(lower=0.0)