from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.customers import CustomersResponse
from app.services import customer_service

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=CustomersResponse, summary="Customer RFM segmentation")
def get_customers(
    currency: str = Query("KES", pattern="^(KES|USD)$"),
    db: Session = Depends(get_db),
) -> CustomersResponse:
    return customer_service.get_customers(db, currency=currency)