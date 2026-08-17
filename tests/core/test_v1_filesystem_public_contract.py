"""Freeze the implemented OpenProjectLab v1 filesystem-visible contract."""

from pathlib import Path

import pytest

from generator.core.filesystem import (
    FileSystem,
    FileSystemError,
    ensure_directory,
    read_text,
    remove_file,
    write_text,
)
from generator.sdk import WritePolicy, WriteStatus


def test_v1_ensure_directory_creates_parent_tree(tmp_path: Path) -> None:
    """Create missing directories and return the normalized destination."""
    destination = tmp_path / "one" / "two"

    result = ensure_directory(destination)

    assert result == destination
    assert destination.is_dir()


def test_v1_ensure_directory_dry_run_has_no_side_effect(tmp_path: Path) -> None:
    """Return the planned directory without creating it in dry-run mode."""
    destination = tmp_path / "planned"

    assert ensure_directory(destination, dry_run=True) == destination
    assert not destination.exists()


def test_v1_write_text_reports_created_and_writes_content(tmp_path: Path) -> None:
    """Create a new file and report CREATED."""
    destination = tmp_path / "nested" / "README.md"

    result = write_text(
        destination,
        "hello",
        policy=WritePolicy.CREATE_ONLY,
    )

    assert result.path == destination
    assert result.status is WriteStatus.CREATED
    assert destination.read_text(encoding="utf-8") == "hello"


def test_v1_write_text_overwrite_reports_updated(tmp_path: Path) -> None:
    """Overwrite changed content and report UPDATED."""
    destination = tmp_path / "README.md"
    destination.write_text("before", encoding="utf-8")

    result = write_text(
        destination,
        "after",
        policy=WritePolicy.OVERWRITE,
    )

    assert result.status is WriteStatus.UPDATED
    assert destination.read_text(encoding="utf-8") == "after"


def test_v1_write_text_identical_overwrite_reports_unchanged(
    tmp_path: Path,
) -> None:
    """Avoid rewriting identical content and report UNCHANGED."""
    destination = tmp_path / "README.md"
    destination.write_text("same", encoding="utf-8")

    result = write_text(
        destination,
        "same",
        policy=WritePolicy.OVERWRITE,
    )

    assert result.status is WriteStatus.UNCHANGED
    assert destination.read_text(encoding="utf-8") == "same"


def test_v1_write_text_skip_existing_preserves_content(tmp_path: Path) -> None:
    """Preserve existing content and report SKIPPED under skip policy."""
    destination = tmp_path / "README.md"
    destination.write_text("original", encoding="utf-8")

    result = write_text(
        destination,
        "replacement",
        policy=WritePolicy.SKIP_EXISTING,
    )

    assert result.status is WriteStatus.SKIPPED
    assert destination.read_text(encoding="utf-8") == "original"


def test_v1_write_text_create_only_rejects_existing_file(
    tmp_path: Path,
) -> None:
    """Reject overwrite when CREATE_ONLY is requested."""
    destination = tmp_path / "README.md"
    destination.write_text("original", encoding="utf-8")

    with pytest.raises(FileSystemError):
        write_text(
            destination,
            "replacement",
            policy=WritePolicy.CREATE_ONLY,
        )

    assert destination.read_text(encoding="utf-8") == "original"


def test_v1_write_text_dry_run_reports_status_without_mutation(
    tmp_path: Path,
) -> None:
    """Compute write status without mutating the filesystem."""
    destination = tmp_path / "README.md"

    result = write_text(
        destination,
        "planned",
        policy=WritePolicy.OVERWRITE,
        dry_run=True,
    )

    assert result.status is WriteStatus.CREATED
    assert not destination.exists()


def test_v1_legacy_overwrite_argument_remains_compatible(
    tmp_path: Path,
) -> None:
    """Keep the compatibility overwrite argument mapped to write policies."""
    destination = tmp_path / "README.md"
    destination.write_text("before", encoding="utf-8")

    result = write_text(destination, "after", overwrite=True)

    assert result.status is WriteStatus.UPDATED
    assert destination.read_text(encoding="utf-8") == "after"


def test_v1_conflicting_write_policy_arguments_are_rejected(
    tmp_path: Path,
) -> None:
    """Reject contradictory modern and compatibility write controls."""
    with pytest.raises(FileSystemError):
        write_text(
            tmp_path / "README.md",
            "content",
            policy=WritePolicy.CREATE_ONLY,
            overwrite=True,
        )


def test_v1_read_text_reports_missing_file_through_filesystem_error(
    tmp_path: Path,
) -> None:
    """Translate missing reads into FileSystemError."""
    with pytest.raises(FileSystemError):
        read_text(tmp_path / "missing.txt")


def test_v1_remove_file_dry_run_preserves_existing_file(tmp_path: Path) -> None:
    """Keep dry-run removal side-effect free."""
    path = tmp_path / "keep.txt"
    path.write_text("keep", encoding="utf-8")

    remove_file(path, dry_run=True)

    assert path.exists()


def test_v1_filesystem_compatibility_aliases_create_directories(
    tmp_path: Path,
) -> None:
    """Keep existing FileSystem directory aliases operational."""
    first = tmp_path / "first"
    second = tmp_path / "second"

    assert FileSystem.ensure_dir(first) == first
    assert FileSystem.mkdir(second) == second
    assert first.is_dir()
    assert second.is_dir()
