"""Representative OpenProjectLab v1 reliability end-to-end tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from generator.core.exceptions import GeneratorValidationError
from generator.core.filesystem import write_text
from generator.courseware.composition import CoursewareComposer
from generator.generators.base import BaseGenerator
from generator.generators.course_generator import CourseGenerator
from generator.plugins.registry import GeneratorRegistry
from generator.sdk import (
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
    RuntimeOptions,
    WritePolicy,
)


def _write_course_template(template_root: Path) -> None:
    """Create the minimum real Course template for isolated reliability E2E."""
    template = template_root / "course" / "README.md.j2"
    template.parent.mkdir(parents=True, exist_ok=True)
    template.write_text(
        "# {{ course_name }}\nLanguage: {{ language }}\nWeeks: {{ weeks }}\n",
        encoding="utf-8",
    )


def _bound_course_generator(template_root: Path) -> type[CourseGenerator]:
    """Bind the production CourseGenerator to an isolated template root."""

    class BoundCourseGenerator(CourseGenerator):
        def __init__(self) -> None:
            super().__init__(template_root=template_root)

    BoundCourseGenerator.__name__ = "ReliabilityCourseGenerator"
    BoundCourseGenerator.__qualname__ = BoundCourseGenerator.__name__
    return BoundCourseGenerator


class FailingGenerator(BaseGenerator):
    """Fail after an earlier production Generator has completed."""

    name = "failing"

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        del request
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        del request, plan
        raise RuntimeError("failing generator stopped composition")


class SentinelGenerator(BaseGenerator):
    """Create a sentinel only when incorrectly executed after a failure."""

    name = "sentinel"

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        del plan
        destination = request.target / "sentinel.txt"
        result = write_text(
            destination,
            "sentinel",
            policy=WritePolicy.OVERWRITE,
        )
        return GenerationResult(
            generator_name=self.name,
            writes=(result,),
        )


def _course_request(
    project: Path,
    *,
    generator_name: str = "course",
    overwrite: bool = False,
) -> GenerateRequest:
    """Build a representative production Course request."""
    return GenerateRequest(
        generator_name=generator_name,
        target=project,
        values={
            "course_name": "Modern Java in Action",
            "language": "zh-TW",
            "weeks": 1,
            "record_manifest": False,
        },
        options=RuntimeOptions(overwrite=overwrite),
    )


def test_v1_reliability_e2e_repeated_generation_is_content_stable(
    tmp_path: Path,
) -> None:
    """Repeat equivalent production generation without artifact drift."""
    template_root = tmp_path / "templates"
    project = tmp_path / "course"
    _write_course_template(template_root)
    generator = CourseGenerator(template_root=template_root)

    first = generator.run(_course_request(project))
    first_content = (project / "README.md").read_text(encoding="utf-8")

    second = generator.run(
        _course_request(
            project,
            overwrite=True,
        )
    )
    second_content = (project / "README.md").read_text(encoding="utf-8")

    assert first.generator_name == second.generator_name == "course"
    assert first_content == second_content
    assert second_content == ("# Modern Java in Action\nLanguage: zh-TW\nWeeks: 1\n")
    assert tuple(project.rglob("*.md")) == (project / "README.md",)


def test_v1_reliability_e2e_invalid_request_fails_before_project_output(
    tmp_path: Path,
) -> None:
    """Stop an invalid production request before persistent project mutation."""
    template_root = tmp_path / "templates"
    project = tmp_path / "invalid-course"
    _write_course_template(template_root)
    generator = CourseGenerator(template_root=template_root)

    with pytest.raises(GeneratorValidationError):
        generator.run(
            _course_request(
                project,
                generator_name="week",
            )
        )

    assert not project.exists()


def test_v1_reliability_e2e_composition_fail_fast_preserves_prior_success(
    tmp_path: Path,
) -> None:
    """Keep earlier success, stop later work, and make no rollback promise."""
    template_root = tmp_path / "templates"
    project = tmp_path / "partial-course"
    _write_course_template(template_root)

    registry = GeneratorRegistry()
    registry.register(_bound_course_generator(template_root))
    registry.register(FailingGenerator)
    registry.register(SentinelGenerator)
    composer = CoursewareComposer(registry)

    requests = (
        _course_request(project),
        GenerateRequest(
            generator_name="failing",
            target=project,
        ),
        GenerateRequest(
            generator_name="sentinel",
            target=project,
        ),
    )

    with pytest.raises(RuntimeError, match="failing generator"):
        composer.run(requests)

    course_readme = project / "README.md"
    sentinel = project / "sentinel.txt"

    assert course_readme.exists()
    assert "Modern Java in Action" in course_readme.read_text(encoding="utf-8")
    assert not sentinel.exists()
