from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.sales import SalesResponse
from app.services import sales_service

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("", response_model=SalesResponse, summary="Sales analytics")
def get_sales(
    date_from: Optional[date] = Query(None, description="Inclusive (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Inclusive (YYYY-MM-DD)"),
    branch_id: Optional[str] = Query(None, description="Filter to a single branch"),
    product_id: Optional[str] = Query(None, description="Filter to a single product"),
    customer_id: Optional[str] = Query(None, description="Filter to a single customer"),
    currency: str = Query("KES", pattern="^(KES|USD)$"),
    db: Session = Depends(get_db),
) -> SalesResponse:
    return sales_service.get_sales_analytics(
        db,
        date_from=date_from,
        date_to=date_to,
        branch_id=branch_id,
        product_id=product_id,
        customer_id=customer_id,
        currency=currency,
    )