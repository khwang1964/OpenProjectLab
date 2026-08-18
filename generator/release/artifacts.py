"""Release artifact enumeration, metadata, and checksum primitives."""

from __future__ import annotations

import hashlib
import re
import zipfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from email.parser import Parser
from pathlib import Path
from types import MappingProxyType
from typing import Literal

ArtifactKind = Literal["wheel", "sdist"]

_WHEEL_SUFFIX = ".whl"
_SDIST_SUFFIX = ".tar.gz"


class ReleaseArtifactError(ValueError):
    """Raised when release artifacts are missing, ambiguous, or inconsistent."""


class ReleaseChecksumMismatchError(ReleaseArtifactError):
    """Raised when artifact bytes do not match the recorded checksum."""


@dataclass(frozen=True, slots=True)
class ReleaseArtifact:
    """Immutable reference to one release artifact."""

    path: Path
    kind: ArtifactKind

    @classmethod
    def from_path(cls, path: str | Path) -> ReleaseArtifact:
        """Create an artifact reference from a canonical release filename."""
        candidate = Path(path)

        if candidate.name.endswith(_WHEEL_SUFFIX):
            kind: ArtifactKind = "wheel"
        elif candidate.name.endswith(_SDIST_SUFFIX):
            kind = "sdist"
        else:
            raise ReleaseArtifactError(f"Unsupported release artifact type: {candidate.name}")

        return cls(path=candidate, kind=kind)


@dataclass(frozen=True, slots=True)
class ReleaseArtifactSet:
    """Immutable collection of artifacts belonging to one release build."""

    artifacts: tuple[ReleaseArtifact, ...]

    def __post_init__(self) -> None:
        """Reject duplicate artifact paths."""
        paths = [artifact.path for artifact in self.artifacts]
        if len(paths) != len(set(paths)):
            raise ReleaseArtifactError("Duplicate release artifact path")


def enumerate_release_artifacts(
    dist_dir: str | Path,
) -> tuple[ReleaseArtifact, ...]:
    """Enumerate canonical wheel/sdist files from one build directory."""
    directory = Path(dist_dir)
    if not directory.is_dir():
        raise ReleaseArtifactError(f"Release artifact directory does not exist: {directory}")

    candidates = [
        path
        for path in directory.iterdir()
        if path.is_file()
        and (path.name.endswith(_WHEEL_SUFFIX) or path.name.endswith(_SDIST_SUFFIX))
    ]

    return tuple(
        ReleaseArtifact.from_path(path) for path in sorted(candidates, key=lambda item: item.name)
    )


def verify_release_artifact_set(
    artifact_set: ReleaseArtifactSet,
    *,
    expected_project: str,
    expected_version: str,
    inspect_wheel_metadata: bool = False,
) -> ReleaseArtifactSet:
    """Validate the artifact set for one release identity."""
    wheels = [artifact for artifact in artifact_set.artifacts if artifact.kind == "wheel"]
    sdists = [artifact for artifact in artifact_set.artifacts if artifact.kind == "sdist"]

    if len(wheels) != 1 or len(sdists) != 1:
        raise ReleaseArtifactError(
            "Release artifact set must contain exactly one wheel and one sdist"
        )

    for artifact in artifact_set.artifacts:
        _verify_filename_identity(
            artifact,
            expected_project=expected_project,
            expected_version=expected_version,
        )

    if inspect_wheel_metadata:
        _verify_wheel_metadata(
            wheels[0].path,
            expected_project=expected_project,
            expected_version=expected_version,
        )

    return artifact_set


def select_current_wheel(
    dist_dir: str | Path,
    *,
    expected_project: str,
    expected_version: str,
) -> Path:
    """Select the unique wheel matching the current release identity."""
    directory = Path(dist_dir)
    if not directory.is_dir():
        raise ReleaseArtifactError(f"Release artifact directory does not exist: {directory}")

    matches = [
        path
        for path in directory.iterdir()
        if path.is_file()
        and path.name.endswith(_WHEEL_SUFFIX)
        and _filename_matches_identity(
            path.name,
            expected_project=expected_project,
            expected_version=expected_version,
            kind="wheel",
        )
    ]

    if len(matches) != 1:
        raise ReleaseArtifactError(
            f"Expected exactly one current release wheel; found {len(matches)}"
        )

    return matches[0]


