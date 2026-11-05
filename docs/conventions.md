# Conventions du projet FoodAnalyser

Ce document fait foi pour tout le dépôt. Une PR qui ne les respecte pas est renvoyée en revue.

## 1. Branches (Git Flow simplifié)

| Branche | Rôle | Créée depuis | Fusionnée dans |
| --- | --- | --- | --- |
| `main` | Code en production, toujours déployable. Protégée. | — | — |
| `develop` | Intégration continue de la prochaine version. Protégée. | `main` | `main` (via `release/*`) |
| `feature/<n°issue>-<slug>` | Nouvelle fonctionnalité | `develop` | `develop` |
| `fix/<n°issue>-<slug>` | Correction d'un bug non urgent | `develop` | `develop` |
| `hotfix/<n°issue>-<slug>` | Correctif urgent en production | `main` | `main` **et** `develop` |
| `docs/<n°issue>-<slug>` | Documentation seule | `develop` | `develop` |
| `chore/<n°issue>-<slug>` | Outillage, CI, dépendances, config | `develop` | `develop` |
| `refacto/<n°issue>-<slug>` | Refactorisation sans changement fonctionnel | `develop` | `develop` |
| `test/<n°issue>-<slug>` | Ajout ou correction de tests | `develop` | `develop` |
| `release/<x.y.z>` | Stabilisation d'une version | `develop` | `main` + `develop` |

Règles :

