/**
 * useGemini — hook for calling NutriSense backend endpoints.
 * Manages loading and error state for all AI-powered features.
 * @module hooks/useGemini
 */

import { useState, useCallback } from "react";
import { scanFoodImage, chatWithCoach, generateMealPlan } from "../utils/api";

/**
 * Hook wrapping backend AI calls with loading and error state.
 * @returns {{ scanFood, chat, planMeals, loading, error }}
 */
export function useGemini() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Analyse a food photo.
   * @param {File} file - Image file.
   * @param {string} userId - Firebase UID.
   * @returns {Promise<Object|null>}
   */
  const scanFood = useCallback(async (file, userId) => {
    setLoading(true);
    setError(null);
    try {
      return await scanFoodImage(file, userId);
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Send a diet coach message.
   * @param {string} userId
   * @param {string} message
   * @param {string} goal
   * @param {string} restrictions
   * @returns {Promise<Object|null>}
   */
  const chat = useCallback(async (userId, message, goal, restrictions) => {
    setLoading(true);
    setError(null);
    try {
      return await chatWithCoach(userId, message, goal, restrictions);
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Generate a 7-day meal plan.
   * @param {string} userId
   * @param {number} calories
   * @param {string} cuisine
   * @param {number} budget
   * @param {string} restrictions
   * @returns {Promise<Object|null>}
   */
  const planMeals = useCallback(async (userId, calories, cuisine, budget, restrictions) => {
    setLoading(true);
    setError(null);
    try {
      return await generateMealPlan(userId, calories, cuisine, budget, restrictions);
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { scanFood, chat, planMeals, loading, error };
}
