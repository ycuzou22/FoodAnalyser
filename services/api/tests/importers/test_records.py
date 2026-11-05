from dataclasses import replace
from decimal import Decimal

import pytest

from app.importers.records import FoodRecord
from app.models.enums import FoodSource

VALID = FoodRecord(
    source=FoodSource.CIQUAL,
    ciqual_code="13005",
    name="Banane",
    kcal_100g=Decimal("89"),
    protein_100g=Decimal("1"),
    carbs_100g=Decimal("20"),
    fat_100g=Decimal("0.3"),
)


def test_valid_record() -> None:
    assert VALID.rejection_reason() is None


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"name": "  "}, "missing_name"),
        ({"ciqual_code": None}, "missing_ciqual_code"),
        ({"kcal_100g": None}, "missing_kcal"),
        ({"kcal_100g": Decimal(901)}, "kcal_out_of_range"),
        ({"kcal_100g": Decimal(-1)}, "kcal_out_of_range"),
        ({"fat_100g": None}, "missing_macros"),
        ({"salt_100g": Decimal(101)}, "nutrient_out_of_range"),
        ({"protein_100g": Decimal(-0.1)}, "nutrient_out_of_range"),
        (
            {"protein_100g": Decimal(40), "carbs_100g": Decimal(40), "fat_100g": Decimal(30)},
            "macros_exceed_100g",
        ),
        ({"nutriscore": "f"}, "invalid_nutriscore"),
    ],
)
def test_rejections(changes: dict[str, object], reason: str) -> None:
    assert replace(VALID, **changes).rejection_reason() == reason  # type: ignore[arg-type]


def test_rounding_tolerance_on_macro_sum() -> None:
    # 101,5 g : les sources arrondissent chaque valeur, on tolère 2 g.
    record = replace(
        VALID, protein_100g=Decimal(50), carbs_100g=Decimal(50), fat_100g=Decimal("1.5")
    )
    assert record.rejection_reason() is None


def test_off_record_requires_valid_barcode() -> None:
    off = replace(VALID, source=FoodSource.OPEN_FOOD_FACTS, ciqual_code=None, barcode="123")
    assert off.rejection_reason() == "invalid_barcode"
