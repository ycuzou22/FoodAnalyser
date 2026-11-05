"""Environnement Alembic asynchrone (asyncpg)."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

import app.models  # noqa: F401 - enregistre toutes les tables dans Base.metadata
from app.core.config import get_settings
from app.db.base import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Schémas gérés par la migration initiale ; « analytics » accueillera les agrégats anonymisés.
MANAGED_SCHEMAS = {None, "public"}


def _include_object(
    obj: object, name: str | None, type_: str, reflected: bool, compare_to: object
) -> bool:
    schema = getattr(obj, "schema", None)
    return schema in MANAGED_SCHEMAS


def _database_url() -> str:
    # Permet `alembic -x url=...` (tests d'intégration) ; sinon API_DATABASE_URL.
    override = context.get_x_argument(as_dictionary=True).get("url")
    return override or get_settings().database_url.get_secret_value()


def run_migrations_offline() -> None:
    """Génère le SQL sans se connecter (`alembic upgrade head --sql`)."""
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_object=_include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def _run_sync(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_object=_include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(_database_url())
    async with engine.connect() as connection:
        await connection.run_sync(_run_sync)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
