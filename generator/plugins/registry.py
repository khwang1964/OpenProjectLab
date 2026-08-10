"""Register plugin generator classes by their public names."""

from __future__ import annotations

from generator.core.exceptions import PluginError
from generator.generators.base import BaseGenerator


class GeneratorRegistry:
    """Store generator classes under unique public names."""

    def __init__(self) -> None:
        """Create an empty generator registry."""
        self._generators: dict[str, type[BaseGenerator]] = {}

    def register(self, generator_class: type[BaseGenerator]) -> None:
        """Register a generator class without replacing an existing name."""
        name = generator_class.name

        if name in self._generators:
            raise PluginError(f"Generator already registered: {name}")

        self._generators[name] = generator_class

    def contains(self, name: str) -> bool:
        """Return whether a generator name is already registered."""
        return name in self._generators

    def get(self, name: str) -> type[BaseGenerator]:
        """Return the generator class registered under the given name."""
        try:
            return self._generators[name]
        except KeyError as exc:
            raise PluginError(f"Generator is not registered: {name}") from exc
