# drf2go - developer entrypoint.
#
# Every Docker/Compose asset lives under .docker/. Because the compose files sit
# in a subdirectory but reference paths relative to the repository root, all
# invocations pass `--project-directory .`. Use these targets instead of raw
# `docker compose` so that never has to be remembered.
#
#   make            # this help
#   make up         # development stack
#   make prod-up    # production stack

.DEFAULT_GOAL := help
SHELL := /bin/sh

# --- configuration ----------------------------------------------------------

ENV_FILE      ?= .env
COMPOSE_DIR   := .docker
DEV_FILE      := $(COMPOSE_DIR)/compose.yaml
PROD_FILE     := $(COMPOSE_DIR)/compose.prod.yaml

COMPOSE       := docker compose --project-directory . --env-file $(ENV_FILE) -f $(DEV_FILE)
COMPOSE_PROD  := docker compose --project-directory . --env-file $(ENV_FILE) -f $(PROD_FILE)

# Run a one-off container rather than exec'ing into a running one, so targets
# such as `make lint` work on a cold checkout with no services running.
DEV_RUN       := $(COMPOSE) run --rm --no-deps \
                   -e WAIT_FOR_DB=false -e AUTO_MIGRATE=false
WEB_EXEC      := $(COMPOSE) exec web

# `make manage ARGS="createsuperuser"`, `make test ARGS="-k websocket"`, ...
ARGS          ?=
SERVICE       ?=

.PHONY: help
help: ## Show this help
	@printf '\033[1mdrf2go\033[0m - available targets\n\n'
	@awk 'BEGIN {FS = ":.*##"} \
		/^## / { printf "\n\033[1m%s\033[0m\n", substr($$0, 4); next } \
		/^[a-zA-Z0-9_-]+:.*##/ { printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@printf '\nOverride the env file with: make up ENV_FILE=.env.production\n\n'

## Setup

.PHONY: env
env: ## Create .env from .env.example if it does not exist yet
	@if [ -f $(ENV_FILE) ]; then \
		echo "$(ENV_FILE) already exists - leaving it untouched"; \
	else \
		cp .env.example $(ENV_FILE) && echo "created $(ENV_FILE) from .env.example"; \
	fi

.PHONY: install
install: ## Install runtime + dev dependencies into a local virtualenv (pipenv)
	pipenv sync --dev

.PHONY: lock
lock: ## Re-resolve Pipfile.lock from Pipfile
	pipenv lock

.PHONY: hooks
hooks: ## Install the pre-commit git hooks
	pipenv run pre-commit install

## Development stack

.PHONY: build
build: ## Build the development images
	$(COMPOSE) build

.PHONY: up
up: ## Build and start the development stack (foreground)
	$(COMPOSE) up --build

.PHONY: up-d
up-d: ## Build and start the development stack (detached)
	$(COMPOSE) up --build -d

.PHONY: down
down: ## Stop the development stack
	$(COMPOSE) down --remove-orphans

.PHONY: destroy
destroy: ## Stop the development stack and delete its volumes
	$(COMPOSE) down --remove-orphans --volumes

.PHONY: restart
restart: ## Restart the development stack
	$(COMPOSE) restart $(SERVICE)

.PHONY: ps
ps: ## Show development container status
	$(COMPOSE) ps

.PHONY: logs
logs: ## Tail development logs (make logs SERVICE=web)
	$(COMPOSE) logs -f --tail=100 $(SERVICE)

.PHONY: shell
shell: ## Open a Django shell in the running web container
	$(WEB_EXEC) python manage.py shell

.PHONY: sh
sh: ## Open a POSIX shell in the running web container
	$(WEB_EXEC) sh

## Django management

.PHONY: manage
manage: ## Run a management command: make manage ARGS="createsuperuser"
	$(WEB_EXEC) python manage.py $(ARGS)

.PHONY: migrate
migrate: ## Apply database migrations
	$(WEB_EXEC) python manage.py migrate

.PHONY: makemigrations
makemigrations: ## Create new migrations
	$(WEB_EXEC) python manage.py makemigrations $(ARGS)

.PHONY: superuser
superuser: ## Create a Django superuser
	$(WEB_EXEC) python manage.py createsuperuser

.PHONY: collectstatic
collectstatic: ## Collect static files
	$(WEB_EXEC) python manage.py collectstatic --noinput

.PHONY: check
check: ## Run Django system checks (deployment profile)
	$(WEB_EXEC) python manage.py check --deploy

## Quality

.PHONY: lint
lint: ## Lint with ruff
	$(DEV_RUN) web ruff check .

.PHONY: lint-fix
lint-fix: ## Lint and auto-fix with ruff
	$(DEV_RUN) web ruff check --fix .

.PHONY: format
format: ## Format with ruff
	$(DEV_RUN) web ruff format .

.PHONY: format-check
format-check: ## Verify formatting without writing changes
	$(DEV_RUN) web ruff format --check .

.PHONY: lint-all
lint-all: ## Run every pre-commit hook against the whole tree
	pipenv run pre-commit run --all-files

## Tests

# AUTO_MIGRATE is disabled here: pytest manages its own test database, so
# migrating the development database first would only slow the run down.
TEST_RUN := $(COMPOSE) run --rm -e AUTO_MIGRATE=false

.PHONY: test
test: ## Run the test suite: make test ARGS="-k websocket"
	$(TEST_RUN) web pytest $(ARGS)

.PHONY: test-cov
test-cov: ## Run the test suite with a coverage report
	$(TEST_RUN) web pytest --cov --cov-report=term-missing --cov-report=xml $(ARGS)

.PHONY: smoke
smoke: ## Exercise Celery and WebSockets against the running dev stack
	$(WEB_EXEC) python scripts/test_celery.py
	$(WEB_EXEC) python scripts/test_websocket.py --url ws://127.0.0.1:8000/ws/simple/

## Production stack

.PHONY: prod-build
prod-build: ## Build the production images
	$(COMPOSE_PROD) build

.PHONY: prod-up
prod-up: ## Build and start the production stack (detached)
	$(COMPOSE_PROD) up --build -d

.PHONY: prod-down
prod-down: ## Stop the production stack
	$(COMPOSE_PROD) down --remove-orphans

.PHONY: prod-destroy
prod-destroy: ## Stop the production stack and delete its volumes
	$(COMPOSE_PROD) down --remove-orphans --volumes

.PHONY: prod-ps
prod-ps: ## Show production container status
	$(COMPOSE_PROD) ps

.PHONY: prod-logs
prod-logs: ## Tail production logs (make prod-logs SERVICE=web)
	$(COMPOSE_PROD) logs -f --tail=100 $(SERVICE)

.PHONY: prod-manage
prod-manage: ## Run a management command in production: make prod-manage ARGS="migrate"
	$(COMPOSE_PROD) exec web python manage.py $(ARGS)

.PHONY: prod-superuser
prod-superuser: ## Create a Django superuser in production
	$(COMPOSE_PROD) exec web python manage.py createsuperuser

.PHONY: prod-config
prod-config: ## Render and validate the production compose file
	$(COMPOSE_PROD) config

## Housekeeping

.PHONY: clean
clean: ## Remove Python, test and coverage artefacts
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache .coverage coverage.xml htmlcov

.PHONY: prune
prune: ## Remove dangling Docker build cache and images
	docker system prune -f
