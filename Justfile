# Default recipe - show help
default:
    @just --list

# Initialize project with uv (create venv and install dependencies)
init:
    @echo "Initializing project with uv..."
    uv venv
    uv sync --extra dev
    @echo "Project initialized! Activate the virtual environment with: source .venv/bin/activate"

# Sync all dependencies from pyproject.toml
sync:
    @echo "Syncing dependencies from pyproject.toml..."
    uv sync

# Run the API script
run:
    @echo "Running API script..."
    uv run python -m src.main.python.okta_api_script.main

# Run the API script via CLI entry point
run-cli:
    @echo "Running API script via CLI..."
    uv run okta-script

# Initialize development environment
init-dev:
    @echo "Installing development dependencies..."
    uv sync --extra dev

# Run tests
test: 
    @echo "Running tests..."
    uv run pytest

# Run tests with coverage report
test-cov: 
    @echo "Running tests with coverage..."
    uv run pytest --cov=src/main/python/ --cov-report=html --cov-report=term

# Run coverage using coverage.py directly
coverage:
    @echo "Running coverage with coverage.py..."
    uv run coverage run --source=src/main/python/ -m pytest src/test/python
    uv run coverage report
    uv run coverage html

# Lint code with ruff
lint:
    @echo "Running linting with ruff..."
    uv run ruff check src/main/python/ src/test/

# Format code with black
format:
    @echo "Formatting code..."
    uv run black src/main/python/ src/test/python

# Run type checking with mypy
check:
    @echo "Running type checking..."
    uv run mypy src/main/python/

# Fix code issues with ruff and black
fix:
    @echo "Fixing code with ruff and black..."
    uv run ruff check --fix src/main/python/ src/test/python
    uv run black src/main/python/ src/test/python

# Build distribution packages for publication
build: init fix lint check test test-cov
    @echo "Building distribution packages..."
    uv build
    @echo "Build complete! Distribution packages are in the 'dist/' directory."

# Clean up generated files and cache
clean:
    @echo "Cleaning up..."
    rm -rf __pycache__ .pytest_cache .mypy_cache htmlcov *.egg-info dist .ruff_cache
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -delete


# Remove virtual environment and fully reset workspace
clean-venv: clean
    @echo "Removing virtual environment and fully resetting workspace..."
    rm -rf .venv .coverage .flake8 .uv
    @echo "Workspace reset complete. Run 'just init' to reinitialize."
