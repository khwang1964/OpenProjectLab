"""Coordinate plugin discovery and registration."""

from __future__ import annotations

from generator.plugins.discovery import discover_generators
from generator.plugins.registry import GeneratorRegistry
from generator.sdk import BaseGenerator


def load_plugin(
    module_name: str,
    registry: GeneratorRegistry,
) -> tuple[type[BaseGenerator], ...]:
    """Discover generators from a plugin module and register them.

    Args:
        module_name: Importable Python module containing plugin generators.
        registry: Registry that receives discovered generator classes.

    Returns:
        The discovered generator classes in discovery order.
    """
    generators = discover_generators(module_name)

    for generator in generators:
        registry.register(generator)

    return generators
