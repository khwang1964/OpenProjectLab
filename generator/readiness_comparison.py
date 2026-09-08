"""Deterministic comparison of canonical release-readiness snapshots."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from generator.release_readiness import ReleaseReadinessStabilitySnapshot


class ReadinessComparisonCategory(StrEnum):
    UNCHANGED = "UNCHANGED"
    IMPROVED = "IMPROVED"
    REGRESSED = "REGRESSED"
    INCOMPARABLE = "INCOMPARABLE"


@dataclass(frozen=True, slots=True)
class ReadinessComparisonFinding:
    path: str
    category: ReadinessComparisonCategory
    reason: str
    before: Any
    after: Any


@dataclass(frozen=True, slots=True)
class ReadinessSnapshotComparison:
    baseline_repository: str
    baseline_revision: str
    candidate_repository: str
    candidate_revision: str
    category: ReadinessComparisonCategory
    findings: tuple[ReadinessComparisonFinding, ...]


def _scalar_category(before: int | float | bool, after: int | float | bool, higher: bool):
    if before == after:
        return ReadinessComparisonCategory.UNCHANGED
    improved = after > before if higher else after < before
    return (
        ReadinessComparisonCategory.IMPROVED if improved else ReadinessComparisonCategory.REGRESSED
    )


class ReleaseReadinessSnapshotComparator:
    @staticmethod
    def compare(
        baseline: ReleaseReadinessStabilitySnapshot,
        candidate: ReleaseReadinessStabilitySnapshot,
    ) -> ReadinessSnapshotComparison:
        if baseline.repository != candidate.repository:
            finding = ReadinessComparisonFinding(
                "$.repository",
                ReadinessComparisonCategory.INCOMPARABLE,
                "REPOSITORY_MISMATCH",
                baseline.repository,
                candidate.repository,
            )
            return ReadinessSnapshotComparison(
                baseline.repository,
                baseline.revision,
                candidate.repository,
                candidate.revision,
                ReadinessComparisonCategory.INCOMPARABLE,
                (finding,),
            )

        findings: list[ReadinessComparisonFinding] = []

        def scalar(
            path: str,
            reason: str,
            before: int | float | bool,
            after: int | float | bool,
            *,
            higher: bool,
        ) -> None:
            findings.append(
                ReadinessComparisonFinding(
                    path,
                    _scalar_category(before, after, higher),
                    reason,
                    before,
                    after,
                )
            )

        scalar(
            "$.required_checks_passed",
            "REQUIRED_CHECKS_CHANGED",
            baseline.required_checks_passed,
            candidate.required_checks_passed,
            higher=True,
        )
        scalar(
            "$.focused_passed",
            "FOCUSED_PASSED_CHANGED",
            baseline.focused_passed,
            candidate.focused_passed,
            higher=True,
        )
        scalar(
            "$.focused_failed",
            "FOCUSED_FAILED_CHANGED",
            baseline.focused_failed,
            candidate.focused_failed,
            higher=False,
        )
        scalar(
            "$.regression_passed",
            "REGRESSION_PASSED_CHANGED",
            baseline.regression_passed,
            candidate.regression_passed,
            higher=True,
        )
        scalar(
            "$.regression_failed",
            "REGRESSION_FAILED_CHANGED",
            baseline.regression_failed,
            candidate.regression_failed,
            higher=False,
        )
        scalar(
            "$.coverage_percent",
            "COVERAGE_CHANGED",
            baseline.coverage_percent,
            candidate.coverage_percent,
            higher=True,
        )
        scalar(
            "$.coverage_threshold",
            "COVERAGE_THRESHOLD_CHANGED",
            baseline.coverage_threshold,
            candidate.coverage_threshold,
            higher=True,
        )
        scalar(
            "$.audit_chain_accepted",
            "AUDIT_CHAIN_CHANGED",
            baseline.audit_chain_accepted,
            candidate.audit_chain_accepted,
            higher=True,
        )
        ReleaseReadinessSnapshotComparator._set_findings(
            findings,
            "$.supported_surfaces",
            baseline.supported_surfaces,
            candidate.supported_surfaces,
            additions_improve=True,
        )
        ReleaseReadinessSnapshotComparator._set_findings(
            findings,
            "$.known_limitations",
            baseline.known_limitations,
            candidate.known_limitations,
            additions_improve=False,
        )
        ReleaseReadinessSnapshotComparator._set_findings(
            findings,
            "$.release_blockers",
            baseline.release_blockers,
            candidate.release_blockers,
            additions_improve=False,
        )
        ordered = tuple(sorted(findings, key=lambda item: (item.path, item.reason)))
        categories = {finding.category for finding in ordered}
        category = ReadinessComparisonCategory.UNCHANGED
        if ReadinessComparisonCategory.REGRESSED in categories:
            category = ReadinessComparisonCategory.REGRESSED
        elif ReadinessComparisonCategory.IMPROVED in categories:
            category = ReadinessComparisonCategory.IMPROVED
        return ReadinessSnapshotComparison(
            baseline.repository,
            baseline.revision,
            candidate.repository,
            candidate.revision,
            category,
            ordered,
        )

    @staticmethod
    def _set_findings(
        findings: list[ReadinessComparisonFinding],
        path: str,
        baseline: tuple[str, ...],
        candidate: tuple[str, ...],
        *,
        additions_improve: bool,
    ) -> None:
        removed = tuple(sorted(set(baseline) - set(candidate)))
        added = tuple(sorted(set(candidate) - set(baseline)))
        if not removed and not added:
            findings.append(
                ReadinessComparisonFinding(
                    path,
                    ReadinessComparisonCategory.UNCHANGED,
                    "SET_UNCHANGED",
                    baseline,
                    candidate,
                )
            )
            return
        if removed:
            category = (
                ReadinessComparisonCategory.REGRESSED
                if additions_improve
                else ReadinessComparisonCategory.IMPROVED
            )
            findings.append(
                ReadinessComparisonFinding(path, category, "ITEMS_REMOVED", removed, ())
            )
        if added:
            category = (
                ReadinessComparisonCategory.IMPROVED
                if additions_improve
                else ReadinessComparisonCategory.REGRESSED
            )
            findings.append(ReadinessComparisonFinding(path, category, "ITEMS_ADDED", (), added))


class ReadinessComparisonRenderer:
    @staticmethod
    def to_json(comparison: ReadinessSnapshotComparison) -> str:
        return (
            json.dumps(
                {
                    "baseline": {
                        "repository": comparison.baseline_repository,
                        "revision": comparison.baseline_revision,
                    },
                    "candidate": {
                        "repository": comparison.candidate_repository,
                        "revision": comparison.candidate_revision,
                    },
                    "category": comparison.category,
                    "findings": [
                        {
                            "after": finding.after,
                            "before": finding.before,
                            "category": finding.category,
                            "path": finding.path,
                            "reason": finding.reason,
                        }
                        for finding in comparison.findings
                    ],
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        )

    @staticmethod
    def to_text(comparison: ReadinessSnapshotComparison) -> str:
        lines = [
            f"category: {comparison.category}",
            f"baseline: {comparison.baseline_repository}@{comparison.baseline_revision}",
            f"candidate: {comparison.candidate_repository}@{comparison.candidate_revision}",
        ]
        lines.extend(
            f"{finding.path}: {finding.category}: {finding.reason}: "
            f"{finding.before!r} -> {finding.after!r}"
            for finding in comparison.findings
        )
        return "\n".join(lines) + "\n"
