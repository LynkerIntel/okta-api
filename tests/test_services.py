"""Tests for the services module."""

from unittest.mock import Mock, patch

import pytest
import requests

# These imports will work if services are in PYTHONPATH
# The test should be run from the project root with proper PYTHONPATH setup
try:
    from okta_opa.services.enrollment import generate_server_enrollment_token
    from okta_opa.services.projects import get_projects_by_team
    from okta_opa.services.resource_groups import (
        get_projects_by_resource_group,
        get_resource_groups_by_team,
    )
    from okta_opa.services.service_token import get_service_token, _get_api_config
except ImportError:
    # Fallback for when running tests from different directories
    from okta_opa.services.enrollment import generate_server_enrollment_token
    from okta_opa.services.projects import get_projects_by_team
    from okta_opa.services.resource_groups import (
        get_projects_by_resource_group,
        get_resource_groups_by_team,
    )
    from okta_opa.services.service_token import get_service_token, _get_api_config


class TestServiceToken:
    """Tests for service_token module."""

    def test_get_service_token_success(self):
        """Test successful service token retrieval."""
        with patch("okta_opa.services.service_token.requests.post") as mock_post:
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
        with patch("okta_opa.services.service_token.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                "401 Unauthorized"
            )
            mock_post.return_value = mock_response

            with pytest.raises(requests.exceptions.HTTPError):
                get_service_token("test-org", "test-team", "bad-key", "bad-secret")

    def test_get_service_token_expires_in_calculation(self):
        """Test that expires_in is calculated correctly."""
        with patch("okta_opa.services.service_token.requests.post") as mock_post:
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


