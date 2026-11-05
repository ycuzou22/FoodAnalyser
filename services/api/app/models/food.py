"""Base d'aliments (CIQUAL, Open Food Facts) et recettes."""

import uuid
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, pg_enum
from app.models.enums import FoodSource

# Valeur nutritionnelle pour 100 g : 0 à 100 g, sauf l'énergie (0 à 900 kcal, l'huile pure).
_NUTRIENT = Numeric(6, 2)


class Food(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "foods"
    __table_args__ = (
        CheckConstraint("kcal_100g BETWEEN 0 AND 900", name="kcal_100g_range"),
        CheckConstraint("protein_100g BETWEEN 0 AND 100", name="protein_100g_range"),
        CheckConstraint("carbs_100g BETWEEN 0 AND 100", name="carbs_100g_range"),
        CheckConstraint("fat_100g BETWEEN 0 AND 100", name="fat_100g_range"),
        CheckConstraint("fiber_100g BETWEEN 0 AND 100", name="fiber_100g_range"),
        CheckConstraint("salt_100g BETWEEN 0 AND 100", name="salt_100g_range"),
        CheckConstraint("nutriscore IN ('a', 'b', 'c', 'd', 'e')", name="nutriscore_grade"),
        CheckConstraint("barcode ~ '^[0-9]{8,14}$'", name="barcode_digits"),
        # Recherche floue tolérante aux fautes (« banan » → « banane »).
        Index(
            "ix_foods_name_trgm",
            "name",
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
    )

    name: Mapped[str] = mapped_column(String(255))
    brand: Mapped[str | None] = mapped_column(String(255))
    barcode: Mapped[str | None] = mapped_column(String(14), unique=True)
    ciqual_code: Mapped[str | None] = mapped_column(String(10), unique=True)
    source: Mapped[FoodSource] = mapped_column(pg_enum(FoodSource, "food_source"))

    kcal_100g: Mapped[Decimal] = mapped_column(_NUTRIENT)
    protein_100g: Mapped[Decimal] = mapped_column(_NUTRIENT)
    carbs_100g: Mapped[Decimal] = mapped_column(_NUTRIENT)
    fat_100g: Mapped[Decimal] = mapped_column(_NUTRIENT)
    fiber_100g: Mapped[Decimal | None] = mapped_column(_NUTRIENT)
    salt_100g: Mapped[Decimal | None] = mapped_column(_NUTRIENT)
    nutriscore: Mapped[str | None] = mapped_column(String(1))

    popularity: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))


class Recipe(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "recipes"
    __table_args__ = (CheckConstraint("servings BETWEEN 1 AND 50", name="servings_range"),)

    # NULL = recette éditoriale (back-office) ; sinon recette privée d'un utilisateur.
    author_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    servings: Mapped[int] = mapped_column(Integer)
    instructions: Mapped[str | None] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))

    ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan", passive_deletes=True
    )


class RecipeIngredient(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "recipe_ingredients"
    __table_args__ = (CheckConstraint("quantity_g > 0", name="quantity_g_positive"),)

    recipe_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"), index=True
    )
    # RESTRICT : un aliment utilisé ne peut pas être supprimé, seulement fusionné (issue #35).
    food_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("foods.id", ondelete="RESTRICT"), index=True
    )
    quantity_g: Mapped[Decimal] = mapped_column(Numeric(7, 2))

    recipe: Mapped[Recipe] = relationship(back_populates="ingredients")
    food: Mapped[Food] = relationship()
