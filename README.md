# FoodAnalyser

Application mobile de suivi nutritionnel : on photographie son assiette, l'IA reconnaît les aliments, estime les portions et calcule calories et macronutriments. Inspirée de Foodvisor.

## Fonctionnalités visées (V1)

- Analyse d'un repas par photo (multi-aliments, estimation de portion)
- Scan de code-barres et recherche dans la base d'aliments (CIQUAL, Open Food Facts)
- Journal alimentaire, objectifs personnalisés, suivi du poids
- Abonnement premium, programmes et recettes
- Back-office de gestion de la base d'aliments et des contenus

## Stack

| Couche | Technologie |
| --- | --- |
| Mobile | React Native + TypeScript |
| Back-office | React + TypeScript (Vite) |
| API | Python FastAPI |
| IA | PyTorch, Triton Inference Server, MLflow |
| Données | PostgreSQL 16, Redis, RabbitMQ, stockage objet S3 |
| Infra | Docker, Kubernetes, GitHub Actions |

## Structure

```
apps/mobile        application iOS / Android
apps/backoffice    administration web
services/api       API REST FastAPI
services/ai        entraînement et inférence des modèles
infra/             Docker, Kubernetes, scripts
docs/              exigences, conventions, architecture, ADR
```

## Documentation

- [Référentiel des exigences](docs/exigences.md) — identifiants `F-xx` et `NFR-xx` cités dans les issues
- [Conventions](docs/conventions.md) — branches, commits, PR, nommage
- [Contribuer](CONTRIBUTING.md)

## Démarrage

Les instructions d'installation arrivent avec l'issue d'initialisation du socle technique (milestone *M1 - Cadrage et design*).
