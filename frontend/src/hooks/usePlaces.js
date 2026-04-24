/**
 * usePlaces — hook for Google Places nearby search with debounce.
 * Debounces geolocation calls to avoid redundant Places API requests (Efficiency pillar).
 * @module hooks/usePlaces
 */

import { useState, useCallback, useRef } from "react";
import { findNearbyPlaces } from "../utils/api";

const DEBOUNCE_MS = 600;

/**
 * Hook for fetching nearby healthy places with built-in debounce.
 * @returns {{ places, loading, error, searchNearby }}
 */
export function usePlaces() {
  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const timerRef = useRef(null);

  /**
   * Debounced search for nearby places.
   * @param {number} lat - Latitude.
   * @param {number} lng - Longitude.
   * @param {string} type - Place type filter.
   */
  const searchNearby = useCallback((lat, lng, type = "restaurant") => {
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(async () => {
      setLoading(true);
      setError(null);
      try {
        const results = await findNearbyPlaces(lat, lng, type);
        setPlaces(results);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }, DEBOUNCE_MS);
  }, []);

  return { places, loading, error, searchNearby };
}
