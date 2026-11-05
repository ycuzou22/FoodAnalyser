import pytest

from app.core.errors import ProblemError
from app.schemas.pagination import Page, PageParams, decode_cursor, encode_cursor


def test_cursor_round_trip() -> None:
    position = {
        "eaten_at": "2026-11-05T12:30:00+00:00",
        "id": "0193a1b2-0000-7000-8000-000000000001",
    }

    assert decode_cursor(encode_cursor(position)) == position


@pytest.mark.parametrize("cursor", ["not base64 !!", "WzEsMiwzXQ", ""])
def test_invalid_cursor_raises_problem(cursor: str) -> None:
    with pytest.raises(ProblemError) as excinfo:
        decode_cursor(cursor)

    assert excinfo.value.status == 400
    assert excinfo.value.code == "invalid_cursor"


def test_page_params_bounds() -> None:
    assert PageParams().limit == 20
    with pytest.raises(ValueError, match="less than or equal to 100"):
        PageParams(limit=101)


def test_page_serialisation() -> None:
    page = Page[int](items=[1, 2], next_cursor="abc")

    assert page.model_dump() == {"items": [1, 2], "next_cursor": "abc"}
