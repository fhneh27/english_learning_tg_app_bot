# How to use this AI folder

Copy `.ai/` and `.env.example` into the root of your project.

Then tell your coding agent:

```text
Read .ai/README.md and .ai/AGENTS.md first.
Build the project exactly according to those files.
Do not invent a different architecture.
Use Docker Compose, PostgreSQL, FastAPI, aiogram, React/Vite, and Gemini API only.
Start with the full project structure and .env.example.
```

Use subagents only for review when needed:

- `.ai/subagents/backend-reviewer.md`
- `.ai/subagents/frontend-reviewer.md`
- `.ai/subagents/docker-db-reviewer.md`
