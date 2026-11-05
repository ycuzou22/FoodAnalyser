"""Compte utilisateur, profil et préférences alimentaires."""

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
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import HEALTH_DATA, Base, TimestampMixin, UUIDPrimaryKeyMixin, pg_enum
from app.models.enums import ActivityLevel, AuthProvider, DietaryPreferenceKind, GoalType, Sex

if TYPE_CHECKING:
    from app.models.meal import Meal
    from app.models.tracking import WaterLog, WeightLog


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        # Unicité insensible à la casse : « Camille@x.fr » et « camille@x.fr » sont le même compte.
        Index("uq_users_email_lower", func.lower(text("email")), unique=True),
    )

    email: Mapped[str] = mapped_column(String(320))
    auth_provider: Mapped[AuthProvider] = mapped_column(pg_enum(AuthProvider, "auth_provider"))
    password_hash: Mapped[str | None] = mapped_column(String(255))
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    timezone: Mapped[str] = mapped_column(String(64), server_default="Europe/Paris")
    locale: Mapped[str] = mapped_column(String(10), server_default="fr-FR")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Demande de suppression : le compte est désactivé tout de suite, purgé sous 30 jours.
    deletion_requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    profile: Mapped["Profile | None"] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    dietary_preferences: Mapped[list["DietaryPreference"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    meals: Mapped[list["Meal"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    weight_logs: Mapped[list["WeightLog"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    water_logs: Mapped[list["WaterLog"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )


class Profile(TimestampMixin, Base):
    """Profil physiologique et cibles. Toutes les colonnes sont des données de santé."""

    __tablename__ = "profiles"
    __table_args__ = (
        CheckConstraint("height_cm BETWEEN 100 AND 250", name="height_cm_range"),
        CheckConstraint("target_weight_kg BETWEEN 20 AND 400", name="target_weight_kg_range"),
        CheckConstraint("kcal_target BETWEEN 1200 AND 6000", name="kcal_target_range"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    sex: Mapped[Sex] = mapped_column(pg_enum(Sex, "sex"), info=HEALTH_DATA)
    birth_date: Mapped[date] = mapped_column(Date, info=HEALTH_DATA)
    height_cm: Mapped[Decimal] = mapped_column(Numeric(4, 1), info=HEALTH_DATA)
    activity_level: Mapped[ActivityLevel] = mapped_column(
        pg_enum(ActivityLevel, "activity_level"), info=HEALTH_DATA
    )
    goal_type: Mapped[GoalType] = mapped_column(pg_enum(GoalType, "goal_type"), info=HEALTH_DATA)
    target_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), info=HEALTH_DATA)
    kcal_target: Mapped[int] = mapped_column(Integer, info=HEALTH_DATA)
    protein_g_target: Mapped[int] = mapped_column(Integer, info=HEALTH_DATA)
    carbs_g_target: Mapped[int] = mapped_column(Integer, info=HEALTH_DATA)
    fat_g_target: Mapped[int] = mapped_column(Integer, info=HEALTH_DATA)

    user: Mapped[User] = relationship(back_populates="profile")


class DietaryPreference(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "dietary_preferences"
    __table_args__ = (UniqueConstraint("user_id", "kind", "value"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[DietaryPreferenceKind] = mapped_column(
        pg_enum(DietaryPreferenceKind, "dietary_preference_kind")
    )
    # Une allergie est une donnée de santé.
    value: Mapped[str] = mapped_column(String(50), info=HEALTH_DATA)

    user: Mapped[User] = relationship(back_populates="dietary_preferences")
