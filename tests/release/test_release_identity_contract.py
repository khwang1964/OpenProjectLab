"""Contract tests for release version / tag / commit identity."""

from __future__ import annotations

import importlib
import subprocess
import tomllib
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"

EXPECTED_RELEASE_MODULE = "generator.release.identity"
EXPECTED_PROJECT_NAME = "openprojectlab"


@pytest.fixture(scope="module")
def release_identity_module() -> ModuleType:
    """Import the production release-identity module expected by Step 8.8.2."""
    try:
        return importlib.import_module(EXPECTED_RELEASE_MODULE)
    except ModuleNotFoundError:
        pytest.fail(
            "Step 8.8.2 requires production release identity support at "
            f"{EXPECTED_RELEASE_MODULE!r}; implement the contract before "
            "turning these tests green."
        )


@pytest.fixture(scope="module")
def pyproject_data() -> dict[str, object]:
    """Load the repository's canonical packaging metadata."""
    with PYPROJECT_PATH.open("rb") as stream:
        return tomllib.load(stream)


def _git(*args: str) -> str:
    """Run a read-only git command against the repository."""
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_pyproject_is_canonical_version_source(
    pyproject_data: dict[str, object],
) -> None:
    """The package version must remain reviewable repository state."""
    project = pyproject_data["project"]

    assert isinstance(project, dict)
    assert project["name"] == EXPECTED_PROJECT_NAME

    version = project["version"]
    assert isinstance(version, str)
    assert version.strip()
    assert version == version.strip()


def test_release_identity_module_exposes_minimum_public_contract(
    release_identity_module: ModuleType,
) -> None:
    """Step 8.8.2 needs one small side-effect-free release identity API."""
    required_symbols = {
        "ReleaseIdentity",
        "ReleaseIdentityError",
        "ReleaseTagConflictError",
        "read_canonical_version",
        "expected_release_tag",
        "validate_release_identity",
    }

    missing = sorted(
        symbol for symbol in required_symbols if not hasattr(release_identity_module, symbol)
    )

    assert missing == [], f"Missing release identity symbols: {missing}"


def test_read_canonical_version_matches_pyproject(
    release_identity_module: ModuleType,
    pyproject_data: dict[str, object],
) -> None:
    """Production version resolution must reuse [project].version."""
    project = pyproject_data["project"]
    assert isinstance(project, dict)

    expected = project["version"]
    actual = release_identity_module.read_canonical_version(PYPROJECT_PATH)

    assert actual == expected


@pytest.mark.parametrize(
    ("version", "expected"),
    [
        ("0.6.0", "v0.6.0"),
        ("1.0.0", "v1.0.0"),
        ("1.0.0rc1", "v1.0.0rc1"),
    ],
)
def test_expected_release_tag_is_deterministic(
    release_identity_module: ModuleType,
    version: str,
    expected: str,
) -> None:
    """The release tag must be derived from the canonical version only."""
    assert release_identity_module.expected_release_tag(version) == expected


@pytest.mark.parametrize(
    "version",
    [
        "",
        " ",
        "v1.0.0",
        "1.0",
        "release-1.0.0",
    ],
)
def test_expected_release_tag_rejects_noncanonical_version_input(
    release_identity_module: ModuleType,
    version: str,
) -> None:
    """Tag derivation must fail closed for malformed or already-tagged input."""
    with pytest.raises(release_identity_module.ReleaseIdentityError):
        release_identity_module.expected_release_tag(version)


def test_release_identity_requires_explicit_commit_sha(
    release_identity_module: ModuleType,
) -> None:
    """A release must bind to an immutable commit, not only a branch."""
    with pytest.raises(release_identity_module.ReleaseIdentityError):
        release_identity_module.ReleaseIdentity(
            version="1.0.0",
            commit_sha="",
            tag="v1.0.0",
        )


