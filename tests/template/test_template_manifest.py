from __future__ import annotations


def test_template_manifest_schema(template_manifest: dict) -> None:
    assert template_manifest["schema_version"] == "2.0"
    assert template_manifest["name"] == "OpenProjectLab Template Pack"
    assert template_manifest["version"] == "2.0.0"
    assert template_manifest["encoding"] == "UTF-8"

    templates = template_manifest["templates"]
    assert isinstance(templates, list)
    assert templates


def test_template_manifest_entries_have_required_fields(
    template_manifest: dict,
) -> None:
    for item in template_manifest["templates"]:
        assert isinstance(item, dict)
        assert isinstance(item.get("path"), str)
        assert item["path"]
        assert isinstance(item.get("generator"), str)
        assert item["generator"]
        assert isinstance(item.get("required"), list)


def test_template_manifest_paths_are_unique(
    template_manifest: dict,
) -> None:
    paths = [item["path"] for item in template_manifest["templates"]]
    assert len(paths) == len(set(paths))


def test_template_manifest_generators_are_known(
    template_manifest: dict,
) -> None:
    allowed = {
        "bootstrap",
        "course",
        "week",
        "lab",
        "assignment",
        "quiz",
        "slides",
        "website",
        "shared",
    }
    actual = {item["generator"] for item in template_manifest["templates"]}
    assert actual <= allowed
