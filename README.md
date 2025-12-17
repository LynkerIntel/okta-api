# Okta API Script

A Python package for calling Okta APIs using the requests module.

This package has the following scripts defined by the `pyproject.toml` file:

- `okta-server-enrollment-token`: Generates a server enrollment token for a specified project within an Okta team.  This token can be used to enroll servers into Okta for identity and access management. 

## Project Structure

```
okta/
├── src
│   └── main/python
│   |    └── okta_api_script/
│   |       ├── __init__.py
│   |       ├── main.py          # Main API logic
│   |       └── cli.py           # Command line interface
│   └── test/python
│       ├── test/python
│       ├── __init__.py
│       └── test_main.py         # Unit tests
├── pyproject.toml           # Project configuration
├── justfile                 # Build automation
└── README.md               # This file
```

## Setup

0. This project is meant to be developed using `direnv` for environment variable management. Ensure you have `direnv` installed and configured in your shell, or that you are using the provided devcontainer setup.  You can also skip this step if you set those values previously or are using some other method to manage environment variables.

1. Initialize the project:
   ```bash
   cp DOTENV .envrc
   # Modifiy .envrc with your environment variables
   direnv allow
   ```

   ```bash
   just init
   ```

2. Install development dependencies:
   ```bash
   just dev-install
   ```

3. Set your environment variables:
   ```bash
   export KEY_ID="your-key-id"
   export KEY_SECRET="your-key-secret"
   ```

4. Run the script:
   ```bash
   just run          # Run as Python module
   just run-cli      # Run via CLI entry point
   ```

## Script Overview

The main script (`okta_api_script.main`) orchestrates the Okta API workflow:

1. **Authenticates** with Okta using service credentials to obtain a bearer token
2. **Retrieves** resource groups for your team
3. **Fetches** projects for each resource group
4. **Generates** a server enrollment token for your target project

### Usage

#### As a Python Module
```bash
just run
```

#### Programmatically
```python
from okta_api_script.main import execute_api_cycle

execute_api_cycle(
    org_name="your-org",
    team_name="your-team",
    target_project="your-project",
    key_id="your-key-id",
    key_secret="your-key-secret",
    output_json=False
)
```

## Script Parameters

The `execute_api_cycle()` function accepts the following parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_name` | `str \| None` | No | Okta organization name. If not provided, reads from `OKTA_ORG` environment variable |
| `team_name` | `str \| None` | No | Team name. If not provided, reads from `OKTA_TEAM` environment variable |
| `target_project` | `str \| None` | No | Target project name. If not provided, reads from `OKTA_TARGET_PROJECT` environment variable |
| `key_id` | `str \| None` | No | Okta API key ID. If not provided, reads from `KEY_ID` environment variable |
| `key_secret` | `str \| None` | No | Okta API key secret. If not provided, reads from `KEY_SECRET` environment variable |
| `output_json` | `bool` | No | If `True`, outputs full response as formatted JSON. If `False` (default), outputs only the enrollment token |

## Environment Variables

The following environment variables are used by the script:

- `OKTA_ORG`: Your Okta organization name (e.g., `noaa`)
- `OKTA_TEAM`: Your team name (e.g., `nos-coastal-modeling-cloud-sandbox`)
- `OKTA_TARGET_PROJECT`: Your target project name
- `KEY_ID`: Your Okta API key ID
- `KEY_SECRET`: Your Okta API key secret

All environment variables must be set for the script to run successfully. You can set them in:
- Your shell environment
- `.envrc` file (with `direnv`)
- Command line arguments to the `execute_api_cycle()` function

## Listing Available Just Targets

```bash
just --list
```
