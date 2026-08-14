"""Milestone 5 representative end-to-end courseware composition tests."""

from __future__ import annotations

from pathlib import Path

import yaml

from generator.core.models import GenerateRequest, GenerationResult, RuntimeOptions
from generator.courseware.composition import CoursewareComposer
from generator.generators.assignment_generator import AssignmentGenerator
from generator.generators.base import BaseGenerator
from generator.generators.course_generator import CourseGenerator
from generator.generators.lab_generator import LabGenerator
from generator.generators.quiz_generator import QuizGenerator
from generator.generators.slides_generator import SlidesGenerator
from generator.generators.website_generator import WebsiteGenerator
from generator.generators.week_generator import WeekGenerator
from generator.plugins.registry import GeneratorRegistry

EXPECTED_GENERATOR_ORDER = (
    "course",
    "week",
    "lab",
    "quiz",
    "assignment",
    "slides",
    "website",
)

EXPECTED_ARTIFACT_PATHS = (
    "README.md",
    "week-01/README.md",
    "week-01/lab/reactive-basics/README.md",
    "week-01/quiz/reactive-basics/README.md",
    "week-01/assignment/reactive-homework/README.md",
    "slides.md",
    "site/index.html",
    "site/weeks/week-01.html",
)


def _write_representative_templates(root: Path) -> None:
    """Create the minimum real-generator template set for the E2E scenario."""
    templates = {
        "course/README.md.j2": """# {{ course_name }}
Language: {{ language }}
Weeks: {{ weeks }}
""",
        "week/README.md.j2": """# Week {{ week }}: {{ title }}
Course: {{ course_name }}
""",
        "lab/README.md.j2": """# Lab: {{ title }}
Week: {{ week }}
Lab ID: {{ lab_id }}
""",
        "quiz/README.md.j2": """# Quiz: {{ title }}
Week: {{ week }}
{% for question in questions %}
## {{ question.id }} — {{ question.prompt }}
{% for choice in question.choices %}
- {{ choice }}
{% endfor %}
{% endfor %}
""",
        "assignment/README.md.j2": """# Assignment: {{ title }}
Week: {{ week }}
{% if objectives %}
## Objectives
{% for item in objectives %}
- {{ item }}
{% endfor %}
{% endif %}
{% if instructions %}
## Instructions
{{ instructions }}
{% endif %}
{% if deliverables %}
## Deliverables
{% for item in deliverables %}
- {{ item }}
{% endfor %}
{% endif %}
{% if resources %}
## Resources
{% for item in resources %}
- {{ item }}
{% endfor %}
{% endif %}
{% if submission %}
## Submission
{{ submission }}
{% endif %}
""",
        "slides/slides.md.j2": """# {{ title }}
{% for slide in slides %}
---

## {{ slide.title }}
{% for item in slide.content %}
- {{ item }}
{% endfor %}
{% endfor %}
""",
        "website/page.html.j2": """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{{ page.title }} | {{ site_title }}</title>
</head>
<body>
  <header>
    <h1>{{ site_title }}</h1>
    <nav>
      <ul>
{% for item in navigation %}
        <li><a href="/{{ item.path }}">{{ item.title }}</a></li>
{% endfor %}
      </ul>
    </nav>
  </header>
  <main>
    <h2>{{ page.title }}</h2>
    <div>{{ page.content }}</div>
  </main>
</body>
</html>
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
    """Bind a production generator class to the isolated E2E template root."""

    class _BoundGenerator(generator_class):  # type: ignore[misc, valid-type]
        def __init__(self) -> None:
            super().__init__(template_root=template_root)

    _BoundGenerator.__name__ = f"E2E{generator_class.__name__}"
    _BoundGenerator.__qualname__ = _BoundGenerator.__name__
    return _BoundGenerator


def _composer(template_root: Path) -> CoursewareComposer:
    """Build a composer containing all Milestone 5 production generators."""
    registry = GeneratorRegistry()

    for generator_class in (
        CourseGenerator,
        WeekGenerator,
        LabGenerator,
        QuizGenerator,
        AssignmentGenerator,
        SlidesGenerator,
        WebsiteGenerator,
    ):
        registry.register(_bound_generator(generator_class, template_root))

    return CoursewareComposer(registry)


def _representative_requests(
    project: Path,
    *,
    dry_run: bool = False,
    overwrite: bool = False,
) -> tuple[GenerateRequest, ...]:
    """Build the complete representative Milestone 5 courseware request set."""
    options = RuntimeOptions(
        dry_run=dry_run,
        overwrite=overwrite,
    )
    common = {
        "course_name": "Modern Java in Action",
        "record_manifest": True,
    }

    return (
        GenerateRequest(
            generator_name="course",
            target=project,
            values={
                **common,
                "course_id": "modern-java",
                "title": "Modern Java in Action",
                "language": "zh-TW",
                "weeks": 1,
            },
            options=options,
        ),
        GenerateRequest(
            generator_name="week",
            target=project,
            values={
                **common,
                "week": 1,
                "title": "Reactive Programming",
                "language": "zh-TW",
            },
            options=options,
        ),
        GenerateRequest(
            generator_name="lab",
            target=project,
            values={
                **common,
                "week": 1,
                "lab_id": "reactive-basics",
                "title": "Reactive Streams Basics",
            },
            options=options,
        ),
        GenerateRequest(
            generator_name="quiz",
            target=project,
            values={
                **common,
                "week": 1,
                "quiz_id": "reactive-basics",
                "title": "Reactive Programming Quiz",
                "questions": (
                    {
                        "id": "q1",
                        "prompt": "Which concept controls producer pressure?",
                        "choices": (
                            "Backpressure",
                            "Inheritance",
                            "Reflection",
                        ),
                        "correct_answer": "Backpressure",
                    },
                ),
            },
            options=options,
        ),
        GenerateRequest(
            generator_name="assignment",
            target=project,
            values={
                **common,
                "week": 1,
                "assignment_id": "reactive-homework",
                "title": "Reactive Programming Homework",
                "objectives": (
                    "Explain asynchronous data flow.",
                    "Apply backpressure concepts.",
                ),
                "instructions": "Implement a small reactive processing example.",
                "deliverables": (
                    "Source code",
                    "Short explanation",
                ),
                "resources": ("Course notes",),
                "submission": "Submit the repository URL.",
            },
            options=options,
        ),
        GenerateRequest(
            generator_name="slides",
            target=project,
            values={
                **common,
                "title": "Week 01: Reactive Programming",
                "slides": (
                    {
                        "title": "Learning Objectives",
                        "content": (
                            "Understand reactive systems.",
                            "Explain asynchronous data flows.",
                        ),
                    },
                    {
                        "title": "Core Concepts",
                        "content": (
                            "Streams",
                            "Backpressure",
                            "Non-blocking execution",
                        ),
                    },
                ),
            },
            options=options,
        ),
        GenerateRequest(
            generator_name="website",
            target=project,
            values={
                **common,
                "title": "Modern Java in Action",
                "pages": (
                    {
                        "path": "index.html",
                        "title": "Home",
                        "content": "Welcome to Modern Java in Action.",
                    },
                    {
                        "path": "weeks/week-01.html",
                        "title": "Week 01",
                        "content": "Reactive Programming.",
                    },
                ),
            },
            options=options,
        ),
    )


def _generated_artifact_paths(project: Path) -> tuple[str, ...]:
    """Return generated user-facing files in deterministic path order."""
    ignored_parts = {".opl"}
    return tuple(
        path.relative_to(project).as_posix()
        for path in sorted(project.rglob("*"))
        if path.is_file() and ignored_parts.isdisjoint(path.relative_to(project).parts)
    )


def _artifact_snapshot(project: Path) -> dict[str, str]:
    """Capture deterministic user-facing artifact content."""
    return {
        relative_path: (project / relative_path).read_text(encoding="utf-8")
        for relative_path in _generated_artifact_paths(project)
    }


def test_milestone_5_representative_courseware_e2e(
    tmp_path: Path,
) -> None:
    """Generate one complete representative course and verify its repository."""
    template_root = tmp_path / "templates"
    project = tmp_path / "modern-java"
    _write_representative_templates(template_root)

    results = _composer(template_root).run(_representative_requests(project))

    assert isinstance(results, tuple)
    assert all(isinstance(result, GenerationResult) for result in results)
    assert tuple(result.generator_name for result in results) == EXPECTED_GENERATOR_ORDER
    assert all(result.dry_run is False for result in results)
    assert all(result.manifest_updated for result in results)

    assert set(_generated_artifact_paths(project)) == set(EXPECTED_ARTIFACT_PATHS)

    course = (project / "README.md").read_text(encoding="utf-8")
    week = (project / "week-01" / "README.md").read_text(encoding="utf-8")
    lab = (project / "week-01" / "lab" / "reactive-basics" / "README.md").read_text(
        encoding="utf-8"
    )
    quiz = (project / "week-01" / "quiz" / "reactive-basics" / "README.md").read_text(
        encoding="utf-8"
    )
    assignment = (project / "week-01" / "assignment" / "reactive-homework" / "README.md").read_text(
        encoding="utf-8"
    )
    slides = (project / "slides.md").read_text(encoding="utf-8")
    home = (project / "site" / "index.html").read_text(encoding="utf-8")
    website_week = (project / "site" / "weeks" / "week-01.html").read_text(encoding="utf-8")

    assert "# Modern Java in Action" in course
    assert "Language: zh-TW" in course
    assert "# Week 1: Reactive Programming" in week
    assert "Course: Modern Java in Action" in week
    assert "Reactive Streams Basics" in lab
    assert "Which concept controls producer pressure?" in quiz
    assert "correct_answer" not in quiz
    assert "Reactive Programming Homework" in assignment
    assert "Apply backpressure concepts." in assignment
    assert "# Week 01: Reactive Programming" in slides
    assert slides.index("## Learning Objectives") < slides.index("## Core Concepts")
    assert "Welcome to Modern Java in Action." in home
    assert "Reactive Programming." in website_week

    manifest_path = project / ".opl" / "manifest.yaml"
    assert manifest_path.exists()

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    generated = manifest["generated"]
    entries = {
        item["path"]: item["generator"]
        for item in generated
        if item["path"] in EXPECTED_ARTIFACT_PATHS
    }

    assert entries == {
        "README.md": "course",
        "week-01/README.md": "week",
        "week-01/lab/reactive-basics/README.md": "lab",
        "week-01/quiz/reactive-basics/README.md": "quiz",
        "week-01/assignment/reactive-homework/README.md": "assignment",
        "slides.md": "slides",
        "site/index.html": "website",
        "site/weeks/week-01.html": "website",
    }


def test_milestone_5_representative_courseware_e2e_is_reproducible(
    tmp_path: Path,
) -> None:
    """The same course intent must produce the same user-facing repository."""
    template_root = tmp_path / "templates"
    first_project = tmp_path / "first-course"
    second_project = tmp_path / "second-course"
    _write_representative_templates(template_root)
    composer = _composer(template_root)

    first_results = composer.run(_representative_requests(first_project))
    second_results = composer.run(_representative_requests(second_project))

    assert tuple(result.generator_name for result in first_results) == (EXPECTED_GENERATOR_ORDER)
    assert tuple(result.generator_name for result in second_results) == (EXPECTED_GENERATOR_ORDER)
    assert set(_generated_artifact_paths(first_project)) == set(EXPECTED_ARTIFACT_PATHS)
    assert set(_generated_artifact_paths(second_project)) == set(EXPECTED_ARTIFACT_PATHS)
    assert _artifact_snapshot(first_project) == _artifact_snapshot(second_project)


def test_milestone_5_representative_courseware_e2e_dry_run_is_non_persistent(
    tmp_path: Path,
) -> None:
    """A complete representative dry-run must leave no project repository."""
    template_root = tmp_path / "templates"
    project = tmp_path / "modern-java-dry-run"
    _write_representative_templates(template_root)

    results = _composer(template_root).run(
        _representative_requests(
            project,
            dry_run=True,
        )
    )

    assert tuple(result.generator_name for result in results) == EXPECTED_GENERATOR_ORDER
    assert all(result.dry_run for result in results)
    assert all(result.manifest_updated is False for result in results)
    assert not project.exists()
