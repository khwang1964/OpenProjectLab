"""Contract tests for plugin generator discovery."""

from __future__ import annotations

import sys
from types import ModuleType

import pytest

from generator.core.exceptions import PluginError
from generator.generators.base import BaseGenerator
from generator.plugins.discovery import discover_generators


class ValidPluginGenerator(BaseGenerator):
    """Minimal generator used to define the discovery contract."""

    name = "valid-plugin"

    def plan(self, request):
        """Build a minimal empty plan for contract testing."""
        from generator.core.models import GenerationPlan

        return GenerationPlan(generator_name=request.generator_name)

    def execute(self, request, plan):
        """Return a minimal result for contract testing."""
        from generator.core.models import GenerationResult

        del plan
        return GenerationResult(
            generator_name=request.generator_name,
            dry_run=request.options.dry_run,
        )


def _install_module(monkeypatch: pytest.MonkeyPatch, name: str, **members: object) -> str:
    """Install an in-memory module for discovery tests."""
    module = ModuleType(name)

    for member_name, member in members.items():
        setattr(module, member_name, member)

    monkeypatch.setitem(sys.modules, name, module)
    return name


def test_discovery_finds_base_generator_subclasses(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Discover concrete BaseGenerator subclasses exported by a plugin module."""
    module_name = _install_module(
        monkeypatch,
        "tests.fake_valid_plugin",
        ValidPluginGenerator=ValidPluginGenerator,
    )

    discovered = discover_generators(module_name)

    assert discovered == (ValidPluginGenerator,)


def test_discovery_ignores_non_generator_objects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ignore plugin module members that are not BaseGenerator subclasses."""
    module_name = _install_module(
        monkeypatch,
        "tests.fake_mixed_plugin",
        ValidPluginGenerator=ValidPluginGenerator,
        helper=lambda: None,
        value=42,
    )

    discovered = discover_generators(module_name)

    assert discovered == (ValidPluginGenerator,)


def test_discovery_rejects_module_without_generator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Raise PluginError when a plugin module exposes no valid generator."""
    module_name = _install_module(
        monkeypatch,
        "tests.fake_invalid_plugin",
        helper=lambda: None,
    )

    with pytest.raises(PluginError):
        discover_generators(module_name)
