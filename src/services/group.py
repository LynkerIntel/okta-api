import os

import requests
from typing import Optional

from services.service_token import _get_api_config, get_service_token 


def delete_group_from_team(
  group_id: str,
  org_name: str | None = None,
  team_name: str | None = None,
  key_id: Optional[str] = None,
  key_secret: Optional[str] = None,
) -> bool:
  """
  Delete a group from the specified Okta team.
  
  Args:
    group_id: The ID of the group to delete
    org_name: Okta organization name
    team_name: Team identifier
  """
  base_url, headers = _get_api_config(org_name, team_name, key_id, key_secret)
  delete_url = f"{base_url}/groups/{group_id}"
  
  response = requests.delete(delete_url, headers=headers)
  
  if response.status_code == 204:
    print(f"Group {group_id} deleted successfully.")
    return True
  else:
    print(f"Failed to delete group {group_id}. Status code: {response.status_code}, Response: {response.text}")
  return False

def list_all_users_for_group(
  group_id: str,
  org_name: str | None = None,
  team_name: str | None = None,
  key_id: Optional[str] = None,
  key_secret: Optional[str] = None,
) -> list[dict]:
  """
  List all users in a group for the specified Okta team.
  
  Args:
    group_id: The ID of the group
    org_name: Okta organization name
    team_name: Team identifier
  Returns:
    List of user dictionaries
  """
  base_url, headers = _get_api_config(org_name, team_name, key_id, key_secret)
  users_url = f"{base_url}/groups/{group_id}/users"
  
  response = requests.get(users_url, headers=headers)
  response.raise_for_status()
  return response.json().get("list", [])

def add_or_remove_group_user(
  group_id: str,
  user_id: str,
  is_add: bool,
  org_name: str | None = None,
  team_name: str | None = None,
  key_id: Optional[str] = None,
  key_secret: Optional[str] = None,
) -> bool:
  """
  Add or remove a user from a group in the specified Okta team.
  
  Args:
    group_id: The ID of the group
    user_id: The ID of the user
    is_add: True to add the user, False to remove the user
    org_name: Okta organization name
    team_name: Team identifier
  """
  base_url, headers = _get_api_config(org_name, team_name, key_id, key_secret)
  add_url = f"{base_url}/groups/{group_id}/users/{user_id}"
  
  if is_add:
    response = requests.post(add_url, headers=headers)
  else:
    response = requests.delete(add_url, headers=headers)
  
  if response.status_code == 204:
    # print(f"User {user_id} added to group {group_id} successfully.")
    return True
  else:
    print(f"Failed to {'add' if is_add else 'remove'} user {user_id} {'to' if is_add else 'from'} group {group_id}. Status code: {response.status_code}, Response: {response.text}")
  return False


def get_roles_for_team(
  org_name: str | None = None,
  team_name: str | None = None,
  target_project: str | None = None,
  key_id: Optional[str] = None,
  key_secret: Optional[str] = None,
) -> list[str]:
  """
  Get a list of roles for the specified Okta team.
  
  Args:
    org_name: Okta organization name
    team_name: Team identifier
  Returns:
    List of role names
  """
  base_url, headers = _get_api_config(org_name, team_name, key_id, key_secret)
  roles_url = f"{base_url}/roles"
  response = requests.get(roles_url, headers=headers)
  response.raise_for_status()
  data = response.json()
  return [role["name"] for role in data.get("list", [])]

def get_groups_for_team(
  org_name: str | None = None,
  team_name: str | None = None,
  key_id: Optional[str] = None,
  key_secret: Optional[str] = None,
) -> list[dict]:
  """
  Get a list of groups for the specified Okta team.
  
  Args:
    org_name: Okta organization name
    team_name: Team identifier
  Returns:
    List of group dictionaries
  """
  base_url, headers = _get_api_config(org_name, team_name, key_id, key_secret)
  groups_url = f"{base_url}/groups"
  
  response = requests.get(groups_url, headers=headers)
  response.raise_for_status()
  return response.json().get("list", [])    

def create_or_read_group(
  group: str,
  org_name: str | None = None,
  team_name: str | None = None,
  key_id: Optional[str] = None,
  key_secret: Optional[str] = None,
  roles: Optional[list[str]] = None,
) -> dict:
  """
  Create or read a group in the specified Okta team.
  
  Args:
    group: Group name to create or read
    org_name: Okta organization name
    team_name: Team identifier
    roles: List of roles to assign to the group (optional)
  
  Returns:
    Dictionary containing group information
  """

  base_url, headers = _get_api_config(org_name, team_name, key_id, key_secret) 
    
  # Try to read existing group first
  group_url = f"{base_url}/groups/{group}"
  response = requests.get(group_url, headers=headers)
  
  if response.status_code == 200 and response.json():
    return response.json()[0]
  
  # Create new group if not found
  create_url = f"{base_url}/groups"
  payload = {
    "profile": {
      "name": group,
      "roles": roles or [],
    }
  }
  
  response = requests.post(create_url, headers=headers, json=payload)
  response.raise_for_status()
  
  return response.json()

