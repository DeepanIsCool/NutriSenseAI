/**
 * Dashboard — weekly nutrition progress visualised with Chart.js.
 * Data sourced from Firestore via /api/dashboard.
 * Accessible: all charts have ARIA labels + text summaries.
 * @module components/Dashboard
 */

import React, { useEffect, useState, useCallback } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar, Doughnut } from "react-chartjs-2";
import { fetchDashboardStats } from "../utils/api";

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend);

const DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

/**
 * Dashboard component.
 * Shows weekly calorie trend, macro breakdown doughnut, and streak counter.
 *
 * @param {{ userId: string, calorieGoal: number }} props
 * @returns {JSX.Element}
 */
function Dashboard({ userId, calorieGoal = 2000 }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /** Fetch weekly stats from Firestore via backend. */
  const loadStats = useCallback(async () => {
    if (!userId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchDashboardStats(userId);
      setStats(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => { loadStats(); }, [loadStats]);

  if (loading) return <p aria-busy="true">Loading dashboard…</p>;
  if (error) return <p role="alert" className="error-msg">{error}</p>;
  if (!stats) return null;

  const calorieData = {
    labels: DAY_LABELS.slice(0, stats.daily_calories.length),
    datasets: [
      {
        label: "Calories (kcal)",
        data: stats.daily_calories,
        backgroundColor: "#4caf8a",
        borderRadius: 6,
      },
      {
        label: "Goal",
        data: stats.daily_calories.map(() => calorieGoal),
        backgroundColor: "rgba(255,99,132,0.25)",
        borderRadius: 6,
      },
    ],
  };

  const macroData = {
    labels: ["Protein", "Carbs", "Fat"],
    datasets: [
      {
        data: [stats.avg_protein, stats.avg_carbs, stats.avg_fat],
        backgroundColor: ["#4caf8a", "#f5a623", "#e74c3c"],
      },
    ],
  };

  return (
    <section aria-labelledby="dashboard-heading" className="card">
      <h2 id="dashboard-heading">📊 Weekly Progress</h2>

      <p>
        🔥 <strong>Streak:</strong> {stats.streak} day{stats.streak !== 1 ? "s" : ""} logged
      </p>

      <div style={{ marginTop: "1.5rem" }}>
        <h3 id="calorie-chart-title">Daily Calories vs Goal</h3>
        <Bar
          data={calorieData}
          aria-label="Bar chart showing daily calories compared to your goal over the past week"
          role="img"
          options={{
            responsive: true,
            plugins: {
              legend: { position: "top" },
              title: { display: false },
            },
            scales: {
              y: { beginAtZero: true },
            },
          }}
        />
        {/* Text fallback for screen readers */}
        <p className="sr-only">
          Your daily calories this week:{" "}
          {stats.daily_calories.map((c, i) => `${DAY_LABELS[i]}: ${c}`).join(", ")}
        </p>
      </div>

      <div style={{ marginTop: "2rem", maxWidth: "280px" }}>
        <h3>Average Macro Breakdown</h3>
        <Doughnut
          data={macroData}
          aria-label={`Doughnut chart showing macro breakdown: Protein ${stats.avg_protein}g, Carbs ${stats.avg_carbs}g, Fat ${stats.avg_fat}g`}
          role="img"
        />
        <p className="sr-only">
          Average macros — Protein: {stats.avg_protein}g, Carbs: {stats.avg_carbs}g, Fat: {stats.avg_fat}g
        </p>
      </div>
    </section>
  );
}

export default Dashboard;
