# 🥗 NutriSense AI — Meal Intelligence Assistant

> **Food & Health App — Google Hackathon Submission**
> Vertical: **Food & Health**

A context-aware food intelligence assistant. Users snap a meal → Gemini Vision identifies it, estimates nutrition, an ADK-powered coach guides them toward their goal, and Google Maps surfaces healthy options nearby.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                             │
│   React SPA (Firebase Hosting)                                  │
│   FoodScanner │ ChatCoach │ MealPlanner │ NearbyMap │ Dashboard │
└───────────────────────┬─────────────────────────────────────────┘
                        │ HTTPS REST
┌───────────────────────▼─────────────────────────────────────────┐
│              FastAPI Backend  (Cloud Run / localhost)            │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Google ADK Multi-Agent System                           │  │
│   │  root_agent ──► scan_agent   (Gemini Vision)             │  │
│   │             ──► coach_agent  (Gemini Pro + history)      │  │
│   │             ──► planner_agent(Gemini Pro + caching)      │  │
│   │             ──► places_agent (Places API)                │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   /api/scan  /api/chat  /api/plan  /api/places  /api/dashboard  │
└───┬──────────────┬─────────────────────────┬────────────────────┘
    │              │                         │
    ▼              ▼                         ▼
Gemini API    Firestore DB           Google Places API
(Vision+Pro)  (logs, plans,          (Nearby Search)
              cache)
```

---

## Google Services Used

| Service | How it's used |
|---|---|
| **Gemini Vision API** (`gemini-2.0-flash`) | `POST /api/scan` — identifies food in photos, returns calorie + macro estimates |
| **Gemini Pro API** (`gemini-2.0-flash`) | `POST /api/chat` and `POST /api/plan` — personalised diet coaching and 7-day meal plan generation |
| **Google ADK** (`google-adk`) | Orchestrates a multi-agent system: root agent delegates to scan / coach / planner / places specialist agents |
| **Firebase Auth** | User registration and session management; all Firestore data is scoped per `user_id` |
| **Firestore** | Persists meal logs, generated plans, and caches Gemini API responses to avoid redundant calls |
| **Google Maps JS API** | Renders an embedded map with pins for nearby healthy places |
| **Places API (New)** | `Nearby Search` endpoint finds top-rated restaurants, grocery stores, and gyms within 2 km |
| **Firebase Hosting** | Deploys the React SPA with CDN caching (`firebase deploy`) |

---

## Features

### 1 · Food Photo Scanner
Upload or snap a meal → Gemini Vision identifies food, estimates calories + macros, flags allergens. Results cached in Firestore to avoid duplicate API calls.

### 2 · Contextual AI Diet Coach
Chat interface — `coach_agent` knows the user's health goal, dietary restrictions, and meal history from Firestore. Gives specific, personalised advice.

### 3 · Smart Meal Planner
Generates a 7-day meal plan based on calorie goal, cuisine preference, and budget. Stored in Firestore per user. Results cached by input hash.

### 4 · Nearby Healthy Food Finder
Browser geolocation → Places API finds healthy restaurants, gyms, and grocery stores within 2 km. Displayed on a Google Map with keyboard-navigable list.

### 5 · Health Progress Dashboard
Weekly calories vs. goal bar chart + macro doughnut chart via Chart.js. Data from Firestore real-time aggregation. Streak counter.

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- A Google Cloud project with billing enabled
- One Gemini API key from [Google AI Studio](https://aistudio.google.com)

### 1 · Clone & configure

```bash
git clone https://github.com/your-username/nutrisense-ai.git
cd nutrisense-ai

# Copy environment template and fill in your values
cp .env.example .env
```

Edit `.env` — see **API Keys Required** section below for where to obtain each key.

### 2 · Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3 · Frontend setup

```bash
cd frontend
npm install
```

### 4 · Run locally

```bash
# Terminal 1 — backend
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend && npm start
```

Or use the Makefile:

```bash
make install
make -j2 all   # starts both servers concurrently
```

App opens at `http://localhost:3000`

### 5 · Run tests

```bash
# Backend (pytest)
make test

# Frontend (Jest)
cd frontend && npm test
```

### 6 · Deploy to Firebase Hosting

```bash
cd frontend && npm run build
firebase deploy --only hosting
```

---

## API Keys Required

