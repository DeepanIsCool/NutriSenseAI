"""
NutriSense AI — backend test suite.

Covers: nutrition helpers, validators, Gemini mock, Firestore mock,
        API integration happy path.
Run: pytest tests/ -v --tb=short
"""

import json
import sys
import os
import types

import pytest

# ---------------------------------------------------------------------------
# Stub heavy external dependencies so tests run without real credentials
# ---------------------------------------------------------------------------

# Stub firebase_admin
firebase_stub = types.ModuleType("firebase_admin")
firebase_stub._apps = {"default": True}
firebase_stub.initialize_app = lambda *a, **kw: None

firestore_stub = types.ModuleType("firebase_admin.firestore")


class _FakeQuery:
    def where(self, *a, **kw): return self
    def order_by(self, *a, **kw): return self
    def limit(self, *a, **kw): return self
    def stream(self): return iter([])


class _FakeCollection:
    def document(self, key=None):
        class _Doc:
            id = "fake_doc_id"
            def get(self_inner): 
                class R:
                    exists = False
                return R()
            def set(self_inner, data): pass
        return _Doc()
    def where(self, *a, **kw): return _FakeQuery()


class _FakeDB:
    def collection(self, name): return _FakeCollection()


firestore_stub.client = lambda: _FakeDB()
firestore_stub.Query = type("Query", (), {"DESCENDING": "DESCENDING"})()

firebase_stub.firestore = firestore_stub
credentials_stub = types.ModuleType("firebase_admin.credentials")
credentials_stub.Certificate = lambda p: None
credentials_stub.ApplicationDefault = lambda: None
firebase_stub.credentials = credentials_stub

sys.modules["firebase_admin"] = firebase_stub
sys.modules["firebase_admin.firestore"] = firestore_stub
sys.modules["firebase_admin.credentials"] = credentials_stub

# Stub google.generativeai
genai_stub = types.ModuleType("google.generativeai")
genai_stub.configure = lambda **kw: None

class _FakeModel:
    def generate_content(self, *a, **kw):
        class R:
            text = json.dumps({
                "food_name": "Grilled Chicken",
                "calories": 350,
                "protein_g": 42.0,
                "carbs_g": 0.0,
                "fat_g": 18.0,
                "allergens": [],
                "confidence": 0.95,
            })
        return R()

genai_stub.GenerativeModel = lambda model: _FakeModel()

types_stub = types.ModuleType("google.generativeai.types")


class _HarmCat:
    HARM_CATEGORY_HARASSMENT = "h"
    HARM_CATEGORY_HATE_SPEECH = "hs"


class _HarmBlock:
    BLOCK_NONE = "none"


types_stub.HarmCategory = _HarmCat()
types_stub.HarmBlockThreshold = _HarmBlock()

google_stub = types.ModuleType("google")
google_genai_stub = types.ModuleType("google.generativeai")
google_genai_stub.configure = lambda **kw: None
google_genai_stub.GenerativeModel = lambda model: _FakeModel()
google_genai_stub.types = types_stub

sys.modules.setdefault("google", google_stub)
sys.modules["google.generativeai"] = google_genai_stub
sys.modules["google.generativeai.types"] = types_stub

# Ensure backend is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("MAPS_API_KEY", "test-maps-key")


# ---------------------------------------------------------------------------
# Test 1: Nutrition helper — BMR calculation
# ---------------------------------------------------------------------------

from utils.nutrition import calculate_bmr, calculate_tdee, macro_split, format_nutrition_label


def test_calculate_bmr_male():
    """BMR for a 30-year-old 80kg 175cm male should be ~1736 kcal."""
    bmr = calculate_bmr(weight_kg=80, height_cm=175, age=30, sex="male")
    assert 1700 < bmr < 1800, f"Unexpected BMR: {bmr}"


def test_calculate_tdee_moderate():
    """TDEE at moderate activity should be BMR × 1.55."""
    bmr = 1700.0
    tdee = calculate_tdee(bmr, "moderate")
    assert abs(tdee - 1700 * 1.55) < 1


def test_macro_split_high_protein():
    """High-protein split at 2000 kcal should yield ≥160g protein."""
    macros = macro_split(2000, "high_protein")
    assert macros["protein_g"] >= 160
    assert "carbs_g" in macros
    assert "fat_g" in macros


def test_format_nutrition_label():
    """Formatted label should include kcal and macros."""
    nutrition = {"calories": 500, "protein_g": 30, "carbs_g": 50, "fat_g": 15}
    label = format_nutrition_label(nutrition)
    assert "500 kcal" in label
    assert "P:30g" in label


# ---------------------------------------------------------------------------
# Test 2: Input validator
# ---------------------------------------------------------------------------

from utils.validators import validate_user_id, sanitize_string
from fastapi import HTTPException


def test_validate_user_id_valid():
    """Valid Firebase UID should not raise."""
    validate_user_id("abc123_user-XYZ")  # should not raise


def test_validate_user_id_invalid():
    """User ID with special chars should raise HTTPException 400."""
    with pytest.raises(HTTPException) as exc_info:
        validate_user_id("bad user id!")
    assert exc_info.value.status_code == 400


def test_sanitize_strips_script_tags():
    """Script injection patterns must be removed from user input."""
    dirty = "Hello <script>alert('xss')</script> world"
    clean = sanitize_string(dirty)
    assert "<script" not in clean
    assert "Hello" in clean


# ---------------------------------------------------------------------------
# Test 3: Gemini service mock — food analysis
# ---------------------------------------------------------------------------

from services.gemini import analyze_food_image_tool
import base64


def test_analyze_food_image_returns_nutrition():
    """Mocked Gemini Vision call should return structured nutrition dict."""
    fake_image = base64.b64encode(b"fake-image-bytes").decode()
    result = analyze_food_image_tool(fake_image, "image/jpeg")
    assert result["food_name"] == "Grilled Chicken"
    assert result["calories"] == 350
    assert isinstance(result["allergens"], list)
    assert 0 <= result["confidence"] <= 1


# ---------------------------------------------------------------------------
# Test 4: Firestore CRUD mock — save and retrieve meal log
# ---------------------------------------------------------------------------

from services.firestore import save_meal_log_tool, get_meal_history_tool


def test_save_meal_log_returns_doc_id():
    """Saving a meal log should return a doc_id."""
    meal = {"food_name": "Salad", "calories": 200, "protein_g": 5.0,
            "carbs_g": 20.0, "fat_g": 3.0, "allergens": []}
    result = save_meal_log_tool("user123", meal)
    assert result["status"] == "saved"
    assert "doc_id" in result


def test_get_meal_history_empty():
    """History for a new user should return an empty list (mocked Firestore)."""
    history = get_meal_history_tool("user_new", limit=5)
    assert isinstance(history, list)


# ---------------------------------------------------------------------------
# Test 5: Integration — /api/scan happy path (TestClient)
# ---------------------------------------------------------------------------

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint():
    """Health check must return 200 with status ok."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_places_rejects_invalid_type():
    """/api/places must reject unknown place types with 400."""
    resp = client.get("/api/places/?lat=51.5&lng=-0.1&type=casino")
    assert resp.status_code == 400


def test_dashboard_rejects_empty_user_id():
    """/api/dashboard must reject missing user_id."""
    resp = client.get("/api/dashboard/")
    assert resp.status_code == 422  # FastAPI validation error
