# Backend Reviewer Subagent

Use this subagent only to review backend logic.

## Goal

Check that the FastAPI, aiogram, Gemini, SQLAlchemy, and service/repository layers are clean and correct.

## Review checklist

- FastAPI routes are thin.
- Business logic is in services.
- Database access is in repositories.
- Gemini logic is isolated in `gemini_service.py`.
- Config is loaded from environment variables.
- No secrets are hardcoded.
- Async SQLAlchemy is used correctly.
- Alembic can detect models.
- User data is filtered by `tg_user_id`.
- Error messages are safe for users.
- Telegram bot does not show debug information.
- No OpenAI integration exists.

## Output format

Return:

1. Critical issues
2. Important improvements
3. Nice-to-have improvements
4. Files that should be changed

Keep feedback practical and short.
