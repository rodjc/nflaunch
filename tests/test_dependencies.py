"""Test that dependencies in pyproject.toml match requirements.txt."""

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from pathlib import Path


def test_dependencies_sync():
    """Verify that dependencies in pyproject.toml match those in requirements.txt."""
    # Get project root directory
    project_root = Path(__file__).parent.parent

    # Read pyproject.toml
    pyproject_path = project_root / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)

    pyproject_deps = set(pyproject_data["project"]["dependencies"])

    # Read requirements.txt
    requirements_path = project_root / "requirements.txt"
    with open(requirements_path) as f:
        requirements_deps = {
            line.strip() for line in f if line.strip() and not line.startswith("#")
        }

    # Compare dependencies
    assert pyproject_deps == requirements_deps, (
        f"Dependencies mismatch!\n"
        f"Only in pyproject.toml: {pyproject_deps - requirements_deps}\n"
        f"Only in requirements.txt: {requirements_deps - pyproject_deps}"
    )
