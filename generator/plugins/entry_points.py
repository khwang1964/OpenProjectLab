"""Python Entry Point integration for OpenProjectLab generator plugins."""

from __future__ import annotations

from importlib.metadata import EntryPoint, entry_points
from typing import Final

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
