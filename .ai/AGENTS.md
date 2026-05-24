# AGENTS.md — Instructions for AI Coding Agents

This file defines how AI agents must work on this project.

The project is a Telegram English Vocabulary AI App. It uses Telegram Bot + Telegram Mini App + FastAPI + PostgreSQL + Gemini AI + Docker Compose.

Agents must read this file before editing code.

---

## 1. Main rule

Build exactly the MVP described in `.ai/README.md`.

Do not invent a different architecture.
Do not add future features unless they are explicitly marked as TODO.
Do not replace the required stack.

---

## 2. Required stack

Use:

- Python 3.11+
- FastAPI
- aiogram 3.x
- SQLAlchemy 2.x async
- Alembic
- PostgreSQL
- React
- Vite
- TypeScript
- Docker Compose
- Gemini API

Do not use:

- OpenAI API
- SQLite as main database
- MongoDB
- Firebase
- Django
- Next.js
- unnecessary UI frameworks
- unnecessary queues or microservices

---

## 3. Project quality target

This project is intended for GitHub portfolio use.

Code must be:

- readable
- structured
- typed where practical
- easy to run locally
- Docker-first
- not overcomplicated
- safe with secrets
- clear for a junior developer to understand

Avoid clever code. Prefer simple reliable code.

---

## 4. Development behavior

When working on the project:

1. Read `.ai/README.md` first.
2. Check existing files before creating new ones.
3. Preserve the requested architecture.
4. Make small logical changes.
5. Explain major changes briefly after each major step.
6. Do not rewrite unrelated files.
7. Do not hide errors.
8. Do not leave broken imports.
9. Do not commit real secrets.
10. Keep `.env.example` updated when adding env variables.

---

## 5. Backend rules

Backend code should be organized by responsibility:

- `api/` for FastAPI routes
- `schemas/` for Pydantic schemas
- `models/` for SQLAlchemy models
- `repositories/` for database access
- `services/` for business logic
- `bot/` for Telegram bot code
- `core/` for config
- `db/` for database session/base

Do not put all logic in `main.py`.
Do not put SQL queries directly inside route handlers.
Do not put Gemini API calls inside route handlers.

Correct flow:

```text
Route / Bot Handler
  -> service
  -> repository / Gemini service
  -> database
```

---

## 6. Gemini AI rules

Gemini is the only AI provider in this project.

The Gemini service must:

- read API key from `GEMINI_API_KEY`
- read model from `GEMINI_MODEL`
- return structured data
- validate data before saving
- handle errors clearly

Do not hardcode the model in many places.
Use config.

Do not expose raw Gemini errors to Telegram users.

---

## 7. Database rules

Use PostgreSQL through Docker Compose.

Use async SQLAlchemy.
Use Alembic migrations.

Every vocabulary entry must include `tg_user_id`.
Every list/read/update/delete operation must check `tg_user_id` where relevant.

Never return another user’s vocabulary entries.

---

## 8. Telegram bot rules

Bot must be friendly and simple.

Do not show:

- internal statuses
- stack traces
- raw JSON
- database IDs
- debug logs

User-facing output should be clean and short.

Bot commands:

- `/start`
- `/help`
- `/app`

For normal text messages, treat text as an English word/phrase and process it.

---

## 9. Frontend rules

Frontend must be mobile-first because Telegram Mini Apps are usually opened on phones.

Keep UI simple:

- one page is enough
- add input
- saved entries list
- search
- status buttons
- delete button

Do not create a complex dashboard.
Do not add routing unless needed.

Frontend must work locally even without Telegram init data by using a safe development fallback user ID.

---

## 10. Docker rules

Docker must be the main way to run the project.

Expected command:

```bash
docker compose up --build
```

Recommended services:

- `db`
- `backend-api`
- `backend-bot`
- `frontend`

Backend API and bot may use the same Docker image with different commands.

---

## 11. Environment rules

Use `.env.example` as the source of truth for required env variables.

Never commit real `.env`.

When adding any new configuration variable:

1. Add it to config code.
2. Add it to `.env.example`.
3. Mention it in README if important.

---

## 12. Testing and checking

Before saying the task is complete, check:

- Docker Compose can parse.
- Python imports are valid.
- FastAPI app starts.
- Bot imports are valid.
- Frontend builds.
- Alembic migration setup is present.
- `.env.example` contains all required variables.
- No OpenAI references exist.
- No real secrets exist.

---

## 13. Subagent usage

Use subagents only when helpful.

This project should not waste too many AI limits. Prefer only these lightweight review roles:

- backend reviewer
- frontend reviewer
- docker/db reviewer

Do not create many subagents.
Do not run subagents repeatedly for tiny changes.

---

## 14. Definition of done for MVP

The MVP is done when:

1. User can run the project with Docker Compose.
2. Bot responds to `/start`.
3. User can send an English word to the bot.
4. Gemini returns a structured explanation.
5. Entry is saved to PostgreSQL.
6. Mini App can show saved entries.
7. User can add entries from Mini App.
8. User can search entries.
9. User can update status.
10. User can delete entries.
11. Root README explains setup clearly.

---

## 15. Final instruction

Prioritize a working clean MVP over a big unfinished system.

Make the project understandable, stable, and easy to continue.
