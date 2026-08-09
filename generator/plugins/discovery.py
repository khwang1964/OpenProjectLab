"""Discover generator classes exposed by plugin modules."""

from __future__ import annotations

from importlib import import_module
from inspect import getmembers, isabstract, isclass

from generator.core.exceptions import PluginError
from generator.generators.base import BaseGenerator


def discover_generators(module_name: str) -> tuple[type[BaseGenerator], ...]:
    """Return concrete BaseGenerator subclasses exposed by a plugin module."""
    try:
        module = import_module(module_name)
    except ImportError as exc:
        raise PluginError(f"Unable to import plugin module: {module_name}") from exc

    generators = tuple(
        member
        for _, member in getmembers(module, isclass)
        if issubclass(member, BaseGenerator)
        and member is not BaseGenerator
        and not isabstract(member)
    )

    if not generators:
        raise PluginError(f"Plugin module exposes no generators: {module_name}")

    return generators
