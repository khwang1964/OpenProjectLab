from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/verification-report-usability.md"
RELEASE = ROOT / ("docs/releases/v1.3.11-v1.3.13-verification-report-usability-design-train.md")


def test_design_train_has_three_ordered_slices() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "v1.3.11 — Canonical verification report serialization" in text
    assert "v1.3.12 — Offline report validation and inspection" in text
    assert "v1.3.13 — Stable result and exit-code contract" in text


def test_report_serialization_is_canonical_strict_and_pure() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "schema-version-1 JSON" in text
    assert "canonical round-trip equality" in text
    assert "Serialization is pure" in text


def test_offline_report_inspection_cannot_reach_runtime() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "without constructing or invoking a verification runtime" in text
    assert "Own no cache, persistence, discovery, retry, polling" in text


def test_stable_result_contract_separates_exit_categories() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "recorded verification failure" in text
    assert "input or" in text
    assert "usage error" in text
    assert "platform-specific subprocess return codes" in text


def test_release_record_keeps_implementation_not_started() -> None:
    text = RELEASE.read_text(encoding="utf-8")
    assert "Status: Design Accepted / Completed" in text
    assert "production implementation is Not Started" in text
    assert "Every merge remains explicitly authorized" in text


def test_governance_surfaces_use_exact_unique_markers() -> None:
    marker = "v1.3.11-v1.3.13-verification-report-usability-design-train"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative_path, exact_marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Production implementation — Not Started" in text


def test_design_preserves_explicit_non_goals() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "no stdin, output-file persistence, batch" in text
    assert "no SDK, HTTP, RPC, plugin, marketplace" in text
    assert "no arbitrary subprocess and no test execution" in text
