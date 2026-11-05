from collections.abc import Callable

import pytest
from fastapi.middleware.cors import CORSMiddleware
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from app.core.config import Settings
from app.main import create_app


async def test_docs_are_disabled_in_production(make_settings: Callable[..., Settings]) -> None:
    app = create_app(
        make_settings(env="production", cors_origins=["https://admin.foodanalyser.app"])
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        assert (await client.get("/docs")).status_code == 404
        assert (await client.get("/openapi.json")).status_code == 404


async def test_docs_are_enabled_outside_production(client: AsyncClient) -> None:
    assert (await client.get("/openapi.json")).status_code == 200


def test_wildcard_cors_is_rejected_in_production(make_settings: Callable[..., Settings]) -> None:
    with pytest.raises(ValidationError, match="ne peut pas contenir"):
        make_settings(env="production", cors_origins=["*"])


def test_connection_urls_are_never_printed(make_settings: Callable[..., Settings]) -> None:
    settings = make_settings(database_url="postgresql+asyncpg://u:hunter2@db:5432/x")

    assert "hunter2" not in repr(settings)
    assert "hunter2" not in str(settings.model_dump())


def test_cors_origins_are_restricted_to_configuration(
    make_settings: Callable[..., Settings],
) -> None:
    app = create_app(make_settings(cors_origins=["http://localhost:5173"]))

    cors = next(m for m in app.user_middleware if m.cls is CORSMiddleware)
    assert cors.kwargs["allow_origins"] == ["http://localhost:5173"]


async def test_cors_rejects_unknown_origin(make_settings: Callable[..., Settings]) -> None:
    app = create_app(make_settings(cors_origins=["http://localhost:5173"]))
    headers = {"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.options("/health", headers=headers)

    assert "access-control-allow-origin" not in response.headers
