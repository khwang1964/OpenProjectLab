from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/read-only-verification-invocation.md"
RELEASE = ROOT / "docs/releases/v1.3.5-read-only-verification-invocation.md"


def test_design_surfaces_exist_and_remain_pending() -> None:
    architecture = ARCHITECTURE.read_text(encoding="utf-8")
    release = RELEASE.read_text(encoding="utf-8")
    assert "Accepted / Terminally Closed" in architecture
    assert "Status: Accepted / Completed" in release
    assert "Production implementation — Not Started" in release


def test_design_defines_one_explicit_invocation() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "ReadOnlyVerificationInvoker" in text
    assert "accepts exactly one immutable `VerificationRequest`" in text
    assert "orchestrator exactly once" in text
    assert "immutable `VerificationReport` unchanged" in text


def test_design_preserves_structured_failures() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "structured collection findings" in text
    assert "structured contradiction findings" in text
    assert "structured validation findings" in text
    assert "never converts an exception or failure into success-shaped evidence" in text


def test_design_requires_independent_stateless_invocations() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "owns no mutable state" in text
    assert "cannot affect a" in text
    assert "later invocation" in text
    assert "no session, queue, batch, or shared result cache" in text


def test_design_preserves_deferred_authority() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "production implementation" in text
    assert "CLI, public SDK, HTTP, RPC, plugin" in text
    assert "test execution and arbitrary subprocess execution" in text
    assert "commit, push, merge, tag, release, publication" in text


def test_governance_surfaces_share_exact_design_markers() -> None:
    marker = "v1.3.5-read-only-verification-invocation-design"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative, exact_marker in surfaces.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Production implementation — Not Started" in text
