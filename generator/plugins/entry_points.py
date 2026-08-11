"""Python Entry Point integration for OpenProjectLab generator plugins."""

from __future__ import annotations

from importlib.metadata import EntryPoint, entry_points
from typing import Final

from generator.plugins.registry import GeneratorRegistry
from generator.plugins.validation import validate_plugin_generator
from generator.sdk import BaseGenerator, PluginError

PLUGIN_ENTRY_POINT_GROUP: Final = "openprojectlab.generators"


def discover_plugin_entry_points() -> tuple[EntryPoint, ...]:
    """Return installed generator plugin Entry Points from the canonical group."""
    return tuple(entry_points(group=PLUGIN_ENTRY_POINT_GROUP))


def load_entry_point_generator(
    entry_point: EntryPoint,
) -> type[BaseGenerator]:
    """Load and validate exactly one generator Plugin Entry Point.

    The loaded object must satisfy the shared Plugin SDK generator validation
    contract, and the Entry Point metadata name must match the generator's
    public runtime name.

    Args:
        entry_point: Python package Entry Point describing one generator plugin.

    Returns:
        The original validated ``BaseGenerator`` subclass.

    Raises:
        PluginError: If loading or Entry Point identity validation fails.
    """
    try:
        candidate = entry_point.load()
    except (ImportError, ModuleNotFoundError, AttributeError) as exc:
        raise PluginError(f"Failed to load plugin entry point: {entry_point.name}") from exc

    generator_class = validate_plugin_generator(candidate)

    if entry_point.name != generator_class.name:
        raise PluginError(
            "Plugin entry point name does not match generator name: "
            f"{entry_point.name} != {generator_class.name}"
        )

    return generator_class


def load_entry_points_into_registry(
    plugin_entry_points: tuple[EntryPoint, ...],
    registry: GeneratorRegistry,
) -> tuple[type[BaseGenerator], ...]:
    """Load, validate, preflight, and register an Entry Point batch atomically.

    Registry mutation is deferred until every Entry Point has loaded,
    validated, passed metadata/runtime identity checks, and completed
    registration preflight.

    Args:
        plugin_entry_points: Entry Points participating in one loading batch.
        registry: Registry that receives the validated generator classes.

    Returns:
        Validated generator classes in the supplied Entry Point order.

    Raises:
        PluginError: If any Entry Point fails to load, validate, match identity,
            or pass registration preflight.
    """
    generators = tuple(
        load_entry_point_generator(entry_point) for entry_point in plugin_entry_points
    )

    _preflight_entry_point_registrations(generators, registry)

    for generator_class in generators:
        registry.register(generator_class)

    return generators


def _preflight_entry_point_registrations(
    generators: tuple[type[BaseGenerator], ...],
    registry: GeneratorRegistry,
) -> None:
    """Reject batch and existing-registry name collisions before mutation."""
    seen_names: set[str] = set()

    for generator_class in generators:
        name = generator_class.name

        if name in seen_names:
            raise PluginError(f"Generator already registered in entry point batch: {name}")

        seen_names.add(name)

        if registry.contains(name):
            raise PluginError(f"Generator already registered: {name}")