class TestGetApiConfig:
    """Tests for _get_api_config function."""

    def test_get_api_config_with_explicit_params(self):
        """Test _get_api_config with explicit parameters."""
        with patch("okta_opa.services.service_token.get_service_token") as mock_token:
            mock_token.return_value = "test-token"

            base_url, headers = _get_api_config(
                "test-org", "test-team", "test-key", "test-secret"
            )

            assert base_url == "https://test-org.pam.okta.com/v1/teams/test-team/"
            assert headers["Authorization"] == "Bearer test-token"
            assert headers["Content-Type"] == "application/json"
            mock_token.assert_called_once_with(
                "test-org", "test-team", "test-key", "test-secret"
            )

    def test_get_api_config_with_env_vars(self):
        """Test _get_api_config using environment variables."""
        with (
            patch.dict(
                "os.environ",
                {
                    "OKTA_ORG": "env-org",
                    "OKTA_TEAM": "env-team",
                    "KEY_ID": "env-key",
                    "KEY_SECRET": "env-secret",
                },
            ),
            patch("okta_opa.services.service_token.get_service_token") as mock_token,
        ):
            mock_token.return_value = "env-token"

            base_url, headers = _get_api_config()

            assert base_url == "https://env-org.pam.okta.com/v1/teams/env-team/"
            assert headers["Authorization"] == "Bearer env-token"
            mock_token.assert_called_once_with(
                "env-org", "env-team", "env-key", "env-secret"
            )

    def test_get_api_config_missing_org_name(self):
        """Test _get_api_config raises error when org_name is missing."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(
                ValueError, match="org_name and team_name variables must be set"
            ):
                _get_api_config()

    def test_get_api_config_missing_team_name(self):
        """Test _get_api_config raises error when team_name is missing."""
        with patch.dict("os.environ", {"OKTA_ORG": "test-org"}, clear=True):
            with pytest.raises(
                ValueError, match="org_name and team_name variables must be set"
            ):
                _get_api_config()

    def test_get_api_config_missing_key_id(self):
        """Test _get_api_config raises error when key_id is missing."""
        with patch.dict(
            "os.environ",
            {"OKTA_ORG": "test-org", "OKTA_TEAM": "test-team"},
            clear=True,
        ):
            with pytest.raises(
                ValueError, match="key_id and key_secret variables must be set"
            ):
                _get_api_config()

    def test_get_api_config_missing_key_secret(self):
        """Test _get_api_config raises error when key_secret is missing."""
        with patch.dict(
            "os.environ",
            {
                "OKTA_ORG": "test-org",
                "OKTA_TEAM": "test-team",
                "KEY_ID": "test-key",
            },
            clear=True,
        ):
            with pytest.raises(
                ValueError, match="key_id and key_secret variables must be set"
            ):
                _get_api_config()

    def test_get_api_config_explicit_params_override_env(self):
        """Test that explicit parameters override environment variables."""
        with (
            patch.dict(
                "os.environ",
                {
                    "OKTA_ORG": "env-org",
                    "OKTA_TEAM": "env-team",
                    "KEY_ID": "env-key",
                    "KEY_SECRET": "env-secret",
                },
            ),
            patch("okta_opa.services.service_token.get_service_token") as mock_token,
        ):
            mock_token.return_value = "explicit-token"

            base_url, headers = _get_api_config(
                "explicit-org", "explicit-team", "explicit-key", "explicit-secret"
            )

            assert (
                base_url == "https://explicit-org.pam.okta.com/v1/teams/explicit-team/"
            )
            mock_token.assert_called_once_with(
                "explicit-org", "explicit-team", "explicit-key", "explicit-secret"
            )


class TestResourceGroups:
    """Tests for resource_groups module."""

    def test_get_resource_groups_by_team_success(self):
        """Test successful resource groups retrieval."""
        with patch("okta_opa.services.resource_groups.requests.get") as mock_get:
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
        with patch("okta_opa.services.resource_groups.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"list": []}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = get_resource_groups_by_team("test-token", "test-org", "test-team")

            assert result == []

    def test_get_resource_groups_by_team_request_exception(self, capsys):
        """Test resource groups retrieval with request exception."""
        with patch("okta_opa.services.resource_groups.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException(
                "Connection error"
            )

            result = get_resource_groups_by_team("test-token", "test-org", "test-team")

            assert result == []
            captured = capsys.readouterr()
            assert "Error fetching resource groups" in captured.out

    def test_get_projects_by_resource_group_success(self):
        """Test successful projects retrieval by resource group."""
        with patch("okta_opa.services.resource_groups.requests.get") as mock_get:
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
        with patch("okta_opa.services.resource_groups.requests.get") as mock_get:
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
        with patch("okta_opa.services.resource_groups.requests.get") as mock_get:
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
        with patch("okta_opa.services.resource_groups.requests.get") as mock_get:
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
        with patch("okta_opa.services.projects.requests.get") as mock_get:
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
        with patch("okta_opa.services.projects.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = []
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = get_projects_by_team("test-token", "test-org", "test-team")

            assert result == []

    def test_get_projects_by_team_request_exception(self, capsys):
        """Test projects retrieval with request exception."""
        with patch("okta_opa.services.projects.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException(
                "Connection error"
            )

            result = get_projects_by_team("test-token", "test-org", "test-team")

            assert result == []
            captured = capsys.readouterr()
            assert "Error fetching projects" in captured.err

    def test_get_projects_by_team_timeout(self, capsys):
        """Test projects retrieval with timeout."""
        with patch("okta_opa.services.projects.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timeout")

            result = get_projects_by_team("test-token", "test-org", "test-team")

            assert result == []
            captured = capsys.readouterr()
            assert "Error fetching projects" in captured.err


class TestEnrollment:
    """Tests for enrollment module."""

    def test_generate_server_enrollment_token_success(self):
        """Test successful enrollment token generation."""
        with patch("okta_opa.services.enrollment.requests.post") as mock_post:
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
        with patch("okta_opa.services.enrollment.requests.post") as mock_post:
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
        with patch("okta_opa.services.enrollment.requests.post") as mock_post:
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
