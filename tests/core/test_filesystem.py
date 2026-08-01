"""Test filesystem operations and write-result contracts."""

from pathlib import Path

import pytest

from generator.core.filesystem import (
    FileSystem,
    FileSystemError,
    copy_file,
    ensure_directory,
    read_text,
    remove_file,
    write_text,
)
from generator.core.models import WritePolicy, WriteStatus


class TestEnsureDirectory:
    """Test directory creation, validation, and dry-run behavior."""

    def test_creates_nested_directory(self, tmp_path: Path) -> None:
        """Create all missing parent directories."""
        target = tmp_path / "courses" / "modern-java" / "week-01"

        result = ensure_directory(target)

        assert result == target
        assert target.is_dir()

    def test_accepts_existing_directory(self, tmp_path: Path) -> None:
        """Return an existing directory without changing it."""
        target = tmp_path / "existing"
        target.mkdir()

        result = ensure_directory(target)

        assert result == target
        assert target.is_dir()

    def test_rejects_existing_file(self, tmp_path: Path) -> None:
        """Reject a path that already exists as a file."""
        target = tmp_path / "not-a-directory"
        target.write_text("content", encoding="utf-8")

        with pytest.raises(FileSystemError, match="不是目錄"):
            ensure_directory(target)

    def test_dry_run_does_not_create_directory(
        self,
        tmp_path: Path,
    ) -> None:
        """Return the target without creating it during a dry run."""
        target = tmp_path / "dry-run-directory"

        result = FileSystem.ensure_directory(target, dry_run=True)

        assert result == target
        assert not target.exists()


