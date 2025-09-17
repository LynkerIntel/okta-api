#!/usr/bin/env python3
"""
Script to validate that coverage configuration is consistent across all tools.
This script reads the coverage threshold from the centralized configuration
and checks that all tools are using the same value.
"""

import tomllib
from pathlib import Path


def check_coverage_config():
    """Check that coverage configuration is consistent."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)
    
    # Get the centralized coverage threshold
    min_coverage = config["tool"]["project-config"]["min_coverage_percentage"]
    print(f"Configured minimum coverage threshold: {min_coverage}%")
    
    # Check pytest configuration
    pytest_config = config["tool"]["pytest"]["ini_options"]["addopts"]
    pytest_coverage = None
    for opt in pytest_config.split():
        if opt.startswith("--cov-fail-under="):
            pytest_coverage = int(opt.split("=")[1])
            break
    
    # Check coverage.py configuration
    coverage_config = config["tool"]["coverage"]["report"]["fail_under"]
    
    print(f"pytest --cov-fail-under: {pytest_coverage}%")
    print(f"coverage.py fail_under: {coverage_config}%")
    
    # Validate consistency
    if pytest_coverage == min_coverage == coverage_config:
        print("✅ All coverage configurations are consistent!")
        return True
    else:
        print("❌ Coverage configurations are inconsistent!")
        print(f"Expected all values to be {min_coverage}%")
        return False


if __name__ == "__main__":
    check_coverage_config()
