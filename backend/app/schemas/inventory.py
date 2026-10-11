from typing import Literal, Optional

from pydantic import BaseModel

RiskStatus = Literal["HEALTHY", "LOW", "CRITICAL"]


class InventoryItem(BaseModel):
    product_id: str
    sku: str
    product: str
    category: Optional[str] = None
    unit: Optional[str] = None

    branch_id: str
    branch: str

    supplier_id: Optional[str] = None
    supplier: Optional[str] = None

    current_stock: int
    daily_demand: float
    units_last_30d: int
    days_remaining: Optional[float]
    lead_time_days: int
    lead_time_demand: float
    reorder_point: int
    risk: RiskStatus


class InventorySummary(BaseModel):
    total_skus: int
    healthy: int
    low: int
    critical: int
    total_inventory_value: float
    currency: str = "KES"


class InventoryResponse(BaseModel):
    summary: InventorySummary
    items: list[InventoryItem]