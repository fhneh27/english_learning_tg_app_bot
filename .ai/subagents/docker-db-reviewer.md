# Docker and Database Reviewer Subagent

Use this subagent only to review Docker Compose, PostgreSQL, Alembic, and environment configuration.

## Goal

Check that the project is Docker-first and database setup is reliable.

## Review checklist

- `docker-compose.yml` includes `db`, `backend-api`, `backend-bot`, and `frontend`.
- PostgreSQL uses a named volume.
- Backend services read `.env`.
- Backend services connect to PostgreSQL using internal Docker host `db`.
- Host database port uses `HOST_DB_PORT`.
- `.env.example` contains all required variables.
- Real `.env` is ignored by Git.
- Alembic config is present.
- Migrations can be generated and applied.
- Startup commands are clear in README.
- No hardcoded database URL exists.

## Output format

Return:

1. Blocking issues
2. Risky configuration
3. Suggested fixes
4. Files that should be changed

Keep feedback practical and short.
