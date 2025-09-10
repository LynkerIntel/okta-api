.PHONY: help init install sync run clean test lint format check

# Default target
help:
	@echo "Available targets:"
	@echo "  init       - Initialize the project with uv (create venv and install dependencies)"
	@echo "  install    - Install project dependencies using uv"
	@echo "  sync       - Sync dependencies from pyproject.toml"
	@echo "  run        - Run the API script using uv"
	@echo "  run-cli    - Run the API script via CLI entry point"
	@echo "  test       - Run tests using uv"
	@echo "  lint       - Run linting with flake8"
	@echo "  format     - Format code with black"
	@echo "  check      - Run type checking with mypy"
	@echo "  dev-install - Install development dependencies"
	@echo "  clean      - Clean up generated files and cache"

# Initialize project with uv
init:
	@echo "Initializing project with uv..."
	uv venv
	uv sync
	@echo "Project initialized! Activate the virtual environment with: source .venv/bin/activate"

# Install dependencies
install:
	@echo "Installing dependencies..."
	uv add requests

# Sync all dependencies from pyproject.toml
sync:
	@echo "Syncing dependencies from pyproject.toml..."
	uv sync

# Run the API script
run:
	@echo "Running API script..."
	uv run python -m okta_api_script.main

# Alternative: run using the CLI entry point
run-cli:
	@echo "Running API script via CLI..."
	uv run okta-script

# Install and run with development dependencies
dev-install:
	@echo "Installing development dependencies..."
	uv sync --extra dev

# Run tests
test:
	@echo "Running tests..."
	uv run pytest

# Run linting
lint:
	@echo "Running linting..."
	uv run flake8 src/ tests/

# Format code
format:
	@echo "Formatting code..."
	uv run black src/ tests/

# Type checking
check:
	@echo "Running type checking..."
	uv run mypy src/

# Clean up
clean:
	@echo "Cleaning up..."
	rm -rf .venv
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf *.egg-info
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
