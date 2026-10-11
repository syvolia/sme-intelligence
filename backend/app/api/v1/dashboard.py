from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dashboard import DashboardResponse
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse, summary="Main dashboard")
def get_dashboard(
    date_from: Optional[date] = Query(None, description="Inclusive (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Inclusive (YYYY-MM-DD)"),
    branch_id: Optional[str] = Query(None, description="Filter to a single branch"),
    currency: str = Query("KES", pattern="^(KES|USD)$"),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    return dashboard_service.get_dashboard(
        db,
        date_from=date_from,
        date_to=date_to,
        branch_id=branch_id,
        currency=currency,
    )