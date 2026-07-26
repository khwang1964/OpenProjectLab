from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = PROJECT_ROOT / "templates"
MANIFEST_PATH = TEMPLATE_ROOT / "manifest.yaml"


@pytest.fixture(scope="session")
def template_root() -> Path:
    return TEMPLATE_ROOT


@pytest.fixture(scope="session")
def template_manifest() -> dict[str, Any]:
    assert MANIFEST_PATH.is_file(), f"找不到 Template Manifest：{MANIFEST_PATH}"
    data = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "Template Manifest 頂層必須是 mapping"
    return data


@pytest.fixture(scope="session")
def template_environment(template_root: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(template_root)),
        undefined=StrictUndefined,
        autoescape=False,
        keep_trailing_newline=True,
    )
