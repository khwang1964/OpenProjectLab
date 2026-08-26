"""Tests for deterministic, inspection-only Bootstrap validation."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import PurePath

import pytest

from generator.core.bootstrap_validation import (
    BootstrapValidationError,
    BootstrapValidationFinding,
    BootstrapValidationRequest,
    BootstrapValidationResult,
    BootstrapValidator,
)


class _Check:
    def __init__(
        self,
        check_id: str,
        *findings: BootstrapValidationFinding,
        calls: list[str] | None = None,
        failure: Exception | None = None,
    ) -> None:
        self.check_id = check_id
        self.findings = findings
        self.calls = calls if calls is not None else []
        self.failure = failure

    def inspect(
        self, request: BootstrapValidationRequest
    ) -> tuple[BootstrapValidationFinding, ...]:
        assert request.target == PurePath("project")
        self.calls.append(self.check_id)
        if self.failure is not None:
            raise self.failure
        return self.findings


def _finding(check_id: str, severity: str, message: str) -> BootstrapValidationFinding:
    return BootstrapValidationFinding(check_id=check_id, severity=severity, message=message)


def test_validation_preserves_check_and_finding_order() -> None:
    calls: list[str] = []
    validator = BootstrapValidator(
        (
            _Check("structure", _finding("structure", "info", "present"), calls=calls),
            _Check("content", _finding("content", "warning", "optional"), calls=calls),
        )
    )

    result = validator.validate(BootstrapValidationRequest(PurePath("project")))

    assert calls == ["structure", "content"]
    assert result.executed_check_ids == ("structure", "content")
    assert tuple(item.message for item in result.findings) == ("present", "optional")


@pytest.mark.parametrize(
    ("severity", "expected"),
    (("error", False), ("warning", True), ("info", True)),
)
def test_validity_is_derived_from_severity(severity: str, expected: bool) -> None:
    result = BootstrapValidator(
        (_Check("check", _finding("check", severity, "evidence")),)
    ).validate(BootstrapValidationRequest(PurePath("project")))
    assert result.is_valid is expected


def test_empty_validation_is_valid_and_immutable() -> None:
    request = BootstrapValidationRequest(PurePath("project"), context={"b": 2, "a": 1})
    result = BootstrapValidator(()).validate(request)
    assert request.context == (("a", 1), ("b", 2))
    assert result == BootstrapValidationResult()
    assert result.is_valid
    with pytest.raises(FrozenInstanceError):
        result.findings = ()  # type: ignore[misc]


def test_duplicate_check_ids_are_rejected_before_inspection() -> None:
    calls: list[str] = []
    with pytest.raises(ValueError, match="duplicate check_id"):
        BootstrapValidator((_Check("same", calls=calls), _Check("same", calls=calls)))
    assert calls == []


def test_check_failure_stops_later_checks_and_exposes_completed_evidence() -> None:
    calls: list[str] = []
    first = _finding("first", "warning", "kept")
    validator = BootstrapValidator(
        (
            _Check("first", first, calls=calls),
            _Check("broken", calls=calls, failure=OSError("read failed")),
            _Check("later", calls=calls),
        )
    )

    with pytest.raises(BootstrapValidationError) as captured:
        validator.validate(BootstrapValidationRequest(PurePath("project")))

    error = captured.value
    assert calls == ["first", "broken"]
    assert error.failed_check_id == "broken"
    assert error.completed_check_ids == ("first",)
    assert error.completed_findings == (first,)
    assert isinstance(error.__cause__, OSError)


def test_invalid_state_is_a_result_not_an_execution_failure() -> None:
    result = BootstrapValidator(
        (_Check("required", _finding("required", "error", "missing")),)
    ).validate(BootstrapValidationRequest(PurePath("project")))
    assert result.is_valid is False
    assert result.findings[0].message == "missing"


def test_mismatched_finding_identity_fails_closed() -> None:
    validator = BootstrapValidator(
        (_Check("expected", _finding("other", "error", "wrong identity")),)
    )
    with pytest.raises(BootstrapValidationError) as captured:
        validator.validate(BootstrapValidationRequest(PurePath("project")))
    assert isinstance(captured.value.__cause__, ValueError)


def test_contracts_normalize_and_reject_invalid_values() -> None:
    finding = BootstrapValidationFinding(" check ", "WARNING", " message ", " path ")
    assert (finding.check_id, finding.severity, finding.message, finding.subject) == (
        "check",
        "warning",
        "message",
        "path",
    )
    with pytest.raises(ValueError, match="severity"):
        BootstrapValidationFinding("check", "fatal", "message")
    with pytest.raises(TypeError, match="BootstrapValidationRequest"):
        BootstrapValidator(()).validate(object())  # type: ignore[arg-type]
