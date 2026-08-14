"""Representative integration tests for Courseware Composition."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from generator.core.exceptions import GeneratorValidationError, PluginError
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


def _write_templates(root: Path) -> None:
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
    """Bind a production generator class to the local integration templates."""

    class _BoundGenerator(generator_class):  # type: ignore[misc, valid-type]
        def __init__(self) -> None:
            super().__init__(template_root=template_root)

    _BoundGenerator.__name__ = f"Bound{generator_class.__name__}"
    _BoundGenerator.__qualname__ = _BoundGenerator.__name__
    return _BoundGenerator


def _registry(template_root: Path) -> GeneratorRegistry:
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

    return registry


def _options(
    *,
    dry_run: bool = False,
    overwrite: bool = False,
) -> RuntimeOptions:
    return RuntimeOptions(
        dry_run=dry_run,
        overwrite=overwrite,
    )


def _requests(
    project: Path,
    *,
    dry_run: bool = False,
    overwrite: bool = False,
    record_manifest: bool = True,
) -> tuple[GenerateRequest, ...]:
    options = _options(
        dry_run=dry_run,
        overwrite=overwrite,
    )

    common = {
        "course_name": "Modern Java in Action",
        "record_manifest": record_manifest,
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


@pytest.fixture
def composition_environment(
    tmp_path: Path,
) -> tuple[CoursewareComposer, Path, Path]:
    template_root = tmp_path / "templates"
    project = tmp_path / "sample-course"
    _write_templates(template_root)

    return CoursewareComposer(_registry(template_root)), template_root, project


def test_representative_courseware_composition_generates_expected_artifact_tree(
    composition_environment: tuple[CoursewareComposer, Path, Path],
) -> None:
    composer, _template_root, project = composition_environment

    results = composer.run(
        _requests(
            project,
            record_manifest=False,
        )
    )

    expected_order = (
        "course",
        "week",
        "lab",
        "quiz",
        "assignment",
        "slides",
        "website",
    )

    assert isinstance(results, tuple)
    assert all(isinstance(result, GenerationResult) for result in results)
    assert tuple(result.generator_name for result in results) == expected_order

    expected_files = (
        project / "README.md",
        project / "week-01" / "README.md",
        project / "week-01" / "lab" / "reactive-basics" / "README.md",
        project / "week-01" / "quiz" / "reactive-basics" / "README.md",
        project / "week-01" / "assignment" / "reactive-homework" / "README.md",
        project / "slides.md",
        project / "site" / "index.html",
        project / "site" / "weeks" / "week-01.html",
    )

    assert all(path.exists() for path in expected_files)

    assert "# Modern Java in Action" in (project / "README.md").read_text(encoding="utf-8")
    assert "# Week 1: Reactive Programming" in (project / "week-01" / "README.md").read_text(
        encoding="utf-8"
    )
    assert "Reactive Streams Basics" in (
        project / "week-01" / "lab" / "reactive-basics" / "README.md"
    ).read_text(encoding="utf-8")

    quiz = (project / "week-01" / "quiz" / "reactive-basics" / "README.md").read_text(
        encoding="utf-8"
    )
    assert "Which concept controls producer pressure?" in quiz
    assert "correct_answer" not in quiz

    assert "Reactive Programming Homework" in (
        project / "week-01" / "assignment" / "reactive-homework" / "README.md"
    ).read_text(encoding="utf-8")

    slides = (project / "slides.md").read_text(encoding="utf-8")
    assert "# Week 01: Reactive Programming" in slides
    assert "## Learning Objectives" in slides
    assert slides.index("## Learning Objectives") < slides.index("## Core Concepts")

    website = (project / "site" / "index.html").read_text(encoding="utf-8")
    assert "<!doctype html>" in website
    assert "/index.html" in website
    assert "/weeks/week-01.html" in website
    assert website.index("/index.html") < website.index("/weeks/week-01.html")


def test_representative_composition_preserves_existing_manifest_infrastructure(
    composition_environment: tuple[CoursewareComposer, Path, Path],
) -> None:
    composer, _template_root, project = composition_environment

    results = composer.run(_requests(project))

    manifest_path = project / ".opl" / "manifest.yaml"
    assert manifest_path.exists()

    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    generated = data["generated"]

    expected_paths = {
        "README.md",
        "week-01/README.md",
        "week-01/lab/reactive-basics/README.md",
        "week-01/quiz/reactive-basics/README.md",
        "week-01/assignment/reactive-homework/README.md",
        "slides.md",
        "site/index.html",
        "site/weeks/week-01.html",
    }

    assert expected_paths.issubset({item["path"] for item in generated})
    assert {item["generator"] for item in generated if item["path"] in expected_paths} == {
        "course",
        "week",
        "lab",
        "quiz",
        "assignment",
        "slides",
        "website",
    }
    assert all(result.manifest_updated for result in results)


def test_representative_composition_dry_run_has_no_persistent_side_effects(
    composition_environment: tuple[CoursewareComposer, Path, Path],
) -> None:
    composer, _template_root, project = composition_environment

    results = composer.run(
        _requests(
            project,
            dry_run=True,
        )
    )

    assert tuple(result.generator_name for result in results) == (
        "course",
        "week",
        "lab",
        "quiz",
        "assignment",
        "slides",
        "website",
    )
    assert all(result.dry_run for result in results)
    assert all(result.manifest_updated is False for result in results)
    assert not project.exists()


def test_composition_preflight_missing_generator_prevents_all_real_execution(
    composition_environment: tuple[CoursewareComposer, Path, Path],
) -> None:
    composer, _template_root, project = composition_environment
    requests = list(
        _requests(
            project,
            record_manifest=False,
        )
    )
    requests.insert(
        1,
        GenerateRequest(
            generator_name="missing-generator",
            target=project,
            values={
                "record_manifest": False,
            },
        ),
    )

    with pytest.raises((PluginError, RuntimeError), match="missing-generator"):
        composer.run(requests)

    assert not project.exists()


def test_real_generator_failure_is_fail_fast_without_cross_generator_rollback(
    composition_environment: tuple[CoursewareComposer, Path, Path],
) -> None:
    composer, _template_root, project = composition_environment
    requests = list(
        _requests(
            project,
            record_manifest=False,
        )
    )

    # Course succeeds first. Week then fails validation. Everything after Week
    # must remain unexecuted, while Course output is intentionally not rolled
    # back because ADR 0020 defines non-transactional fail-fast composition.
    requests[1] = GenerateRequest(
        generator_name="week",
        target=project,
        values={
            "course_name": "Modern Java in Action",
            "week": 0,
            "title": "Invalid Week",
            "record_manifest": False,
        },
    )

    with pytest.raises(
        (GeneratorValidationError, RuntimeError),
    ) as exc_info:
        composer.run(requests)

    assert "week" in str(exc_info.value).lower()
    assert (project / "README.md").exists()
    assert not (project / "week-01").exists()
    assert not (project / "slides.md").exists()
    assert not (project / "site").exists()


def test_representative_composition_respects_overwrite_policy(
    composition_environment: tuple[CoursewareComposer, Path, Path],
) -> None:
    composer, _template_root, project = composition_environment

    composer.run(
        _requests(
            project,
            record_manifest=False,
        )
    )

    original_course = (project / "README.md").read_text(encoding="utf-8")

    with pytest.raises((RuntimeError, OSError)):
        composer.run(
            _requests(
                project,
                overwrite=False,
                record_manifest=False,
            )
        )

    assert (project / "README.md").read_text(encoding="utf-8") == original_course

    results = composer.run(
        _requests(
            project,
            overwrite=True,
            record_manifest=False,
        )
    )

    assert tuple(result.generator_name for result in results) == (
        "course",
        "week",
        "lab",
        "quiz",
        "assignment",
        "slides",
        "website",
    )
    assert all(result.dry_run is False for result in results)
