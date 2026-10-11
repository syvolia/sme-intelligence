from datetime import date

from pydantic import BaseModel


class DashboardKpis(BaseModel):
    revenue: float
    gross_profit: float
    inventory_value: float
    outstanding_payments: float
    cash_balance: float
    currency: str = "KES"


class RevenuePoint(BaseModel):
    date: date
    value: float


class CashflowPoint(BaseModel):
    date: date
    balance: float
    lower: float
    upper: float


class InventoryRiskItem(BaseModel):
    product_id: str
    product: str
    branch_id: str
    branch: str
    current_stock: int
    daily_demand: float
    days_remaining: float
    reorder_point: int
    risk: str                    # LOW | MEDIUM | HIGH


class RecommendationSummary(BaseModel):
    id: str
    type: str                    # inventory | cashflow | pricing | customer | supplier
    title: str
    priority: str                # low | medium | high


class DashboardResponse(BaseModel):
    kpis: DashboardKpis
    revenue_trend: list[RevenuePoint]
    cashflow_forecast: list[CashflowPoint]
    inventory_risk: list[InventoryRiskItem]
    recommendations: list[RecommendationSummary]