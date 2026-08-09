"""Error contract tests for plugin loading."""

from __future__ import annotations

import sys
from types import ModuleType

import pytest

from generator.plugins.loader import load_plugin
from generator.plugins.registry import GeneratorRegistry
from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
    PluginError,
)


class DuplicatePluginGenerator(BaseGenerator):
    """Generator used to exercise duplicate registration failures."""

    name = "duplicate-plugin"

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Build an empty generation plan for the requested generator."""
        return GenerationPlan(generator_name=request.generator_name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Return an empty result for the supplied generation plan."""
        del plan
        return GenerationResult(generator_name=request.generator_name)


def test_load_plugin_rejects_missing_module() -> None:
    """Translate a missing plugin module into PluginError."""
    registry = GeneratorRegistry()

    with pytest.raises(PluginError):
        load_plugin("tests.plugin_module_that_does_not_exist", registry)


def test_load_plugin_rejects_module_without_generator(monkeypatch) -> None:
    """Reject plugin modules that expose no BaseGenerator subclass."""
    module_name = "tests.synthetic_empty_plugin"
    module = ModuleType(module_name)
    module.not_a_generator = object()
    monkeypatch.setitem(sys.modules, module_name, module)
    registry = GeneratorRegistry()

    with pytest.raises(PluginError):
        load_plugin(module_name, registry)


def test_load_plugin_rejects_duplicate_registration(monkeypatch) -> None:
    """Reject a plugin whose generator name is already registered."""
    module_name = "tests.synthetic_duplicate_plugin"
    module = ModuleType(module_name)
    module.DuplicatePluginGenerator = DuplicatePluginGenerator
    monkeypatch.setitem(sys.modules, module_name, module)

    registry = GeneratorRegistry()
    registry.register(DuplicatePluginGenerator)

    with pytest.raises(PluginError):
        load_plugin(module_name, registry)
