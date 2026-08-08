"""Week generator implementation for OpenProjectLab."""

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


class WeekGenerator(BaseGenerator):
    """Generate an OpenProjectLab weekly lesson scaffold."""

    name = "week"
    description = "Generate an OpenProjectLab weekly lesson scaffold"

    def __init__(
        self,
        template_root: Path | None = None,
        output_root: Path | None = None,
        *,
        filesystem: FileSystem | None = None,
    ) -> None:
        """Initialize the generator and its filesystem dependencies."""
        super().__init__()
        self._template_root = Path(template_root) if template_root else None
        self._output_root = Path(output_root) if output_root else None
        self._filesystem = filesystem or FileSystem()

    def validate_request(self, request: GenerateRequest) -> None:
        """Validate a Week request before planning."""
        self._validate_generator_name(request.generator_name)
        self._resolve_template_root()
        self._validate_week(request.values.get("week"))

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Build an immutable plan for Week template output."""
        ctx = dict(request.values)
        template_name = str(ctx.get("template_name", "week/README.md.j2"))
        output_name = Path(ctx.get("output_name", "README.md"))
        directory_pattern = str(
            ctx.get("directory_pattern", "week-{week:02d}"),
        )

        number = self._validate_week(ctx.get("week"))
        ctx["week"] = number
        ctx.setdefault("week_padded", f"{number:02d}")

        directory = self._format_week_directory(directory_pattern, number)
        output = request.target / directory / output_name

        operation = GenerationOperation(
            template_name=template_name,
            destination=output,
            context=ctx,
            write_policy=request.options.write_policy,
        )

        return GenerationPlan(
            generator_name=self.name,
            operations=(operation,),
        )

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Execute a previously validated Week generation plan."""
        template_root = self._resolve_template_root()
        renderer = TemplateRenderer(template_root)

        writes: list[WriteResult] = []
        manifest = None

        if bool(request.values.get("record_manifest", True)):
            manifest = GenerationManifest.load(
                request.target,
                filesystem=self._filesystem,
            )
            manifest.set_project(name=request.values.get("course_name"))

        for operation in plan.operations:
            content = renderer.render(
                operation.template_name,
                operation.context,
            )

            if manifest is not None:
                manifest.record(
                    operation.destination,
                    generator=self.name,
                    template=operation.template_name,
                    metadata={
                        "week": operation.context.get("week"),
                        "title": operation.context.get("title"),
                    },
                )

            write_result = self._filesystem.write_text(
                operation.destination,
                content,
                overwrite=request.options.overwrite,
                dry_run=request.options.dry_run,
            )
            writes.append(write_result)

        if manifest is not None:
            manifest.save(dry_run=request.options.dry_run)

        return GenerationResult(
            generator_name=self.name,
            writes=tuple(writes),
            dry_run=request.options.dry_run,
            manifest_updated=(manifest is not None and not request.options.dry_run),
        )

    def generate(self, request: GenerateRequest) -> GenerationResult:
        """Generate through the canonical framework lifecycle."""
        return self.run(request)

    def _resolve_template_root(self) -> Path:
        """Resolve the template root."""
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

    @classmethod
    def _validate_week(cls, value: object) -> int:
        """Validate and return a positive integer week number."""
        if isinstance(value, bool) or not isinstance(value, int):
            raise GeneratorValidationError(
                generator=cls.name,
                field="week",
                message="week 必須是整數",
            )
        if value <= 0:
            raise GeneratorValidationError(
                generator=cls.name,
                field="week",
                message="week 必須大於 0",
            )
        return value

    @classmethod
    def _format_week_directory(cls, pattern: str, week: int) -> Path:
        """Format and validate the relative week directory."""
        try:
            directory = pattern.format(week=week)
        except (KeyError, IndexError, ValueError) as exc:
            raise GeneratorValidationError(
                generator=cls.name,
                field="directory_pattern",
                message=f"無效的 directory_pattern：{pattern}",
            ) from exc

        path = Path(directory)
        if path.is_absolute():
            raise GeneratorValidationError(
                generator=cls.name,
                field="directory_pattern",
                message="week 目錄不可為絕對路徑",
            )
        if not path.parts or str(path) in {"", "."}:
            raise GeneratorValidationError(
                generator=cls.name,
                field="directory_pattern",
                message="week 目錄不可為空",
            )
        if ".." in path.parts:
            raise GeneratorValidationError(
                generator=cls.name,
                field="directory_pattern",
                message="week 目錄不可包含父目錄跳脫",
            )
        return path
