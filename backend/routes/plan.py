"""
/api/plan — Smart meal planner route.

Delegates to planner_agent to generate a 7-day meal plan,
then persists it to Firestore for the user session.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from services.gemini import generate_meal_plan_tool
from services.firestore import save_meal_plan_tool
from utils.validators import validate_user_id, sanitize_string

router = APIRouter()


class PlanRequest(BaseModel):
    """Request body for meal plan generation."""

    user_id: str
    calorie_goal: int = Field(..., ge=800, le=5000)
    cuisine_preference: str = Field(default="balanced", max_length=50)
    budget_usd: float = Field(..., ge=20.0, le=500.0)
    dietary_restrictions: str = Field(default="none", max_length=200)

    @field_validator("cuisine_preference", "dietary_restrictions")
    @classmethod
    def sanitize_text(cls, value: str) -> str:
        """Sanitize text inputs before sending to Gemini."""
        return sanitize_string(value.strip())


class PlanResponse(BaseModel):
    """Response containing the generated 7-day plan."""

    days: list[dict]
    doc_id: str | None = None


@router.post("/", response_model=PlanResponse)
async def generate_plan(body: PlanRequest) -> PlanResponse:
    """
    Generate a personalised 7-day meal plan.

    - Validates input ranges (calories 800–5000, budget $20–$500).
    - Calls Gemini Pro via generate_meal_plan_tool (cached).
    - Saves plan to Firestore.
    - Returns structured day-by-day meal plan.
    """
    validate_user_id(body.user_id)

    try:
        plan = generate_meal_plan_tool(
            calorie_goal=body.calorie_goal,
            cuisine_preference=body.cuisine_preference,
            budget_usd=body.budget_usd,
            dietary_restrictions=body.dietary_restrictions,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Planner error: {exc}") from exc

    save_result = save_meal_plan_tool(body.user_id, plan)
    return PlanResponse(days=plan.get("days", []), doc_id=save_result.get("doc_id"))
