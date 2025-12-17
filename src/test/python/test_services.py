"""Tests for the services module."""

from unittest.mock import Mock, patch

import pytest
import requests

# These imports will work if services are in PYTHONPATH
# The test should be run from the project root with proper PYTHONPATH setup
try:
    from services.enrollment import generate_server_enrollment_token
    from services.projects import get_projects_by_team
    from services.resource_groups import (
        get_projects_by_resource_group,
        get_resource_groups_by_team,
    )
    from services.service_token import get_service_token
except ImportError:
    # Fallback for when running tests from different directories
    from okta_api_script.services.enrollment import generate_server_enrollment_token
    from okta_api_script.services.projects import get_projects_by_team
    from okta_api_script.services.resource_groups import (
        get_projects_by_resource_group,
        get_resource_groups_by_team,
    )
    from okta_api_script.services.service_token import get_service_token


class TestServiceToken:
    """Tests for service_token module."""

    def test_get_service_token_success(self):
        """Test successful service token retrieval."""
        with patch("services.service_token.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "bearer_token": "test-bearer-token",
                "expires_at": "2025-12-20T12:00:00Z",
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = get_service_token(
                "test-org", "test-team", "test-key", "test-secret"
            )

            assert result["bearer_token"] == "test-bearer-token"
            assert "expires_in" in result
            assert isinstance(result["expires_in"], int)
            mock_post.assert_called_once_with(
                "https://test-org.pam.okta.com/v1/teams/test-team/service_token",
                json={"key_id": "test-key", "key_secret": "test-secret"},
                headers={"Content-Type": "application/json"},
            )

    def test_get_service_token_failure(self):
        """Test service token retrieval with HTTP error."""
        with patch("services.service_token.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                "401 Unauthorized"
            )
            mock_post.return_value = mock_response

            with pytest.raises(requests.exceptions.HTTPError):
                get_service_token("test-org", "test-team", "bad-key", "bad-secret")

    def test_get_service_token_expires_in_calculation(self):
        """Test that expires_in is calculated correctly."""
        with patch("services.service_token.requests.post") as mock_post:
            mock_response = Mock()
            # Set expires_at to 1 hour in the future
            mock_response.json.return_value = {
                "bearer_token": "test-token",
                "expires_at": "2099-12-20T12:00:00Z",
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = get_service_token(
                "test-org", "test-team", "test-key", "test-secret"
            )

            # expires_in should be positive and large (years into the future)
            assert result["expires_in"] > 0
            assert result["expires_in"] > 86400  # More than a day


class TestResourceGroups:
    """Tests for resource_groups module."""

    def test_get_resource_groups_by_team_success(self):
        """Test successful resource groups retrieval."""
        with patch("services.resource_groups.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "list": [
                    {"id": "rg-1", "name": "Resource Group 1"},
                    {"id": "rg-2", "name": "Resource Group 2"},
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = get_resource_groups_by_team("test-token", "test-org", "test-team")

            assert len(result) == 2
            assert result[0]["id"] == "rg-1"
            assert result[1]["id"] == "rg-2"
            mock_get.assert_called_once_with(
                "https://test-org.pam.okta.com/v1/teams/test-team/resource_groups",
                headers={
                    "Authorization": "Bearer test-token",
                    "Content-Type": "application/json",
                },
            )

    def test_get_resource_groups_by_team_empty(self):
        """Test resource groups retrieval with empty list."""
        with patch("services.resource_groups.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"list": []}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = get_resource_groups_by_team("test-token", "test-org", "test-team")

            assert result == []

    def test_get_resource_groups_by_team_request_exception(self, capsys):
        """Test resource groups retrieval with request exception."""
        with patch("services.resource_groups.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException(
                "Connection error"
            )

            result = get_resource_groups_by_team("test-token", "test-org", "test-team")

            assert result == []
            captured = capsys.readouterr()
            assert "Error fetching resource groups" in captured.out

    def test_get_projects_by_resource_group_success(self):
        """Test successful projects retrieval by resource group."""
        with patch("services.resource_groups.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "list": [
                    {"id": "proj-1", "name": "Project 1", "deleted_at": None},
                    {"id": "proj-2", "name": "Project 2", "deleted_at": None},
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = get_projects_by_resource_group(
                "test-token", "test-org", "test-team", "rg-1"
            )

            assert len(result) == 2
            assert result[0]["id"] == "proj-1"
            assert result[1]["id"] == "proj-2"
            mock_get.assert_called_once_with(
                "https://test-org.pam.okta.com/v1/teams/test-team/resource_groups/rg-1/projects",
                headers={
                    "Authorization": "Bearer test-token",
                    "Content-Type": "application/json",
                },
            )

    def test_get_projects_by_resource_group_filters_deleted(self):
        """Test that deleted projects are filtered out."""
        with patch("services.resource_groups.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "list": [
                    {"id": "proj-1", "name": "Project 1", "deleted_at": None},
                    {
                        "id": "proj-2",
                        "name": "Project 2",
                        "deleted_at": "2025-12-01T00:00:00Z",
                    },
                    {"id": "proj-3", "name": "Project 3", "deleted_at": None},
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = get_projects_by_resource_group(
                "test-token", "test-org", "test-team", "rg-1"
            )

            # Only non-deleted projects should be returned
            assert len(result) == 2
            assert result[0]["id"] == "proj-1"
            assert result[1]["id"] == "proj-3"
            # Verify that only id and name are included
            assert "deleted_at" not in result[0]

    def test_get_projects_by_resource_group_empty(self):
        """Test projects retrieval with empty list."""
        with patch("services.resource_groups.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"list": []}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = get_projects_by_resource_group(
                "test-token", "test-org", "test-team", "rg-1"
            )

            assert result == []

    def test_get_projects_by_resource_group_request_exception(self, capsys):
        """Test projects retrieval with request exception."""
        with patch("services.resource_groups.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException(
                "Connection error"
            )

            result = get_projects_by_resource_group(
                "test-token", "test-org", "test-team", "rg-1"
            )

            assert result == []
            captured = capsys.readouterr()
            assert "Error fetching projects" in captured.err


class TestProjects:
    """Tests for projects module."""

    def test_get_projects_by_team_success(self):
        """Test successful projects retrieval by team."""
        with patch("services.projects.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = [
                {"id": "proj-1", "name": "Project 1"},
                {"id": "proj-2", "name": "Project 2"},
            ]
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = get_projects_by_team("test-token", "test-org", "test-team")

            assert len(result) == 2
            assert result[0]["id"] == "proj-1"
            assert result[1]["id"] == "proj-2"
            mock_get.assert_called_once_with(
                "https://test-org.pam.okta.com/v1/teams/test-team/projects",
                headers={
                    "Authorization": "Bearer test-token",
                    "Content-Type": "application/json",
                },
            )

    def test_get_projects_by_team_empty(self):
        """Test projects retrieval with empty list."""
        with patch("services.projects.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = []
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = get_projects_by_team("test-token", "test-org", "test-team")

            assert result == []

    def test_get_projects_by_team_request_exception(self, capsys):
        """Test projects retrieval with request exception."""
        with patch("services.projects.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException(
                "Connection error"
            )

            result = get_projects_by_team("test-token", "test-org", "test-team")

            assert result == []
            captured = capsys.readouterr()
            assert "Error fetching projects" in captured.err

    def test_get_projects_by_team_timeout(self, capsys):
        """Test projects retrieval with timeout."""
        with patch("services.projects.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timeout")

            result = get_projects_by_team("test-token", "test-org", "test-team")

            assert result == []
            captured = capsys.readouterr()
            assert "Error fetching projects" in captured.err


class TestEnrollment:
    """Tests for enrollment module."""

    def test_generate_server_enrollment_token_success(self):
        """Test successful enrollment token generation."""
        with patch("services.enrollment.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "token": "test-enrollment-token",
                "enrollment_token": "et-123",
                "created_at": "2025-12-17T10:00:00Z",
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = generate_server_enrollment_token(
                "test-team",
                "test-project",
                "test-org",
                "test-bearer",
                "rg-1",
                "proj-1",
            )

            assert result["token"] == "test-enrollment-token"
            assert result["enrollment_token"] == "et-123"
            mock_post.assert_called_once_with(
                "https://test-org.pam.okta.com/v1/teams/test-team/resource_groups/rg-1/projects/proj-1/server_enrollment_tokens",
                json={"description": "Generated by script"},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer test-bearer",
                },
            )

    def test_generate_server_enrollment_token_custom_description(self):
        """Test enrollment token generation with custom description."""
        with patch("services.enrollment.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "token": "test-enrollment-token",
                "enrollment_token": "et-123",
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = generate_server_enrollment_token(
                "test-team",
                "test-project",
                "test-org",
                "test-bearer",
                "rg-1",
                "proj-1",
                description="Custom description",
            )

            assert result["token"] == "test-enrollment-token"
            # Verify the custom description was sent
            call_args = mock_post.call_args
            assert call_args[1]["json"]["description"] == "Custom description"

    def test_generate_server_enrollment_token_failure(self):
        """Test enrollment token generation with HTTP error."""
        with patch("services.enrollment.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                "403 Forbidden"
            )
            mock_post.return_value = mock_response

            with pytest.raises(requests.exceptions.HTTPError):
                generate_server_enrollment_token(
                    "test-team",
                    "test-project",
                    "test-org",
                    "bad-bearer",
                    "rg-1",
                    "proj-1",
                )
