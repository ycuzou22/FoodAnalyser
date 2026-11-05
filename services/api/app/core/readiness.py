"""Vérifications de disponibilité des dépendances, utilisées par `GET /ready`."""

import asyncio
from collections.abc import Awaitable, Callable, Mapping

import aio_pika
import structlog
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

ReadinessCheck = Callable[[], Awaitable[None]]

logger = structlog.get_logger("app.readiness")


def database_check(engine: AsyncEngine) -> ReadinessCheck:
    async def check() -> None:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

    return check


def redis_check(client: Redis) -> ReadinessCheck:
    async def check() -> None:
        if not await client.ping():
            raise ConnectionError("Redis n'a pas répondu au PING")

    return check


def rabbitmq_check(url: str, timeout: float) -> ReadinessCheck:
    async def check() -> None:
        connection = await aio_pika.connect(url, timeout=timeout)
        await connection.close()

    return check


async def run_checks(
    checks: Mapping[str, ReadinessCheck], per_check_seconds: float
) -> dict[str, bool]:
    """Lance toutes les vérifications en parallèle, chacune bornée à `per_check_seconds`.

    Le détail d'un échec (hôte, message du pilote) part dans les logs, jamais dans la réponse.
    """

    async def guarded(name: str, check: ReadinessCheck) -> tuple[str, bool]:
        try:
            async with asyncio.timeout(per_check_seconds):
                await check()
        except Exception as exc:
            logger.warning("readiness_check_failed", check=name, error_type=type(exc).__name__)
            return name, False
        return name, True

    results = await asyncio.gather(*(guarded(name, check) for name, check in checks.items()))
    return dict(results)
