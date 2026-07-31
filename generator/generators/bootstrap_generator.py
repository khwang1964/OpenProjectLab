"""Bootstrap generator implementation for OpenProjectLab."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from generator.core.filesystem import FileSystem
from generator.core.generation_manifest import GenerationManifest
from generator.core.models import GenerationResult, WriteResult
from generator.core.template import TemplateRenderer

_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True, slots=True)
class BootstrapResult(GenerationResult):
    """Provide transitional bootstrap-specific result properties.

    BootstrapGenerator now follows the shared GenerationResult contract.
    These additional properties are retained temporarily for compatibility
    with existing callers and will be removed after migration.
    """

    project_root: Path = Path()
    generated_files: tuple[Path, ...] = ()
    created_directories: tuple[Path, ...] = ()

    def __post_init__(self) -> None:
        """Normalize shared and bootstrap-specific result fields."""
        super(BootstrapResult, self).__post_init__()
        object.__setattr__(self, "project_root", Path(self.project_root))
        object.__setattr__(
            self,
            "generated_files",
            tuple(Path(path) for path in self.generated_files),
        )
        object.__setattr__(
            self,
            "created_directories",
            tuple(Path(path) for path in self.created_directories),
        )


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
        output_root: Path | None = None,
        context: Mapping[str, Any] | None = None,
        *,
        template_root: Path | None = None,
        project_slug: str | None = None,
        overwrite: bool = True,
        dry_run: bool = False,
        record_manifest: bool = True,
        **context_values: Any,
    ) -> GenerationResult:
        """Generate a project scaffold and return the shared result contract."""
        resolved_template_root = self._resolve_template_root(template_root)
        resolved_output_root = self._resolve_output_root(output_root)

        resolved_context = dict(context or {})
        resolved_context.update(context_values)

        slug = self._validate_project_slug(project_slug or resolved_context.get("project_slug"))
        resolved_context["project_slug"] = slug

        project_root = resolved_output_root / slug
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
            record_manifest=record_manifest,
        )

        for directory in directories:
            self._filesystem.ensure_directory(
                directory,
                dry_run=dry_run,
            )

        writes: list[WriteResult] = []

        for path, _, content in rendered_files:
            write_result = self._filesystem.write_text(
                path,
                content,
                overwrite=overwrite,
                dry_run=dry_run,
            )
            writes.append(write_result)

        if manifest is not None:
            manifest.save(dry_run=dry_run)

        generated_files = tuple(path for path, _, _ in rendered_files)

        return BootstrapResult(
            generator_name=self.name,
            writes=tuple(writes),
            dry_run=dry_run,
            manifest_updated=manifest is not None and not dry_run,
            project_root=project_root,
            generated_files=generated_files,
            created_directories=directories,
        )

    def run(
        self,
        output_root: Path | None = None,
        context: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> GenerationResult:
        """Provide a compatibility alias for generate."""
        return self.generate(
            output_root,
            context,
            **kwargs,
        )

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
        override: Path | None,
    ) -> Path:
        """Resolve the effective template root."""
        result = Path(override) if override else self._template_root

        if result is None:
            raise ValueError("未提供 template_root")

        return result

    def _resolve_output_root(
        self,
        override: Path | None,
    ) -> Path:
        """Resolve the effective output root."""
        result = Path(override) if override else self._output_root

        if result is None:
            raise ValueError("未提供 output_root")

        return result

    @staticmethod
    def _validate_project_slug(value: object) -> str:
        """Validate and return a normalized project slug."""
        if not isinstance(value, str) or not value:
            raise ValueError("project_slug 必須是非空字串")

        if not _SLUG_PATTERN.fullmatch(value):
            raise ValueError("project_slug 必須符合 ^[a-z0-9]+(?:-[a-z0-9]+)*$")

        return value
