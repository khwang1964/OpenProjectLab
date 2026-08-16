"""Deterministic Marketplace repository/index contracts.

This module intentionally implements only the Step 7.4 metadata lookup boundary.
It does not acquire, verify, install, activate, or execute Marketplace artifacts.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol, runtime_checkable

from .models import (
    ArtifactCoordinate,
    ArtifactIdentity,
    ArtifactVersion,
    MarketplaceArtifact,
)


class MarketplaceRepositoryError(Exception):
    """Base error for expected Marketplace repository failures."""


class ArtifactNotFoundError(MarketplaceRepositoryError):
    """Raised when an exact Marketplace artifact coordinate is unavailable."""


class ArtifactAlreadyExistsError(MarketplaceRepositoryError):
    """Raised when a repository contains the same coordinate more than once."""


@runtime_checkable
class MarketplaceRepository(Protocol):
    """Read-only Marketplace repository/index contract."""

    def find(
        self,
        identity: ArtifactIdentity,
        version: ArtifactVersion,
    ) -> MarketplaceArtifact:
        """Return the artifact matching one exact coordinate."""

    def available_versions(
        self,
        identity: ArtifactIdentity,
    ) -> tuple[ArtifactVersion, ...]:
        """Return available versions in deterministic ascending order."""

    def list_artifacts(self) -> tuple[MarketplaceArtifact, ...]:
        """Return all artifacts in deterministic coordinate order."""


def _coordinate_sort_key(
    artifact: MarketplaceArtifact,
) -> tuple[str, str, tuple[int, int, int]]:
    return (
        artifact.identity.namespace,
        artifact.identity.name,
        artifact.version.parts,
    )


class InMemoryMarketplaceRepository:
    """Deterministic, side-effect-free repository backed by immutable artifacts."""

    def __init__(
        self,
        artifacts: Iterable[MarketplaceArtifact] = (),
    ) -> None:
        by_coordinate: dict[ArtifactCoordinate, MarketplaceArtifact] = {}

        for artifact in artifacts:
            if not isinstance(artifact, MarketplaceArtifact):
                raise TypeError("repository artifacts must be MarketplaceArtifact instances")

            coordinate = artifact.coordinate
            if coordinate in by_coordinate:
                raise ArtifactAlreadyExistsError(
                    f"Marketplace artifact already exists: {coordinate}"
                )

            by_coordinate[coordinate] = artifact

        self._by_coordinate = by_coordinate

    def find(
        self,
        identity: ArtifactIdentity,
        version: ArtifactVersion,
    ) -> MarketplaceArtifact:
        if not isinstance(identity, ArtifactIdentity):
            raise TypeError("identity must be an ArtifactIdentity")
        if not isinstance(version, ArtifactVersion):
            raise TypeError("version must be an ArtifactVersion")

        coordinate = ArtifactCoordinate(
            identity=identity,
            version=version,
        )

        try:
            return self._by_coordinate[coordinate]
        except KeyError as exc:
            raise ArtifactNotFoundError(f"Marketplace artifact not found: {coordinate}") from exc

    def available_versions(
        self,
        identity: ArtifactIdentity,
    ) -> tuple[ArtifactVersion, ...]:
        if not isinstance(identity, ArtifactIdentity):
            raise TypeError("identity must be an ArtifactIdentity")

        versions = (
            artifact.version
            for artifact in self._by_coordinate.values()
            if artifact.identity == identity
        )
        return tuple(sorted(versions))

    def list_artifacts(self) -> tuple[MarketplaceArtifact, ...]:
        return tuple(
            sorted(
                self._by_coordinate.values(),
                key=_coordinate_sort_key,
            )
        )
