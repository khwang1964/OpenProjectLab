from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
USER_GUIDE_ROOT = REPO_ROOT / "docs" / "user-guide"

EN_ROOT = USER_GUIDE_ROOT / "en"
ZH_TW_ROOT = USER_GUIDE_ROOT / "zh-TW"

REQUIRED_CHAPTERS = frozenset(
    {
        "README.md",
        "concepts.md",
        "installation.md",
        "quick-start.md",
        "configuration.md",
        "cli.md",
        "generators.md",
        "courseware.md",
        "plugins.md",
        "ai-integration.md",
        "marketplace.md",
        "troubleshooting.md",
        "upgrading.md",
    }
)


def _top_level_markdown_files(manual_root: Path) -> frozenset[str]:
    if not manual_root.is_dir():
        pytest.fail(f"Missing required v1.0 user manual root: {manual_root.relative_to(REPO_ROOT)}")

    return frozenset(
        path.name
        for path in manual_root.iterdir()
        if path.is_file() and path.suffix.lower() == ".md"
    )


def test_english_manual_contains_all_required_chapters() -> None:
    english_files = _top_level_markdown_files(EN_ROOT)

    missing = REQUIRED_CHAPTERS - english_files

    assert missing == frozenset(), (
        f"English v1.0 User Manual is missing required chapters: {sorted(missing)}"
    )


def test_zh_tw_manual_contains_all_required_chapters() -> None:
    zh_tw_files = _top_level_markdown_files(ZH_TW_ROOT)

    missing = REQUIRED_CHAPTERS - zh_tw_files

    assert missing == frozenset(), (
        "Traditional Chinese (Taiwan) v1.0 User Manual is missing "
        f"required chapters: {sorted(missing)}"
    )


def test_english_and_zh_tw_manual_chapter_sets_match() -> None:
    english_files = _top_level_markdown_files(EN_ROOT)
    zh_tw_files = _top_level_markdown_files(ZH_TW_ROOT)

    english_only = english_files - zh_tw_files
    zh_tw_only = zh_tw_files - english_files

    assert english_only == frozenset() and zh_tw_only == frozenset(), (
        "EN / zh-TW User Manual structural parity drift detected. "
        f"English-only chapters: {sorted(english_only)}; "
        f"zh-TW-only chapters: {sorted(zh_tw_only)}"
    )


def test_no_orphan_optional_markdown_chapter_exists_in_only_one_language() -> None:
    english_files = _top_level_markdown_files(EN_ROOT)
    zh_tw_files = _top_level_markdown_files(ZH_TW_ROOT)

    english_optional = english_files - REQUIRED_CHAPTERS
    zh_tw_optional = zh_tw_files - REQUIRED_CHAPTERS

    assert english_optional == zh_tw_optional, (
        "Optional User Manual chapters must also preserve bilingual parity. "
        f"English optional chapters: {sorted(english_optional)}; "
        f"zh-TW optional chapters: {sorted(zh_tw_optional)}"
    )
