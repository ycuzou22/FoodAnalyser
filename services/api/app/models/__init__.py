"""Modèles SQLAlchemy. Les importer tous ici les enregistre dans `Base.metadata` (Alembic)."""

from app.models.food import Food, Recipe, RecipeIngredient
from app.models.food_source import FoodSourceImport
from app.models.meal import AiPrediction, Meal, MealItem
from app.models.tracking import Consent, Subscription, WaterLog, WeightLog
from app.models.user import DietaryPreference, Profile, User

__all__ = [
    "AiPrediction",
    "Consent",
    "DietaryPreference",
    "Food",
    "FoodSourceImport",
    "Meal",
    "MealItem",
    "Profile",
    "Recipe",
    "RecipeIngredient",
    "Subscription",
    "User",
    "WaterLog",
    "WeightLog",
]
