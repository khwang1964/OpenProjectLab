"""Fail-closed v1.1 artifact-backed reliability contract."""

from __future__ import annotations

import configparser
import json
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
    validate_release_identity,
)

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = ROOT / "pyproject.toml"
DESIGN = ROOT / "docs" / "releases" / "v1.1-reliability-artifact-backed-verification.md"
DOC_PARITY = ROOT / "docs" / "releases" / "v1.1-documentation-parity.md"

DIST_DIR_ENV = "OPL_TEST_DIST_DIR"
WHEEL_ENV = "OPL_TEST_WHEEL"
CHECKSUM_ENV = "OPL_TEST_CHECKSUM_MANIFEST"
COMMIT_ENV = "OPL_RELEASE_COMMIT_SHA"

EVIDENCE_NAME = "candidate-build-evidence.json"
REPOSITORY_VERSION = "1.0.0"
EXPECTED_CANDIDATE_VERSION = "1.1.0rc1"
EXPECTED_CANDIDATE_TAG = "v1.1.0-rc.1"

FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _read(path: Path) -> str:
    if not path.is_file():
        pytest.fail(f"Missing required v1.1 release authority: {path}")
    return path.read_text(encoding="utf-8")


def _required_path(environment_name: str, *, directory: bool = False) -> Path:
    raw = os.environ.get(environment_name)
    if not raw:
        pytest.skip(
            f"{environment_name} is not set; the v1.1 packaging gate "
            "supplies candidate artifact evidence"
        )

    path = Path(raw).expanduser().resolve()
    valid = path.is_dir() if directory else path.is_file()
    if not valid:
        kind = "directory" if directory else "file"
        pytest.fail(f"{environment_name} does not name a {kind}: {path}")
    return path


def _repository_project() -> dict[str, object]:
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]
    assert isinstance(project, dict)
    return project


def _evidence() -> dict[str, object]:
    dist = _required_path(DIST_DIR_ENV, directory=True)
    path = dist / EVIDENCE_NAME
    if not path.is_file():
        pytest.fail(f"Missing candidate build evidence: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _candidate_project_name() -> str:
    return str(_repository_project()["name"])


def _candidate_version() -> str:
    evidence = _evidence()
    version = str(evidence["candidate_version"])
    assert version == EXPECTED_CANDIDATE_VERSION
    return version


def _artifacts() -> tuple[ReleaseArtifact, ...]:
    return enumerate_release_artifacts(_required_path(DIST_DIR_ENV, directory=True))


def _artifact(kind: str) -> ReleaseArtifact:
    matches = [artifact for artifact in _artifacts() if artifact.kind == kind]
    assert len(matches) == 1
    return matches[0]


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


def _manifest() -> dict[str, str]:
    path = _required_path(CHECKSUM_ENV)
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, filename = line.split(maxsplit=1)
        entries[filename.lstrip("* ")] = digest
    return entries


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_v1_1_8_governing_design_is_terminally_accepted_without_accepting_v1_1() -> None:
    text = _read(DESIGN)

    assert "v1.1.8 --- Reliability / Artifact-backed Verification" in text
    assert "v1.1.8 Reliability / Artifact-backed Verification --- Accepted" in text
    assert "Implementation / Evidence PR #216 --- Merged" in text
    assert ("Implementation merge --- 19103257e7fe405f8d38ad4e43fd549e78867bde") in text

    assert "Candidate build boundary --- Passed" in text
    assert "Artifact identity verification --- Passed" in text
    assert "Clean-installed user verification --- Passed" in text
    assert "Post-merge consistency verification --- Passed" in text

    assert "Formal v1.1 Acceptance --- Not Accepted" in text
    assert "Next --- v1.1.9 Formal v1.1 Acceptance" in text


def test_v1_1_7_documentation_predecessor_is_accepted() -> None:
    text = _read(DOC_PARITY)

    assert "v1.1.7 Documentation / EN-zh-TW Parity --- Accepted" in text
    assert "Formal v1.1 Acceptance --- Not Accepted" in text


def test_repository_identity_remains_v1_0_while_candidate_is_v1_1_rc() -> None:
    project = _repository_project()
    evidence = _evidence()

    assert project["version"] == REPOSITORY_VERSION
    assert evidence["repository_version"] == REPOSITORY_VERSION
    assert evidence["candidate_version"] == EXPECTED_CANDIDATE_VERSION
    assert evidence["candidate_tag"] == EXPECTED_CANDIDATE_TAG


def test_candidate_artifact_set_matches_candidate_identity() -> None:
    artifacts = _artifacts()
    artifact_set = ReleaseArtifactSet(artifacts=artifacts)

    verified = verify_release_artifact_set(
        artifact_set,
        expected_project=_candidate_project_name(),
        expected_version=_candidate_version(),
        inspect_wheel_metadata=True,
    )

    assert verified is artifact_set
    assert {artifact.kind for artifact in artifacts} == {"wheel", "sdist"}
    assert _required_path(WHEEL_ENV) == _artifact("wheel").path.resolve()


def test_candidate_wheel_and_sdist_metadata_match_candidate_identity() -> None:
    expected_name = _candidate_project_name()
    expected_version = _candidate_version()

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


def test_candidate_wheel_preserves_opl_console_entry_point() -> None:
    parser = configparser.ConfigParser()
    parser.read_string(_wheel_text(_artifact("wheel").path, ".dist-info/entry_points.txt"))

    assert parser["console_scripts"]["opl"] == "generator.cli.main:main"


def test_candidate_checksum_manifest_covers_exact_artifact_set() -> None:
    artifacts = _artifacts()
    recorded = _manifest()
    generated = dict(generate_sha256_manifest(artifacts))

    assert recorded == generated
    assert all(re.fullmatch(r"[0-9a-f]{64}", digest) for digest in recorded.values())
    verify_checksum_manifest(artifacts, recorded)


def test_candidate_source_identity_matches_build_evidence() -> None:
    commit_sha = os.environ.get(COMMIT_ENV)
    if not commit_sha:
        pytest.skip(
            f"{COMMIT_ENV} is not set; the v1.1 packaging gate supplies the candidate source commit"
        )

    assert FULL_SHA_RE.fullmatch(commit_sha)

    evidence = _evidence()
    assert evidence["source_commit_sha"] == commit_sha

    resolved = _git("rev-parse", f"{commit_sha}^{{commit}}")
    assert resolved == commit_sha

    identity = ReleaseIdentity(
        version=_candidate_version(),
        commit_sha=commit_sha,
        tag=EXPECTED_CANDIDATE_TAG,
    )

    assert expected_release_tag(_candidate_version()) == EXPECTED_CANDIDATE_TAG
    assert validate_release_identity(identity, tag_target_sha=None) is identity


def test_candidate_source_commit_remains_reachable_from_current_history() -> None:
    commit_sha = os.environ.get(COMMIT_ENV)
    if not commit_sha:
        pytest.skip(
            f"{COMMIT_ENV} is not set; the v1.1 packaging gate supplies the candidate source commit"
        )

    assert FULL_SHA_RE.fullmatch(commit_sha)

    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit_sha, "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        f"candidate source commit {commit_sha} must remain reachable from HEAD"
    )


def test_v1_1_8_keeps_core_verification_network_and_credential_free() -> None:
    text = _read(DESIGN)

    required = (
        "credential-free",
        "network-independent",
        "Experimental live-provider path is not required",
        "Formal v1.1 Acceptance:** Not Accepted",
    )
    for term in required:
        assert term in text
