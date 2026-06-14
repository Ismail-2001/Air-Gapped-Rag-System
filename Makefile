.PHONY: build up down logs test test-all test-auth test-audit lint lint-ruff lint-mypy \
        lint-bandit clean-docs clean clean-all shell-app shell-ollama backup secrets

# ── Docker Orchestration ──
build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

restart:
	docker compose restart

# ── Testing ──
test:
	docker compose run --rm app python -m pytest tests/ -v -m "not slow"

test-all:
	docker compose run --rm app python -m pytest tests/ -v --tb=long

test-auth:
	docker compose run --rm app python -m pytest tests/test_auth.py -v

test-audit:
	docker compose run --rm app python -m pytest tests/test_audit.py -v

test-coverage:
	docker compose run --rm app python -m pytest tests/ --cov=app --cov-report=term --cov-report=html

# ── Code Quality ──
lint-ruff:
	ruff check app/ tests/

lint-ruff-fix:
	ruff check --fix app/ tests/

lint-format:
	ruff format --check app/ tests/

lint-format-fix:
	ruff format app/ tests/

lint-mypy:
	mypy app/ --strict --ignore-missing-imports

lint-bandit:
	bandit -r app/ -ll -c pyproject.toml

lint: lint-ruff lint-format lint-mypy lint-bandit

# ── Maintenance ──
clean-docs:
	rm -rf documents/*.pdf

clean-pyc:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

clean: clean-pyc

clean-all: clean
	rm -rf chroma_data/*
	rm -rf audit_logs/*
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

# ── Operations ──
shell-app:
	docker exec -it fortaleza-app /bin/bash || docker compose exec app /bin/bash

shell-ollama:
	docker exec -it fortaleza-ollama /bin/bash || docker compose exec ollama /bin/bash

backup:
	@echo "Run: bash scripts/backup.sh"

secrets:
	@echo "Run: bash scripts/generate_secrets.sh"

# ── Quality Gate (CI entry point) ──
quality-gate: lint test-all
	@echo "[FORTALEZA] Quality gate passed."
