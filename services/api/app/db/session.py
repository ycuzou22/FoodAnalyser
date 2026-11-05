"""Connexion PostgreSQL asynchrone (SQLAlchemy 2 + asyncpg)."""

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings


def create_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(
        settings.database_url.get_secret_value(),
        pool_size=10,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=1800,
        # Jamais `echo=True` : les requêtes journalisées contiendraient des données personnelles.
        echo=False,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Dépendance FastAPI : une session par requête, annulée en cas d'erreur.

    Le commit est explicite dans les services (`await session.commit()`).
    """
    factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
