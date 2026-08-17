"""Freeze the reviewed OpenProjectLab v1 packaging metadata contract."""

from __future__ import annotations

import importlib
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = PROJECT_ROOT / "pyproject.toml"


def _pyproject() -> dict[str, object]:
    """Load project metadata from the canonical pyproject.toml."""
    with PYPROJECT.open("rb") as file:
        return tomllib.load(file)


def test_v1_distribution_identity_is_openprojectlab() -> None:
    """Keep the installed distribution identity stable."""
    project = _pyproject()["project"]

    assert isinstance(project, dict)
    assert project["name"] == "openprojectlab"


def test_v1_python_support_floor_is_declared() -> None:
    """Keep the reviewed Python runtime floor explicit in package metadata."""
    project = _pyproject()["project"]

    assert isinstance(project, dict)
    assert project["requires-python"] == ">=3.12"


def test_v1_required_runtime_dependencies_are_declared() -> None:
    """Keep the runtime dependencies required by current core behavior declared."""
    project = _pyproject()["project"]

    assert isinstance(project, dict)
    dependencies = set(project["dependencies"])

    assert "Jinja2>=3.1" in dependencies
    assert "PyYAML>=6.0" in dependencies


def test_v1_console_entry_point_is_opl() -> None:
    """Freeze the canonical installed CLI entry point."""
    project = _pyproject()["project"]

    assert isinstance(project, dict)
    scripts = project["scripts"]

    assert scripts == {"opl": "generator.cli.main:main"}


def test_v1_generator_package_is_included_by_setuptools_discovery() -> None:
    """Keep generator and its subpackages inside the built distribution."""
    tool = _pyproject()["tool"]

    assert isinstance(tool, dict)
    setuptools = tool["setuptools"]
    assert isinstance(setuptools, dict)
    packages = setuptools["packages"]
    assert isinstance(packages, dict)
    find = packages["find"]
    assert isinstance(find, dict)

    assert "generator" in find["include"]
    assert "generator.*" in find["include"]


def test_v1_console_entry_point_target_is_importable() -> None:
    """Require the configured console-script target to resolve in source tests."""
    module = importlib.import_module("generator.cli.main")

    assert callable(module.main)


def test_v1_packaging_audit_does_not_claim_top_level_templates_are_packaged() -> None:
    """Record the current packaging boundary for later clean-install validation.

    Top-level templates are currently excluded by setuptools discovery.
    Step 8.4 must decide how release artifacts provide Generator templates;
    this Step 8.2 test intentionally does not claim that they are packaged.
    """
    tool = _pyproject()["tool"]

    assert isinstance(tool, dict)
    setuptools = tool["setuptools"]
    assert isinstance(setuptools, dict)
    packages = setuptools["packages"]
    assert isinstance(packages, dict)
    find = packages["find"]
    assert isinstance(find, dict)

    assert "templates" in find["exclude"]
    assert "templates.*" in find["exclude"]
