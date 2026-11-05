# Commandes du monorepo FoodAnalyser. `make help` liste les cibles.
# Sous Windows : utiliser Git Bash (make fourni par Git for Windows / Chocolatey), ou lancer les commandes affichées à la main.

PY_SERVICES := services/api services/ai
COMPOSE_ENV := infra/docker/.env
COMPOSE := docker compose -f infra/docker/compose.dev.yml --env-file $(COMPOSE_ENV)

.DEFAULT_GOAL := help
.PHONY: help install lint format test up down logs ps reset-db check-env

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Installe les dépendances JS et Python et les hooks Git
	pnpm install
	@for s in $(PY_SERVICES); do echo "→ uv sync $$s"; (cd $$s && uv sync) || exit 1; done
	uvx pre-commit install --install-hooks

lint: ## Vérifie format, lint et typage sur tout le dépôt
	pnpm lint
	@for s in $(PY_SERVICES); do echo "→ lint $$s"; (cd $$s && uv run ruff check . && uv run ruff format --check . && uv run mypy) || exit 1; done
	python3 -m unittest discover -s infra/scripts -q

format: ## Reformate tout le dépôt
	pnpm format
	@for s in $(PY_SERVICES); do (cd $$s && uv run ruff check --fix . && uv run ruff format .) || exit 1; done

test: ## Lance tous les tests
	pnpm test
	@for s in $(PY_SERVICES); do echo "→ tests $$s"; (cd $$s && uv run pytest) || exit 1; done
	python3 -m unittest discover -s infra/scripts -q

# --- Environnement Docker de développement -----------------------------------

check-env:
	@test -f $(COMPOSE_ENV) || { echo "✗ $(COMPOSE_ENV) manquant : cp infra/docker/.env.example $(COMPOSE_ENV)"; exit 1; }

up: check-env ## Démarre PostgreSQL, Redis, RabbitMQ, MinIO et l'API (http://localhost:8000)
	$(COMPOSE) up -d --build --wait
	@echo "✔ API : http://localhost:8000/docs · RabbitMQ : http://localhost:15672 · MinIO : http://localhost:9001"

down: check-env ## Arrête l'environnement (les données sont conservées)
	$(COMPOSE) down

logs: check-env ## Suit les logs (make logs s=api pour un seul service)
	$(COMPOSE) logs -f $(s)

ps: check-env ## État des conteneurs
	$(COMPOSE) ps

reset-db: check-env ## Repart d'une base PostgreSQL vide
	$(COMPOSE) stop api postgres
	$(COMPOSE) rm -f postgres
	docker volume rm -f foodanalyser_pg-data
	$(COMPOSE) up -d --wait postgres api
