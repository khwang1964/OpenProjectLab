from __future__ import annotations

import shutil
import tempfile
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any

import yaml


class UpgradeError(RuntimeError):
    """Base exception for upgrade failures."""


class ManifestError(UpgradeError):
    """Raised when an upgrade manifest is invalid."""


class IntegrityError(UpgradeError):
    """Raised when a payload checksum is invalid."""


class UnsafePathError(UpgradeError):
    """Raised when an upgrade path is unsafe."""


class UpgradeConflictError(UpgradeError):
    """Raised when the current project state conflicts with the patch."""


class Operation(StrEnum):
    ADD = "add"
    MODIFY = "modify"
    DELETE = "delete"


@dataclass(frozen=True, slots=True)
class PatchEntry:
    path: str
    operation: Operation
    sha256: str | None = None
    source_sha256: str | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> PatchEntry:
        if not isinstance(data, dict):
            raise ManifestError("Manifest entry 必須是 mapping")

        raw_path = data.get("path")
        raw_operation = data.get("operation")
        raw_sha256 = data.get("sha256")
        raw_source_sha256 = data.get("source_sha256")

        if not isinstance(raw_path, str) or not raw_path.strip():
            raise ManifestError("entry.path 必須是非空字串")

        path = validate_relative_path(raw_path)

        try:
            operation = Operation(raw_operation)
        except ValueError as exc:
            raise ManifestError(f"不支援的 operation：{raw_operation!r}") from exc

        if operation in {Operation.ADD, Operation.MODIFY}:
            validate_sha256(raw_sha256, f"{path}.sha256")
        elif raw_sha256 is not None:
            raise ManifestError(f"delete entry 不可指定 sha256：{path}")

        if raw_source_sha256 is not None:
            validate_sha256(raw_source_sha256, f"{path}.source_sha256")

        return cls(
            path=path,
            operation=operation,
            sha256=raw_sha256.lower() if raw_sha256 else None,
            source_sha256=(raw_source_sha256.lower() if raw_source_sha256 else None),
        )


@dataclass(frozen=True, slots=True)
class UpgradeManifest:
    schema_version: str
    package: str
    version: str
    description: str
    entries: tuple[PatchEntry, ...]

    @classmethod
    def load(cls, path: Path) -> UpgradeManifest:
        if not path.is_file():
            raise ManifestError(f"找不到 upgrade manifest：{path}")

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ManifestError("Upgrade manifest 頂層必須是 mapping")

        schema_version = data.get("schema_version")
        package = data.get("package")
        version = data.get("version")
        description = data.get("description", "")
        raw_entries = data.get("entries")

        if schema_version != "1.0":
            raise ManifestError(f"不支援的 schema_version：{schema_version!r}")
        if not isinstance(package, str) or not package.strip():
            raise ManifestError("package 必須是非空字串")
        if not isinstance(version, str) or not version.strip():
            raise ManifestError("version 必須是非空字串")
        if not isinstance(description, str):
            raise ManifestError("description 必須是字串")
        if not isinstance(raw_entries, list) or not raw_entries:
            raise ManifestError("entries 必須是非空 list")

        entries = tuple(PatchEntry.from_mapping(item) for item in raw_entries)
        paths = [entry.path for entry in entries]

        if len(paths) != len(set(paths)):
            raise ManifestError("Manifest 不可包含重複 path")

        return cls(
            schema_version=schema_version,
            package=package,
            version=version,
            description=description,
            entries=entries,
        )


@dataclass(slots=True)
class UpgradePlan:
    package: str
    version: str
    added: list[str] = field(default_factory=list)
    modified: list[str] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    @property
    def change_count(self) -> int:
        return len(self.added) + len(self.modified) + len(self.deleted)


@dataclass(frozen=True, slots=True)
class UpgradeResult:
    package: str
    version: str
    backup_dir: Path
    changed_paths: tuple[str, ...]


