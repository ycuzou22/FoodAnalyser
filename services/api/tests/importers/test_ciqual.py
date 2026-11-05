from decimal import Decimal
from pathlib import Path

import pytest
from openpyxl import Workbook

from app.importers.ciqual import CiqualFormatError, read_ciqual
from app.importers.records import FoodRecord
from app.models.enums import FoodSource

FIXTURE = Path(__file__).parents[1] / "fixtures" / "ciqual_sample.csv"


def _by_code(path: Path) -> dict[str | None, FoodRecord]:
    return {record.ciqual_code: record for record in read_ciqual(path)}


def test_reads_regulatory_energy_and_jones_protein() -> None:
    banana = _by_code(FIXTURE)["13005"]

    assert banana.source is FoodSource.CIQUAL
    assert banana.name == "Banane, pulpe, crue"
    # « Energie, Règlement UE 1169/2011 (kcal) », pas « Energie, N x facteur Jones » (95).
    assert banana.kcal_100g == Decimal("89.2")
    # « Protéines, N x facteur de Jones » (1,06) plutôt que « N x 6.25 » (1,2).
    assert banana.protein_100g == Decimal("1.06")
    assert banana.carbs_100g == Decimal("19.7")
    assert banana.fiber_100g == Decimal("2.7")
    assert banana.salt_100g == Decimal(0)  # « traces »


def test_special_values() -> None:
    records = _by_code(FIXTURE)

    assert records["20047"].salt_100g == Decimal("0.005")  # « < 0,01 »
    assert records["19024"].fiber_100g is None  # « - »
    # kcal absent : calculé depuis les kJ du règlement UE (640 / 4,184).
    assert records["9100"].kcal_100g == Decimal("152.96")


def test_rejection_reasons() -> None:
    reasons = {r.ciqual_code: r.rejection_reason() for r in read_ciqual(FIXTURE)}

    assert reasons["13005"] is None
    assert reasons["11000"] is None  # 899 kcal, l'huile reste valide
    assert reasons[None] == "missing_ciqual_code"
    assert reasons["24999"] == "missing_kcal"


def test_reads_xlsx_with_english_headers_and_numeric_cells(tmp_path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    assert sheet is not None
    sheet.append(
        [
            "alim_code",
            "alim_nom_eng",
            "Energy, Regulation EU No 1169/2011 (kcal/100g)",
            "Protein, nitrogen x Jones' factor (g/100g)",
            "Carbohydrate (g/100g)",
            "Fat (g/100g)",
            "Fibres (g/100g)",
            "Salt (g/100g)",
        ]
    )
    sheet.append([13005, "Banana, pulp, raw", 89.2, 1.06, 19.7, 0.25, 2.7, "traces"])
    path = tmp_path / "ciqual.xlsx"
    workbook.save(path)

    (record,) = list(read_ciqual(path))

    assert record.ciqual_code == "13005"  # 13005.0 lu par Excel → « 13005 »
    assert record.name == "Banana, pulp, raw"
    assert record.kcal_100g == Decimal("89.2")
    assert record.rejection_reason() is None


def test_missing_columns_stop_the_import_with_headers(tmp_path: Path) -> None:
    path = tmp_path / "pas_ciqual.csv"
    path.write_text("alim_code;alim_nom_fr;Eau (g/100 g)\n1;Eau;100\n", encoding="utf-8")

    # L'erreur survient à l'ouverture, avant toute itération : aucun import n'est commencé.
    with pytest.raises(CiqualFormatError, match="Colonnes introuvables.*En-têtes lus"):
        read_ciqual(path)


def test_unsupported_format(tmp_path: Path) -> None:
    path = tmp_path / "ciqual.json"
    path.write_text("{}", encoding="utf-8")

    with pytest.raises(CiqualFormatError, match="Format non pris en charge"):
        read_ciqual(path)
