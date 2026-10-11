from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.forecast import DemandForecastResponse
from app.services import forecast_service

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get(
    "/demand",
    response_model=DemandForecastResponse,
    summary="Daily demand forecast per product × branch",
)
def get_demand_forecast(
    product_id: str = Query(..., description="Product UUID"),
    location_id: str = Query(..., description="Branch UUID"),
    horizon_days: int = Query(30, ge=1, le=90),
    history_days: int = Query(60, ge=14, le=180),
    db: Session = Depends(get_db),
) -> DemandForecastResponse:
    return forecast_service.get_demand_forecast(
        db,
        product_id=product_id,
        location_id=location_id,
        horizon_days=horizon_days,
        history_days=history_days,
    )