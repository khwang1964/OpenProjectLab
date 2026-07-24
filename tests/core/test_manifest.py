from pathlib import Path

import pytest

from generator.core.exceptions import ConfigurationError
from generator.core.manifest import GeneratorManifest


def test_manifest_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "generator.yaml"
    expected = GeneratorManifest(
        name="demo",
        version="1.0.0",
        description="Demo generator",
        entrypoint="demo.generator:DemoGenerator",
    )
    expected.dump(path)
    assert GeneratorManifest.load(path) == expected


def test_manifest_requires_all_fields() -> None:
    with pytest.raises(ConfigurationError):
        GeneratorManifest.from_mapping({"name": "demo"})
