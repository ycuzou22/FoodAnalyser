"""Fabriques de données de test. Données entièrement fictives (aucune donnée réelle)."""

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from app.db.ids import uuid7
from app.models import (
    AiPrediction,
    Consent,
    DietaryPreference,
    Food,
    Meal,
    MealItem,
    Profile,
    Subscription,
    User,
    WaterLog,
    WeightLog,
)
from app.models.enums import (
    ActivityLevel,
    AuthProvider,
    ConsentType,
    DietaryPreferenceKind,
    FoodSource,
    GoalType,
    MealSource,
    MealType,
    PredictionStatus,
    Sex,
    SubscriptionPlatform,
    SubscriptionStatus,
)


def make_user(**overrides: Any) -> User:
    values: dict[str, Any] = {
        "email": f"test-{uuid7().hex[-12:]}@example.test",
        "auth_provider": AuthProvider.EMAIL,
        "password_hash": "$argon2id$v=19$fictif",
    }
    values.update(overrides)
    return User(**values)


def make_profile(user: User, **overrides: Any) -> Profile:
    values: dict[str, Any] = {
        "user": user,
        "sex": Sex.FEMALE,
        "birth_date": date(1996, 4, 12),
        "height_cm": Decimal("165.0"),
        "activity_level": ActivityLevel.LIGHT,
        "goal_type": GoalType.MAINTAIN,
        "kcal_target": 1900,
        "protein_g_target": 100,
        "carbs_g_target": 230,
        "fat_g_target": 63,
    }
    values.update(overrides)
    return Profile(**values)


def make_food(**overrides: Any) -> Food:
    values: dict[str, Any] = {
        "name": "Yaourt nature",
        "source": FoodSource.CIQUAL,
        "ciqual_code": uuid7().hex[-8:],  # partie aléatoire (le début est l'horodatage)
        "kcal_100g": Decimal("61"),
        "protein_100g": Decimal("4.3"),
        "carbs_100g": Decimal("5.0"),
        "fat_100g": Decimal("2.5"),
        "nutriscore": "a",
    }
    values.update(overrides)
    return Food(**values)


def make_meal(user: User, food: Food, quantity_g: str = "125", **overrides: Any) -> Meal:
    quantity = Decimal(quantity_g)
    ratio = quantity / 100
    item = MealItem(
        food=food,
        quantity_g=quantity,
        food_name=food.name,
        kcal=food.kcal_100g * ratio,
        protein_g=food.protein_100g * ratio,
        carbs_g=food.carbs_100g * ratio,
        fat_g=food.fat_100g * ratio,
    )
    values: dict[str, Any] = {
        "user": user,
        "meal_type": MealType.BREAKFAST,
        "eaten_at": datetime(2026, 11, 5, 7, 30, tzinfo=UTC),
        "source": MealSource.MANUAL,
        "items": [item],
    }
    values.update(overrides)
    return Meal(**values)


def make_full_user_graph(food: Food) -> tuple[User, list[object]]:
    """Un utilisateur avec une ligne dans chaque table qui le référence."""
    user = make_user()
    prediction = AiPrediction(
        user=user,
        image_key=f"raw/{user.id}/photo.jpg",
        model_version="test-0",
        status=PredictionStatus.COMPLETED,
        predictions={"items": []},
    )
    meal = make_meal(user, food, source=MealSource.PHOTO)
    meal.ai_prediction = prediction
    related: list[object] = [
        make_profile(user),
        DietaryPreference(user=user, kind=DietaryPreferenceKind.ALLERGEN, value="peanuts"),
        prediction,
        meal,
        WeightLog(user=user, logged_on=date(2026, 11, 5), weight_kg=Decimal("64.5")),
        WaterLog(user=user, logged_on=date(2026, 11, 5), volume_ml=1500),
        Subscription(
            user=user,
            platform=SubscriptionPlatform.APP_STORE,
            product_id="premium_monthly",
            original_transaction_id=f"txn-{uuid7().hex}",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=datetime(2026, 12, 5, tzinfo=UTC),
        ),
        Consent(
            user=user,
            consent_type=ConsentType.HEALTH_DATA,
            granted=True,
            version="2026-11",
            source="onboarding",
        ),
    ]
    return user, related