class TestWriteText:
    """Test text writes, policies, statuses, and dry-run behavior."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Create missing parents and report a created file."""
        target = tmp_path / "generated" / "docs" / "README.md"

        result = write_text(target, "# OpenProjectLab\n")

        assert result.path == target
        assert result.status is WriteStatus.CREATED
        assert target.read_text(encoding="utf-8") == "# OpenProjectLab\n"

    def test_supports_unicode(self, tmp_path: Path) -> None:
        """Write and read Unicode content using UTF-8."""
        target = tmp_path / "課程說明.md"
        content = "第一週: 函數式程式設計\n"

        result = write_text(target, content)

        assert result.status is WriteStatus.CREATED
        assert read_text(target) == content

    def test_overwrites_existing_file_by_default(
        self,
        tmp_path: Path,
    ) -> None:
        """Preserve the legacy default overwrite behavior."""
        target = tmp_path / "output.txt"
        target.write_text("old", encoding="utf-8")

        result = write_text(target, "new")

        assert result.status is WriteStatus.UPDATED
        assert target.read_text(encoding="utf-8") == "new"

    def test_reports_updated_for_changed_content(
        self,
        tmp_path: Path,
    ) -> None:
        """Report an update when overwrite changes existing content."""
        target = tmp_path / "output.txt"
        target.write_text("old", encoding="utf-8")

        result = write_text(
            target,
            "new",
            policy=WritePolicy.OVERWRITE,
        )

        assert result.path == target
        assert result.status is WriteStatus.UPDATED
        assert target.read_text(encoding="utf-8") == "new"

    def test_reports_unchanged_for_identical_content(
        self,
        tmp_path: Path,
    ) -> None:
        """Avoid rewriting a file whose content is unchanged."""
        target = tmp_path / "output.txt"
        target.write_text("same", encoding="utf-8")
        original_timestamp = target.stat().st_mtime_ns

        result = write_text(
            target,
            "same",
            policy=WritePolicy.OVERWRITE,
        )

        assert result.path == target
        assert result.status is WriteStatus.UNCHANGED
        assert target.stat().st_mtime_ns == original_timestamp

    def test_skips_existing_file(self, tmp_path: Path) -> None:
        """Preserve existing content under the skip-existing policy."""
        target = tmp_path / "output.txt"
        target.write_text("old", encoding="utf-8")

        result = write_text(
            target,
            "new",
            policy=WritePolicy.SKIP_EXISTING,
        )

        assert result.path == target
        assert result.status is WriteStatus.SKIPPED
        assert target.read_text(encoding="utf-8") == "old"

    def test_create_only_rejects_existing_file(
        self,
        tmp_path: Path,
    ) -> None:
        """Reject an existing destination under create-only policy."""
        target = tmp_path / "output.txt"
        target.write_text("old", encoding="utf-8")

        with pytest.raises(FileSystemError, match="不允許覆寫"):
            write_text(
                target,
                "new",
                policy=WritePolicy.CREATE_ONLY,
            )

        assert target.read_text(encoding="utf-8") == "old"

    def test_legacy_overwrite_true_updates_file(
        self,
        tmp_path: Path,
    ) -> None:
        """Support the legacy overwrite=True argument."""
        target = tmp_path / "output.txt"
        target.write_text("old", encoding="utf-8")

        result = write_text(target, "new", overwrite=True)

        assert result.status is WriteStatus.UPDATED
        assert target.read_text(encoding="utf-8") == "new"

    def test_legacy_overwrite_false_rejects_file(
        self,
        tmp_path: Path,
    ) -> None:
        """Support the legacy overwrite=False argument."""
        target = tmp_path / "output.txt"
        target.write_text("old", encoding="utf-8")

        with pytest.raises(FileSystemError, match="不允許覆寫"):
            write_text(target, "new", overwrite=False)

        assert target.read_text(encoding="utf-8") == "old"

    def test_rejects_conflicting_policy_arguments(
        self,
        tmp_path: Path,
    ) -> None:
        """Reject inconsistent modern and legacy policy arguments."""
        target = tmp_path / "output.txt"

        with pytest.raises(FileSystemError, match="互相衝突"):
            write_text(
                target,
                "content",
                policy=WritePolicy.CREATE_ONLY,
                overwrite=True,
            )

    def test_rejects_directory_target(self, tmp_path: Path) -> None:
        """Reject an existing directory as a file destination."""
        target = tmp_path / "directory"
        target.mkdir()

        with pytest.raises(FileSystemError, match="是目錄"):
            write_text(target, "content")

    def test_dry_run_reports_created_without_writing(
        self,
        tmp_path: Path,
    ) -> None:
        """Report creation without producing filesystem effects."""
        target = tmp_path / "dry-run" / "output.txt"

        result = write_text(target, "content", dry_run=True)

        assert result.path == target
        assert result.status is WriteStatus.CREATED
        assert not target.exists()
        assert not target.parent.exists()

    def test_dry_run_reports_updated_without_writing(
        self,
        tmp_path: Path,
    ) -> None:
        """Report an update without changing existing content."""
        target = tmp_path / "output.txt"
        target.write_text("old", encoding="utf-8")

        result = write_text(
            target,
            "new",
            policy=WritePolicy.OVERWRITE,
            dry_run=True,
        )

        assert result.path == target
        assert result.status is WriteStatus.UPDATED
        assert target.read_text(encoding="utf-8") == "old"

    def test_dry_run_reports_unchanged(self, tmp_path: Path) -> None:
        """Report unchanged content during a dry run."""
        target = tmp_path / "output.txt"
        target.write_text("same", encoding="utf-8")

        result = write_text(
            target,
            "same",
            policy=WritePolicy.OVERWRITE,
            dry_run=True,
        )

        assert result.path == target
        assert result.status is WriteStatus.UNCHANGED
        assert target.read_text(encoding="utf-8") == "same"

    def test_dry_run_reports_skipped(self, tmp_path: Path) -> None:
        """Report a skipped existing file during a dry run."""
        target = tmp_path / "output.txt"
        target.write_text("old", encoding="utf-8")

        result = write_text(
            target,
            "new",
            policy=WritePolicy.SKIP_EXISTING,
            dry_run=True,
        )

        assert result.path == target
        assert result.status is WriteStatus.SKIPPED
        assert target.read_text(encoding="utf-8") == "old"


class TestReadText:
    """Test text-file reading and validation."""

    def test_reads_existing_file(self, tmp_path: Path) -> None:
        """Read an existing UTF-8 text file."""
        target = tmp_path / "README.md"
        target.write_text("# OpenProjectLab\n", encoding="utf-8")

        result = read_text(target)

        assert result == "# OpenProjectLab\n"

    def test_rejects_missing_file(self, tmp_path: Path) -> None:
        """Reject a missing input file."""
        target = tmp_path / "missing.txt"

        with pytest.raises(FileSystemError, match="找不到檔案"):
            read_text(target)

    def test_rejects_directory(self, tmp_path: Path) -> None:
        """Reject a directory as a text-file source."""
        target = tmp_path / "directory"
        target.mkdir()

        with pytest.raises(FileSystemError, match="不是檔案"):
            read_text(target)


