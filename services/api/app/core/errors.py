"""Réponses d'erreur au format RFC 9457 (`application/problem+json`).

Toutes les erreurs de l'API ont la même forme, quelle que soit leur origine :

    {"type": "...", "title": "...", "status": 404, "detail": "...", "instance": "/chemin",
     "request_id": "..."}
"""

from http import HTTPStatus
from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.middleware import REQUEST_ID_HEADER

PROBLEM_JSON = "application/problem+json"
PROBLEM_TYPE_BASE = "https://foodanalyser.app/problems/"

logger = structlog.get_logger("app.errors")


class ProblemError(Exception):
    """Erreur métier levée par le code applicatif.

    `code` identifie le problème de façon stable (ex. `free_quota_exceeded`) : le mobile
    s'appuie dessus, jamais sur le texte de `detail`.
    """

    def __init__(
        self,
        status: int,
        code: str,
        detail: str | None = None,
        *,
        extensions: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(detail or code)
        self.status = status
        self.code = code
        self.detail = detail
        self.extensions = extensions or {}


def problem_response(
    request: Request,
    status: int,
    *,
    code: str | None = None,
    detail: str | None = None,
    extensions: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    request_id: str | None = getattr(request.state, "request_id", None)
    body: dict[str, Any] = {
        "type": f"{PROBLEM_TYPE_BASE}{code}" if code else "about:blank",
        "title": HTTPStatus(status).phrase,
        "status": status,
        "instance": request.url.path,
    }
    if detail:
        body["detail"] = detail
    if request_id:
        body["request_id"] = request_id
    body.update(extensions or {})

    response_headers = dict(headers or {})
    if request_id:
        response_headers[REQUEST_ID_HEADER] = request_id
    return JSONResponse(
        jsonable_encoder(body),
        status_code=status,
        headers=response_headers,
        media_type=PROBLEM_JSON,
    )


async def _problem_error_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, ProblemError):  # garanti par l'enregistrement
        raise exc
    return problem_response(
        request, exc.status, code=exc.code, detail=exc.detail, extensions=exc.extensions
    )


async def _http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, StarletteHTTPException):  # garanti par l'enregistrement
        raise exc
    detail: str | None = exc.detail if isinstance(exc.detail, str) else None
    # « Not Found » répété dans `detail` n'apporte rien : on ne garde qu'un détail spécifique.
    if detail == HTTPStatus(exc.status_code).phrase:
        detail = None
    headers = dict(exc.headers) if exc.headers else None
    return problem_response(request, exc.status_code, detail=detail, headers=headers)


async def _validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, RequestValidationError):  # garanti par l'enregistrement
        raise exc
    # On ne renvoie pas la valeur saisie (`input`) : elle peut contenir une donnée personnelle.
    errors = [
        {"loc": list(err.get("loc", ())), "msg": err.get("msg", ""), "type": err.get("type", "")}
        for err in exc.errors()
    ]
    return problem_response(
        request,
        422,
        code="validation_error",
        detail="La requête contient des champs invalides.",
        extensions={"errors": errors},
    )


async def _unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    # Le détail technique va dans les logs, jamais dans la réponse.
    logger.exception("unhandled_error", path=request.url.path, error_type=type(exc).__name__)
    return problem_response(request, 500, code="internal_error")


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ProblemError, _problem_error_handler)
    app.add_exception_handler(StarletteHTTPException, _http_exception_handler)
    app.add_exception_handler(RequestValidationError, _validation_error_handler)
    app.add_exception_handler(Exception, _unhandled_error_handler)
