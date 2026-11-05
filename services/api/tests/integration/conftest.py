"""Tests d'intégration contre un vrai PostgreSQL.

Ils ne tournent que si API_TEST_DATABASE_URL est défini, par exemple :

    API_TEST_DATABASE_URL=postgresql+asyncpg://foodanalyser:...@localhost:5432/foodanalyser_test \\
        uv run pytest -m integration

La base indiquée est entièrement vidée puis recréée par les migrations : ne jamais pointer
vers une base contenant des données.
"""

import os
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

TEST_DATABASE_URL = os.environ.get("API_TEST_DATABASE_URL")
API_ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.integration


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        if "integration" in str(item.path):
            item.add_marker(pytest.mark.integration)
            if not TEST_DATABASE_URL:
                item.add_marker(pytest.mark.skip(reason="API_TEST_DATABASE_URL non défini"))


def alembic_config() -> Config:
    assert TEST_DATABASE_URL is not None
    config = Config(str(API_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(API_ROOT / "migrations"))
    config.cmd_opts = type("Opts", (), {"x": [f"url={TEST_DATABASE_URL}"]})()  # type: ignore[assignment]
    return config


@pytest.fixture(scope="session")
def migrated_database() -> str:
    """Repart de zéro puis applique toutes les migrations (teste aussi le downgrade)."""
    assert TEST_DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    return TEST_DATABASE_URL


@pytest.fixture
async def engine(migrated_database: str) -> AsyncIterator[AsyncEngine]:
    db_engine = create_async_engine(migrated_database)
    yield db_engine
    await db_engine.dispose()


@pytest.fixture
async def session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Session isolée : tout ce que fait le test est annulé à la fin."""
    async with engine.connect() as connection:
        transaction = await connection.begin()
        db_session = AsyncSession(
            bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
        )
        try:
            yield db_session
        finally:
            await db_session.close()
            await transaction.rollback()
