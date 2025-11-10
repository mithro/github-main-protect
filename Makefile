.PHONY: help install test run clean clean-exports lint format check type-check security ci-local

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

type-check: ## Run type checking with mypy
	uv run mypy github_branch_protection_checker/ --ignore-missing-imports

security: ## Run security checks (bandit, safety, gitleaks)
	@echo "Running bandit security scan..."
	uv run bandit -r github_branch_protection_checker/ -f screen || true
	@echo ""
	@echo "Running safety check..."
	uv pip freeze | uv run safety check --stdin || true
	@echo ""
	@echo "Running gitleaks (if installed)..."
	@command -v gitleaks >/dev/null 2>&1 && gitleaks detect --source . --verbose || echo "gitleaks not installed, skipping"

ci-local: ## Run all CI checks locally
	@echo "=== Running CI Checks Locally ==="
	@echo ""
	@echo "1. Linting..."
	@$(MAKE) lint
	@echo ""
	@echo "2. Format check..."
	uv run ruff format --check github_branch_protection_checker/ tests/
	@echo ""
	@echo "3. Type checking..."
	@$(MAKE) type-check || true
	@echo ""
	@echo "4. Fast tests..."
	@$(MAKE) test
	@echo ""
	@echo "5. Security checks..."
	@$(MAKE) security
	@echo ""
	@echo "=== All CI Checks Complete ==="

all: install test ## Install dependencies and run tests
