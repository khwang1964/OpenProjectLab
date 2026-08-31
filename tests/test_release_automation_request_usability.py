from __future__ import annotations

import json

import pytest

from generator.release_automation import (
    TestEvidence as EvidenceCounts,
)
from generator.release_automation import (
    VerificationDocumentError,
    VerificationRequest,
    VerificationRequestCodec,
    VerificationRequestEncoder,
    VerificationRequestInspectionRenderer,
    VerificationRequestInspector,
)

SHA = "a" * 40


def _request() -> VerificationRequest:
    return VerificationRequest("khwang1964/OpenProjectLab", "main", SHA, 295, EvidenceCounts(19))


def test_encoder_is_canonical_and_round_trips() -> None:
    document = VerificationRequestEncoder.encode(_request())
    assert document.endswith("\n") and not document.endswith("\n\n")
    assert VerificationRequestCodec.decode(document) == _request()
    assert document == VerificationRequestEncoder.encode(_request())


def test_encoder_rejects_wrong_or_incomplete_requests() -> None:
    with pytest.raises(TypeError):
        VerificationRequestEncoder.encode(object())  # type: ignore[arg-type]
    incomplete = VerificationRequest("x/y", "main", SHA, 1, None)
    with pytest.raises(VerificationDocumentError):
        VerificationRequestEncoder.encode(incomplete)


def test_inspector_and_renderers_are_deterministic() -> None:
    inspection = VerificationRequestInspector.inspect(VerificationRequestEncoder.encode(_request()))
    payload = json.loads(VerificationRequestInspectionRenderer.to_json(inspection))
    assert payload["status"] == "valid"
    assert payload["request"]["pull_request_number"] == 295
    assert VerificationRequestInspectionRenderer.to_text(inspection).startswith("status: valid\n")
