from pathlib import Path

import yaml

from generator.core.models import GenerateRequest, GenerationResult, RuntimeOptions
from generator.generators.lab_generator import LabGenerator


def _templates(root: Path) -> None:
    lab = root / "lab" / "README.md.j2"
    lab.parent.mkdir(parents=True, exist_ok=True)
    lab.write_text(
        "# {{ title }}\nWeek {{ week }}\n",
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
        generator_name="lab",
        target=project,
        values={
            "course_name": "Modern Java",
            "week": 3,
            "lab_id": "streams-practice",
            "title": "Streams Practice",
            "record_manifest": record_manifest,
        },
        options=RuntimeOptions(
            dry_run=dry_run,
            overwrite=overwrite,
        ),
    )


def test_lab_generator_renders_expected_primary_artifact(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    result = LabGenerator(templates).generate(_request(project, record_manifest=False))

    readme = project / "week-03" / "lab" / "streams-practice" / "README.md"

    assert isinstance(result, GenerationResult)
    assert result.generator_name == "lab"
    assert result.dry_run is False
    assert readme.exists()
    assert readme.read_text(encoding="utf-8") == ("# Streams Practice\nWeek 3\n")


def test_lab_generator_records_existing_manifest_schema(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    result = LabGenerator(templates).generate(_request(project, overwrite=True))

    manifest_path = project / ".opl" / "manifest.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    item = next(
        item
        for item in data["generated"]
        if item["path"] == "week-03/lab/streams-practice/README.md"
    )

    assert result.manifest_updated is True
    assert item["generator"] == "lab"
    assert item["metadata"] == {
        "week": 3,
        "lab_id": "streams-practice",
        "title": "Streams Practice",
    }


def test_lab_generator_dry_run_does_not_create_artifact_or_manifest(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    result = LabGenerator(templates).generate(_request(project, dry_run=True))

    assert result.dry_run is True
    assert result.manifest_updated is False
    assert not project.exists()


def test_lab_generator_manifest_can_be_disabled(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    LabGenerator(templates).generate(_request(project, record_manifest=False))

    assert (project / "week-03" / "lab" / "streams-practice" / "README.md").exists()
    assert not (project / ".opl").exists()
