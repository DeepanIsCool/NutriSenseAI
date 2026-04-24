/**
 * Centralised API client for NutriSense AI backend.
 * All calls go over HTTPS. No plain HTTP endpoints used.
 * @module api
 */

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

/**
 * Scan a food image and return nutrition estimates.
 * @param {File} imageFile - The food image file to analyse.
 * @param {string} userId - Firebase Auth UID of the current user.
 * @returns {Promise<Object>} Nutrition data including calories and macros.
 */
export async function scanFoodImage(imageFile, userId) {
  const formData = new FormData();
  formData.append("file", imageFile);
  formData.append("user_id", userId);

  const resp = await fetch(`${BASE_URL}/scan/`, {
    method: "POST",
    body: formData,
  });
  if (!resp.ok) throw new Error(`Scan failed: ${resp.status}`);
  return resp.json();
}

/**
 * Send a message to the AI diet coach.
 * @param {string} userId - Firebase Auth UID.
 * @param {string} message - User's question (max 500 chars).
 * @param {string} userGoal - Health goal string.
 * @param {string} dietaryRestrictions - Comma-separated restrictions.
 * @returns {Promise<Object>} Coach reply and context metadata.
 */
export async function chatWithCoach(userId, message, userGoal, dietaryRestrictions) {
  const resp = await fetch(`${BASE_URL}/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: userId,
      message: message.slice(0, 500),
      user_goal: userGoal,
      dietary_restrictions: dietaryRestrictions,
    }),
  });
  if (!resp.ok) throw new Error(`Chat failed: ${resp.status}`);
  return resp.json();
}

/**
 * Generate a 7-day meal plan.
 * @param {string} userId - Firebase Auth UID.
 * @param {number} calorieGoal - Daily calorie target (800–5000).
 * @param {string} cuisinePreference - Preferred cuisine.
 * @param {number} budgetUsd - Weekly food budget.
 * @param {string} dietaryRestrictions - Comma-separated restrictions.
 * @returns {Promise<Object>} Meal plan with 7 days of meals.
 */
export async function generateMealPlan(userId, calorieGoal, cuisinePreference, budgetUsd, dietaryRestrictions) {
  const resp = await fetch(`${BASE_URL}/plan/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: userId,
      calorie_goal: calorieGoal,
      cuisine_preference: cuisinePreference,
      budget_usd: budgetUsd,
      dietary_restrictions: dietaryRestrictions,
    }),
  });
  if (!resp.ok) throw new Error(`Plan failed: ${resp.status}`);
  return resp.json();
}

/**
 * Find healthy places near a coordinate.
 * @param {number} lat - User latitude.
 * @param {number} lng - User longitude.
 * @param {string} type - Place type: restaurant | grocery_or_supermarket | gym.
 * @returns {Promise<Array>} List of nearby places with ratings.
 */
export async function findNearbyPlaces(lat, lng, type = "restaurant") {
  const params = new URLSearchParams({ lat, lng, type });
  const resp = await fetch(`${BASE_URL}/places/?${params}`);
  if (!resp.ok) throw new Error(`Places failed: ${resp.status}`);
  return resp.json();
}

/**
 * Fetch weekly dashboard stats for the current user.
 * @param {string} userId - Firebase Auth UID.
 * @returns {Promise<Object>} Weekly calories, macros, and streak.
 */
export async function fetchDashboardStats(userId) {
  const params = new URLSearchParams({ user_id: userId });
  const resp = await fetch(`${BASE_URL}/dashboard/?${params}`);
  if (!resp.ok) throw new Error(`Dashboard failed: ${resp.status}`);
  return resp.json();
}
