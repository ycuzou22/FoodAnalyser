# services/api

API REST de FoodAnalyser (FastAPI, Python 3.12).

```bash
uv sync            # installe les dépendances (dont dev)
uv run ruff check .
uv run mypy
uv run pytest
```

## Base de données

```bash
uv run alembic upgrade head                                   # applique les migrations
uv run alembic revision --autogenerate --rev-id 0002 -m "..." # nouvelle migration, à relire
uv run alembic check                                          # modèles et migrations alignés ?
```

Tests d'intégration (base dédiée, **entièrement vidée** à chaque lancement) :

```bash
API_TEST_DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/foodanalyser_test \
  uv run pytest -m integration
```

Modèle de données : [docs/architecture/modele-donnees.md](../../docs/architecture/modele-donnees.md).
