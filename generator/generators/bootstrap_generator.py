"""Bootstrap generator implementation for OpenProjectLab."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path

from generator.core.filesystem import FileSystem
from generator.core.generation_manifest import GenerationManifest
from generator.core.models import GenerateRequest, GenerationResult, WriteResult
from generator.core.template import TemplateRenderer

_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class BootstrapGenerator:
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
        self._template_root = Path(template_root) if template_root else None
        self._output_root = Path(output_root) if output_root else None
        self._filesystem = filesystem or FileSystem()

    def generate(
        self,
        request: GenerateRequest,
    ) -> GenerationResult:
        """Generate a project scaffold from the shared request contract."""
        self._validate_generator_name(request.generator_name)

        resolved_template_root = self._resolve_template_root()
        resolved_context = dict(request.values)

        slug = self._validate_project_slug(
            resolved_context.get("project_slug"),
        )
        resolved_context["project_slug"] = slug

        project_root = request.target / slug
        renderer = TemplateRenderer(resolved_template_root)

        directories = tuple(
            project_root / relative_path for relative_path in self.DIRECTORY_MANIFEST
        )

        rendered_files = tuple(
            (
                project_root / output_name,
                template_name,
                renderer.render(template_name, resolved_context),
            )
            for output_name, template_name in self.TEMPLATE_MANIFEST.items()
        )

        manifest = self._prepare_manifest(
            project_root=project_root,
            project_slug=slug,
            project_name=resolved_context.get("project_name"),
            rendered_files=rendered_files,
            record_manifest=bool(resolved_context.get("record_manifest", True)),
        )

        for directory in directories:
            self._filesystem.ensure_directory(
                directory,
                dry_run=request.options.dry_run,
            )

        writes: list[WriteResult] = []

        for path, _, content in rendered_files:
            write_result = self._filesystem.write_text(
                path,
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
            manifest_updated=manifest is not None and not request.options.dry_run,
        )

    def run(self, request: GenerateRequest) -> GenerationResult:
        """Run the canonical generation lifecycle for one request."""
        return self.generate(request)

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
            raise ValueError("未提供 template_root")

        return self._template_root

    def _validate_generator_name(self, generator_name: str) -> None:
        """Reject requests addressed to a different generator."""
        if generator_name != self.name:
            raise ValueError(
                f"generator_name 必須是 {self.name!r}，收到 {generator_name!r}",
            )

    @staticmethod
    def _validate_project_slug(value: object) -> str:
        """Validate and return a normalized project slug."""
        if not isinstance(value, str) or not value:
            raise ValueError("project_slug 必須是非空字串")

        if not _SLUG_PATTERN.fullmatch(value):
            raise ValueError("project_slug 必須符合 ^[a-z0-9]+(?:-[a-z0-9]+)*$")

        return value
