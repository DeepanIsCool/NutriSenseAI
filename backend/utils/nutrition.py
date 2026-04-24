"""
Nutrition helper utilities.

Pure functions used by routes and tests. No external dependencies.
"""


def calculate_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    """
    Calculate Basal Metabolic Rate using the Mifflin-St Jeor equation.

    Args:
        weight_kg: Body weight in kilograms.
        height_cm: Height in centimetres.
        age: Age in years.
        sex: 'male' or 'female'.

    Returns:
        BMR in kilocalories per day.
    """
    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
    return base + (5 if sex.lower() == "male" else -161)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Multiply BMR by an activity factor to get Total Daily Energy Expenditure.

    Args:
        bmr: Basal Metabolic Rate (kcal/day).
        activity_level: One of 'sedentary', 'light', 'moderate', 'active', 'very_active'.

    Returns:
        TDEE in kilocalories per day.

    Raises:
        ValueError: If activity_level is not recognised.
    """
    factors = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }
    if activity_level not in factors:
        raise ValueError(f"Unknown activity level: {activity_level}")
    return round(bmr * factors[activity_level], 1)


def macro_split(calorie_goal: int, split: str = "balanced") -> dict[str, float]:
    """
    Compute macro-nutrient gram targets from a calorie goal.

    Args:
        calorie_goal: Daily calorie target (kcal).
        split: Macro split preset — 'balanced', 'low_carb', or 'high_protein'.

    Returns:
        dict with protein_g, carbs_g, fat_g.
    """
    presets: dict[str, tuple[float, float, float]] = {
        "balanced":     (0.25, 0.50, 0.25),
        "low_carb":     (0.35, 0.20, 0.45),
        "high_protein": (0.40, 0.40, 0.20),
    }
    protein_pct, carbs_pct, fat_pct = presets.get(split, presets["balanced"])
    return {
        "protein_g": round((calorie_goal * protein_pct) / 4, 1),
        "carbs_g":   round((calorie_goal * carbs_pct) / 4, 1),
        "fat_g":     round((calorie_goal * fat_pct) / 9, 1),
    }


def format_nutrition_label(nutrition: dict) -> str:
    """
    Format a nutrition dict into a human-readable label.

    Args:
        nutrition: Dict with keys calories, protein_g, carbs_g, fat_g.

    Returns:
        Formatted string, e.g. '350 kcal | P:28g C:40g F:8g'.
    """
    return (
        f"{nutrition.get('calories', 0)} kcal | "
        f"P:{nutrition.get('protein_g', 0)}g "
        f"C:{nutrition.get('carbs_g', 0)}g "
        f"F:{nutrition.get('fat_g', 0)}g"
    )
