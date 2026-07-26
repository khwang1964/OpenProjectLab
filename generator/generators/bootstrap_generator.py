"""Bootstrap generator implementation for OpenProjectLab."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from generator.core.filesystem import FileSystem
from generator.core.generation_manifest import GenerationManifest
from generator.core.template import TemplateRenderer

_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True, slots=True)
class BootstrapResult:
    project_root: Path
    generated_files: tuple[Path, ...]
    created_directories: tuple[Path, ...]
    dry_run: bool


class BootstrapGenerator:
    name = "bootstrap"
    description = "Generate a complete OpenProjectLab course scaffold"
    TEMPLATE_MANIFEST: Mapping[str, str] = {
        "README.md": "bootstrap/project/README.md.j2",
        "LICENSE": "bootstrap/project/LICENSE.j2",
        "CONTRIBUTING.md": "bootstrap/project/CONTRIBUTING.md.j2",
        ".gitignore": "bootstrap/project/gitignore.j2",
        "course.yaml": "bootstrap/project/course.yaml.j2",
    }
    DIRECTORY_MANIFEST = ("docs", "assets", "templates", "weeks")

    def __init__(
        self,
        template_root: Path | None = None,
        output_root: Path | None = None,
        *,
        filesystem: FileSystem | None = None,
    ):
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
    ) -> BootstrapResult:
        tr = self._resolve_template_root(template_root)
        oroot = self._resolve_output_root(output_root)
        ctx = dict(context or {})
        ctx.update(context_values)
        slug = self._validate_project_slug(project_slug or ctx.get("project_slug"))
        ctx["project_slug"] = slug
        project_root = oroot / slug
        renderer = TemplateRenderer(tr)
        dirs = tuple(project_root / r for r in self.DIRECTORY_MANIFEST)
        rendered = []
        generated = []
        for output_name, template_name in self.TEMPLATE_MANIFEST.items():
            path = project_root / output_name
            rendered.append((path, renderer.render(template_name, ctx)))
            generated.append(path)
        manifest = None
        if record_manifest:
            manifest = GenerationManifest.load(project_root, filesystem=self._filesystem)
            manifest.set_project(slug=slug, name=ctx.get("project_name"))
            for (path, _), template_name in zip(
                rendered, self.TEMPLATE_MANIFEST.values(), strict=False
            ):
                manifest.record(path, generator=self.name, template=template_name)
        if not dry_run:
            for d in dirs:
                self._filesystem.ensure_directory(d)
            for path, content in rendered:
                self._filesystem.write_text(path, content, overwrite=overwrite)
        if manifest is not None:
            manifest.save(dry_run=dry_run)
        return BootstrapResult(project_root, tuple(generated), dirs, dry_run)

    def run(self, output_root=None, context=None, **kwargs):
        return self.generate(output_root, context, **kwargs)

    def _resolve_template_root(self, override):
        result = Path(override) if override else self._template_root
        if result is None:
            raise ValueError("未提供 template_root")
        return result

    def _resolve_output_root(self, override):
        result = Path(override) if override else self._output_root
        if result is None:
            raise ValueError("未提供 output_root")
        return result

    @staticmethod
    def _validate_project_slug(value):
        if not isinstance(value, str) or not value:
            raise ValueError("project_slug 必須是非空字串")
        if not _SLUG_PATTERN.fullmatch(value):
            raise ValueError("project_slug 必須符合 ^[a-z0-9]+(?:-[a-z0-9]+)*$")
        return value
