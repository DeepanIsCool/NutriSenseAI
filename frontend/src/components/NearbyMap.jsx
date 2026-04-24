/**
 * NearbyMap — shows healthy restaurants, grocery stores, and gyms on a Google Map.
 * Uses Google Maps JS API Loader + Places API via backend proxy.
 * Fully keyboard-navigable with ARIA labels.
 * @module components/NearbyMap
 */

import React, { useState, useEffect, useRef, useCallback } from "react";
import { Loader } from "@googlemaps/js-api-loader";
import { usePlaces } from "../hooks/usePlaces";

const PLACE_TYPES = [
  { value: "restaurant", label: "🍽 Restaurants" },
  { value: "grocery_or_supermarket", label: "🛒 Grocery Stores" },
  { value: "gym", label: "🏋️ Gyms" },
];

/**
 * NearbyMap component.
 * Renders a Google Map centred on the user's location,
 * with pins for nearby healthy places.
 *
 * @returns {JSX.Element}
 */
function NearbyMap() {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef([]);
  const [placeType, setPlaceType] = useState("restaurant");
  const [location, setLocation] = useState(null);
  const [geoError, setGeoError] = useState(null);
  const { places, loading, error, searchNearby } = usePlaces();

  /** Load Google Maps and initialise the map instance. */
  useEffect(() => {
    const loader = new Loader({
      apiKey: process.env.REACT_APP_MAPS_API_KEY || "",
      version: "weekly",
    });

    loader.load().then(() => {
      if (mapRef.current && !mapInstanceRef.current) {
        mapInstanceRef.current = new window.google.maps.Map(mapRef.current, {
          zoom: 14,
          center: { lat: 37.7749, lng: -122.4194 },
        });
      }
    });
  }, []);

  /** Request geolocation, then trigger nearby search. */
  const handleLocate = useCallback(() => {
    if (!navigator.geolocation) {
      setGeoError("Geolocation not supported by your browser.");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        const { latitude, longitude } = coords;
        setLocation({ lat: latitude, lng: longitude });
        if (mapInstanceRef.current) {
          mapInstanceRef.current.setCenter({ lat: latitude, lng: longitude });
        }
        searchNearby(latitude, longitude, placeType);
      },
      () => setGeoError("Could not retrieve your location.")
    );
  }, [placeType, searchNearby]);

  /** Re-search when place type changes. */
  useEffect(() => {
    if (location) searchNearby(location.lat, location.lng, placeType);
  }, [placeType]); // eslint-disable-line react-hooks/exhaustive-deps

  /** Drop map markers for each place result. */
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    markersRef.current.forEach((m) => m.setMap(null));
    markersRef.current = [];

    places.forEach((place) => {
      if (!place.maps_url) return;
      const marker = new window.google.maps.Marker({
        position: mapInstanceRef.current.getCenter(),
        map: mapInstanceRef.current,
        title: place.name,
      });
      markersRef.current.push(marker);
    });
  }, [places]);

  return (
    <section aria-labelledby="map-heading" className="card">
      <h2 id="map-heading">📍 Healthy Places Near Me</h2>

      <div role="group" aria-label="Filter place type" style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem", flexWrap: "wrap" }}>
        {PLACE_TYPES.map(({ value, label }) => (
          <button
            key={value}
            onClick={() => setPlaceType(value)}
            aria-pressed={placeType === value}
            className={`btn-filter ${placeType === value ? "active" : ""}`}
          >
            {label}
          </button>
        ))}
      </div>

      <button onClick={handleLocate} disabled={loading} aria-busy={loading} className="btn-primary">
        {loading ? "Searching…" : "Find Near Me"}
      </button>

      {(geoError || error) && (
        <p role="alert" className="error-msg">{geoError || error}</p>
      )}

      <div
        ref={mapRef}
        role="application"
        aria-label="Google Map showing healthy places near you"
        style={{ width: "100%", height: "320px", marginTop: "1rem", borderRadius: "8px" }}
      />

      {places.length > 0 && (
        <ul aria-label="List of nearby healthy places" style={{ marginTop: "1rem", padding: 0, listStyle: "none" }}>
          {places.map((place, i) => (
            <li key={i} style={{ marginBottom: "0.5rem" }}>
              <a
                href={place.maps_url}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={`Open ${place.name} in Google Maps`}
              >
                <strong>{place.name}</strong>
              </a>{" "}
              ⭐ {place.rating} — <small>{place.address}</small>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default NearbyMap;
