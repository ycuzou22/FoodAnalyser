import asyncio

from fastapi import FastAPI
from httpx import AsyncClient


async def test_health_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_ready_when_all_dependencies_answer(client: AsyncClient) -> None:
    response = await client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {"database": "ok", "redis": "ok", "rabbitmq": "ok"},
    }


async def test_ready_returns_503_when_database_is_down(app: FastAPI, client: AsyncClient) -> None:
    async def database_down() -> None:
        raise ConnectionRefusedError("connect to 10.0.0.12:5432 failed, password=secret")

    app.state.readiness_checks["database"] = database_down

    response = await client.get("/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "unavailable"
    assert body["checks"]["database"] == "failed"
    assert body["checks"]["redis"] == "ok"
    # Aucun détail technique (hôte, mot de passe) ne fuit dans la réponse.
    assert "10.0.0.12" not in response.text
    assert "secret" not in response.text


async def test_ready_times_out_a_hanging_dependency(app: FastAPI, client: AsyncClient) -> None:
    async def hangs() -> None:
        await asyncio.sleep(10)

    app.state.readiness_checks["rabbitmq"] = hangs

    response = await client.get("/ready")

    assert response.status_code == 503
    assert response.json()["checks"]["rabbitmq"] == "failed"
