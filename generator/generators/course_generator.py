"""Course generator implementation for OpenProjectLab."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from generator.core.filesystem import FileSystem
from generator.core.generation_manifest import GenerationManifest
from generator.core.models import GenerationResult
from generator.core.template import TemplateRenderer


@dataclass(frozen=True, slots=True)
class CourseResult(GenerationResult):
    """Provide transitional course-specific result properties."""

    output_path: Path = Path()

    def __post_init__(self) -> None:
        """Normalize shared and course-specific result fields."""
        super(CourseResult, self).__post_init__()
        object.__setattr__(self, "output_path", Path(self.output_path))


class CourseGenerator:
    """產生 OpenProjectLab 課程基本結構。"""

    name = "course"
    description = "Generate an OpenProjectLab course scaffold"

    def __init__(
        self,
        template_root: Path | None = None,
        output_root: Path | None = None,
        *,
        filesystem: FileSystem | None = None,
    ) -> None:
        """初始化 Generator 及其模板與檔案系統相依項目。"""
        self._template_root = Path(template_root) if template_root else None
        self._output_root = Path(output_root) if output_root else None
        self._filesystem = filesystem or FileSystem()

    def generate(
        self,
        output_root: Path | None = None,
        context: Mapping[str, Any] | None = None,
        *,
        template_root: Path | None = None,
        template_name: str | Path = "course/README.md.j2",
        output_name: str | Path = "README.md",
        overwrite: bool = True,
        dry_run: bool = False,
        record_manifest: bool = True,
        **context_values: Any,
    ) -> GenerationResult:
        """Generate course content and return the shared result contract."""
        resolved_template_root = self._resolve_template_root(template_root)
        resolved_output_root = self._resolve_output_root(output_root)
        resolved_context = dict(context or {})
        resolved_context.update(context_values)
        renderer = TemplateRenderer(resolved_template_root)
        output = resolved_output_root / Path(output_name)
        content = renderer.render(template_name, resolved_context)
        manifest = None
        if record_manifest:
            manifest = GenerationManifest.load(
                resolved_output_root,
                filesystem=self._filesystem,
            )
            manifest.set_project(name=resolved_context.get("course_name"))
            manifest.record(
                output,
                generator=self.name,
                template=template_name,
                metadata=(
                    {"weeks": resolved_context.get("weeks")}
                    if resolved_context.get("weeks") is not None
                    else {}
                ),
            )
        write_result = self._filesystem.write_text(
            output,
            content,
            overwrite=overwrite,
            dry_run=dry_run,
        )
        if manifest is not None:
            manifest.save(dry_run=dry_run)
        return GenerationResult(
            generator_name=self.name,
            writes=(write_result,),
            dry_run=dry_run,
            manifest_updated=manifest is not None and not dry_run,
        )

    def run(
        self,
        output_root: Path | None = None,
        context: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> GenerationResult:
        """提供與 Generator registry 相容的執行介面。"""
        return self.generate(output_root, context, **kwargs)

    def _resolve_template_root(self, override: Path | None) -> Path:
        """解析 template_root。"""
        result = Path(override) if override else self._template_root
        if result is None:
            raise ValueError("未提供 template_root")
        return result

    def _resolve_output_root(self, override: Path | None) -> Path:
        """解析 output_root。"""
        result = Path(override) if override else self._output_root
        if result is None:
            raise ValueError("未提供 output_root")
        return result
