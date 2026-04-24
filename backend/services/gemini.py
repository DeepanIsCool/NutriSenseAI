"""
Gemini service — wraps Gemini Vision and Pro API calls.

All results are cached in Firestore to avoid redundant API calls
and reduce latency on repeated requests (Efficiency pillar).
"""

import base64
import hashlib
import json
import os
from typing import Any

import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold, HarmCategory

# Configure SDK once at import time
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

_VISION_MODEL = "gemini-2.0-flash"
_PRO_MODEL = "gemini-2.0-flash"

_SAFETY = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
}


def _cache_key(prefix: str, payload: str) -> str:
    """Generate a deterministic Firestore cache key from a payload hash."""
    digest = hashlib.sha256(payload.encode()).hexdigest()[:16]
    return f"{prefix}_{digest}"


def analyze_food_image_tool(image_base64: str, mime_type: str = "image/jpeg") -> dict:
    """
    Identify food in an image and return nutrition estimates.

    Args:
        image_base64: Base64-encoded image bytes.
        mime_type: MIME type of the image (default image/jpeg).

    Returns:
        dict with keys: food_name, calories, protein_g, carbs_g,
                        fat_g, allergens, confidence.
    """
    # Lazy import to avoid circular dependency with firestore service
    from services.firestore import get_cached_result, set_cached_result  # noqa: PLC0415

    cache_key = _cache_key("scan", image_base64[:64])
    cached = get_cached_result(cache_key)
    if cached:
        return cached

    model = genai.GenerativeModel(_VISION_MODEL)
    prompt = (
        "Analyse this food image. Return ONLY valid JSON with these exact keys: "
        "food_name (string), calories (int), protein_g (float), carbs_g (float), "
        "fat_g (float), allergens (list of strings), confidence (float 0-1). "
        "No markdown, no explanation."
    )
    image_part = {"mime_type": mime_type, "data": image_base64}
    response = model.generate_content([prompt, image_part], safety_settings=_SAFETY)

    raw = response.text.strip().strip("```json").strip("```").strip()
    result = json.loads(raw)
    set_cached_result(cache_key, result)
    return result


def get_nutrition_advice_tool(
    user_goal: str,
    dietary_restrictions: str,
    recent_meals: list[str],
    question: str,
) -> str:
    """
    Generate personalised nutrition advice using Gemini Pro.

    Args:
        user_goal: User's health goal (e.g., 'lose 5kg', 'build muscle').
        dietary_restrictions: Comma-separated restrictions (e.g., 'vegan, gluten-free').
        recent_meals: List of recent meal descriptions.
        question: Specific question from the user.

    Returns:
        Personalised advice string (max 200 words).
    """
    model = genai.GenerativeModel(_PRO_MODEL)
    meal_summary = "; ".join(recent_meals[-5:]) if recent_meals else "No recent meals."
    prompt = (
        f"User goal: {user_goal}\n"
        f"Dietary restrictions: {dietary_restrictions}\n"
        f"Recent meals: {meal_summary}\n"
        f"Question: {question}\n\n"
        "Give specific, actionable nutrition advice in under 200 words. "
        "Reference the user's actual data. Do not give generic tips."
    )
    response = model.generate_content(prompt, safety_settings=_SAFETY)
    return response.text.strip()


def generate_meal_plan_tool(
    calorie_goal: int,
    cuisine_preference: str,
    budget_usd: float,
    dietary_restrictions: str,
) -> dict:
    """
    Generate a 7-day meal plan with Gemini Pro.

    Args:
        calorie_goal: Daily calorie target (kcal).
        cuisine_preference: Preferred cuisine type (e.g., 'Mediterranean').
        budget_usd: Weekly food budget in USD.
        dietary_restrictions: Comma-separated dietary restrictions.

    Returns:
        dict with key 'days' containing a list of 7 day plans.
    """
    cache_key = _cache_key(
        "plan", f"{calorie_goal}{cuisine_preference}{budget_usd}{dietary_restrictions}"
    )
    from services.firestore import get_cached_result, set_cached_result  # noqa: PLC0415

    cached = get_cached_result(cache_key)
    if cached:
        return cached

    model = genai.GenerativeModel(_PRO_MODEL)
    prompt = (
        f"Create a 7-day meal plan for:\n"
        f"- Daily calories: {calorie_goal} kcal\n"
        f"- Cuisine: {cuisine_preference}\n"
        f"- Weekly budget: ${budget_usd}\n"
        f"- Restrictions: {dietary_restrictions}\n\n"
        "Return ONLY valid JSON: "
        '{"days": [{"day": 1, "meals": {"breakfast": {"name": "", "calories": 0}, '
        '"lunch": {"name": "", "calories": 0}, '
        '"dinner": {"name": "", "calories": 0}, '
        '"snack": {"name": "", "calories": 0}}}]}'
        " for all 7 days. No markdown."
    )
    response = model.generate_content(prompt, safety_settings=_SAFETY)
    raw = response.text.strip().strip("```json").strip("```").strip()
    result = json.loads(raw)
    set_cached_result(cache_key, result)
    return result
