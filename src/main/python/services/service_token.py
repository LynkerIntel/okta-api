from datetime import UTC, datetime
from typing import Any, cast

import requests


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
