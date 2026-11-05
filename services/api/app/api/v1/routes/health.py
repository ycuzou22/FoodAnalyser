"""Sondes de vie et de disponibilité (Kubernetes, Docker Compose, supervision)."""

from typing import Literal

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

from app.core.readiness import run_checks

router = APIRouter(tags=["santé"])


class HealthResponse(BaseModel):
    status: Literal["ok"]


class ReadinessResponse(BaseModel):
    status: Literal["ready", "unavailable"]
    checks: dict[str, Literal["ok", "failed"]]


@router.get("/health", summary="Sonde de vie")
async def health() -> HealthResponse:
    """Répond tant que le processus tourne. Ne touche à aucune dépendance."""
    return HealthResponse(status="ok")


@router.get(
    "/ready",
    summary="Sonde de disponibilité",
    responses={503: {"model": ReadinessResponse, "description": "Une dépendance est indisponible"}},
)
async def ready(request: Request, response: Response) -> ReadinessResponse:
    """Vérifie PostgreSQL, Redis et RabbitMQ. 503 si l'un d'eux ne répond pas."""
    results = await run_checks(
        request.app.state.readiness_checks,
        per_check_seconds=request.app.state.settings.readiness_timeout_seconds,
    )
    all_ok = all(results.values())
    if not all_ok:
        response.status_code = 503
    return ReadinessResponse(
        status="ready" if all_ok else "unavailable",
        checks={name: "ok" if ok else "failed" for name, ok in results.items()},
    )
