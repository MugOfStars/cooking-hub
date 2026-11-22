# Cooking Hub

A personal cooking companion: save recipes (from websites or physical cookbooks),
log the dishes you've made with ratings and notes, and, eventually, get recipe ideas
based on flavor profiles and what's in your pantry.

> **Status:** early scaffolding. V1 target: December 2026.

## Features

- [ ] Save recipes from a URL (auto-imported), a cookbook (title + page), or manual entry
- [ ] Log cooks: date, 1–5 rating, notes, modifications, photo
- [ ] Recipe ideas from flavor profiles and pantry ingredients *(post-v1)*

## Tech stack

| Layer    | Choice                                              |
|----------|-----------------------------------------------------|
| Backend  | FastAPI, SQLAlchemy 2.0, Pydantic, Alembic          |
| Database | PostgreSQL 16 (Docker for local dev)                |
| Import   | [recipe-scrapers](https://github.com/hhursev/recipe-scrapers) |
| Frontend | React, Vite, TypeScript, TanStack Query             |
| Tooling  | uv, ruff, pytest, GitHub Actions                    |

## Architecture

```
browser ──► Vite dev server ──/api proxy──► FastAPI ──► PostgreSQL
            (localhost:5173)                (localhost:8000)  (Docker, :5432)
```

## Design decisions

- **SQLAlchemy 2.0 + Pydantic (not SQLModel).** ORM models describe the database and
  Pydantic schemas describe the API. Keeping them separate lets the API hide, rename or
  nest fields without touching tables.
- **Sync database access.** A single-user app gains nothing from async database calls,
  and sync code is simpler to write and test.
- **Constraints live in the database.** `source_type` and `rating` have CHECK
  constraints, so bad data is rejected even if API validation is bypassed. Text + CHECK
  is used instead of a Postgres ENUM because ENUMs are awkward to change in migrations.
- **Cook history is protected.** `cook_logs.recipe_id` is `ON DELETE RESTRICT`, so a
  recipe with logged cooks can't be deleted by accident.
- **Postgres-native types.** Ingredients and instructions are `JSONB`, tags are `TEXT[]`.
  Ingredients are stored as objects (`{"raw": "2 cups flour"}`) so parsed fields can
  be added later for pantry matching.
- **Vite proxy instead of CORS.** In development, `/api/*` is forwarded to FastAPI, so
  the browser only ever talks to one origin.
- **The health check touches the database.** `/api/health` runs `SELECT 1` and
  returns 503 if Postgres is unreachable, so it verifies the whole stack.

## Local development

### Prerequisites

- [Docker](https://www.docker.com/) (or [OrbStack](https://orbstack.dev/) on macOS)
- [uv](https://docs.astral.sh/uv/) (installs Python 3.14 automatically)
- Node.js 20+

### Setup

```bash
# 1. Config + database
cp .env.example .env
docker compose up -d              # Postgres on localhost:5432

# 2. Backend (http://localhost:8000, API docs at /docs)
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload

# 3. Frontend (http://localhost:5173), in a second terminal
cd frontend
npm install
npm run dev
```

The page should show **API: ok / DB: ok**.

### Common tasks

```bash
# Backend (run inside backend/)
uv run pytest                                    # tests (needs Postgres running)
uv run ruff check . && uv run ruff format .      # lint + format
uv run alembic revision --autogenerate -m "..."  # new migration after model changes

# Database
docker compose down       # stop Postgres (data is kept in a named volume)
docker compose down -v    # stop and delete all local data
```

### Production image

In production, one container serves both the API and the built React app, so the
browser still talks to a single origin. To build and run it locally against the
compose Postgres:

```bash
docker build -t cooking-hub .
docker run --rm -p 8000:8000 \
  -e DATABASE_URL=postgresql+psycopg://cooking_hub:change-me-locally@host.docker.internal:5432/cooking_hub \
  cooking-hub
# open http://localhost:8000
```

## Project layout

```
backend/
  app/          FastAPI app: config, database session, ORM models
  migrations/   Alembic migrations
  tests/        pytest suite
frontend/       React + Vite app
docker-compose.yml   Local PostgreSQL
.github/workflows/   CI: ruff, migrations, pytest against a Postgres service
```

## Data

All recipes in this repo (fixtures, tests, screenshots) are made-up demo data.

## License

[MIT](LICENSE)
