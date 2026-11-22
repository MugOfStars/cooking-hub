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

<!-- TODO: design decisions section -->

## Local development

### Prerequisites

- [Docker](https://www.docker.com/) (or [OrbStack](https://orbstack.dev/) on macOS)
- [uv](https://docs.astral.sh/uv/) (installs Python 3.12 automatically)
- Node.js 20+

### Setup

<!-- TODO: filled in as each piece lands -->

```bash
cp .env.example .env
docker compose up -d
```

## Project layout

```
backend/    FastAPI app, models, Alembic migrations, tests
frontend/   React + Vite app
docker-compose.yml   Local PostgreSQL
```

## Data

All recipes in this repo (fixtures, tests, screenshots) are made-up demo data.

## License

[MIT](LICENSE)
