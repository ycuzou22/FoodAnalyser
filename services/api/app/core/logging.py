"""Journalisation structurée en JSON.

Règle du projet : aucun log ne contient de donnée personnelle (e-mail, poids, contenu d'un
repas, jeton). On journalise des identifiants techniques, jamais des valeurs métier.
"""

import logging
import sys

import structlog

from app.core.config import LogLevel


def configure_logging(level: LogLevel = "INFO", *, json: bool = True, cache: bool = True) -> None:
    """Configure structlog et y redirige les logs de la bibliothèque standard (uvicorn…).

    `cache=False` en test : `structlog.testing.capture_logs` ne voit pas les loggers mis en cache.
    """
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer() if json else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[*shared_processors, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=cache,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=[structlog.stdlib.ProcessorFormatter.remove_processors_meta, renderer],
        )
    )
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)

    # Le middleware produit déjà une ligne par requête : on coupe l'access log d'uvicorn.
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.access").propagate = False
