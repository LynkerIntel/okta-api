.PHONY: help init install sync run clean clean-venv test test-cov coverage lint format fix check check-config init-dev build

# Default target - show help
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s - %s\n", $$1, $$2}'

# Initialize project with uv
init: ## Initialize the project with uv (create venv and install dependencies)
	@echo "Initializing project with uv..."
	uv venv
	uv sync --extra dev
	@echo "Project initialized! Activate the virtual environment with: source .venv/bin/activate"

# Install dependencies
install: ## Install project dependencies using uv
	@echo "Installing dependencies..."
	uv add requests

# Sync all dependencies from pyproject.toml
sync: ## Sync dependencies from pyproject.toml
	@echo "Syncing dependencies from pyproject.toml..."
	uv sync

# Run the API script
run: ## Run the API script using uv
	@echo "Running API script..."
	uv run python -m src.main.python.okta_api_script.main

# Alternative: run using the CLI entry point
run-cli: ## Run the API script via CLI entry point
	@echo "Running API script via CLI..."
	uv run okta-script

# Install and run with development dependencies
init-dev: ## Initialize development environment
	@echo "Installing development dependencies..."
	uv sync --extra dev

# Run tests
test: ## Run tests using uv
	@echo "Running tests..."
	uv run pytest

# Run tests with coverage
test-cov: ## Run tests with coverage report (pytest-cov)
	@echo "Running tests with coverage..."
	uv run pytest --cov=src/main/python/okta_api_script --cov-report=html --cov-report=term

# Run coverage using coverage.py directly
coverage: ## Run coverage using coverage.py directly
	@echo "Running coverage with coverage.py..."
	uv run coverage run --source=src/main/python/okta_api_script -m pytest src/test/
	uv run coverage report
	uv run coverage html

# Run linting
lint: ## Lint code with ruff
	@echo "Running linting with ruff..."
	uv run ruff check src/main/python/ src/test/

# Format code
format: ## Format code with black
	@echo "Formatting code..."
	uv run black src/main/python/ src/test/

# Type checking
check: ## Run type checking with mypy
	@echo "Running type checking..."
	uv run mypy src/main/python/

# Fix code issues (ruff and black formatting)
fix: ## Fix code issues with ruff and black
	@echo "Fixing code with ruff and black..."
	uv run ruff check --fix src/main/python/ src/test/
	uv run black src/main/python/ src/test/

# Build distribution packages
build: init fix lint check test test-cov ## Build distribution packages for publication
	@echo "Building distribution packages..."
	uv build
	@echo "Build complete! Distribution packages are in the 'dist/' directory."

# Clean up
clean: ## Clean up generated files and cache
	@echo "Cleaning up..."
	@rm -rf __pycache__ .pytest_cache .mypy_cache htmlcov *.egg-info dist
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete

clean-venv: ## Remove virtual environment and fully reset workspace
	@echo "Removing virtual environment and fully resetting workspace..."
	@rm -rf .venv .coverage .flake8
	@rm -rf .uv
	@$(MAKE) clean
	@echo "Workspace reset complete. Run 'make init' to reinitialize."
