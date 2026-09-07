"""Bounded offline assembly of v1.4.0 release-readiness snapshots."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from generator.release_automation import VerificationDocumentError
from generator.release_readiness import (
    ReleaseReadinessStabilitySnapshot,
    ReleaseReadinessStabilitySnapshotCodec,
)

MAX_EVIDENCE_FILES = 32
MAX_EVIDENCE_DOCUMENT_BYTES = 1024 * 1024
MAX_EVIDENCE_AGGREGATE_BYTES = 8 * 1024 * 1024
_REVISION = re.compile(r"[0-9a-f]{40}")


@dataclass(frozen=True, slots=True)
class ReadinessEvidenceManifest:
    repository: str
    revision: str
    evidence_files: tuple[str, ...]


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise VerificationDocumentError(f"duplicate field: {key}")
        result[key] = value
    return result


def _json_object(document: str) -> dict[str, Any]:
    try:
        value = json.loads(document, object_pairs_hook=_pairs)
    except (json.JSONDecodeError, TypeError) as error:
        raise VerificationDocumentError("document must be valid JSON") from error
    if not isinstance(value, dict):
        raise VerificationDocumentError("document must be one JSON object")
    return value


class ReadinessEvidenceManifestCodec:
    FIELDS = frozenset(("evidence_files", "repository", "revision"))

    @classmethod
    def decode(cls, document: str) -> ReadinessEvidenceManifest:
        value = _json_object(document)
        unknown = set(value) - cls.FIELDS
        missing = cls.FIELDS - set(value)
        if unknown:
            raise VerificationDocumentError(f"unknown fields: {', '.join(sorted(unknown))}")
        if missing:
            raise VerificationDocumentError(f"missing fields: {', '.join(sorted(missing))}")
        repository = value["repository"]
        revision = value["revision"]
        files = value["evidence_files"]
        if not isinstance(repository, str) or not repository:
            raise VerificationDocumentError("$.repository must be a nonempty string")
        if not isinstance(revision, str) or not _REVISION.fullmatch(revision):
            raise VerificationDocumentError("$.revision must be a lowercase 40-character revision")
        if not isinstance(files, list) or not all(isinstance(item, str) for item in files):
            raise VerificationDocumentError("$.evidence_files must be an array of paths")
        evidence_files = tuple(files)
        if not evidence_files or len(evidence_files) > MAX_EVIDENCE_FILES:
            raise VerificationDocumentError("$.evidence_files has an invalid file count")
        if evidence_files != tuple(sorted(set(evidence_files))):
            raise VerificationDocumentError("$.evidence_files must be sorted and unique")
        for index, item in enumerate(evidence_files):
            path = PurePosixPath(item)
            if not item or path.is_absolute() or ".." in path.parts or "\\" in item:
                raise VerificationDocumentError(f"$.evidence_files[{index}] is unsafe")
        return ReadinessEvidenceManifest(repository, revision, evidence_files)

    @staticmethod
    def encode(manifest: ReadinessEvidenceManifest) -> str:
        return json.dumps(
            {
                "evidence_files": list(manifest.evidence_files),
                "repository": manifest.repository,
                "revision": manifest.revision,
            },
            sort_keys=True,
            separators=(",", ":"),
        )


@dataclass(frozen=True, slots=True, order=True)
class ReadinessAssemblyFinding:
    path: str
    reason: str
    message: str


@dataclass(frozen=True, slots=True)
class ReadinessAssemblyResult:
    snapshot: ReleaseReadinessStabilitySnapshot | None
    findings: tuple[ReadinessAssemblyFinding, ...]

    @property
    def is_valid(self) -> bool:
        return self.snapshot is not None and not self.findings


class BoundedEvidenceReader:
    def __init__(self, input_root: Path) -> None:
        self._root = input_root.resolve(strict=True)
        if not self._root.is_dir():
            raise VerificationDocumentError("input root must be a directory")

    def read_all(self, paths: tuple[str, ...]) -> tuple[str, ...]:
        documents: list[str] = []
        total = 0
        for index, relative in enumerate(paths):
            candidate = self._root.joinpath(*PurePosixPath(relative).parts)
            if candidate.is_symlink():
                raise VerificationDocumentError(f"$.evidence_files[{index}] must not be a symlink")
            resolved = candidate.resolve(strict=True)
            if os.path.commonpath((self._root, resolved)) != str(self._root):
                raise VerificationDocumentError(f"$.evidence_files[{index}] escapes input root")
            with resolved.open("rb") as stream:
                data = stream.read(MAX_EVIDENCE_DOCUMENT_BYTES + 1)
            if len(data) > MAX_EVIDENCE_DOCUMENT_BYTES:
                raise VerificationDocumentError(f"$.evidence_files[{index}] exceeds byte limit")
            total += len(data)
            if total > MAX_EVIDENCE_AGGREGATE_BYTES:
                raise VerificationDocumentError("evidence exceeds aggregate byte limit")
            documents.append(data.decode("utf-8"))
        return tuple(documents)


class ReleaseReadinessSnapshotAssembler:
    @staticmethod
    def assemble(
        manifest: ReadinessEvidenceManifest, documents: tuple[str, ...]
    ) -> ReadinessAssemblyResult:
        findings: list[ReadinessAssemblyFinding] = []
        values: dict[str, Any] = {}
        for index, document in enumerate(documents):
            try:
                evidence = _json_object(document)
            except VerificationDocumentError as error:
                findings.append(
                    ReadinessAssemblyFinding(
                        f"$.evidence_files[{index}]", "INVALID_DOCUMENT", str(error)
                    )
                )
                continue
            for field, value in evidence.items():
                if field in values:
                    findings.append(
                        ReadinessAssemblyFinding(
                            f"$.{field}",
                            "CONFLICTING_EVIDENCE",
                            "field occurs in more than one document",
                        )
                    )
                else:
                    values[field] = value
        values.setdefault("repository", manifest.repository)
        values.setdefault("revision", manifest.revision)
        values.setdefault("observed_revision", manifest.revision)
        if (
            values.get("repository") != manifest.repository
            or values.get("revision") != manifest.revision
        ):
            findings.append(
                ReadinessAssemblyFinding(
                    "$.revision", "REVISION_MISMATCH", "evidence does not match manifest identity"
                )
            )
        snapshot = None
        if not findings:
            try:
                snapshot = ReleaseReadinessStabilitySnapshotCodec.decode(json.dumps(values))
            except VerificationDocumentError as error:
                findings.append(ReadinessAssemblyFinding("$", "INCOMPLETE_EVIDENCE", str(error)))
        ordered = tuple(sorted(findings))
        return ReadinessAssemblyResult(None if ordered else snapshot, ordered)