class TestCopyFile:
    """Test file copying, overwrite protection, and dry-run behavior."""

    def test_creates_parent_directory(self, tmp_path: Path) -> None:
        """Create missing destination parents while copying."""
        source = tmp_path / "template.md"
        destination = tmp_path / "course" / "week-01" / "README.md"
        source.write_text("template", encoding="utf-8")

        result = copy_file(source, destination)

        assert result == destination
        assert destination.read_text(encoding="utf-8") == "template"

    def test_can_reject_overwrite(self, tmp_path: Path) -> None:
        """Preserve an existing destination when overwrite is disabled."""
        source = tmp_path / "source.txt"
        destination = tmp_path / "destination.txt"
        source.write_text("source", encoding="utf-8")
        destination.write_text("destination", encoding="utf-8")

        with pytest.raises(FileSystemError, match="不允許覆寫"):
            copy_file(source, destination, overwrite=False)

        assert destination.read_text(encoding="utf-8") == "destination"

    def test_rejects_missing_source(self, tmp_path: Path) -> None:
        """Reject a missing source file."""
        source = tmp_path / "missing.txt"
        destination = tmp_path / "destination.txt"

        with pytest.raises(FileSystemError, match="找不到來源檔案"):
            copy_file(source, destination)

    def test_dry_run_does_not_require_source(
        self,
        tmp_path: Path,
    ) -> None:
        """Return the destination without copying during a dry run."""
        source = tmp_path / "missing-source.txt"
        destination = tmp_path / "dry-run" / "destination.txt"

        result = FileSystem.copy_file(
            source,
            destination,
            dry_run=True,
        )

        assert result == destination
        assert not destination.exists()
        assert not destination.parent.exists()


class TestRemoveFile:
    """Test file removal, missing-file handling, and dry runs."""

    def test_deletes_existing_file(self, tmp_path: Path) -> None:
        """Delete an existing file."""
        target = tmp_path / "temporary.txt"
        target.write_text("temporary", encoding="utf-8")

        remove_file(target)

        assert not target.exists()

    def test_ignores_missing_file_by_default(
        self,
        tmp_path: Path,
    ) -> None:
        """Ignore a missing file under the default policy."""
        remove_file(tmp_path / "missing.txt")

    def test_can_reject_missing_file(self, tmp_path: Path) -> None:
        """Raise an error when missing_ok is disabled."""
        with pytest.raises(
            FileSystemError,
            match="找不到要刪除的檔案",
        ):
            remove_file(
                tmp_path / "missing.txt",
                missing_ok=False,
            )

    def test_rejects_directory(self, tmp_path: Path) -> None:
        """Reject a directory passed to the file-removal operation."""
        target = tmp_path / "directory"
        target.mkdir()

        with pytest.raises(FileSystemError, match="拒絕"):
            remove_file(target)

    def test_dry_run_preserves_file(self, tmp_path: Path) -> None:
        """Preserve an existing file during a dry run."""
        target = tmp_path / "preserved.txt"
        target.write_text("content", encoding="utf-8")

        FileSystem.remove_file(target, dry_run=True)

        assert target.exists()


class TestFileSystemCompatibility:
    """Test the stateless FileSystem compatibility interface."""

    def test_class_is_importable(self) -> None:
        """Expose the FileSystem compatibility class."""
        assert FileSystem is not None

    def test_ensure_dir_alias(self, tmp_path: Path) -> None:
        """Create a directory through the legacy ensure_dir alias."""
        target = tmp_path / "legacy" / "directory"

        result = FileSystem.ensure_dir(target)

        assert result == target
        assert target.is_dir()

    def test_mkdir_alias(self, tmp_path: Path) -> None:
        """Create a directory through the legacy mkdir alias."""
        target = tmp_path / "legacy-mkdir"

        result = FileSystem.mkdir(target)

        assert result == target
        assert target.is_dir()

    def test_write_and_read_text(self, tmp_path: Path) -> None:
        """Write and read text through the compatibility class."""
        target = tmp_path / "legacy" / "README.md"
        content = "OPL compatibility test\n"

        result = FileSystem.write_text(target, content)

        assert result.path == target
        assert result.status is WriteStatus.CREATED
        assert FileSystem.read_text(target) == content

    def test_copy_and_remove_file(self, tmp_path: Path) -> None:
        """Copy and remove a file through the compatibility class."""
        source = tmp_path / "source.txt"
        destination = tmp_path / "nested" / "destination.txt"
        source.write_text("content", encoding="utf-8")

        result = FileSystem.copy_file(source, destination)

        assert result == destination
        assert destination.read_text(encoding="utf-8") == "content"

        FileSystem.remove_file(destination)

        assert not destination.exists()

    def test_write_text_dry_run(self, tmp_path: Path) -> None:
        """Return a created result without writing during a dry run."""
        target = tmp_path / "dry-run" / "output.txt"

        result = FileSystem.write_text(
            target,
            "content",
            dry_run=True,
        )

        assert result.path == target
        assert result.status is WriteStatus.CREATED
        assert not target.exists()
        assert not target.parent.exists()
