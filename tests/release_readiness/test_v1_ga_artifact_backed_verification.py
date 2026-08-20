"""Fail-closed coordination tests for GA.4 artifact-backed verification."""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

DESIGN = REPO_ROOT / "docs" / "releases" / "v1.0-ga-artifact-backed-verification.md"

EXPECTED_VERSION = "1.0.0"
EXPECTED_GA_TAG = "v1.0.0"
EXPECTED_WHEEL = "openprojectlab-1.0.0-py3-none-any.whl"
EXPECTED_SDIST = "openprojectlab-1.0.0.tar.gz"

WHEEL_ENV = "OPL_TEST_WHEEL"
DIST_ENV = "OPL_TEST_DIST_DIR"
CHECKSUM_ENV = "OPL_TEST_CHECKSUM_MANIFEST"
COMMIT_ENV = "OPL_RELEASE_COMMIT_SHA"

REQUIRED_ARTIFACT_INPUTS = (
    WHEEL_ENV,
    DIST_ENV,
    CHECKSUM_ENV,
    COMMIT_ENV,
)

REQUIRED_REUSED_SUITES = (
    "tests/release_readiness/test_v1_integrated_package_release_identity.py",
    "tests/release_readiness/test_v1_artifact_backed_installed_user_e2e.py",
    "tests/release_readiness/test_v1_documentation_first_15_minutes.py",
    "tests/documentation/test_first_15_minutes.py",
)

FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _read(path: Path) -> str:
    assert path.is_file(), f"Required GA.4 file is missing: {path}"
    return path.read_text(encoding="utf-8")


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    assert value, f"{name} must be set for GA.4 completion evidence"
    return value


def _required_path(name: str, *, directory: bool = False) -> Path:
    path = Path(_required_env(name)).expanduser().resolve()
    exists = path.is_dir() if directory else path.is_file()
    kind = "directory" if directory else "file"
    assert exists, f"{name} must name an existing {kind}: {path}"
    return path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest() -> dict[str, str]:
    path = _required_path(CHECKSUM_ENV)
    raw = path.read_text(encoding="utf-8")
    assert not raw.startswith("\ufeff"), "GA checksum manifest must not contain a BOM"

    entries: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        digest, filename = line.split(maxsplit=1)
        filename = filename.lstrip("* ")
        digest = digest.lower()
        assert SHA256_RE.fullmatch(digest), f"Invalid SHA-256 digest for {filename}"
        entries[filename] = digest
    return entries


def test_ga_artifact_backed_governing_design_exists() -> None:
    assert DESIGN.is_file()


def test_ga_4_contract_keeps_stable_identity() -> None:
    normalized = " ".join(_read(DESIGN).split())

    assert EXPECTED_VERSION in normalized
    assert EXPECTED_GA_TAG in normalized
    assert EXPECTED_WHEEL in normalized
    assert EXPECTED_SDIST in normalized


def test_all_required_ga_artifact_inputs_are_present() -> None:
    missing = [name for name in REQUIRED_ARTIFACT_INPUTS if not os.environ.get(name)]
    assert missing == [], f"Missing required GA artifact inputs: {missing}"


def test_required_reused_artifact_backed_suites_remain_present() -> None:
    missing = [
        relative for relative in REQUIRED_REUSED_SUITES if not (REPO_ROOT / relative).is_file()
    ]
    assert missing == []


def test_configured_ga_wheel_belongs_to_configured_dist_directory() -> None:
    wheel = _required_path(WHEEL_ENV)
    dist = _required_path(DIST_ENV, directory=True)

    assert wheel.parent == dist
    assert wheel.name == EXPECTED_WHEEL


def test_configured_dist_contains_exact_ga_distributions() -> None:
    dist = _required_path(DIST_ENV, directory=True)

    distributions = sorted(
        path.name
        for path in dist.iterdir()
        if path.is_file() and (path.name.endswith(".whl") or path.name.endswith(".tar.gz"))
    )

    assert distributions == [EXPECTED_WHEEL, EXPECTED_SDIST]


def test_configured_checksum_manifest_matches_exact_ga_artifact_bytes() -> None:
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
    assert set(recorded) == {EXPECTED_WHEEL, EXPECTED_SDIST}


def test_configured_release_source_sha_is_full_immutable_identity() -> None:
    commit_sha = _required_env(COMMIT_ENV)

    assert FULL_SHA_RE.fullmatch(commit_sha)


def test_ga_4_contract_rejects_required_skips_as_completion_evidence() -> None:
    normalized = " ".join(_read(DESIGN).lower().split())

    assert "required ga artifact-backed skips" in normalized
    assert "0" in normalized
    assert "must not silently skip" in normalized


def test_ga_4_contract_remains_prepublication() -> None:
    """GA.4 must remain an artifact-verification gate, not a publication gate."""
    normalized = " ".join(_read(DESIGN).lower().split())

    assert "ga.4 does not:" in normalized
    assert "create `v1.0.0`" in normalized
    assert "push `v1.0.0`" in normalized
    assert "create or publish a github release" in normalized
    assert "formally accept ga" in normalized
