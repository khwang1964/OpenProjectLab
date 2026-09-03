import hashlib
import json

import pytest

from generator.release_audit_bundle import (
    DEFAULT_SCHEMA_REGISTRY,
    AuditBundleMigrationExecutor,
    AuditBundleMigrationReceiptCodec,
    AuditBundleMigrationReceiptVerifier,
    AuditBundleMigrationRequest,
)
from generator.release_automation import VerificationDocumentError


def legacy_bundle() -> str:
    return json.dumps(
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


def migration() -> tuple[str, str, str]:
    source = legacy_bundle()
    plan = DEFAULT_SCHEMA_REGISTRY.plan("0", "1")
    request = AuditBundleMigrationRequest(
        hashlib.sha256(source.encode()).hexdigest(),
        "1",
        plan.preview_fingerprint,
        True,
    )
    result = AuditBundleMigrationExecutor.execute(request, source)
    return source, result.output_document, result.receipt


def test_receipt_codec_is_strict_and_canonical() -> None:
    _, _, document = migration()
    receipt = AuditBundleMigrationReceiptCodec.decode(document)
    assert AuditBundleMigrationReceiptCodec.encode(receipt) == document
    payload = json.loads(document)
    payload["unknown"] = True
    with pytest.raises(VerificationDocumentError, match="unknown receipt field"):
        AuditBundleMigrationReceiptCodec.decode(
            json.dumps(payload, sort_keys=True, separators=(",", ":"))
        )


def test_verifier_accepts_exact_source_output_plan_bindings() -> None:
    source, output, receipt = migration()
    verification = AuditBundleMigrationReceiptVerifier.verify(source, output, receipt)
    assert verification.is_valid
    assert verification.findings == ()


def test_verifier_reports_stable_source_and_output_mismatches() -> None:
    source, output, receipt = migration()
    payload = json.loads(receipt)
    payload["source_sha256"] = "0" * 64
    payload["output_sha256"] = "f" * 64
    changed = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    verification = AuditBundleMigrationReceiptVerifier.verify(source, output, changed)
    assert not verification.is_valid
    assert tuple(item.path for item in verification.findings) == (
        "$.output_sha256",
        "$.source_sha256",
    )


def test_verifier_reports_plan_and_step_mismatches() -> None:
    source, output, receipt = migration()
    payload = json.loads(receipt)
    payload["plan_fingerprint"] = "0" * 64
    payload["steps"] = []
    changed = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    verification = AuditBundleMigrationReceiptVerifier.verify(source, output, changed)
    assert tuple(item.path for item in verification.findings) == (
        "$.plan_fingerprint",
        "$.steps",
    )
