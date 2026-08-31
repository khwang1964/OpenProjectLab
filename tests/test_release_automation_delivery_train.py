from __future__ import annotations

import json
from dataclasses import FrozenInstanceError

import pytest

from generator.release_automation import (
    CheckConclusion,
    CheckEvidence,
    ReadOnlyVerificationInvoker,
    ReleaseEvidence,
    RepositoryObservation,
    VerificationDocumentError,
    VerificationFinding,
    VerificationFindingStage,
    VerificationReport,
    VerificationReportRenderer,
    VerificationRequest,
    VerificationRequestCodec,
    VerificationRuntime,
)
from generator.release_automation import (
    TestEvidence as EvidenceCounts,
)

SHA = "a" * 40


def _document(**changes: object) -> str:
    payload = {
        "schema_version": 1,
        "expected_repository": "khwang1964/OpenProjectLab",
        "expected_branch": "main",
        "expected_sha": SHA,
        "pull_request_number": 290,
        "focused_tests": {"passed": 28, "failed": 0, "skipped": 0, "deselected": 0},
    }
    payload.update(changes)
    return json.dumps(payload)


def test_request_codec_decodes_exact_schema() -> None:
    request = VerificationRequestCodec.decode(_document())
    assert request.pull_request_number == 290
    assert request.focused_tests == EvidenceCounts(28)
    with pytest.raises(FrozenInstanceError):
        request.pull_request_number = 1  # type: ignore[misc]


@pytest.mark.parametrize(
    "document",
    [
        "[]",
        "not-json",
        _document(schema_version=True),
        _document(schema_version=2),
        _document(pull_request_number="290"),
        _document(extra=True),
        _document(focused_tests={"passed": 1}),
        _document(focused_tests={"passed": True, "failed": 0, "skipped": 0, "deselected": 0}),
        _document()[:-1] + ',"schema_version":1}',
    ],
)
def test_request_codec_rejects_invalid_documents(document: str) -> None:
    with pytest.raises(VerificationDocumentError):
        VerificationRequestCodec.decode(document)


class RecordingOrchestrator:
    def __init__(self, report: VerificationReport) -> None:
        self.report = report
        self.calls = []

    def verify(self, request: VerificationRequest) -> VerificationReport:
        self.calls.append(request)
        return self.report


def test_invoker_delegates_once_and_returns_same_report() -> None:
    report = VerificationReport(None, None, None, ())
    orchestrator = RecordingOrchestrator(report)
    runtime = object.__new__(VerificationRuntime)
    object.__setattr__(runtime, "orchestrator", orchestrator)
    invoker = ReadOnlyVerificationInvoker(runtime)
    request = VerificationRequestCodec.decode(_document())
    assert invoker.invoke(request) is report
    assert orchestrator.calls == [request]


def test_invoker_rejects_wrong_request_before_delegation() -> None:
    report = VerificationReport(None, None, None, ())
    orchestrator = RecordingOrchestrator(report)
    runtime = object.__new__(VerificationRuntime)
    object.__setattr__(runtime, "orchestrator", orchestrator)
    with pytest.raises(TypeError):
        ReadOnlyVerificationInvoker(runtime).invoke(object())  # type: ignore[arg-type]
    assert orchestrator.calls == []


def test_renderers_are_deterministic_and_status_consistent() -> None:
    repository = RepositoryObservation(
        "khwang1964/OpenProjectLab", "main", SHA, SHA, "https://github.com/x/y.git", True
    )
    evidence = ReleaseEvidence(
        "khwang1964/OpenProjectLab",
        "main",
        SHA,
        (CheckEvidence("quality", CheckConclusion.PASSED),),
        EvidenceCounts(28),
    )
    report = VerificationReport(repository, None, evidence, ())
    first = VerificationReportRenderer.to_json(report)
    assert first == VerificationReportRenderer.to_json(report)
    assert first.endswith("\n") and not first.endswith("\n\n")
    assert json.loads(first)["status"] == "passed"
    assert VerificationReportRenderer.to_text(report).startswith("status: passed\n")


def test_renderers_preserve_finding_category_and_failure_status() -> None:
    finding = VerificationFinding(
        VerificationFindingStage.COLLECTION,
        "command_failed",
        "read command failed",
    )
    report = VerificationReport(None, None, None, (finding,))
    payload = json.loads(VerificationReportRenderer.to_json(report))
    assert payload["status"] == "failed"
    assert payload["findings"][0]["stage"] == "collection"
    assert "[collection/command_failed]" in VerificationReportRenderer.to_text(report)
