"""Cross-document contracts for v1 public, policy, and support claims."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RELEASES_DIR = REPO_ROOT / "docs" / "releases"
REFERENCE_DIR = REPO_ROOT / "docs" / "reference"

PUBLIC_AUDIT_PATH = RELEASES_DIR / "v1.0-public-contract-audit.md"
PUBLIC_ACCEPTANCE_PATH = RELEASES_DIR / "v1.0-public-contract-freeze-acceptance.md"
POLICY_PATH = RELEASES_DIR / "v1.0-compatibility-deprecation-policy.md"
POLICY_ACCEPTANCE_PATH = RELEASES_DIR / "v1.0-compatibility-deprecation-policy-acceptance.md"
SUPPORT_MATRIX_PATH = REFERENCE_DIR / "support-matrix.md"
LIMITATIONS_PATH = RELEASES_DIR / "v1.0-known-limitations.md"
SUPPORT_ACCEPTANCE_PATH = RELEASES_DIR / "v1.0-support-matrix-known-limitations-acceptance.md"
STEP_8_9_DESIGN_PATH = RELEASES_DIR / "v1.0-full-release-readiness-verification.md"

ACCEPTED_RECORDS = {
    "8.2": PUBLIC_ACCEPTANCE_PATH,
    "8.6": POLICY_ACCEPTANCE_PATH,
    "8.7": SUPPORT_ACCEPTANCE_PATH,
}

PUBLIC_CONTRACT_CLASSIFICATIONS = (
    "Stable",
    "Candidate",
    "Experimental",
    "Internal",
    "Deferred",
)


def _read(path: Path) -> str:
    """Read one required UTF-8 repository document."""
    assert path.is_file(), f"Required v1 consistency document is missing: {path}"
    return path.read_text(encoding="utf-8")


def _metadata_value(document: str, label: str) -> str:
    """Return a blockquote metadata value with optional Markdown hard break."""
    pattern = re.compile(
        rf"^>\s*\*\*{re.escape(label)}:\*\*\s*(?P<value>.+?)\\?\s*$",
        re.MULTILINE,
    )
    match = pattern.search(document)
    assert match is not None, f"Missing required metadata field: {label}"
    return match.group("value").strip()


def _assert_contains(document: str, markers: tuple[str, ...], owner: str) -> None:
    """Assert that one authority exposes every required contract marker."""
    normalized_document = re.sub(r"\s+", " ", document)
    missing = [
        marker for marker in markers if re.sub(r"\s+", " ", marker) not in normalized_document
    ]
    assert missing == [], f"{owner} is missing required markers: {missing}"


@pytest.mark.parametrize(
    "path",
    (
        PUBLIC_AUDIT_PATH,
        PUBLIC_ACCEPTANCE_PATH,
        POLICY_PATH,
        POLICY_ACCEPTANCE_PATH,
        SUPPORT_MATRIX_PATH,
        LIMITATIONS_PATH,
        SUPPORT_ACCEPTANCE_PATH,
        STEP_8_9_DESIGN_PATH,
    ),
)
def test_consistency_authorities_exist(path: Path) -> None:
    """Step 8.9.3 must use repository-owned authoritative documents."""
    assert path.is_file(), f"Required v1 consistency authority is missing: {path}"


@pytest.mark.parametrize(
    ("step", "path"),
    tuple(ACCEPTED_RECORDS.items()),
)
def test_public_policy_and_support_authorities_are_accepted(
    step: str,
    path: Path,
) -> None:
    """Step 8.9 must consume accepted Step 8.2, 8.6, and 8.7 records."""
    record = _read(path)

    assert _metadata_value(record, "Status") == "Accepted"
    assert _metadata_value(record, "Step").startswith(step)


def test_public_contract_audit_defines_complete_classification_vocabulary() -> None:
    """The frozen audit remains the source of public-surface classifications."""
    audit = _read(PUBLIC_AUDIT_PATH)

    _assert_contains(audit, PUBLIC_CONTRACT_CLASSIFICATIONS, "Step 8.2 audit")


def test_compatibility_policy_preserves_release_series_boundaries() -> None:
    """Patch, minor, and major release lanes must remain distinguishable."""
    policy = _read(POLICY_PATH)

    _assert_contains(policy, ("1.0.x", "1.x", "2.0"), "Step 8.6 policy")


def test_deprecated_stable_policy_requires_migration_and_emergency_rules() -> None:
    """Deprecated Stable behavior must retain its complete lifecycle contract."""
    policy = _read(POLICY_PATH)

    _assert_contains(
        policy,
        ("Deprecated Stable", "migration", "emergency", "major version"),
        "Step 8.6 policy",
    )


def test_policy_preserves_nonstable_classification_boundaries() -> None:
    """Non-Stable surfaces must not become Stable through release wording."""
    policy = _read(POLICY_PATH)

    _assert_contains(
        policy,
        ("Stable", "Experimental", "Internal", "Deferred"),
        "Step 8.6 policy",
    )


def test_support_matrix_records_only_evidence_backed_supported_environments() -> None:
    """Supported environment claims must retain their exact evidence labels."""
    support_matrix = _read(SUPPORT_MATRIX_PATH)

    _assert_contains(
        support_matrix,
        (
            "Supported",
            "ubuntu-latest",
            "Python 3.14",
            "Windows",
            "Python 3.14.5",
        ),
        "Step 8.7 support matrix",
    )


def test_support_matrix_distinguishes_unverified_environment_claims() -> None:
    """The support contract must preserve non-Supported classifications."""
    support_matrix = _read(SUPPORT_MATRIX_PATH)

    _assert_contains(
        support_matrix,
        ("Supported", "Experimental"),
        "Step 8.7 support matrix",
    )


def test_known_limitations_preserve_experimental_and_deferred_scope() -> None:
    """Known limitations must keep non-blocking scope visible to users."""
    limitations = _read(LIMITATIONS_PATH)

    _assert_contains(
        limitations,
        ("Known Limitation", "Experimental", "Deferred"),
        "Step 8.7 known limitations",
    )


def test_known_limitations_keep_marketplace_and_ai_deferrals_visible() -> None:
    """Previously deferred Marketplace and AI expansion remains outside v1.0."""
    limitations = _read(LIMITATIONS_PATH)

    _assert_contains(
        limitations,
        ("Marketplace", "AI", "Deferred"),
        "Step 8.7 known limitations",
    )


def test_step_8_9_preserves_prior_authority_ownership() -> None:
    """Full-readiness verification must not redefine earlier authorities."""
    design = _read(STEP_8_9_DESIGN_PATH)

    _assert_contains(
        design,
        (
            "Step 8.2 remains authoritative",
            "Step 8.6 remains authoritative",
            "Step 8.7 remains authoritative",
        ),
        "Step 8.9 governing design",
    )


def test_step_8_9_does_not_expand_support_or_stability_claims() -> None:
    """A successful release build must not widen accepted public claims."""
    design = _read(STEP_8_9_DESIGN_PATH)

    _assert_contains(
        design,
        (
            "does not automatically expand support",
            "Public-contract drift blocks Step 8.9 acceptance",
            "Experimental and Internal behavior is not accidentally presented as Stable",
        ),
        "Step 8.9 governing design",
    )


def test_step_8_9_keeps_rc_acceptance_out_of_scope() -> None:
    """Consistency automation must not pre-approve Step 8.10."""
    design = _read(STEP_8_9_DESIGN_PATH)

    _assert_contains(
        design,
        ("Step 8.10 remains the owner", "does not itself accept or"),
        "Step 8.9 governing design",
    )
