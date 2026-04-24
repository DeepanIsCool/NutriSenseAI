/**
 * MealPlanner — generates a 7-day personalised meal plan via Gemini Pro.
 * Plan is persisted to Firestore for the user's session.
 * @module components/MealPlanner
 */

import React, { useState, useCallback } from "react";
import { useGemini } from "../hooks/useGemini";

const CUISINES = ["Balanced", "Mediterranean", "Asian", "Mexican", "Indian", "American"];

/**
 * MealPlanner component.
 * Collects user preferences and renders a 7-day meal plan.
 *
 * @param {{ userId: string }} props
 * @returns {JSX.Element}
 */
function MealPlanner({ userId }) {
  const [calories, setCalories] = useState(2000);
  const [cuisine, setCuisine] = useState("Balanced");
  const [budget, setBudget] = useState(100);
  const [restrictions, setRestrictions] = useState("none");
  const [plan, setPlan] = useState(null);
  const { planMeals, loading, error } = useGemini();

  /** Request a new meal plan from the backend. */
  const handleGenerate = useCallback(async () => {
    if (!userId) return;
    const data = await planMeals(userId, calories, cuisine, budget, restrictions);
    if (data) setPlan(data.days);
  }, [userId, calories, cuisine, budget, restrictions, planMeals]);

  return (
    <section aria-labelledby="planner-heading" className="card">
      <h2 id="planner-heading">📅 7-Day Meal Planner</h2>

      <form onSubmit={(e) => { e.preventDefault(); handleGenerate(); }} aria-label="Meal plan preferences form">
        <div className="form-group">
          <label htmlFor="calorie-input">Daily calorie goal (kcal)</label>
          <input
            id="calorie-input"
            type="number"
            min={800}
            max={5000}
            value={calories}
            onChange={(e) => setCalories(Number(e.target.value))}
            aria-describedby="calorie-hint"
          />
          <small id="calorie-hint">Between 800 and 5000 kcal</small>
        </div>

        <div className="form-group">
          <label htmlFor="cuisine-select">Cuisine preference</label>
          <select
            id="cuisine-select"
            value={cuisine}
            onChange={(e) => setCuisine(e.target.value)}
            aria-label="Select your preferred cuisine style"
          >
            {CUISINES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="budget-input">Weekly budget (USD)</label>
          <input
            id="budget-input"
            type="number"
            min={20}
            max={500}
            value={budget}
            onChange={(e) => setBudget(Number(e.target.value))}
          />
        </div>

        <div className="form-group">
          <label htmlFor="restrictions-input">Dietary restrictions</label>
          <input
            id="restrictions-input"
            type="text"
            value={restrictions}
            maxLength={200}
            onChange={(e) => setRestrictions(e.target.value)}
            placeholder="e.g. vegan, gluten-free"
            aria-label="Enter any dietary restrictions separated by commas"
          />
        </div>

        <button type="submit" disabled={loading} aria-busy={loading} className="btn-primary">
          {loading ? "Generating plan…" : "Generate Plan"}
        </button>
      </form>

      {error && <p role="alert" className="error-msg">{error}</p>}

      {plan && (
        <div aria-live="polite" style={{ marginTop: "1.5rem" }}>
          {plan.map((day) => (
            <details key={day.day} style={{ marginBottom: "0.75rem" }}>
              <summary style={{ cursor: "pointer", fontWeight: 600 }}>
                Day {day.day}
              </summary>
              <ul style={{ marginTop: "0.4rem" }}>
                {Object.entries(day.meals).map(([mealName, meal]) => (
                  <li key={mealName}>
                    <strong style={{ textTransform: "capitalize" }}>{mealName}:</strong>{" "}
                    {meal.name} — {meal.calories} kcal
                  </li>
                ))}
              </ul>
            </details>
          ))}
        </div>
      )}
    </section>
  );
}

export default MealPlanner;
