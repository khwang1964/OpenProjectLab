"""Course generator implementation for OpenProjectLab."""

from __future__ import annotations

from pathlib import Path

from generator.core.exceptions import GeneratorValidationError
from generator.core.filesystem import FileSystem
from generator.core.generation_manifest import GenerationManifest
from generator.core.models import GenerateRequest, GenerationResult
from generator.core.template import TemplateRenderer


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

    def generate(self, request: GenerateRequest) -> GenerationResult:
        """Generate course content from the shared request contract."""
        self._validate_generator_name(request.generator_name)

        resolved_template_root = self._resolve_template_root()
        resolved_output_root = request.target
        resolved_context = dict(request.values)
        template_name = str(
            resolved_context.get("template_name", "course/README.md.j2"),
        )
        output_name = Path(resolved_context.get("output_name", "README.md"))
        renderer = TemplateRenderer(resolved_template_root)
        output = resolved_output_root / output_name
        content = renderer.render(template_name, resolved_context)
        record_manifest = bool(resolved_context.get("record_manifest", True))
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
            overwrite=request.options.overwrite,
            dry_run=request.options.dry_run,
        )
        if manifest is not None:
            manifest.save(dry_run=request.options.dry_run)
        return GenerationResult(
            generator_name=self.name,
            writes=(write_result,),
            dry_run=request.options.dry_run,
            manifest_updated=manifest is not None and not request.options.dry_run,
        )

    def run(self, request: GenerateRequest) -> GenerationResult:
        """Run the canonical generation lifecycle for one request."""
        return self.generate(request)

    def _resolve_template_root(self) -> Path:
        """解析 template_root。"""
        if self._template_root is None:
            raise GeneratorValidationError(
                generator=self.name,
                field="template_root",
                message="未提供 template_root",
            )
        return self._template_root

    def _validate_generator_name(self, generator_name: str) -> None:
        """Reject requests addressed to a different generator."""
        if generator_name != self.name:
            raise GeneratorValidationError(
                generator=self.name,
                field="generator_name",
                message=(f"generator_name 必須是 {self.name!r}，收到 {generator_name!r}"),
            )
