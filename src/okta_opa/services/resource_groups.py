import sys
from typing import Any, cast

import requests


def get_resource_groups_by_team(
    bearer_token: str, org_name: str, team_name: str
) -> list[dict[str, Any]]:
    """
    Retrieve a list of resource groups for a given team using bearer token auth.

    Args:
      bearer_token (str): The bearer token for authentication
      team_name (str): The name of the team to get resource groups for

    Returns:
      List[Dict[str, Any]]: A list of project dictionaries
    """
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    # Replace with actual API endpoint
    url = f"https://{org_name}.pam.okta.com/v1/teams/{team_name}/resource_groups"

    try:
        # print(f"Fetching resource groups from URL: {url} with headers: {headers}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return cast(list[dict[str, Any]], response.json()["list"])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching resource groups: {e}")
        return []


def get_projects_by_resource_group(
    bearer_token: str, org_name: str, team_name: str, resource_group_id: str
) -> list[dict[str, Any]]:
    """
    Retrieve a list of projects for a resource group using bearer token auth.

    Args:
      bearer_token (str): The bearer token for authentication
      team_name (str): The name of the team to get projects for
      resource_group_id (str): The ID of the resource group to filter projects by

    Returns:
      List[Dict[str, Any]]: A list of project dictionaries
    """
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    # Replace with actual API endpoint
    url = f"https://{org_name}.pam.okta.com/v1/teams/{team_name}/resource_groups/{resource_group_id}/projects"

    try:
        # print(f"Fetching resourcegroups from URL: {url} with headers: {headers}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        list = response.json()["list"]
        # print(f"Projects in resource group {resource_group_id}: {list}")
        return [
            {"id": r["id"], "name": r["name"]} for r in list if r["deleted_at"] is None
        ]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching projects: {e}", file=sys.stderr)
        return []
