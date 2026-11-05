"""Lecture de la table CIQUAL de l'Anses (aliments génériques).

Formats acceptés : `.xls` (diffusion 2020), `.xlsx` et `.csv` (séparateur `;` ou `,`).

Les colonnes de nutriments sont repérées par motif et non par intitulé exact : les libellés
varient d'une version à l'autre (et entre version française et anglaise). Si une colonne
indispensable est introuvable, l'import s'arrête avec la liste des en-têtes lus, plutôt
que d'importer des valeurs fausses.
"""

import csv
import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

from app.importers.parsing import clean_text, kcal_from_kj, normalize_header, parse_decimal
from app.importers.records import NAME_MAX_LENGTH, FoodRecord
from app.models.enums import FoodSource


class CiqualFormatError(ValueError):
    """Le fichier ne ressemble pas à une table CIQUAL exploitable."""


@dataclass(frozen=True)
class _ColumnRule:
    field: str
    patterns: tuple[str, ...]  # tous doivent être présents dans l'en-tête normalisé
    required: bool = True
    excludes: tuple[str, ...] = ()


# L'ordre compte : pour un même champ, la première règle qui trouve une colonne l'emporte.
_RULES: tuple[_ColumnRule, ...] = (
    _ColumnRule("code", (r"^alim_code$",)),
    _ColumnRule("name", (r"^alim_nom_fr$",), required=False),
    _ColumnRule("name", (r"^alim_nom_eng?$",), required=False),
    # Énergie selon le règlement UE 1169/2011 (étiquetage), en kcal, sinon en kJ.
    _ColumnRule("kcal", (r"(energie|energy)", r"1169", r"kcal"), required=False),
    _ColumnRule("kj", (r"(energie|energy)", r"1169", r"kj"), required=False),
    # Protéines : facteur de Jones (référence étiquetage) avant N x 6,25.
    _ColumnRule("protein", (r"^(proteines|protein)", r"jones"), required=False),
    _ColumnRule("protein", (r"^(proteines|protein)", r"6[.,]25"), required=False),
    _ColumnRule("carbs", (r"^(glucides|carbohydrate)",), excludes=(r"fibre",)),
    _ColumnRule("fat", (r"^(lipides|fat)\b",)),
    _ColumnRule("fiber", (r"^(fibres|fibre|fiber)",), required=False),
    _ColumnRule("salt", (r"^(sel|salt)\b",), required=False),
)


def _map_columns(headers: Sequence[object]) -> dict[str, int]:
    normalized = [normalize_header(h) for h in headers]
    mapping: dict[str, int] = {}
    for rule in _RULES:
        if rule.field in mapping:
            continue
        for index, header in enumerate(normalized):
            if all(re.search(p, header) for p in rule.patterns) and not any(
                re.search(e, header) for e in rule.excludes
            ):
                mapping[rule.field] = index
                break

    missing = [r.field for r in _RULES if r.required and r.field not in mapping]
    if "name" not in mapping:
        missing.append("name (alim_nom_fr)")
    if "kcal" not in mapping and "kj" not in mapping:
        missing.append("énergie UE 1169/2011 (kcal ou kJ)")
    if "protein" not in mapping:
        missing.append("protéines")
    if missing:
        raise CiqualFormatError(
            f"Colonnes introuvables : {', '.join(missing)}. En-têtes lus : {list(headers)}"
        )
    return mapping


def _read_table(path: Path) -> Iterator[Sequence[object]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as handle:
            sample = handle.read(4096)
            handle.seek(0)
            dialect = csv.Sniffer().sniff(sample, delimiters=";,\t")
            yield from csv.reader(handle, dialect)
    elif suffix == ".xlsx":
        from openpyxl import load_workbook

        workbook = load_workbook(path, read_only=True, data_only=True)
        try:
            sheet = workbook.worksheets[0]
            yield from sheet.iter_rows(values_only=True)
        finally:
            workbook.close()
    elif suffix == ".xls":
        import xlrd

        book = xlrd.open_workbook(str(path), on_demand=True)
        try:
            xls_sheet = book.sheet_by_index(0)
            for row_index in range(xls_sheet.nrows):
                yield xls_sheet.row_values(row_index)
        finally:
            book.release_resources()
    else:
        raise CiqualFormatError(f"Format non pris en charge : {suffix} (attendu .xls, .xlsx, .csv)")


def _cell(row: Sequence[object], mapping: dict[str, int], field: str) -> object:
    index = mapping.get(field)
    return row[index] if index is not None and index < len(row) else None


def _code(raw: object) -> str | None:
    # Excel lit souvent « 25601 » comme le nombre 25601.0.
    if isinstance(raw, float) and raw.is_integer():
        raw = int(raw)
    text = clean_text(raw, 10)
    return text if text and text.isdigit() else None


def read_ciqual(path: Path) -> Iterator[FoodRecord]:
    """Ouvre le fichier et vérifie ses colonnes **immédiatement**, puis lit les lignes en flux.

    Un fichier mal formé lève `CiqualFormatError` dès l'appel, avant qu'un import ne commence
    (et donc avant toute écriture en base).
    """
    rows = _read_table(path)
    try:
        headers = next(rows)
    except StopIteration as exc:
        raise CiqualFormatError("Fichier vide") from exc
    return _records(rows, _map_columns(headers))


def _records(rows: Iterator[Sequence[object]], mapping: dict[str, int]) -> Iterator[FoodRecord]:
    for row in rows:
        kcal = parse_decimal(_cell(row, mapping, "kcal"))
        if kcal is None:
            kcal = kcal_from_kj(parse_decimal(_cell(row, mapping, "kj")))
        yield FoodRecord(
            source=FoodSource.CIQUAL,
            ciqual_code=_code(_cell(row, mapping, "code")),
            name=clean_text(_cell(row, mapping, "name"), NAME_MAX_LENGTH) or "",
            kcal_100g=kcal,
            protein_100g=parse_decimal(_cell(row, mapping, "protein")),
            carbs_100g=parse_decimal(_cell(row, mapping, "carbs")),
            fat_100g=parse_decimal(_cell(row, mapping, "fat")),
            fiber_100g=parse_decimal(_cell(row, mapping, "fiber")),
            salt_100g=parse_decimal(_cell(row, mapping, "salt")),
        )
