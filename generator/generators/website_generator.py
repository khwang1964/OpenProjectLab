"""Website generator implementation for OpenProjectLab."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath, PureWindowsPath

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


class WebsiteGenerator(BaseGenerator):
    """Generate an OpenProjectLab deterministic static course website."""

    name = "website"
    description = "Generate an OpenProjectLab static course website"

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
        """Validate a Website request before planning."""
        self._validate_generator_name(request.generator_name)
        self._resolve_template_root()
        self._validate_title(request.values.get("title"))
        self._validate_pages(request.values.get("pages"))

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Build an immutable deterministic plan for Website output."""
        template_name = str(
            request.values.get(
                "template_name",
                "website/page.html.j2",
            )
        )
        output_directory = self._validate_output_directory(
            request.values.get("output_directory", "site")
        )

        site_title = self._validate_title(
            request.values.get("title"),
        )
        pages = self._validate_pages(
            request.values.get("pages"),
        )

        navigation = tuple(
            {
                "path": page["path"],
                "title": page["title"],
            }
            for page in pages
        )

        operations: list[GenerationOperation] = []

        for page in pages:
            context = {
                "site_title": site_title,
                "page": dict(page),
                "navigation": tuple(dict(item) for item in navigation),
            }

            destination = request.target / output_directory / Path(str(page["path"]))

            operations.append(
                GenerationOperation(
                    template_name=template_name,
                    destination=destination,
                    context=context,
                    write_policy=request.options.write_policy,
                )
            )

        return GenerationPlan(
            generator_name=self.name,
            operations=tuple(operations),
        )

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Execute a previously validated Website generation plan."""
        template_root = self._resolve_template_root()
        renderer = TemplateRenderer(template_root)

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
                page = operation.context.get("page", {})

                page_title = None
                if isinstance(page, Mapping):
                    page_title = page.get("title")

                manifest.record(
                    operation.destination,
                    generator=self.name,
                    template=operation.template_name,
                    metadata={
                        "site_title": operation.context.get("site_title"),
                        "page_title": page_title,
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
            manifest.save(
                dry_run=request.options.dry_run,
            )

        return GenerationResult(
            generator_name=self.name,
            writes=tuple(writes),
            dry_run=request.options.dry_run,
            manifest_updated=(manifest is not None and not request.options.dry_run),
        )

    def generate(
        self,
        request: GenerateRequest,
    ) -> GenerationResult:
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

    def _validate_generator_name(
        self,
        generator_name: str,
    ) -> None:
        """Reject requests addressed to another generator."""
        if generator_name != self.name:
            raise GeneratorValidationError(
                generator=self.name,
                field="generator_name",
                message=(f"generator_name 必須是 {self.name!r}，收到 {generator_name!r}"),
            )

    @classmethod
    def _validate_title(
        cls,
        value: object,
    ) -> str:
        """Validate and normalize the site title."""
        return cls._validate_text(
            value,
            field="title",
        )

    @classmethod
    def _validate_pages(
        cls,
        value: object,
    ) -> tuple[dict[str, str], ...]:
        """Validate and normalize an ordered collection of pages."""
        if isinstance(
            value,
            (str, bytes, bytearray, Mapping),
        ) or not isinstance(value, Sequence):
            raise GeneratorValidationError(
                generator=cls.name,
                field="pages",
                message="pages 必須是非空的有序集合",
            )

        if not value:
            raise GeneratorValidationError(
                generator=cls.name,
                field="pages",
                message="pages 不可為空",
            )

        pages: list[dict[str, str]] = []
        seen_paths: set[str] = set()

        for page in value:
            normalized = cls._validate_page(page)
            path = normalized["path"]

            if path in seen_paths:
                raise GeneratorValidationError(
                    generator=cls.name,
                    field="path",
                    message=f"page path 不可重複：{path!r}",
                )

            seen_paths.add(path)
            pages.append(normalized)

        if "index.html" not in seen_paths:
            raise GeneratorValidationError(
                generator=cls.name,
                field="pages",
                message="pages 必須包含 index.html",
            )

        return tuple(pages)

    @classmethod
    def _validate_page(
        cls,
        value: object,
    ) -> dict[str, str]:
        """Validate and normalize one Website page."""
        if not isinstance(value, Mapping):
            raise GeneratorValidationError(
                generator=cls.name,
                field="pages",
                message="每個 page 必須是 mapping",
            )

        if "path" not in value:
            raise GeneratorValidationError(
                generator=cls.name,
                field="path",
                message="每個 page 必須包含 path",
            )

        path = cls._validate_page_path(
            value.get("path"),
        )

        if "title" not in value:
            raise GeneratorValidationError(
                generator=cls.name,
                field="title",
                message="每個 page 必須包含 title",
            )

        title = cls._validate_text(
            value.get("title"),
            field="title",
        )

        if "content" not in value:
            raise GeneratorValidationError(
                generator=cls.name,
                field="content",
                message="每個 page 必須包含 content",
            )

        content = cls._validate_content(
            value.get("content"),
        )

        return {
            "path": path,
            "title": title,
            "content": content,
        }

    @classmethod
    def _validate_page_path(
        cls,
        value: object,
    ) -> str:
        """Validate and normalize a relative HTML page path."""
        if not isinstance(value, str):
            raise GeneratorValidationError(
                generator=cls.name,
                field="path",
                message="page path 必須是字串",
            )

        candidate = value.strip()

        if not candidate:
            raise GeneratorValidationError(
                generator=cls.name,
                field="path",
                message="page path 不可為空",
            )

        posix_path = PurePosixPath(candidate)
        windows_path = PureWindowsPath(candidate)

        if posix_path.is_absolute() or windows_path.is_absolute():
            raise GeneratorValidationError(
                generator=cls.name,
                field="path",
                message="page path 必須是相對路徑",
            )

        if ".." in posix_path.parts or ".." in windows_path.parts:
            raise GeneratorValidationError(
                generator=cls.name,
                field="path",
                message="page path 不可包含路徑穿越",
            )

        if windows_path.drive:
            raise GeneratorValidationError(
                generator=cls.name,
                field="path",
                message="page path 不可包含磁碟機路徑",
            )

        normalized = posix_path.as_posix()

        while normalized.startswith("./"):
            normalized = normalized[2:]

        if not normalized or normalized == ".":
            raise GeneratorValidationError(
                generator=cls.name,
                field="path",
                message="page path 不可為空",
            )

        if not normalized.endswith(".html"):
            raise GeneratorValidationError(
                generator=cls.name,
                field="path",
                message="page path 必須以 .html 結尾",
            )

        return normalized

    @classmethod
    def _validate_content(
        cls,
        value: object,
    ) -> str:
        """Validate authored page content without changing it."""
        if not isinstance(value, str):
            raise GeneratorValidationError(
                generator=cls.name,
                field="content",
                message="content 必須是字串",
            )

        return value

    @classmethod
    def _validate_output_directory(
        cls,
        value: object,
    ) -> Path:
        """Validate the optional relative Website output directory."""
        if not isinstance(value, str):
            raise GeneratorValidationError(
                generator=cls.name,
                field="output_directory",
                message="output_directory 必須是字串",
            )

        candidate = value.strip()

        if not candidate:
            raise GeneratorValidationError(
                generator=cls.name,
                field="output_directory",
                message="output_directory 不可為空",
            )

        posix_path = PurePosixPath(candidate)
        windows_path = PureWindowsPath(candidate)

        if (
            posix_path.is_absolute()
            or windows_path.is_absolute()
            or windows_path.drive
            or ".." in posix_path.parts
            or ".." in windows_path.parts
        ):
            raise GeneratorValidationError(
                generator=cls.name,
                field="output_directory",
                message="output_directory 必須是安全的相對路徑",
            )

        normalized = posix_path.as_posix()

        while normalized.startswith("./"):
            normalized = normalized[2:]

        if not normalized or normalized == ".":
            raise GeneratorValidationError(
                generator=cls.name,
                field="output_directory",
                message="output_directory 不可為空",
            )

        return Path(normalized)

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
