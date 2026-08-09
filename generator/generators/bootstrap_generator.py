"""Bootstrap generator implementation for OpenProjectLab."""

from __future__ import annotations

import re
from collections.abc import Mapping
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

_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class BootstrapGenerator(BaseGenerator):
    """Generate a complete OpenProjectLab course scaffold."""

    name = "bootstrap"
    description = "Generate a complete OpenProjectLab course scaffold"

    TEMPLATE_MANIFEST: Mapping[str, str] = {
        "README.md": "bootstrap/project/README.md.j2",
        "LICENSE": "bootstrap/project/LICENSE.j2",
        "CONTRIBUTING.md": "bootstrap/project/CONTRIBUTING.md.j2",
        ".gitignore": "bootstrap/project/gitignore.j2",
        "course.yaml": "bootstrap/project/course.yaml.j2",
    }

    DIRECTORY_MANIFEST = (
        "docs",
        "assets",
        "templates",
        "weeks",
    )

    def __init__(
        self,
        template_root: Path | None = None,
        output_root: Path | None = None,
        *,
        filesystem: FileSystem | None = None,
    ) -> None:
        """Initialize the generator dependencies and default roots."""
        super().__init__()
        self._template_root = Path(template_root) if template_root else None
        self._output_root = Path(output_root) if output_root else None
        self._filesystem = filesystem or FileSystem()

    def validate_request(self, request: GenerateRequest) -> None:
        """Validate a Bootstrap request before planning."""
        self._validate_generator_name(request.generator_name)
        self._resolve_template_root()
        self._validate_project_slug(request.values.get("project_slug"))

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Build an immutable plan for Bootstrap template outputs."""
        resolved_context = dict(request.values)
        slug = self._validate_project_slug(
            resolved_context.get("project_slug"),
        )
        resolved_context["project_slug"] = slug

        project_root = request.target / slug
        operations = tuple(
            GenerationOperation(
                template_name=template_name,
                destination=project_root / output_name,
                context=resolved_context,
                write_policy=request.options.write_policy,
            )
            for output_name, template_name in self.TEMPLATE_MANIFEST.items()
        )

        return GenerationPlan(
            generator_name=self.name,
            operations=operations,
        )

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Execute a previously validated Bootstrap generation plan."""
        resolved_template_root = self._resolve_template_root()
        renderer = TemplateRenderer(resolved_template_root)

        rendered_files = tuple(
            (
                operation.destination,
                operation.template_name,
                renderer.render(
                    operation.template_name,
                    operation.context,
                ),
            )
            for operation in plan.operations
        )

        project_slug = self._validate_project_slug(
            request.values.get("project_slug"),
        )
        project_root = request.target / project_slug

        directories = tuple(
            project_root / relative_path for relative_path in self.DIRECTORY_MANIFEST
        )

        manifest = self._prepare_manifest(
            project_root=project_root,
            project_slug=project_slug,
            project_name=request.values.get("project_name"),
            rendered_files=rendered_files,
            record_manifest=bool(
                request.values.get("record_manifest", True),
            ),
        )

        for directory in directories:
            self._filesystem.ensure_directory(
                directory,
                dry_run=request.options.dry_run,
            )

        writes: list[WriteResult] = []

        for operation, (_, _, content) in zip(
            plan.operations,
            rendered_files,
            strict=True,
        ):
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

    def _prepare_manifest(
        self,
        *,
        project_root: Path,
        project_slug: str,
        project_name: object,
        rendered_files: tuple[tuple[Path, str, str], ...],
        record_manifest: bool,
    ) -> GenerationManifest | None:
        """Prepare the generation manifest when recording is enabled."""
        if not record_manifest:
            return None

        manifest = GenerationManifest.load(
            project_root,
            filesystem=self._filesystem,
        )
        manifest.set_project(
            slug=project_slug,
            name=project_name,
        )

        for path, template_name, _ in rendered_files:
            manifest.record(
                path,
                generator=self.name,
                template=template_name,
            )

        return manifest

    def _resolve_template_root(
        self,
    ) -> Path:
        """Resolve the effective template root."""
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
    def _validate_project_slug(cls, value: object) -> str:
        """Validate and return a normalized project slug."""
        if not isinstance(value, str) or not value:
            raise GeneratorValidationError(
                generator=cls.name,
                field="project_slug",
                message="project_slug 必須是非空字串",
            )

        if not _SLUG_PATTERN.fullmatch(value):
            raise GeneratorValidationError(
                generator=cls.name,
                field="project_slug",
                message="project_slug 必須符合 ^[a-z0-9]+(?:-[a-z0-9]+)*$",
            )

        return value
