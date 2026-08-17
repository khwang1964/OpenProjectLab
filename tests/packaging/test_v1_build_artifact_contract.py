"""OpenProjectLab v1 build-artifact packaging contract tests."""

from __future__ import annotations

import configparser
import os
import tomllib
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = PROJECT_ROOT / "pyproject.toml"
WHEEL_ENV = "OPL_TEST_WHEEL"
REQUIRED_TEMPLATE_FAMILIES = (
    "bootstrap",
    "course",
    "week",
    "lab",
    "assignment",
    "quiz",
    "slides",
    "website",
)


def _pyproject() -> dict[str, object]:
    with PYPROJECT.open("rb") as stream:
        return tomllib.load(stream)


def _configured_wheel() -> Path:
    raw = os.environ.get(WHEEL_ENV)
    if not raw:
        pytest.skip(f"{WHEEL_ENV} is not set; build a wheel before artifact inspection")
    wheel = Path(raw).expanduser().resolve()
    if not wheel.is_file():
        pytest.fail(f"{WHEEL_ENV} does not name a wheel file: {wheel}")
    if wheel.suffix != ".whl":
        pytest.fail(f"{WHEEL_ENV} must name a .whl file: {wheel}")
    return wheel


def _wheel_names(wheel: Path) -> set[str]:
    with zipfile.ZipFile(wheel) as archive:
        return set(archive.namelist())


def _wheel_text(wheel: Path, suffix: str) -> str:
    with zipfile.ZipFile(wheel) as archive:
        matches = [name for name in archive.namelist() if name.endswith(suffix)]
        assert len(matches) == 1, f"expected one {suffix!r}, found {matches}"
        return archive.read(matches[0]).decode("utf-8")


def test_v1_distribution_identity_and_python_requirement_are_declared() -> None:
    data = _pyproject()
    project = data["project"]

    assert isinstance(project, dict)
    assert project["name"] == "openprojectlab"
    assert project["requires-python"] == ">=3.12"
    assert isinstance(project["version"], str)
    assert project["version"]


def test_v1_runtime_dependencies_are_declared() -> None:
    data = _pyproject()
    project = data["project"]

    assert isinstance(project, dict)
    dependencies = set(project["dependencies"])
    assert "Jinja2>=3.1" in dependencies
    assert "PyYAML>=6.0" in dependencies


def test_v1_console_script_contract_is_declared() -> None:
    data = _pyproject()
    project = data["project"]

    assert isinstance(project, dict)
    scripts = project["scripts"]
    assert isinstance(scripts, dict)
    assert scripts["opl"] == "generator.cli.main:main"


def test_v1_setuptools_discovers_generator_runtime_packages() -> None:
    data = _pyproject()
    tool = data["tool"]

    assert isinstance(tool, dict)
    setuptools = tool["setuptools"]
    assert isinstance(setuptools, dict)
    packages = setuptools["packages"]
    assert isinstance(packages, dict)
    find = packages["find"]
    assert isinstance(find, dict)

    assert find["include"] == ["generator", "generator.*"]
    assert "tests" in find["exclude"]
    assert "docs" in find["exclude"]
    assert "examples" in find["exclude"]


def test_v1_package_data_includes_runtime_templates() -> None:
    data = _pyproject()
    tool = data["tool"]

    assert isinstance(tool, dict)
    setuptools = tool["setuptools"]
    assert isinstance(setuptools, dict)
    package_data = setuptools["package-data"]
    assert isinstance(package_data, dict)

    patterns = package_data["generator.resources"]
    assert "templates/**/*" in patterns


def test_v1_repository_templates_are_not_mistaken_for_python_packages() -> None:
    data = _pyproject()
    tool = data["tool"]

    assert isinstance(tool, dict)
    setuptools = tool["setuptools"]
    assert isinstance(setuptools, dict)
    packages = setuptools["packages"]
    assert isinstance(packages, dict)
    find = packages["find"]
    assert isinstance(find, dict)

    assert "templates" in find["exclude"]
    assert "templates.*" in find["exclude"]


def test_v1_built_wheel_contains_generator_and_console_entry_point() -> None:
    wheel = _configured_wheel()
    names = _wheel_names(wheel)

    assert "generator/__init__.py" in names
    assert "generator/resources/__init__.py" in names

    entry_points = configparser.ConfigParser()
    entry_points.read_string(_wheel_text(wheel, ".dist-info/entry_points.txt"))
    assert entry_points["console_scripts"]["opl"] == "generator.cli.main:main"


def test_v1_built_wheel_contains_required_template_families() -> None:
    wheel = _configured_wheel()
    names = _wheel_names(wheel)

    missing = [
        family
        for family in REQUIRED_TEMPLATE_FAMILIES
        if not any(
            name.startswith(f"generator/resources/templates/{family}/") and not name.endswith("/")
            for name in names
        )
    ]
    assert missing == []


def test_v1_built_wheel_metadata_matches_pyproject_contract() -> None:
    wheel = _configured_wheel()
    metadata = _wheel_text(wheel, ".dist-info/METADATA")

    assert "Name: openprojectlab" in metadata
    assert "Requires-Python: >=3.12" in metadata
    assert "Requires-Dist: Jinja2>=3.1" in metadata
    assert "Requires-Dist: PyYAML>=6.0" in metadata


def test_v1_built_wheel_excludes_repository_only_trees() -> None:
    wheel = _configured_wheel()
    names = _wheel_names(wheel)

    forbidden_prefixes = (
        "tests/",
        "docs/",
        "examples/",
        "courses/",
        "website/",
        "scripts/",
        "templates/",
    )
    unexpected = sorted(
        name for name in names if any(name.startswith(prefix) for prefix in forbidden_prefixes)
    )
    assert unexpected == []
