import json
from argparse import Namespace
from pathlib import Path

import pytest

from generator.cli.release_evidence import _handle_readiness_decide
from generator.readiness_decision import (
    ReadinessDecisionDisposition,
    ReadinessDecisionRenderer,
    ReleaseReadinessDecisionBuilder,
)
from generator.release_readiness import (
    ReleaseReadinessStabilityPolicyCodec,
    ReleaseReadinessStabilitySnapshotCodec,
)

REVISION = "b" * 40
BASELINE_REVISION = "a" * 40
REPOSITORY = "khwang1964/OpenProjectLab"
SURFACES = ["audit-bundle", "cli", "release-evidence", "sdk"]
ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / (
    "docs/releases/v1.4.3-deterministic-readiness-decision-record-implementation.md"
)


def snapshot(*, revision: str = REVISION, **changes: object) -> str:
    value = {
        "audit_chain_accepted": True,
        "collected_at": "2026-09-08T00:00:00Z",
        "coverage_percent": 90.0,
        "coverage_threshold": 67.0,
        "focused_failed": 0,
        "focused_passed": 20,
        "known_limitations": [],
        "observed_revision": revision,
        "regression_failed": 0,
        "regression_passed": 2800,
        "release_blockers": [],
        "repository": REPOSITORY,
        "required_checks_passed": True,
        "revision": revision,
        "supported_surfaces": SURFACES,
    }
    value.update(changes)
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def policy(**changes: object) -> str:
    value = {"repository": REPOSITORY, "required_surfaces": SURFACES, "revision": REVISION}
    value.update(changes)
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def build(*, snapshot_document: str = "", policy_document: str = "", baseline: str | None = None):
    return ReleaseReadinessDecisionBuilder.build(
        ReleaseReadinessStabilitySnapshotCodec.decode(snapshot_document or snapshot()),
        ReleaseReadinessStabilityPolicyCodec.decode(policy_document or policy()),
        ReleaseReadinessStabilitySnapshotCodec.decode(baseline) if baseline is not None else None,
    )


def write_documents(tmp_path: Path, candidate: str, rule: str, baseline: str | None = None):
    snapshot_path = tmp_path / "snapshot.json"
    policy_path = tmp_path / "policy.json"
    snapshot_path.write_text(candidate, encoding="utf-8")
    policy_path.write_text(rule, encoding="utf-8")
    baseline_path = None
    if baseline is not None:
        baseline_path = tmp_path / "baseline.json"
        baseline_path.write_text(baseline, encoding="utf-8")
    return snapshot_path, policy_path, baseline_path


def test_ready_without_baseline_is_reviewable_and_absence_is_explicit() -> None:
    record = build()
    assert record.disposition == ReadinessDecisionDisposition.REVIEWABLE
    assert record.baseline_revision is None
    assert record.comparison_category is None
    document = json.loads(ReadinessDecisionRenderer.to_json(record))
    assert document["baseline_revision"] is None
    assert document["comparison_category"] is None


@pytest.mark.parametrize("category_change", ({}, {"coverage_percent": 89.0}))
def test_non_regressed_baseline_is_reviewable(category_change: dict[str, object]) -> None:
    record = build(baseline=snapshot(revision=BASELINE_REVISION, **category_change))
    assert record.disposition == ReadinessDecisionDisposition.REVIEWABLE


@pytest.mark.parametrize(
    "changes",
    (
        {"required_checks_passed": False},
        {"regression_failed": 1},
        {"release_blockers": ["unresolved"]},
    ),
)
def test_blocked_evaluation_is_blocked(changes: dict[str, object]) -> None:
    assert build(snapshot_document=snapshot(**changes)).disposition == (
        ReadinessDecisionDisposition.BLOCKED
    )


def test_regressed_baseline_is_blocked() -> None:
    record = build(baseline=snapshot(revision=BASELINE_REVISION, coverage_percent=95.0))
    assert record.disposition == ReadinessDecisionDisposition.BLOCKED
    assert any(item.source == "comparison" for item in record.findings)


