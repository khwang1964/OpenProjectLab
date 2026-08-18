"""Contract tests for the v1 deprecation policy."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO_ROOT / "docs" / "releases" / "v1.0-compatibility-deprecation-policy.md"

REQUIRED_DEPRECATION_RECORD_FIELDS = frozenset(
    {
        "Contract:",
        "Canonical identity/access path:",
        "Classification: Stable → Deprecated Stable",
        "Deprecation introduced in:",
        "Reason:",
        "Replacement:",
        "Migration path:",
        "Behavior during deprecation:",
        "Expected removal:",
        "Documentation locations:",
        "Tests protecting compatibility:",
        "Owner:",
    }
)

REQUIRED_MIGRATION_GUIDANCE_MARKERS = frozenset(
    {
        "old usage",
        "replacement usage",
        "semantic differences",
        "changed defaults",
        "configuration changes",
        "artifact/output differences",
        "failure-behavior differences",
        "plugin/integration impact",
        "automated migration support, if any",
        "validation steps after migration",
    }
)

REQUIRED_EMERGENCY_EXCEPTION_FIELDS = frozenset(
    {
        "Affected Stable contract:",
        "Severity:",
        "Why compatibility cannot safely be preserved:",
        "Why deprecation cannot reasonably precede the fix:",
        "User impact:",
        "Migration / mitigation:",
        "Tests:",
        "Documentation:",
        "Release-note notice:",
        "Approver / review record:",
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
    """Collapse Markdown wrapping while preserving canonical markers."""
    return re.sub(r"\s+", " ", text).strip()


def _assert_all_present(text: str, required: frozenset[str]) -> None:
    """Assert that every required policy marker is present."""
    missing = sorted(marker for marker in required if marker not in text)
    assert missing == [], f"Policy is missing required markers: {missing}"


def test_deprecation_policy_document_exists() -> None:
    """Step 8.6 must have one canonical deprecation policy source."""
    assert POLICY_PATH.is_file()


def test_deprecation_is_distinct_from_removal(policy_text: str) -> None:
    """Deprecation must preserve Stable behavior rather than remove it."""
    assert "Deprecation Lifecycle" in policy_text
    assert "Deprecation is not removal." in policy_text
    assert "Deprecated Stable (still functional)" in policy_text
    assert "Deprecated Stable behavior remains part of the v1 compatibility surface." in policy_text


def test_deprecated_stable_behavior_remains_functional_during_v1(
    policy_text: str,
) -> None:
    """Deprecated Stable behavior must remain available through the v1 line."""
    assert "preserve compatibility for the remainder of v1.x" in policy_text
    assert "Normal Stable removal is therefore not permitted in v1.0.x or v1.x." in policy_text


def test_normal_removal_is_no_earlier_than_next_major(policy_text: str) -> None:
    """Normal Stable removal must wait until a major-version boundary."""
    assert "Minimum Deprecation Window" in policy_text
    assert "remove or break no earlier than v2.0" in policy_text
    assert "target release is a major version" in policy_text


def test_deprecation_record_requires_canonical_identity_and_owner(
    policy_text: str,
) -> None:
    """Every Stable deprecation must carry a complete, reviewable record."""
    _assert_all_present(policy_text, REQUIRED_DEPRECATION_RECORD_FIELDS)


def test_deprecation_requires_replacement_or_explicit_no_replacement(
    policy_text: str,
) -> None:
    """A deprecation must identify a replacement or explicitly state none exists."""
    assert "Replacement:" in policy_text
    assert (
        "If no replacement exists, say so explicitly and explain the migration "
        "consequence." in policy_text
    )


def test_migration_guidance_is_mandatory_before_removal(
    policy_text: str,
) -> None:
    """A deprecated Stable contract cannot be removed without migration guidance."""
    assert "Migration Guidance" in policy_text
    assert (
        "Migration guidance is mandatory before a deprecated Stable contract is "
        "removed or incompatibly changed." in policy_text
    )
    _assert_all_present(policy_text, REQUIRED_MIGRATION_GUIDANCE_MARKERS)


def test_user_facing_migration_guidance_requires_bilingual_parity(
    policy_text: str,
) -> None:
    """User-facing migration instructions must preserve EN/zh-TW parity."""
    assert "User-facing migration guidance must preserve EN/zh-TW functional parity." in policy_text
    assert "docs/user-guide/en/" in policy_text
    assert "docs/user-guide/zh-TW/" in policy_text


def test_runtime_deprecation_warning_is_optional_but_governed(
    policy_text: str,
) -> None:
    """Runtime warnings are optional, but any warning must be well-behaved."""
    assert "Runtime warnings are not mandatory for every deprecation." in policy_text
    assert "deterministic, testable, actionable" in policy_text
    assert "not excessively noisy" in policy_text


def test_documentation_and_changelog_obligations_are_explicit(
    policy_text: str,
) -> None:
    """Deprecation must be documented where users and maintainers rely on it."""
    assert "Documentation and CHANGELOG Policy" in policy_text
    assert "CHANGELOG/release notes" in policy_text
    assert "English and zh-TW User Manuals" in policy_text
    assert "migration guidance" in policy_text


def test_changelog_has_explicit_deprecated_category(policy_text: str) -> None:
    """The CHANGELOG policy must expose a dedicated deprecation category."""
    assert "Deprecated Stable" in policy_text
    assert "Deprecated Stable behavior remains; migration advised" in policy_text


def test_emergency_compatibility_exception_requires_complete_record(
    policy_text: str,
) -> None:
    """Early breaking changes require a narrow, explicit emergency record."""
    assert "Emergency Compatibility Exception" in policy_text
    _assert_all_present(policy_text, REQUIRED_EMERGENCY_EXCEPTION_FIELDS)


def test_emergency_break_requires_compatibility_preservation_first(
    policy_text: str,
) -> None:
    """Emergency governance must prefer compatibility before a breaking fix."""
    assert "preserve compatibility" in policy_text
    assert "provide temporary bridge" in policy_text
    assert "documented emergency break" in policy_text


def test_convenience_is_not_a_valid_emergency_break_reason(
    policy_text: str,
) -> None:
    """Cleanup or refactoring preference must not justify an early break."""
    assert (
        "Convenience, cleanup, refactoring preference, or implementation "
        "simplification are insufficient reasons." in policy_text
    )


def test_deprecated_stable_behavior_remains_tested_until_legal_removal(
    policy_text: str,
) -> None:
    """Compatibility tests must remain until policy permits removal."""
    assert "Tests protecting compatibility:" in policy_text
    assert "Deprecated Stable behavior remains tested until legal removal." in (policy_text)


def test_removal_requires_major_version_review_artifacts(
    policy_text: str,
) -> None:
    """Normal removal must include documentation, tests, and review evidence."""
    required_markers = frozenset(
        {
            "deprecation was formally recorded",
            "migration guidance exists",
            "relevant documentation is updated",
            "CHANGELOG/release notes identify removal",
            "compatibility tests are intentionally updated/removed",
            "Code Review records an intentional breaking change",
        }
    )

    _assert_all_present(policy_text, required_markers)


def test_deprecation_policy_does_not_expand_non_stable_guarantees(
    policy_text: str,
) -> None:
    """Deprecation governance must apply Stable guarantees only where intended."""
    assert "Experimental capabilities do not receive the full Stable guarantee." in (policy_text)
    assert "Internal behavior may evolve during compatible v1 releases" in policy_text
    assert "Deferred capabilities are outside v1.0 scope" in policy_text


def test_deprecation_policy_preserves_later_milestone_ownership(
    policy_text: str,
) -> None:
    """Step 8.6 must not pre-empt support or release-automation work."""
    assert "does not create Step 8.7 support claims" in policy_text
    assert "does not pre-empt Step 8.8 release automation" in policy_text
