# Telegram English Vocabulary Mini App

Telegram English Vocabulary Mini App is an MVP vocabulary notebook for Russian-speaking learners. A user can send an English word or phrase to a Telegram bot or enter it through a Telegram Mini App, get a structured OpenAI explanation, and save the result to PostgreSQL for later review.

## Stack

- FastAPI for the backend API
- aiogram for the Telegram bot
- PostgreSQL with SQLAlchemy 2.x async and Alembic
- OpenAI API for vocabulary analysis
- React + Vite + TypeScript for the Telegram Mini App
- Docker Compose for local development

## Project Structure

```text
backend/
  app/
    api/
    bot/
    core/
    db/
    models/
    repositories/
    schemas/
    services/
  alembic/
frontend/
  src/
docker-compose.yml
.env.example
README.md
```

## MVP Features

- Telegram bot commands: `/start`, `/help`, `/app`
- Add vocabulary from bot messages
- Add vocabulary from the Mini App
- Save entries by `tg_user_id`
- Search entries by English text or Russian meaning
- Update entry status: `new`, `learning`, `learned`
- Delete entries
- PostgreSQL persistence through Docker
- Alembic migrations

## Environment Variables

1. Copy the example file:

```bash
cp .env.example .env
```

1. Fill in:

- `TG_BOT_TOKEN`
- `OPENAI_API_KEY`

The default OpenAI model is controlled only through `.env`:

```env
OPENAI_MODEL=gpt-4o-mini
```

## Run With Docker Compose

```bash
docker compose up --build
```

Services after startup:

- API: [http://localhost:8000](http://localhost:8000)
- Frontend: [http://localhost:5173](http://localhost:5173)
- PostgreSQL host port: `55432`

## Migrations

Apply migrations:

```bash
docker compose exec backend-api alembic upgrade head
```

Create a new migration later:

```bash
docker compose exec backend-api alembic revision --autogenerate -m "describe change"
```

## API Overview

Base prefix: `/api/v1`

- `GET /api/v1/health`
- `POST /api/v1/vocabulary`
- `GET /api/v1/vocabulary`
- `GET /api/v1/vocabulary/{entry_id}?tg_user_id=...`
- `PATCH /api/v1/vocabulary/{entry_id}?tg_user_id=...`
- `DELETE /api/v1/vocabulary/{entry_id}?tg_user_id=...`

Example create request:

```json
{
  "tg_user_id": 123456789,
  "text": "shallow"
}
```

Example list query:

```text
/api/v1/vocabulary?tg_user_id=123456789&q=shallow&status=new
```

## Bot Notes

- `/start` explains the flow and shows a Mini App button.
- Regular text messages are treated as English vocabulary input.
- The bot uses the same backend service layer as the API, so vocabulary is saved consistently.

## Frontend Notes

- The Mini App reads `window.Telegram.WebApp.initDataUnsafe.user.id` when available.
- Local development falls back to `123456789` when Telegram init data is missing.
- The frontend uses `VITE_API_URL` and proxies API requests through Vite in Docker.

## Development Notes

- Docker Compose is the primary way to run the project.
- PostgreSQL credentials are built into the SQLAlchemy URL from environment variables.
- OpenAI is the only AI provider used in this repository.
- No real secrets should be committed. `.env` is ignored by Git.

## Basic Run Instructions

1. Copy `.env.example` to `.env`.
1. Add your Telegram bot token and OpenAI API key.
1. Start the stack with `docker compose up --build`.
1. Apply the migration with `docker compose exec backend-api alembic upgrade head`.
1. Open the Mini App locally at [http://localhost:5173](http://localhost:5173).
1. Set your Telegram bot Mini App URL to the `WEBAPP_URL` value from `.env`.
