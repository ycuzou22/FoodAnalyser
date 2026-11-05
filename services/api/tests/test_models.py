"""Tests du modèle de données sans base : règles vérifiables sur les métadonnées."""

import time
import uuid

from sqlalchemy import ForeignKeyConstraint

import app.models  # noqa: F401 - enregistre les tables
from app.db.base import Base
from app.db.ids import uuid7

EXPECTED_TABLES = {
    "users",
    "profiles",
    "dietary_preferences",
    "foods",
    "recipes",
    "recipe_ingredients",
    "meals",
    "meal_items",
    "ai_predictions",
    "weight_logs",
    "water_logs",
    "subscriptions",
    "consents",
    "food_source_imports",
}


def test_all_v1_tables_are_declared() -> None:
    assert set(Base.metadata.tables) == EXPECTED_TABLES


def test_every_reference_to_users_cascades_on_delete() -> None:
    """Droit à l'effacement : supprimer un utilisateur doit supprimer toutes ses données."""
    for table in Base.metadata.tables.values():
        for constraint in table.constraints:
            if (
                isinstance(constraint, ForeignKeyConstraint)
                and constraint.referred_table.name == "users"
            ):
                assert constraint.ondelete == "CASCADE", f"{table.name}.{constraint.name}"


def test_health_data_columns_are_marked() -> None:
    marked = {
        f"{table.name}.{column.name}"
        for table in Base.metadata.tables.values()
        for column in table.columns
        if column.info.get("health_data")
    }

    assert marked == {
        "profiles.sex",
        "profiles.birth_date",
        "profiles.height_cm",
        "profiles.activity_level",
        "profiles.goal_type",
        "profiles.target_weight_kg",
        "profiles.kcal_target",
        "profiles.protein_g_target",
        "profiles.carbs_g_target",
        "profiles.fat_g_target",
        "dietary_preferences.value",
        "weight_logs.weight_kg",
    }


def test_table_names_are_plural_snake_case() -> None:
    for name in Base.metadata.tables:
        assert name == name.lower()
        assert name.endswith("s"), name


def test_uuid7_has_version_and_variant() -> None:
    value = uuid7()

    assert value.version == 7
    assert value.variant == uuid.RFC_4122


def test_uuid7_is_time_ordered_and_unique() -> None:
    first = uuid7()
    time.sleep(0.002)
    second = uuid7()

    assert first < second
    assert len({uuid7() for _ in range(10_000)}) == 10_000
