"""Assignment generator implementation for OpenProjectLab."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
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


class AssignmentGenerator(BaseGenerator):
    """Generate a Week-scoped OpenProjectLab assignment scaffold."""

    name = "assignment"
    description = "Generate an OpenProjectLab assignment scaffold"

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
        """Validate an Assignment request before planning."""
        self._validate_generator_name(request.generator_name)
        self._resolve_template_root()
        self._validate_week(request.values.get("week"))
        self._validate_assignment_id(request.values.get("assignment_id"))
        self._validate_title(request.values.get("title"))
        self._validate_optional_sequence(request.values, "objectives")
        self._validate_optional_text(request.values, "instructions")
        self._validate_optional_sequence(request.values, "deliverables")
        self._validate_optional_sequence(request.values, "resources")
        self._validate_optional_text(request.values, "submission")

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Build an immutable plan for Assignment template output."""
        ctx = dict(request.values)
        template_name = str(
            ctx.get("template_name", "assignment/README.md.j2"),
        )
        output_name = Path(ctx.get("output_name", "README.md"))

        week = self._validate_week(ctx.get("week"))
        assignment_id = self._validate_assignment_id(
            ctx.get("assignment_id"),
        )
        title = self._validate_title(ctx.get("title"))

        ctx["week"] = week
        ctx["week_padded"] = f"{week:02d}"
        ctx["assignment_id"] = assignment_id
        ctx["title"] = title

        for field in ("objectives", "deliverables", "resources"):
            if field in ctx:
                ctx[field] = self._validate_sequence(
                    ctx.get(field),
                    field=field,
                )

        for field in ("instructions", "submission"):
            if field in ctx:
                ctx[field] = self._validate_text(
                    ctx.get(field),
                    field=field,
                )

        output = request.target / f"week-{week:02d}" / "assignment" / assignment_id / output_name

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
        """Execute a previously validated Assignment generation plan."""
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
                        "assignment_id": operation.context.get("assignment_id"),
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
    def _validate_assignment_id(cls, value: object) -> str:
        """Validate and normalize a Week-scoped Assignment identity."""
        if not isinstance(value, str):
            raise GeneratorValidationError(
                generator=cls.name,
                field="assignment_id",
                message="assignment_id 必須是字串",
            )

        assignment_id = value.strip()
        if not assignment_id:
            raise GeneratorValidationError(
                generator=cls.name,
                field="assignment_id",
                message="assignment_id 不可為空",
            )

        path = Path(assignment_id)
        if (
            path.is_absolute()
            or ".." in path.parts
            or "/" in assignment_id
            or "\\" in assignment_id
        ):
            raise GeneratorValidationError(
                generator=cls.name,
                field="assignment_id",
                message="assignment_id 不可包含路徑語意",
            )

        return assignment_id

    @classmethod
    def _validate_title(cls, value: object) -> str:
        """Validate and normalize an Assignment display title."""
        return cls._validate_text(value, field="title")

    @classmethod
    def _validate_optional_sequence(
        cls,
        values: Mapping[str, object],
        field: str,
    ) -> None:
        """Validate an optional ordered string collection."""
        if field in values:
            cls._validate_sequence(values.get(field), field=field)

    @classmethod
    def _validate_optional_text(
        cls,
        values: Mapping[str, object],
        field: str,
    ) -> None:
        """Validate an optional non-empty string field."""
        if field in values:
            cls._validate_text(values.get(field), field=field)

    @classmethod
    def _validate_sequence(
        cls,
        value: object,
        *,
        field: str,
    ) -> tuple[str, ...]:
        """Validate and normalize an ordered collection of strings."""
        if isinstance(value, (str, bytes, bytearray, Mapping)) or not isinstance(value, Sequence):
            raise GeneratorValidationError(
                generator=cls.name,
                field=field,
                message=f"{field} 必須是有序集合",
            )

        normalized: list[str] = []
        for item in value:
            normalized.append(cls._validate_text(item, field=field))

        return tuple(normalized)

    @classmethod
    def _validate_text(
        cls,
        value: object,
        *,
        field: str,
    ) -> str:
        """Validate and normalize a required string value."""
        if not isinstance(value, str):
            raise GeneratorValidationError(
                generator=cls.name,
                field=field,
                message=f"{field} 必須是字串",
            )

        normalized = value.strip()
        if not normalized:
            raise GeneratorValidationError(
                generator=cls.name,
                field=field,
                message=f"{field} 不可為空",
            )

        return normalized
