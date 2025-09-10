"""Tests for the main module."""

import pytest
import os
from unittest.mock import patch, Mock
from okta_api_script.main import get_service_token, main


def test_get_service_token_success():
    """Test successful API call."""
    with patch("okta_api_script.main.requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {"token": "test-token"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = get_service_token("test-team", "test-org", "test-key", "test-secret")

        assert result == {"token": "test-token"}
        mock_post.assert_called_once()


def test_main_missing_env_vars():
    """Test main function with missing environment variables."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(
            ValueError, match="KEY_ID and KEY_SECRET environment variables must be set"
        ):
            main()


def test_main_success():
    """Test successful main execution."""
    with patch.dict(os.environ, {"KEY_ID": "test-key", "KEY_SECRET": "test-secret"}):
        with patch("okta_api_script.main.get_service_token") as mock_get_token:
            with patch("builtins.print") as mock_print:
                mock_get_token.return_value = {"token": "test-token"}

                main()

                mock_get_token.assert_called_once_with(
                    "nos-coastal-modeling-cloud-sandbox-group",
                    "noaa",
                    "test-key",
                    "test-secret",
                )
                mock_print.assert_called_once_with({"token": "test-token"})
