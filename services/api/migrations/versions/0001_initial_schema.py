"""Schéma initial : comptes, profils, aliments, repas, suivi, abonnements, consentements.

Révision : 0001
Précédente : aucune

Voir docs/architecture/modele-donnees.md pour le diagramme entité-relation.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


ENUM_TYPES = (
    "auth_provider",
    "sex",
    "activity_level",
    "goal_type",
    "dietary_preference_kind",
    "food_source",
    "meal_type",
    "meal_source",
    "prediction_status",
    "subscription_platform",
    "subscription_status",
    "consent_type",
)


def upgrade() -> None:
    # Recherche floue des aliments (index trigramme ix_foods_name_trgm).
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    # Agrégats anonymisés du tableau de bord, isolés des données personnelles (issue #52).
    op.execute("CREATE SCHEMA IF NOT EXISTS analytics")

    op.create_table(
        "foods",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("brand", sa.String(length=255), nullable=True),
        sa.Column("barcode", sa.String(length=14), nullable=True),
        sa.Column("ciqual_code", sa.String(length=10), nullable=True),
        sa.Column(
            "source", sa.Enum("ciqual", "off", "internal", name="food_source"), nullable=False
        ),
        sa.Column("kcal_100g", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("protein_100g", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("carbs_100g", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("fat_100g", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("fiber_100g", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("salt_100g", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("nutriscore", sa.String(length=1), nullable=True),
        sa.Column("popularity", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("barcode ~ '^[0-9]{8,14}$'", name=op.f("ck_foods_barcode_digits")),
        sa.CheckConstraint(
            "nutriscore IN ('a', 'b', 'c', 'd', 'e')", name=op.f("ck_foods_nutriscore_grade")
        ),
        sa.CheckConstraint("carbs_100g BETWEEN 0 AND 100", name=op.f("ck_foods_carbs_100g_range")),
        sa.CheckConstraint("fat_100g BETWEEN 0 AND 100", name=op.f("ck_foods_fat_100g_range")),
        sa.CheckConstraint("fiber_100g BETWEEN 0 AND 100", name=op.f("ck_foods_fiber_100g_range")),
        sa.CheckConstraint("kcal_100g BETWEEN 0 AND 900", name=op.f("ck_foods_kcal_100g_range")),
        sa.CheckConstraint(
            "protein_100g BETWEEN 0 AND 100", name=op.f("ck_foods_protein_100g_range")
        ),
        sa.CheckConstraint("salt_100g BETWEEN 0 AND 100", name=op.f("ck_foods_salt_100g_range")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_foods")),
        sa.UniqueConstraint("barcode", name=op.f("uq_foods_barcode")),
        sa.UniqueConstraint("ciqual_code", name=op.f("uq_foods_ciqual_code")),
    )
    op.create_index(
        "ix_foods_name_trgm",
        "foods",
        ["name"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"name": "gin_trgm_ops"},
    )
    op.create_table(
        "users",
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column(
            "auth_provider",
            sa.Enum("email", "apple", "google", name="auth_provider"),
            nullable=False,
        ),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("timezone", sa.String(length=64), server_default="Europe/Paris", nullable=False),
        sa.Column("locale", sa.String(length=10), server_default="fr-FR", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deletion_requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(
        "uq_users_email_lower", "users", [sa.literal_column("lower(email)")], unique=True
    )
    op.create_table(
        "ai_predictions",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("image_key", sa.String(length=512), nullable=False),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "completed", "failed", name="prediction_status"),
            server_default="pending",
            nullable=False,
        ),
        sa.Column("predictions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("final_correction", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("latency_ms >= 0", name=op.f("ck_ai_predictions_latency_ms_positive")),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_ai_predictions_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ai_predictions")),
    )
    op.create_index(op.f("ix_ai_predictions_user_id"), "ai_predictions", ["user_id"], unique=False)
    op.create_table(
        "consents",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "consent_type",
            sa.Enum("health_data", "ai_training", "analytics", "marketing", name="consent_type"),
            nullable=False,
        ),
        sa.Column("granted", sa.Boolean(), nullable=False),
        sa.Column("version", sa.String(length=20), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_consents_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_consents")),
    )
    op.create_index(
        "ix_consents_user_id_consent_type_created_at",
        "consents",
        ["user_id", "consent_type", "created_at"],
        unique=False,
    )
    op.create_table(
        "dietary_preferences",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "kind", sa.Enum("diet", "allergen", name="dietary_preference_kind"), nullable=False
        ),
        sa.Column("value", sa.String(length=50), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_dietary_preferences_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_dietary_preferences")),
        sa.UniqueConstraint(
            "user_id", "kind", "value", name=op.f("uq_dietary_preferences_user_id_kind_value")
        ),
    )
    op.create_index(
        op.f("ix_dietary_preferences_user_id"), "dietary_preferences", ["user_id"], unique=False
    )
    op.create_table(
        "profiles",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("sex", sa.Enum("female", "male", name="sex"), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("height_cm", sa.Numeric(precision=4, scale=1), nullable=False),
        sa.Column(
            "activity_level",
            sa.Enum(
                "sedentary", "light", "moderate", "active", "very_active", name="activity_level"
            ),
            nullable=False,
        ),
        sa.Column(
            "goal_type",
            sa.Enum("lose_weight", "maintain", "gain_muscle", "rebalance", name="goal_type"),
            nullable=False,
        ),
        sa.Column("target_weight_kg", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("kcal_target", sa.Integer(), nullable=False),
        sa.Column("protein_g_target", sa.Integer(), nullable=False),
        sa.Column("carbs_g_target", sa.Integer(), nullable=False),
        sa.Column("fat_g_target", sa.Integer(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "height_cm BETWEEN 100 AND 250", name=op.f("ck_profiles_height_cm_range")
        ),
        sa.CheckConstraint(
            "kcal_target BETWEEN 1200 AND 6000", name=op.f("ck_profiles_kcal_target_range")
        ),
        sa.CheckConstraint(
            "target_weight_kg BETWEEN 20 AND 400", name=op.f("ck_profiles_target_weight_kg_range")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_profiles_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_profiles")),
    )
    op.create_table(
        "recipes",
        sa.Column("author_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("servings", sa.Integer(), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("is_public", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("servings BETWEEN 1 AND 50", name=op.f("ck_recipes_servings_range")),
        sa.ForeignKeyConstraint(
            ["author_id"], ["users.id"], name=op.f("fk_recipes_author_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_recipes")),
    )
    op.create_index(op.f("ix_recipes_author_id"), "recipes", ["author_id"], unique=False)
    op.create_table(
        "subscriptions",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "platform",
            sa.Enum("app_store", "play_store", name="subscription_platform"),
            nullable=False,
        ),
        sa.Column("product_id", sa.String(length=100), nullable=False),
        sa.Column("original_transaction_id", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "trialing",
                "active",
                "grace_period",
                "billing_issue",
                "cancelled",
                "expired",
                name="subscription_status",
            ),
            nullable=False,
        ),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("trial_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_subscriptions_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subscriptions")),
        sa.UniqueConstraint(
            "platform",
            "original_transaction_id",
            name=op.f("uq_subscriptions_platform_original_transaction_id"),
        ),
    )
    op.create_index(op.f("ix_subscriptions_user_id"), "subscriptions", ["user_id"], unique=False)
    op.create_table(
        "water_logs",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("logged_on", sa.Date(), nullable=False),
        sa.Column("volume_ml", sa.Integer(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "volume_ml BETWEEN 0 AND 10000", name=op.f("ck_water_logs_volume_ml_range")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_water_logs_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_water_logs")),
        sa.UniqueConstraint("user_id", "logged_on", name=op.f("uq_water_logs_user_id_logged_on")),
    )
    op.create_table(
        "weight_logs",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("logged_on", sa.Date(), nullable=False),
        sa.Column("weight_kg", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "weight_kg BETWEEN 20 AND 400", name=op.f("ck_weight_logs_weight_kg_range")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_weight_logs_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_weight_logs")),
        sa.UniqueConstraint("user_id", "logged_on", name=op.f("uq_weight_logs_user_id_logged_on")),
    )
    op.create_table(
        "meals",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "meal_type",
            sa.Enum("breakfast", "lunch", "dinner", "snack", name="meal_type"),
            nullable=False,
        ),
        sa.Column("eaten_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "source", sa.Enum("photo", "barcode", "manual", name="meal_source"), nullable=False
        ),
        sa.Column("photo_key", sa.String(length=512), nullable=True),
        sa.Column("ai_prediction_id", sa.Uuid(), nullable=True),
        sa.Column("is_favorite", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["ai_prediction_id"],
            ["ai_predictions.id"],
            name=op.f("fk_meals_ai_prediction_id_ai_predictions"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_meals_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_meals")),
    )
    op.create_index(op.f("ix_meals_ai_prediction_id"), "meals", ["ai_prediction_id"], unique=False)
    op.create_index("ix_meals_user_id_eaten_at", "meals", ["user_id", "eaten_at"], unique=False)
    op.create_table(
        "recipe_ingredients",
        sa.Column("recipe_id", sa.Uuid(), nullable=False),
        sa.Column("food_id", sa.Uuid(), nullable=False),
        sa.Column("quantity_g", sa.Numeric(precision=7, scale=2), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.CheckConstraint(
            "quantity_g > 0", name=op.f("ck_recipe_ingredients_quantity_g_positive")
        ),
        sa.ForeignKeyConstraint(
            ["food_id"],
            ["foods.id"],
            name=op.f("fk_recipe_ingredients_food_id_foods"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
            name=op.f("fk_recipe_ingredients_recipe_id_recipes"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_recipe_ingredients")),
    )
    op.create_index(
        op.f("ix_recipe_ingredients_food_id"), "recipe_ingredients", ["food_id"], unique=False
    )
    op.create_index(
        op.f("ix_recipe_ingredients_recipe_id"), "recipe_ingredients", ["recipe_id"], unique=False
    )
    op.create_table(
        "meal_items",
        sa.Column("meal_id", sa.Uuid(), nullable=False),
        sa.Column("food_id", sa.Uuid(), nullable=False),
        sa.Column("quantity_g", sa.Numeric(precision=7, scale=2), nullable=False),
        sa.Column("food_name", sa.String(length=255), nullable=False),
        sa.Column("kcal", sa.Numeric(precision=7, scale=2), nullable=False),
        sa.Column("protein_g", sa.Numeric(precision=7, scale=2), nullable=False),
        sa.Column("carbs_g", sa.Numeric(precision=7, scale=2), nullable=False),
        sa.Column("fat_g", sa.Numeric(precision=7, scale=2), nullable=False),
        sa.Column("ai_confidence", sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column("corrected", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.CheckConstraint(
            "ai_confidence BETWEEN 0 AND 1", name=op.f("ck_meal_items_ai_confidence_range")
        ),
        sa.CheckConstraint(
            "kcal >= 0 AND protein_g >= 0 AND carbs_g >= 0 AND fat_g >= 0",
            name=op.f("ck_meal_items_nutrients_positive"),
        ),
        sa.CheckConstraint(
            "quantity_g > 0 AND quantity_g <= 5000", name=op.f("ck_meal_items_quantity_g_range")
        ),
        sa.ForeignKeyConstraint(
            ["food_id"], ["foods.id"], name=op.f("fk_meal_items_food_id_foods"), ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["meal_id"], ["meals.id"], name=op.f("fk_meal_items_meal_id_meals"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_meal_items")),
    )
    op.create_index(op.f("ix_meal_items_food_id"), "meal_items", ["food_id"], unique=False)
    op.create_index(op.f("ix_meal_items_meal_id"), "meal_items", ["meal_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_meal_items_meal_id"), table_name="meal_items")
    op.drop_index(op.f("ix_meal_items_food_id"), table_name="meal_items")
    op.drop_table("meal_items")
    op.drop_index(op.f("ix_recipe_ingredients_recipe_id"), table_name="recipe_ingredients")
    op.drop_index(op.f("ix_recipe_ingredients_food_id"), table_name="recipe_ingredients")
    op.drop_table("recipe_ingredients")
    op.drop_index("ix_meals_user_id_eaten_at", table_name="meals")
    op.drop_index(op.f("ix_meals_ai_prediction_id"), table_name="meals")
    op.drop_table("meals")
    op.drop_table("weight_logs")
    op.drop_table("water_logs")
    op.drop_index(op.f("ix_subscriptions_user_id"), table_name="subscriptions")
    op.drop_table("subscriptions")
    op.drop_index(op.f("ix_recipes_author_id"), table_name="recipes")
    op.drop_table("recipes")
    op.drop_table("profiles")
    op.drop_index(op.f("ix_dietary_preferences_user_id"), table_name="dietary_preferences")
    op.drop_table("dietary_preferences")
    op.drop_index("ix_consents_user_id_consent_type_created_at", table_name="consents")
    op.drop_table("consents")
    op.drop_index(op.f("ix_ai_predictions_user_id"), table_name="ai_predictions")
    op.drop_table("ai_predictions")
    op.drop_index("uq_users_email_lower", table_name="users")
    op.drop_table("users")
    op.drop_index(
        "ix_foods_name_trgm",
        table_name="foods",
        postgresql_using="gin",
        postgresql_ops={"name": "gin_trgm_ops"},
    )
    op.drop_table("foods")

    # Alembic ne supprime pas les types ENUM avec les tables.
    for enum_name in ENUM_TYPES:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
    # Sans CASCADE : échoue volontairement si le schéma contient encore des objets.
    op.execute("DROP SCHEMA IF EXISTS analytics")
    # L'extension pg_trgm est laissée en place : d'autres bases ou schémas peuvent l'utiliser.
