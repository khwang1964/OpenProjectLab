"""Contract tests for plugin generator registration."""

from __future__ import annotations

import pytest

from generator.core.exceptions import PluginError
from generator.core.models import GenerationPlan, GenerationResult
from generator.generators.base import BaseGenerator
from generator.plugins.registry import GeneratorRegistry


class FirstPluginGenerator(BaseGenerator):
    """Minimal generator used to define registry behavior."""

    name = "example-plugin"

    def plan(self, request):
        """Build a minimal empty plan for contract testing."""
        return GenerationPlan(generator_name=request.generator_name)

    def execute(self, request, plan):
        """Return a minimal result for contract testing."""
        del plan
        return GenerationResult(
            generator_name=request.generator_name,
            dry_run=request.options.dry_run,
        )


class DuplicatePluginGenerator(FirstPluginGenerator):
    """Generator intentionally reusing an existing registry name."""


class SecondPluginGenerator(FirstPluginGenerator):
    """Generator with a distinct registration name."""

    name = "second-plugin"


def test_registry_registers_generator_by_unique_name() -> None:
    """Register a generator class and retrieve it by its public name."""
    registry = GeneratorRegistry()

    registry.register(FirstPluginGenerator)

    assert registry.get("example-plugin") is FirstPluginGenerator


def test_registry_rejects_duplicate_generator_name() -> None:
    """Do not silently replace a generator registered under the same name."""
    registry = GeneratorRegistry()
    registry.register(FirstPluginGenerator)

    with pytest.raises(PluginError):
        registry.register(DuplicatePluginGenerator)


def test_registry_keeps_distinct_generator_registrations() -> None:
    """Retain independently registered generators under distinct names."""
    registry = GeneratorRegistry()

    registry.register(FirstPluginGenerator)
    registry.register(SecondPluginGenerator)

    assert registry.get("example-plugin") is FirstPluginGenerator
    assert registry.get("second-plugin") is SecondPluginGenerator
