/**
 * FoodScanner — upload a meal photo and get instant nutrition analysis.
 * Uses Gemini Vision via the /api/scan endpoint.
 * @module components/FoodScanner
 */

import React, { useState, useCallback } from "react";
import { useGemini } from "../hooks/useGemini";

/**
 * FoodScanner component.
 * Allows users to upload or snap a food image, then displays
 * Gemini Vision nutrition estimates.
 *
 * @param {{ userId: string }} props
 * @returns {JSX.Element}
 */
function FoodScanner({ userId }) {
  const [preview, setPreview] = useState(null);
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const { scanFood, loading, error } = useGemini();

  /** Handle file input change — generate a local preview URL. */
  const handleFileChange = useCallback((e) => {
    const selected = e.target.files[0];
    if (!selected) return;
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setResult(null);
  }, []);

  /** Submit the selected image to the backend for analysis. */
  const handleScan = useCallback(async () => {
    if (!file || !userId) return;
    const data = await scanFood(file, userId);
    if (data) setResult(data);
  }, [file, userId, scanFood]);

  return (
    <section aria-labelledby="scanner-heading" className="card">
      <h2 id="scanner-heading">🔍 Food Scanner</h2>
      <p>Snap or upload a meal photo — Gemini Vision identifies it instantly.</p>

      <label htmlFor="food-upload" className="upload-label">
        Choose meal photo
        <input
          id="food-upload"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleFileChange}
          aria-label="Upload a food photo for nutrition analysis"
          style={{ display: "none" }}
        />
      </label>

      {preview && (
        <img
          src={preview}
          alt="Preview of the meal you selected for nutrition analysis"
          className="preview-img"
          width={300}
          height={220}
          style={{ objectFit: "cover", borderRadius: "8px", marginTop: "1rem" }}
        />
      )}

      <button
        onClick={handleScan}
        disabled={!file || loading}
        aria-busy={loading}
        className="btn-primary"
        style={{ marginTop: "1rem" }}
      >
        {loading ? "Analysing…" : "Analyse Meal"}
      </button>

      {error && (
        <p role="alert" className="error-msg">
          {error}
        </p>
      )}

      {result && (
        <article aria-live="polite" className="result-card" style={{ marginTop: "1.5rem" }}>
          <h3>{result.food_name}</h3>
          <dl className="macro-grid">
            <div>
              <dt>Calories</dt>
              <dd>{result.calories} kcal</dd>
            </div>
            <div>
              <dt>Protein</dt>
              <dd>{result.protein_g}g</dd>
            </div>
            <div>
              <dt>Carbs</dt>
              <dd>{result.carbs_g}g</dd>
            </div>
            <div>
              <dt>Fat</dt>
              <dd>{result.fat_g}g</dd>
            </div>
          </dl>
          {result.allergens.length > 0 && (
            <p>
              <strong>Allergens:</strong> {result.allergens.join(", ")}
            </p>
          )}
          <p>
            <small>Confidence: {Math.round(result.confidence * 100)}%</small>
          </p>
        </article>
      )}
    </section>
  );
}

export default FoodScanner;
