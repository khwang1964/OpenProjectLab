"""Marketplace Template Package contracts.

Step 7.7 defines immutable metadata for versioned Template Packages while
reusing the Marketplace artifact identity/version contract.

This module does not render Jinja templates, execute generators, write output,
access the network, activate packages, or expose Marketplace models through
``generator.sdk``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

from .models import (
    ArtifactCoordinate,
    ArtifactType,
    MarketplaceArtifact,
)

_SUPPORTED_TEMPLATE_MANIFEST_SCHEMA_VERSION = 1


class TemplatePackageValidationError(ValueError):
    """Raised when Template Package metadata violates the contract."""


def _require_nonblank(
    value: str,
    *,
    field_name: str,
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _normalize_relative_path(value: str) -> str:
    raw = _require_nonblank(
        value,
        field_name="relative_path",
    )

    normalized = raw.replace("\\", "/")

    if normalized.startswith("/"):
        raise ValueError("relative_path must not be absolute")

    if len(normalized) >= 2 and normalized[1] == ":":
        raise ValueError("relative_path must not include a drive prefix")

    path = PurePosixPath(normalized)

    if path.is_absolute():
        raise ValueError("relative_path must not be absolute")

    if any(part in {".", ".."} for part in path.parts):
        raise ValueError("relative_path must not contain traversal segments")

    if not path.parts:
        raise ValueError("relative_path must identify a package entry")

    return path.as_posix()


@dataclass(frozen=True, slots=True)
class TemplateEntry:
    """One immutable template or resource entry in a Template Package."""

    name: str
    relative_path: str
    media_type: str

    def __post_init__(self) -> None:
        name = _require_nonblank(
            self.name,
            field_name="name",
        )
        relative_path = _normalize_relative_path(
            self.relative_path,
        )
        media_type = _require_nonblank(
            self.media_type,
            field_name="media_type",
        )

        object.__setattr__(self, "name", name)
        object.__setattr__(
            self,
            "relative_path",
            relative_path,
        )
        object.__setattr__(
            self,
            "media_type",
            media_type,
        )


def _validate_entries(
    entries: tuple[TemplateEntry, ...],
    *,
    collection_name: str,
) -> tuple[TemplateEntry, ...]:
    if not isinstance(entries, tuple):
        raise TypeError(f"{collection_name} must be a tuple of TemplateEntry values")

    for entry in entries:
        if not isinstance(entry, TemplateEntry):
            raise TypeError(f"{collection_name} must contain only TemplateEntry values")

    names: set[str] = set()
    paths: set[str] = set()

    for entry in entries:
        if entry.name in names:
            raise TemplatePackageValidationError(
                f"duplicate {collection_name} entry name: {entry.name}"
            )

        if entry.relative_path in paths:
            raise TemplatePackageValidationError(
                f"duplicate {collection_name} entry path: {entry.relative_path}"
            )

        names.add(entry.name)
        paths.add(entry.relative_path)

    return tuple(
        sorted(
            entries,
            key=lambda entry: (
                entry.name,
                entry.relative_path,
                entry.media_type,
            ),
        )
    )


@dataclass(frozen=True, slots=True)
class TemplatePackageManifest:
    """Immutable manifest describing templates and static resources."""

    schema_version: int
    templates: tuple[TemplateEntry, ...]
    resources: tuple[TemplateEntry, ...]

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != _SUPPORTED_TEMPLATE_MANIFEST_SCHEMA_VERSION
        ):
            raise ValueError(
                f"unsupported Template Package manifest schema version: {self.schema_version!r}"
            )

        templates = _validate_entries(
            self.templates,
            collection_name="templates",
        )
        resources = _validate_entries(
            self.resources,
            collection_name="resources",
        )

        template_paths = {entry.relative_path for entry in templates}
        resource_paths = {entry.relative_path for entry in resources}

        collisions = template_paths & resource_paths
        if collisions:
            collision = sorted(collisions)[0]
            raise TemplatePackageValidationError(f"template/resource path collision: {collision}")

        object.__setattr__(
            self,
            "templates",
            templates,
        )
        object.__setattr__(
            self,
            "resources",
            resources,
        )


@dataclass(frozen=True, slots=True)
class TemplatePackage:
    """Marketplace artifact specialized for immutable Template metadata."""

    artifact: MarketplaceArtifact
    manifest: TemplatePackageManifest

    def __post_init__(self) -> None:
        if not isinstance(
            self.artifact,
            MarketplaceArtifact,
        ):
            raise TypeError("artifact must be a MarketplaceArtifact")

        if not isinstance(
            self.manifest,
            TemplatePackageManifest,
        ):
            raise TypeError("manifest must be a TemplatePackageManifest")

        if self.artifact.artifact_type is not ArtifactType.TEMPLATE:
            raise TemplatePackageValidationError(
                "TemplatePackage requires a Marketplace artifact with artifact_type='template'"
            )

    @property
    def coordinate(self) -> ArtifactCoordinate:
        return self.artifact.coordinate
