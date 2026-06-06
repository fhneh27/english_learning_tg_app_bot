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
---

## 16. Frontend UX and Animation Rules

The frontend is an important part of the portfolio value of this project.

The goal is not only functionality but also a polished user experience.

### Design philosophy

The application should feel:

* modern
* premium
* smooth
* mobile-first
* visually polished
* comfortable to use
* portfolio-quality

Avoid generic "student project" UI.

### GSAP

Use GSAP for advanced animations.

Preferred packages:

```bash
gsap
@gsap/react
```

For React applications:

* prefer `useGSAP()`
* clean up animations properly
* use reusable animation helpers where appropriate

### Animation principles

Animations must improve UX.

Good uses:

* page transitions
* screen enter animations
* modal open/close transitions
* bottom navigation transitions
* active tab indicators
* card appearance animations
* staggered list animations
* success state animations
* progress animations
* loading state animations
* micro-interactions for buttons

Avoid:

* excessive animation
* distracting effects
* long delays
* heavy animations on every element
* animations that reduce performance

### Performance

Telegram Mini Apps must remain responsive.

Prefer animating:

* opacity
* transform
* translate
* scale
* rotation

Avoid animating layout-heavy properties when possible.

### UX Improvements

When improving frontend:

1. Analyze the current UI first.
2. Improve the existing interface before creating new components.
3. Keep navigation intuitive.
4. Improve spacing and hierarchy.
5. Improve visual feedback.
6. Improve loading states.
7. Improve empty states.
8. Improve success/error states.
9. Keep mobile usability as a priority.

### Working Process

Before implementing frontend changes:

1. Inspect the current frontend structure.
2. Identify UX problems.
3. Create a short improvement plan.
4. Implement improvements incrementally.
5. Explain what was changed.

The goal is to make the application feel like a production-quality product rather than a basic MVP.
