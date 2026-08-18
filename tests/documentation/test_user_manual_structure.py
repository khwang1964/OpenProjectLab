from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
USER_GUIDE_ROOT = REPO_ROOT / "docs" / "user-guide"

LANGUAGE_ROOTS = {
    "en": USER_GUIDE_ROOT / "en",
    "zh-TW": USER_GUIDE_ROOT / "zh-TW",
}

REQUIRED_CHAPTERS = (
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
)


@pytest.mark.parametrize(("language", "manual_root"), LANGUAGE_ROOTS.items())
def test_required_user_manual_root_exists(
    language: str,
    manual_root: Path,
) -> None:
    assert manual_root.is_dir(), (
        f"Missing required v1.0 user manual root for {language}: "
        f"{manual_root.relative_to(REPO_ROOT)}"
    )


@pytest.mark.parametrize(("language", "manual_root"), LANGUAGE_ROOTS.items())
@pytest.mark.parametrize("chapter", REQUIRED_CHAPTERS)
def test_required_user_manual_chapter_exists(
    language: str,
    manual_root: Path,
    chapter: str,
) -> None:
    chapter_path = manual_root / chapter

    assert chapter_path.is_file(), (
        f"Missing required v1.0 user manual chapter for {language}: "
        f"{chapter_path.relative_to(REPO_ROOT)}"
    )


@pytest.mark.parametrize(("language", "manual_root"), LANGUAGE_ROOTS.items())
def test_user_manual_root_contains_only_markdown_chapter_files_at_top_level(
    language: str,
    manual_root: Path,
) -> None:
    if not manual_root.is_dir():
        pytest.fail(
            f"Missing required v1.0 user manual root for {language}: "
            f"{manual_root.relative_to(REPO_ROOT)}"
        )

    unexpected_files = sorted(
        path.name
        for path in manual_root.iterdir()
        if path.is_file() and path.suffix.lower() != ".md"
    )

    assert unexpected_files == [], (
        f"Unexpected non-Markdown top-level files in {language} user manual: {unexpected_files}"
    )
