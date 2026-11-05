# syntax=docker/dockerfile:1.7
# Image de l'API FoodAnalyser.
#   target dev     : dépendances de dev, rechargement à chaud (docker compose)
#   target runtime : image de production minimale, utilisateur non-root

ARG PYTHON_VERSION=3.12

# ---------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH=/opt/venv/bin:$PATH
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /usr/local/bin/uv
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app
WORKDIR /app

# ---------------------------------------------------------------------------
FROM base AS builder
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# ---------------------------------------------------------------------------
FROM base AS dev
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project
# Le code est monté par le Compose ; cette copie sert si l'image est lancée seule.
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "app"]

# ---------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/opt/venv/bin:$PATH
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
# Code possédé par root et lisible seulement : le processus (utilisateur app) ne peut pas le modifier.
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./
USER app
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--no-server-header"]
