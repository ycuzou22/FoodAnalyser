"""Configuration typée de l'API, lue depuis les variables d'environnement préfixées API_."""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "test", "staging", "production"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


class Settings(BaseSettings):
    """Paramètres de l'API.

    Les URL de connexion contiennent des identifiants : elles sont typées `SecretStr`
    pour ne jamais apparaître dans un `repr`, un log ou une trace d'erreur. Elles n'ont
    pas de valeur par défaut : un service mal configuré refuse de démarrer.
    """

    model_config = SettingsConfigDict(env_prefix="API_", env_file=".env", extra="ignore")

    env: Environment = "development"
    log_level: LogLevel = "INFO"

    database_url: SecretStr
    redis_url: SecretStr
    rabbitmq_url: SecretStr

    cors_origins: list[str] = []
    readiness_timeout_seconds: float = 2.0

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def docs_enabled(self) -> bool:
        """Swagger UI et le schéma OpenAPI ne sont pas exposés en production."""
        return not self.is_production

    @model_validator(mode="after")
    def _forbid_wildcard_cors_in_production(self) -> "Settings":
        if self.is_production and "*" in self.cors_origins:
            raise ValueError("API_CORS_ORIGINS ne peut pas contenir « * » en production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # valeurs lues dans l'environnement
