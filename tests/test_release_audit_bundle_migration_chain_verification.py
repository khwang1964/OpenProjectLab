import hashlib
import json

import pytest

from generator.release_audit_bundle import (
    DEFAULT_SCHEMA_REGISTRY,
    AuditBundleMigrationChainManifest,
    AuditBundleMigrationChainManifestCodec,
    AuditBundleMigrationChainVerifier,
    AuditBundleMigrationExecutor,
    AuditBundleMigrationRequest,
)
from generator.release_automation import VerificationDocumentError


def evidence() -> tuple[str, str, str, str]:
    source = json.dumps(
        {
            "metadata": {},
            "report_document": "{}",
            "report_sha256": "1" * 64,
            "request_document": "{}",
            "request_sha256": "0" * 64,
            "schema_version": "0",
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    plan = DEFAULT_SCHEMA_REGISTRY.plan("0", "1")
    request = AuditBundleMigrationRequest(
        hashlib.sha256(source.encode()).hexdigest(), "1", plan.preview_fingerprint, True
    )
    result = AuditBundleMigrationExecutor.execute(request, source)
    manifest = AuditBundleMigrationChainManifest(
        "1",
        hashlib.sha256(source.encode()).hexdigest(),
        result.output_sha256,
        (hashlib.sha256(result.receipt.encode()).hexdigest(),),
    )
    return (
        source,
        result.output_document,
        result.receipt,
        (AuditBundleMigrationChainManifestCodec.encode(manifest)),
    )


def test_manifest_codec_is_strict_canonical_and_nonempty() -> None:
    *_, document = evidence()
    manifest = AuditBundleMigrationChainManifestCodec.decode(document)
    assert AuditBundleMigrationChainManifestCodec.encode(manifest) == document
    payload = json.loads(document)
    payload["unknown"] = True
    with pytest.raises(VerificationDocumentError, match="unknown chain field"):
        AuditBundleMigrationChainManifestCodec.decode(
            json.dumps(payload, sort_keys=True, separators=(",", ":"))
        )


def test_verifier_accepts_exact_ordered_chain() -> None:
    source, output, receipt, manifest = evidence()
    verification = AuditBundleMigrationChainVerifier.verify(manifest, (source, output), (receipt,))
    assert verification.is_valid
    assert verification.findings == ()


def test_verifier_reports_count_and_terminal_mismatches() -> None:
    source, output, receipt, manifest = evidence()
    count = AuditBundleMigrationChainVerifier.verify(manifest, (source,), (receipt,))
    assert tuple(item.path for item in count.findings) == (
        "$.bundles",
        "$.final_bundle_sha256",
    )
    payload = json.loads(manifest)
    payload["initial_bundle_sha256"] = "0" * 64
    changed = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    terminal = AuditBundleMigrationChainVerifier.verify(changed, (source, output), (receipt,))
    assert not terminal.is_valid
    assert "$.initial_bundle_sha256" in tuple(item.path for item in terminal.findings)


def test_manifest_rejects_duplicate_receipt_identities() -> None:
    *_, document = evidence()
    payload = json.loads(document)
    payload["receipt_sha256"] *= 2
    with pytest.raises(VerificationDocumentError, match="duplicate receipt identity"):
        AuditBundleMigrationChainManifestCodec.decode(
            json.dumps(payload, sort_keys=True, separators=(",", ":"))
        )
