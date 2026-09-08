"""Deterministic readiness decision record for human release review."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum

from generator.readiness_comparison import (
    ReadinessComparisonCategory,
    ReleaseReadinessSnapshotComparator,
)
from generator.release_readiness import (
    ReleaseReadinessStabilityEvaluator,
    ReleaseReadinessStabilityPolicy,
    ReleaseReadinessStabilitySnapshot,
    StabilityOutcome,
)


class ReadinessDecisionDisposition(StrEnum):
    REVIEWABLE = "REVIEWABLE"
    BLOCKED = "BLOCKED"
    INDETERMINATE = "INDETERMINATE"


@dataclass(frozen=True, slots=True, order=True)
class ReadinessDecisionFinding:
    source: str
    path: str
    reason: str
    category: str
    message: str


@dataclass(frozen=True, slots=True)
class ReadinessDecisionRecord:
    repository: str
    candidate_revision: str
    policy_revision: str
    baseline_revision: str | None
    evaluation_outcome: StabilityOutcome
    comparison_category: ReadinessComparisonCategory | None
    disposition: ReadinessDecisionDisposition
    findings: tuple[ReadinessDecisionFinding, ...]


class ReleaseReadinessDecisionBuilder:
    @staticmethod
    def build(
        snapshot: ReleaseReadinessStabilitySnapshot,
        policy: ReleaseReadinessStabilityPolicy,
        baseline: ReleaseReadinessStabilitySnapshot | None = None,
    ) -> ReadinessDecisionRecord:
        evaluation = ReleaseReadinessStabilityEvaluator.evaluate(snapshot, policy)
        comparison = (
            ReleaseReadinessSnapshotComparator.compare(baseline, snapshot)
            if baseline is not None
            else None
        )
        findings = [
            ReadinessDecisionFinding(
                "evaluation", finding.path, finding.reason, evaluation.outcome, finding.message
            )
            for finding in evaluation.findings
        ]
        if comparison is not None:
            findings.extend(
                ReadinessDecisionFinding(
                    "comparison",
                    finding.path,
                    finding.reason,
                    finding.category,
                    f"before={finding.before!r}; after={finding.after!r}",
                )
                for finding in comparison.findings
                if finding.category != ReadinessComparisonCategory.UNCHANGED
            )

        disposition = ReadinessDecisionDisposition.REVIEWABLE
        if evaluation.outcome == StabilityOutcome.BLOCKED or (
            comparison is not None and comparison.category == ReadinessComparisonCategory.REGRESSED
        ):
            disposition = ReadinessDecisionDisposition.BLOCKED
        if evaluation.outcome == StabilityOutcome.INDETERMINATE or (
            comparison is not None
            and comparison.category == ReadinessComparisonCategory.INCOMPARABLE
        ):
            disposition = ReadinessDecisionDisposition.INDETERMINATE

        return ReadinessDecisionRecord(
            repository=snapshot.repository,
            candidate_revision=snapshot.revision,
            policy_revision=policy.revision,
            baseline_revision=baseline.revision if baseline is not None else None,
            evaluation_outcome=evaluation.outcome,
            comparison_category=comparison.category if comparison is not None else None,
            disposition=disposition,
            findings=tuple(sorted(findings)),
        )


class ReadinessDecisionRenderer:
    @staticmethod
    def to_json(record: ReadinessDecisionRecord) -> str:
        return (
            json.dumps(
                {
                    "baseline_revision": record.baseline_revision,
                    "candidate_revision": record.candidate_revision,
                    "comparison_category": record.comparison_category,
                    "disposition": record.disposition,
                    "evaluation_outcome": record.evaluation_outcome,
                    "findings": [
                        {
                            "category": finding.category,
                            "message": finding.message,
                            "path": finding.path,
                            "reason": finding.reason,
                            "source": finding.source,
                        }
                        for finding in record.findings
                    ],
                    "policy_revision": record.policy_revision,
                    "repository": record.repository,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        )

    @staticmethod
    def to_text(record: ReadinessDecisionRecord) -> str:
        baseline = record.baseline_revision if record.baseline_revision is not None else "none"
        comparison = (
            record.comparison_category if record.comparison_category is not None else "none"
        )
        lines = [
            f"disposition: {record.disposition}",
            f"repository: {record.repository}",
            f"candidate_revision: {record.candidate_revision}",
            f"policy_revision: {record.policy_revision}",
            f"baseline_revision: {baseline}",
            f"evaluation_outcome: {record.evaluation_outcome}",
            f"comparison_category: {comparison}",
        ]
        lines.extend(
            f"{item.source}:{item.path}: {item.category}: {item.reason}: {item.message}"
            for item in record.findings
        )
        return "\n".join(lines) + "\n"
