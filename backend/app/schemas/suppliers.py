from typing import Optional

from pydantic import BaseModel


class SupplierRow(BaseModel):
    supplier_id: str
    supplier: str
    country: Optional[str] = None

    orders: int
    received_orders: int
    avg_delivery_days: float
    avg_lateness_days: float
    on_time_pct: float               # 0..1
    recent_on_time_pct: float        # 0..1, last 90 days
    avg_cost: float
    total_spend: float
    reliability: float               # 0..100
    trend: str                       # improving | stable | degrading
    tier: str                        # Excellent | Good | Fair | Poor


class SupplierSummary(BaseModel):
    total_suppliers: int
    avg_reliability: float
    avg_on_time_pct: float
    best_supplier: Optional[str] = None
    worst_supplier: Optional[str] = None
    at_risk_count: int               # reliability < 75
    currency: str = "KES"


class SuppliersResponse(BaseModel):
    summary: SupplierSummary
    suppliers: list[SupplierRow]