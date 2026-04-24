"""
NutriSense AI agents built with Google ADK.

Defines a multi-agent system:
- root_agent      : orchestrator that delegates to specialists
- scan_agent      : interprets Gemini Vision food analysis
- coach_agent     : personalised diet coaching
- planner_agent   : 7-day meal plan generation
"""

import os

from google.adk.agents import Agent

from services.gemini import (
    analyze_food_image_tool,
    generate_meal_plan_tool,
    get_nutrition_advice_tool,
)
from services.firestore import (
    save_meal_log_tool,
    get_meal_history_tool,
    save_meal_plan_tool,
)
from services.maps import find_nearby_healthy_places_tool


# ---------------------------------------------------------------------------
# Specialist agents
# ---------------------------------------------------------------------------

scan_agent = Agent(
    name="scan_agent",
    model="gemini-2.0-flash",
    description="Identifies food from images and returns calorie + macro estimates.",
    instruction=(
        "You are a food recognition specialist. "
        "When given a food image analysis result, extract: food name, "
        "estimated calories, protein (g), carbs (g), fat (g), and any "
        "common allergens. Return structured JSON. "
        "Be concise and accurate. Do not hallucinate nutrients."
    ),
    tools=[analyze_food_image_tool, save_meal_log_tool],
)

coach_agent = Agent(
    name="coach_agent",
    model="gemini-2.0-flash",
    description="Provides personalised diet coaching based on user goals and history.",
    instruction=(
        "You are a certified nutrition coach. "
        "Use the user's health goal, dietary restrictions, and meal history "
        "to give specific, actionable advice — not generic tips. "
        "Always cite the user's actual data when making recommendations. "
        "Keep responses under 200 words."
    ),
    tools=[get_nutrition_advice_tool, get_meal_history_tool],
)

planner_agent = Agent(
    name="planner_agent",
    model="gemini-2.0-flash",
    description="Generates a 7-day personalised meal plan.",
    instruction=(
        "You are a meal planning expert. "
        "Generate a realistic 7-day meal plan based on calorie goal, "
        "cuisine preference, and budget. Each day must include "
        "breakfast, lunch, dinner, and one snack with estimated calories. "
        "Return valid JSON conforming to the MealPlan schema."
    ),
    tools=[generate_meal_plan_tool, save_meal_plan_tool],
)

places_agent = Agent(
    name="places_agent",
    model="gemini-2.0-flash",
    description="Finds healthy restaurants and grocery stores nearby.",
    instruction=(
        "You help users find healthy food options near them. "
        "Use the places tool to search for healthy restaurants, "
        "grocery stores, or gyms. Format results as a clean list "
        "with name, distance, and rating."
    ),
    tools=[find_nearby_healthy_places_tool],
)

# ---------------------------------------------------------------------------
# Root orchestrator
# ---------------------------------------------------------------------------

root_agent = Agent(
    name="nutrisense_root",
    model="gemini-2.0-flash",
    description="NutriSense AI orchestrator — routes requests to specialist agents.",
    instruction=(
        "You are NutriSense AI, a food and health intelligence assistant. "
        "Route user requests to the correct specialist:\n"
        "- Food photo analysis → scan_agent\n"
        "- Diet advice / coaching → coach_agent\n"
        "- Meal planning → planner_agent\n"
        "- Nearby healthy places → places_agent\n"
        "Always be helpful, concise, and evidence-based."
    ),
    sub_agents=[scan_agent, coach_agent, planner_agent, places_agent],
)
