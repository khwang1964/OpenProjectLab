"""Test generation-manifest persistence, validation, and write results."""

from pathlib import Path
from typing import Any

import pytest
import yaml

from generator.core.generation_manifest import (
    SCHEMA_VERSION,
    GenerationManifest,
    GenerationManifestError,
)
from generator.core.models import WriteStatus


def test_new_manifest_defaults(tmp_path: Path) -> None:
    """Load a new manifest with the current schema and no entries."""
    manifest = GenerationManifest.load(tmp_path)

    assert manifest.schema_version == SCHEMA_VERSION
    assert manifest.entries == ()


def test_record_save_and_load_unicode(tmp_path: Path) -> None:
    """Save and reload Unicode project and entry metadata."""
    manifest = GenerationManifest(
        tmp_path,
        project={
            "slug": "modern-java",
            "name": "現代 Java",
        },
    )
    manifest.record(
        tmp_path / "week-01" / "README.md",
        generator="week",
        template="week/README.md.j2",
        metadata={
            "week": 1,
            "title": "課程介紹",
        },
    )

    result = manifest.save()

    assert result.path == tmp_path / ".opl" / "manifest.yaml"
    assert result.status is WriteStatus.CREATED
    assert result.path.exists()

    loaded = GenerationManifest.load(tmp_path)

    assert loaded.project["name"] == "現代 Java"
    assert loaded.entries[0].metadata["title"] == "課程介紹"


def test_same_path_updates_instead_of_duplicates(
    tmp_path: Path,
) -> None:
    """Replace an existing entry when recording the same path."""
    manifest = GenerationManifest(tmp_path)
    manifest.record(
        "README.md",
        generator="bootstrap",
        template="a.j2",
    )
    manifest.record(
        "README.md",
        generator="course",
        template="b.j2",
    )

    assert len(manifest.entries) == 1
    assert manifest.entries[0].generator == "course"
    assert manifest.entries[0].template == "b.j2"


@pytest.mark.parametrize(
    "bad_path",
    [
        "../secret",
        "a/../../secret",
        "/absolute",
        "",
    ],
)
def test_rejects_unsafe_paths(
    tmp_path: Path,
    bad_path: str,
) -> None:
    """Reject unsafe relative and absolute generated paths."""
    with pytest.raises(GenerationManifestError):
        GenerationManifest(tmp_path).record(
            bad_path,
            generator="x",
            template="x.j2",
        )


def test_rejects_absolute_path_outside_project(
    tmp_path: Path,
) -> None:
    """Reject an absolute generated path outside the project root."""
    project_root = tmp_path / "project"
    outside_path = tmp_path / "outside.txt"

    with pytest.raises(GenerationManifestError):
        GenerationManifest(project_root).record(
            outside_path,
            generator="x",
            template="x.j2",
        )


def test_rejects_unsupported_schema(tmp_path: Path) -> None:
    """Reject a manifest using an unsupported schema version."""
    with pytest.raises(GenerationManifestError):
        GenerationManifest(
            tmp_path,
            schema_version="2.0",
        )


def test_rejects_invalid_yaml(tmp_path: Path) -> None:
    """Reject a manifest file containing invalid YAML."""
    path = tmp_path / ".opl" / "manifest.yaml"
    path.parent.mkdir()
    path.write_text(
        "generated: [",
        encoding="utf-8",
    )

    with pytest.raises(GenerationManifestError):
        GenerationManifest.load(tmp_path)


def test_rejects_missing_required_entry_field(
    tmp_path: Path,
) -> None:
    """Reject a manifest entry missing required fields."""
    path = tmp_path / ".opl" / "manifest.yaml"
    path.parent.mkdir()
    path.write_text(
        ("schema_version: '1.0'\nproject: {}\ngenerated:\n  - path: README.md\n"),
        encoding="utf-8",
    )

    with pytest.raises(GenerationManifestError):
        GenerationManifest.load(tmp_path)


def test_dry_run_has_no_side_effect(tmp_path: Path) -> None:
    """Return a created result without writing during a dry run."""
    manifest = GenerationManifest(tmp_path)
    manifest.record(
        "README.md",
        generator="course",
        template="course/README.md.j2",
    )
    expected_path = tmp_path / ".opl" / "manifest.yaml"

    result = manifest.save(dry_run=True)

    assert result.path == expected_path
    assert result.status is WriteStatus.CREATED
    assert not expected_path.exists()
    assert not expected_path.parent.exists()


def test_yaml_shape(tmp_path: Path) -> None:
    """Persist YAML keys in the documented top-level order."""
    manifest = GenerationManifest(
        tmp_path,
        project={"slug": "x"},
    )
    manifest.record(
        "README.md",
        generator="course",
        template="course/README.md.j2",
    )

    result = manifest.save()
    data: dict[str, Any] = yaml.safe_load(result.path.read_text(encoding="utf-8"))

    assert result.status is WriteStatus.CREATED
    assert list(data) == [
        "schema_version",
        "project",
        "generated",
    ]