- `<slug>` : kebab-case, en anglais, 2 à 5 mots, sans accents. Ex. : `feature/12-photo-meal-analysis`.
- Une branche = une issue. Pas de push direct sur `main` ni `develop`.
- Une branche fusionnée est supprimée.
- Versions au format [SemVer](https://semver.org/lang/fr/) : `MAJEUR.MINEUR.CORRECTIF`, tag `vX.Y.Z` sur `main`.

## 2. Messages de commit

Format :

```
[TAG] portée: description courte à l'impératif (#n°issue)

Corps facultatif : pourquoi le changement, pas comment.
```

- Le tag est **en majuscules entre crochets**, la portée en minuscules, la description en français, 72 caractères max sur la première ligne, sans point final.
- La référence à l'issue `(#12)` est obligatoire sauf pour `[MERGE]`.
- Un commit = un changement cohérent. Pas de « WIP » sur une branche partagée.

| Tag | Usage |
| --- | --- |
| `[ADD]` | Ajout d'une fonctionnalité, d'un fichier, d'un écran |
| `[UPDATE]` | Modification d'une fonctionnalité existante |
| `[FIX]` | Correction de bug |
| `[DEL]` | Suppression de code, de fichier, de dépendance |
| `[REFACTO]` | Restructuration sans changement de comportement |
| `[STYLE]` | Formatage, lint, nommage (aucun impact fonctionnel) |
| `[DOCS]` | Documentation |
| `[TEST]` | Ajout ou correction de tests |
| `[CONFIG]` | Configuration, CI/CD, Docker, outillage |
| `[DEPS]` | Mise à jour de dépendances |
| `[PERF]` | Amélioration de performance |
| `[SECU]` | Correctif ou durcissement de sécurité |
| `[MERGE]` | Commit de fusion |
| `[RELEASE]` | Préparation d'une version |

Portées autorisées : `mobile`, `backoffice`, `api`, `ai`, `db`, `infra`, `ci`, `docs`, `repo`. La portée est facultative pour `[MERGE]` et `[RELEASE]`.

Le hook `commit-msg` (`infra/scripts/check_commit_msg.py`) applique ces règles à chaque commit ; les messages générés par Git (`Merge branch…`, `Revert "…"`, `fixup!`) sont acceptés.

Exemples :

```
[ADD] api: endpoint POST /meals/analyze pour l'analyse photo (#14)
[FIX] mobile: jauge de calories négative après suppression d'un repas (#57)
[SECU] api: contrôle d'appartenance sur GET /meals/{id} (IDOR) (#31)
[CONFIG] ci: pipeline lint + tests pour services/api (#5)
[MERGE] develop dans main pour v0.2.0
```

## 3. Pull requests

- **Titre** : même format que le commit principal → `[ADD] mobile: écran de résultat d'analyse (#16)`.
- **Cible** : `develop` (sauf `hotfix/*` et `release/*` → `main`).
- **Description** : le modèle `.github/PULL_REQUEST_TEMPLATE.md` est obligatoire, avec `Closes #n°` pour fermer l'issue.
- **Taille** : viser moins de 400 lignes modifiées ; au-delà, découper.
- **Revue** : 1 approbation minimum ; l'auteur ne fusionne pas sans revue.
- **CI** : lint, tests, analyse statique et scan de dépendances doivent être verts.
- **Fusion** : *Squash and merge* vers `develop` (le message final respecte la norme de commit) ; *Merge commit* de `release/*` vers `main`.
- **Labels** : reprendre au minimum le `type:` et le `scope:` de l'issue.
- Brouillon (*draft*) tant que la PR n'est pas prête à être relue.

## 4. Issues

- Titre : `[Domaine] Verbe à l'infinitif + objet` → `[API] Créer l'endpoint d'analyse photo d'un repas`.
- Chaque issue porte : un label `type:`, un `scope:`, une `priority:`, une `size:`, un milestone, et la référence au cahier des charges (`F-xx`, `NFR-xx`).
- Sections obligatoires : Contexte, Objectif, Description, Tâches, Critères d'acceptation, Spécifications techniques, Fichiers concernés, Dépendances, Branche, Definition of Done.

## 5. Arborescence

Dossiers en **kebab-case**, en anglais.

```
foodanalyser/
├── apps/
│   ├── mobile/                 # React Native + TypeScript (iOS, Android)
│   │   └── src/
│   │       ├── api/            # clients HTTP générés / écrits
│   │       ├── components/     # composants réutilisables
│   │       ├── features/       # un dossier par fonctionnalité (meal-analysis, journal…)
│   │       ├── hooks/
│   │       ├── navigation/
│   │       ├── screens/
│   │       ├── store/          # état global
│   │       ├── theme/
│   │       ├── i18n/
│   │       └── utils/
│   └── backoffice/             # React + TypeScript (Vite)
│       └── src/ (même découpage)
├── services/
│   ├── api/                    # FastAPI
│   │   ├── app/
│   │   │   ├── api/v1/routes/  # un fichier par ressource
│   │   │   ├── core/           # config, sécurité, logs
│   │   │   ├── models/         # modèles SQLAlchemy
│   │   │   ├── schemas/        # schémas Pydantic
│   │   │   ├── services/       # logique métier
│   │   │   ├── repositories/   # accès aux données
│   │   │   └── workers/        # consommateurs RabbitMQ
│   │   ├── migrations/         # Alembic
│   │   └── tests/
│   └── ai/                     # entraînement + inférence
│       ├── training/
│       ├── inference/
│       ├── datasets/           # scripts uniquement, jamais les images
│       ├── models/             # configs Triton (poids hors Git)
│       └── tests/
├── infra/
│   ├── docker/
│   ├── k8s/
│   └── scripts/
├── docs/
│   ├── adr/                    # décisions d'architecture
│   ├── api/
│   ├── architecture/
│   └── security/
└── .github/
    ├── ISSUE_TEMPLATE/
    └── workflows/
```

## 6. Nommage des fichiers

| Contexte | Convention | Exemple |
| --- | --- | --- |
| Composant / écran React (Native) | PascalCase `.tsx` | `MealResultScreen.tsx`, `CalorieGauge.tsx` |
| Hook React | camelCase préfixé `use` | `useDailySummary.ts` |
| Autre module TS (utils, api, store) | camelCase `.ts` | `mealApi.ts`, `formatMacros.ts` |
| Test TS | même nom + `.test` | `CalorieGauge.test.tsx` |
| Module Python | snake_case `.py` | `meal_service.py`, `portion_estimator.py` |
| Test Python | préfixe `test_` | `test_meal_service.py` |
| Migration Alembic | `<révision>_<description_snake>.py` | `0003_add_weight_logs.py` |
| ADR | `NNNN-titre-kebab.md` | `0001-choix-react-native.md` |
| Workflow CI | kebab-case `.yml` | `api-ci.yml` |
| Dockerfile | `Dockerfile` ou `Dockerfile.<cible>` | `Dockerfile.worker` |
| Documentation | kebab-case `.md` | `guide-installation.md` |

## 7. Nommage dans le code

**Langue** : le code (variables, fonctions, classes, tables) est en **anglais** ; commentaires, docs et messages de commit en **français**.

| Élément | TypeScript | Python |
| --- | --- | --- |
| Variable, fonction | `camelCase` | `snake_case` |
| Classe, type, interface | `PascalCase` (pas de préfixe `I`) | `PascalCase` |
| Constante | `UPPER_SNAKE_CASE` | `UPPER_SNAKE_CASE` |
| Booléen | `is/has/can/should` + nom | `is_/has_/can_` + nom |
| Fonction asynchrone | verbe explicite (`fetchMeals`) | verbe explicite (`fetch_meals`) |
| Enum | `PascalCase`, membres `PascalCase` | `PascalCase`, membres `UPPER_SNAKE_CASE` |
| Privé | `#champ` ou pas d'export | préfixe `_` |

Base de données (PostgreSQL) :

- Tables en `snake_case` au pluriel : `users`, `meal_items`, `weight_logs`.
- Colonnes en `snake_case` ; clé primaire `id` (UUID v7) ; clé étrangère `<table_singulier>_id`.
- Horodatage `created_at`, `updated_at` en `timestamptz` UTC.
- Index `ix_<table>_<colonnes>`, contraintes uniques `uq_<table>_<colonnes>`.

API REST :

- Préfixe versionné `/api/v1`, ressources au pluriel en kebab-case : `/api/v1/meals`, `/api/v1/weight-logs`.
- Champs JSON en `snake_case`.
- Erreurs au format RFC 9457 (`application/problem+json`).

Variables d'environnement : `UPPER_SNAKE_CASE` préfixées par service (`API_DATABASE_URL`, `AI_MODEL_VERSION`). Jamais de secret commité : `.env.example` documente les clés.

## 8. Qualité

| Outil | TypeScript | Python |
| --- | --- | --- |
| Formatage | Prettier | Ruff format |
| Lint | ESLint | Ruff |
| Types | `strict: true` | mypy (strict sur `app/`) |
| Tests | Jest, Testing Library | pytest |
| Pre-commit | husky + lint-staged | pre-commit |

## 9. Labels

| Famille | Valeurs |
| --- | --- |
| `type:` | `feature`, `bug`, `docs`, `chore`, `security`, `test`, `design`, `research`, `epic` |
| `scope:` | `mobile`, `backoffice`, `api`, `ai`, `db`, `infra`, `ci`, `legal` |
| `priority:` | `must`, `should`, `could` (MoSCoW du cahier des charges) |
| `size:` | `XS` (< 2 h), `S` (½ j), `M` (1-2 j), `L` (3-5 j), `XL` (> 5 j, à découper) |
| `status:` | `blocked`, `needs-info`, `ready` |
| Divers | `good first issue`, `help wanted`, `duplicate`, `wontfix` |

## 10. Milestones

| Milestone | Contenu |
| --- | --- |
| `M1 - Cadrage et design` | Specs, maquettes, AIPD, socle technique, prototype IA |
| `M2 - MVP` | Fonctionnalités `must` : comptes, analyse photo, journal, abonnement, back-office |
| `M3 - Bêta fermée` | Fonctionnalités `should`, pentest, charge, accessibilité, bêta |
| `M4 - Lancement V1` | Publication stores, monitoring, conformité finale |
| `Backlog V2` | Fonctionnalités `could` |
