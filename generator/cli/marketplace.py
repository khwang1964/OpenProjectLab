"""Internal fail-closed adapters for the deterministic local Marketplace CLI.

This module deliberately contains no production parser registration or command
handlers.  Delivery slice v1.1.4.2 only provides strict value parsing and a
schema-version-1 local catalog loader over the existing Marketplace models.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import NoReturn

from generator.marketplace.models import (
    ArtifactCoordinate,
    ArtifactIdentity,
    ArtifactType,
    ArtifactVersion,
    CompatibilityRequirement,
    DistributionMetadata,
    IntegrityMetadata,
    MarketplaceArtifact,
)
from generator.marketplace.repository import (
    ArtifactAlreadyExistsError,
    InMemoryMarketplaceRepository,
    MarketplaceRepository,
)


class MarketplaceCliAdapterError(ValueError):
    """Base error for handled Marketplace CLI adapter input failures."""


class MarketplaceIdentityParseError(MarketplaceCliAdapterError):
    """Raised when an identity is not canonical ``namespace/name`` syntax."""


class MarketplaceCoordinateParseError(MarketplaceCliAdapterError):
    """Raised when a coordinate is not canonical identity-at-version syntax."""


class MarketplaceCatalogError(MarketplaceCliAdapterError):
    """Raised when a local Marketplace catalog cannot be loaded safely."""


def parse_artifact_identity(value: str) -> ArtifactIdentity:
    """Parse one exact ``namespace/name`` Marketplace identity."""
    if not isinstance(value, str) or value.count("/") != 1:
        raise MarketplaceIdentityParseError(
            "Marketplace identity must use exact namespace/name syntax"
        )

    namespace, name = value.split("/", 1)
    try:
        return ArtifactIdentity(namespace=namespace, name=name)
    except (TypeError, ValueError) as exc:
        raise MarketplaceIdentityParseError(
            "Marketplace identity must use exact namespace/name syntax"
        ) from exc


def parse_artifact_coordinate(value: str) -> ArtifactCoordinate:
    """Parse one exact ``namespace/name@MAJOR.MINOR.PATCH`` coordinate."""
    if not isinstance(value, str) or value.count("@") != 1:
        raise MarketplaceCoordinateParseError(
            "Marketplace coordinate must use exact namespace/name@MAJOR.MINOR.PATCH syntax"
        )

    identity_text, version_text = value.split("@", 1)
    try:
        identity = parse_artifact_identity(identity_text)
        version = ArtifactVersion(version_text)
        return ArtifactCoordinate(identity=identity, version=version)
    except (MarketplaceIdentityParseError, TypeError, ValueError) as exc:
        raise MarketplaceCoordinateParseError(
            "Marketplace coordinate must use exact namespace/name@MAJOR.MINOR.PATCH syntax"
        ) from exc


def load_marketplace_catalog(path: Path) -> InMemoryMarketplaceRepository:
    """Load one explicit UTF-8 schema-version-1 JSON catalog."""
    if not isinstance(path, Path):
        raise TypeError("catalog path must be a pathlib.Path")

    try:
        raw_text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise MarketplaceCatalogError(f"unable to read Marketplace catalog: {path}") from exc

    try:
        raw_catalog = json.loads(raw_text)
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise MarketplaceCatalogError("Marketplace catalog must be valid UTF-8 JSON") from exc

    catalog = _require_object(raw_catalog, field="catalog")
    _require_exact_fields(catalog, {"schema_version", "artifacts"}, field="catalog")
    _require_schema_version(catalog["schema_version"], field="catalog.schema_version")

    raw_artifacts = catalog["artifacts"]
    if not isinstance(raw_artifacts, list):
        raise MarketplaceCatalogError("catalog.artifacts must be an array")

    artifacts = tuple(
        _parse_catalog_artifact(raw_artifact, index=index)
        for index, raw_artifact in enumerate(raw_artifacts)
    )
    try:
        return InMemoryMarketplaceRepository(artifacts)
    except ArtifactAlreadyExistsError as exc:
        raise MarketplaceCatalogError("catalog contains a duplicate artifact coordinate") from exc


def get_marketplace_versions(
    repository: MarketplaceRepository,
    identity: str,
) -> tuple[ArtifactVersion, ...]:
    """Return deterministic versions for one validated Marketplace identity."""
    parsed_identity = parse_artifact_identity(identity)
    return repository.available_versions(parsed_identity)


def inspect_marketplace_artifact(
    repository: MarketplaceRepository,
    coordinate: str,
) -> MarketplaceArtifact:
    """Return the artifact at one validated exact Marketplace coordinate."""
    parsed_coordinate = parse_artifact_coordinate(coordinate)
    return repository.find(
        parsed_coordinate.identity,
        parsed_coordinate.version,
    )


def _parse_catalog_artifact(raw_artifact: object, *, index: int) -> MarketplaceArtifact:
    field = f"catalog.artifacts[{index}]"
    artifact = _require_object(raw_artifact, field=field)
    _require_exact_fields(
        artifact,
        {
            "schema_version",
            "identity",
            "version",
            "artifact_type",
            "description",
            "compatibility",
            "distribution",
            "integrity",
        },
        field=field,
    )
    _require_schema_version(artifact["schema_version"], field=f"{field}.schema_version")

    identity = _require_object(artifact["identity"], field=f"{field}.identity")
    _require_exact_fields(identity, {"namespace", "name"}, field=f"{field}.identity")

    distribution = _require_object(artifact["distribution"], field=f"{field}.distribution")
    _require_exact_fields(distribution, {"kind", "reference"}, field=f"{field}.distribution")

    integrity = _require_object(artifact["integrity"], field=f"{field}.integrity")
    _require_exact_fields(integrity, {"algorithm", "digest"}, field=f"{field}.integrity")

    try:
        return MarketplaceArtifact(
            schema_version=1,
            identity=ArtifactIdentity(
                namespace=_require_string(
                    identity["namespace"], field=f"{field}.identity.namespace"
                ),
                name=_require_string(identity["name"], field=f"{field}.identity.name"),
            ),
            version=ArtifactVersion(_require_string(artifact["version"], field=f"{field}.version")),
            artifact_type=ArtifactType(
                _require_string(artifact["artifact_type"], field=f"{field}.artifact_type")
            ),
            description=_require_string(
                artifact["description"], field=f"{field}.description", allow_empty=True
            ),
            compatibility=CompatibilityRequirement(
                _require_string(artifact["compatibility"], field=f"{field}.compatibility")
            ),
            distribution=DistributionMetadata(
                kind=_require_string(distribution["kind"], field=f"{field}.distribution.kind"),
                reference=_require_string(
                    distribution["reference"], field=f"{field}.distribution.reference"
                ),
            ),
            integrity=IntegrityMetadata(
                algorithm=_require_string(
                    integrity["algorithm"], field=f"{field}.integrity.algorithm"
                ),
                digest=_require_string(integrity["digest"], field=f"{field}.integrity.digest"),
            ),
        )
    except (TypeError, ValueError) as exc:
        raise MarketplaceCatalogError(
            f"{field} violates the Marketplace artifact contract"
        ) from exc


def _require_object(value: object, *, field: str) -> Mapping[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise MarketplaceCatalogError(f"{field} must be a JSON object")
    return value


def _require_exact_fields(value: Mapping[str, object], expected: set[str], *, field: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        details = []
        if missing:
            details.append(f"missing {missing}")
        if unknown:
            details.append(f"unknown {unknown}")
        _catalog_failure(f"{field} has invalid fields: {', '.join(details)}")


def _require_schema_version(value: object, *, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value != 1:
        raise MarketplaceCatalogError(f"{field} must be integer 1")


def _require_string(value: object, *, field: str, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value):
        raise MarketplaceCatalogError(f"{field} must be a string")
    return value


def _catalog_failure(message: str) -> NoReturn:
    raise MarketplaceCatalogError(message)
