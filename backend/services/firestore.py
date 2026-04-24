"""
Firestore service — meal logs, plans, and result caching.

Uses Firebase Admin SDK with service-account credentials loaded
from environment variables (Security pillar — no hardcoded secrets).
"""

import json
import os
from datetime import datetime
from typing import Any

import firebase_admin
from firebase_admin import credentials, firestore

# ---------------------------------------------------------------------------
# Initialise Firebase Admin SDK (idempotent)
# ---------------------------------------------------------------------------

def _init_firebase() -> None:
    """Initialise Firebase Admin SDK if not already initialised."""
    if firebase_admin._apps:
        return
    cred_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH")
    if cred_path:
        cred = credentials.Certificate(cred_path)
    else:
        # Fall back to Application Default Credentials (Cloud Run / CI)
        cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)


_init_firebase()
_db = firestore.client()

# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

_CACHE_COLLECTION = "gemini_cache"


def get_cached_result(cache_key: str) -> dict | None:
    """
    Retrieve a previously cached Gemini result from Firestore.

    Args:
        cache_key: Unique key identifying the cached entry.

    Returns:
        Cached dict or None if not found.
    """
    doc = _db.collection(_CACHE_COLLECTION).document(cache_key).get()
    if doc.exists:
        return doc.to_dict().get("data")
    return None


def set_cached_result(cache_key: str, data: dict) -> None:
    """
    Persist a Gemini result to Firestore for future cache hits.

    Args:
        cache_key: Unique key identifying the cached entry.
        data: Result dict to store.
    """
    _db.collection(_CACHE_COLLECTION).document(cache_key).set(
        {"data": data, "cached_at": datetime.utcnow().isoformat()}
    )


# ---------------------------------------------------------------------------
# Meal log CRUD
# ---------------------------------------------------------------------------

_MEALS_COLLECTION = "meal_logs"


def save_meal_log_tool(user_id: str, meal_data: dict) -> dict:
    """
    Save a scanned meal entry to Firestore.

    Args:
        user_id: Firebase Auth UID of the user.
        meal_data: Nutrition data dict from Gemini Vision analysis.

    Returns:
        dict with 'doc_id' of the saved document.
    """
    doc_ref = _db.collection(_MEALS_COLLECTION).document()
    payload = {
        **meal_data,
        "user_id": user_id,
        "logged_at": datetime.utcnow().isoformat(),
    }
    doc_ref.set(payload)
    return {"doc_id": doc_ref.id, "status": "saved"}


def get_meal_history_tool(user_id: str, limit: int = 10) -> list[dict]:
    """
    Retrieve the most recent meal logs for a user.

    Args:
        user_id: Firebase Auth UID of the user.
        limit: Maximum number of records to return (default 10).

    Returns:
        List of meal log dicts ordered by most recent first.
    """
    docs = (
        _db.collection(_MEALS_COLLECTION)
        .where("user_id", "==", user_id)
        .order_by("logged_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    return [{"id": d.id, **d.to_dict()} for d in docs]


# ---------------------------------------------------------------------------
# Meal plan CRUD
# ---------------------------------------------------------------------------

_PLANS_COLLECTION = "meal_plans"


def save_meal_plan_tool(user_id: str, plan_data: dict) -> dict:
    """
    Save a generated meal plan to Firestore.

    Args:
        user_id: Firebase Auth UID of the user.
        plan_data: Generated meal plan dict.

    Returns:
        dict with 'doc_id' of the saved document.
    """
    doc_ref = _db.collection(_PLANS_COLLECTION).document()
    doc_ref.set(
        {
            **plan_data,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
        }
    )
    return {"doc_id": doc_ref.id, "status": "saved"}


def get_weekly_stats_tool(user_id: str) -> dict:
    """
    Aggregate weekly calorie and macro totals from meal logs.

    Args:
        user_id: Firebase Auth UID of the user.

    Returns:
        dict with daily_calories list, avg_protein, avg_carbs, avg_fat, streak.
    """
    from datetime import timedelta  # noqa: PLC0415

    seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
    docs = (
        _db.collection(_MEALS_COLLECTION)
        .where("user_id", "==", user_id)
        .where("logged_at", ">=", seven_days_ago)
        .stream()
    )
    meals = [d.to_dict() for d in docs]

    daily: dict[str, dict] = {}
    for meal in meals:
        day = meal.get("logged_at", "")[:10]
        if day not in daily:
            daily[day] = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
        daily[day]["calories"] += meal.get("calories", 0)
        daily[day]["protein"] += meal.get("protein_g", 0)
        daily[day]["carbs"] += meal.get("carbs_g", 0)
        daily[day]["fat"] += meal.get("fat_g", 0)

    days_list = sorted(daily.values(), key=lambda x: x)
    total = len(days_list) or 1

    return {
        "daily_calories": [d["calories"] for d in days_list],
        "avg_protein": round(sum(d["protein"] for d in days_list) / total, 1),
        "avg_carbs": round(sum(d["carbs"] for d in days_list) / total, 1),
        "avg_fat": round(sum(d["fat"] for d in days_list) / total, 1),
        "streak": len(daily),
    }