def validate_sha256(value: Any, field_name: str) -> None:
    if not isinstance(value, str) or len(value) != 64:
        raise ManifestError(f"{field_name} 必須是 64 字元 SHA256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ManifestError(f"{field_name} 不是有效十六進位") from exc


def validate_relative_path(raw_path: str) -> str:
    if "\\" in raw_path:
        raise UnsafePathError(f"Manifest path 必須使用 '/'：{raw_path}")

    path = PurePosixPath(raw_path)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise UnsafePathError(f"不安全的相對路徑：{raw_path}")

    normalized = path.as_posix()
    if normalized in {"", "."}:
        raise UnsafePathError("Manifest path 不可為空")

    reserved = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
    for part in path.parts:
        if Path(part).stem.upper() in reserved:
            raise UnsafePathError(f"Manifest path 使用 Windows 保留名稱：{raw_path}")

    return normalized


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class UpgradeManager:
    MANIFEST_NAME = "upgrade-manifest.yaml"
    PAYLOAD_DIR = "payload"

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root.resolve()

    def inspect(self, package_path: Path) -> UpgradePlan:
        with self._extract(package_path) as extracted:
            manifest = UpgradeManifest.load(extracted / self.MANIFEST_NAME)
            self._verify_payload(extracted, manifest)
            return self._build_plan(manifest)

    def apply(
        self,
        package_path: Path,
        *,
        allow_conflicts: bool = False,
        backup_root: Path | None = None,
    ) -> UpgradeResult:
        with self._extract(package_path) as extracted:
            manifest = UpgradeManifest.load(extracted / self.MANIFEST_NAME)
            self._verify_payload(extracted, manifest)
            plan = self._build_plan(manifest)

            if plan.has_conflicts and not allow_conflicts:
                details = "\n".join(f"- {item}" for item in plan.conflicts)
                raise UpgradeConflictError(f"Upgrade plan 包含衝突：\n{details}")

            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            backups = (
                backup_root.resolve()
                if backup_root is not None
                else self.project_root / ".opl" / "backups"
            )
            backup_dir = backups / (f"{manifest.package}-{manifest.version}-{timestamp}")
            backup_dir.mkdir(parents=True, exist_ok=False)

            journal: list[tuple[str, Path, bool]] = []
            changed: list[str] = []

            try:
                for entry in manifest.entries:
                    target = self._target(entry.path)
                    existed = target.exists()

                    if existed:
                        backup_target = backup_dir / entry.path
                        backup_target.parent.mkdir(
                            parents=True,
                            exist_ok=True,
                        )
                        if target.is_dir():
                            shutil.copytree(target, backup_target)
                        else:
                            shutil.copy2(target, backup_target)

                    journal.append((entry.path, target, existed))

                    if entry.operation is Operation.DELETE:
                        self._remove(target)
                    else:
                        source = extracted / self.PAYLOAD_DIR / entry.path
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source, target)

                    changed.append(entry.path)

                self._write_report(backup_dir, manifest, plan)
            except Exception:
                self._rollback(journal, backup_dir)
                raise

            return UpgradeResult(
                package=manifest.package,
                version=manifest.version,
                backup_dir=backup_dir,
                changed_paths=tuple(changed),
            )

    def _build_plan(self, manifest: UpgradeManifest) -> UpgradePlan:
        plan = UpgradePlan(
            package=manifest.package,
            version=manifest.version,
        )

        for entry in manifest.entries:
            target = self._target(entry.path)

            if entry.operation is Operation.ADD:
                if target.exists():
                    plan.conflicts.append(f"add 目標已存在：{entry.path}")
                else:
                    plan.added.append(entry.path)

            elif entry.operation is Operation.MODIFY:
                if not target.exists():
                    plan.conflicts.append(f"modify 目標不存在：{entry.path}")
                    continue

                if entry.source_sha256:
                    actual_source = file_sha256(target)
                    if actual_source != entry.source_sha256:
                        plan.conflicts.append(f"來源版本 SHA256 不符：{entry.path}")
                        continue

                if target.is_file() and file_sha256(target) == entry.sha256:
                    plan.unchanged.append(entry.path)
                else:
                    plan.modified.append(entry.path)

            else:
                if not target.exists():
                    plan.unchanged.append(entry.path)
                    continue

                if entry.source_sha256:
                    actual_source = file_sha256(target)
                    if actual_source != entry.source_sha256:
                        plan.conflicts.append(f"刪除來源 SHA256 不符：{entry.path}")
                        continue

                plan.deleted.append(entry.path)

        return plan

    def _verify_payload(
        self,
        extracted: Path,
        manifest: UpgradeManifest,
    ) -> None:
        for entry in manifest.entries:
            if entry.operation is Operation.DELETE:
                continue

            payload = extracted / self.PAYLOAD_DIR / entry.path
            if not payload.is_file():
                raise IntegrityError(f"Package payload 缺少檔案：{entry.path}")

            actual = file_sha256(payload)
            if actual != entry.sha256:
                raise IntegrityError(f"Payload SHA256 不符：{entry.path}")

    def _target(self, relative_path: str) -> Path:
        target = (self.project_root / relative_path).resolve()
        try:
            target.relative_to(self.project_root)
        except ValueError as exc:
            raise UnsafePathError(f"目標路徑逃逸 project root：{relative_path}") from exc
        return target

    @staticmethod
    def _remove(path: Path) -> None:
        if not path.exists():
            return
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    def _rollback(
        self,
        journal: list[tuple[str, Path, bool]],
        backup_dir: Path,
    ) -> None:
        for relative_path, target, existed in reversed(journal):
            self._remove(target)
            if not existed:
                continue

            backup = backup_dir / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            if backup.is_dir():
                shutil.copytree(backup, target)
            else:
                shutil.copy2(backup, target)

    @staticmethod
    def _write_report(
        backup_dir: Path,
        manifest: UpgradeManifest,
        plan: UpgradePlan,
    ) -> None:
        report = {
            "schema_version": "1.0",
            "package": manifest.package,
            "version": manifest.version,
            "description": manifest.description,
            "added": plan.added,
            "modified": plan.modified,
            "deleted": plan.deleted,
            "unchanged": plan.unchanged,
            "conflicts": plan.conflicts,
        }
        (backup_dir / "upgrade-report.yaml").write_text(
            yaml.safe_dump(
                report,
                allow_unicode=True,
                sort_keys=False,
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _extract(package_path: Path):
        if not package_path.is_file():
            raise UpgradeError(f"找不到 upgrade package：{package_path}")
        if not zipfile.is_zipfile(package_path):
            raise UpgradeError(f"不是有效 ZIP：{package_path}")

        temporary = tempfile.TemporaryDirectory(prefix="opl-upgrade-")

        class ExtractedContext:
            def __enter__(self) -> Path:
                root = Path(temporary.name)
                with zipfile.ZipFile(package_path) as archive:
                    for member in archive.infolist():
                        name = member.filename.rstrip("/")
                        if name:
                            validate_relative_path(name)
                    archive.extractall(root)
                return root

            def __exit__(self, exc_type, exc, tb) -> None:
                temporary.cleanup()

        return ExtractedContext()
