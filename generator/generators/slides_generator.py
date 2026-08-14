"""Slides generator implementation for OpenProjectLab."""

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


class SlidesGenerator(BaseGenerator):
    """Generate an OpenProjectLab Markdown slide deck."""

    name = "slides"
    description = "Generate an OpenProjectLab Markdown slide deck"

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
        """Validate a Slides request before planning."""
        self._validate_generator_name(request.generator_name)
        self._resolve_template_root()
        self._validate_title(request.values.get("title"))
        self._validate_slides(request.values.get("slides"))

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Build an immutable plan for Slides template output."""
        ctx = dict(request.values)
        template_name = str(
            ctx.get("template_name", "slides/slides.md.j2"),
        )
        output_name = Path(ctx.get("output_name", "slides.md"))

        title = self._validate_title(ctx.get("title"))
        slides = self._validate_slides(ctx.get("slides"))

        ctx["title"] = title
        ctx["slides"] = slides

        operation = GenerationOperation(
            template_name=template_name,
            destination=request.target / output_name,
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
        """Execute a previously validated Slides generation plan."""
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
                slides = operation.context.get("slides", ())
                manifest.record(
                    operation.destination,
                    generator=self.name,
                    template=operation.template_name,
                    metadata={
                        "title": operation.context.get("title"),
                        "slide_count": len(slides),
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
    def _validate_title(cls, value: object) -> str:
        """Validate and normalize the slide deck title."""
        return cls._validate_text(value, field="title")

    @classmethod
    def _validate_slides(
        cls,
        value: object,
    ) -> tuple[dict[str, object], ...]:
        """Validate and normalize an ordered collection of slides."""
        if isinstance(value, (str, bytes, bytearray, Mapping)) or not isinstance(value, Sequence):
            raise GeneratorValidationError(
                generator=cls.name,
                field="slides",
                message="slides 必須是非空的有序集合",
            )

        if not value:
            raise GeneratorValidationError(
                generator=cls.name,
                field="slides",
                message="slides 不可為空",
            )

        return tuple(cls._validate_slide(slide) for slide in value)

    @classmethod
    def _validate_slide(
        cls,
        value: object,
    ) -> dict[str, object]:
        """Validate and normalize one slide."""
        if not isinstance(value, Mapping):
            raise GeneratorValidationError(
                generator=cls.name,
                field="slides",
                message="每個 slide 必須是 mapping",
            )

        title = cls._validate_text(
            value.get("title"),
            field="title",
        )

        if "content" not in value:
            raise GeneratorValidationError(
                generator=cls.name,
                field="content",
                message="每個 slide 必須包含 content",
            )

        content = cls._validate_content(value.get("content"))

        return {
            "title": title,
            "content": content,
        }

    @classmethod
    def _validate_content(
        cls,
        value: object,
    ) -> tuple[str, ...]:
        """Validate and normalize one slide's ordered content."""
        if isinstance(value, (str, bytes, bytearray, Mapping)) or not isinstance(value, Sequence):
            raise GeneratorValidationError(
                generator=cls.name,
                field="content",
                message="content 必須是有序集合",
            )

        return tuple(cls._validate_text(item, field="content") for item in value)

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