@pytest.mark.parametrize(
    "commit_sha",
    [
        "main",
        "origin/main",
        "HEAD",
        "release/v1.0.0",
        "1234",
    ],
)
def test_release_identity_rejects_floating_or_invalid_commit_identity(
    release_identity_module: ModuleType,
    commit_sha: str,
) -> None:
    """Release identity must use a full immutable Git commit SHA."""
    with pytest.raises(release_identity_module.ReleaseIdentityError):
        release_identity_module.ReleaseIdentity(
            version="1.0.0",
            commit_sha=commit_sha,
            tag="v1.0.0",
        )


def test_release_identity_accepts_current_repository_head_sha(
    release_identity_module: ModuleType,
) -> None:
    """The repository HEAD SHA is a valid immutable source identity."""
    head_sha = _git("rev-parse", "HEAD")

    identity = release_identity_module.ReleaseIdentity(
        version="1.0.0",
        commit_sha=head_sha,
        tag="v1.0.0",
    )

    assert identity.commit_sha == head_sha


def test_release_identity_rejects_version_tag_mismatch(
    release_identity_module: ModuleType,
) -> None:
    """Version and tag must describe the same logical release."""
    with pytest.raises(release_identity_module.ReleaseIdentityError):
        release_identity_module.ReleaseIdentity(
            version="1.0.0",
            commit_sha="a" * 40,
            tag="v1.0.1",
        )


def test_release_identity_is_immutable(
    release_identity_module: ModuleType,
) -> None:
    """Release identity must not change after validation."""
    identity = release_identity_module.ReleaseIdentity(
        version="1.0.0",
        commit_sha="a" * 40,
        tag="v1.0.0",
    )

    with pytest.raises((AttributeError, TypeError)):
        identity.version = "1.0.1"


def test_validate_release_identity_accepts_matching_values(
    release_identity_module: ModuleType,
) -> None:
    """Pure validation accepts a coherent version / SHA / tag tuple."""
    identity = release_identity_module.ReleaseIdentity(
        version="1.0.0",
        commit_sha="a" * 40,
        tag="v1.0.0",
    )

    validated = release_identity_module.validate_release_identity(
        identity,
        tag_target_sha="a" * 40,
    )

    assert validated is identity


def test_validate_release_identity_rejects_tag_target_mismatch(
    release_identity_module: ModuleType,
) -> None:
    """A release tag must point at the approved release commit."""
    identity = release_identity_module.ReleaseIdentity(
        version="1.0.0",
        commit_sha="a" * 40,
        tag="v1.0.0",
    )

    with pytest.raises(release_identity_module.ReleaseTagConflictError):
        release_identity_module.validate_release_identity(
            identity,
            tag_target_sha="b" * 40,
        )


def test_validate_release_identity_allows_tag_not_yet_created(
    release_identity_module: ModuleType,
) -> None:
    """Pre-tag validation may proceed when no conflicting tag exists yet."""
    identity = release_identity_module.ReleaseIdentity(
        version="1.0.0",
        commit_sha="a" * 40,
        tag="v1.0.0",
    )

    validated = release_identity_module.validate_release_identity(
        identity,
        tag_target_sha=None,
    )

    assert validated is identity


def test_validate_release_identity_has_no_git_side_effects(
    release_identity_module: ModuleType,
) -> None:
    """Pure identity validation must not create or move Git tags."""
    identity = release_identity_module.ReleaseIdentity(
        version="1.0.0",
        commit_sha="a" * 40,
        tag="v1.0.0",
    )
    before = _git("status", "--porcelain")

    release_identity_module.validate_release_identity(
        identity,
        tag_target_sha=None,
    )

    after = _git("status", "--porcelain")
    assert after == before


def test_release_identity_does_not_require_github_or_network(
    release_identity_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Step 8.8.2 identity rules must remain deterministic and offline."""

    def _unexpected_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("Release identity validation must not use network access")

    monkeypatch.setattr("urllib.request.urlopen", _unexpected_network)

    identity = release_identity_module.ReleaseIdentity(
        version="1.0.0",
        commit_sha="a" * 40,
        tag="v1.0.0",
    )

    assert (
        release_identity_module.validate_release_identity(
            identity,
            tag_target_sha=None,
        )
        is identity
    )
