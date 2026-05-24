# Telegram English Vocabulary AI App — Technical Task (T3)

This folder is made for AI coding agents. It contains the full technical task, project rules, architecture requirements, MVP scope, environment format, and implementation steps.

The goal is to build a clean portfolio-ready Telegram project: a personal English vocabulary notebook powered by Gemini AI, PostgreSQL, Docker Compose, FastAPI, aiogram, and a Telegram Mini App frontend.

---

## 1. Project idea

Build a Telegram-based English learning application.

The app should help a user quickly save new English words or phrases during daily life, for example during school lessons. The user enters an English word, phrase, or sentence. The app sends it to Gemini AI. Gemini analyzes the meaning and returns a useful learning card. The result is saved to PostgreSQL so the user can later open the app, view saved entries, search them, and repeat them.

This is not just a translator. It is a smart vocabulary notebook.

The first version is MVP V1 only.

---

## 2. Main product logic

User flow:

1. User opens Telegram.
2. User either:
   - sends a word or phrase directly to the bot, or
   - opens the Telegram Mini App and types the word or phrase there.
3. Backend receives the input.
4. Backend validates the input.
5. Backend sends the text to Gemini API.
6. Gemini returns structured vocabulary data.
7. Backend saves the result to PostgreSQL.
8. User sees the processed learning card.
9. User can later open the Mini App and view saved vocabulary.

---

## 3. MVP V1 scope

Build only the core features. Do not add advanced future functionality unless it is marked as TODO.

### Must have in V1

- Telegram bot using aiogram.
- Telegram Mini App frontend using React + Vite + TypeScript.
- FastAPI backend.
- PostgreSQL database through Docker Compose.
- SQLAlchemy models.
- Alembic migrations.
- Gemini API integration only.
- `.env.example` with all required variables.
- Docker-first project structure.
- Saved vocabulary entries by Telegram user ID.
- API endpoints for creating and reading vocabulary entries.
- Clean README in project root.
- Basic frontend UI for adding and viewing entries.
- Basic error handling.
- Clean code organization.

### Should have in V1 if simple

- Search by original text or translation.
- Entry status: `new`, `learning`, `learned`.
- Delete entry.
- Update entry status.
- Simple loading and error states in frontend.

### Must not have in V1

- Payments.
- Multi-language learning system beyond English input and Russian explanations.
- Complex spaced repetition algorithm.
- Authentication outside Telegram user identity.
- Admin panel.
- OpenAI integration.
- Long-term analytics.
- Social features.
- Public user profiles.
- Unnecessary microservices.

---

## 4. Required technology stack

### Backend

- Python 3.11+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x async style
- asyncpg
- Alembic
- aiogram 3.x
- httpx
- python-dotenv or pydantic-settings
- PostgreSQL

### Frontend

- React
- Vite
- TypeScript
- Telegram WebApp SDK
- CSS modules or simple clean CSS

Do not use a heavy UI library unless absolutely necessary.

### AI

Use Gemini API only.

Do not implement OpenAI, Anthropic, local LLM, or any other AI provider in V1.

Gemini configuration must come from environment variables:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`

The default model in `.env.example` should be editable. Use a free/cheap Gemini model by default, for example:

```env
GEMINI_MODEL=gemini-2.0-flash
```

If the exact model name changes later, the developer should only change `.env`, not source code.

---

## 5. Required project structure

Create this structure:

```text
project-root/
  .ai/
    README.md
    AGENTS.md
    subagents/
      backend-reviewer.md
      frontend-reviewer.md
      docker-db-reviewer.md

  backend/
    app/
      __init__.py
      main.py
      core/
        __init__.py
        config.py
      api/
        __init__.py
        v1/
          __init__.py
          router.py
          vocabulary.py
      bot/
        __init__.py
        main.py
        handlers.py
        keyboards.py
      db/
        __init__.py
        session.py
        base.py
      models/
        __init__.py
        vocabulary.py
      schemas/
        __init__.py
        vocabulary.py
      services/
        __init__.py
        gemini_service.py
        vocabulary_service.py
      repositories/
        __init__.py
        vocabulary_repository.py
    alembic/
      versions/
    alembic.ini
    Dockerfile
    requirements.txt

  frontend/
    src/
      main.tsx
      App.tsx
      api/
        client.ts
        vocabulary.ts
      components/
        EntryCard.tsx
        EntryForm.tsx
        EntryList.tsx
      types/
        vocabulary.ts
      styles/
        global.css
    index.html
    package.json
    tsconfig.json
    vite.config.ts
    Dockerfile

  docker-compose.yml
  .env.example
  .gitignore
  README.md
```

Keep this structure unless there is a strong technical reason to change it. If changing it, document why.

---

## 6. Environment variables

Create `.env.example` in the project root.

Use this format and add all required variables:

```env
# PostgreSQL inside Docker
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=english_vocabulary
POSTGRES_HOST=db
DB_PORT=5432
HOST_DB_PORT=55432

