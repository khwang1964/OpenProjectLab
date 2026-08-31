from __future__ import annotations

import json

import pytest

from generator.release_automation import (
    VerificationDocumentError,
    VerificationFinding,
    VerificationFindingStage,
    VerificationReport,
    VerificationReportCodec,
    VerificationReportEncoder,
    VerificationReportInspectionRenderer,
    VerificationReportInspector,
)


def _failed_report() -> VerificationReport:
    finding = VerificationFinding(
        VerificationFindingStage.COLLECTION,
        "collection_failed",
        "offline fixture",
    )
    return VerificationReport(None, None, None, (finding,))


def test_report_encoder_is_canonical_and_round_trips() -> None:
    report = _failed_report()
    document = VerificationReportEncoder.encode(report)
    assert document.endswith("\n") and not document.endswith("\n\n")
    assert VerificationReportCodec.decode(document) == report
    assert VerificationReportEncoder.encode(VerificationReportCodec.decode(document)) == document


def test_report_codec_rejects_unknown_duplicate_and_contradictory_documents() -> None:
    document = VerificationReportEncoder.encode(_failed_report())
    payload = json.loads(document)
    payload["unknown"] = True
    with pytest.raises(VerificationDocumentError):
        VerificationReportCodec.decode(json.dumps(payload))
    duplicate = document.replace('"status":"failed"', '"status":"failed","status":"failed"')
    with pytest.raises(VerificationDocumentError):
        VerificationReportCodec.decode(duplicate)
    payload.pop("unknown")
    payload["status"] = "passed"
    with pytest.raises(VerificationDocumentError):
        VerificationReportCodec.decode(json.dumps(payload))


def test_report_inspection_is_offline_and_deterministic() -> None:
    document = VerificationReportEncoder.encode(_failed_report())
    inspection = VerificationReportInspector.inspect(document)
    assert inspection.status == "failed"
    assert VerificationReportInspectionRenderer.to_json(inspection) == document
    assert "status: failed" in VerificationReportInspectionRenderer.to_text(inspection)
