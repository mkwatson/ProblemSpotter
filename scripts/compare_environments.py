#!/usr/bin/env python3
"""Compare local development environment with CI requirements."""

import sys
from pathlib import Path
from typing import Any, cast

try:
    import tomli
except ImportError:
    msg = "Error: tomli package not installed. Run: pip install tomli"
    print(msg, file=sys.stderr)
    sys.exit(1)

try:
    import pkg_resources
except ImportError:
    print(
        "Error: pkg_resources not found. Run: pip install setuptools",
        file=sys.stderr,
    )
    sys.exit(1)


def load_pyproject_requirements() -> set[str]:
    """Load required packages from pyproject.toml.

    Returns:
        Set of required package specifications.
    """
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found", file=sys.stderr)
        sys.exit(1)

    with open(pyproject_path, "rb") as f:
        pyproject = cast(dict[str, Any], tomli.load(f))

    requirements: set[str] = set()

    # Add main dependencies
    deps = cast(list[str], pyproject["project"]["dependencies"])
    requirements.update(deps)

    # Add dev dependencies
    optional_deps = pyproject["project"]["optional-dependencies"]
    dev_deps = cast(list[str], optional_deps["dev"])
    requirements.update(dev_deps)

    return requirements


def get_installed_packages() -> dict[str, str]:
    """Get currently installed packages and their versions.

    Returns:
        Dictionary mapping package names to their versions.
    """
    return {pkg.key: pkg.version for pkg in pkg_resources.working_set}


def normalize_package_name(name: str) -> str:
    """Normalize package name by replacing hyphens with underscores.

    Args:
        name: Package name to normalize.

    Returns:
        Normalized package name.
    """
    return name.replace("-", "_")


def check_missing_packages(required: set[str], installed: dict[str, str]) -> list[str]:
    """Check for missing required packages.

    Args:
        required: Set of required package specifications.
        installed: Dictionary of installed packages and versions.

    Returns:
        List of missing package requirements.
    """
    missing: list[str] = []
    for req in required:
        # Extract package name from requirement
        # Handle requirements like "package>=1.0.0"
        pkg_name = (
            req.split(">=")[0].split("<=")[0].split("==")[0].split(">")[0].split("<")[0].strip()
        )
        normalized_name = normalize_package_name(pkg_name)
        installed_names = {normalize_package_name(k) for k in installed}

        if normalized_name not in installed_names:
            missing.append(req)

    return missing


def main() -> int:
    """Main function.

    Returns:
        Exit code (0 for success, 1 for missing packages).
    """
    try:
        required_packages = load_pyproject_requirements()
        installed_packages = get_installed_packages()

        missing_packages = check_missing_packages(required_packages, installed_packages)

        if missing_packages:
            print("Missing required packages:")
            for pkg in missing_packages:
                print(f"  - {pkg}")
            print("\nTo install missing packages, run:")
            cmd = " ".join(f'"{pkg}"' for pkg in missing_packages)
            print(f"pip install {cmd}")
            return 1

        print("All required packages are installed.")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
