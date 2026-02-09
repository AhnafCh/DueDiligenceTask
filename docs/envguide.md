# Environment Variable Guide

This guide explains exactly where to go and what to do to collect the required variables for your `.env` file.

---

## 1. Google API Key (`GOOGLE_API_KEY`)
*Required for AI-powered document analysis and answer generation using Gemini 2.5 Pro.*

1.  **Website**: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2.  **Action**: Log in with your Google account.
3.  **Create**: Click **Create API key in new project** or use an existing one.
4.  **Copy**: Copy the generated API key.
5.  **Limits**: Free tier is available but check the **[Generative AI pricing](https://ai.google.dev/pricing)** for rate limits and commercial use.

---

<!-- Redis section removed - now using database-backed queue -->

---

## 3. Database URL (`DATABASE_URL`)
*Determines where your projects, sections, and answers are saved.*

### Option A: SQLite (Default/Simplest)
1.  **Website**: N/A (Included with Python).
2.  **Value**: `sqlite:///./questionnaire.db`
3.  **Tool to view data**: Download **[DB Browser for SQLite](https://sqlitebrowser.org/dl/)** if you want to see the tables visually.

### Option B: PostgreSQL (Better for large data)
1.  **Website**: [https://www.postgresql.org/download/windows/](https://www.postgresql.org/download/windows/)
2.  **Download**: Download the **Interactive Installer by EDB**.
3.  **Setup**: During installation, set a password (remember it!).
4.  **Create DB**: Use the installed "pgAdmin 4" tool to create a new database named `questionnaire`.
5.  **Value**: `postgresql://postgres:YOUR_PASSWORD@localhost:5432/questionnaire`

---

## 4. CORS Origins (`CORS_ORIGINS`)
*Allows the frontend to communicate with the backend.*

1.  **Identify Port**: Check your frontend project.
    *   If using **Vite**, it's usually `http://localhost:5173`.
    *   If using **Create React App**, it's usually `http://localhost:3000`.
2.  **Value**: Enter the URL in your `.env`. You can add multiple separated by commas: `http://localhost:3000,http://localhost:5173`.

---

## 5. API Settings (`API_HOST`, `API_PORT`, `API_RELOAD`)
*Controls how the backend server starts.*

1.  **API_HOST**: Use `0.0.0.0` (allows access from other devices on your network) or `127.0.0.1` (local only).
2.  **API_PORT**: Set to `8000` (default for FastAPI).
3.  **API_RELOAD**: Set to `true` while developing so the server restarts when you save code changes.

---

## How to Apply These Values
1.  Go to the `backend/` folder.
2.  Create a file named `.env`.
3.  Paste the following (replacing with your actual values):
    ```env
    GOOGLE_API_KEY=your-api-key-here
    CELERY_BROKER_URL=sqla+sqlite:///./questionnaire.db
    DATABASE_URL=sqlite:///./questionnaire.db
    CORS_ORIGINS=http://localhost:5173
    API_HOST=0.0.0.0
    API_PORT=8000
    API_RELOAD=true
    LOG_LEVEL=INFO
    ```
