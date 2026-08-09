"""Plugin discovery and registration support for OpenProjectLab."""

from generator.plugins.discovery import discover_generators
from generator.plugins.registry import GeneratorRegistry

__all__ = ["GeneratorRegistry", "discover_generators"]
