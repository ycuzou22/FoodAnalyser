"""Lecture de l'export CSV d'Open Food Facts (produits emballés).

Fichier : `en.openfoodfacts.org.products.csv.gz` (séparateur tabulation, plusieurs Go). Il est
lu en flux, ligne à ligne, sans jamais être chargé en mémoire. Seuls les produits vendus en
France sont retenus pour la V1.
"""

import csv
import gzip
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import TextIO

from app.importers.parsing import clean_text, kcal_from_kj, parse_decimal
from app.importers.records import NAME_MAX_LENGTH, NUTRISCORE_GRADES, FoodRecord
from app.models.enums import FoodSource

DEFAULT_COUNTRY_TAG = "en:france"

# Certaines cellules (ingrédients) dépassent la limite par défaut de 128 Ko du module csv.
csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


def _open(path: Path) -> TextIO:
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", newline="")
    return path.open(encoding="utf-8", newline="")


def _popularity(raw: str | None) -> int:
    value = parse_decimal(raw)
    return max(0, int(value)) if value is not None else 0


def _nutriscore(raw: str | None) -> str | None:
    grade = (raw or "").strip().lower()
    # OFF utilise aussi « unknown » et « not-applicable ».
    return grade if grade in NUTRISCORE_GRADES else None


def read_off(path: Path, country_tag: str = DEFAULT_COUNTRY_TAG) -> Iterator[FoodRecord]:
    with _open(path) as handle:
        reader = csv.DictReader(handle, delimiter="\t", quoting=csv.QUOTE_NONE)
        for row in reader:
            countries = (row.get("countries_tags") or "").split(",")
            if country_tag not in countries:
                continue

            kcal = parse_decimal(row.get("energy-kcal_100g"))
            if kcal is None:
                # « energy_100g » et « energy-kj_100g » sont exprimés en kJ.
                kcal = kcal_from_kj(
                    parse_decimal(row.get("energy-kj_100g") or row.get("energy_100g"))
                )

            name = row.get("product_name_fr") or row.get("product_name")
            brands = (row.get("brands") or "").split(",")[0]
            yield FoodRecord(
                source=FoodSource.OPEN_FOOD_FACTS,
                barcode=(row.get("code") or "").strip() or None,
                name=clean_text(name, NAME_MAX_LENGTH) or "",
                brand=clean_text(brands, NAME_MAX_LENGTH),
                kcal_100g=kcal,
                protein_100g=parse_decimal(row.get("proteins_100g")),
                carbs_100g=parse_decimal(row.get("carbohydrates_100g")),
                fat_100g=parse_decimal(row.get("fat_100g")),
                fiber_100g=parse_decimal(row.get("fiber_100g")),
                salt_100g=parse_decimal(row.get("salt_100g")),
                nutriscore=_nutriscore(row.get("nutriscore_grade")),
                popularity=_popularity(row.get("unique_scans_n")),
            )
