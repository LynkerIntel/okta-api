"""Tests for the group module."""

from unittest.mock import Mock, patch

import pytest
import requests

# These imports will work if services are in PYTHONPATH
# The test should be run from the project root with proper PYTHONPATH setup
try:
    from services.group import (
        add_or_remove_group_user,
        create_or_read_group,
        delete_group_from_team,
        get_groups_for_team,
        get_roles_for_team,
        list_all_users_for_group,
    )
except ImportError:
    # Fallback for when running tests from different directories
    from okta_api.services.group import (
        add_or_remove_group_user,
        create_or_read_group,
        delete_group_from_team,
        get_groups_for_team,
        get_roles_for_team,
        list_all_users_for_group,
    )


class TestDeleteGroupFromTeam:
    """Tests for delete_group_from_team function."""

    def test_delete_group_success(self):
        """Test successful group deletion."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.delete"
        ) as mock_delete:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.status_code = 204
            mock_delete.return_value = mock_response

            result = delete_group_from_team("group-123", "test-org", "test-team")

            assert result is True
            mock_delete.assert_called_once()
            args, kwargs = mock_delete.call_args
            assert "group-123" in args[0]

    def test_delete_group_with_credentials(self):
        """Test group deletion with explicit credentials."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.delete"
        ) as mock_delete:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.status_code = 204
            mock_delete.return_value = mock_response

            result = delete_group_from_team(
                "group-123",
                "test-org",
                "test-team",
                key_id="key-123",
                key_secret="secret-456",
            )

            assert result is True

    def test_delete_group_failure(self):
        """Test group deletion failure."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.delete"
        ) as mock_delete:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "Not found"
            mock_delete.return_value = mock_response

            result = delete_group_from_team("group-123", "test-org", "test-team")

            assert result is False


class TestListAllUsersForGroup:
    """Tests for list_all_users_for_group function."""

    def test_list_users_success(self):
        """Test successful user list retrieval."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.get"
        ) as mock_get:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.json.return_value = {
                "list": [
                    {"id": "user-1", "name": "User 1"},
                    {"id": "user-2", "name": "User 2"},
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = list_all_users_for_group("group-123", "test-org", "test-team")

            assert len(result) == 2
            assert result[0]["id"] == "user-1"
            assert result[1]["id"] == "user-2"

    def test_list_users_empty(self):
        """Test listing users when group has no users."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.get"
        ) as mock_get:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.json.return_value = {"list": []}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = list_all_users_for_group("group-123", "test-org", "test-team")

            assert result == []

    def test_list_users_no_list_key(self):
        """Test listing users when response has no list key."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.get"
        ) as mock_get:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.json.return_value = {}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = list_all_users_for_group("group-123", "test-org", "test-team")

            assert result == []

    def test_list_users_http_error(self):
        """Test listing users with HTTP error."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.get"
        ) as mock_get:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                "404 Not found"
            )
            mock_get.return_value = mock_response

            with pytest.raises(requests.exceptions.HTTPError):
                list_all_users_for_group("group-123", "test-org", "test-team")


class TestAddOrRemoveGroupUser:
    """Tests for add_or_remove_group_user function."""

    def test_add_user_success(self):
        """Test successful user addition to group."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.post"
        ) as mock_post:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.status_code = 204
            mock_post.return_value = mock_response

            result = add_or_remove_group_user(
                "group-123", "user-456", is_add=True, org_name="test-org", team_name="test-team"
            )

            assert result is True
            mock_post.assert_called_once()

    def test_remove_user_success(self):
        """Test successful user removal from group."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.delete"
        ) as mock_delete:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.status_code = 204
            mock_delete.return_value = mock_response

            result = add_or_remove_group_user(
                "group-123", "user-456", is_add=False, org_name="test-org", team_name="test-team"
            )

            assert result is True
            mock_delete.assert_called_once()

    def test_add_user_failure(self):
        """Test user addition failure."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.post"
        ) as mock_post:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.text = "Bad request"
            mock_post.return_value = mock_response

            result = add_or_remove_group_user(
                "group-123", "user-456", is_add=True, org_name="test-org", team_name="test-team"
            )

            assert result is False

    def test_remove_user_failure(self):
        """Test user removal failure."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.delete"
        ) as mock_delete:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "Not found"
            mock_delete.return_value = mock_response

            result = add_or_remove_group_user(
                "group-123", "user-456", is_add=False, org_name="test-org", team_name="test-team"
            )

            assert result is False


class TestGetRolesForTeam:
    """Tests for get_roles_for_team function."""

    def test_get_roles_success(self):
        """Test successful roles retrieval."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.get"
        ) as mock_get:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.json.return_value = {
                "list": [
                    {"name": "Role1", "id": "role-1"},
                    {"name": "Role2", "id": "role-2"},
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = get_roles_for_team("test-org", "test-team")

            assert len(result) == 2
            assert "Role1" in result
            assert "Role2" in result

    def test_get_roles_empty(self):
        """Test roles retrieval when no roles exist."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.get"
        ) as mock_get:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.json.return_value = {"list": []}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = get_roles_for_team("test-org", "test-team")

            assert result == []

    def test_get_roles_no_list_key(self):
        """Test roles retrieval when response has no list key."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.get"
        ) as mock_get:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.json.return_value = {}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = get_roles_for_team("test-org", "test-team")

            assert result == []

    def test_get_roles_http_error(self):
        """Test roles retrieval with HTTP error."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.get"
        ) as mock_get:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                "500 Server error"
            )
            mock_get.return_value = mock_response

            with pytest.raises(requests.exceptions.HTTPError):
                get_roles_for_team("test-org", "test-team")


class TestGetGroupsForTeam:
    """Tests for get_groups_for_team function."""

    def test_get_groups_success(self):
        """Test successful groups retrieval."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.get"
        ) as mock_get:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.json.return_value = {
                "list": [
                    {"id": "group-1", "name": "Group 1"},
                    {"id": "group-2", "name": "Group 2"},
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = get_groups_for_team("test-org", "test-team")

            assert len(result) == 2
            assert result[0]["id"] == "group-1"
            assert result[1]["id"] == "group-2"

    def test_get_groups_empty(self):
        """Test groups retrieval when no groups exist."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.get"
        ) as mock_get:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.json.return_value = {"list": []}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = get_groups_for_team("test-org", "test-team")

            assert result == []

    def test_get_groups_no_list_key(self):
        """Test groups retrieval when response has no list key."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.get"
        ) as mock_get:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.json.return_value = {}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = get_groups_for_team("test-org", "test-team")

            assert result == []

    def test_get_groups_http_error(self):
        """Test groups retrieval with HTTP error."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.get"
        ) as mock_get:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                "401 Unauthorized"
            )
            mock_get.return_value = mock_response

            with pytest.raises(requests.exceptions.HTTPError):
                get_groups_for_team("test-org", "test-team")


class TestCreateOrReadGroup:
    """Tests for create_or_read_group function."""

    def test_read_existing_group(self):
        """Test reading an existing group."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.get"
        ) as mock_get:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"id": "group-123", "name": "Test Group"}]
            mock_get.return_value = mock_response

            result = create_or_read_group(
                "Test Group", "test-org", "test-team"
            )

            assert result["id"] == "group-123"
            assert result["name"] == "Test Group"
            mock_get.assert_called_once()

    def test_create_new_group(self):
        """Test creating a new group when it doesn't exist."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.get"
        ) as mock_get, patch("services.group.requests.post") as mock_post:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            # First call for reading returns empty
            mock_get_response = Mock()
            mock_get_response.status_code = 200
            mock_get_response.json.return_value = []
            mock_get.return_value = mock_get_response

            # Post call for creation
            mock_post_response = Mock()
            mock_post_response.json.return_value = {"id": "group-new", "name": "New Group"}
            mock_post_response.raise_for_status.return_value = None
            mock_post.return_value = mock_post_response

            result = create_or_read_group(
                "New Group", "test-org", "test-team"
            )

            assert result["id"] == "group-new"
            assert result["name"] == "New Group"
            mock_get.assert_called_once()
            mock_post.assert_called_once()

    def test_create_group_with_roles(self):
        """Test creating a new group with roles."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.get"
        ) as mock_get, patch("services.group.requests.post") as mock_post:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            # First call for reading returns empty
            mock_get_response = Mock()
            mock_get_response.status_code = 200
            mock_get_response.json.return_value = []
            mock_get.return_value = mock_get_response

            # Post call for creation
            mock_post_response = Mock()
            mock_post_response.json.return_value = {
                "id": "group-new",
                "name": "New Group",
                "roles": ["admin", "user"],
            }
            mock_post_response.raise_for_status.return_value = None
            mock_post.return_value = mock_post_response

            result = create_or_read_group(
                "New Group", "test-org", "test-team", roles=["admin", "user"]
            )

            assert result["id"] == "group-new"
            assert "roles" in result
            # Verify the payload includes roles
            call_args = mock_post.call_args
            assert call_args[1]["json"]["profile"]["roles"] == ["admin", "user"]

    def test_create_group_with_credentials(self):
        """Test creating a group with explicit credentials."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.get"
        ) as mock_get, patch("services.group.requests.post") as mock_post:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            # First call for reading returns empty
            mock_get_response = Mock()
            mock_get_response.status_code = 200
            mock_get_response.json.return_value = []
            mock_get.return_value = mock_get_response

            # Post call for creation
            mock_post_response = Mock()
            mock_post_response.json.return_value = {"id": "group-new", "name": "New Group"}
            mock_post_response.raise_for_status.return_value = None
            mock_post.return_value = mock_post_response

            result = create_or_read_group(
                "New Group",
                "test-org",
                "test-team",
                key_id="key-123",
                key_secret="secret-456",
            )

            assert result["id"] == "group-new"

    def test_create_group_failure(self):
        """Test group creation failure."""
        with patch("services.group._get_api_config") as mock_config, patch(
            "services.group.requests.get"
        ) as mock_get, patch("services.group.requests.post") as mock_post:
            mock_config.return_value = (
                "https://test-org.pam.okta.com/v1/teams/test-team",
                {"Authorization": "Bearer token"},
            )
            # First call for reading returns empty
            mock_get_response = Mock()
            mock_get_response.status_code = 200
            mock_get_response.json.return_value = []
            mock_get.return_value = mock_get_response

            # Post call fails
            mock_post_response = Mock()
            mock_post_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                "400 Bad request"
            )
            mock_post.return_value = mock_post_response

            with pytest.raises(requests.exceptions.HTTPError):
                create_or_read_group("New Group", "test-org", "test-team")
