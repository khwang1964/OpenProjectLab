"""Guard the Step 8.4 canonical runtime-template migration."""

from __future__ import annotations

from pathlib import Path

import generator
from generator.resources import package_template_root


def test_v1_canonical_template_root_is_inside_generator_package() -> None:
    generator_root = Path(generator.__file__).resolve().parent
    template_root = package_template_root().resolve()

    assert generator_root in template_root.parents


def test_v1_legacy_repository_template_root_is_not_required() -> None:
    project_root = Path(__file__).resolve().parents[2]
    legacy_root = project_root / "templates"

    assert package_template_root().resolve() != legacy_root.resolve()
