from pathlib import Path

import pytest

from generator.core.config import ProjectConfig
from generator.core.exceptions import ConfigurationError


def test_load_valid_config(tmp_path: Path) -> None:
    config_file = tmp_path / "default.yaml"

    config_file.write_text(
        """
project:
  name: OPL Demo

paths:
  templates: templates

generator:
  overwrite: false

plugins: {}
""".strip(),
        encoding="utf-8",
    )

    config = ProjectConfig.load(config_file)

    assert config.project["name"] == "OPL Demo"
    assert config.paths["templates"] == "templates"


def test_missing_config_raises_error(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.yaml"

    with pytest.raises(
        ConfigurationError,
        match="找不到設定檔",
    ):
        ProjectConfig.load(missing_file)


def test_invalid_yaml_raises_error(tmp_path: Path) -> None:
    config_file = tmp_path / "invalid.yaml"

    config_file.write_text(
        "project: [invalid",
        encoding="utf-8",
    )

    with pytest.raises(
        ConfigurationError,
        match="YAML 格式錯誤",
    ):
        ProjectConfig.load(config_file)


def test_section_must_be_mapping(tmp_path: Path) -> None:
    config_file = tmp_path / "invalid-section.yaml"

    config_file.write_text(
        """
project:
  name: OPL Demo

paths:
  - templates
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(
        ConfigurationError,
        match="'paths' 必須是 mapping",
    ):
        ProjectConfig.load(config_file)


def test_template_root_relative_path(tmp_path: Path) -> None:
    config = ProjectConfig(
        paths={"templates": "templates"},
    )

    result = config.template_root(tmp_path)

    assert result == (tmp_path / "templates").resolve()


def test_template_root_absolute_path(tmp_path: Path) -> None:
    absolute_templates = tmp_path / "shared-templates"

    config = ProjectConfig(
        paths={"templates": str(absolute_templates)},
    )

    result = config.template_root(Path.cwd())

    assert result == absolute_templates.resolve()
