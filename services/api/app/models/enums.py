"""Énumérations métier, stockées en types ENUM PostgreSQL (valeurs en minuscules)."""

import enum


class AuthProvider(enum.StrEnum):
    EMAIL = "email"
    APPLE = "apple"
    GOOGLE = "google"


class Sex(enum.StrEnum):
    FEMALE = "female"
    MALE = "male"


class ActivityLevel(enum.StrEnum):
    SEDENTARY = "sedentary"  # facteur 1,2
    LIGHT = "light"  # 1,375
    MODERATE = "moderate"  # 1,55
    ACTIVE = "active"  # 1,725
    VERY_ACTIVE = "very_active"  # 1,9


class GoalType(enum.StrEnum):
    LOSE_WEIGHT = "lose_weight"
    MAINTAIN = "maintain"
    GAIN_MUSCLE = "gain_muscle"
    REBALANCE = "rebalance"


class DietaryPreferenceKind(enum.StrEnum):
    DIET = "diet"  # végétarien, vegan, halal…
    ALLERGEN = "allergen"  # 14 allergènes réglementaires UE


class FoodSource(enum.StrEnum):
    CIQUAL = "ciqual"
    OPEN_FOOD_FACTS = "off"
    INTERNAL = "internal"


class MealType(enum.StrEnum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class MealSource(enum.StrEnum):
    PHOTO = "photo"
    BARCODE = "barcode"
    MANUAL = "manual"


class SubscriptionPlatform(enum.StrEnum):
    APP_STORE = "app_store"
    PLAY_STORE = "play_store"


class SubscriptionStatus(enum.StrEnum):
    TRIALING = "trialing"
    ACTIVE = "active"
    GRACE_PERIOD = "grace_period"
    BILLING_ISSUE = "billing_issue"
    CANCELLED = "cancelled"  # résilié, actif jusqu'à la fin de la période
    EXPIRED = "expired"


class PredictionStatus(enum.StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class ConsentType(enum.StrEnum):
    HEALTH_DATA = "health_data"  # obligatoire pour utiliser l'app
    AI_TRAINING = "ai_training"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
