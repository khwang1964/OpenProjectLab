"""Lab generator implementation for OpenProjectLab."""

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


class LabGenerator(BaseGenerator):
    """Generate a Week-scoped OpenProjectLab lab scaffold."""

    name = "lab"
    description = "Generate an OpenProjectLab lab scaffold"

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
        """Validate a Lab request before planning."""
        self._validate_generator_name(request.generator_name)
        self._resolve_template_root()
        self._validate_week(request.values.get("week"))
        self._validate_lab_id(request.values.get("lab_id"))
        self._validate_title(request.values.get("title"))

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Build an immutable plan for Lab template output."""
        ctx = dict(request.values)
        template_name = str(ctx.get("template_name", "lab/README.md.j2"))
        output_name = Path(ctx.get("output_name", "README.md"))

        week = self._validate_week(ctx.get("week"))
        lab_id = self._validate_lab_id(ctx.get("lab_id"))
        title = self._validate_title(ctx.get("title"))

        ctx["week"] = week
        ctx["week_padded"] = f"{week:02d}"
        ctx["lab_id"] = lab_id
        ctx["title"] = title

        output = request.target / f"week-{week:02d}" / "lab" / lab_id / output_name

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
        """Execute a previously validated Lab generation plan."""
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
                        "lab_id": operation.context.get("lab_id"),
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
    def _validate_lab_id(cls, value: object) -> str:
        """Validate and normalize a Week-scoped Lab identity."""
        if not isinstance(value, str):
            raise GeneratorValidationError(
                generator=cls.name,
                field="lab_id",
                message="lab_id 必須是字串",
            )

        lab_id = value.strip()
        if not lab_id:
            raise GeneratorValidationError(
                generator=cls.name,
                field="lab_id",
                message="lab_id 不可為空",
            )

        path = Path(lab_id)
        if path.is_absolute() or ".." in path.parts or "/" in lab_id or "\\" in lab_id:
            raise GeneratorValidationError(
                generator=cls.name,
                field="lab_id",
                message="lab_id 不可包含路徑語意",
            )

        return lab_id

    @classmethod
    def _validate_title(cls, value: object) -> str:
        """Validate and normalize a Lab display title."""
        if not isinstance(value, str):
            raise GeneratorValidationError(
                generator=cls.name,
                field="title",
                message="title 必須是字串",
            )

        title = value.strip()
        if not title:
            raise GeneratorValidationError(
                generator=cls.name,
                field="title",
                message="title 不可為空",
            )

        return title
