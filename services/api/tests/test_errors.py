from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import BaseModel

from app.core.errors import PROBLEM_JSON, ProblemError


class _Payload(BaseModel):
    weight_kg: float


def _add_test_routes(app: FastAPI) -> None:
    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("database password=hunter2 leaked in a stack trace")

    @app.get("/quota")
    async def quota() -> None:
        raise ProblemError(
            402, "free_quota_exceeded", "Quota gratuit atteint.", extensions={"limit": 3}
        )

    @app.post("/validate")
    async def validate(payload: _Payload) -> _Payload:
        return payload


async def test_unknown_route_returns_problem_json(client: AsyncClient) -> None:
    response = await client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.headers["content-type"] == PROBLEM_JSON
    body = response.json()
    assert body["type"] == "about:blank"
    assert body["title"] == "Not Found"
    assert body["status"] == 404
    assert body["instance"] == "/does-not-exist"
    assert body["request_id"] == response.headers["x-request-id"]


async def test_problem_error_exposes_stable_code(app: FastAPI, client: AsyncClient) -> None:
    _add_test_routes(app)

    response = await client.get("/quota")

    assert response.status_code == 402
    body = response.json()
    assert body["type"] == "https://foodanalyser.app/problems/free_quota_exceeded"
    assert body["detail"] == "Quota gratuit atteint."
    assert body["limit"] == 3


async def test_validation_error_does_not_echo_input(app: FastAPI, client: AsyncClient) -> None:
    _add_test_routes(app)

    response = await client.post("/validate", json={"weight_kg": "soixante-douze kilos"})

    assert response.status_code == 422
    assert response.headers["content-type"] == PROBLEM_JSON
    body = response.json()
    assert body["type"].endswith("/validation_error")
    assert body["errors"][0]["loc"] == ["body", "weight_kg"]
    assert "soixante-douze" not in response.text


async def test_unhandled_error_returns_500_without_details(
    app: FastAPI, client: AsyncClient
) -> None:
    _add_test_routes(app)

    response = await client.get("/boom", headers={"X-Request-ID": "trace-500-abcdef"})

    assert response.status_code == 500
    assert response.headers["content-type"] == PROBLEM_JSON
    assert response.headers["x-request-id"] == "trace-500-abcdef"
    body = response.json()
    assert body["type"].endswith("/internal_error")
    assert body["request_id"] == "trace-500-abcdef"
    assert "hunter2" not in response.text
    assert "RuntimeError" not in response.text
