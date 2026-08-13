from pathlib import Path

import yaml

from generator.core.models import GenerateRequest, GenerationResult, RuntimeOptions
from generator.generators.assignment_generator import AssignmentGenerator


def _templates(root: Path) -> None:
    assignment = root / "assignment" / "README.md.j2"
    assignment.parent.mkdir(parents=True, exist_ok=True)
    assignment.write_text(
        """# 作業：{{ title }}

> Week {{ week_padded }} · Assignment ID: `{{ assignment_id }}`

{% if objectives is defined and objectives %}
## 學習目標

{% for objective in objectives %}
- {{ objective }}
{% endfor %}

{% endif %}
{% if instructions is defined and instructions %}
## 作業說明

{{ instructions }}

{% endif %}
{% if deliverables is defined and deliverables %}
## 繳交內容

{% for deliverable in deliverables %}
- {{ deliverable }}
{% endfor %}

{% endif %}
{% if resources is defined and resources %}
## 參考資源

{% for resource in resources %}
- {{ resource }}
{% endfor %}

{% endif %}
{% if submission is defined and submission %}
## 繳交方式

{{ submission }}

{% endif %}
""",
        encoding="utf-8",
    )


def _request(
    project: Path,
    *,
    dry_run: bool = False,
    overwrite: bool = False,
    record_manifest: bool = True,
) -> GenerateRequest:
    return GenerateRequest(
        generator_name="assignment",
        target=project,
        values={
            "course_name": "Modern Java",
            "week": 4,
            "assignment_id": "streams-homework",
            "title": "Streams Homework",
            "objectives": (
                "Use stream pipelines.",
                "Choose terminal operations.",
            ),
            "instructions": "Complete all tasks.",
            "deliverables": (
                "src/StreamsHomework.java",
                "README.md",
            ),
            "resources": (
                "docs/streams.md",
                "examples/streams.java",
            ),
            "submission": "Submit the requested files.",
            "record_manifest": record_manifest,
        },
        options=RuntimeOptions(
            dry_run=dry_run,
            overwrite=overwrite,
        ),
    )


def test_assignment_generator_renders_expected_primary_artifact(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    result = AssignmentGenerator(templates).generate(
        _request(project, record_manifest=False),
    )

    readme = project / "week-04" / "assignment" / "streams-homework" / "README.md"
    content = readme.read_text(encoding="utf-8")

    assert isinstance(result, GenerationResult)
    assert result.generator_name == "assignment"
    assert result.dry_run is False
    assert readme.exists()
    assert "# 作業：Streams Homework" in content
    assert "Week 04" in content
    assert "Use stream pipelines." in content
    assert "Complete all tasks." in content
    assert "src/StreamsHomework.java" in content
    assert "docs/streams.md" in content
    assert "Submit the requested files." in content


def test_assignment_generator_preserves_structured_order_in_rendered_output(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    AssignmentGenerator(templates).generate(
        _request(project, record_manifest=False),
    )

    readme = project / "week-04" / "assignment" / "streams-homework" / "README.md"
    content = readme.read_text(encoding="utf-8")

    objective_1 = content.index("Use stream pipelines.")
    objective_2 = content.index("Choose terminal operations.")
    deliverable_1 = content.index("src/StreamsHomework.java")
    deliverable_2 = content.index("README.md", deliverable_1)
    resource_1 = content.index("docs/streams.md")
    resource_2 = content.index("examples/streams.java")

    assert objective_1 < objective_2
    assert deliverable_1 < deliverable_2
    assert resource_1 < resource_2


def test_assignment_generator_records_existing_manifest_schema(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    result = AssignmentGenerator(templates).generate(
        _request(project, overwrite=True),
    )

    manifest_path = project / ".opl" / "manifest.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    item = next(
        item
        for item in data["generated"]
        if item["path"] == "week-04/assignment/streams-homework/README.md"
    )

    assert result.manifest_updated is True
    assert item["generator"] == "assignment"
    assert item["metadata"] == {
        "week": 4,
        "assignment_id": "streams-homework",
        "title": "Streams Homework",
    }


def test_assignment_generator_dry_run_does_not_create_artifact_or_manifest(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    result = AssignmentGenerator(templates).generate(
        _request(project, dry_run=True),
    )

    assert result.dry_run is True
    assert result.manifest_updated is False
    assert not project.exists()


def test_assignment_generator_manifest_can_be_disabled(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    AssignmentGenerator(templates).generate(
        _request(project, record_manifest=False),
    )

    assert (project / "week-04" / "assignment" / "streams-homework" / "README.md").exists()
    assert not (project / ".opl").exists()


def test_assignment_generator_force_overwrites_existing_artifact(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    readme = project / "week-04" / "assignment" / "streams-homework" / "README.md"
    readme.parent.mkdir(parents=True)
    readme.write_text("existing", encoding="utf-8")

    AssignmentGenerator(templates).generate(
        _request(
            project,
            overwrite=True,
            record_manifest=False,
        ),
    )

    assert readme.read_text(encoding="utf-8") != "existing"
