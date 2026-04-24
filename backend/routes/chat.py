"""
/api/chat — Contextual AI diet coach route.

Streams user messages through coach_agent, which has access to
Firestore meal history for personalised responses.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from services.gemini import get_nutrition_advice_tool
from services.firestore import get_meal_history_tool
from utils.validators import validate_user_id, sanitize_string

router = APIRouter()

_MAX_MESSAGE_LEN = 500


class ChatRequest(BaseModel):
    """Incoming chat request from the diet coach UI."""

    user_id: str
    message: str = Field(..., max_length=_MAX_MESSAGE_LEN)
    user_goal: str = Field(default="maintain weight", max_length=100)
    dietary_restrictions: str = Field(default="none", max_length=200)

    @field_validator("message", "user_goal", "dietary_restrictions")
    @classmethod
    def strip_and_sanitize(cls, value: str) -> str:
        """Strip whitespace and sanitize user text inputs."""
        return sanitize_string(value.strip())


class ChatResponse(BaseModel):
    """Structured response from the AI coach."""

    reply: str
    recent_meals_used: int


@router.post("/", response_model=ChatResponse)
async def chat_with_coach(body: ChatRequest) -> ChatResponse:
    """
    Send a message to the AI diet coach and receive personalised advice.

    - Fetches last 5 meals from Firestore for context.
    - Calls Gemini Pro via get_nutrition_advice_tool.
    - Returns personalised advice string.
    """
    validate_user_id(body.user_id)

    history = get_meal_history_tool(body.user_id, limit=5)
    recent_meal_names = [m.get("food_name", "") for m in history if m.get("food_name")]

    try:
        advice = get_nutrition_advice_tool(
            user_goal=body.user_goal,
            dietary_restrictions=body.dietary_restrictions,
            recent_meals=recent_meal_names,
            question=body.message,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Gemini error: {exc}") from exc

    return ChatResponse(reply=advice, recent_meals_used=len(recent_meal_names))