# Telegram Bot
TG_BOT_TOKEN=your_bot_token_here

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_RELOAD=true
API_V1_PREFIX=/api/v1

# Frontend / Telegram Mini App
FRONTEND_PORT=5173
WEBAPP_URL=http://localhost:5173
VITE_API_URL=/api/v1

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TIMEOUT_SECONDS=30

# App settings
APP_ENV=development
LOG_LEVEL=INFO
DEFAULT_UI_LANGUAGE=ru
DEFAULT_LEARNING_LANGUAGE=en
DEFAULT_TRANSLATION_LANGUAGE=ru

# Security / CORS
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Backend should build database URL from the PostgreSQL variables. Do not hardcode database credentials in code.

Example internal Docker database URL:

```text
postgresql+asyncpg://postgres:postgres@db:5432/english_vocabulary
```

Do not commit a real `.env` file.

---

## 7. Database design

Use PostgreSQL.

### Table: vocabulary_entries

Recommended columns:

```text
id UUID primary key
tg_user_id BIGINT not null
original_text TEXT not null
normalized_text TEXT not null
translation_ru TEXT not null
meaning_ru TEXT not null
part_of_speech VARCHAR(64) nullable
level VARCHAR(16) nullable
transcription TEXT nullable
examples JSONB not null default []
synonyms JSONB not null default []
tags JSONB not null default []
status VARCHAR(32) not null default 'new'
ai_model VARCHAR(128) nullable
raw_ai_response JSONB nullable
created_at TIMESTAMP with time zone not null
updated_at TIMESTAMP with time zone not null
```

### Status values

Use simple statuses:

- `new`
- `learning`
- `learned`

No complex spaced repetition in V1.

### User identity

Every entry must belong to a Telegram user:

```text
tg_user_id
```

Do not mix entries between users.

---

## 8. Gemini response format

The Gemini service must request structured JSON.

The app should ask Gemini to analyze the English input and return JSON like this:

```json
{
  "original_text": "shallow",
  "normalized_text": "shallow",
  "translation_ru": "мелкий; поверхностный",
  "meaning_ru": "Слово может описывать небольшую глубину или поверхностное отношение/мысль.",
  "part_of_speech": "adjective",
  "level": "B1",
  "transcription": "/ˈʃæl.oʊ/",
  "examples": [
    {
      "en": "The water is shallow near the shore.",
      "ru": "Вода мелкая возле берега."
    },
    {
      "en": "That was a shallow explanation.",
      "ru": "Это было поверхностное объяснение."
    }
  ],
  "synonyms": ["superficial", "not deep"],
  "tags": ["adjective", "common"]
}
```

### Gemini prompt rules

The prompt must tell Gemini:

- The input is English or mostly English.
- Return only valid JSON.
- Do not return Markdown.
- Explain meanings in Russian.
- Examples must be practical and natural.
- If the input is a phrase, explain it as a phrase, not as separate words only.
- If the input has several meanings, show the most useful meanings.
- Keep output concise but useful.

### AI error handling

If Gemini fails:

- Return a clear error to the user.
- Do not save broken empty entries.
- Log the error.
- Do not expose API keys or internal stack traces.

---

## 9. Backend API design

Use FastAPI with `/api/v1` prefix.

### Endpoints

Minimum endpoints:

```text
GET /api/v1/health
POST /api/v1/vocabulary
GET /api/v1/vocabulary
GET /api/v1/vocabulary/{entry_id}
PATCH /api/v1/vocabulary/{entry_id}
DELETE /api/v1/vocabulary/{entry_id}
```

### POST /vocabulary

Request:

```json
{
  "tg_user_id": 123456789,
  "text": "shallow"
}
```

Response:

```json
{
  "id": "uuid",
  "tg_user_id": 123456789,
  "original_text": "shallow",
  "translation_ru": "мелкий; поверхностный",
  "meaning_ru": "...",
  "examples": [...],
  "status": "new",
  "created_at": "..."
}
```

### GET /vocabulary

Query params:

```text
tg_user_id required
q optional
status optional
limit optional default 50
offset optional default 0
```

Must return only entries for the requested `tg_user_id`.

### PATCH /vocabulary/{entry_id}

V1 should support updating status only:

```json
{
  "status": "learning"
}
```

---

## 10. Telegram bot behavior

Use aiogram 3.x.

### Commands

- `/start`
- `/help`
- `/app`

### /start response

The bot should explain shortly:

- Send me an English word or phrase.
- I will explain it with Gemini and save it.
- Open the Mini App to view your vocabulary.

Add a button to open the Telegram Mini App using `WEBAPP_URL`.

### Text message behavior

When the user sends normal text:

1. Treat it as an English word/phrase/sentence.
2. Send it to backend service logic.
3. Gemini processes it.
4. Save to DB.
5. Return a clean Telegram message.

Example Telegram response:

