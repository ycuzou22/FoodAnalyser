"""Suivi du poids, de l'hydratation, abonnements et consentements."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import (
    HEALTH_DATA,
    Base,
    CreatedAtMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    pg_enum,
)
from app.models.enums import ConsentType, SubscriptionPlatform, SubscriptionStatus

if TYPE_CHECKING:
    from app.models.user import User


class WeightLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "weight_logs"
    __table_args__ = (
        UniqueConstraint("user_id", "logged_on"),  # une mesure par jour, la dernière remplace
        CheckConstraint("weight_kg BETWEEN 20 AND 400", name="weight_kg_range"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    logged_on: Mapped[date] = mapped_column(Date)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(5, 2), info=HEALTH_DATA)

    user: Mapped["User"] = relationship(back_populates="weight_logs")


class WaterLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "water_logs"
    __table_args__ = (
        UniqueConstraint("user_id", "logged_on"),
        CheckConstraint("volume_ml BETWEEN 0 AND 10000", name="volume_ml_range"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    logged_on: Mapped[date] = mapped_column(Date)
    volume_ml: Mapped[int] = mapped_column(Integer)

    user: Mapped["User"] = relationship(back_populates="water_logs")


class Subscription(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """État d'un abonnement, mis à jour uniquement par les webhooks RevenueCat (issue #32)."""

    __tablename__ = "subscriptions"
    __table_args__ = (UniqueConstraint("platform", "original_transaction_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    platform: Mapped[SubscriptionPlatform] = mapped_column(
        pg_enum(SubscriptionPlatform, "subscription_platform")
    )
    product_id: Mapped[str] = mapped_column(String(100))
    original_transaction_id: Mapped[str] = mapped_column(String(255))
    status: Mapped[SubscriptionStatus] = mapped_column(
        pg_enum(SubscriptionStatus, "subscription_status")
    )
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    trial_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship()


class Consent(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    """Historique des consentements, en ajout seul : chaque changement crée une ligne.

    Le consentement en vigueur est la ligne la plus récente pour (utilisateur, type).
    """

    __tablename__ = "consents"
    __table_args__ = (
        Index(
            "ix_consents_user_id_consent_type_created_at", "user_id", "consent_type", "created_at"
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    consent_type: Mapped[ConsentType] = mapped_column(pg_enum(ConsentType, "consent_type"))
    granted: Mapped[bool] = mapped_column(Boolean)
    version: Mapped[str] = mapped_column(String(20))
    source: Mapped[str] = mapped_column(String(20))

    user: Mapped["User"] = relationship()
