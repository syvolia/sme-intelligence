from typing import Optional

from pydantic import BaseModel


class CashflowPoint(BaseModel):
    date: str
    balance: float
    lower: float
    upper: float
    inflow: float
    outflow: float


class CashflowSummary(BaseModel):
    current_cash: float
    expected_income: float
    expected_expenses: float
    predicted_min_balance: float
    min_safe_balance: float
    currency: str = "KES"


class ShortageAlert(BaseModel):
    predicted_date: str
    expected_minimum: float
    minimum_safe_balance: float
    recommendation: str


class CashflowForecastResponse(BaseModel):
    summary: CashflowSummary
    forecast: list[CashflowPoint]
    alert: Optional[ShortageAlert] = None