import sys
from typing import Any, cast

import requests


def get_projects_by_team(
    bearer_token: str, org_name: str, team_name: str
) -> list[dict[str, Any]]:
    """
    Retrieve a list of projects for a given team using bearer token authentication.

    Args:
      bearer_token (str): The bearer token for authentication
      team_name (str): The name of the team to get projects for

    Returns:
      List[Dict[str, Any]]: A list of project dictionaries
    """
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    # Replace with actual API endpoint
    url = f"https://{org_name}.pam.okta.com/v1/teams/{team_name}/projects"

    try:
        # print(f"Fetching projects from URL: {url} with headers: {headers}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return cast(list[dict[str, Any]], response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error fetching projects: {e}", file=sys.stderr)
        return []
