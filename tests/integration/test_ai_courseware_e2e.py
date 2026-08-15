"""Milestone 6 representative deterministic AI-to-courseware E2E tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from generator.ai.course_builder import AICourseBuilder, AICourseBuildRequest
from generator.ai.errors import AIResponseValidationError
from generator.ai.models import AIResponse
from generator.ai.testing import FakeAIProvider
from generator.core.models import GenerateRequest, GenerationResult, RuntimeOptions
from generator.courseware.composition import CoursewareComposer
from generator.courseware.models import Course
from generator.generators.base import BaseGenerator
from generator.generators.course_generator import CourseGenerator
from generator.generators.week_generator import WeekGenerator
from generator.plugins.registry import GeneratorRegistry

EXPECTED_ARTIFACT_PATHS = (
    "README.md",
    "week-01/README.md",
    "week-02/README.md",
)

EXPECTED_GENERATOR_ORDER = (
    "course",
    "week",
    "week",
)


def _build_request() -> AICourseBuildRequest:
    return AICourseBuildRequest(
        course_id="modern-java",
        title="Modern Java",
        language="zh-TW",
        objectives=(
            "Understand modern Java language features.",
            "Apply streams and functional programming.",
        ),
        week_count=2,
    )


def _ai_response() -> AIResponse:
    return AIResponse(
        content={
            "course_id": "modern-java",
            "title": "Modern Java",
            "language": "zh-TW",
            "weeks": [
                {
                    "number": 2,
                    "title": "Streams",
                },
                {
                    "number": 1,
                    "title": "Lambda Expressions",
                },
            ],
        },
        metadata={
            "provider": "fake",
            "model": "deterministic-test-model",
        },
    )


def _write_templates(root: Path) -> None:
    templates = {
        "course/README.md.j2": """# {{ course_name }}
Language: {{ language }}
Weeks: {{ weeks }}
""",
        "week/README.md.j2": """# Week {{ week }}: {{ title }}
