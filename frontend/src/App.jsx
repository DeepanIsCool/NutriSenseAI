/**
 * App — NutriSense AI root component.
 * Manages tab navigation and Firebase Auth gate.
 * Semantic HTML: uses <nav>, <main>, <button>. No div-onclick anti-patterns.
 * @module App
 */

import React, { useState } from "react";
import { useAuth } from "./hooks/useAuth";
import AuthForm from "./components/AuthForm";
import FoodScanner from "./components/FoodScanner";
import ChatCoach from "./components/ChatCoach";
import MealPlanner from "./components/MealPlanner";
import NearbyMap from "./components/NearbyMap";
import Dashboard from "./components/Dashboard";
import "./App.css";

const TABS = [
  { id: "scanner", label: "🔍 Scanner" },
  { id: "coach", label: "💬 Coach" },
  { id: "planner", label: "📅 Planner" },
  { id: "map", label: "📍 Nearby" },
  { id: "dashboard", label: "📊 Dashboard" },
];

/**
 * App root component.
 * Gates all features behind Firebase Auth.
 * @returns {JSX.Element}
 */
function App() {
  const { user, loading, logOut } = useAuth();
  const [activeTab, setActiveTab] = useState("scanner");

  if (loading) {
    return (
      <main aria-busy="true" style={{ textAlign: "center", marginTop: "4rem" }}>
        <p>Loading NutriSense AI…</p>
      </main>
    );
  }

  if (!user) return <AuthForm />;

  return (
    <>
      <header className="app-header" role="banner">
        <span className="app-logo">🥗 NutriSense AI</span>
        <button
          onClick={logOut}
          aria-label="Sign out of NutriSense AI"
          className="btn-link"
        >
          Sign out
        </button>
      </header>

      <nav aria-label="Main navigation" className="tab-nav">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            aria-current={activeTab === tab.id ? "page" : undefined}
            aria-label={`Navigate to ${tab.label}`}
            className={`tab-btn ${activeTab === tab.id ? "tab-active" : ""}`}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <main id="main-content" className="app-main">
        {activeTab === "scanner" && <FoodScanner userId={user.uid} />}
        {activeTab === "coach" && (
          <ChatCoach
            userId={user.uid}
            userGoal="maintain weight"
            dietaryRestrictions="none"
          />
        )}
        {activeTab === "planner" && <MealPlanner userId={user.uid} />}
        {activeTab === "map" && <NearbyMap />}
        {activeTab === "dashboard" && (
          <Dashboard userId={user.uid} calorieGoal={2000} />
        )}
      </main>

      <footer role="contentinfo" style={{ textAlign: "center", padding: "2rem", color: "#999", fontSize: "0.85rem" }}>
        NutriSense AI · Powered by Google Gemini, Firebase &amp; ADK
      </footer>
    </>
  );
}

export default App;
