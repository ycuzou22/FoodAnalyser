"""Enregistrement d'aliment normalisé, commun à toutes les sources, et règles de validation."""

from dataclasses import dataclass
from decimal import Decimal

from app.importers.parsing import is_valid_gtin
from app.models.enums import FoodSource

MAX_KCAL_100G = Decimal(900)  # l'huile pure est la valeur la plus haute possible
MAX_GRAMS_100G = Decimal(100)
# Tolérance d'arrondi sur la somme protéines + glucides + lipides (les sources arrondissent).
MACRO_SUM_TOLERANCE = Decimal(2)
NAME_MAX_LENGTH = 255
NUTRISCORE_GRADES = frozenset("abcde")


@dataclass(frozen=True, slots=True)
class FoodRecord:
    source: FoodSource
    name: str
    kcal_100g: Decimal | None
    protein_100g: Decimal | None
    carbs_100g: Decimal | None
    fat_100g: Decimal | None
    fiber_100g: Decimal | None = None
    salt_100g: Decimal | None = None
    brand: str | None = None
    barcode: str | None = None
    ciqual_code: str | None = None
    nutriscore: str | None = None
    popularity: int = 0

    def rejection_reason(self) -> str | None:
        """Motif de rejet, ou None si l'enregistrement peut être importé.

        Les motifs servent de clés dans le rapport d'import : ils sont courts et stables.
        """
        if not self.name.strip():
            return "missing_name"
        if self.source is FoodSource.CIQUAL and not self.ciqual_code:
            return "missing_ciqual_code"
        if self.source is FoodSource.OPEN_FOOD_FACTS and (
            self.barcode is None or not is_valid_gtin(self.barcode)
        ):
            return "invalid_barcode"
        if self.kcal_100g is None:
            return "missing_kcal"
        if not Decimal(0) <= self.kcal_100g <= MAX_KCAL_100G:
            return "kcal_out_of_range"

        macros = (self.protein_100g, self.carbs_100g, self.fat_100g)
        if any(value is None for value in macros):
            return "missing_macros"
        for value in (*macros, self.fiber_100g, self.salt_100g):
            if value is not None and not Decimal(0) <= value <= MAX_GRAMS_100G:
                return "nutrient_out_of_range"
        if sum(v for v in macros if v is not None) > MAX_GRAMS_100G + MACRO_SUM_TOLERANCE:
            return "macros_exceed_100g"

        if self.nutriscore is not None and self.nutriscore not in NUTRISCORE_GRADES:
            return "invalid_nutriscore"
        return None
