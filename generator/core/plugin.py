from __future__ import annotations

from dataclasses import dataclass
from importlib.metadata import entry_points

from generator.core.exceptions import PluginError


@dataclass(frozen=True, slots=True)
class PluginDescriptor:
    name: str
    object_path: str


class PluginManager:
    GROUP = "openprojectlab.generators"

    def discover(self) -> list[PluginDescriptor]:
        return [PluginDescriptor(ep.name, ep.value) for ep in entry_points(group=self.GROUP)]

    def load_into(self, registry) -> None:
        for ep in entry_points(group=self.GROUP):
            try:
                registry.register(ep.name, ep.load())
            except Exception as exc:
                raise PluginError(f"外掛載入失敗：{ep.name}") from exc
