"""
NutriSense AI — FastAPI backend entry point.

Boots the ADK-powered agent server alongside custom REST routes
for the Food & Health hackathon submission.
"""

import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.scan import router as scan_router
from routes.chat import router as chat_router
from routes.plan import router as plan_router
from routes.places import router as places_router
from routes.dashboard import router as dashboard_router

load_dotenv()

app = FastAPI(
    title="NutriSense AI",
    description="Food & Health AI Assistant powered by Google ADK + Gemini",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan_router, prefix="/api/scan", tags=["Food Scanner"])
app.include_router(chat_router, prefix="/api/chat", tags=["AI Coach"])
app.include_router(plan_router, prefix="/api/plan", tags=["Meal Planner"])
app.include_router(places_router, prefix="/api/places", tags=["Nearby Places"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint for deployment monitoring."""
    return {"status": "ok", "service": "nutrisense-ai"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
