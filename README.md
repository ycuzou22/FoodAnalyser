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

### Prérequis

| Outil | Version | Installation |
| --- | --- | --- |
| Node.js | 20 LTS ou plus | [nodejs.org](https://nodejs.org/) |
| pnpm | 10 | `corepack enable` |
| Python | 3.12 ou plus | [python.org](https://www.python.org/) |
| uv | dernière | `pip install uv` ou [docs.astral.sh/uv](https://docs.astral.sh/uv/) |
| Go | 1.22 ou plus | requis une fois par pre-commit pour construire gitleaks |
| make | — | inclus sous Linux / macOS ; sous Windows, utiliser Git Bash |

### Installation

```bash
git clone https://github.com/ycuzou22/FoodAnalyser.git
cd FoodAnalyser
make install      # dépendances JS + Python + hooks Git
```

### Commandes courantes

| Commande | Effet |
| --- | --- |
| `make lint` | Prettier, ESLint, Ruff, mypy, tests du vérificateur de commits |
| `make format` | Reformate tout le dépôt |
| `make test` | Tous les tests |

### Hooks Git

À chaque commit, les hooks reformatent le code (Ruff, Prettier), cherchent des secrets (gitleaks, clés privées) et vérifient le message au format `[TAG] portée: description (#n°)`. Un message non conforme est refusé avec l'explication du format attendu.

Copier chaque `.env.example` en `.env` avant de lancer un service.
