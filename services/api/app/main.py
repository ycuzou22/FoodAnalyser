"""Point d'entrée de l'API : `uvicorn app.main:app`."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from app import __version__
from app.api.v1.router import api_router
from app.api.v1.routes import health
from app.core.config import Settings, get_settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging
from app.core.middleware import REQUEST_ID_HEADER, RequestContextMiddleware
from app.core.readiness import database_check, rabbitmq_check, redis_check
from app.db.session import create_engine, create_session_factory


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    engine = create_engine(settings)
    redis = Redis.from_url(settings.redis_url.get_secret_value())

    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)
    app.state.redis = redis
    app.state.readiness_checks = {
        "database": database_check(engine),
        "redis": redis_check(redis),
        "rabbitmq": rabbitmq_check(
            settings.rabbitmq_url.get_secret_value(), settings.readiness_timeout_seconds
        ),
    }
    try:
        yield
    finally:
        await redis.aclose()
        await engine.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(
        settings.log_level,
        json=settings.env != "development",
        cache=settings.env != "test",
    )

    app = FastAPI(
        title="FoodAnalyser API",
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )
    app.state.settings = settings

    register_error_handlers(app)

    # Ordre d'exécution : RequestContext (le plus externe) puis CORS.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", REQUEST_ID_HEADER],
        expose_headers=[REQUEST_ID_HEADER],
    )
    app.add_middleware(RequestContextMiddleware)

    app.include_router(health.router)
    app.include_router(api_router)
    return app


app = create_app()
