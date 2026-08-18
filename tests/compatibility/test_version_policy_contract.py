"""Contract tests for the v1 compatibility version policy."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO_ROOT / "docs" / "releases" / "v1.0-compatibility-deprecation-policy.md"

REQUIRED_CLASSIFICATIONS = frozenset(
    {
        "Stable",
        "Candidate",
        "Experimental",
        "Internal",
        "Deferred",
    }
)

VERSION_SERIES_MARKERS = frozenset(
    {
        "v1.0.x",
        "v1.x",
        "v2.0",
    }
)

COMPATIBILITY_MARKERS = frozenset(
    {
        "Compatible Change",
        "Breaking Change",
        "Deprecation Lifecycle",
        "Emergency Compatibility Exception",
    }
)


@pytest.fixture(scope="module")
def policy_text() -> str:
    """Return normalized Step 8.6 policy text."""
    if not POLICY_PATH.is_file():
        pytest.fail(f"Missing Step 8.6 governing policy: {POLICY_PATH.relative_to(REPO_ROOT)}")

    raw = POLICY_PATH.read_text(encoding="utf-8")
    return _normalize_whitespace(raw)


def _normalize_whitespace(text: str) -> str:
    """Collapse Markdown wrapping without changing canonical identifiers."""
    return re.sub(r"\s+", " ", text).strip()


def _assert_all_present(text: str, required: frozenset[str]) -> None:
    """Assert that every required canonical policy marker is present."""
    missing = sorted(marker for marker in required if marker not in text)
    assert missing == [], f"Policy is missing required markers: {missing}"


def test_policy_document_exists() -> None:
    """Step 8.6 must have one canonical governing policy document."""
    assert POLICY_PATH.is_file()


def test_policy_defines_all_version_series(policy_text: str) -> None:
    """The policy must explicitly govern patch, minor, and major releases."""
    _assert_all_present(policy_text, VERSION_SERIES_MARKERS)


def test_v1_0_x_is_compatibility_preserving(policy_text: str) -> None:
    """Patch releases must preserve the frozen Stable v1 contract."""
    assert "v1.0.x --- Compatibility-Preserving Fixes" in policy_text
    assert "Patch releases are the most conservative maintenance line." in policy_text
    assert "must not intentionally remove or rename Stable symbols" in policy_text


def test_v1_x_is_backward_compatible_evolution(policy_text: str) -> None:
    """Minor releases may add capability but must preserve Stable v1 behavior."""
    assert "v1.x --- Backward-Compatible Evolution" in policy_text
    assert (
        "Minor releases may evolve OPL while preserving existing Stable v1 behavior." in policy_text
    )
    assert (
        "must not intentionally remove or incompatibly redefine a Stable v1 contract" in policy_text
    )


def test_v2_0_allows_governed_breaking_change(policy_text: str) -> None:
    """Major releases may break Stable contracts only with explicit governance."""
    assert "v2.0 --- Intentional Breaking Evolution" in policy_text
    assert (
        "A major release may intentionally remove or incompatibly change Stable v1 "
        "contracts" in policy_text
    )
    assert "migration/replacement guidance" in policy_text
    assert (
        "A major version permits breaking change; it does not permit undocumented "
        "breaking change." in policy_text
    )


def test_policy_keeps_contract_classifications_distinct(policy_text: str) -> None:
    """Step 8.6 must preserve the Step 8.2 classification model."""
    _assert_all_present(policy_text, REQUIRED_CLASSIFICATIONS)

    assert (
        "Only contracts explicitly classified Stable receive the full v1 "
        "compatibility commitment." in policy_text
    )
    assert "Experimental capabilities do not receive the full Stable guarantee." in (policy_text)
    assert "Internal behavior may evolve during compatible v1 releases" in policy_text
    assert "Deferred capabilities are outside v1.0 scope" in policy_text


def test_policy_defines_compatible_and_breaking_change_behaviorally(
    policy_text: str,
) -> None:
    """Compatibility must be judged by behavior rather than symbol presence only."""
    _assert_all_present(policy_text, COMPATIBILITY_MARKERS)

    assert "Compatibility Is Behavioral" in policy_text
    assert "Compatibility is not limited to whether a Python import still succeeds." in policy_text
    assert (
        "A breaking change requires an existing Stable consumer to modify code, "
        "commands, configuration, expected artifacts, or operational assumptions" in policy_text
    )


def test_normal_stable_removal_is_deferred_until_next_major(
    policy_text: str,
) -> None:
    """Normal Stable removal must not occur during the v1 release line."""
    assert "Minimum Deprecation Window" in policy_text
    assert "remove or break no earlier than v2.0" in policy_text
    assert "Normal Stable removal is therefore not permitted in v1.0.x or v1.x." in policy_text


def test_deprecation_is_not_removal(policy_text: str) -> None:
    """Deprecated Stable behavior must remain available during the v1 line."""
    assert "Deprecation is not removal." in policy_text
    assert "Deprecated Stable (still functional)" in policy_text
    assert "Deprecated Stable behavior remains part of the v1 compatibility surface." in policy_text


def test_major_breaking_change_requires_migration_guidance(policy_text: str) -> None:
    """A major-version break must still include migration guidance."""
    assert "Migration Guidance" in policy_text
    assert (
        "Migration guidance is mandatory before a deprecated Stable contract is "
        "removed or incompatibly changed." in policy_text
    )
    assert "replacement usage" in policy_text
    assert "validation steps after migration" in policy_text


def test_emergency_break_requires_explicit_governance(policy_text: str) -> None:
    """Early breaking changes require a narrow documented emergency exception."""
    required_fields = frozenset(
        {
            "Affected Stable contract:",
            "Why compatibility cannot safely be preserved:",
            "Migration / mitigation:",
            "Approver / review record:",
        }
    )
    _assert_all_present(policy_text, required_fields)

    assert "Emergency Compatibility Exception" in policy_text
    assert (
        "Convenience, cleanup, refactoring preference, or implementation "
        "simplification are insufficient reasons." in policy_text
    )


def test_policy_preserves_step_8_2_as_surface_source_of_truth(
    policy_text: str,
) -> None:
    """Step 8.6 must govern compatibility without duplicating the frozen inventory."""
    assert (
        "Step 8.2 contract-freeze tests remain authoritative for the exact v1.0 "
        "Stable surface." in policy_text
    )
    assert "Step 8.6 must not duplicate that source of truth unnecessarily." in policy_text


def test_policy_does_not_preempt_step_8_7_or_step_8_8(policy_text: str) -> None:
    """Compatibility governance must keep later Milestone 8 ownership separate."""
    assert "Step 8.7 support-matrix" in policy_text
    assert "Step 8.8 release publication/reproducibility automation" in policy_text
    assert "does not create Step 8.7 support claims" in policy_text
    assert "does not pre-empt Step 8.8 release automation" in policy_text


def test_policy_requires_compatibility_review_record(policy_text: str) -> None:
    """Stable-contract changes must carry explicit compatibility review metadata."""
    required_fields = frozenset(
        {
            "Affected contract:",
            "Classification:",
            "Current behavior:",
            "Proposed behavior:",
            "Compatibility impact:",
            "Why compatible / breaking:",
            "Deprecation required:",
            "Migration required:",
            "Documentation impact:",
            "Test impact:",
            "Release-series eligibility:",
            "Emergency exception: yes/no",
        }
    )

    _assert_all_present(policy_text, required_fields)
