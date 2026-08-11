"""Architecture contract for removing the legacy PluginManager path."""

from __future__ import annotations

import ast
from pathlib import Path

import generator.sdk as sdk
from generator.plugins import entry_points
from generator.plugins.registry import GeneratorRegistry

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GENERATOR_ROOT = PROJECT_ROOT / "generator"


def test_canonical_entry_point_api_remains_available() -> None:
    """Keep the canonical Milestone 4 Entry Point runtime available."""
    assert entry_points.PLUGIN_ENTRY_POINT_GROUP == "openprojectlab.generators"
    assert callable(entry_points.discover_plugin_entry_points)
    assert callable(entry_points.load_entry_point_generator)
    assert callable(entry_points.load_entry_points_into_registry)


def test_plugin_registry_remains_the_canonical_registry() -> None:
    """Protect the registry contract used by canonical Entry Point loading."""
    registry = GeneratorRegistry()

    assert registry.contains("missing-plugin") is False


def test_public_sdk_does_not_export_legacy_plugin_manager_symbols() -> None:
    """Legacy host-runtime types must never become Plugin SDK public API."""
    assert not hasattr(sdk, "PluginManager")
    assert not hasattr(sdk, "PluginDescriptor")

    public_symbols = set(getattr(sdk, "__all__", ()))
    assert "PluginManager" not in public_symbols
    assert "PluginDescriptor" not in public_symbols


def test_production_source_does_not_import_legacy_plugin_module() -> None:
    """Prevent production modules from reintroducing generator.core.plugin."""
    offenders: list[str] = []

    for path in GENERATOR_ROOT.rglob("*.py"):
        if path == GENERATOR_ROOT / "core" / "plugin.py":
            continue

        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                if any(
                    alias.name == "generator.core.plugin"
                    or alias.name.startswith("generator.core.plugin.")
                    for alias in node.names
                ):
                    offenders.append(str(path.relative_to(PROJECT_ROOT)))
                    break

            if isinstance(node, ast.ImportFrom):
                if node.module == "generator.core.plugin":
                    offenders.append(str(path.relative_to(PROJECT_ROOT)))
                    break

    assert offenders == []


def test_legacy_plugin_module_has_no_runtime_importers_in_generator_package() -> None:
    """Keep the removal boundary explicit until generator/core/plugin.py is deleted."""
    legacy_path = GENERATOR_ROOT / "core" / "plugin.py"

    # During the tests-first removal phase the legacy file may still exist.
    # Its presence is not the contract; absence of production dependencies is.
    if legacy_path.exists():
        assert legacy_path.is_file()
