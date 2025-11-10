.PHONY: help install test run clean clean-exports lint format check

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies using uv
	uv sync

test: ## Run fast tests only (skips slow integration tests)
	uv run pytest -v

test-all: ## Run all tests including slow integration tests
	uv run pytest -v -m ""

test-slow: ## Run only slow integration tests
	uv run pytest -v -m slow

test-coverage: ## Run tests with coverage report
	uv run pytest --cov=github_branch_protection_checker --cov-report=html --cov-report=term

run: ## Run the branch protection checker
	uv run python -m github_branch_protection_checker

clean: ## Remove build artifacts, cache files, and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .venv/

clean-exports: ## Remove exported report files
	rm -f unprotected-repos-*.json
	rm -f unprotected-repos-*.csv
	rm -f unprotected-repos-*.md

lint: ## Run linting checks (requires ruff)
	@command -v ruff >/dev/null 2>&1 || (echo "Error: ruff not installed. Run: uv pip install ruff" && exit 1)
	uv run ruff check github_branch_protection_checker/ tests/

format: ## Format code with ruff (requires ruff)
	@command -v ruff >/dev/null 2>&1 || (echo "Error: ruff not installed. Run: uv pip install ruff" && exit 1)
	uv run ruff format github_branch_protection_checker/ tests/

check: test lint ## Run tests and linting

all: install test ## Install dependencies and run tests
