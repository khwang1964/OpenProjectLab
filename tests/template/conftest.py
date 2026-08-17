from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from generator.resources import package_template_root

TEMPLATE_ROOT = package_template_root()
MANIFEST_PATH = TEMPLATE_ROOT / "manifest.yaml"


@pytest.fixture(scope="session")
def template_root() -> Path:
    """Return the canonical package-owned runtime template root."""
    return TEMPLATE_ROOT


@pytest.fixture(scope="session")
def template_manifest() -> dict[str, Any]:
    """Load the canonical package-owned Template Manifest."""
    assert MANIFEST_PATH.is_file(), f"找不到 Template Manifest：{MANIFEST_PATH}"
    data = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "Template Manifest 頂層必須是 mapping"
    return data


@pytest.fixture(scope="session")
def template_environment(template_root: Path) -> Environment:
    """Build the shared Jinja environment from package-owned resources."""
    return Environment(
        loader=FileSystemLoader(str(template_root)),
        undefined=StrictUndefined,
        autoescape=False,
        keep_trailing_newline=True,
    )
