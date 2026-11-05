import gzip
import shutil
from decimal import Decimal
from pathlib import Path

from app.importers.off import read_off
from app.importers.records import FoodRecord

FIXTURE = Path(__file__).parents[1] / "fixtures" / "off_sample.tsv"


def _records(path: Path = FIXTURE) -> list[FoodRecord]:
    return list(read_off(path))


def test_keeps_only_products_sold_in_france() -> None:
    barcodes = [r.barcode for r in _records()]

    assert "3000000000021" not in barcodes  # vendu en Espagne uniquement
    assert "3017620422003" in barcodes


def test_reference_product_has_kcal_macros_and_nutriscore() -> None:
    nutella = next(r for r in _records() if r.barcode == "3017620422003")

    assert nutella.name == "Pâte à tartiner aux noisettes et au cacao"  # nom français prioritaire
    assert nutella.brand == "Nutella"  # première marque
    assert nutella.kcal_100g == Decimal(539)
    assert (nutella.protein_100g, nutella.carbs_100g, nutella.fat_100g) == (
        Decimal("6.3"),
        Decimal("57.5"),
        Decimal("30.9"),
    )
    assert nutella.nutriscore == "e"
    assert nutella.popularity == 1520
    assert nutella.rejection_reason() is None


def test_kcal_computed_from_kj_and_english_name_fallback() -> None:
    yogurt = next(r for r in _records() if r.barcode == "3000000000014")

    assert yogurt.name == "Yogurt"
    assert yogurt.kcal_100g == Decimal("59.99")  # 251 kJ / 4,184


def test_unknown_nutriscore_is_dropped() -> None:
    soda = next(r for r in _records() if r.barcode == "3000000000038")

    assert soda.nutriscore is None
    assert soda.rejection_reason() is None


def test_rejection_reasons() -> None:
    reasons = {r.barcode: r.rejection_reason() for r in _records()}

    assert reasons["3000000000020"] == "invalid_barcode"
    assert reasons["3000000000045"] == "missing_macros"


def test_reads_gzip_export(tmp_path: Path) -> None:
    compressed = tmp_path / "off.csv.gz"
    with FIXTURE.open("rb") as source, gzip.open(compressed, "wb") as target:
        shutil.copyfileobj(source, target)

    assert [r.barcode for r in read_off(compressed)] == [r.barcode for r in _records()]
