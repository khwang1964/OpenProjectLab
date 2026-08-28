from dataclasses import FrozenInstanceError

import pytest

from generator.release_automation import (
    CheckConclusion,
    CheckEvidence,
    FindingCode,
    ReleaseEvidence,
    ReleaseEvidenceValidator,
)
from generator.release_automation import (
    TestEvidence as ReleaseTestEvidence,
)

SHA = "a" * 40


def valid_evidence() -> ReleaseEvidence:
    return ReleaseEvidence(
        repository="khwang1964/OpenProjectLab",
        branch="main",
        candidate_sha=SHA,
        checks=(CheckEvidence("quality", CheckConclusion.PASSED),),
        focused_tests=ReleaseTestEvidence(passed=6),
    )


def test_evidence_is_immutable_and_checks_are_deterministic() -> None:
    evidence = ReleaseEvidence(
        repository="khwang1964/OpenProjectLab",
        branch="main",
        candidate_sha=SHA,
        checks=(
            CheckEvidence("z", CheckConclusion.PASSED),
            CheckEvidence("a", CheckConclusion.PASSED),
        ),
        focused_tests=ReleaseTestEvidence(passed=6),
    )
    assert tuple(check.name for check in evidence.checks) == ("a", "z")
    with pytest.raises(FrozenInstanceError):
        evidence.branch = "other"  # type: ignore[misc]


def test_valid_evidence_passes() -> None:
    result = ReleaseEvidenceValidator().validate(
        valid_evidence(),
        expected_repository="khwang1964/OpenProjectLab",
        expected_branch="main",
        expected_sha=SHA,
    )
    assert result.is_valid
    assert result.findings == ()


def test_missing_or_failed_evidence_fails_closed_in_stable_order() -> None:
    evidence = ReleaseEvidence(
        repository="wrong/repository",
        branch="feature",
        candidate_sha="b" * 40,
        checks=(),
    )
    result = ReleaseEvidenceValidator().validate(
        evidence,
        expected_repository="khwang1964/OpenProjectLab",
        expected_branch="main",
        expected_sha=SHA,
    )
    assert not result.is_valid
    assert tuple(finding.code for finding in result.findings) == (
        FindingCode.REPOSITORY_MISMATCH,
        FindingCode.BRANCH_MISMATCH,
        FindingCode.SHA_MISMATCH,
        FindingCode.MISSING_CHECKS,
        FindingCode.FOCUSED_TESTS_NOT_PASSED,
    )


def test_pending_ci_and_failed_focused_tests_fail_closed() -> None:
    evidence = ReleaseEvidence(
        repository="khwang1964/OpenProjectLab",
        branch="main",
        candidate_sha=SHA,
        checks=(CheckEvidence("quality", CheckConclusion.PENDING),),
        focused_tests=ReleaseTestEvidence(passed=5, failed=1),
    )
    result = ReleaseEvidenceValidator().validate(
        evidence,
        expected_repository="khwang1964/OpenProjectLab",
        expected_branch="main",
        expected_sha=SHA,
    )
    assert tuple(finding.code for finding in result.findings) == (
        FindingCode.CI_NOT_PASSED,
        FindingCode.FOCUSED_TESTS_NOT_PASSED,
    )
