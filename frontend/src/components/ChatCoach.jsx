/**
 * ChatCoach — conversational AI diet coach powered by Gemini Pro + ADK.
 * Maintains local message history. Backend has access to Firestore meal history.
 * @module components/ChatCoach
 */

import React, { useState, useRef, useEffect, useCallback } from "react";
import { useGemini } from "../hooks/useGemini";

/**
 * ChatCoach component.
 * Provides a conversational interface to the AI diet coach.
 *
 * @param {{ userId: string, userGoal: string, dietaryRestrictions: string }} props
 * @returns {JSX.Element}
 */
function ChatCoach({ userId, userGoal = "maintain weight", dietaryRestrictions = "none" }) {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hi! I'm your NutriSense coach. Ask me anything about your diet." },
  ]);
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);
  const { chat, loading, error } = useGemini();

  /** Scroll to the latest message on update. */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  /** Send user message and append coach reply. */
  const handleSend = useCallback(async () => {
    const trimmed = input.trim().slice(0, 500);
    if (!trimmed || !userId) return;

    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setInput("");

    const data = await chat(userId, trimmed, userGoal, dietaryRestrictions);
    if (data) {
      setMessages((prev) => [...prev, { role: "assistant", text: data.reply }]);
    }
  }, [input, userId, userGoal, dietaryRestrictions, chat]);

  /** Allow Enter key to send (Shift+Enter for newline). */
  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  return (
    <section aria-labelledby="coach-heading" className="card">
      <h2 id="coach-heading">💬 AI Diet Coach</h2>

      <div
        role="log"
        aria-live="polite"
        aria-label="Conversation with your AI diet coach"
        className="chat-log"
        style={{ maxHeight: "360px", overflowY: "auto", padding: "0.5rem" }}
      >
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`chat-bubble chat-${msg.role}`}
            style={{
              textAlign: msg.role === "user" ? "right" : "left",
              margin: "0.4rem 0",
            }}
          >
            <span className="bubble-text">{msg.text}</span>
          </div>
        ))}
        {loading && (
          <div aria-busy="true" className="chat-bubble chat-assistant">
            <span className="bubble-text typing">Thinking…</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {error && (
        <p role="alert" className="error-msg">
          {error}
        </p>
      )}

      <div className="chat-input-row" style={{ display: "flex", gap: "0.5rem", marginTop: "0.75rem" }}>
        <label htmlFor="chat-input" className="sr-only">
          Message your diet coach
        </label>
        <textarea
          id="chat-input"
          rows={2}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about your diet…"
          maxLength={500}
          aria-label="Type your diet question here"
          style={{ flex: 1, resize: "none", borderRadius: "6px", padding: "0.5rem" }}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          aria-label="Send message to diet coach"
          className="btn-primary"
        >
          Send
        </button>
      </div>
    </section>
  );
}

export default ChatCoach;