def generate_sha256_manifest(
    artifacts: Sequence[ReleaseArtifact],
) -> Mapping[str, str]:
    """Generate deterministic SHA-256 checksums for release artifacts."""
    manifest = {
        artifact.path.name: _sha256_file(artifact.path)
        for artifact in sorted(artifacts, key=lambda item: item.path.name)
    }

    if len(manifest) != len(artifacts):
        raise ReleaseArtifactError(
            "Release artifact filenames must be unique for checksum manifest"
        )

    return MappingProxyType(manifest)


def verify_checksum_manifest(
    artifacts: Sequence[ReleaseArtifact],
    manifest: Mapping[str, str],
) -> None:
    """Verify every release artifact against its recorded SHA-256 checksum."""
    artifact_names = {artifact.path.name for artifact in artifacts}
    manifest_names = set(manifest)

    if artifact_names != manifest_names:
        raise ReleaseArtifactError(
            "Checksum manifest must contain exactly the release artifact set"
        )

    for artifact in artifacts:
        expected = manifest[artifact.path.name]
        actual = _sha256_file(artifact.path)

        if actual != expected:
            raise ReleaseChecksumMismatchError(f"Checksum mismatch for {artifact.path.name}")


def _verify_filename_identity(
    artifact: ReleaseArtifact,
    *,
    expected_project: str,
    expected_version: str,
) -> None:
    """Verify artifact filename belongs to the expected release identity."""
    if not _filename_matches_identity(
        artifact.path.name,
        expected_project=expected_project,
        expected_version=expected_version,
        kind=artifact.kind,
    ):
        raise ReleaseArtifactError(
            f"Release artifact filename does not match expected identity: {artifact.path.name}"
        )


def _filename_matches_identity(
    filename: str,
    *,
    expected_project: str,
    expected_version: str,
    kind: ArtifactKind,
) -> bool:
    """Return whether one artifact filename matches project/version."""
    project_pattern = re.escape(expected_project).replace(r"\-", "[-_]")
    version_pattern = re.escape(expected_version).replace(r"\-", "[-_]")

    if kind == "wheel":
        pattern = (
            rf"^{project_pattern}-{version_pattern}"
            rf"(?:-[^-]+)?-[^-]+-[^-]+-[^-]+\.whl$"
        )
    else:
        pattern = rf"^{project_pattern}-{version_pattern}\.tar\.gz$"

    return re.fullmatch(pattern, filename) is not None


def _verify_wheel_metadata(
    wheel_path: Path,
    *,
    expected_project: str,
    expected_version: str,
) -> None:
    """Inspect wheel METADATA and verify project/version identity."""
    try:
        with zipfile.ZipFile(wheel_path) as archive:
            metadata_names = [
                name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
            ]

            if len(metadata_names) != 1:
                raise ReleaseArtifactError(
                    "Wheel must contain exactly one .dist-info/METADATA file"
                )

            raw = archive.read(metadata_names[0]).decode("utf-8")
    except (OSError, KeyError, UnicodeDecodeError, zipfile.BadZipFile) as exc:
        raise ReleaseArtifactError(f"Unable to inspect wheel metadata: {wheel_path.name}") from exc

    metadata = Parser().parsestr(raw)
    name = metadata.get("Name")
    version = metadata.get("Version")

    if name != expected_project or version != expected_version:
        raise ReleaseArtifactError("Wheel metadata does not match expected release identity")


def _sha256_file(path: Path) -> str:
    """Return the SHA-256 digest for one artifact file."""
    digest = hashlib.sha256()

    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ReleaseArtifactError(f"Unable to read release artifact: {path}") from exc

    return digest.hexdigest()
