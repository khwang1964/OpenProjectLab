"""Marketplace domain contracts.

Marketplace models are intentionally kept out of ``generator.sdk`` until a
separate public-API compatibility decision is made.
"""

from .models import (
    ArtifactCoordinate,
    ArtifactIdentity,
    ArtifactType,
    ArtifactVersion,
    CompatibilityRequirement,
    DistributionMetadata,
    IntegrityMetadata,
    MarketplaceArtifact,
)

__all__ = [
    "ArtifactCoordinate",
    "ArtifactIdentity",
    "ArtifactType",
    "ArtifactVersion",
    "CompatibilityRequirement",
    "DistributionMetadata",
    "IntegrityMetadata",
    "MarketplaceArtifact",
]
