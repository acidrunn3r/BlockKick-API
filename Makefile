.PHONY: help up down logs restart lint format shell migrate test bump

rule ?= patch

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

restart:
	docker compose restart api

build:
	docker compose build --no-cache

shell:
	docker compose exec api bash

migrate:
	docker compose exec api alembic upgrade head

makemigrations:
	docker compose exec api alembic revision --autogenerate -m "$(MSG)"

# Dev
install:
	poetry install --with dev

lint:
	poetry run ruff check app/
	poetry run black --check app/

format:
	poetry run black app/
	poetry run ruff check --fix app/

test:
	poetry run pytest

bump: ## Bump version (rule=patch|minor|major)
	poetry version $(rule)
	git add pyproject.toml
	git commit -m "bump: v$$(poetry version -s)"
	git tag v$$(poetry version -s)
