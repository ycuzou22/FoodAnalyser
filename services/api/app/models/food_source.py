"""Traçabilité des imports de données nutritionnelles (licence, version, volumes)."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin, pg_enum
from app.models.enums import FoodSource


class FoodSourceImport(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    """Un import d'une source dans la table `foods`. Sert d'attribution et d'audit."""

    __tablename__ = "food_source_imports"

    source: Mapped[FoodSource] = mapped_column(pg_enum(FoodSource, "food_source"))
    source_version: Mapped[str] = mapped_column(String(100))
    license: Mapped[str] = mapped_column(String(100))
    attribution: Mapped[str] = mapped_column(Text)
    file_name: Mapped[str] = mapped_column(String(255))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rows_read: Mapped[int] = mapped_column(Integer, default=0)
    rows_inserted: Mapped[int] = mapped_column(Integer, default=0)
    rows_updated: Mapped[int] = mapped_column(Integer, default=0)
    rows_rejected: Mapped[int] = mapped_column(Integer, default=0)
    # Nombre de lignes rejetées par motif, ex. {"missing_kcal": 120, "invalid_barcode": 4}
    rejections: Mapped[dict[str, int]] = mapped_column(JSONB, default=dict)
