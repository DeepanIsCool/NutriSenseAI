"""
Google Maps & Places service — nearby healthy food finder.

Uses Places API (New) Nearby Search via HTTPS.
All calls debounced at route level; results cached in Firestore.
"""

import os
from typing import Any

import requests

_PLACES_BASE = "https://places.googleapis.com/v1/places:searchNearby"
_MAPS_API_KEY = os.environ.get("MAPS_API_KEY", "")


def find_nearby_healthy_places_tool(
    latitude: float,
    longitude: float,
    radius_meters: int = 2000,
    place_type: str = "restaurant",
) -> list[dict]:
    """
    Search for healthy food establishments near a coordinate.

    Args:
        latitude: User's current latitude.
        longitude: User's current longitude.
        radius_meters: Search radius (default 2000m = 2km).
        place_type: One of 'restaurant', 'grocery_or_supermarket', 'gym'.

    Returns:
        List of place dicts with name, address, rating, and maps_url.
    """
    if not _MAPS_API_KEY:
        return [{"error": "MAPS_API_KEY not configured"}]

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": _MAPS_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.id",
    }
    payload = {
        "includedTypes": [place_type],
        "maxResultCount": 10,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": radius_meters,
            }
        },
        "rankPreference": "RATING",
    }

    response = requests.post(_PLACES_BASE, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()

    results = []
    for place in data.get("places", []):
        place_id = place.get("id", "")
        results.append(
            {
                "name": place.get("displayName", {}).get("text", ""),
                "address": place.get("formattedAddress", ""),
                "rating": place.get("rating", 0),
                "maps_url": f"https://www.google.com/maps/place/?q=place_id:{place_id}",
            }
        )
    return results
