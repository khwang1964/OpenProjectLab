import pytest
import yaml

from generator.core.generation_manifest import (
    SCHEMA_VERSION,
    GenerationManifest,
    GenerationManifestError,
)


def test_new_manifest_defaults(tmp_path):
    manifest = GenerationManifest.load(tmp_path)
    assert manifest.schema_version == SCHEMA_VERSION
    assert manifest.entries == ()


def test_record_save_and_load_unicode(tmp_path):
    m = GenerationManifest(tmp_path, project={"slug": "modern-java", "name": "現代 Java"})
    m.record(
        tmp_path / "week-01" / "README.md",
        generator="week",
        template="week/README.md.j2",
        metadata={"week": 1, "title": "課程介紹"},
    )
    path = m.save()
    assert path.exists()
    loaded = GenerationManifest.load(tmp_path)
    assert loaded.project["name"] == "現代 Java"
    assert loaded.entries[0].metadata["title"] == "課程介紹"


def test_same_path_updates_instead_of_duplicates(tmp_path):
    m = GenerationManifest(tmp_path)
    m.record("README.md", generator="bootstrap", template="a.j2")
    m.record("README.md", generator="course", template="b.j2")
    assert len(m.entries) == 1 and m.entries[0].generator == "course"


@pytest.mark.parametrize("bad", ["../secret", "a/../../secret", "/absolute", ""])
def test_rejects_unsafe_paths(tmp_path, bad):
    with pytest.raises(GenerationManifestError):
        GenerationManifest(tmp_path).record(bad, generator="x", template="x.j2")


def test_rejects_absolute_path_outside_project(tmp_path):
    with pytest.raises(GenerationManifestError):
        GenerationManifest(tmp_path / "project").record(
            tmp_path / "outside.txt", generator="x", template="x.j2"
        )


def test_rejects_unsupported_schema(tmp_path):
    with pytest.raises(GenerationManifestError):
        GenerationManifest(tmp_path, schema_version="2.0")


def test_rejects_invalid_yaml(tmp_path):
    path = tmp_path / ".opl" / "manifest.yaml"
    path.parent.mkdir()
    path.write_text("generated: [", encoding="utf-8")
    with pytest.raises(GenerationManifestError):
        GenerationManifest.load(tmp_path)


def test_rejects_missing_required_entry_field(tmp_path):
    path = tmp_path / ".opl" / "manifest.yaml"
    path.parent.mkdir()
    path.write_text(
        "schema_version: '1.0'\nproject: {}\ngenerated:\n  - path: README.md\n", encoding="utf-8"
    )
    with pytest.raises(GenerationManifestError):
        GenerationManifest.load(tmp_path)


def test_dry_run_has_no_side_effect(tmp_path):
    m = GenerationManifest(tmp_path)
    m.record("README.md", generator="course", template="course/README.md.j2")
    assert m.save(dry_run=True) == tmp_path / ".opl" / "manifest.yaml"
    assert not (tmp_path / ".opl").exists()


def test_yaml_shape(tmp_path):
    m = GenerationManifest(tmp_path, project={"slug": "x"})
    m.record("README.md", generator="course", template="course/README.md.j2")
    m.save()
    data = yaml.safe_load(m.path.read_text(encoding="utf-8"))
    assert list(data) == ["schema_version", "project", "generated"]
