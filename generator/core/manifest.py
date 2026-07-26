from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from generator.core.exceptions import ConfigurationError


@dataclass(frozen=True, slots=True)
class GeneratorManifest:
    """描述 Generator 的可攜式中繼資料。"""

    name: str
    version: str
    description: str
    entrypoint: str

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> GeneratorManifest:
        """From mapping"""
        required = ("name", "version", "description", "entrypoint")
        missing = [key for key in required if not data.get(key)]
        if missing:
            raise ConfigurationError("Generator manifest 缺少必要欄位：" + ", ".join(missing))
        return cls(**{key: str(data[key]).strip() for key in required})

    @classmethod
    def load(cls, path: Path) -> GeneratorManifest:
        """Load"""
        if not path.exists():
            raise ConfigurationError(f"找不到 Generator manifest：{path}")
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            raise ConfigurationError(f"Manifest YAML 格式錯誤：{path}") from exc
        if not isinstance(data, dict):
            raise ConfigurationError("Generator manifest 根節點必須是 mapping")
        return cls.from_mapping(data)

    def dump(self, path: Path) -> None:
        """Dump"""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump(asdict(self), sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
