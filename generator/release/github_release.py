"""Pure GitHub Release consistency contracts."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from .artifacts import ReleaseArtifactSet
from .identity import ReleaseIdentity

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class GitHubReleaseError(ValueError):
    """Raised when a GitHub Release specification is invalid."""


class GitHubReleaseConflictError(GitHubReleaseError):
    """Raised when existing GitHub Release state conflicts with expectation."""


@dataclass(frozen=True, slots=True)
class GitHubReleaseSpec:
    """Immutable publication specification for one GitHub Release."""

    version: str
    tag: str
    commit_sha: str
    title: str
    draft: bool
    prerelease: bool
    asset_names: tuple[str, ...]
    checksums: Mapping[str, str]

    def __post_init__(self) -> None:
        """Freeze checksum mapping defensively."""
        object.__setattr__(
            self,
            "checksums",
            MappingProxyType(dict(self.checksums)),
        )


def build_github_release_spec(
    *,
    identity: ReleaseIdentity,
    artifact_set: ReleaseArtifactSet,
    checksums: Mapping[str, str],
) -> GitHubReleaseSpec:
    """Build and validate the expected GitHub Release publication state."""
    artifact_names = tuple(sorted(artifact.path.name for artifact in artifact_set.artifacts))
    expected_checksum_names = set(artifact_names)
    checksum_names = set(checksums)

    if checksum_names != expected_checksum_names:
        raise GitHubReleaseError(
            "Checksum manifest must exactly cover the verified release artifacts"
        )

    normalized_checksums: dict[str, str] = {}
    for name in sorted(checksums):
        digest = checksums[name]
        if not isinstance(digest, str) or not _SHA256_RE.fullmatch(digest):
            raise GitHubReleaseError(f"Invalid SHA-256 checksum for release asset {name!r}")
        normalized_checksums[name] = digest

    asset_names = tuple(sorted((*artifact_names, "SHA256SUMS.txt")))

    return GitHubReleaseSpec(
        version=identity.version,
        tag=identity.tag,
        commit_sha=identity.commit_sha,
        title=f"OpenProjectLab v{identity.version}",
        draft=True,
        prerelease="rc" in identity.version,
        asset_names=asset_names,
        checksums=normalized_checksums,
    )


def validate_existing_github_release(
    spec: GitHubReleaseSpec,
    *,
    existing_tag: str,
    existing_commit_sha: str,
    existing_asset_names: Sequence[str],
    existing_draft: bool,
    existing_prerelease: bool,
) -> GitHubReleaseSpec:
    """Validate existing GitHub Release state without external side effects."""
    if existing_tag != spec.tag:
        raise GitHubReleaseConflictError(
            f"Existing GitHub Release tag {existing_tag!r} does not match expected {spec.tag!r}"
        )

    if existing_commit_sha != spec.commit_sha:
        raise GitHubReleaseConflictError(
            "Existing GitHub Release commit does not match approved release SHA"
        )

    if tuple(sorted(existing_asset_names)) != tuple(sorted(spec.asset_names)):
        raise GitHubReleaseConflictError(
            "Existing GitHub Release assets do not match verified release assets"
        )

    if existing_draft is not True:
        raise GitHubReleaseConflictError(
            "Existing GitHub Release is already published; automatic mutation is not allowed"
        )

    if existing_prerelease != spec.prerelease:
        raise GitHubReleaseConflictError(
            "Existing GitHub Release prerelease classification conflicts "
            "with expected release identity"
        )

    return spec
