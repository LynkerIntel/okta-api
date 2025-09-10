"""Main module for Okta API interactions."""

import requests
import os
from typing import Any


def get_service_token(
    team_name: str, org_name: str, key_id: str, key_secret: str
) -> dict[str, Any]:
    """
    Get a service token from Okta API.

    Args:
        team_name: The team name
        org_name: The organization name
        key_id: The API key ID
        key_secret: The API key secret

    Returns:
        dict: The API response data
    """
    url = f"https://{org_name}.pam.okta.com/v1/teams/{team_name}/service_token"

    payload = {"key_id": key_id, "key_secret": key_secret}

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes

    return response.json()


def main() -> None:
    """Main entry point for the script."""
    team_name = "nos-coastal-modeling-cloud-sandbox-group"
    org_name = "noaa"

    # Get credentials from environment variables
    key_id = os.getenv("KEY_ID")
    key_secret = os.getenv("KEY_SECRET")

    if not key_id or not key_secret:
        raise ValueError("KEY_ID and KEY_SECRET environment variables must be set")

    try:
        data = get_service_token(team_name, org_name, key_id, key_secret)
        print(data)
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
    except ValueError as e:
        print(f"Configuration error: {e}")


if __name__ == "__main__":
    main()
