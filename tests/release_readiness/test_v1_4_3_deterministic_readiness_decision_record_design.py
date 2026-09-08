from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs/architecture/deterministic-readiness-decision-record.md"
RELEASE = ROOT / "docs/releases/v1.4.3-deterministic-readiness-decision-record-design.md"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_design_is_pending_and_implementation_not_started() -> None:
    assert "Proposed / Pending design review" in normalized(ARCH)
    assert "Proposed / Pending design review" in normalized(RELEASE)
    assert "Production implementation is Not Started" in normalized(RELEASE)


def test_dispositions_are_deterministic_and_fail_closed() -> None:
    text = normalized(ARCH)
    for phrase in (
        "REVIEWABLE",
        "BLOCKED",
        "INDETERMINATE",
        "stable source, path, reason code, category",
        "deterministic ordering",
        "incomparable evidence",
    ):
        assert phrase in text


def test_accepted_v1_4_contracts_are_composed_without_redefinition() -> None:
    text = normalized(RELEASE)
    for phrase in (
        "v1.4.0 readiness evaluation",
        "v1.4.1 canonical snapshot assembly",
        "v1.4.2 snapshot comparison",
        "without changing their schemas, outcomes, or authority boundaries",
    ):
        assert phrase in text


def test_cli_is_bounded_offline_and_read_only() -> None:
    text = normalized(ARCH)
    assert "readiness decide --snapshot SNAPSHOT --policy POLICY --baseline BASELINE" in text
    assert "--format json|text" in text
    assert "--baseline" in text
    assert "is optional" in text
    assert "aggregate-byte limits apply before decoding" in text
    assert "Exit 0" in text and "exit 1" in text and "exit 2" in text
    assert "no discovery or mutation" in text


def test_authority_and_finish_line_boundaries_are_explicit() -> None:
    text = normalized(ARCH)
    for phrase in (
        "not release authorization",
        "does not infer ancestry",
        "access credentials or networks",
        "publication state",
        "final planned v1.4 feature slice",
        "finish-line review",
    ):
        assert phrase in text


def test_governance_markers_are_exact_and_unique() -> None:
    base = "v1.4.3-deterministic-readiness-decision-record-design"
    for relative, suffix in (
        ("CHANGELOG.md", "changelog"),
        ("docs/HISTORY.md", "history"),
        ("docs/roadmap.md", "roadmap"),
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(f"<!-- {base}-{suffix} -->") == 1
        assert "Production implementation — Not Started" in text
