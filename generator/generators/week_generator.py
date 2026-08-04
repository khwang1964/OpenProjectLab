"""Week generator implementation for OpenProjectLab."""

from __future__ import annotations

from pathlib import Path

from generator.core.exceptions import GeneratorValidationError
from generator.core.filesystem import FileSystem
from generator.core.generation_manifest import GenerationManifest
from generator.core.models import GenerateRequest, GenerationResult
from generator.core.template import TemplateRenderer


class WeekGenerator:
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
        self._template_root = Path(template_root) if template_root else None
        self._output_root = Path(output_root) if output_root else None
        self._filesystem = filesystem or FileSystem()

    def generate(self, request: GenerateRequest) -> GenerationResult:
        """Generate weekly lesson content from the shared request contract."""
        self._validate_generator_name(request.generator_name)

        template_root = self._resolve_template_root()
        output_root = request.target
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
        output = output_root / directory / output_name
        renderer = TemplateRenderer(template_root)
        content = renderer.render(template_name, ctx)
        record_manifest = bool(ctx.get("record_manifest", True))
        manifest = None
        if record_manifest:
            manifest = GenerationManifest.load(
                output_root,
                filesystem=self._filesystem,
            )
            manifest.set_project(name=ctx.get("course_name"))
            manifest.record(
                output,
                generator=self.name,
                template=template_name,
                metadata={"week": number, "title": ctx.get("title")},
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
