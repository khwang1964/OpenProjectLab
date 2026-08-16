"""Immutable Marketplace artifact models defined by ADR 0023."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from functools import total_ordering

_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$")
_SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
_REQUIREMENT_PART_PATTERN = re.compile(
    r"^(==|!=|>=|<=|>|<)(0|[1-9]\d*)(?:\.(0|[1-9]\d*))?(?:\.(0|[1-9]\d*))?$"
)
_SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")

_SUPPORTED_SCHEMA_VERSION = 1


def _require_nonblank(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _validate_identity_component(value: str, *, field_name: str) -> str:
    value = _require_nonblank(value, field_name=field_name)

    if not _IDENTIFIER_PATTERN.fullmatch(value):
        raise ValueError(
            f"{field_name} must contain only letters, digits, '.', '_', or '-' "
            "and must not contain path semantics"
        )

    if value in {".", ".."}:
        raise ValueError(f"{field_name} must not contain path traversal semantics")

    return value


@dataclass(frozen=True, slots=True)
class ArtifactIdentity:
    """Stable Marketplace artifact identity independent of display metadata."""

    namespace: str
    name: str

    def __post_init__(self) -> None:
        _validate_identity_component(self.namespace, field_name="namespace")
        _validate_identity_component(self.name, field_name="name")

    def __str__(self) -> str:
        return f"{self.namespace}/{self.name}"


@total_ordering
@dataclass(frozen=True, slots=True)
class ArtifactVersion:
    """Canonical ``MAJOR.MINOR.PATCH`` Marketplace artifact version."""

    value: str

    def __post_init__(self) -> None:
        value = _require_nonblank(self.value, field_name="version")
        if _SEMVER_PATTERN.fullmatch(value) is None:
            raise ValueError("version must use canonical MAJOR.MINOR.PATCH syntax")

    @property
    def parts(self) -> tuple[int, int, int]:
        match = _SEMVER_PATTERN.fullmatch(self.value)
        if match is None:  # Defensive: construction already validates this.
            raise ValueError("invalid artifact version")
        return tuple(int(part) for part in match.groups())

    def __str__(self) -> str:
        return self.value

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, ArtifactVersion):
            return NotImplemented
        return self.parts < other.parts


class ArtifactType(StrEnum):
    """Initial Marketplace artifact categories defined by ADR 0023."""

    PLUGIN = "plugin"
    GENERATOR = "generator"
    TEMPLATE = "template"


@dataclass(frozen=True, slots=True)
class ArtifactCoordinate:
    """Immutable identity + version coordinate for one artifact release."""

    identity: ArtifactIdentity
    version: ArtifactVersion

    def __post_init__(self) -> None:
        if not isinstance(self.identity, ArtifactIdentity):
            raise TypeError("identity must be an ArtifactIdentity")
        if not isinstance(self.version, ArtifactVersion):
            raise TypeError("version must be an ArtifactVersion")

    def __str__(self) -> str:
        return f"{self.identity}@{self.version}"


@dataclass(frozen=True, slots=True)
class _VersionPredicate:
    operator: str
    version: tuple[int, int, int]

    def matches(self, candidate: tuple[int, int, int]) -> bool:
        if self.operator == "==":
            return candidate == self.version
        if self.operator == "!=":
            return candidate != self.version
        if self.operator == ">=":
            return candidate >= self.version
        if self.operator == "<=":
            return candidate <= self.version
        if self.operator == ">":
            return candidate > self.version
        if self.operator == "<":
            return candidate < self.version
        raise ValueError(f"unsupported compatibility operator: {self.operator}")


def _normalize_requirement_version(
    major: str,
    minor: str | None,
    patch: str | None,
) -> tuple[int, int, int]:
    return (
        int(major),
        int(minor) if minor is not None else 0,
        int(patch) if patch is not None else 0,
    )


def _parse_requirement(value: str) -> tuple[_VersionPredicate, ...]:
    value = _require_nonblank(value, field_name="compatibility requirement")

    predicates: list[_VersionPredicate] = []
    for raw_part in value.split(","):
        part = raw_part.strip()
        if not part:
            raise ValueError("compatibility requirement contains an empty clause")

        match = _REQUIREMENT_PART_PATTERN.fullmatch(part)
        if match is None:
            raise ValueError(
                "compatibility requirement must use comma-separated version "
                "comparators such as '>=0.7,<1.0'"
            )

        operator, major, minor, patch = match.groups()
        predicates.append(
            _VersionPredicate(
                operator=operator,
                version=_normalize_requirement_version(major, minor, patch),
            )
        )

    return tuple(predicates)


def _parse_runtime_version(value: str) -> tuple[int, int, int]:
    value = _require_nonblank(value, field_name="runtime version")
    match = _SEMVER_PATTERN.fullmatch(value)
    if match is None:
        raise ValueError("runtime version must use canonical MAJOR.MINOR.PATCH syntax")
    return tuple(int(part) for part in match.groups())


@dataclass(frozen=True, slots=True)
class CompatibilityRequirement:
    """Deterministic OPL runtime compatibility requirement."""

    value: str

    def __post_init__(self) -> None:
        _parse_requirement(self.value)

    def __str__(self) -> str:
        return self.value

    def supports(self, runtime_version: str) -> bool:
        candidate = _parse_runtime_version(runtime_version)
        return all(predicate.matches(candidate) for predicate in _parse_requirement(self.value))


@dataclass(frozen=True, slots=True)
class DistributionMetadata:
    """Provider-independent information describing artifact acquisition."""

    kind: str
    reference: str

    def __post_init__(self) -> None:
        _require_nonblank(self.kind, field_name="distribution kind")
        _require_nonblank(self.reference, field_name="distribution reference")


@dataclass(frozen=True, slots=True)
class IntegrityMetadata:
    """Artifact integrity metadata.

    ADR 0023 initially supports SHA-256 only. Integrity verification itself
    belongs to a later Marketplace step; this model validates the contract.
    """

    algorithm: str
    digest: str

    def __post_init__(self) -> None:
        algorithm = _require_nonblank(
            self.algorithm,
            field_name="integrity algorithm",
        )
        digest = _require_nonblank(
            self.digest,
            field_name="integrity digest",
        )

        if algorithm != "sha256":
            raise ValueError("unsupported integrity algorithm")
        if _SHA256_PATTERN.fullmatch(digest) is None:
            raise ValueError("sha256 digest must contain exactly 64 hexadecimal digits")


@dataclass(frozen=True, slots=True)
class MarketplaceArtifact:
    """Common immutable Marketplace artifact contract."""

    schema_version: int
    identity: ArtifactIdentity
    version: ArtifactVersion
    artifact_type: ArtifactType
    description: str
    compatibility: CompatibilityRequirement
    distribution: DistributionMetadata
    integrity: IntegrityMetadata

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != _SUPPORTED_SCHEMA_VERSION
        ):
            raise ValueError(f"unsupported Marketplace schema version: {self.schema_version!r}")

        if not isinstance(self.identity, ArtifactIdentity):
            raise TypeError("identity must be an ArtifactIdentity")
        if not isinstance(self.version, ArtifactVersion):
            raise TypeError("version must be an ArtifactVersion")
        if not isinstance(self.artifact_type, ArtifactType):
            raise TypeError("artifact_type must be an ArtifactType")
        if not isinstance(self.description, str):
            raise TypeError("description must be a string")
        if not isinstance(self.compatibility, CompatibilityRequirement):
            raise TypeError("compatibility must be a CompatibilityRequirement")
        if not isinstance(self.distribution, DistributionMetadata):
            raise TypeError("distribution must be DistributionMetadata")
        if not isinstance(self.integrity, IntegrityMetadata):
            raise TypeError("integrity must be IntegrityMetadata")

    @property
    def coordinate(self) -> ArtifactCoordinate:
        return ArtifactCoordinate(
            identity=self.identity,
            version=self.version,
        )
