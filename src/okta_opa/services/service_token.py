from datetime import UTC, datetime
import os
from typing import Any, cast

import requests


def _get_api_config(
    org_name: str | None = None,
    team_name: str | None = None,
    key_id: str | None = None,
    key_secret: str | None = None,
) -> tuple[str, dict[str, str]]:
    org_name = org_name or os.getenv("OKTA_ORG")
    team_name = team_name or os.getenv("OKTA_TEAM")

    if not team_name or not org_name:
        raise ValueError("org_name and team_name variables must be set")

    key_id = key_id or os.getenv("KEY_ID")
    key_secret = key_secret or os.getenv("KEY_SECRET")
    if not key_id or not key_secret:
        raise ValueError("key_id and key_secret variables must be set")

    # Get bearer token (implement your token retrieval logic)
    bearer_token = get_service_token(
        org_name, team_name, key_id, key_secret
    )  # Placeholder for actual token retrieval method

    base_url = f"https://{org_name}.pam.okta.com/v1/teams/{team_name}/"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    return base_url, headers


def get_service_token(
    org_name: str, team_name: str, key_id: str, key_secret: str
) -> dict[str, Any]:
    """
    Get a service token from Okta API.

    Args:
        org_name: The organization name
        team_name: The team name
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

    data = response.json()

    now = datetime.now(UTC)
    expires_at = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))

    time_diff = expires_at - now
    seconds = int(time_diff.total_seconds())
    # print(f"Token expires in: {seconds} seconds")
    data["expires_in"] = seconds
    return cast(dict[str, Any], data)
