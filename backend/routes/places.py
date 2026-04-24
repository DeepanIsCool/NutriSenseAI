"""
/api/places — Nearby healthy food finder route.

Calls Google Places API (New) via places_agent tool.
Results are cached and debounced at the service level.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.maps import find_nearby_healthy_places_tool

router = APIRouter()


class PlaceResult(BaseModel):
    """A single nearby place result."""

    name: str
    address: str
    rating: float
    maps_url: str


@router.get("/", response_model=list[PlaceResult])
async def find_nearby(
    lat: float = Query(..., ge=-90, le=90, description="User latitude"),
    lng: float = Query(..., ge=-180, le=180, description="User longitude"),
    radius: int = Query(default=2000, ge=100, le=10000, description="Search radius metres"),
    type: str = Query(default="restaurant", description="Place type: restaurant | grocery_or_supermarket | gym"),
) -> list[PlaceResult]:
    """
    Find healthy restaurants, grocery stores, or gyms near the user.

    - Validates coordinate ranges server-side.
    - Calls Places API (New) Nearby Search.
    - Returns top 10 results ranked by rating.
    """
    allowed_types = {"restaurant", "grocery_or_supermarket", "gym"}
    if type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"type must be one of {allowed_types}")

    try:
        places = find_nearby_healthy_places_tool(
            latitude=lat,
            longitude=lng,
            radius_meters=radius,
            place_type=type,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Places API error: {exc}") from exc

    return [PlaceResult(**p) for p in places if "error" not in p]
