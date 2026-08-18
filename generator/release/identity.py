"""Pure release identity validation for OpenProjectLab."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:rc\d+)?$")
_FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class ReleaseIdentityError(ValueError):
    """Raised when release identity data is invalid or inconsistent."""


class ReleaseTagConflictError(ReleaseIdentityError):
    """Raised when an existing release tag points at a different commit."""


@dataclass(frozen=True, slots=True)
class ReleaseIdentity:
    """Immutable version / commit / tag identity for one release."""

    version: str
    commit_sha: str
    tag: str

    def __post_init__(self) -> None:
        """Validate the release identity tuple."""
        _validate_version(self.version)
        _validate_commit_sha(self.commit_sha)

        expected_tag = expected_release_tag(self.version)
        if self.tag != expected_tag:
            raise ReleaseIdentityError(
                "Release tag does not match the canonical version: "
                f"expected {expected_tag!r}, got {self.tag!r}"
            )


def read_canonical_version(pyproject_path: str | Path) -> str:
    """Read the canonical project version from ``pyproject.toml``.

    Args:
        pyproject_path: Path to the repository ``pyproject.toml``.

    Returns:
        The canonical ``[project].version`` value.

    Raises:
        ReleaseIdentityError: If the file cannot provide a valid canonical
            version.
    """
    path = Path(pyproject_path)

    try:
        with path.open("rb") as stream:
            data = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ReleaseIdentityError(f"Unable to read canonical version from {path}") from exc

    project = data.get("project")
    if not isinstance(project, dict):
        raise ReleaseIdentityError("pyproject.toml is missing [project]")

    version = project.get("version")
    if not isinstance(version, str):
        raise ReleaseIdentityError("pyproject.toml [project].version must be a string")

    _validate_version(version)
    return version


def expected_release_tag(version: str) -> str:
    """Derive the canonical release tag from a canonical version.

    Args:
        version: Canonical package version without a ``v`` prefix.

    Returns:
        The canonical Git tag.

    Raises:
        ReleaseIdentityError: If ``version`` is malformed.
    """
    _validate_version(version)
    return f"v{version}"


def validate_release_identity(
    identity: ReleaseIdentity,
    *,
    tag_target_sha: str | None,
) -> ReleaseIdentity:
    """Validate an existing-or-planned tag binding without side effects.

    ``tag_target_sha`` is ``None`` when the tag has not yet been created.
    When present, it must be a full immutable SHA equal to the approved
    release commit.

    Args:
        identity: The release identity to validate.
        tag_target_sha: Existing tag target SHA, or ``None`` for pre-tag
            validation.

    Returns:
        The same validated ``ReleaseIdentity`` instance.

    Raises:
        ReleaseIdentityError: If the provided tag target SHA is malformed.
        ReleaseTagConflictError: If the existing tag points at another
            commit.
    """
    if tag_target_sha is None:
        return identity

    _validate_commit_sha(tag_target_sha)

    if tag_target_sha != identity.commit_sha:
        raise ReleaseTagConflictError(
            "Release tag target conflicts with the approved release commit: "
            f"tag points to {tag_target_sha}, expected {identity.commit_sha}"
        )

    return identity


def _validate_version(version: str) -> None:
    """Validate the canonical release-version shape."""
    if not isinstance(version, str) or version != version.strip():
        raise ReleaseIdentityError("Release version must be a non-empty canonical version string")

    if not _VERSION_RE.fullmatch(version):
        raise ReleaseIdentityError("Release version must use canonical X.Y.Z or X.Y.ZrcN syntax")


def _validate_commit_sha(commit_sha: str) -> None:
    """Validate a full immutable lowercase Git SHA-1 identity."""
    if not isinstance(commit_sha, str) or not _FULL_SHA_RE.fullmatch(commit_sha):
        raise ReleaseIdentityError("Release commit must be a full 40-character lowercase Git SHA")
