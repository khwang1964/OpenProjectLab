"""Contract tests for Step 8.10.5 RC artifact-backed verification."""

from __future__ import annotations

import hashlib
import os
import re
import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"
DESIGN = REPO_ROOT / "docs" / "releases" / "v1.0-rc-artifact-backed-verification.md"

EXPECTED_PROJECT = "openprojectlab"
EXPECTED_VERSION = "1.0.0rc1"
EXPECTED_RC_TAG = "v1.0.0-rc.1"

WHEEL_ENV = "OPL_TEST_WHEEL"
DIST_ENV = "OPL_TEST_DIST_DIR"
CHECKSUM_ENV = "OPL_TEST_CHECKSUM_MANIFEST"
COMMIT_ENV = "OPL_RELEASE_COMMIT_SHA"

REQUIRED_ARTIFACT_INPUTS = {
    WHEEL_ENV,
    DIST_ENV,
    CHECKSUM_ENV,
    COMMIT_ENV,
}

REQUIRED_REUSED_SUITES = {
    "tests/release_readiness/test_v1_integrated_package_release_identity.py",
    "tests/release_readiness/test_v1_artifact_backed_installed_user_e2e.py",
    "tests/release_readiness/test_v1_documentation_first_15_minutes.py",
    "tests/documentation/test_first_15_minutes.py",
}

FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _read(path: Path) -> str:
    assert path.is_file(), f"Required file is missing: {path}"
    return path.read_text(encoding="utf-8")


def _required_path(name: str, *, directory: bool = False) -> Path:
    raw = os.environ.get(name)
    if not raw:
        pytest.skip(f"{name} is not set; the RC artifact gate supplies this input")

    path = Path(raw).expanduser().resolve()
    exists = path.is_dir() if directory else path.is_file()
    if not exists:
        kind = "directory" if directory else "file"
        pytest.fail(f"{name} does not name a {kind}: {path}")
    return path


def _manifest() -> dict[str, str]:
    path = _required_path(CHECKSUM_ENV)
    entries: dict[str, str] = {}

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, filename = line.split(maxsplit=1)
        entries[filename.lstrip("* ")] = digest

    return entries


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_rc_artifact_backed_governing_design_exists() -> None:
    """Step 8.10.5 must have an explicit governing design."""
    assert DESIGN.is_file()


def test_rc_artifact_backed_contract_keeps_expected_identity() -> None:
    """The RC artifact gate must remain bound to the first RC identity."""
    project = tomllib.loads(_read(PYPROJECT))["project"]

    assert isinstance(project, dict)
    assert project["name"] == EXPECTED_PROJECT
    assert project["version"] == EXPECTED_VERSION

    design = _read(DESIGN)
    assert EXPECTED_VERSION in design
    assert EXPECTED_RC_TAG in design


def test_contract_names_all_required_artifact_inputs() -> None:
    """Completion evidence must require all four artifact identity inputs."""
    design = _read(DESIGN)

    missing = sorted(name for name in REQUIRED_ARTIFACT_INPUTS if name not in design)
    assert missing == []


def test_required_reused_artifact_backed_suites_remain_present() -> None:
    """Step 8.10.5 must reuse existing accepted artifact-backed authorities."""
    missing = sorted(
        relative for relative in REQUIRED_REUSED_SUITES if not (REPO_ROOT / relative).is_file()
    )
    assert missing == []


def test_contract_rejects_required_skips_as_completion_evidence() -> None:
    """Artifact-backed skips may not satisfy final Step 8.10.5 evidence."""
    normalized = " ".join(_read(DESIGN).lower().split())

    assert "zero required artifact-backed skips" in normalized
    assert "required artifact-backed skips do not count" in normalized


def test_contract_remains_prepublication() -> None:
    """Artifact-backed verification must not create or accept a release."""
    normalized = " ".join(_read(DESIGN).lower().split())

    assert "create or move `v1.0.0-rc.1`" in normalized
    assert "publication remains later" in normalized
    assert "formally accept the rc" in normalized


def test_configured_rc_wheel_belongs_to_configured_dist_directory() -> None:
    """The installed wheel must be one exact artifact from the RC build set."""
    wheel = _required_path(WHEEL_ENV)
    dist = _required_path(DIST_ENV, directory=True)

    assert wheel.parent == dist
    assert wheel.name == "openprojectlab-1.0.0rc1-py3-none-any.whl"


def test_configured_dist_contains_exact_current_rc_distributions() -> None:
    """The RC dist directory must expose one current wheel and one current sdist."""
    dist = _required_path(DIST_ENV, directory=True)

    distributions = sorted(
        path.name
        for path in dist.iterdir()
        if path.is_file() and (path.name.endswith(".whl") or path.name.endswith(".tar.gz"))
    )

    assert distributions == [
        "openprojectlab-1.0.0rc1-py3-none-any.whl",
        "openprojectlab-1.0.0rc1.tar.gz",
    ]


def test_configured_checksum_manifest_matches_exact_rc_artifact_bytes() -> None:
    """The configured manifest must bind the exact current wheel and sdist bytes."""
    dist = _required_path(DIST_ENV, directory=True)
    recorded = _manifest()

    artifacts = sorted(
        (
            path
            for path in dist.iterdir()
            if path.is_file() and (path.name.endswith(".whl") or path.name.endswith(".tar.gz"))
        ),
        key=lambda path: path.name,
    )

    generated = {path.name: _sha256(path) for path in artifacts}

    assert recorded == generated
    assert set(recorded) == {
        "openprojectlab-1.0.0rc1-py3-none-any.whl",
        "openprojectlab-1.0.0rc1.tar.gz",
    }
    assert all(re.fullmatch(r"[0-9a-f]{64}", digest) for digest in recorded.values())


def test_configured_release_source_sha_is_full_immutable_identity() -> None:
    """The artifact-backed gate requires one full immutable source SHA."""
    commit_sha = os.environ.get(COMMIT_ENV)
    if not commit_sha:
        pytest.skip(f"{COMMIT_ENV} is not set; the RC artifact gate supplies this input")

    assert FULL_SHA_RE.fullmatch(commit_sha)
