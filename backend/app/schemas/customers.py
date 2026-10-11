from typing import Optional

from pydantic import BaseModel


class CustomerTotals(BaseModel):
    total_customers: int
    active_customers: int          # purchased in last 30 days
    repeat_customers: int          # 2+ orders
    avg_customer_value: float
    currency: str = "KES"


class SegmentSummary(BaseModel):
    segment: str
    count: int
    revenue: float
    revenue_share: float           # 0..1
    avg_monetary: float
    avg_frequency: float
    avg_recency_days: float


class CustomerScatterPoint(BaseModel):
    customer_id: str
    name: Optional[str] = None
    segment: str
    recency_days: int
    frequency: int
    monetary: float


class CustomerListRow(BaseModel):
    customer_id: str
    name: Optional[str] = None
    segment: str
    recency_days: int
    frequency: int
    monetary: float
    r_score: int
    f_score: int
    m_score: int


class CustomersResponse(BaseModel):
    totals: CustomerTotals
    segments: list[SegmentSummary]
    scatter: list[CustomerScatterPoint]
    top_customers: list[CustomerListRow]