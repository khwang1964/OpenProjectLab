from dataclasses import replace

from generator.release_audit_bundle import (
    VerificationAuditBundleBuilder,
    VerificationAuditBundleCodec,
    VerificationAuditBundleValidator,
)
from generator.release_automation import VerificationReportEncoder, VerificationRequestEncoder
from tests.test_release_automation_report_usability import _failed_report
from tests.test_release_automation_request_usability import _request


def _bundle():
    return VerificationAuditBundleBuilder.build(
        VerificationRequestEncoder.encode(_request()),
        VerificationReportEncoder.encode(_failed_report()),
        {"source": "test"},
    )


def test_bundle_codec_is_canonical_and_round_trips() -> None:
    bundle = _bundle()
    document = VerificationAuditBundleCodec.encode(bundle)
    assert VerificationAuditBundleCodec.decode(document) == bundle
    assert document == VerificationAuditBundleCodec.encode(bundle)


def test_bundle_validation_recomputes_fingerprints() -> None:
    bundle = replace(_bundle(), request_sha256="0" * 64)
    validation = VerificationAuditBundleValidator.validate(bundle)
    assert not validation.is_valid
    assert [item.path for item in validation.findings] == ["$.request_sha256"]


def test_identical_inputs_produce_identical_bundles() -> None:
    assert _bundle() == _bundle()
