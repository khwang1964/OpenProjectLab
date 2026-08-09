"""Course generator implementation for OpenProjectLab."""

from __future__ import annotations

from pathlib import Path

from generator.core.exceptions import GeneratorValidationError
from generator.core.filesystem import FileSystem
from generator.core.generation_manifest import GenerationManifest
from generator.core.models import (
    GenerateRequest,
    GenerationOperation,
    GenerationPlan,
    GenerationResult,
    WriteResult,
)
from generator.core.template import TemplateRenderer
from generator.generators.base import BaseGenerator


class CourseGenerator(BaseGenerator):
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
        super().__init__()
        self._template_root = Path(template_root) if template_root else None
        self._output_root = Path(output_root) if output_root else None
        self._filesystem = filesystem or FileSystem()

    def validate_request(self, request: GenerateRequest) -> None:
        """Validate a Course request before planning."""
        self._validate_generator_name(request.generator_name)
        self._resolve_template_root()

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Build an immutable plan for Course template output."""
        resolved_context = dict(request.values)

        template_name = str(
            resolved_context.get(
                "template_name",
                "course/README.md.j2",
            ),
        )
        output_name = Path(
            resolved_context.get(
                "output_name",
                "README.md",
            ),
        )

        operation = GenerationOperation(
            template_name=template_name,
            destination=request.target / output_name,
            context=resolved_context,
            write_policy=request.options.write_policy,
        )

        return GenerationPlan(
            generator_name=self.name,
            operations=(operation,),
        )

    def generate(
        self,
        request: GenerateRequest,
    ) -> GenerationResult:
        """Generate through the canonical framework lifecycle."""
        return self.run(request)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Execute a previously validated Course generation plan."""
        resolved_template_root = self._resolve_template_root()
        renderer = TemplateRenderer(resolved_template_root)

        writes: list[WriteResult] = []
        manifest = None

        if bool(request.values.get("record_manifest", True)):
            manifest = GenerationManifest.load(
                request.target,
                filesystem=self._filesystem,
            )
            manifest.set_project(
                name=request.values.get("course_name"),
            )

        for operation in plan.operations:
            content = renderer.render(
                operation.template_name,
                operation.context,
            )

            if manifest is not None:
                weeks = operation.context.get("weeks")
                manifest.record(
                    operation.destination,
                    generator=self.name,
                    template=operation.template_name,
                    metadata=({"weeks": weeks} if weeks is not None else {}),
                )

            write_result = self._filesystem.write_text(
                operation.destination,
                content,
                overwrite=request.options.overwrite,
                dry_run=request.options.dry_run,
            )
            writes.append(write_result)

        if manifest is not None:
            manifest.save(
                dry_run=request.options.dry_run,
            )

        return GenerationResult(
            generator_name=self.name,
            writes=tuple(writes),
            dry_run=request.options.dry_run,
            manifest_updated=(manifest is not None and not request.options.dry_run),
        )

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
