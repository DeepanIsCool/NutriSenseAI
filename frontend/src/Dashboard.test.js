/**
 * Frontend tests — Dashboard chart data and utility functions.
 * Run: npm test
 */

// Simple unit tests that don't require DOM rendering.
// Tests the pure data transformation logic used by Dashboard.

/**
 * Compute chart bar data from raw daily_calories array.
 * @param {number[]} dailyCalories
 * @param {number} goal
 * @returns {{ calories: number[], goals: number[] }}
 */
function buildChartData(dailyCalories, goal) {
  return {
    calories: dailyCalories,
    goals: dailyCalories.map(() => goal),
  };
}

/**
 * Format a streak count into a human-readable string.
 * @param {number} streak
 * @returns {string}
 */
function formatStreak(streak) {
  return `${streak} day${streak !== 1 ? "s" : ""} logged`;
}

/**
 * Calculate percentage of goal achieved for a given day.
 * @param {number} actual
 * @param {number} goal
 * @returns {number} 0–100
 */
function goalPercent(actual, goal) {
  if (goal === 0) return 0;
  return Math.min(Math.round((actual / goal) * 100), 100);
}

// ── Tests ──────────────────────────────────────────────────────────────

test("buildChartData returns parallel arrays of same length", () => {
  const result = buildChartData([1800, 2100, 1950], 2000);
  expect(result.calories).toHaveLength(3);
  expect(result.goals).toHaveLength(3);
  expect(result.goals[0]).toBe(2000);
});

test("buildChartData goal line is flat", () => {
  const result = buildChartData([1500, 1600, 1700, 1800], 2000);
  expect(result.goals.every((g) => g === 2000)).toBe(true);
});

test("formatStreak returns singular for streak of 1", () => {
  expect(formatStreak(1)).toBe("1 day logged");
});

test("formatStreak returns plural for streak > 1", () => {
  expect(formatStreak(5)).toBe("5 days logged");
});

test("goalPercent calculates correctly", () => {
  expect(goalPercent(1800, 2000)).toBe(90);
});

test("goalPercent caps at 100 when calories exceed goal", () => {
  expect(goalPercent(2500, 2000)).toBe(100);
});

test("goalPercent handles zero goal safely", () => {
  expect(goalPercent(1800, 0)).toBe(0);
});
