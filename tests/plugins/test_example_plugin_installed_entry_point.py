"""End-to-end test for the installed example third-party Plugin distribution."""

from __future__ import annotations

import importlib.metadata
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

from generator.plugins.entry_points import (
    PLUGIN_ENTRY_POINT_GROUP,
    load_entry_points_into_registry,
)
from generator.plugins.registry import GeneratorRegistry
from generator.sdk import BaseGenerator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_ROOT = PROJECT_ROOT / "examples" / "plugins" / "hello-generator"
ENTRY_POINT_NAME = "hello-plugin"


@contextmanager
def _temporary_sys_path(path: Path) -> Iterator[None]:
    """Temporarily prepend a path so EntryPoint.load() can import the package."""
    sys.path.insert(0, str(path))
    try:
        yield
    finally:
        try:
            sys.path.remove(str(path))
        except ValueError:
            pass


def _install_example_plugin(target: Path) -> None:
    """Install the example distribution into an isolated target directory."""
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-deps",
            "--target",
            str(target),
            str(EXAMPLE_ROOT),
        ],
        check=True,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )


def _discover_installed_example_entry_point(
    target: Path,
) -> importlib.metadata.EntryPoint:
    """Discover hello-plugin from real distribution metadata in target."""
    distributions = importlib.metadata.distributions(path=[str(target)])
    entry_points = tuple(
        entry_point
        for distribution in distributions
        for entry_point in distribution.entry_points
        if entry_point.group == PLUGIN_ENTRY_POINT_GROUP and entry_point.name == ENTRY_POINT_NAME
    )

    assert len(entry_points) == 1
    return entry_points[0]


def test_installed_example_plugin_is_discovered_and_registered(
    tmp_path: Path,
) -> None:
    """Install, discover, load, validate, and register the example Plugin."""
    install_target = tmp_path / "site-packages"
    install_target.mkdir()

    _install_example_plugin(install_target)

    entry_point = _discover_installed_example_entry_point(install_target)

    assert entry_point.group == "openprojectlab.generators"
    assert entry_point.name == ENTRY_POINT_NAME
    assert entry_point.value == "opl_hello_plugin.generator:HelloGenerator"

    registry = GeneratorRegistry()

    with _temporary_sys_path(install_target):
        loaded = load_entry_points_into_registry((entry_point,), registry)

    assert len(loaded) == 1
    generator_type = loaded[0]

    assert issubclass(generator_type, BaseGenerator)
    assert generator_type.name == ENTRY_POINT_NAME
    assert registry.get(ENTRY_POINT_NAME) is generator_type


def test_installed_example_plugin_distribution_metadata_exists(
    tmp_path: Path,
) -> None:
    """Verify pip installation creates discoverable Python distribution metadata."""
    install_target = tmp_path / "site-packages"
    install_target.mkdir()

    _install_example_plugin(install_target)

    distributions = tuple(importlib.metadata.distributions(path=[str(install_target)]))
    names = {distribution.metadata["Name"] for distribution in distributions}

    assert "opl-hello-plugin" in names


def test_installed_example_plugin_loading_does_not_execute_lifecycle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure real Entry Point loading never invokes generator run/plan/execute."""
    install_target = tmp_path / "site-packages"
    install_target.mkdir()

    _install_example_plugin(install_target)
    entry_point = _discover_installed_example_entry_point(install_target)

    registry = GeneratorRegistry()

    with _temporary_sys_path(install_target):
        generator_type = entry_point.load()

        def fail_run(self, request):
            raise AssertionError("loading must not call run()")

        def fail_plan(self, request):
            raise AssertionError("loading must not call plan()")

        def fail_execute(self, request, plan):
            raise AssertionError("loading must not call execute()")

        monkeypatch.setattr(generator_type, "run", fail_run)
        monkeypatch.setattr(generator_type, "plan", fail_plan)
        monkeypatch.setattr(generator_type, "execute", fail_execute)

        loaded = load_entry_points_into_registry((entry_point,), registry)

    assert loaded == (generator_type,)
    assert registry.get(ENTRY_POINT_NAME) is generator_type
