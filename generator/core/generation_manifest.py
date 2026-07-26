"""Generation manifest support for OpenProjectLab.

The manifest records generated files under ``<project>/.opl/manifest.yaml``.
All recorded paths are safe, project-relative POSIX paths.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from generator.core.filesystem import FileSystem

SCHEMA_VERSION = "1.0"
MANIFEST_RELATIVE_PATH = Path(".opl") / "manifest.yaml"


class GenerationManifestError(ValueError):
    """Raised when manifest content or a generated entry is invalid."""


@dataclass(frozen=True, slots=True)
class GeneratedEntry:
    """One generated-file record."""

    path: str
    generator: str
    template: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """將資料轉換成可序列化的 dictionary。"""
        result: dict[str, Any] = {
            "path": self.path,
            "generator": self.generator,
            "template": self.template,
        }
        if self.metadata:
            result["metadata"] = dict(self.metadata)
        return result


class GenerationManifest:
    """Load, validate, update, and persist an OPL generation manifest."""

    def __init__(
        self,
        project_root: Path,
        *,
        schema_version: str = SCHEMA_VERSION,
        project: Mapping[str, Any] | None = None,
        entries: list[GeneratedEntry] | None = None,
        filesystem: FileSystem | None = None,
    ) -> None:
        self.project_root = Path(project_root)
        self.schema_version = self._validate_schema_version(schema_version)
        self.project = self._validate_mapping("project", project or {})
        self._entries: dict[str, GeneratedEntry] = {entry.path: entry for entry in (entries or [])}
        self._filesystem = filesystem or FileSystem()

    @property
    def path(self) -> Path:
        return self.project_root / MANIFEST_RELATIVE_PATH

    @property
    def entries(self) -> tuple[GeneratedEntry, ...]:
        return tuple(self._entries[path] for path in sorted(self._entries))

    @classmethod
    def load(
        cls,
        project_root: Path,
        *,
        filesystem: FileSystem | None = None,
    ) -> GenerationManifest:
        fs = filesystem or FileSystem()
        root = Path(project_root)
        manifest_path = root / MANIFEST_RELATIVE_PATH
        if not manifest_path.exists():
            return cls(root, filesystem=fs)

        try:
            raw = yaml.safe_load(fs.read_text(manifest_path)) or {}
        except yaml.YAMLError as exc:
            raise GenerationManifestError(f"Manifest YAML 格式錯誤：{manifest_path}") from exc

        if not isinstance(raw, Mapping):
            raise GenerationManifestError("Manifest 最上層必須是 mapping")

        schema_version = raw.get("schema_version")
        project = raw.get("project", {})
        generated = raw.get("generated", [])
        if not isinstance(generated, list):
            raise GenerationManifestError("Manifest generated 必須是 list")

        entries: list[GeneratedEntry] = []
        for index, item in enumerate(generated):
            if not isinstance(item, Mapping):
                raise GenerationManifestError(f"Manifest generated[{index}] 必須是 mapping")
            missing = {"path", "generator", "template"} - set(item)
            if missing:
                names = ", ".join(sorted(missing))
                raise GenerationManifestError(f"Manifest generated[{index}] 缺少欄位：{names}")
            metadata = item.get("metadata", {})
            entries.append(
                GeneratedEntry(
                    path=cls._validate_relative_path(item["path"]),
                    generator=cls._validate_non_empty("generator", item["generator"]),
                    template=cls._validate_non_empty("template", item["template"]),
                    metadata=cls._validate_mapping("metadata", metadata),
                )
            )

        return cls(
            root,
            schema_version=schema_version,
            project=project,
            entries=entries,
            filesystem=fs,
        )

    def set_project(self, **values: Any) -> None:
        self.project.update({key: value for key, value in values.items() if value is not None})

    def record(
        self,
        path: Path | str,
        *,
        generator: str,
        template: Path | str,
        metadata: Mapping[str, Any] | None = None,
    ) -> GeneratedEntry:
        relative = self._project_relative_path(path)
        entry = GeneratedEntry(
            path=relative,
            generator=self._validate_non_empty("generator", generator),
            template=self._validate_relative_path(template),
            metadata=self._validate_mapping("metadata", metadata or {}),
        )
        self._entries[entry.path] = entry
        return entry

    def to_dict(self) -> dict[str, Any]:
        """將資料轉換成可序列化的 dictionary。"""
        return {
            "schema_version": self.schema_version,
            "project": dict(self.project),
            "generated": [entry.to_dict() for entry in self.entries],
        }

    def dumps(self) -> str:
        """將 Manifest 序列化為 YAML 字串。"""
        return yaml.safe_dump(
            self.to_dict(),
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )

    def save(self, *, dry_run: bool = False) -> Path:
        """將 Manifest 寫入磁碟並回傳路徑。"""
        content = self.dumps()
        return self._filesystem.write_text(
            self.path,
            content,
            overwrite=True,
            dry_run=dry_run,
        )

    def _project_relative_path(self, value: Path | str) -> str:
        """Project relative path"""
        path = Path(value)
        if path.is_absolute():
            try:
                path = path.relative_to(self.project_root)
            except ValueError as exc:
                raise GenerationManifestError(f"產生檔案不在專案根目錄內：{value}") from exc
        return self._validate_relative_path(path)

    @staticmethod
    def _validate_schema_version(value: Any) -> str:
        """Validate schema version"""
        if value != SCHEMA_VERSION:
            raise GenerationManifestError(
                f"不支援的 Manifest schema_version：{value!r}；預期 {SCHEMA_VERSION!r}"
            )
        return str(value)

    @staticmethod
    def _validate_non_empty(name: str, value: Any) -> str:
        """Validate non empty"""
        if not isinstance(value, str) or not value.strip():
            raise GenerationManifestError(f"Manifest {name} 必須是非空字串")
        return value.strip()

    @staticmethod
    def _validate_mapping(name: str, value: Any) -> dict[str, Any]:
        """Validate mapping"""
        if not isinstance(value, Mapping):
            raise GenerationManifestError(f"Manifest {name} 必須是 mapping")
        return dict(value)

    @staticmethod
    def _validate_relative_path(value: Path | str) -> str:
        """Validate relative path"""
        if not isinstance(value, (str, Path)):
            raise GenerationManifestError("Manifest path 必須是字串或 Path")
        text = str(value).replace("\\", "/")
        path = PurePosixPath(text)
        if path.is_absolute() or not path.parts or text in {"", "."}:
            raise GenerationManifestError(f"Manifest path 必須是非空相對路徑：{value}")
        if ".." in path.parts:
            raise GenerationManifestError(f"Manifest path 不可包含父目錄跳脫：{value}")
        return path.as_posix()
