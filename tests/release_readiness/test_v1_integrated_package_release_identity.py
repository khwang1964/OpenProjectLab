"""Step 8.9.6 integrated package and release-identity verification."""

from __future__ import annotations

import configparser
import os
import re
import subprocess
import tarfile
import tomllib
import zipfile
from email.parser import Parser
from pathlib import Path, PurePosixPath

import pytest

from generator.release.artifacts import (
    ReleaseArtifact,
    ReleaseArtifactSet,
    enumerate_release_artifacts,
    generate_sha256_manifest,
    verify_checksum_manifest,
    verify_release_artifact_set,
)
from generator.release.identity import (
    ReleaseIdentity,
    expected_release_tag,
    read_canonical_version,
    validate_release_identity,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"
DIST_DIR_ENV = "OPL_TEST_DIST_DIR"
WHEEL_ENV = "OPL_TEST_WHEEL"
CHECKSUM_ENV = "OPL_TEST_CHECKSUM_MANIFEST"
COMMIT_ENV = "OPL_RELEASE_COMMIT_SHA"
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _required_path(environment_name: str, *, directory: bool = False) -> Path:
    raw = os.environ.get(environment_name)
    if not raw:
        pytest.skip(f"{environment_name} is not set; the packaging gate supplies release artifacts")

    path = Path(raw).expanduser().resolve()
    expected_type_exists = path.is_dir() if directory else path.is_file()
    if not expected_type_exists:
        expected_type = "directory" if directory else "file"
        pytest.fail(f"{environment_name} does not name a {expected_type}: {path}")
    return path


def _project() -> dict[str, object]:
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]
    assert isinstance(project, dict)
    return project


def _artifacts() -> tuple[ReleaseArtifact, ...]:
    return enumerate_release_artifacts(_required_path(DIST_DIR_ENV, directory=True))


def _artifact(kind: str) -> ReleaseArtifact:
    matches = [artifact for artifact in _artifacts() if artifact.kind == kind]
    assert len(matches) == 1
    return matches[0]


def _manifest() -> dict[str, str]:
    path = _required_path(CHECKSUM_ENV)
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, filename = line.split(maxsplit=1)
        entries[filename.lstrip("* ")] = digest
    return entries


def _wheel_text(wheel: Path, suffix: str) -> str:
    with zipfile.ZipFile(wheel) as archive:
        matches = [name for name in archive.namelist() if name.endswith(suffix)]
        assert len(matches) == 1
        return archive.read(matches[0]).decode("utf-8")


def _sdist_root_text(sdist: Path, filename: str) -> str:
    with tarfile.open(sdist, "r:gz") as archive:
        matches = [
            member
            for member in archive.getmembers()
            if PurePosixPath(member.name).parts[1:] == (filename,)
        ]
        assert len(matches) == 1
        stream = archive.extractfile(matches[0])
        assert stream is not None
        return stream.read().decode("utf-8")


def test_complete_artifact_set_matches_canonical_project_identity() -> None:
    project = _project()
    artifacts = _artifacts()
    artifact_set = ReleaseArtifactSet(artifacts=artifacts)

    verified = verify_release_artifact_set(
        artifact_set,
        expected_project=str(project["name"]),
        expected_version=str(project["version"]),
        inspect_wheel_metadata=True,
    )

    assert verified is artifact_set
    assert {artifact.kind for artifact in artifacts} == {"wheel", "sdist"}
    assert _required_path(WHEEL_ENV) == _artifact("wheel").path.resolve()


def test_wheel_and_sdist_internal_metadata_match_canonical_identity() -> None:
    project = _project()
    expected_name = str(project["name"])
    expected_version = str(project["version"])
    wheel = _artifact("wheel").path
    sdist = _artifact("sdist").path

    wheel_metadata = Parser().parsestr(_wheel_text(wheel, ".dist-info/METADATA"))
    sdist_metadata = Parser().parsestr(_sdist_root_text(sdist, "PKG-INFO"))
    sdist_pyproject = tomllib.loads(_sdist_root_text(sdist, "pyproject.toml"))["project"]

    assert wheel_metadata["Name"] == expected_name
    assert wheel_metadata["Version"] == expected_version
    assert sdist_metadata["Name"] == expected_name
    assert sdist_metadata["Version"] == expected_version
    assert sdist_pyproject["name"] == expected_name
    assert sdist_pyproject["version"] == expected_version


def test_wheel_console_entry_point_matches_canonical_contract() -> None:
    entry_points = configparser.ConfigParser()
    entry_points.read_string(_wheel_text(_artifact("wheel").path, ".dist-info/entry_points.txt"))

    assert entry_points["console_scripts"]["opl"] == "generator.cli.main:main"


def test_recorded_checksums_cover_and_verify_the_exact_artifact_set() -> None:
    artifacts = _artifacts()
    recorded = _manifest()
    generated = dict(generate_sha256_manifest(artifacts))

    assert recorded == generated
    assert all(re.fullmatch(r"[0-9a-f]{64}", digest) for digest in recorded.values())
    verify_checksum_manifest(artifacts, recorded)


def test_release_source_identity_binds_canonical_version_to_build_commit() -> None:
    commit_sha = os.environ.get(COMMIT_ENV)
    if not commit_sha:
        pytest.skip(f"{COMMIT_ENV} is not set; the packaging gate supplies the build commit")

    assert FULL_SHA_RE.fullmatch(commit_sha)
    assert commit_sha == _git("rev-parse", "HEAD")

    version = read_canonical_version(PYPROJECT)
    identity = ReleaseIdentity(
        version=version,
        commit_sha=commit_sha,
        tag=expected_release_tag(version),
    )

    assert validate_release_identity(identity, tag_target_sha=None) is identity
