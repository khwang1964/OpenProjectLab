"""Fail-closed contract tests for GA.8 Formal GA Acceptance."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

ACCEPTANCE_RECORD = REPO_ROOT / "docs" / "releases" / "v1.0-ga-acceptance-record.md"

EXPECTED_VERSION = "1.0.0"
EXPECTED_TAG = "v1.0.0"
EXPECTED_PUBLICATION_COMMIT = "d469b41b898d80811a14a423d08b09d0b51bc189"
EXPECTED_RC_VERSION = "1.0.0rc1"
EXPECTED_RC_TAG = "v1.0.0-rc.1"

FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")

TERMINAL_DOCUMENTS = (
    "docs/releases/v1.0-ga-acceptance-record.md",
    "docs/releases/v1.0-ga-acceptance.md",
    "docs/roadmap.md",
    "docs/HISTORY.md",
    "CHANGELOG.md",
)

REQUIRED_CLOSURE_GATES = (
    "GA.8 acceptance PR --- Merged",
    "GA.8 PR required CI --- Passed",
    "main synchronized with origin/main --- Passed",
    "post-merge consistency verification --- Passed",
    "terminal documentation alignment --- Completed",
)


def _read() -> str:
    assert ACCEPTANCE_RECORD.is_file(), (
        f"Required GA.8 acceptance record is missing: {ACCEPTANCE_RECORD}"
    )
    return ACCEPTANCE_RECORD.read_text(encoding="utf-8")


def _normalized() -> str:
    return " ".join(_read().split())


def _metadata_value(document: str, label: str) -> str:
    prefix = f"> **{label}:**"
    for line in document.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    raise AssertionError(f"Missing metadata field: {label}")


def test_ga_8_acceptance_record_exists() -> None:
    assert ACCEPTANCE_RECORD.is_file()


def test_ga_8_records_exact_stable_publication_identity() -> None:
    document = _read()

    assert _metadata_value(document, "Canonical package version") == f"`{EXPECTED_VERSION}`"
    assert _metadata_value(document, "Published GA tag") == f"`{EXPECTED_TAG}`"
    assert (
        _metadata_value(document, "Approved publication commit")
        == f"`{EXPECTED_PUBLICATION_COMMIT}`"
    )
    assert FULL_SHA_RE.fullmatch(EXPECTED_PUBLICATION_COMMIT)


def test_ga_1_through_ga_7_are_completed_and_ga_8_is_in_progress() -> None:
    normalized = _normalized()

    for step in range(1, 8):
        assert f"GA.{step} --- Completed" in normalized

    assert "GA.8 --- In Progress" in normalized


def test_ga_8_does_not_preaccept_formal_ga() -> None:
    document = _read()

    assert _metadata_value(document, "Formal v1.0.0 GA Acceptance") == "Not Accepted"

    current_state = document.split("## 14. Current State", maxsplit=1)[1]
    current_state = current_state.split(
        "## 15. Terminal Acceptance Transition",
        maxsplit=1,
    )[0]

    assert "Formal v1.0.0 GA Acceptance --- Not Accepted" in current_state


def test_ga_8_retains_ga_4_artifact_backed_evidence() -> None:
    normalized = _normalized()

    assert "Focused artifact-backed suite --- 30 passed" in normalized
    assert "Required GA artifact-backed skips --- 0" in normalized
    assert "Installed distribution version --- 1.0.0" in normalized
    assert "First 15 Minutes --- Passed" in normalized
    assert "Representative installed-user E2E --- Passed" in normalized


def test_ga_8_retains_ga_5_regression_and_quality_evidence() -> None:
    normalized = _normalized()

    assert "Full regression --- 1980 passed, 4 skipped, 1 deselected" in normalized
    assert "Coverage --- 90.90%" in normalized
    assert "Required coverage --- 67.0% --- Passed" in normalized
    assert "git diff --check --- Passed" in normalized
    assert "Ruff --- Passed" in normalized
    assert "Ruff Format --- Passed" in normalized
    assert "pre-commit --- Passed" in normalized


def test_ga_8_retains_ga_6_ci_evidence() -> None:
    normalized = _normalized()

    assert "CI / Quality checks --- Passed" in normalized
    assert "CI / Packaging artifact verification --- Passed" in normalized


def test_ga_8_retains_ga_7_publication_evidence() -> None:
    normalized = _normalized()

    assert f"Annotated tag --- {EXPECTED_TAG}" in normalized
    assert f"Remote peeled tag target --- {EXPECTED_PUBLICATION_COMMIT}" in normalized
    assert "Draft-first GitHub Release verification --- Passed" in normalized
    assert "Stable publication --- Passed" in normalized
    assert "GitHub Release draft --- false" in normalized
    assert "GitHub Release prerelease --- false" in normalized
    assert "Post-publication identity re-read --- Passed" in normalized


def test_ga_8_preserves_historical_rc_identity() -> None:
    normalized = _normalized()

    assert f"Package version --- {EXPECTED_RC_VERSION}" in normalized
    assert f"Tag --- {EXPECTED_RC_TAG}" in normalized
    assert "must not move the RC tag" in _read()


def test_ga_8_declares_all_required_closure_gates() -> None:
    normalized = _normalized()

    for gate in REQUIRED_CLOSURE_GATES:
        assert gate in normalized


def test_ga_8_declares_terminal_documentation_scope() -> None:
    normalized = _normalized()

    for relative_path in TERMINAL_DOCUMENTS:
        assert relative_path in normalized


def test_ga_8_terminal_acceptance_is_only_a_future_transition() -> None:
    document = _read()
    normalized = _normalized()

    assert "This section describes the allowed future transition" in document
    assert "it does not assert that the transition has already occurred" in normalized
    assert "Only after every GA.8 closure gate passes" in normalized
    assert "Formal v1.0.0 GA Acceptance --- Accepted" in normalized


def test_ga_8_is_fail_closed_on_unresolved_closure() -> None:
    normalized = _normalized()

    assert "Formal GA Acceptance must remain `Not Accepted`" in normalized
    assert "acceptance PR not merged" in normalized
    assert "required PR CI not green" in normalized
    assert "post-merge consistency test failure" in normalized
    assert "unresolved acceptance closure marker" in normalized
