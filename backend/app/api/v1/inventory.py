from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.inventory import InventoryResponse
from app.services import inventory_service

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("", response_model=InventoryResponse, summary="Inventory intelligence")
def get_inventory(
    branch_id: Optional[str] = Query(None),
    risk: Optional[str] = Query(
        None,
        pattern="^(HEALTHY|LOW|CRITICAL)$",
        description="Filter to a single risk status",
    ),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Substring match on name or SKU"),
    currency: str = Query("KES", pattern="^(KES|USD)$"),
    db: Session = Depends(get_db),
) -> InventoryResponse:
    return inventory_service.get_inventory(
        db,
        branch_id=branch_id,
        risk=risk,
        category=category,
        search=search,
        currency=currency,
    )