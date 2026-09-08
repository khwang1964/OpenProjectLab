import json
from argparse import Namespace
from pathlib import Path

import pytest

from generator.cli.release_evidence import _handle_readiness_compare
from generator.readiness_comparison import (
    ReadinessComparisonCategory,
    ReadinessComparisonRenderer,
    ReleaseReadinessSnapshotComparator,
)
from generator.release_readiness import ReleaseReadinessStabilitySnapshotCodec

BASELINE_REVISION = "a" * 40
CANDIDATE_REVISION = "b" * 40
SURFACES = ["audit-bundle", "cli", "release-evidence", "sdk"]
ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / (
    "docs/releases/v1.4.2-deterministic-readiness-snapshot-comparison-implementation.md"
)


def snapshot(*, revision: str = BASELINE_REVISION, **changes: object) -> str:
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
        "repository": "khwang1964/OpenProjectLab",
        "required_checks_passed": True,
        "revision": revision,
        "supported_surfaces": SURFACES,
    }
    value.update(changes)
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def compare(candidate_document: str = ""):
    return ReleaseReadinessSnapshotComparator.compare(
        ReleaseReadinessStabilitySnapshotCodec.decode(snapshot()),
        ReleaseReadinessStabilitySnapshotCodec.decode(
            candidate_document or snapshot(revision=CANDIDATE_REVISION)
        ),
    )


def write_documents(tmp_path: Path, candidate_document: str) -> tuple[Path, Path]:
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    baseline.write_text(snapshot(), encoding="utf-8")
    candidate.write_text(candidate_document, encoding="utf-8")
    return baseline, candidate


def test_unchanged_gate_evidence_is_deterministic_across_revisions() -> None:
    result = compare()
    assert result.category == ReadinessComparisonCategory.UNCHANGED
    assert result.baseline_revision == BASELINE_REVISION
    assert result.candidate_revision == CANDIDATE_REVISION
    assert [item.path for item in result.findings] == sorted(item.path for item in result.findings)
    assert ReadinessComparisonRenderer.to_json(result) == ReadinessComparisonRenderer.to_json(
        compare()
    )


def test_improvements_are_reported_without_claiming_ancestry() -> None:
    result = compare(
        snapshot(
            revision=CANDIDATE_REVISION,
            coverage_percent=91.0,
            focused_passed=21,
            supported_surfaces=[*SURFACES, "website"],
        )
    )
    assert result.category == ReadinessComparisonCategory.IMPROVED
    assert {item.category for item in result.findings} >= {
        ReadinessComparisonCategory.IMPROVED,
        ReadinessComparisonCategory.UNCHANGED,
    }


@pytest.mark.parametrize(
    ("changes", "path"),
    (
        ({"required_checks_passed": False}, "$.required_checks_passed"),
        ({"focused_failed": 1}, "$.focused_failed"),
        ({"regression_passed": 2799}, "$.regression_passed"),
        ({"coverage_percent": 66.0}, "$.coverage_percent"),
        ({"audit_chain_accepted": False}, "$.audit_chain_accepted"),
        ({"supported_surfaces": SURFACES[:-1]}, "$.supported_surfaces"),
        ({"known_limitations": ["windows-only"]}, "$.known_limitations"),
        ({"release_blockers": ["unresolved"]}, "$.release_blockers"),
    ),
)
def test_every_readiness_gate_regression_fails_closed(
    changes: dict[str, object], path: str
) -> None:
    result = compare(snapshot(revision=CANDIDATE_REVISION, **changes))
    assert result.category == ReadinessComparisonCategory.REGRESSED
    assert any(item.path == path for item in result.findings)


def test_repository_mismatch_is_incomparable_without_improvement_findings() -> None:
    result = compare(
        snapshot(
            revision=CANDIDATE_REVISION,
            repository="different/repository",
            focused_passed=999,
        )
    )
    assert result.category == ReadinessComparisonCategory.INCOMPARABLE
    assert len(result.findings) == 1
    assert result.findings[0].reason == "REPOSITORY_MISMATCH"


@pytest.mark.parametrize(
    ("candidate_document", "expected_exit"),
    (
        (snapshot(revision=CANDIDATE_REVISION), 0),
        (snapshot(revision=CANDIDATE_REVISION, regression_failed=1), 1),
        (snapshot(revision=CANDIDATE_REVISION, repository="other/repo"), 2),
        ("{}", 2),
    ),
)
def test_cli_exit_contract(tmp_path: Path, candidate_document: str, expected_exit: int) -> None:
    baseline, candidate = write_documents(tmp_path, candidate_document)
    args = Namespace(
        baseline=str(baseline),
        candidate=str(candidate),
        format="json",
    )
    assert _handle_readiness_compare(args) == expected_exit


def test_cli_parser_requires_explicit_local_inputs() -> None:
    from generator.cli.main import build_parser

    args = build_parser().parse_args(
        [
            "release-evidence",
            "readiness",
            "compare",
            "--baseline",
            "baseline.json",
            "--candidate",
            "candidate.json",
            "--format",
            "text",
        ]
    )
    assert args.baseline == "baseline.json"
    assert args.candidate == "candidate.json"
    assert callable(args.command_handler)


def test_cli_rejects_document_over_predecode_limit(tmp_path: Path, capsys) -> None:
    baseline, candidate = write_documents(tmp_path, snapshot(revision=CANDIDATE_REVISION))
    baseline.write_bytes(b" " * (1024 * 1024 + 1))
    args = Namespace(baseline=str(baseline), candidate=str(candidate), format="json")
    assert _handle_readiness_compare(args) == 2
    assert "1 MiB limit" in capsys.readouterr().err


def test_implementation_record_preserves_pending_acceptance_boundary() -> None:
    text = IMPLEMENTATION.read_text(encoding="utf-8")
    assert "Implemented / Pending post-merge verification" in text
    assert "Production implementation — Implemented" in text
    assert "Implementation acceptance — Pending post-merge verification" in text
    for fragment in (
        "does not discover inputs",
        "infer Git ancestry",
        "authorize a release",
        "network or credentials",
        "publication state",
    ):
        assert fragment in " ".join(text.split())


def test_governance_surfaces_have_exact_implementation_markers() -> None:
    base = "v1.4.2-deterministic-readiness-snapshot-comparison-implementation"
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
