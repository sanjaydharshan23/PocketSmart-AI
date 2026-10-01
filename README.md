# PocketSmart AI

A complete FastAPI + Jinja2 + JavaScript implementation of the PocketSmart AI specification: Home Interior, Party, and Jewelry budget planners; registration/login; JWT-in-cookie sessions; recommendation history; Gemini integration; and fallback recommendations when AI is unavailable.

## 1. VS Code setup

1. Install Python 3.11+ and VS Code.
2. Open this folder in VS Code.
3. Create a virtual environment:
   - Windows PowerShell: `py -3 -m venv .venv`
   - macOS/Linux: `python3 -m venv .venv`
4. Activate it:
   - Windows PowerShell: `.venv\\Scripts\\Activate.ps1`
   - macOS/Linux: `source .venv/bin/activate`
5. Install packages: `pip install -r requirements.txt`
6. Copy `.env.example` to `.env`.
7. Set a strong `SECRET_KEY`.
8. Add `GEMINI_API_KEY` if you want live Gemini recommendations.
9. Start the app: `uvicorn app.main:app --reload`
10. Open http://127.0.0.1:8000

## 2. Gemini configuration

The source document specifies Gemini 1.5 Flash Pro. The code intentionally keeps the model configurable with `GEMINI_MODEL`. Set it to the model identifier available to your Google AI account. The example defaults to `gemini-2.5-flash` so a current Gemini API account can be used; if your account exposes the documented model, you can set `GEMINI_MODEL=gemini-1.5-flash-pro`.

Without a Gemini key, the app still runs end-to-end using deterministic fallback recommendations and marketplace search links. This is useful for UI/API testing.

## 3. Application routes

- `GET /` landing page
- `GET /login`, `/register`, `/dashboard`, `/history`
- `GET /planner/home`, `/planner/party`, `/planner/jewelry`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `POST /api/generate-home`
- `POST /api/generate-party`
- `POST /api/generate-jewelry` (multipart form, optional image)
- `GET /api/history`
- `GET /health`

FastAPI Swagger docs are available at `/docs`.

## 4. Testing

Run: `pytest -q`

The test suite covers health, registration/login, protected planner access, and fallback recommendation generation.

## 5. Project structure

```text
pocketsmart_ai/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── auth.py
│   ├── models/
│   ├── routers/
│   ├── services/
│   ├── templates/
│   └── static/
├── tests/
├── uploads/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 6. Architecture notes

The documentation mixes Flask and FastAPI in different sections. This implementation uses FastAPI consistently because the later milestones explicitly define FastAPI routes, startup, structured models, Jinja2 templates, and Uvicorn. The source also mentions third-party product/service APIs and simulated scraping; to keep the application reliable and compliant without undocumented credentials or brittle scraping, the implementation uses generated/search links plus fallback catalog data. Real affiliate/product APIs can be added behind `app/services/catalog.py` later.

## 7. Production hardening checklist

Use HTTPS, a random secret key, secure cookies, a production database, rate limiting, CSRF protection if changing auth architecture, object storage for uploads, virus/content scanning for uploaded images, provider-specific API credentials, structured logging, and monitoring before public deployment.
