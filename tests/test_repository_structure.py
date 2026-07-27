"""Tests for the OpenProjectLab repository structure audit."""

from pathlib import Path

from scripts.audit_repository import (
    RepositoryRequirement,
    find_missing_requirements,
    format_missing_requirement,
)


def test_repository_requirement_detects_existing_file(
    tmp_path: Path,
) -> None:
    """Verify that an existing file requirement is detected."""
    target = tmp_path / "README.md"
    target.write_text("# Test\n", encoding="utf-8")

    requirement = RepositoryRequirement("README.md")

    assert requirement.exists(tmp_path)


def test_repository_requirement_detects_existing_directory(
    tmp_path: Path,
) -> None:
    """Verify that an existing directory requirement is detected."""
    target = tmp_path / "docs"
    target.mkdir()

    requirement = RepositoryRequirement(
        "docs",
        kind="directory",
    )

    assert requirement.exists(tmp_path)


def test_repository_requirement_rejects_wrong_path_kind(
    tmp_path: Path,
) -> None:
    """Verify that a file does not satisfy a directory requirement."""
    target = tmp_path / "docs"
    target.write_text("not a directory\n", encoding="utf-8")

    requirement = RepositoryRequirement(
        "docs",
        kind="directory",
    )

    assert not requirement.exists(tmp_path)


def test_find_missing_requirements(
    tmp_path: Path,
) -> None:
    """Verify that all missing requirements are returned."""
    existing = tmp_path / "README.md"
    existing.write_text("# Test\n", encoding="utf-8")

    requirements = (
        RepositoryRequirement("README.md"),
        RepositoryRequirement("LICENSE"),
        RepositoryRequirement("docs", kind="directory"),
    )

    missing = find_missing_requirements(
        tmp_path,
        requirements,
    )

    assert missing == [
        RepositoryRequirement("LICENSE"),
        RepositoryRequirement("docs", kind="directory"),
    ]


def test_format_missing_requirement() -> None:
    """Verify the console representation of a missing requirement."""
    requirement = RepositoryRequirement(
        ".github/workflows",
        kind="directory",
    )

    assert format_missing_requirement(requirement) == "- directory: .github/workflows"