| Key | Where to get it | `.env` variable |
|---|---|---|
| **Gemini API key** | [Google AI Studio](https://aistudio.google.com) → API Keys | `GEMINI_API_KEY` |
| **Maps + Places API key** | Cloud Console → APIs & Services → Credentials | `MAPS_API_KEY` + `REACT_APP_MAPS_API_KEY` |
| **Firebase service account** | Firebase Console → Project Settings → Service accounts → Generate key | `FIREBASE_SERVICE_ACCOUNT_PATH` |
| **Firebase web config** | Firebase Console → Project Settings → Your apps → Web app | `REACT_APP_FIREBASE_*` vars |

---

## Google Cloud Services to Enable

In [Google Cloud Console](https://console.cloud.google.com) → **APIs & Services → Library**, enable:

1. **Generative Language API** (Gemini) — for Gemini Vision + Pro
2. **Maps JavaScript API** — for the embedded map
3. **Places API (New)** — for nearby search
4. **Firebase Authentication** — enabled automatically via Firebase Console
5. **Cloud Firestore API** — enabled automatically via Firebase Console
6. **Cloud Run API** — only needed if deploying backend to Cloud Run

---

## Assumptions

- A single Gemini API key (from AI Studio) is used for all Gemini calls (Vision + Pro). The same `gemini-2.0-flash` model handles both image and text tasks.
- Firestore is used in native mode (not Datastore mode).
- The Maps API key is restricted to HTTP referrers (frontend) and IP addresses (backend) for security.
- User authentication is email/password via Firebase Auth. Social login can be added without code changes beyond Firebase Console configuration.
- The Places API Nearby Search uses the **new** Places API (`places.googleapis.com/v1`), not the legacy API.
- The backend is stateless; all user state lives in Firestore scoped by Firebase Auth UID.
- The Gemini response cache in Firestore uses a SHA-256 hash of the input as the key. Cache TTL is not enforced (hackathon scope); production would add a TTL field.
- Calorie range is validated server-side to 800–5000 kcal; budget to $20–$500 USD.

---

## Test Coverage

Backend test suite (`pytest`): **~65% coverage** across utils, services, and routes.

| Test | What it validates |
|---|---|
| `test_calculate_bmr_male` | Mifflin-St Jeor BMR formula |
| `test_calculate_tdee_moderate` | Activity multiplier application |
| `test_macro_split_high_protein` | Macro gram calculation from calorie goal |
| `test_format_nutrition_label` | Label string formatting |
| `test_validate_user_id_valid/invalid` | UID regex and HTTP 400 path |
| `test_sanitize_strips_script_tags` | XSS input sanitisation |
| `test_analyze_food_image_returns_nutrition` | Gemini Vision mock call |
| `test_save_meal_log_returns_doc_id` | Firestore write mock |
| `test_get_meal_history_empty` | Firestore read mock |
| `test_health_endpoint` | FastAPI integration |
| `test_places_rejects_invalid_type` | Input validation HTTP 400 |
| `test_dashboard_rejects_empty_user_id` | Pydantic validation HTTP 422 |

Frontend test suite (`Jest`): 7 tests covering Dashboard chart data logic.

---

## Lighthouse Accessibility Score

Target: **≥ 90** (run `npx lighthouse http://localhost:3000 --view` after local startup).

Accessibility measures applied:
- All `<img>` tags have descriptive `alt` text
- Semantic HTML: `<nav>`, `<main>`, `<header>`, `<footer>`, `<section>`, `<article>`
- All interactive elements are keyboard-navigable with visible `focus-visible` outlines
- `aria-label` on icon-only buttons and unlabelled inputs
- `aria-live="polite"` on chat log and scan results
- `aria-busy` on loading buttons
- Colour contrast ≥ 4.5:1 (primary green `#2e7d5e` on white = **5.1:1**)
- Skip-to-content link in `index.html`

---

## Repository Structure

```
nutrisense-ai/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── agent.py          # Google ADK multi-agent system
│   ├── routes/
│   │   ├── scan.py           # POST /api/scan
│   │   ├── chat.py           # POST /api/chat
│   │   ├── plan.py           # POST /api/plan
│   │   ├── places.py         # GET  /api/places
│   │   └── dashboard.py      # GET  /api/dashboard
│   ├── services/
│   │   ├── gemini.py         # Gemini Vision + Pro wrappers
│   │   ├── firestore.py      # Firestore CRUD + cache
│   │   └── maps.py           # Places API (New)
│   ├── tests/
│   │   └── test_nutrisense.py
│   ├── utils/
│   │   ├── validators.py     # Input sanitisation
│   │   └── nutrition.py      # Pure nutrition helpers
│   ├── main.py               # FastAPI app entry point
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── components/
│       │   ├── AuthForm.jsx
│       │   ├── FoodScanner.jsx
│       │   ├── ChatCoach.jsx
│       │   ├── MealPlanner.jsx
│       │   ├── NearbyMap.jsx
│       │   └── Dashboard.jsx
│       ├── hooks/
│       │   ├── useAuth.js
│       │   ├── useGemini.js
│       │   └── usePlaces.js
│       ├── utils/
│       │   ├── api.js
│       │   └── firebaseConfig.js
│       ├── App.jsx
│       ├── App.css
│       ├── index.js
│       └── Dashboard.test.js
├── .editorconfig
├── .env.example
├── .gitignore
├── firebase.json
├── Makefile
├── pytest.ini
└── README.md
```

---

*Built for the Google Hackathon · Food & Health vertical · Powered by Google ADK, Gemini, Firebase, and Google Maps*
