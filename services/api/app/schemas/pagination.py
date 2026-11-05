"""Pagination par curseur commune à toutes les listes de l'API.

Le curseur est opaque pour le client : un JSON encodé en base64 URL-safe. Le client renvoie
tel quel le `next_cursor` reçu ; il ne doit ni le construire ni l'interpréter.
"""

import base64
import binascii
import json
from typing import Annotated, Any, Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

from app.core.errors import ProblemError

T = TypeVar("T")

MAX_CURSOR_LENGTH = 512


class PageParams(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    cursor: str | None = Field(default=None, max_length=MAX_CURSOR_LENGTH)


class Page(BaseModel, Generic[T]):  # noqa: UP046 - syntaxe PEP 695 pas encore généralisée
    items: list[T]
    next_cursor: str | None = None


def page_params(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    cursor: Annotated[str | None, Query(max_length=MAX_CURSOR_LENGTH)] = None,
) -> PageParams:
    """Dépendance FastAPI : `params: Annotated[PageParams, Depends(page_params)]`."""
    return PageParams(limit=limit, cursor=cursor)


def encode_cursor(position: dict[str, Any]) -> str:
    raw = json.dumps(position, separators=(",", ":"), sort_keys=True, default=str)
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def decode_cursor(cursor: str) -> dict[str, Any]:
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        position = json.loads(base64.urlsafe_b64decode(padded.encode()))
    except (binascii.Error, ValueError, UnicodeDecodeError) as exc:
        raise ProblemError(400, "invalid_cursor", "Le curseur de pagination est invalide.") from exc
    if not isinstance(position, dict):
        raise ProblemError(400, "invalid_cursor", "Le curseur de pagination est invalide.")
    return position
