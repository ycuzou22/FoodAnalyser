"""Import de bout en bout dans PostgreSQL : insertion, idempotence, traçabilité."""

from pathlib import Path

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.importers.ciqual import read_ciqual
from app.importers.loader import SourceInfo, load_foods
from app.importers.off import read_off
from app.models import Food, FoodSourceImport
from app.models.enums import FoodSource

FIXTURES = Path(__file__).parents[1] / "fixtures"
CIQUAL = SourceInfo(FoodSource.CIQUAL, "test", "Licence Ouverte", "Anses", "ciqual_sample.csv")
OFF = SourceInfo(FoodSource.OPEN_FOOD_FACTS, "test", "ODbL", "OFF", "off_sample.tsv")


async def _clean(session: AsyncSession) -> None:
    # load_foods valide ses propres transactions : on travaille sur une base nettoyée.
    await session.execute(delete(FoodSourceImport))
    await session.execute(delete(Food))
    await session.commit()


async def test_import_is_idempotent_and_traced(engine: AsyncEngine) -> None:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        await _clean(session)
        try:
            first = await load_foods(session, read_ciqual(FIXTURES / "ciqual_sample.csv"), CIQUAL)
            second = await load_foods(session, read_ciqual(FIXTURES / "ciqual_sample.csv"), CIQUAL)

            assert (first.rows_read, first.rows_inserted, first.rows_updated) == (7, 5, 0)
            assert dict(first.rejections) == {"missing_ciqual_code": 1, "missing_kcal": 1}
            assert (second.rows_inserted, second.rows_updated) == (0, 5)
            assert await session.scalar(select(func.count()).select_from(Food)) == 5

            traces = (await session.scalars(select(FoodSourceImport))).all()
            assert len(traces) == 2
            assert all(t.finished_at is not None for t in traces)
            assert traces[0].rejections == {"missing_ciqual_code": 1, "missing_kcal": 1}
        finally:
            await _clean(session)


async def test_off_import_and_barcode_lookup(engine: AsyncEngine) -> None:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        await _clean(session)
        try:
            report = await load_foods(session, read_off(FIXTURES / "off_sample.tsv"), OFF)

            # 7 lignes françaises lues, 2 rejetées, 5 lignes valides dont un doublon → 4 produits.
            assert report.rows_read == 7
            assert dict(report.rejections) == {"invalid_barcode": 1, "missing_macros": 1}
            assert report.rows_inserted == 4

            nutella = await session.scalar(select(Food).where(Food.barcode == "3017620422003"))
            assert nutella is not None
            assert (nutella.kcal_100g, nutella.nutriscore) == (539, "e")

            duplicate = await session.scalar(select(Food).where(Food.barcode == "3000000000052"))
            assert duplicate is not None
            assert duplicate.name == "Nouveau nom"  # la dernière occurrence l'emporte
        finally:
            await _clean(session)


async def test_small_batches_give_the_same_result(engine: AsyncEngine) -> None:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        await _clean(session)
        try:
            report = await load_foods(
                session, read_off(FIXTURES / "off_sample.tsv"), OFF, batch_size=2
            )
            # Avec des lots de 2, le doublon tombe dans deux lots différents : mise à jour.
            assert report.rows_inserted + report.rows_updated == 5
            assert await session.scalar(select(func.count()).select_from(Food)) == 4
        finally:
            await _clean(session)
