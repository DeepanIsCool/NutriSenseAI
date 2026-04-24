"""
/api/scan — Food photo scanner route.

Accepts a base64-encoded image, delegates to scan_agent via ADK,
and returns structured nutrition data.
"""

import base64
from io import BytesIO

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

from services.gemini import analyze_food_image_tool
from services.firestore import save_meal_log_tool
from utils.validators import validate_user_id, sanitize_string

router = APIRouter()


class ScanResponse(BaseModel):
    """Structured response from food image analysis."""

    food_name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    allergens: list[str]
    confidence: float
    doc_id: str | None = None


@router.post("/", response_model=ScanResponse)
async def scan_food(
    file: UploadFile = File(...),
    user_id: str = Form(...),
) -> ScanResponse:
    """
    Analyse a food photo and return nutrition estimates.

    - Validates user_id and file type.
    - Calls Gemini Vision via ADK scan_agent tool.
    - Persists result to Firestore meal log.
    - Returns structured nutrition data.
    """
    validate_user_id(user_id)

    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported image type.")

    # Limit upload size to 5MB
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image exceeds 5MB limit.")

    image_b64 = base64.b64encode(contents).decode("utf-8")

    try:
        nutrition = analyze_food_image_tool(image_b64, file.content_type)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Gemini Vision error: {exc}") from exc

    # Persist to Firestore
    save_result = save_meal_log_tool(user_id, nutrition)

    return ScanResponse(**nutrition, doc_id=save_result.get("doc_id"))
