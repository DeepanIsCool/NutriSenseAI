/**
 * AuthForm — Firebase email/password sign-in and sign-up.
 * Security: never stores credentials locally; uses Firebase Auth tokens.
 * Accessibility: all inputs labelled, errors announced via aria-live.
 * @module components/AuthForm
 */

import React, { useState, useCallback } from "react";
import { useAuth } from "../hooks/useAuth";

/**
 * AuthForm component.
 * Toggles between sign-in and sign-up modes.
 *
 * @returns {JSX.Element}
 */
function AuthForm() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { signIn, signUp } = useAuth();

  /** Handle form submission for both sign-in and sign-up. */
  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();
      setAuthError(null);
      setLoading(true);
      try {
        if (isSignUp) {
          await signUp(email, password);
        } else {
          await signIn(email, password);
        }
      } catch (err) {
        setAuthError(err.message);
      } finally {
        setLoading(false);
      }
    },
    [email, password, isSignUp, signIn, signUp]
  );

  return (
    <main className="auth-container" style={{ maxWidth: "400px", margin: "4rem auto", padding: "2rem" }}>
      <h1 style={{ marginBottom: "0.5rem" }}>🥗 NutriSense AI</h1>
      <p style={{ color: "#666", marginBottom: "2rem" }}>
        Food & Health App — Meal Intelligence Assistant
      </p>

      <h2>{isSignUp ? "Create Account" : "Sign In"}</h2>

      {authError && (
        <p role="alert" aria-live="assertive" className="error-msg">
          {authError}
        </p>
      )}

      <form onSubmit={handleSubmit} aria-label={isSignUp ? "Sign up form" : "Sign in form"}>
        <div className="form-group">
          <label htmlFor="email-input">Email address</label>
          <input
            id="email-input"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
            aria-required="true"
          />
        </div>

        <div className="form-group">
          <label htmlFor="password-input">Password</label>
          <input
            id="password-input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            autoComplete={isSignUp ? "new-password" : "current-password"}
            aria-required="true"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          aria-busy={loading}
          className="btn-primary"
          style={{ width: "100%", marginTop: "1rem" }}
        >
          {loading ? "Please wait…" : isSignUp ? "Create Account" : "Sign In"}
        </button>
      </form>

      <button
        onClick={() => setIsSignUp((prev) => !prev)}
        className="btn-link"
        style={{ marginTop: "1rem", display: "block", textAlign: "center" }}
        aria-label={isSignUp ? "Switch to sign in" : "Switch to create account"}
      >
        {isSignUp ? "Already have an account? Sign in" : "New here? Create account"}
      </button>
    </main>
  );
}

export default AuthForm;
