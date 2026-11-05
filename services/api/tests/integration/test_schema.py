"""Contraintes du schéma vérifiées sur un vrai PostgreSQL (migrations appliquées)."""

from datetime import date
from decimal import Decimal

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

import app.models  # noqa: F401
from app.db.base import Base
from app.models import Food, MealItem, User, WeightLog
from tests.factories import make_food, make_full_user_graph, make_meal, make_user

USER_TABLES = (
    "profiles",
    "dietary_preferences",
    "ai_predictions",
    "meals",
    "weight_logs",
    "water_logs",
    "subscriptions",
    "consents",
)


async def test_migrations_match_models(engine: AsyncEngine) -> None:
    def diff(sync_connection: object) -> list[object]:
        context = MigrationContext.configure(
            sync_connection,  # type: ignore[arg-type]
            opts={"compare_type": True, "compare_server_default": True},
        )
        return compare_metadata(context, Base.metadata)

    async with engine.connect() as connection:
        differences = await connection.run_sync(diff)

    assert differences == []


async def test_deleting_a_user_deletes_all_their_data(session: AsyncSession) -> None:
    food = make_food()
    user, related = make_full_user_graph(food)
    session.add_all([food, user, *related])
    await session.flush()
    user_id = user.id

    for table in USER_TABLES:
        count = await session.scalar(
            text(f"SELECT count(*) FROM {table} WHERE user_id = :uid"),  # noqa: S608 - nom fixe
            {"uid": user_id},
        )
        assert count == 1, table

    await session.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": user_id})

    for table in USER_TABLES:
        count = await session.scalar(
            text(f"SELECT count(*) FROM {table} WHERE user_id = :uid"),  # noqa: S608
            {"uid": user_id},
        )
        assert count == 0, table
    assert await session.scalar(select(func.count()).select_from(MealItem)) == 0
    # L'aliment de référence, lui, est conservé.
    assert await session.get(Food, food.id) is not None


async def test_meal_item_quantity_must_be_positive(session: AsyncSession) -> None:
    food = make_food()
    session.add(make_meal(make_user(), food, quantity_g="0"))

    with pytest.raises(IntegrityError, match="ck_meal_items_quantity_g_range"):
        await session.flush()


@pytest.mark.parametrize("weight", ["19.99", "400.01"])
async def test_weight_outside_plausible_range_is_rejected(
    session: AsyncSession, weight: str
) -> None:
    session.add(WeightLog(user=make_user(), logged_on=date(2026, 11, 5), weight_kg=Decimal(weight)))

    with pytest.raises(IntegrityError, match="ck_weight_logs_weight_kg_range"):
        await session.flush()


async def test_one_weight_per_user_per_day(session: AsyncSession) -> None:
    user = make_user()
    session.add_all(
        [
            WeightLog(user=user, logged_on=date(2026, 11, 5), weight_kg=Decimal("64.5")),
            WeightLog(user=user, logged_on=date(2026, 11, 5), weight_kg=Decimal("64.2")),
        ]
    )

    with pytest.raises(IntegrityError, match="uq_weight_logs_user_id_logged_on"):
        await session.flush()


async def test_email_is_unique_regardless_of_case(session: AsyncSession) -> None:
    session.add(make_user(email="Camille@Example.test"))
    await session.flush()
    session.add(make_user(email="camille@example.test"))

    with pytest.raises(IntegrityError, match="uq_users_email_lower"):
        await session.flush()


async def test_referenced_food_cannot_be_deleted(session: AsyncSession) -> None:
    food = make_food()
    session.add(make_meal(make_user(), food))
    await session.flush()

    with pytest.raises(IntegrityError, match="fk_meal_items_food_id_foods"):
        await session.execute(text("DELETE FROM foods WHERE id = :id"), {"id": food.id})


async def test_invalid_nutriscore_is_rejected(session: AsyncSession) -> None:
    session.add(make_food(nutriscore="f"))

    with pytest.raises(IntegrityError, match="ck_foods_nutriscore_grade"):
        await session.flush()


async def test_fuzzy_search_finds_food_despite_typo(session: AsyncSession) -> None:
    session.add_all([make_food(name="Banane"), make_food(name="Pomme"), make_food(name="Ananas")])
    await session.flush()

    rows = await session.execute(
        select(Food.name)
        .where(Food.name.op("%")("banan"))
        .order_by(func.similarity(Food.name, "banan").desc())
    )

    assert rows.scalars().first() == "Banane"


async def test_ids_are_uuid_v7(session: AsyncSession) -> None:
    user = make_user()
    session.add(user)
    await session.flush()

    stored: User | None = await session.get(User, user.id)
    assert stored is not None
    assert stored.id.version == 7
