from __future__ import annotations

import zipfile
from hashlib import sha256
from pathlib import Path

import pytest
import yaml

from generator.core.upgrade import (
    IntegrityError,
    ManifestError,
    PatchEntry,
    UnsafePathError,
    UpgradeConflictError,
    UpgradeManager,
    UpgradeManifest,
)


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def make_package(
    path: Path,
    entries: list[dict],
    payloads: dict[str, bytes],
) -> Path:
    manifest = {
        "schema_version": "1.0",
        "package": "test-patch",
        "version": "1.0.0",
        "description": "test",
        "entries": entries,
    }
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "upgrade-manifest.yaml",
            yaml.safe_dump(manifest, sort_keys=False),
        )
        for name, data in payloads.items():
            archive.writestr(f"payload/{name}", data)
    return path


@pytest.mark.parametrize(
    "path",
    [
        "../escape.txt",
        "/absolute.txt",
        "folder\\file.txt",
        "folder/../file.txt",
        "CON.txt",
    ],
)
def test_patch_entry_rejects_unsafe_paths(path: str) -> None:
    with pytest.raises(UnsafePathError):
        PatchEntry.from_mapping(
            {
                "path": path,
                "operation": "add",
                "sha256": "0" * 64,
            }
        )


def test_manifest_rejects_duplicate_paths(tmp_path: Path) -> None:
    manifest = tmp_path / "upgrade-manifest.yaml"
    manifest.write_text(
        yaml.safe_dump(
            {
                "schema_version": "1.0",
                "package": "duplicate",
                "version": "1.0.0",
                "entries": [
                    {
                        "path": "a.txt",
                        "operation": "add",
                        "sha256": "0" * 64,
                    },
                    {
                        "path": "a.txt",
                        "operation": "delete",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ManifestError, match="重複"):
        UpgradeManifest.load(manifest)


def test_inspect_does_not_change_project(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    package = make_package(
        tmp_path / "patch.zip",
        [
            {
                "path": "new.txt",
                "operation": "add",
                "sha256": digest(b"new"),
            }
        ],
        {"new.txt": b"new"},
    )

    plan = UpgradeManager(project).inspect(package)

    assert plan.added == ["new.txt"]
    assert not (project / "new.txt").exists()


def test_apply_add_modify_delete_and_backup(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / "modify.txt").write_text("old", encoding="utf-8")
    (project / "delete.txt").write_text("delete", encoding="utf-8")

    package = make_package(
        tmp_path / "patch.zip",
        [
            {
                "path": "add.txt",
                "operation": "add",
                "sha256": digest(b"added"),
            },
            {
                "path": "modify.txt",
                "operation": "modify",
                "sha256": digest(b"modified"),
                "source_sha256": digest(b"old"),
            },
            {
                "path": "delete.txt",
                "operation": "delete",
                "source_sha256": digest(b"delete"),
            },
        ],
        {
            "add.txt": b"added",
            "modify.txt": b"modified",
        },
    )

    result = UpgradeManager(project).apply(package)

    assert (project / "add.txt").read_bytes() == b"added"
    assert (project / "modify.txt").read_bytes() == b"modified"
    assert not (project / "delete.txt").exists()

    assert (result.backup_dir / "modify.txt").read_text(encoding="utf-8") == "old"
    assert (result.backup_dir / "delete.txt").read_text(encoding="utf-8") == "delete"
    assert (result.backup_dir / "upgrade-report.yaml").is_file()


def test_apply_rejects_conflict_by_default(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / "existing.txt").write_text("existing", encoding="utf-8")

    package = make_package(
        tmp_path / "patch.zip",
        [
            {
                "path": "existing.txt",
                "operation": "add",
                "sha256": digest(b"replacement"),
            }
        ],
        {"existing.txt": b"replacement"},
    )

    with pytest.raises(UpgradeConflictError):
        UpgradeManager(project).apply(package)


def test_source_sha256_detects_local_modification(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / "file.txt").write_text("local edit", encoding="utf-8")

    package = make_package(
        tmp_path / "patch.zip",
        [
            {
                "path": "file.txt",
                "operation": "modify",
                "sha256": digest(b"new"),
                "source_sha256": digest(b"expected old"),
            }
        ],
        {"file.txt": b"new"},
    )

    plan = UpgradeManager(project).inspect(package)

    assert plan.has_conflicts
    assert "來源版本 SHA256 不符：file.txt" in plan.conflicts


def test_payload_integrity_failure(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    package = make_package(
        tmp_path / "patch.zip",
        [
            {
                "path": "file.txt",
                "operation": "add",
                "sha256": digest(b"expected"),
            }
        ],
        {"file.txt": b"tampered"},
    )

    with pytest.raises(IntegrityError):
        UpgradeManager(project).inspect(package)


def test_invalid_zip_is_rejected(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    package = tmp_path / "invalid.zip"
    package.write_text("not a zip", encoding="utf-8")

    with pytest.raises(Exception, match="有效 ZIP"):
        UpgradeManager(project).inspect(package)
