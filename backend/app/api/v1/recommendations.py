from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.recommendations import RecommendationsResponse
from app.services import recommendation_service

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get(
    "",
    response_model=RecommendationsResponse,
    summary="Ranked AI recommendations across all domains",
)
def get_recommendations(
    currency: str = Query("KES", pattern="^(KES|USD)$"),
    db: Session = Depends(get_db),
) -> RecommendationsResponse:
    return recommendation_service.get_recommendations(db, currency=currency)