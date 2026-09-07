import json
from pathlib import Path

import pytest

from generator.readiness_assembly import (
    BoundedEvidenceReader,
    ReadinessEvidenceManifestCodec,
    ReleaseReadinessSnapshotAssembler,
)
from generator.release_automation import VerificationDocumentError

REVISION = "a" * 40


def manifest(files: list[str]) -> str:
    return json.dumps(
        {"evidence_files": files, "repository": "khwang1964/OpenProjectLab", "revision": REVISION},
        sort_keys=True,
        separators=(",", ":"),
    )


def evidence() -> dict[str, object]:
    return {
        "audit_chain_accepted": True,
        "collected_at": "2026-09-08T00:00:00Z",
        "coverage_percent": 90.0,
        "coverage_threshold": 67.0,
        "focused_failed": 0,
        "focused_passed": 10,
        "known_limitations": [],
        "regression_failed": 0,
        "regression_passed": 2700,
        "release_blockers": [],
        "required_checks_passed": True,
        "supported_surfaces": ["cli", "sdk"],
    }


def test_manifest_is_canonical_strict_and_immutable() -> None:
    decoded = ReadinessEvidenceManifestCodec.decode(manifest(["a.json"]))
    assert ReadinessEvidenceManifestCodec.encode(decoded) == manifest(["a.json"])
    with pytest.raises((VerificationDocumentError, json.JSONDecodeError)):
        ReadinessEvidenceManifestCodec.decode(manifest(["a.json"])[:-1] + ',"unknown":1}')


@pytest.mark.parametrize("path", ("../a.json", "/a.json", "a\\b.json"))
def test_manifest_rejects_unsafe_paths(path: str) -> None:
    with pytest.raises(VerificationDocumentError):
        ReadinessEvidenceManifestCodec.decode(manifest([path]))


def test_reader_rejects_symlink_and_assembler_is_revision_bound(tmp_path: Path) -> None:
    document = tmp_path / "evidence.json"
    document.write_text(json.dumps(evidence()), encoding="utf-8")
    reader = BoundedEvidenceReader(tmp_path)
    documents = reader.read_all(("evidence.json",))
    result = ReleaseReadinessSnapshotAssembler.assemble(
        ReadinessEvidenceManifestCodec.decode(manifest(["evidence.json"])), documents
    )
    assert result.is_valid and result.snapshot is not None
    assert result.snapshot.revision == REVISION
    link = tmp_path / "link.json"
    try:
        link.symlink_to(document)
    except OSError:
        pytest.skip("symlink unavailable")
    with pytest.raises(VerificationDocumentError):
        reader.read_all(("link.json",))


def test_conflicting_or_incomplete_evidence_fails_closed() -> None:
    decoded = ReadinessEvidenceManifestCodec.decode(manifest(["a.json", "b.json"]))
    conflict = ReleaseReadinessSnapshotAssembler.assemble(
        decoded, ('{"focused_passed":1}', '{"focused_passed":2}')
    )
    assert not conflict.is_valid and conflict.findings[0].reason == "CONFLICTING_EVIDENCE"
    incomplete = ReleaseReadinessSnapshotAssembler.assemble(
        ReadinessEvidenceManifestCodec.decode(manifest(["a.json"])), ("{}",)
    )
    assert not incomplete.is_valid and incomplete.findings[0].reason == "INCOMPLETE_EVIDENCE"


def test_cli_exposes_explicit_bounded_read_only_assembly() -> None:
    from generator.cli.main import build_parser

    args = build_parser().parse_args(
        [
            "release-evidence",
            "readiness",
            "assemble",
            "--manifest",
            "m.json",
            "--input-root",
            "evidence",
            "--format",
            "json",
        ]
    )
    assert args.manifest == "m.json" and args.input_root == "evidence"
    assert callable(args.command_handler)
