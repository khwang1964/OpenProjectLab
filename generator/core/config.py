from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from generator.core.exceptions import ConfigurationError


@dataclass(slots=True)
class ProjectConfig:
    """保存及解析 OpenProjectLab 專案設定。"""

    project: dict[str, Any] = field(default_factory=dict)
    paths: dict[str, Any] = field(default_factory=dict)
    generator: dict[str, Any] = field(default_factory=dict)
    plugins: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> ProjectConfig:
        """從 YAML 檔案載入並驗證專案設定。"""
        if not path.exists():
            raise ConfigurationError(f"找不到設定檔：{path}")

        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            raise ConfigurationError(f"YAML 格式錯誤：{path}") from exc
        except OSError as exc:
            raise ConfigurationError(f"無法讀取設定檔：{path}") from exc

        if not isinstance(data, dict):
            raise ConfigurationError("設定檔根節點必須是 mapping")

        sections: dict[str, dict[str, Any]] = {}

        for section_name in ("project", "paths", "generator", "plugins"):
            section = data.get(section_name, {})

            if section is None:
                section = {}

            if not isinstance(section, dict):
                raise ConfigurationError(f"設定區段 '{section_name}' 必須是 mapping")

            sections[section_name] = section

        return cls(
            project=sections["project"],
            paths=sections["paths"],
            generator=sections["generator"],
            plugins=sections["plugins"],
        )

    def template_root(self, project_root: Path) -> Path:
        """解析並回傳模板根目錄。"""
        configured_path = self.paths.get("templates", "templates")

        if configured_path is None:
            configured_path = "templates"

        if not isinstance(configured_path, (str, Path)):
            raise ConfigurationError("設定項目 'paths.templates' 必須是字串或路徑")

        template_path = Path(configured_path)

        if template_path.is_absolute():
            return template_path

        return project_root / template_path
