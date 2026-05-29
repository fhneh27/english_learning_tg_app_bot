# Деплой на Railway (пошагово)

Проект: API + Telegram-бот + PostgreSQL + фронт (Mini App).

## Сейчас на экране (один сервис из GitHub)

**Не жмите Deploy**, пока не сделаете шаги 1–4.

### 1. Переименуйте сервис

Сервис `english_learning_tg_app_bot` — это **API**, не бот.

- Откройте сервис → **Settings** → имя, например: `api`

### 2. PostgreSQL

1. На канвасе проекта: **+ Create** → **Database** → **PostgreSQL**
2. Дождитесь статуса **Active**

### 3. Переменные API (вкладка Variables)

**Raw Editor** — вставьте и подставьте секреты (`TG_BOT_TOKEN`, `OPENAI_API_KEY`):

```env
POSTGRES_USER=${{Postgres.PGUSER}}
POSTGRES_PASSWORD=${{Postgres.PGPASSWORD}}
POSTGRES_DB=${{Postgres.PGDATABASE}}
POSTGRES_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
HOST_DB_PORT=5432

TG_BOT_TOKEN=ВАШ_ТОКЕН
OPENAI_API_KEY=ВАШ_КЛЮЧ
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT_SECONDS=30

BACKEND_HOST=0.0.0.0
BACKEND_PORT=${{PORT}}
BACKEND_RELOAD=false
API_V1_PREFIX=/api/v1

APP_ENV=production
LOG_LEVEL=INFO
DEFAULT_UI_LANGUAGE=ru
DEFAULT_LEARNING_LANGUAGE=en
DEFAULT_TRANSLATION_LANGUAGE=ru

WEBAPP_URL=https://ЗАМЕНИТЕ-ПОСЛЕ-ФРОНТА.railway.app
CORS_ORIGINS=https://ЗАМЕНИТЕ-ПОСЛЕ-ФРОНТА.railway.app

FRONTEND_PORT=5173
VITE_API_URL=/api/v1
```

`Postgres` в `${{Postgres.*}}` — **имя вашей БД-сервиса** на канвасе (если другое — выберите из списка Variables → Reference).

### 4. Домен API

**Settings** → **Networking** → **Generate Domain**

Проверка после деплоя: `https://ВАШ-API.railway.app/api/v1/health`

### 5. Deploy API

Вверху: **Apply changes** → **Deploy**.

Миграции запускаются автоматически (`preDeployCommand` в `railway.toml`).

---

## Бот (второй сервис)

1. **+ Create** → **GitHub Repo** → тот же `english_learning_tg_app_bot`
2. Имя: `bot`
3. **Settings** → **Config-as-code** → **railway.bot.toml**
4. **Variables** — скопируйте с сервиса `api` (Reference → Duplicate)
5. **Deploy** (публичный домен боту не нужен)

---

## Фронт (третий сервис)

1. **+ Create** → **GitHub Repo** → тот же репозиторий
2. Имя: `frontend`
3. **Config-as-code** → **railway.frontend.toml**
4. **Variables**:

```env
VITE_API_URL=https://ВАШ-API.railway.app/api/v1
```

5. **Networking** → **Generate Domain** → URL фронта
6. В сервисе **api** обновите:

```env
WEBAPP_URL=https://ВАШ-ФРОНТ.railway.app
CORS_ORIGINS=https://ВАШ-ФРОНТ.railway.app
```

7. Redeploy `api` и `bot`
8. [@BotFather](https://t.me/BotFather) → Web App URL = `WEBAPP_URL`

---

## Порядок сервисов на канвасе

```text
PostgreSQL ──► api ──► frontend
                 └──► bot
```

## Если билд падает

- **Settings** → **Build** → Dockerfile path: `backend/Dockerfile`
- **Deploy** → Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Логи: вкладка **Deployments** → последний деплой
