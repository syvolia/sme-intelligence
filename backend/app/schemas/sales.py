from datetime import date
from typing import Optional

from pydantic import BaseModel


class SalesKpis(BaseModel):
    revenue: float
    orders: int
    avg_order_value: float
    gross_margin: float          # 0..1
    currency: str = "KES"


class TimePoint(BaseModel):
    date: date
    value: float


class ProductRevenue(BaseModel):
    product_id: str
    product: str
    category: Optional[str] = None
    revenue: float
    units: int


class CategoryRevenue(BaseModel):
    category: str
    revenue: float


class LocationRevenue(BaseModel):
    location_id: str
    location: str
    revenue: float


class SalesResponse(BaseModel):
    kpis: SalesKpis
    revenue_over_time: list[TimePoint]
    revenue_by_product: list[ProductRevenue]
    revenue_by_category: list[CategoryRevenue]
    revenue_by_location: list[LocationRevenue]
    top_products: list[ProductRevenue]
    bottom_products: list[ProductRevenue]