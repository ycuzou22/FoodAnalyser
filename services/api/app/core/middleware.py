"""Middleware ASGI : identifiant de requête et ligne de log d'accès."""

import re
import time
import uuid

import structlog
from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUEST_ID_HEADER = "X-Request-ID"

# Un identifiant fourni par le client n'est repris que s'il est « propre » : on évite
# ainsi l'injection de contenu arbitraire (retours à la ligne, JSON) dans les logs.
_SAFE_REQUEST_ID = re.compile(r"[A-Za-z0-9._-]{8,64}")


def _resolve_request_id(scope: Scope) -> str:
    incoming = Headers(scope=scope).get(REQUEST_ID_HEADER)
    if incoming and _SAFE_REQUEST_ID.fullmatch(incoming):
        return incoming
    return uuid.uuid4().hex


class RequestContextMiddleware:
    """Attribue un `X-Request-ID` à chaque requête, le renvoie et l'ajoute à tous les logs.

    Écrit en ASGI pur (et non `BaseHTTPMiddleware`) pour ne pas bufferiser les réponses.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = _resolve_request_id(scope)
        # `scope["state"]` est l'objet lu par `request.state` : le gestionnaire d'erreurs 500,
        # placé plus haut dans la pile, y retrouve l'identifiant.
        scope.setdefault("state", {})["request_id"] = request_id
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        status_code = 500
        start = time.perf_counter()

        async def send_with_request_id(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                MutableHeaders(scope=message)[REQUEST_ID_HEADER] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        finally:
            # Le chemin seul, sans la chaîne de requête : elle peut contenir des données saisies.
            # Logger obtenu à chaque requête : un proxy global resterait figé sur la configuration
            # en vigueur lors de son premier usage.
            structlog.get_logger("app.access").info(
                "request",
                method=scope["method"],
                path=scope["path"],
                status=status_code,
                duration_ms=round((time.perf_counter() - start) * 1000, 2),
            )
