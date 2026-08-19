"""Step 8.9.4 documentation and First 15 Minutes integration contract."""

from __future__ import annotations

import os
import re
import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTATION_TESTS = REPO_ROOT / "tests" / "documentation"
EN_MANUAL = REPO_ROOT / "docs" / "user-guide" / "en"
ZH_TW_MANUAL = REPO_ROOT / "docs" / "user-guide" / "zh-TW"
PYPROJECT = REPO_ROOT / "pyproject.toml"
GOVERNING_DESIGN = REPO_ROOT / "docs" / "releases" / "v1.0-full-release-readiness-verification.md"
STEP_8_5_ACCEPTANCE = (
    REPO_ROOT / "docs" / "releases" / "v1.0-documentation-user-manuals-acceptance.md"
)

REQUIRED_DOCUMENTATION_SUITES = {
    "test_first_15_minutes.py",
    "test_user_manual_functional_parity.py",
    "test_user_manual_parity.py",
    "test_user_manual_structure.py",
}
EXPECTED_CHAPTER_COUNT = 13


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _manual_chapters(directory: Path) -> set[str]:
    return {path.name for path in directory.glob("*.md") if path.is_file()}


def _required_wheel() -> Path:
    raw_path = os.environ.get("OPL_TEST_WHEEL")
    if not raw_path:
        pytest.skip(
            "OPL_TEST_WHEEL is not set; the packaging job supplies the "
            "current wheel for final Step 8.9.4 evidence"
        )

    wheel = Path(raw_path).expanduser().resolve()
    assert wheel.is_file(), f"OPL_TEST_WHEEL does not identify a file: {wheel}"
    assert wheel.suffix == ".whl", f"OPL_TEST_WHEEL is not a wheel: {wheel}"
    return wheel


def _normalized_distribution(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def test_accepted_documentation_contract_suites_remain_present() -> None:
    present = {path.name for path in DOCUMENTATION_TESTS.glob("test_*.py")}
    assert REQUIRED_DOCUMENTATION_SUITES <= present


def test_english_and_zh_tw_manuals_retain_exact_chapter_parity() -> None:
    english = _manual_chapters(EN_MANUAL)
    zh_tw = _manual_chapters(ZH_TW_MANUAL)

    assert len(english) == EXPECTED_CHAPTER_COUNT
    assert len(zh_tw) == EXPECTED_CHAPTER_COUNT
    assert english == zh_tw


def test_step_8_5_documentation_acceptance_remains_accepted() -> None:
    acceptance = _read(STEP_8_5_ACCEPTANCE)
    assert re.search(r"(?im)^>\s*\*\*Status:\*\*\s*Accepted\s*$", acceptance)


def test_first_15_minutes_suite_is_explicitly_wheel_backed() -> None:
    source = _read(DOCUMENTATION_TESTS / "test_first_15_minutes.py")
    assert "OPL_TEST_WHEEL" in source
    assert "pytest.skip" in source


def test_step_8_9_4_requires_a_real_wheel() -> None:
    _required_wheel()


def test_step_8_9_4_wheel_matches_canonical_project_identity() -> None:
    wheel = _required_wheel()
    project = tomllib.loads(_read(PYPROJECT))["project"]
    expected_prefix = (
        f"{_normalized_distribution(project['name'])}-{str(project['version']).replace('-', '_')}"
    )
    normalized_filename = _normalized_distribution(wheel.name)

    assert normalized_filename.startswith(_normalized_distribution(expected_prefix))


def test_governing_design_rejects_skips_as_final_evidence() -> None:
    design = " ".join(_read(GOVERNING_DESIGN).lower().split())
    assert "first 15 minutes" in design
    assert "skipped wheel-backed tests cannot count as final acceptance evidence" in design
    assert "tests/documentation" in design


def test_step_8_9_4_does_not_claim_rc_acceptance() -> None:
    """Step 8.9 acceptance must not pre-approve the independent RC gate."""
    design = _read(GOVERNING_DESIGN)

    assert "Step 8.10 RC Acceptance" in design
    assert "Step 8.9 formal acceptance is complete." in design
    assert "No Step 8.10 RC acceptance evidence is claimed here." in design
