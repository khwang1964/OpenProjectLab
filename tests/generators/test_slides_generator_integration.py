from pathlib import Path

import yaml

from generator.core.models import GenerateRequest, GenerationResult, RuntimeOptions
from generator.generators.slides_generator import SlidesGenerator


def _templates(root: Path) -> None:
    slides = root / "slides" / "slides.md.j2"
    slides.parent.mkdir(parents=True, exist_ok=True)
    slides.write_text(
        """# {{ title }}
{% for slide in slides %}
---

## {{ slide.title }}
{% for item in slide.content %}
- {{ item }}
{% endfor %}
{% endfor %}
""",
        encoding="utf-8",
    )


def _slides() -> tuple[dict[str, object], ...]:
    return (
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
    )


def _request(
    project: Path,
    *,
    dry_run: bool = False,
    overwrite: bool = False,
    record_manifest: bool = True,
) -> GenerateRequest:
    return GenerateRequest(
        generator_name="slides",
        target=project,
        values={
            "course_name": "Modern Java",
            "title": "Week 01: Reactive Programming",
            "slides": _slides(),
            "record_manifest": record_manifest,
        },
        options=RuntimeOptions(
            dry_run=dry_run,
            overwrite=overwrite,
        ),
    )


def test_slides_generator_renders_expected_primary_artifact(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    result = SlidesGenerator(templates).generate(
        _request(project, record_manifest=False),
    )

    slides_file = project / "slides.md"
    content = slides_file.read_text(encoding="utf-8")

    assert isinstance(result, GenerationResult)
    assert result.generator_name == "slides"
    assert result.dry_run is False
    assert slides_file.exists()
    assert "# Week 01: Reactive Programming" in content
    assert "## Learning Objectives" in content
    assert "Understand reactive systems." in content
    assert "Explain asynchronous data flows." in content
    assert "## Core Concepts" in content
    assert "Streams" in content
    assert "Backpressure" in content
    assert "Non-blocking execution" in content


def test_slides_generator_preserves_slide_and_content_order(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    SlidesGenerator(templates).generate(
        _request(project, record_manifest=False),
    )

    content = (project / "slides.md").read_text(encoding="utf-8")

    objectives = content.index("## Learning Objectives")
    core = content.index("## Core Concepts")
    first_objective = content.index("Understand reactive systems.")
    second_objective = content.index("Explain asynchronous data flows.")
    streams = content.index("Streams")
    backpressure = content.index("Backpressure")
    non_blocking = content.index("Non-blocking execution")

    assert objectives < core
    assert first_objective < second_objective
    assert streams < backpressure < non_blocking


def test_slides_generator_records_existing_manifest_schema(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    result = SlidesGenerator(templates).generate(
        _request(project, overwrite=True),
    )

    manifest_path = project / ".opl" / "manifest.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    item = next(item for item in data["generated"] if item["path"] == "slides.md")

    assert result.manifest_updated is True
    assert item["generator"] == "slides"
    assert item["metadata"] == {
        "title": "Week 01: Reactive Programming",
        "slide_count": 2,
    }


def test_slides_generator_dry_run_does_not_create_artifact_or_manifest(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    result = SlidesGenerator(templates).generate(
        _request(project, dry_run=True),
    )

    assert result.dry_run is True
    assert result.manifest_updated is False
    assert not project.exists()


def test_slides_generator_manifest_can_be_disabled(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    SlidesGenerator(templates).generate(
        _request(project, record_manifest=False),
    )

    assert (project / "slides.md").exists()
    assert not (project / ".opl").exists()


def test_slides_generator_force_overwrites_existing_artifact(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    slides_file = project / "slides.md"
    slides_file.parent.mkdir(parents=True)
    slides_file.write_text("existing", encoding="utf-8")

    SlidesGenerator(templates).generate(
        _request(
            project,
            overwrite=True,
            record_manifest=False,
        ),
    )

    assert slides_file.read_text(encoding="utf-8") != "existing"
