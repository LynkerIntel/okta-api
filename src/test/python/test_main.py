"""Tests for the main module."""

import json
import os
import sys
from unittest.mock import Mock, patch

import pytest
import requests

from okta_api_script.main import execute_api_cycle, get_service_token


def test_get_service_token_success():
    """Test successful API call."""
    with patch("okta_api_script.main.requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {
            "bearer_token": "test-token",
            "expires_at": "2025-12-02T12:00:00Z",
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = get_service_token("test-org", "test-team", "test-key", "test-secret")

        assert result["bearer_token"] == "test-token"
        assert "expires_in" in result
        mock_post.assert_called_once()


def test_main_missing_env_vars():
    """Test main function with missing environment variables."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(
            ValueError,
            match="org_name, team_name, and target_project variables must be set",
        ):
            execute_api_cycle()


def test_main_success():
    """Test successful main execution."""
    org = "test-org"
    team = "test-team"
    with patch.dict(
        os.environ,
        {
            "OKTA_ORG": org,
            "OKTA_TEAM": team,
            "OKTA_TARGET_PROJECT": "test-project",
            "KEY_ID": "test-key",
            "KEY_SECRET": "test-secret",
        },
    ):
        with patch("okta_api_script.main.get_service_token") as mock_get_token:
            with patch(
                "okta_api_script.main.get_resource_groups_by_team"
            ) as mock_get_rg:
                with patch(
                    "okta_api_script.main.get_projects_by_resource_group"
                ) as mock_get_projects:
                    with patch(
                        "okta_api_script.main.generate_server_enrollment_token"
                    ) as mock_gen_token:
                        mock_get_token.return_value = {
                            "bearer_token": "test-token",
                            "expires_at": "2025-12-02T12:00:00Z",
                            "expires_in": 3600,
                        }
                        mock_get_rg.return_value = [{"id": "rg-1"}]
                        mock_get_projects.return_value = [{"id": "proj-1"}]
                        mock_gen_token.return_value = {
                            "token": "test-enrollment-token",
                            "enrollment_token": "et-123",
                        }

                        execute_api_cycle()

                        mock_get_token.assert_called_once_with(
                            org,
                            team,
                            "test-key",
                            "test-secret",
                        )


def test_cli_module_structure():
    """Test that cli module has the correct structure."""
    # Test that the CLI module can be imported
    try:
        # We can't directly test the if __name__ == "__main__" block
        # but we can verify the module imports execute_api_cycle correctly
        from okta_api_script.main import execute_api_cycle as api_cycle

        # Verify execute_api_cycle is callable
        assert callable(api_cycle)
    except ImportError as e:
        pytest.fail(f"Failed to import execute_api_cycle: {e}")


def test_main_request_exception():
    """Test main function handles RequestException."""
    with patch.dict(
        os.environ,
        {
            "OKTA_ORG": "test-org",
            "OKTA_TEAM": "test-team",
            "OKTA_TARGET_PROJECT": "test-project",
            "KEY_ID": "test-key",
            "KEY_SECRET": "test-secret",
        },
    ):
        with patch("okta_api_script.main.get_service_token") as mock_get_token:
            mock_get_token.side_effect = requests.exceptions.RequestException(
                "Connection error"
            )
            with patch("builtins.print") as mock_print:
                execute_api_cycle()
                # Verify error was printed to stderr
                error_msg = "Error making API request: Connection error"
                import sys

                mock_print.assert_called_with(error_msg, file=sys.stderr)


def test_main_value_error_from_api():
    """Test main function handles ValueError from API call."""
    with patch.dict(
        os.environ,
        {
            "OKTA_ORG": "test-org",
            "OKTA_TEAM": "test-team",
            "OKTA_TARGET_PROJECT": "test-project",
            "KEY_ID": "test-key",
            "KEY_SECRET": "test-secret",
        },
    ):
        with patch("okta_api_script.main.get_service_token") as mock_get_token:
            mock_get_token.side_effect = ValueError("Invalid response format")
            with patch("builtins.print") as mock_print:
                execute_api_cycle()
                # Verify error was printed to stderr
                error_msg = "Configuration error: Invalid response format"
                import sys

                mock_print.assert_called_with(error_msg, file=sys.stderr)


def test_main_success_with_json_output():
    """Test successful main execution with JSON output enabled."""
    org = "test-org"
    team = "test-team"
    with patch.dict(
        os.environ,
        {
            "OKTA_ORG": org,
            "OKTA_TEAM": team,
            "OKTA_TARGET_PROJECT": "test-project",
            "KEY_ID": "test-key",
            "KEY_SECRET": "test-secret",
        },
    ):
        with patch("okta_api_script.main.get_service_token") as mock_get_token:
            with patch(
                "okta_api_script.main.get_resource_groups_by_team"
            ) as mock_get_rg:
                with patch(
                    "okta_api_script.main.get_projects_by_resource_group"
                ) as mock_get_projects:
                    with patch(
                        "okta_api_script.main.generate_server_enrollment_token"
                    ) as mock_gen_token:
                        with patch("builtins.print") as mock_print:
                            mock_get_token.return_value = {
                                "bearer_token": "test-token",
                                "expires_at": "2025-12-02T12:00:00Z",
                                "expires_in": 3600,
                            }
                            mock_get_rg.return_value = [{"id": "rg-1"}]
                            mock_get_projects.return_value = [{"id": "proj-1"}]
                            mock_gen_token.return_value = {
                                "token": "test-enrollment-token",
                                "enrollment_token": "et-123",
                            }

                            execute_api_cycle(output_json=True)

                            # Verify print was called with JSON output
                            mock_print.assert_called_once()
                            call_args = mock_print.call_args[0][0]
                            # Verify it's valid JSON and contains token
                            parsed = json.loads(call_args)
                            assert parsed["token"] == "test-enrollment-token"


def test_main_success_without_json_output():
    """Test successful main execution with JSON output disabled."""
    org = "test-org"
    team = "test-team"
    with patch.dict(
        os.environ,
        {
            "OKTA_ORG": org,
            "OKTA_TEAM": team,
            "OKTA_TARGET_PROJECT": "test-project",
            "KEY_ID": "test-key",
            "KEY_SECRET": "test-secret",
        },
    ):
        with patch("okta_api_script.main.get_service_token") as mock_get_token:
            with patch(
                "okta_api_script.main.get_resource_groups_by_team"
            ) as mock_get_rg:
                with patch(
                    "okta_api_script.main.get_projects_by_resource_group"
                ) as mock_get_projects:
                    with patch(
                        "okta_api_script.main.generate_server_enrollment_token"
                    ) as mock_gen_token:
                        with patch("builtins.print") as mock_print:
                            mock_get_token.return_value = {
                                "bearer_token": "test-token",
                                "expires_at": "2025-12-02T12:00:00Z",
                                "expires_in": 3600,
                            }
                            mock_get_rg.return_value = [{"id": "rg-1"}]
                            mock_get_projects.return_value = [{"id": "proj-1"}]
                            mock_gen_token.return_value = {
                                "token": "test-enrollment-token",
                                "enrollment_token": "et-123",
                            }

                            execute_api_cycle(output_json=False)

                            # Verify print was called with token string
                            mock_print.assert_called_once_with("test-enrollment-token")


def test_main_no_token_in_response():
    """Test main function handles missing token in enrollment response."""
    org = "test-org"
    team = "test-team"
    with patch.dict(
        os.environ,
        {
            "OKTA_ORG": org,
            "OKTA_TEAM": team,
            "OKTA_TARGET_PROJECT": "test-project",
            "KEY_ID": "test-key",
            "KEY_SECRET": "test-secret",
        },
    ):
        with patch("okta_api_script.main.get_service_token") as mock_get_token:
            with patch(
                "okta_api_script.main.get_resource_groups_by_team"
            ) as mock_get_rg:
                with patch(
                    "okta_api_script.main.get_projects_by_resource_group"
                ) as mock_get_projects:
                    with patch(
                        "okta_api_script.main.generate_server_enrollment_token"
                    ) as mock_gen_token:
                        with patch("builtins.print") as mock_print:
                            mock_get_token.return_value = {
                                "bearer_token": "test-token",
                                "expires_at": "2025-12-02T12:00:00Z",
                                "expires_in": 3600,
                            }
                            mock_get_rg.return_value = [{"id": "rg-1"}]
                            mock_get_projects.return_value = [{"id": "proj-1"}]
                            mock_gen_token.return_value = {
                                "token": None,
                                "enrollment_token": "et-123",
                            }

                            execute_api_cycle()

                            # Verify error was printed to stderr
                            error_msg = "Configuration error: No token received"
                            mock_print.assert_called_with(error_msg, file=sys.stderr)
