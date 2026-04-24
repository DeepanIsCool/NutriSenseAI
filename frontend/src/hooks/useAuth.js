/**
 * useAuth — Firebase Auth state hook.
 * Provides current user and sign-in/out helpers.
 * @module hooks/useAuth
 */

import { useState, useEffect } from "react";
import {
  getAuth,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
} from "firebase/auth";

/**
 * Custom hook that exposes Firebase Auth state and helpers.
 * @returns {{ user: Object|null, loading: boolean, signIn: Function, signUp: Function, logOut: Function }}
 */
export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const auth = getAuth();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      setUser(firebaseUser);
      setLoading(false);
    });
    return unsubscribe;
  }, [auth]);

  /**
   * Sign in an existing user.
   * @param {string} email
   * @param {string} password
   */
  const signIn = (email, password) =>
    signInWithEmailAndPassword(auth, email, password);

  /**
   * Register a new user.
   * @param {string} email
   * @param {string} password
   */
  const signUp = (email, password) =>
    createUserWithEmailAndPassword(auth, email, password);

  /** Sign out the current user. */
  const logOut = () => signOut(auth);

  return { user, loading, signIn, signUp, logOut };
}
