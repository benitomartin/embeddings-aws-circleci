# Makefile

.PHONY: help clean ruff

all: ruff mypy test clean

build-deploy: ## Build and deploy to AWS Lambda

	@echo "Starting build and deploy..."
	chmod +x ./scripts/build_deploy.sh
	@echo "Scripts made executable."

	@echo "Running build-deploy scripts..."
	./scripts/build_deploy.sh
	@echo "Build and deploy complete."

ruff: ## Run Ruff linter
	@echo "Running Ruff linter..."
	uv run ruff check . --fix --exit-non-zero-on-fix
	@echo "Ruff linter complete."

mypy: ## Run MyPy static type checker
	@echo "Running MyPy static type checker..."
	uv run mypy
	@echo "MyPy static type checker complete."

test: ## Run pytest tests
	@echo "Running pytest tests..."
	uv run pytest
	@echo "pytest tests complete."

clean: ## Clean up cached generated files
	@echo "Cleaning up generated files..."
	find . -type d \( -name "__pycache__" -o -name ".ruff_cache" -o -name ".pytest_cache" -o -name ".mypy_cache" \) -exec rm -rf {} +
	@echo "Cleanup complete."

help: ## Display this help message
	@echo "Default target: $(.DEFAULT_GOAL)"
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