Course: {{ course_name }}
""",
    }

    for relative_path, body in templates.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")


def _bound_generator[GeneratorT: BaseGenerator](
    generator_class: type[GeneratorT],
    template_root: Path,
) -> type[GeneratorT]:
    class _BoundGenerator(generator_class):  # type: ignore[misc, valid-type]
        def __init__(self) -> None:
            super().__init__(template_root=template_root)

    _BoundGenerator.__name__ = f"AIE2E{generator_class.__name__}"
    _BoundGenerator.__qualname__ = _BoundGenerator.__name__
    return _BoundGenerator


def _composer(template_root: Path) -> CoursewareComposer:
    registry = GeneratorRegistry()

    for generator_class in (
        CourseGenerator,
        WeekGenerator,
    ):
        registry.register(_bound_generator(generator_class, template_root))

    return CoursewareComposer(registry)


def _build_course(
    provider: FakeAIProvider,
) -> Course:
    return AICourseBuilder(
        provider=provider,
    ).build(_build_request())


def _composition_requests(
    course: Course,
    project: Path,
    *,
    dry_run: bool = False,
) -> tuple[GenerateRequest, ...]:
    options = RuntimeOptions(
        dry_run=dry_run,
        overwrite=False,
    )
    common = {
        "course_name": course.title,
        "record_manifest": True,
    }

    return (
        GenerateRequest(
            generator_name="course",
            target=project,
            values={
                **common,
                "course_id": course.course_id,
                "title": course.title,
                "language": course.language,
                "weeks": len(course.weeks),
            },
            options=options,
        ),
        *(
            GenerateRequest(
                generator_name="week",
                target=project,
                values={
                    **common,
                    "week": week.number,
                    "title": week.title,
                    "language": course.language,
                },
                options=options,
            )
            for week in course.weeks
        ),
    )


def _generated_artifact_paths(project: Path) -> tuple[str, ...]:
    ignored_parts = {".opl"}

    return tuple(
        path.relative_to(project).as_posix()
        for path in sorted(project.rglob("*"))
        if path.is_file() and ignored_parts.isdisjoint(path.relative_to(project).parts)
    )


def _artifact_snapshot(project: Path) -> dict[str, str]:
    return {
        relative_path: (project / relative_path).read_text(encoding="utf-8")
        for relative_path in _generated_artifact_paths(project)
    }


def test_ai_courseware_e2e_builds_and_composes_production_course(
    tmp_path: Path,
) -> None:
    template_root = tmp_path / "templates"
    project = tmp_path / "modern-java"
    _write_templates(template_root)

    provider = FakeAIProvider(
        responses=(_ai_response(),),
    )

    course = _build_course(provider)
    results = _composer(template_root).run(
        _composition_requests(
            course,
            project,
        )
    )

    assert len(provider.requests) == 1
    assert provider.requests[0].task == "courseware.build"
    assert provider.requests[0].response_contract == "courseware.course.v1"

    assert course.course_id == "modern-java"
    assert course.title == "Modern Java"
    assert course.language == "zh-TW"
    assert tuple(week.number for week in course.weeks) == (1, 2)
    assert tuple(week.title for week in course.weeks) == (
        "Lambda Expressions",
        "Streams",
    )

    assert isinstance(results, tuple)
    assert all(isinstance(result, GenerationResult) for result in results)
    assert tuple(result.generator_name for result in results) == (EXPECTED_GENERATOR_ORDER)
    assert all(result.dry_run is False for result in results)
    assert all(result.manifest_updated for result in results)

    assert _generated_artifact_paths(project) == EXPECTED_ARTIFACT_PATHS

    course_artifact = (project / "README.md").read_text(encoding="utf-8")
    week_one = (project / "week-01" / "README.md").read_text(encoding="utf-8")
    week_two = (project / "week-02" / "README.md").read_text(encoding="utf-8")

    assert "# Modern Java" in course_artifact
    assert "Language: zh-TW" in course_artifact
    assert "Weeks: 2" in course_artifact
    assert "# Week 1: Lambda Expressions" in week_one
    assert "Course: Modern Java" in week_one
    assert "# Week 2: Streams" in week_two
    assert "Course: Modern Java" in week_two


def test_ai_courseware_e2e_is_reproducible(
    tmp_path: Path,
) -> None:
    template_root = tmp_path / "templates"
    first_project = tmp_path / "first-course"
    second_project = tmp_path / "second-course"
    _write_templates(template_root)

    first_course = _build_course(
        FakeAIProvider(
            responses=(_ai_response(),),
        )
    )
    second_course = _build_course(
        FakeAIProvider(
            responses=(_ai_response(),),
        )
    )

    composer = _composer(template_root)

    first_results = composer.run(
        _composition_requests(
            first_course,
            first_project,
        )
    )
    second_results = composer.run(
        _composition_requests(
            second_course,
            second_project,
        )
    )

    assert first_course == second_course
    assert tuple(result.generator_name for result in first_results) == (EXPECTED_GENERATOR_ORDER)
    assert tuple(result.generator_name for result in second_results) == (EXPECTED_GENERATOR_ORDER)
    assert _generated_artifact_paths(first_project) == EXPECTED_ARTIFACT_PATHS
    assert _generated_artifact_paths(second_project) == EXPECTED_ARTIFACT_PATHS
    assert _artifact_snapshot(first_project) == _artifact_snapshot(second_project)


def test_ai_courseware_e2e_dry_run_has_no_persistent_output(
    tmp_path: Path,
) -> None:
    template_root = tmp_path / "templates"
    project = tmp_path / "modern-java-dry-run"
    _write_templates(template_root)

    course = _build_course(
        FakeAIProvider(
            responses=(_ai_response(),),
        )
    )

    results = _composer(template_root).run(
        _composition_requests(
            course,
            project,
            dry_run=True,
        )
    )

    assert tuple(result.generator_name for result in results) == (EXPECTED_GENERATOR_ORDER)
    assert all(result.dry_run for result in results)
    assert all(result.manifest_updated is False for result in results)
    assert not project.exists()


def test_invalid_ai_courseware_fails_before_filesystem_side_effect(
    tmp_path: Path,
) -> None:
    project = tmp_path / "invalid-ai-course"

    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content=None,
                metadata={
                    "provider": "fake",
                    "model": "deterministic-test-model",
                },
            ),
        ),
    )

    with pytest.raises(AIResponseValidationError):
        _build_course(provider)

    assert len(provider.requests) == 1
    assert not project.exists()
    assert list(tmp_path.iterdir()) == []
