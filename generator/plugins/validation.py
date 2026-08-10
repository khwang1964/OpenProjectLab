"""Validation helpers for third-party OpenProjectLab generator plugins."""

from __future__ import annotations

import inspect
import re
from typing import Final

from generator.sdk import BaseGenerator, PluginError

_PLUGIN_NAME_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[a-z][a-z0-9-]*$")


def validate_plugin_generator(candidate: object) -> type[BaseGenerator]:
    """Validate and return a third-party generator plugin class.

    Validation is intentionally side-effect free. It does not register the
    candidate, execute the generator lifecycle, or mutate plugin state.

    Args:
        candidate: Object resolved from plugin discovery or an entry point.

    Returns:
        The original validated ``BaseGenerator`` subclass.

    Raises:
        PluginError: If the candidate violates the Plugin SDK contract.
    """
    if not inspect.isclass(candidate):
        raise PluginError("Plugin candidate must be a class.")

    if not issubclass(candidate, BaseGenerator):
        raise PluginError("Plugin candidate must inherit from BaseGenerator.")

    if candidate is BaseGenerator:
        raise PluginError("BaseGenerator itself cannot be registered as a plugin.")

    if inspect.isabstract(candidate):
        raise PluginError("Plugin generator must be a concrete class.")

    _validate_plugin_name(candidate.name)
    _validate_zero_argument_construction(candidate)

    return candidate


def _validate_plugin_name(name: object) -> None:
    """Validate the public plugin generator name."""
    if not isinstance(name, str):
        raise PluginError("Plugin generator name must be a string.")

    if not _PLUGIN_NAME_PATTERN.fullmatch(name):
        raise PluginError("Plugin generator name must match ^[a-z][a-z0-9-]*$.")


def _validate_zero_argument_construction(
    generator_class: type[BaseGenerator],
) -> None:
    """Require Plugin SDK v1 generators to support zero-argument construction."""
    try:
        generator_class()
    except TypeError as exc:
        raise PluginError("Plugin generator must support zero-argument construction.") from exc
