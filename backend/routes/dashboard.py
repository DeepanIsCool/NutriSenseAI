"""
/api/dashboard — Health progress dashboard route.

Aggregates weekly calorie and macro data from Firestore
for Chart.js visualisation on the frontend.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.firestore import get_weekly_stats_tool
from utils.validators import validate_user_id

router = APIRouter()


class DashboardStats(BaseModel):
    """Weekly aggregated nutrition statistics."""

    daily_calories: list[int]
    avg_protein: float
    avg_carbs: float
    avg_fat: float
    streak: int


@router.get("/", response_model=DashboardStats)
async def get_dashboard(user_id: str = Query(..., min_length=1, max_length=128)) -> DashboardStats:
    """
    Retrieve weekly nutrition stats for the progress dashboard.

    - Validates user_id format.
    - Aggregates Firestore meal logs for the past 7 days.
    - Returns daily calories + macro averages + streak count.
    """
    validate_user_id(user_id)

    try:
        stats = get_weekly_stats_tool(user_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Firestore error: {exc}") from exc

    return DashboardStats(**stats)
