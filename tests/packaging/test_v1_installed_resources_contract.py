"""OpenProjectLab v1 installed runtime-resource contract tests."""

from __future__ import annotations

from pathlib import Path

from generator.cli.main import DEFAULT_TEMPLATE_ROOT
from generator.resources import package_template_root

REQUIRED_TEMPLATE_FAMILIES = (
    "bootstrap",
    "course",
    "week",
    "lab",
    "assignment",
    "quiz",
    "slides",
    "website",
)


def test_v1_generator_exposes_package_owned_template_root() -> None:
    template_root = package_template_root()

    assert isinstance(template_root, Path)
    assert template_root.is_dir()


def test_v1_cli_default_template_root_uses_package_resource_boundary() -> None:
    assert DEFAULT_TEMPLATE_ROOT == package_template_root()


def test_v1_required_template_families_are_packaged() -> None:
    template_root = package_template_root()

    missing = [
        family for family in REQUIRED_TEMPLATE_FAMILIES if not (template_root / family).is_dir()
    ]
    assert missing == []


def test_v1_required_template_families_contain_runtime_files() -> None:
    template_root = package_template_root()

    empty = []
    for family in REQUIRED_TEMPLATE_FAMILIES:
        family_root = template_root / family
        if not family_root.is_dir():
            empty.append(family)
            continue
        if not any(path.is_file() for path in family_root.rglob("*")):
            empty.append(family)

    assert empty == []


def test_v1_runtime_resource_root_is_inside_generator_package() -> None:
    import generator

    generator_root = Path(generator.__file__).resolve().parent
    template_root = package_template_root().resolve()

    assert generator_root in template_root.parents


def test_v1_runtime_resource_root_is_not_legacy_repository_template_root() -> None:
    import generator

    generator_root = Path(generator.__file__).resolve().parent
    legacy_root = generator_root.parent / "templates"

    assert package_template_root().resolve() != legacy_root.resolve()
