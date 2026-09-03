import hashlib
import json

import pytest

from generator.release_audit_bundle import (
    DEFAULT_SCHEMA_REGISTRY,
    AuditBundleMigrationError,
    AuditBundleMigrationExecutor,
    AuditBundleMigrationRequest,
    VerificationAuditBundleCodec,
)


def _legacy_bundle() -> str:
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


def _request(document: str) -> AuditBundleMigrationRequest:
    plan = DEFAULT_SCHEMA_REGISTRY.plan("0", "1")
    return AuditBundleMigrationRequest(
        hashlib.sha256(document.encode()).hexdigest(),
        "1",
        plan.preview_fingerprint,
        True,
    )


def test_executor_produces_deterministic_verified_output_and_receipt() -> None:
    source = _legacy_bundle()
    first = AuditBundleMigrationExecutor.execute(_request(source), source)
    second = AuditBundleMigrationExecutor.execute(_request(source), source)
    assert first == second
    assert first.steps == ("upgrade-0-to-1",)
    assert VerificationAuditBundleCodec.decode(first.output_document).schema_version == "1"
    assert first.output_sha256 == hashlib.sha256(first.output_document.encode()).hexdigest()
    assert json.loads(first.receipt)["output_sha256"] == first.output_sha256


def test_executor_requires_source_identity_and_exact_preview_fingerprint() -> None:
    source = _legacy_bundle()
    request = _request(source)
    with pytest.raises(AuditBundleMigrationError, match="source identity mismatch"):
        AuditBundleMigrationExecutor.execute(
            AuditBundleMigrationRequest("0" * 64, "1", request.preview_fingerprint, True),
            source,
        )
    with pytest.raises(AuditBundleMigrationError, match="accepted plan mismatch"):
        AuditBundleMigrationExecutor.execute(
            AuditBundleMigrationRequest(request.source_sha256, "1", "0" * 64, True),
            source,
        )


def test_executor_requires_distinct_output_intent() -> None:
    source = _legacy_bundle()
    request = _request(source)
    with pytest.raises(AuditBundleMigrationError, match="distinct output"):
        AuditBundleMigrationExecutor.execute(
            AuditBundleMigrationRequest(
                request.source_sha256,
                request.target_schema,
                request.preview_fingerprint,
                False,
            ),
            source,
        )


def test_executor_fails_closed_for_unknown_step_registry() -> None:
    source = _legacy_bundle()
    with pytest.raises(AuditBundleMigrationError, match="unknown migration step"):
        AuditBundleMigrationExecutor.execute(_request(source), source, step_registry=())