```text
📌 shallow

🇷🇺 мелкий; поверхностный

Meaning:
Слово может описывать небольшую глубину или поверхностное отношение/мысль.

Examples:
1. The water is shallow near the shore.
   Вода мелкая возле берега.

2. That was a shallow explanation.
   Это было поверхностное объяснение.

Saved ✅
```

Do not show internal statuses, raw JSON, database IDs, or debug information to the user.

---

## 11. Frontend Mini App behavior

Frontend must be simple, clean, and mobile-first.

### Screens in V1

Single-page app is enough.

Required UI blocks:

1. Header
   - App name.
   - Short subtitle.
2. Add entry form
   - Text input.
   - Submit button.
3. Entries list
   - Saved vocabulary cards.
4. Search input
   - Optional but recommended.
5. Status controls
   - New / Learning / Learned.

### Telegram WebApp integration

Use Telegram WebApp SDK to read user data if available.

Frontend should get Telegram user ID from Telegram WebApp init data when running inside Telegram.

For local development, allow a fallback test user ID from environment or frontend constant, for example:

```ts
const DEV_TG_USER_ID = 123456789;
```

Do not make local development impossible if Telegram init data is missing.

### Design requirements

The UI should look like a small real product, not a raw test page.

Style direction:

- clean cards
- readable spacing
- mobile-first layout
- pleasant typography
- clear buttons
- no visual noise
- no huge framework required

---

## 12. Docker requirements

Create Docker Compose setup with services:

```text
db
backend
frontend
```

The backend service should run FastAPI and should also be able to run bot polling.

Preferred simple MVP approach:

- One backend Docker image.
- Backend container can run API.
- Bot can run as separate service using the same image but different command.

Example services:

```text
backend-api
backend-bot
db
frontend
```

This is better than running API and bot in one process.

### Docker Compose should include

- PostgreSQL volume.
- Proper env loading.
- Healthcheck for database if simple.
- Backend depends on db.
- Frontend depends on backend.

---

## 13. Alembic requirements

Set up Alembic properly.

Must support:

```bash
docker compose exec backend-api alembic revision --autogenerate -m "init"
docker compose exec backend-api alembic upgrade head
```

Migrations should be generated from SQLAlchemy models.

---

## 14. Code quality rules

Follow these rules strictly:

- Keep code readable.
- Use type hints in Python.
- Keep functions small.
- Avoid global mutable state.
- Keep settings in config module.
- Do not hardcode secrets.
- Do not expose internal errors to users.
- Do not mix Telegram bot logic with API routes.
- Do not put database queries inside route handlers directly.
- Use services/repositories separation.
- Keep frontend components small.
- Avoid overengineering.
- Do not add features outside MVP.

---

## 15. Implementation plan for AI agent

Follow this order.

### Step 1 — Create project skeleton

Create the full folder structure from this file.

Add empty but valid Python and frontend files.

### Step 2 — Add Docker Compose

Create:

- `docker-compose.yml`
- backend Dockerfile
- frontend Dockerfile
- `.env.example`
- `.gitignore`

Make sure containers can start.

### Step 3 — Backend config

Create settings loader from environment variables.

Build database URL from env variables.

### Step 4 — Database setup

Create:

- async SQLAlchemy engine
- session dependency
- base model
- vocabulary model
- Alembic config

### Step 5 — Vocabulary backend API

Create schemas, repository, service, and FastAPI routes.

Implement CRUD endpoints.

### Step 6 — Gemini service

Create Gemini service with structured JSON response.

Use `GEMINI_API_KEY` and `GEMINI_MODEL` from env.

Validate Gemini output before saving.

### Step 7 — Telegram bot

Create aiogram bot.

Implement `/start`, `/help`, `/app`, and text handling.

Add Mini App button.

### Step 8 — Frontend Mini App

Create React/Vite frontend.

Implement:

- add form
- vocabulary list
- status update
- delete
- loading states
- error states

### Step 9 — Project README

Create root README with:

- project description
- stack
- setup
- env
- Docker commands
- migrations
- development notes

### Step 10 — Final check

Check:

- Docker Compose syntax
- imports
- env variable names
- frontend API URL
- database migrations
- user ID filtering
- no OpenAI references
- no secrets committed

---

## 16. Expected final result

After implementation, the developer should be able to run:

```bash
cp .env.example .env
# fill TG_BOT_TOKEN and GEMINI_API_KEY

docker compose up --build
```

Then:

- FastAPI should be available on `http://localhost:8000`.
- Frontend should be available on `http://localhost:5173`.
- PostgreSQL should be available on host port `55432`.
- Telegram bot should respond to `/start` and text messages.
- Vocabulary entries should be saved in PostgreSQL.

---

## 17. Important warning for AI agents

Do not build a different product.

This is a Telegram English vocabulary notebook powered by Gemini AI.

Do not replace Gemini with OpenAI.
Do not replace PostgreSQL with SQLite.
Do not remove Docker.
Do not skip Telegram Mini App.
Do not create a huge enterprise architecture.
Do not add paid features.
Do not add unnecessary complexity.

Build the MVP cleanly and reliably first.
