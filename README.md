# Okta API Script

A Python package for calling Okta APIs using the requests module.

## Project Structure

```
okta/
├── src/
│   └── okta_api_script/
│       ├── __init__.py
│       ├── main.py          # Main API logic
│       └── cli.py           # Command line interface
├── tests/
│   ├── __init__.py
│   └── test_main.py         # Unit tests
├── pyproject.toml           # Project configuration
├── Makefile                 # Build automation
└── README.md               # This file
```

## Setup

1. Initialize the project:
   ```bash
   cp DOTENV .envrc
   # Modifiy .envrc with your environment variables
   direnv allow
   ```

   ```bash
   make init
   ```

2. Install development dependencies:
   ```bash
   make dev-install
   ```

3. Set your environment variables:
   ```bash
   export KEY_ID="your-key-id"
   export KEY_SECRET="your-key-secret"
   ```

4. Run the script:
   ```bash
   make run          # Run as Python module
   make run-cli      # Run via CLI entry point
   ```

## Environment Variables

- `KEY_ID`: Your Okta key ID
- `KEY_SECRET`: Your Okta key secret

## Available Make Targets

- `make init` - Initialize the project with uv
- `make run` - Run the API script as Python module
- `make run-cli` - Run the API script via CLI entry point
- `make test` - Run tests with pytest
- `make lint` - Run linting with flake8
- `make format` - Format code with black
- `make check` - Run type checking with mypy
- `make dev-install` - Install development dependencies
- `make clean` - Clean up generated files

## Package Features

- ✅ Proper Python package structure with src layout
- ✅ Environment variable configuration
- ✅ Error handling and validation
- ✅ Type hints and documentation
- ✅ Unit tests with pytest
- ✅ CLI entry point
- ✅ Development tools (black, flake8, mypy)
