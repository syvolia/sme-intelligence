from pydantic import BaseModel


class DemandHistoryPoint(BaseModel):
    date: str
    value: float


class DemandForecastPoint(BaseModel):
    date: str
    value: float
    lower: float
    upper: float


class ForecastMetrics(BaseModel):
    model: str
    mae: float
    rmse: float
    mape: float


class DemandForecastResponse(BaseModel):
    product_id: str
    product: str
    location_id: str
    location: str
    horizon_days: int
    history: list[DemandHistoryPoint]
    forecast: list[DemandForecastPoint]
    metrics: ForecastMetrics