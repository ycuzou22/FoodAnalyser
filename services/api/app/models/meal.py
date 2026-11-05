"""Repas, aliments d'un repas et prédictions de l'IA."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, pg_enum
from app.models.enums import MealSource, MealType, PredictionStatus

if TYPE_CHECKING:
    from app.models.food import Food
    from app.models.user import User


class AiPrediction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Résultat brut d'une analyse photo, conservé pour mesurer et réentraîner le modèle."""

    __tablename__ = "ai_predictions"
    __table_args__ = (CheckConstraint("latency_ms >= 0", name="latency_ms_positive"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    # Clé de l'objet dans le stockage S3, jamais une URL publique.
    image_key: Mapped[str] = mapped_column(String(512))
    model_version: Mapped[str] = mapped_column(String(50))
    status: Mapped[PredictionStatus] = mapped_column(
        pg_enum(PredictionStatus, "prediction_status"), server_default=PredictionStatus.PENDING
    )
    predictions: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    final_correction: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    latency_ms: Mapped[int | None] = mapped_column(Integer)

    user: Mapped["User"] = relationship()


class Meal(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "meals"
    __table_args__ = (Index("ix_meals_user_id_eaten_at", "user_id", "eaten_at"),)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    meal_type: Mapped[MealType] = mapped_column(pg_enum(MealType, "meal_type"))
    eaten_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source: Mapped[MealSource] = mapped_column(pg_enum(MealSource, "meal_source"))
    photo_key: Mapped[str | None] = mapped_column(String(512))
    ai_prediction_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("ai_predictions.id", ondelete="SET NULL"), index=True
    )
    is_favorite: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))

    user: Mapped["User"] = relationship(back_populates="meals")
    ai_prediction: Mapped[AiPrediction | None] = relationship()
    items: Mapped[list["MealItem"]] = relationship(
        back_populates="meal", cascade="all, delete-orphan", passive_deletes=True
    )


class MealItem(UUIDPrimaryKeyMixin, Base):
    """Aliment d'un repas.

    Les valeurs nutritionnelles sont copiées à l'enregistrement (snapshot) : corriger la base
    d'aliments ne réécrit pas l'historique de l'utilisateur.
    """

    __tablename__ = "meal_items"
    __table_args__ = (
        CheckConstraint("quantity_g > 0 AND quantity_g <= 5000", name="quantity_g_range"),
        CheckConstraint("ai_confidence BETWEEN 0 AND 1", name="ai_confidence_range"),
        CheckConstraint(
            "kcal >= 0 AND protein_g >= 0 AND carbs_g >= 0 AND fat_g >= 0",
            name="nutrients_positive",
        ),
    )

    meal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("meals.id", ondelete="CASCADE"), index=True
    )
    food_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("foods.id", ondelete="RESTRICT"), index=True
    )
    quantity_g: Mapped[Decimal] = mapped_column(Numeric(7, 2))

    food_name: Mapped[str] = mapped_column(String(255))
    kcal: Mapped[Decimal] = mapped_column(Numeric(7, 2))
    protein_g: Mapped[Decimal] = mapped_column(Numeric(7, 2))
    carbs_g: Mapped[Decimal] = mapped_column(Numeric(7, 2))
    fat_g: Mapped[Decimal] = mapped_column(Numeric(7, 2))

    ai_confidence: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    corrected: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))

    meal: Mapped[Meal] = relationship(back_populates="items")
    food: Mapped["Food"] = relationship()
