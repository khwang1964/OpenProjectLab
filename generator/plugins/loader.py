"""Coordinate plugin discovery, validation, and registration."""

from __future__ import annotations

from generator.plugins.discovery import discover_generators
from generator.plugins.registry import GeneratorRegistry
from generator.plugins.validation import validate_plugin_generator
from generator.sdk import BaseGenerator, PluginError


def load_plugin(
    module_name: str,
    registry: GeneratorRegistry,
) -> tuple[type[BaseGenerator], ...]:
    """Discover, validate, preflight, and register plugin generators.

    The registry is not mutated until every discovered generator has passed
    validation and all public-name conflicts have been checked.

    Args:
        module_name: Importable Python module containing plugin generators.
        registry: Registry that receives validated generator classes.

    Returns:
        The validated generator classes in discovery order.

    Raises:
        PluginError: If discovery, validation, or registration preflight fails.
    """
    discovered = discover_generators(module_name)
    validated = tuple(validate_plugin_generator(generator) for generator in discovered)

    _preflight_registration(validated, registry)

    for generator in validated:
        registry.register(generator)

    return validated


def _preflight_registration(
    generators: tuple[type[BaseGenerator], ...],
    registry: GeneratorRegistry,
) -> None:
    """Reject name conflicts before mutating the registry."""
    seen_names: set[str] = set()

    for generator in generators:
        name = generator.name

        if name in seen_names:
            raise PluginError(f"Generator already registered in plugin load: {name}")

        seen_names.add(name)

        try:
            registry.get(name)
        except PluginError:
            continue

        raise PluginError(f"Generator already registered: {name}")
