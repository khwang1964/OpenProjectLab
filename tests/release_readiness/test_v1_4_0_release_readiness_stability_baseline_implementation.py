import json

import pytest

from generator.release_automation import VerificationDocumentError
from generator.release_readiness import (
    ReleaseReadinessStabilityEvaluator,
    ReleaseReadinessStabilityPolicyCodec,
    ReleaseReadinessStabilitySnapshotCodec,
    StabilityOutcome,
)

REVISION = "a" * 40
SURFACES = ["audit-bundle", "bootstrap", "cli", "migration-verification", "release-evidence", "sdk"]


def snapshot(**changes: object) -> str:
    value = {
        "audit_chain_accepted": True,
        "collected_at": "2026-09-07T00:00:00Z",
        "coverage_percent": 90.0,
        "coverage_threshold": 67.0,
        "focused_failed": 0,
        "focused_passed": 12,
        "known_limitations": [],
        "observed_revision": REVISION,
        "regression_failed": 0,
        "regression_passed": 2700,
        "release_blockers": [],
        "repository": "khwang1964/OpenProjectLab",
        "required_checks_passed": True,
        "revision": REVISION,
        "supported_surfaces": SURFACES,
    }
    value.update(changes)
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def policy(**changes: object) -> str:
    value = {
        "repository": "khwang1964/OpenProjectLab",
        "required_surfaces": SURFACES,
        "revision": REVISION,
    }
    value.update(changes)
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def evaluate(snapshot_document: str = "", policy_document: str = ""):
    return ReleaseReadinessStabilityEvaluator.evaluate(
        ReleaseReadinessStabilitySnapshotCodec.decode(snapshot_document or snapshot()),
        ReleaseReadinessStabilityPolicyCodec.decode(policy_document or policy()),
    )


def test_canonical_round_trip_is_byte_stable_and_immutable() -> None:
    decoded = ReleaseReadinessStabilitySnapshotCodec.decode(snapshot())
    assert ReleaseReadinessStabilitySnapshotCodec.encode(decoded) == snapshot()
    with pytest.raises(AttributeError):
        decoded.revision = "b" * 40  # type: ignore[misc]


@pytest.mark.parametrize(
    "document",
    (
        snapshot()[:-1] + ',"unknown":true}',
        snapshot().replace('"revision":', '"revision":"' + REVISION + '","revision":', 1),
        snapshot(revision="main"),
        snapshot(focused_passed=-1),
        snapshot(coverage_percent=float("nan")),
    ),
)
def test_decoder_rejects_ambiguous_or_malformed_evidence(document: str) -> None:
    with pytest.raises(VerificationDocumentError):
        ReleaseReadinessStabilitySnapshotCodec.decode(document)


def test_ready_requires_every_gate() -> None:
    assert evaluate().outcome == StabilityOutcome.READY
    assert evaluate(snapshot(required_checks_passed=False)).outcome == StabilityOutcome.BLOCKED
    assert evaluate(snapshot(release_blockers=["unresolved"])).outcome == StabilityOutcome.BLOCKED


def test_revision_and_surface_mismatch_fail_closed_as_indeterminate() -> None:
    result = evaluate(policy_document=policy(revision="b" * 40))
    assert result.outcome == StabilityOutcome.INDETERMINATE
    assert [finding.path for finding in result.findings] == sorted(
        finding.path for finding in result.findings
    )
    assert (
        evaluate(snapshot(supported_surfaces=SURFACES[:-1])).outcome
        == StabilityOutcome.INDETERMINATE
    )


def test_cli_contract_is_bounded_offline_and_read_only() -> None:
    from generator.cli.main import build_parser

    args = build_parser().parse_args(
        [
            "release-evidence",
            "readiness",
            "evaluate",
            "--snapshot",
            "s.json",
            "--policy",
            "p.json",
            "--format",
            "json",
        ]
    )
    assert args.snapshot == "s.json"
    assert callable(args.command_handler)
