"""Deterministic Marketplace installation contracts.

Step 7.6 installation records validated artifact payloads in a side-effect-free
in-memory store. Installation is intentionally separate from activation.

This module does not:
- verify integrity
- access a package manager
- access the network
- discover entry points
- register plugins
- execute generators
- write Courseware output
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, runtime_checkable

from .models import (
    ArtifactCoordinate,
    MarketplaceArtifact,
)


class ArtifactInstallationError(Exception):
    """Base error for expected Marketplace installation failures."""


class ArtifactAlreadyInstalledError(ArtifactInstallationError):
    """Raised when an exact artifact coordinate is already installed."""


class ArtifactNotInstalledError(ArtifactInstallationError):
    """Raised when installed state is requested for an unavailable coordinate."""


class ArtifactInstallationStatus(StrEnum):
    """Deterministic installation outcomes."""

    INSTALLED = "installed"


@dataclass(frozen=True, slots=True)
class ArtifactInstallationResult:
    """Immutable result returned by one installation operation."""

    artifact: MarketplaceArtifact
    status: ArtifactInstallationStatus
    payload_size: int

    def __post_init__(self) -> None:
        if not isinstance(self.artifact, MarketplaceArtifact):
            raise TypeError("artifact must be a MarketplaceArtifact")
        if not isinstance(self.status, ArtifactInstallationStatus):
            raise TypeError("status must be an ArtifactInstallationStatus")
        if (
            isinstance(self.payload_size, bool)
            or not isinstance(self.payload_size, int)
            or self.payload_size < 0
        ):
            raise ValueError("payload_size must be a non-negative integer")


@runtime_checkable
class ArtifactInstaller(Protocol):
    """Marketplace installation boundary.

    Implementations install an artifact payload but do not activate it.
    """

    def install(
        self,
        artifact: MarketplaceArtifact,
        payload: bytes,
    ) -> ArtifactInstallationResult:
        """Install one artifact payload without activating the artifact."""


def _artifact_sort_key(
    artifact: MarketplaceArtifact,
) -> tuple[str, str, tuple[int, int, int]]:
    return (
        artifact.identity.namespace,
        artifact.identity.name,
        artifact.version.parts,
    )


class InMemoryArtifactInstaller:
    """Deterministic, no-network, no-filesystem installation implementation."""

    def __init__(self) -> None:
        self._artifacts: dict[ArtifactCoordinate, MarketplaceArtifact] = {}
        self._payloads: dict[ArtifactCoordinate, bytes] = {}

    def install(
        self,
        artifact: MarketplaceArtifact,
        payload: bytes,
    ) -> ArtifactInstallationResult:
        if not isinstance(artifact, MarketplaceArtifact):
            raise TypeError("artifact must be a MarketplaceArtifact")
        if not isinstance(payload, bytes):
            raise TypeError("installation payload must be bytes")

        coordinate = artifact.coordinate

        if coordinate in self._artifacts:
            raise ArtifactAlreadyInstalledError(
                f"Marketplace artifact already installed: {coordinate}"
            )

        self._artifacts[coordinate] = artifact
        self._payloads[coordinate] = bytes(payload)

        return ArtifactInstallationResult(
            artifact=artifact,
            status=ArtifactInstallationStatus.INSTALLED,
            payload_size=len(payload),
        )

    def is_installed(
        self,
        coordinate: ArtifactCoordinate,
    ) -> bool:
        if not isinstance(coordinate, ArtifactCoordinate):
            raise TypeError("coordinate must be an ArtifactCoordinate")
        return coordinate in self._artifacts

    def installed_payload(
        self,
        coordinate: ArtifactCoordinate,
    ) -> bytes:
        if not isinstance(coordinate, ArtifactCoordinate):
            raise TypeError("coordinate must be an ArtifactCoordinate")

        try:
            return self._payloads[coordinate]
        except KeyError as exc:
            raise ArtifactNotInstalledError(
                f"Marketplace artifact is not installed: {coordinate}"
            ) from exc

    def list_installed(self) -> tuple[MarketplaceArtifact, ...]:
        return tuple(
            sorted(
                self._artifacts.values(),
                key=_artifact_sort_key,
            )
        )
