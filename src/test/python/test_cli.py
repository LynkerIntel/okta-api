"""Tests for the CLI module."""

from click.testing import CliRunner

from okta_api_script.cli import cli


def test_cli_has_main():
    """Test that CLI module has cli command."""
    assert cli is not None
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "--org" in result.output
