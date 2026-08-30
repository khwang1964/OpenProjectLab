from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / ("docs/releases/v1.3.5-v1.3.7-read-only-verification-delivery-train.md")


def test_train_defines_three_ordered_capabilities() -> None:
    text = TRAIN.read_text(encoding="utf-8")
    assert "v1.3.5 — one stateless" in text
    assert "v1.3.6 — strict deterministic" in text
    assert "v1.3.7 — one explicit opt-in" in text
    assert "v1.3.7 depends on v1.3.6" in text
    assert "v1.3.5 delegates to the accepted v1.3.4" in text


def test_train_preserves_shared_boundaries() -> None:
    text = TRAIN.read_text(encoding="utf-8")
    assert "caller-supplied exact evidence" in text
    assert "deterministic fail-closed processing" in text
    assert "no arbitrary subprocess or test execution" in text
    assert "no Git/GitHub mutation" in text


def test_train_uses_batched_but_separate_acceptance() -> None:
    text = TRAIN.read_text(encoding="utf-8")
    assert "One Design PR" in text
    assert "one terminal Design Acceptance PR" in text
    assert "implementation PR delivers" in text
    assert "separate-closure PR pair remains required" in text


def test_train_governance_marker_is_exact() -> None:
    marker = "v1.3.5-v1.3.7-read-only-verification-delivery-train"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative, exact_marker in surfaces.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
