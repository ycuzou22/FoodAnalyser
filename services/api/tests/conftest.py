import os
from collections.abc import AsyncIterator, Callable

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

# Valeurs factices : aucune connexion réelle n'est ouverte par les tests unitaires.
os.environ.setdefault("API_ENV", "test")
os.environ.setdefault("API_DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("API_REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("API_RABBITMQ_URL", "amqp://test:test@localhost:5672/")

from app.core.config import Settings  # noqa: E402
from app.core.readiness import ReadinessCheck  # noqa: E402
from app.main import create_app  # noqa: E402


async def _ok() -> None:
    return None


@pytest.fixture
def make_settings() -> Callable[..., Settings]:
    def factory(**overrides: object) -> Settings:
        values: dict[str, object] = {
            "env": "test",
            "database_url": "postgresql+asyncpg://test:test@localhost:5432/test",
            "redis_url": "redis://localhost:6379/0",
            "rabbitmq_url": "amqp://test:test@localhost:5672/",
            "readiness_timeout_seconds": 0.2,
        }
        values.update(overrides)
        return Settings.model_validate(values)

    return factory


@pytest.fixture
def app(make_settings: Callable[..., Settings]) -> FastAPI:
    """Application sans lifespan : les dépendances externes sont remplacées par des fakes."""
    application = create_app(make_settings())
    checks: dict[str, ReadinessCheck] = {"database": _ok, "redis": _ok, "rabbitmq": _ok}
    application.state.readiness_checks = checks
    return application


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client
