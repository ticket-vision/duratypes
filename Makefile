# Makefile for duratypes development tasks
# Requires: uv (for dependency management)

.PHONY: help install install-dev clean test test-cov lint format type-check security pre-commit build docs serve-docs

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation targets
install: ## Install the package in production mode
	uv pip install .

install-dev: ## Install the package in development mode with all dependencies
	uv sync --all-extras --dev
	uv pip install -e .

# Cleaning targets
clean: ## Clean up build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Testing targets
test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage report
	uv run pytest --cov=duratypes --cov-report=term-missing --cov-report=html --cov-report=xml

test-fast: ## Run tests without coverage (faster)
	uv run pytest --no-cov

test-verbose: ## Run tests with verbose output
	uv run pytest -v

test-performance: ## Run only performance benchmark tests
	uv run pytest tests/test_core.py::TestPerformanceBenchmarks -v

test-thread-safety: ## Run only thread safety tests
	uv run pytest tests/test_core.py::TestThreadSafety -v

# Code quality targets
lint: ## Run linting with ruff
	uv run ruff check .

lint-fix: ## Run linting with automatic fixes
	uv run ruff check --fix .

format: ## Format code with ruff
	uv run ruff format .

format-check: ## Check code formatting without making changes
	uv run ruff format --check .

type-check: ## Run type checking with mypy
	uv run mypy src/duratypes

# Security targets
security: ## Run security checks
	uv run bandit -r src/duratypes -f json -o bandit-report.json || true
	uv run bandit -r src/duratypes

# Pre-commit targets
pre-commit-install: ## Install pre-commit hooks
	uv run pre-commit install

pre-commit-run: ## Run pre-commit hooks on all files
	uv run pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	uv run pre-commit autoupdate

# Build targets
build: clean ## Build the package
	uv build

build-wheel: clean ## Build wheel only
	uv build --wheel

build-sdist: clean ## Build source distribution only
	uv build --sdist

# Development workflow targets
dev-setup: install-dev pre-commit-install ## Complete development environment setup
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify everything works."

check: lint type-check test ## Run all quality checks (lint, type-check, test)

check-fast: lint type-check test-fast ## Run quality checks without coverage (faster)

ci: lint format-check type-check test-cov ## Run all CI checks

# Documentation targets (placeholder for future)
docs: ## Build documentation (placeholder)
	@echo "Documentation building not yet implemented"

serve-docs: ## Serve documentation locally (placeholder)
	@echo "Documentation serving not yet implemented"

# Release targets (placeholder for future)
release-check: ## Check if ready for release
	@echo "Checking release readiness..."
	@make clean
	@make check
	@make build
	@echo "Release check complete!"

# Utility targets
show-deps: ## Show current dependencies
	uv tree

show-outdated: ## Show outdated dependencies
	uv pip list --outdated

update-deps: ## Update dependencies
	uv sync --upgrade

# Environment info
info: ## Show environment information
	@echo "Python version:"
	@python --version
	@echo "\nUV version:"
	@uv --version
	@echo "\nProject info:"
	@uv pip show duratypes || echo "Package not installed"
