"""Lecture des valeurs brutes des fichiers sources (nombres, codes-barres, textes)."""

import re
import unicodedata
from decimal import Decimal, InvalidOperation

KJ_PER_KCAL = Decimal("4.184")

_LESS_THAN = re.compile(r"^<\s*(?P<value>[0-9]+(?:[.,][0-9]+)?)$")
_TRACES = frozenset({"traces", "trace", "tr"})
_MISSING = frozenset({"", "-", "nd", "n/a", "na", "null", "none"})


def parse_decimal(raw: object) -> Decimal | None:
    """Convertit une valeur de table nutritionnelle en Decimal.

    Conventions (documentées dans docs/sources-donnees.md) :
    - virgule ou point décimal (« 12,5 » = « 12.5 ») ;
    - « - », vide, « ND » → valeur inconnue (None) ;
    - « traces » → 0 ;
    - « < 0,5 » (sous la limite de quantification) → moitié du seuil, soit 0,25.
    """
    if raw is None:
        return None
    if isinstance(raw, Decimal):
        return raw
    if isinstance(raw, int | float):
        return Decimal(str(raw))

    text = str(raw).strip().replace("\u00a0", "").replace("\u202f", "")
    lowered = text.lower()
    if lowered in _MISSING:
        return None
    if lowered in _TRACES:
        return Decimal(0)

    match = _LESS_THAN.match(text)
    if match:
        return Decimal(match["value"].replace(",", ".")) / 2

    try:
        value = Decimal(text.replace(",", "."))
    except InvalidOperation:
        return None
    return value if value.is_finite() else None


def kcal_from_kj(kj: Decimal | None) -> Decimal | None:
    return None if kj is None else (kj / KJ_PER_KCAL).quantize(Decimal("0.01"))


def is_valid_gtin(code: str) -> bool:
    """Code-barres EAN-8, UPC-A (12), EAN-13 ou GTIN-14 avec clé de contrôle correcte."""
    if not code.isdigit() or len(code) not in (8, 12, 13, 14):
        return False
    digits = [int(c) for c in code]
    body, check = digits[:-1], digits[-1]
    # Poids 3 et 1 en alternance, en partant du chiffre le plus à droite du corps.
    total = sum(d * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(body)))
    return (10 - total % 10) % 10 == check


def clean_text(raw: object, max_length: int) -> str | None:
    """Nettoie un libellé : normalisation Unicode, espaces, caractères de contrôle, longueur."""
    if raw is None:
        return None
    text = unicodedata.normalize("NFC", str(raw))
    text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C" or ch == " ")
    text = " ".join(text.split())
    return text[:max_length] if text else None


def normalize_header(header: object) -> str:
    """En-tête de colonne comparable : minuscules, sans accents, espaces simples."""
    text = unicodedata.normalize("NFKD", str(header or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return " ".join(text.lower().split())
