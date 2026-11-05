from decimal import Decimal

import pytest

from app.importers.parsing import (
    clean_text,
    is_valid_gtin,
    kcal_from_kj,
    normalize_header,
    parse_decimal,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("12,5", Decimal("12.5")),
        ("12.5", Decimal("12.5")),
        (" 3 ", Decimal(3)),
        (7, Decimal(7)),
        (0.25, Decimal("0.25")),
        ("traces", Decimal(0)),
        ("Traces", Decimal(0)),
        ("< 0,5", Decimal("0.25")),
        ("<0.01", Decimal("0.005")),
        ("1 234", Decimal(1234)),
        ("-", None),
        ("", None),
        ("ND", None),
        (None, None),
        ("abc", None),
        ("nan", None),
        ("inf", None),
    ],
)
def test_parse_decimal(raw: object, expected: Decimal | None) -> None:
    assert parse_decimal(raw) == expected


def test_kcal_from_kj() -> None:
    assert kcal_from_kj(Decimal(2252)) == Decimal("538.24")
    assert kcal_from_kj(None) is None


@pytest.mark.parametrize(
    ("code", "valid"),
    [
        ("3017620422003", True),  # EAN-13
        ("50000005", True),  # EAN-8
        ("3000000000014", True),
        ("3017620422004", False),  # mauvaise clé
        ("301762042200", False),  # UPC-A à clé fausse
        ("30176204220a3", False),
        ("123", False),
        ("", False),
    ],
)
def test_is_valid_gtin(code: str, valid: bool) -> None:
    assert is_valid_gtin(code) is valid


def test_clean_text_removes_control_characters_and_truncates() -> None:
    assert clean_text("  Pâte\u0000  à\n tartiner\t ", 255) == "Pâte à tartiner"
    assert clean_text("x" * 300, 255) == "x" * 255
    assert clean_text("   ", 255) is None
    assert clean_text(None, 255) is None


def test_normalize_header() -> None:
    assert normalize_header("Protéines, N x facteur de Jones (g/100 g)") == (
        "proteines, n x facteur de jones (g/100 g)"
    )
