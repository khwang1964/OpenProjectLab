"""Freeze the implemented OpenProjectLab v1 configuration contract."""

from pathlib import Path

import pytest

from generator.core.config import ProjectConfig
from generator.core.exceptions import ConfigurationError


def test_v1_config_loads_supported_mapping_sections(tmp_path: Path) -> None:
    """Load the four implemented top-level configuration sections."""
    path = tmp_path / "opl.yaml"
    path.write_text(
        """
project:
  name: Demo
paths:
  templates: custom-templates
generator:
  dry_run: true
plugins:
  enabled: true
""".lstrip(),
        encoding="utf-8",
    )

    config = ProjectConfig.load(path)

    assert config.project == {"name": "Demo"}
    assert config.paths == {"templates": "custom-templates"}
    assert config.generator == {"dry_run": True}
    assert config.plugins == {"enabled": True}


def test_v1_config_missing_sections_default_to_empty_mappings(
    tmp_path: Path,
) -> None:
    """Keep omitted supported sections deterministic and empty."""
    path = tmp_path / "opl.yaml"
    path.write_text("project:\n  name: Demo\n", encoding="utf-8")

    config = ProjectConfig.load(path)

    assert config.project == {"name": "Demo"}
    assert config.paths == {}
    assert config.generator == {}
    assert config.plugins == {}


def test_v1_config_null_sections_normalize_to_empty_mappings(
    tmp_path: Path,
) -> None:
    """Normalize explicit null supported sections to empty mappings."""
    path = tmp_path / "opl.yaml"
    path.write_text(
        """
project:
paths:
generator:
plugins:
""".lstrip(),
        encoding="utf-8",
    )

    config = ProjectConfig.load(path)

    assert config.project == {}
    assert config.paths == {}
    assert config.generator == {}
    assert config.plugins == {}


def test_v1_config_requires_existing_file(tmp_path: Path) -> None:
    """Report missing configuration through ConfigurationError."""
    with pytest.raises(ConfigurationError):
        ProjectConfig.load(tmp_path / "missing.yaml")


def test_v1_config_rejects_non_mapping_root(tmp_path: Path) -> None:
    """Require the YAML document root to be a mapping."""
    path = tmp_path / "opl.yaml"
    path.write_text("- one\n- two\n", encoding="utf-8")

    with pytest.raises(ConfigurationError):
        ProjectConfig.load(path)


@pytest.mark.parametrize(
    "section",
    ["project", "paths", "generator", "plugins"],
)
def test_v1_config_requires_supported_sections_to_be_mappings(
    tmp_path: Path,
    section: str,
) -> None:
    """Reject non-mapping values for implemented configuration sections."""
    path = tmp_path / "opl.yaml"
    path.write_text(f"{section}: invalid\n", encoding="utf-8")

    with pytest.raises(ConfigurationError):
        ProjectConfig.load(path)


def test_v1_template_root_defaults_under_project_root(tmp_path: Path) -> None:
    """Resolve the default templates path relative to the supplied project root."""
    config = ProjectConfig()

    assert config.template_root(tmp_path) == tmp_path / "templates"


def test_v1_template_root_resolves_relative_config_under_project_root(
    tmp_path: Path,
) -> None:
    """Resolve configured relative template paths beneath the project root."""
    config = ProjectConfig(paths={"templates": "course-templates"})

    assert config.template_root(tmp_path) == tmp_path / "course-templates"


def test_v1_template_root_preserves_absolute_config(tmp_path: Path) -> None:
    """Return configured absolute template paths without rebasing them."""
    absolute = (tmp_path / "absolute-templates").resolve()
    config = ProjectConfig(paths={"templates": absolute})

    assert config.template_root(tmp_path / "project") == absolute


def test_v1_template_root_rejects_invalid_configured_type(
    tmp_path: Path,
) -> None:
    """Reject unsupported values for paths.templates."""
    config = ProjectConfig(paths={"templates": 42})

    with pytest.raises(ConfigurationError):
        config.template_root(tmp_path)
