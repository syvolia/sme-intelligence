from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.cashflow import CashflowForecastResponse
from app.services import cashflow_service

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get(
    "/cashflow",
    response_model=CashflowForecastResponse,
    summary="30-day cash-flow projection with shortage detection",
)
def get_cashflow_forecast(
    horizon_days: int = Query(30, ge=7, le=90),
    currency: str = Query("KES", pattern="^(KES|USD)$"),
    db: Session = Depends(get_db),
) -> CashflowForecastResponse:
    return cashflow_service.get_cashflow_forecast(
        db,
        horizon_days=horizon_days,
        currency=currency,
    )