"""Week generator implementation for OpenProjectLab."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from generator.core.filesystem import FileSystem
from generator.core.generation_manifest import GenerationManifest
from generator.core.template import TemplateRenderer


class WeekGenerator:
    """Week Generator"""

    name = "week"
    description = "Generate an OpenProjectLab weekly lesson scaffold"

    def __init__(
        self,
        template_root: Path | None = None,
        output_root: Path | None = None,
        *,
        filesystem: FileSystem | None = None,
    ):
        self._template_root = Path(template_root) if template_root else None
        self._output_root = Path(output_root) if output_root else None
        self._filesystem = filesystem or FileSystem()

    def generate(
        self,
        output_root: Path | None = None,
        context: Mapping[str, Any] | None = None,
        *,
        template_root: Path | None = None,
        template_name: str | Path = "week/README.md.j2",
        output_name: str | Path = "README.md",
        directory_pattern: str = "week-{week:02d}",
        overwrite: bool = True,
        dry_run: bool = False,
        record_manifest: bool = True,
        **context_values: Any,
    ) -> Path:
        """Generator"""
        tr = self._resolve_template_root(template_root)
        root = self._resolve_output_root(output_root)
        ctx = dict(context or {})
        ctx.update(context_values)
        number = self._validate_week(ctx.get("week"))
        ctx["week"] = number
        ctx.setdefault("week_padded", f"{number:02d}")
        directory = self._format_week_directory(directory_pattern, number)
        output = root / directory / Path(output_name)
        renderer = TemplateRenderer(tr)
        content = renderer.render(template_name, ctx)
        manifest = None
        if record_manifest:
            manifest = GenerationManifest.load(root, filesystem=self._filesystem)
            manifest.set_project(name=ctx.get("course_name"))
            manifest.record(
                output,
                generator=self.name,
                template=template_name,
                metadata={"week": number, "title": ctx.get("title")},
            )
        self._filesystem.write_text(output, content, overwrite=overwrite, dry_run=dry_run)
        if manifest is not None:
            manifest.save(dry_run=dry_run)
        return output

    def run(self, output_root=None, context=None, **kwargs):
        """Run"""
        return self.generate(output_root, context, **kwargs)

    def _resolve_template_root(self, override):
        """Resolve template root"""
        result = Path(override) if override else self._template_root
        if result is None:
            raise ValueError("未提供 template_root")
        return result

    def _resolve_output_root(self, override):
        """Resolve output root"""
        result = Path(override) if override else self._output_root
        if result is None:
            raise ValueError("未提供 output_root")
        return result

    @staticmethod
    def _validate_week(value):
        """Validate week"""
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("week 必須是整數")
        if value <= 0:
            raise ValueError("week 必須大於 0")
        return value

    @staticmethod
    def _format_week_directory(pattern, week):
        """Format week directory"""
        try:
            directory = pattern.format(week=week)
        except (KeyError, IndexError, ValueError) as exc:
            raise ValueError(f"無效的 directory_pattern：{pattern}") from exc
        path = Path(directory)
        if path.is_absolute():
            raise ValueError("week 目錄不可為絕對路徑")
        if not path.parts or str(path) in {"", "."}:
            raise ValueError("week 目錄不可為空")
        if ".." in path.parts:
            raise ValueError("week 目錄不可包含父目錄跳脫")
        return path
