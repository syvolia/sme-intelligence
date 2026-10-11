from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.suppliers import SuppliersResponse
from app.services import supplier_service

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("", response_model=SuppliersResponse, summary="Supplier scorecard")
def get_suppliers(
    currency: str = Query("KES", pattern="^(KES|USD)$"),
    db: Session = Depends(get_db),
) -> SuppliersResponse:
    return supplier_service.get_suppliers(db, currency=currency)