@pytest.mark.parametrize(
    ("policy_document", "baseline"),
    (
        (policy(repository="other/repository"), None),
        (policy(), snapshot(revision=BASELINE_REVISION, repository="other/repository")),
    ),
)
def test_mismatched_evidence_is_indeterminate(policy_document: str, baseline: str | None) -> None:
    assert build(policy_document=policy_document, baseline=baseline).disposition == (
        ReadinessDecisionDisposition.INDETERMINATE
    )


def test_findings_and_renderers_are_deterministic() -> None:
    arguments = {
        "snapshot_document": snapshot(required_checks_passed=False, release_blockers=["z"]),
        "baseline": snapshot(revision=BASELINE_REVISION, coverage_percent=95.0),
    }
    first = build(**arguments)
    second = build(**arguments)
    assert first.findings == tuple(sorted(first.findings))
    assert ReadinessDecisionRenderer.to_json(first) == ReadinessDecisionRenderer.to_json(second)
    assert ReadinessDecisionRenderer.to_text(first) == ReadinessDecisionRenderer.to_text(second)


@pytest.mark.parametrize(
    ("candidate", "rule", "baseline", "expected_exit"),
    (
        (snapshot(), policy(), None, 0),
        (snapshot(required_checks_passed=False), policy(), None, 1),
        (snapshot(), policy(repository="other/repository"), None, 2),
        ("{}", policy(), None, 2),
    ),
)
def test_cli_exit_contract(
    tmp_path: Path, candidate: str, rule: str, baseline: str | None, expected_exit: int
) -> None:
    snapshot_path, policy_path, baseline_path = write_documents(tmp_path, candidate, rule, baseline)
    args = Namespace(
        snapshot=str(snapshot_path),
        policy=str(policy_path),
        baseline=str(baseline_path) if baseline_path else None,
        format="json",
    )
    assert _handle_readiness_decide(args) == expected_exit


def test_cli_parser_accepts_only_explicit_local_inputs() -> None:
    from generator.cli.main import build_parser

    args = build_parser().parse_args(
        [
            "release-evidence",
            "readiness",
            "decide",
            "--snapshot",
            "snapshot.json",
            "--policy",
            "policy.json",
            "--format",
            "text",
        ]
    )
    assert args.baseline is None
    assert callable(args.command_handler)


def test_cli_rejects_document_over_predecode_limit(tmp_path: Path, capsys) -> None:
    snapshot_path, policy_path, _ = write_documents(tmp_path, snapshot(), policy())
    snapshot_path.write_bytes(b" " * (1024 * 1024 + 1))
    args = Namespace(
        snapshot=str(snapshot_path), policy=str(policy_path), baseline=None, format="json"
    )
    assert _handle_readiness_decide(args) == 2
    assert "1 MiB limit" in capsys.readouterr().err


def test_implementation_record_preserves_pending_acceptance_and_finish_line() -> None:
    text = " ".join(IMPLEMENTATION.read_text(encoding="utf-8").split())
    for fragment in (
        "Implemented / Pending post-merge verification",
        "Implementation acceptance — Pending post-merge verification",
        "does not discover inputs",
        "infer Git ancestry",
        "authorize a release",
        "network or credentials",
        "finish-line review",
    ):
        assert fragment in text


def test_governance_surfaces_have_exact_implementation_markers() -> None:
    base = "v1.4.3-deterministic-readiness-decision-record-implementation"
    for relative, suffix in (
        ("CHANGELOG.md", "changelog"),
        ("docs/HISTORY.md", "history"),
        ("docs/roadmap.md", "roadmap"),
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        marker = f"<!-- {base}-{suffix} -->"
        assert text.count(marker) == 1
        block = text.split(marker, 1)[1]
        assert "Implementation acceptance — Pending post-merge verification" in block
