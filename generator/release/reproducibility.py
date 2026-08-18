"""Semantic release reproducibility and clean-install primitives."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from .artifacts import ReleaseArtifactSet

_WHEEL_SUFFIX = ".whl"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ReleaseReproducibilityError(ValueError):
    """Raised when release rebuilds are not semantically reproducible."""


@dataclass(frozen=True, slots=True)
class ReleaseBuildSnapshot:
    """Immutable semantic and byte-level evidence for one release build."""

    project_name: str
    version: str
    artifact_names: tuple[str, ...]
    artifact_kinds: tuple[str, ...]
    wheel_project: str
    wheel_version: str
    checksums: tuple[tuple[str, str], ...]


def build_release_snapshot(
    *,
    project_name: str,
    version: str,
    artifact_set: ReleaseArtifactSet,
    wheel_project: str,
    wheel_version: str,
    checksums: Mapping[str, str],
) -> ReleaseBuildSnapshot:
    """Capture deterministic release-build evidence for later comparison."""
    artifact_names = tuple(sorted(artifact.path.name for artifact in artifact_set.artifacts))
    artifact_kinds = tuple(sorted(artifact.kind for artifact in artifact_set.artifacts))

    if set(checksums) != set(artifact_names):
        raise ReleaseReproducibilityError(
            "Checksum evidence must exactly cover the release artifact set"
        )

    checksum_items: list[tuple[str, str]] = []
    for name in sorted(checksums):
        digest = checksums[name]
        if not isinstance(digest, str) or not _SHA256_RE.fullmatch(digest):
            raise ReleaseReproducibilityError(f"Invalid SHA-256 checksum for artifact {name!r}")
        checksum_items.append((name, digest))

    return ReleaseBuildSnapshot(
        project_name=project_name,
        version=version,
        artifact_names=artifact_names,
        artifact_kinds=artifact_kinds,
        wheel_project=wheel_project,
        wheel_version=wheel_version,
        checksums=tuple(checksum_items),
    )


def compare_release_snapshots(
    baseline: ReleaseBuildSnapshot,
    rebuilt: ReleaseBuildSnapshot,
) -> tuple[str, ...]:
    """Return semantic differences between two release-build snapshots.

    Checksum values are intentionally excluded. Different artifact bytes do
    not by themselves violate Step 8.8 semantic reproducibility.
    """
    differences: list[str] = []

    if baseline.project_name != rebuilt.project_name:
        differences.append("project_name")
    if baseline.version != rebuilt.version:
        differences.append("version")
    if baseline.artifact_kinds != rebuilt.artifact_kinds:
        differences.append("artifact_kinds")
    if baseline.wheel_project != rebuilt.wheel_project:
        differences.append("wheel_project")
    if baseline.wheel_version != rebuilt.wheel_version:
        differences.append("wheel_version")

    return tuple(differences)


def verify_semantic_reproducibility(
    baseline: ReleaseBuildSnapshot,
    rebuilt: ReleaseBuildSnapshot,
) -> ReleaseBuildSnapshot:
    """Fail closed unless two builds are semantically contract-equivalent."""
    differences = compare_release_snapshots(baseline, rebuilt)

    if differences:
        raise ReleaseReproducibilityError(
            "Release rebuild is not semantically reproducible; "
            f"different fields: {', '.join(differences)}"
        )

    return rebuilt


def verify_wheel_for_clean_install(
    wheel_path: str | Path,
    *,
    expected_project: str,
    expected_version: str,
) -> Path:
    """Validate the exact wheel used by installed-user release verification."""
    path = Path(wheel_path)

    if not path.is_file():
        raise ReleaseReproducibilityError(f"Release wheel does not exist: {path}")

    if not path.name.endswith(_WHEEL_SUFFIX):
        raise ReleaseReproducibilityError(
            f"Clean-install verification requires a wheel: {path.name}"
        )

    project_pattern = re.escape(expected_project).replace(r"\-", "[-_]")
    version_pattern = re.escape(expected_version).replace(r"\-", "[-_]")
    pattern = (
        rf"^{project_pattern}-{version_pattern}"
        rf"(?:-[^-]+)?-[^-]+-[^-]+-[^-]+\.whl$"
    )

    if re.fullmatch(pattern, path.name) is None:
        raise ReleaseReproducibilityError(
            "Release wheel filename does not match expected project/version"
        )

    return path.resolve()
