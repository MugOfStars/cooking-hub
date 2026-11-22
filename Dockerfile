# Production image: one container serves both the API and the built React app.
# Build from the repo root:  docker build -t cooking-hub .

# --- Stage 1: build the frontend. Node exists only in this stage. ---
FROM node:24-alpine AS frontend
WORKDIR /app/frontend
# Copy the manifests first so `npm ci` is cached until dependencies actually change.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Stage 2: the runtime image. Python plus the built static files, no Node. ---
FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1

WORKDIR /app/backend
# Same caching trick: install dependencies before copying the source code.
COPY backend/pyproject.toml backend/uv.lock backend/.python-version ./
RUN uv sync --locked --no-dev
COPY backend/ ./
# Same relative layout as the repo, so app/frontend.py finds ../frontend/dist.
COPY --from=frontend /app/frontend/dist /app/frontend/dist

# Don't run as root: limits the damage if the app were ever compromised.
RUN useradd --no-create-home app
USER app

ENV PATH="/app/backend/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
