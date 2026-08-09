"""Integration contract tests for plugin loading."""

from __future__ import annotations

import sys
from types import ModuleType

from generator.plugins.loader import load_plugin
from generator.plugins.registry import GeneratorRegistry
from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
)


class ExamplePluginGenerator(BaseGenerator):
    """Minimal third-party generator used by plugin loading tests."""

    name = "example-plugin"

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
        return GenerationResult(
            generator_name=request.generator_name,
            dry_run=request.options.dry_run,
        )


def _install_plugin_module(
    monkeypatch,
    module_name: str,
) -> None:
    """Install a synthetic plugin module for one test."""
    module = ModuleType(module_name)
    module.ExamplePluginGenerator = ExamplePluginGenerator
    monkeypatch.setitem(sys.modules, module_name, module)


def test_load_plugin_discovers_and_registers_generators(monkeypatch) -> None:
    """Discover plugin generators and register them in the supplied registry."""
    module_name = "tests.synthetic_plugin_loading"
    _install_plugin_module(monkeypatch, module_name)
    registry = GeneratorRegistry()

    loaded = load_plugin(module_name, registry)

    assert loaded == (ExamplePluginGenerator,)
    assert registry.get("example-plugin") is ExamplePluginGenerator


def test_load_plugin_returns_registered_generator_classes(monkeypatch) -> None:
    """Return generator classes in the same contract used by the registry."""
    module_name = "tests.synthetic_plugin_loading_return"
    _install_plugin_module(monkeypatch, module_name)
    registry = GeneratorRegistry()

    loaded = load_plugin(module_name, registry)

    assert loaded
    assert all(issubclass(generator, BaseGenerator) for generator in loaded)
