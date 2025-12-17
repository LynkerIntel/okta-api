#!/usr/bin/env python3
"""Command line interface for okta-opa-script."""

import os

import click

from okta_api_script.main import execute_api_cycle


@click.command()
@click.option(
    "--org",
    default=lambda: os.getenv("OKTA_ORG"),
    help="Okta organization name (defaults to OKTA_ORG environment variable)",
)
@click.option(
    "--team",
    default=lambda: os.getenv("OKTA_TEAM"),
    help="Okta team name (defaults to OKTA_TEAM environment variable)",
)
@click.option(
    "--project",
    default=lambda: os.getenv("OKTA_TARGET_PROJECT"),
    help="Okta target project (defaults to OKTA_TARGET_PROJECT environment variable)",
)
@click.option(
    "--key",
    default=lambda: os.getenv("KEY_ID"),
    help="Okta key ID (defaults to KEY_ID environment variable)",
)
@click.option(
    "--secret",
    default=lambda: os.getenv("KEY_SECRET"),
    help="Okta key secret (defaults to KEY_SECRET environment variable)",
)
@click.option(
    "--json",
    default=False,
    help="Output JSON instead of just the server enrollment token (defaults to False)",
)
def cli(
    org: str | None,
    team: str | None,
    project: str | None,
    key: str | None,
    secret: str | None,
    json: bool = False,
) -> None:
    """Okta API script command line interface."""
    execute_api_cycle(org, team, project, key, secret, json)
