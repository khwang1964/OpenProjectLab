"""Contract tests for plugin registry membership queries."""

from __future__ import annotations

from generator.core.models import GenerationPlan, GenerationResult
from generator.generators.base import BaseGenerator
from generator.plugins.registry import GeneratorRegistry


class RegisteredPluginGenerator(BaseGenerator):
    """Minimal generator used to define registry membership behavior."""

    name = "registered-plugin"

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


class ConstructorGuardGenerator(RegisteredPluginGenerator):
    """Generator that must never be instantiated by a membership query."""

    name = "constructor-guard"

    def __init__(self) -> None:
        """Fail if registry membership lookup instantiates the generator."""
        raise AssertionError("contains() must not instantiate generators")


def test_empty_registry_does_not_contain_name() -> None:
    """Return False when no generator is registered under the queried name."""
    registry = GeneratorRegistry()

    assert registry.contains("registered-plugin") is False


def test_registry_contains_registered_generator_name() -> None:
    """Return True for the public name of a registered generator."""
    registry = GeneratorRegistry()
    registry.register(RegisteredPluginGenerator)

    assert registry.contains("registered-plugin") is True


def test_registry_does_not_contain_unknown_name() -> None:
    """Return False for an unknown name without raising an exception."""
    registry = GeneratorRegistry()
    registry.register(RegisteredPluginGenerator)

    assert registry.contains("missing-plugin") is False


def test_contains_does_not_mutate_existing_registry_entries() -> None:
    """Membership queries must leave existing registrations unchanged."""
    registry = GeneratorRegistry()
    registry.register(RegisteredPluginGenerator)

    assert registry.contains("missing-plugin") is False
    assert registry.get("registered-plugin") is RegisteredPluginGenerator


def test_contains_does_not_instantiate_registered_generator() -> None:
    """Membership queries inspect names only and never construct generators."""
    registry = GeneratorRegistry()
    registry.register(ConstructorGuardGenerator)

    assert registry.contains("constructor-guard") is True
    assert registry.get("constructor-guard") is ConstructorGuardGenerator
