"""Deterministic Marketplace artifact acquisition contracts.

Step 7.5 acquisition returns artifact bytes only. It intentionally performs no
integrity verification, installation, activation, plugin registration,
generator execution, filesystem mutation, or network access.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

from .models import (
    ArtifactCoordinate,
    MarketplaceArtifact,
)


class ArtifactAcquisitionError(Exception):
    """Base error for expected Marketplace acquisition failures."""


class ArtifactPayloadNotFoundError(ArtifactAcquisitionError):
    """Raised when no payload exists for an exact artifact coordinate."""


@runtime_checkable
class ArtifactAcquirer(Protocol):
    """Artifact acquisition boundary returning bytes for one artifact."""

    def acquire(
        self,
        artifact: MarketplaceArtifact,
    ) -> bytes:
        """Return payload bytes for ``artifact`` without activating it."""


class InMemoryArtifactAcquirer:
    """Deterministic no-network acquirer backed by an in-memory payload map."""

    def __init__(
        self,
        payloads: Mapping[ArtifactCoordinate, bytes] | None = None,
    ) -> None:
        source = {} if payloads is None else payloads

        copied: dict[ArtifactCoordinate, bytes] = {}

        for coordinate, payload in source.items():
            if not isinstance(coordinate, ArtifactCoordinate):
                raise TypeError("acquisition payload keys must be ArtifactCoordinate instances")

            if not isinstance(payload, bytes):
                raise TypeError("acquisition payload values must be bytes")

            copied[coordinate] = payload

        self._payloads = copied

    def acquire(
        self,
        artifact: MarketplaceArtifact,
    ) -> bytes:
        if not isinstance(artifact, MarketplaceArtifact):
            raise TypeError("artifact must be a MarketplaceArtifact")

        coordinate = artifact.coordinate

        try:
            return self._payloads[coordinate]
        except KeyError as exc:
            raise ArtifactPayloadNotFoundError(
                f"Marketplace artifact payload not found: {coordinate}"
            ) from exc
