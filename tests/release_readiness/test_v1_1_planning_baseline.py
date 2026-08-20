"""Fail-closed contract tests for the OpenProjectLab v1.1 planning baseline."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE = REPO_ROOT / "docs" / "releases" / "v1.1-planning-baseline.md"
ROADMAP = REPO_ROOT / "docs" / "roadmap.md"
HISTORY = REPO_ROOT / "docs" / "HISTORY.md"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_planning_baseline_exists_and_remains_pre_acceptance() -> None:
    document = _read(BASELINE)

    assert "**Status:** Proposed" in document
    assert "**Target Release:** OpenProjectLab v1.1.0" in document
    assert "**Formal v1.1 Acceptance:** Not Accepted" in document
    assert "v1.1 Planning Baseline --- In Progress" in document


def test_planning_baseline_preserves_accepted_v1_contracts() -> None:
    document = _read(BASELINE)

    required_contracts = (
        "generator.sdk",
        "Generator lifecycle",
        "Plugin Entry Point",
        "Courseware Domain",
        "provider-independent AI contracts",
        "deterministic Marketplace contracts",
        "opl",
    )
    for contract in required_contracts:
        assert contract in document

    assert "1.x   → backward-compatible evolution" in document
    assert "2.0   → intentional breaking Stable-contract changes" in document


def test_ai_and_marketplace_implementation_remain_not_started() -> None:
    document = _read(BASELINE)

    assert "Marketplace CLI --- Not Started" in document
    assert "AI CLI --- Not Started" in document
    assert "Live provider invocation remains Experimental and opt-in" in document
    assert "must not imply a remote service" in document


def test_deferred_scope_remains_explicit() -> None:
    document = _read(BASELINE)

    required_non_goals = (
        "remote Marketplace service",
        "automatic Plugin or Generator activation",
        "artifact signing",
        "general dependency resolution",
        "ratings, reviews, monetization",
        "AI Refactoring Assistant",
        "streaming or tool calling",
        "generalized cross-Generator transaction rollback",
    )
    for non_goal in required_non_goals:
        assert non_goal in document


def test_documentation_and_artifact_backed_gates_are_required() -> None:
    document = _read(BASELINE)

    assert "English and Traditional Chinese (Taiwan) functional parity" in document
    assert "built wheel and sdist verification passed" in document
    assert "clean-install and installed-user workflows passed" in document
    assert "support-matrix updates only after direct evidence exists" in document


def test_terminal_documents_align_to_planning_state() -> None:
    for path in (ROADMAP, HISTORY, CHANGELOG):
        document = _read(path)
        assert "v1.1 Planning Baseline" in document
        assert "Formal v1.1 Acceptance --- Not Accepted" in document


def test_planning_documents_do_not_fabricate_future_evidence() -> None:
    planning_sections = (
        _read(BASELINE),
        _read(ROADMAP).split("# Milestone 9 --- v1.1", maxsplit=1)[1],
        _read(HISTORY).split("# v1.1 Planning Baseline", maxsplit=1)[1],
    )
    forbidden = (
        "v1.1 CI --- Passed",
        "v1.1 acceptance PR --- Merged",
        "Formal v1.1 Acceptance --- Accepted",
        "v1.1.0 tag --- Published",
    )

    for document in planning_sections:
        for marker in forbidden:
            assert marker not in document
