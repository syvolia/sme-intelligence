from typing import Literal

from pydantic import BaseModel

RecommendationType = Literal["inventory", "cashflow", "pricing", "customer", "supplier"]
Priority = Literal["high", "medium", "low"]


class Recommendation(BaseModel):
    id: str
    type: RecommendationType
    priority: Priority
    priority_score: float          # internal ordering signal
    title: str
    problem: str
    evidence: str
    recommendation: str
    expected_impact: str


class RecommendationTotals(BaseModel):
    total: int
    high: int
    medium: int
    low: int
    by_type: dict[str, int]


class RecommendationsResponse(BaseModel):
    generated_at: str
    currency: str
    totals: RecommendationTotals
    cards: list[Recommendation]