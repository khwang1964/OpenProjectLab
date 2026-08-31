from __future__ import annotations

import hashlib

from generator.release_automation import (
    VerificationReportComparator,
    VerificationReportComparisonRenderer,
    VerificationReportEncoder,
    VerificationReportFingerprinter,
)
from tests.test_release_automation_report_usability import _failed_report


def test_fingerprint_is_sha256_of_canonical_utf8_report() -> None:
    report = _failed_report()
    actual = VerificationReportFingerprinter.fingerprint(report)
    expected = hashlib.sha256(VerificationReportEncoder.encode(report).encode("utf-8")).hexdigest()
    assert actual.algorithm == "sha256"
    assert actual.digest == expected


def test_equal_reports_compare_without_differences() -> None:
    report = _failed_report()
    comparison = VerificationReportComparator.compare(report, report)
    assert comparison.is_equal
    assert comparison.differences == ()
    assert comparison.left_fingerprint == comparison.right_fingerprint


def test_comparison_rendering_is_deterministic() -> None:
    report = _failed_report()
    comparison = VerificationReportComparator.compare(report, report)
    assert VerificationReportComparisonRenderer.to_json(comparison) == (
        VerificationReportComparisonRenderer.to_json(comparison)
    )
