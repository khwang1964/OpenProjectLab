"""v1.1.4.2 internal Marketplace catalog and parsing adapter tests."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from generator.cli.main import build_parser
from generator.cli.marketplace import (
    MarketplaceCatalogError,
    MarketplaceCoordinateParseError,
    MarketplaceIdentityParseError,
    load_marketplace_catalog,
    parse_artifact_coordinate,
    parse_artifact_identity,
)
from generator.marketplace.models import ArtifactIdentity, ArtifactVersion


def _catalog() -> dict[str, object]:
    return {
        "schema_version": 1,
        "artifacts": [
            {
                "schema_version": 1,
                "identity": {"namespace": "community", "name": "course-template"},
                "version": "1.2.3",
                "artifact_type": "template",
                "description": "A deterministic local template",
                "compatibility": ">=1.0,<2.0",
                "distribution": {
                    "kind": "file",
                    "reference": "community/course-template-1.2.3.opl",
                },
                "integrity": {
                    "algorithm": "sha256",
                    "digest": hashlib.sha256(b"payload").hexdigest(),
                },
            }
        ],
    }


def _write_catalog(tmp_path: Path, catalog: object) -> Path:
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(catalog), encoding="utf-8")
    return path


def _top_level_commands() -> frozenset[str]:
    for action in build_parser()._actions:
        choices = getattr(action, "choices", None)
        if isinstance(choices, dict) and "list" in choices:
            return frozenset(choices)
    raise AssertionError("CLI subcommand registry was not found")


@pytest.mark.parametrize(
    "value",
    ("community/course-template", "a/b", "alpha-1/template_name"),
)
def test_parse_artifact_identity_accepts_only_canonical_values(value: str) -> None:
    assert str(parse_artifact_identity(value)) == value


@pytest.mark.parametrize(
    "value",
    ("", "community", "/name", "namespace/", "a/b/c", "../name", "a\\b"),
)
def test_parse_artifact_identity_fails_closed(value: str) -> None:
    with pytest.raises(MarketplaceIdentityParseError):
        parse_artifact_identity(value)


def test_parse_artifact_coordinate_builds_existing_domain_models() -> None:
    coordinate = parse_artifact_coordinate("community/course-template@1.2.3")

    assert coordinate.identity == ArtifactIdentity("community", "course-template")
    assert coordinate.version == ArtifactVersion("1.2.3")


@pytest.mark.parametrize(
    "value",
    (
        "community/course-template",
        "community/course-template@",
        "community/course-template@1.2",
        "community/course-template@01.2.3",
        "community/course-template@1.2.3-rc.1",
        "community/course-template@1.2.3+build",
        "community/course-template@1.2.3@extra",
    ),
)
def test_parse_artifact_coordinate_fails_closed(value: str) -> None:
    with pytest.raises(MarketplaceCoordinateParseError):
        parse_artifact_coordinate(value)


def test_load_catalog_constructs_deterministic_existing_repository(tmp_path: Path) -> None:
    repository = load_marketplace_catalog(_write_catalog(tmp_path, _catalog()))

    identity = ArtifactIdentity("community", "course-template")
    assert repository.available_versions(identity) == (ArtifactVersion("1.2.3"),)
    assert str(repository.find(identity, ArtifactVersion("1.2.3")).coordinate) == (
        "community/course-template@1.2.3"
    )


@pytest.mark.parametrize("schema_version", (True, 0, 2, "1", None))
def test_load_catalog_requires_integer_schema_version_one(
    tmp_path: Path, schema_version: object
) -> None:
    catalog = _catalog()
    catalog["schema_version"] = schema_version

    with pytest.raises(MarketplaceCatalogError):
        load_marketplace_catalog(_write_catalog(tmp_path, catalog))


@pytest.mark.parametrize("artifacts", ({}, "artifact", None, 1))
def test_load_catalog_requires_artifacts_array(tmp_path: Path, artifacts: object) -> None:
    catalog = _catalog()
    catalog["artifacts"] = artifacts

    with pytest.raises(MarketplaceCatalogError):
        load_marketplace_catalog(_write_catalog(tmp_path, catalog))


def test_load_catalog_rejects_malformed_json(tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(MarketplaceCatalogError):
        load_marketplace_catalog(path)


def test_load_catalog_rejects_invalid_utf8(tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"
    path.write_bytes(b"\xff")

    with pytest.raises(MarketplaceCatalogError):
        load_marketplace_catalog(path)


def test_load_catalog_rejects_missing_unknown_and_wrong_typed_fields(tmp_path: Path) -> None:
    for mutation in ("missing", "unknown", "wrong-type"):
        catalog = _catalog()
        artifact = catalog["artifacts"][0]  # type: ignore[index]
        if mutation == "missing":
            del artifact["integrity"]
        elif mutation == "unknown":
            artifact["publisher"] = "unaccepted"
        else:
            artifact["version"] = 123

        with pytest.raises(MarketplaceCatalogError):
            load_marketplace_catalog(_write_catalog(tmp_path, catalog))


def test_load_catalog_rejects_duplicate_exact_coordinates(tmp_path: Path) -> None:
    catalog = _catalog()
    artifacts = catalog["artifacts"]
    assert isinstance(artifacts, list)
    artifacts.append(copy.deepcopy(artifacts[0]))

    with pytest.raises(MarketplaceCatalogError, match="duplicate"):
        load_marketplace_catalog(_write_catalog(tmp_path, catalog))


def test_internal_adapters_remain_available_after_production_registration() -> None:
    assert "marketplace" in _top_level_commands()
