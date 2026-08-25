"""Release-level EN / zh-TW documentation parity contract for v1.1."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

DESIGN = ROOT / "docs" / "releases" / "v1.1-documentation-parity.md"
ROADMAP = ROOT / "docs" / "roadmap.md"
AI_ACCEPTANCE = ROOT / "docs" / "releases" / "v1.1-ai-cli-implementation-acceptance.md"

USER_GUIDE = ROOT / "docs" / "user-guide"
EN_ROOT = USER_GUIDE / "en"
ZH_TW_ROOT = USER_GUIDE / "zh-TW"

EN_CLI = EN_ROOT / "cli.md"
ZH_TW_CLI = ZH_TW_ROOT / "cli.md"
EN_MARKETPLACE = EN_ROOT / "marketplace.md"
ZH_TW_MARKETPLACE = ZH_TW_ROOT / "marketplace.md"

STRUCTURAL_PARITY = ROOT / "tests" / "documentation" / "test_user_manual_parity.py"
FUNCTIONAL_PARITY = ROOT / "tests" / "documentation" / "test_user_manual_functional_parity.py"
AI_PARITY = ROOT / "tests" / "documentation" / "test_v1_1_ai_cli_user_manual_parity.py"

MARKETPLACE_SUBCOMMANDS = (
    "versions",
    "inspect",
    "verify",
    "install",
)

MARKETPLACE_COMMAND_SHAPES = (
    "opl marketplace versions IDENTITY --catalog FILE [--json]",
    "opl marketplace inspect COORDINATE --catalog FILE [--json]",
    ("opl marketplace verify COORDINATE --catalog FILE --payload-root DIR [--json]"),
    ("opl marketplace install COORDINATE --catalog FILE --payload-root DIR [--dry-run] [--json]"),
)

AI_COMMANDS = (
    "opl ai course",
    "opl ai review",
    "opl ai document",
    "opl ai template",
)


def _read(path: Path) -> str:
    if not path.is_file():
        pytest.fail(f"Missing required v1.1 documentation authority: {path}")
    return path.read_text(encoding="utf-8")


def _markdown_names(root: Path) -> frozenset[str]:
    if not root.is_dir():
        pytest.fail(f"Missing required User Manual root: {root}")
    return frozenset(
        path.name for path in root.iterdir() if path.is_file() and path.suffix.lower() == ".md"
    )


def _current_state(text: str) -> str:
    marker = "## 9. Current State"
    if marker not in text:
        pytest.fail("v1.1 documentation parity design is missing Current State")
    return text.split(marker, maxsplit=1)[1]


def test_v1_1_release_documentation_parity_design_exists() -> None:
    text = _read(DESIGN)

    assert "v1.1.7 --- Documentation / EN-zh-TW Parity" in text
    assert "> **Formal v1.1 Acceptance:** Not Accepted" in text


def test_ai_cli_implementation_is_accepted_before_v1_1_7() -> None:
    text = _read(AI_ACCEPTANCE)

    assert "> **AI CLI Implementation Acceptance:** Accepted" in text
    assert "> **Formal v1.1 Acceptance:** Not Accepted" in text


def test_en_and_zh_tw_top_level_manual_structure_matches() -> None:
    assert _markdown_names(EN_ROOT) == _markdown_names(ZH_TW_ROOT)


@pytest.mark.parametrize("path", (EN_CLI, ZH_TW_CLI))
def test_bilingual_cli_manuals_document_reviewed_v1_1_command_families(
    path: Path,
) -> None:
    text = _read(path)
    lowered = text.lower()

    assert "marketplace" in lowered
    assert "ai" in lowered


@pytest.mark.parametrize("path", (EN_CLI, ZH_TW_CLI))
def test_bilingual_cli_manuals_document_marketplace_subcommand_inventory(
    path: Path,
) -> None:
    text = _read(path)

    for subcommand in MARKETPLACE_SUBCOMMANDS:
        assert subcommand in text


@pytest.mark.parametrize(
    ("path", "rejection_marker"),
    (
        (EN_CLI, "does not add `opl marketplace list`"),
        (ZH_TW_CLI, "不新增 `opl marketplace list`"),
    ),
)
def test_bilingual_cli_manuals_explicitly_reject_marketplace_list(
    path: Path,
    rejection_marker: str,
) -> None:
    text = _read(path)

    assert rejection_marker in text


@pytest.mark.parametrize("path", (EN_MARKETPLACE, ZH_TW_MARKETPLACE))
def test_bilingual_marketplace_manuals_document_exact_command_shapes(
    path: Path,
) -> None:
    text = _read(path)

    for command in MARKETPLACE_COMMAND_SHAPES:
        assert command in text


@pytest.mark.parametrize("path", (EN_CLI, ZH_TW_CLI))
def test_bilingual_cli_manuals_document_exact_ai_inventory(path: Path) -> None:
    text = _read(path)

    for command in AI_COMMANDS:
        assert command in text


def test_existing_documentation_parity_authorities_remain_present() -> None:
    for authority in (
        STRUCTURAL_PARITY,
        FUNCTIONAL_PARITY,
        AI_PARITY,
    ):
        assert authority.is_file(), f"Missing documentation authority: {authority}"


def test_first_15_minutes_authority_remains_present() -> None:
    candidates = (
        ROOT / "tests" / "documentation" / "test_first_15_minutes.py",
        ROOT / "tests" / "release_readiness" / "test_v1_documentation_first_15_minutes.py",
    )

    assert any(path.is_file() for path in candidates), (
        "At least one executable First 15 Minutes / onboarding authority must remain present"
    )


def test_v1_1_7_current_state_does_not_preaccept_formal_v1_1() -> None:
    design = _read(DESIGN)
    state = _current_state(design)

    assert "Formal v1.1 Acceptance --- Not Accepted" in state
    assert "Formal v1.1 Acceptance --- Accepted" not in state

    assert "> **Formal v1.1 Acceptance:** Not Accepted" in design
    assert "> **Formal v1.1 Acceptance:** Not Accepted" in _read(AI_ACCEPTANCE)


def test_v1_1_8_remains_next_release_gate() -> None:
    text = _read(DESIGN)

    assert "v1.1.8 Reliability / Artifact-backed Verification" in text
