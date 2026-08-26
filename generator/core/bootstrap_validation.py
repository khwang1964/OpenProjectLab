"""Deterministic, inspection-only Bootstrap validation runtime."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import PurePath
from typing import Any, Protocol

from generator.core.bootstrap_apply import BootstrapApplyResult
from generator.core.bootstrap_planning import FrozenMapping, _freeze_mapping

_SEVERITIES = frozenset({"error", "warning", "info"})


@dataclass(frozen=True, slots=True)
class BootstrapValidationRequest:
    """Identify immutable project state and optional prior apply evidence."""

    target: PurePath
    context: FrozenMapping = field(default_factory=tuple)
    apply_result: BootstrapApplyResult | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "target", PurePath(self.target))
        object.__setattr__(
            self,
            "context",
            _freeze_mapping(self.context)
            if isinstance(self.context, Mapping)
            else tuple(self.context),
        )
        if self.apply_result is not None and not isinstance(
            self.apply_result, BootstrapApplyResult
        ):
            raise TypeError("apply_result must be a BootstrapApplyResult")


@dataclass(frozen=True, slots=True)
class BootstrapValidationFinding:
    """Describe immutable invalid or advisory validation evidence."""

    check_id: str
    severity: str
    message: str
    subject: str | None = None

    def __post_init__(self) -> None:
        check_id = self.check_id.strip()
        severity = self.severity.strip().lower()
        message = self.message.strip()
        subject = self.subject.strip() if self.subject is not None else None
        if not check_id:
            raise ValueError("check_id must not be empty")
        if severity not in _SEVERITIES:
            raise ValueError("severity must be error, warning, or info")
        if not message:
            raise ValueError("message must not be empty")
        object.__setattr__(self, "check_id", check_id)
        object.__setattr__(self, "severity", severity)
        object.__setattr__(self, "message", message)
        object.__setattr__(self, "subject", subject or None)


class BootstrapValidationCheck(Protocol):
    """Describe one injected, inspection-only validation check."""

    check_id: str

    def inspect(self, request: BootstrapValidationRequest) -> Sequence[BootstrapValidationFinding]:
        """Inspect observable state without mutation."""


@dataclass(frozen=True, slots=True)
class BootstrapValidationResult:
    """Aggregate ordered validation evidence and derived validity."""

    executed_check_ids: tuple[str, ...] = ()
    findings: tuple[BootstrapValidationFinding, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "executed_check_ids", tuple(self.executed_check_ids))
        object.__setattr__(self, "findings", tuple(self.findings))

    @property
    def is_valid(self) -> bool:
        """Return false exactly when error evidence exists."""
        return all(finding.severity != "error" for finding in self.findings)


class BootstrapValidationError(RuntimeError):
    """Expose fail-closed evidence when one validation check cannot complete."""

    def __init__(
        self,
        *,
        failed_check_id: str,
        completed_check_ids: tuple[str, ...],
        completed_findings: tuple[BootstrapValidationFinding, ...],
    ) -> None:
        super().__init__(f"Bootstrap validation failed at check: {failed_check_id}")
        self.failed_check_id = failed_check_id
        self.completed_check_ids = tuple(completed_check_ids)
        self.completed_findings = tuple(completed_findings)


class BootstrapValidator:
    """Run injected checks sequentially and preserve deterministic evidence."""

    def __init__(self, checks: Iterable[BootstrapValidationCheck]) -> None:
        self._checks = tuple(checks)
        check_ids = tuple(self._normalized_check_id(check) for check in self._checks)
        if len(check_ids) != len(set(check_ids)):
            raise ValueError("Bootstrap validation contains duplicate check_id values")
        self._check_ids = check_ids

    def validate(self, request: BootstrapValidationRequest) -> BootstrapValidationResult:
        """Inspect in configured order and stop fail closed on check failure."""
        if not isinstance(request, BootstrapValidationRequest):
            raise TypeError("bootstrap validation requires a BootstrapValidationRequest")

        completed_ids: list[str] = []
        completed_findings: list[BootstrapValidationFinding] = []
        for check, check_id in zip(self._checks, self._check_ids, strict=True):
            try:
                findings = tuple(check.inspect(request))
                if any(not isinstance(item, BootstrapValidationFinding) for item in findings):
                    raise TypeError("validation checks must return validation findings")
                if any(item.check_id != check_id for item in findings):
                    raise ValueError("validation finding identity does not match its check")
            except Exception as exc:
                raise BootstrapValidationError(
                    failed_check_id=check_id,
                    completed_check_ids=tuple(completed_ids),
                    completed_findings=tuple(completed_findings),
                ) from exc
            completed_ids.append(check_id)
            completed_findings.extend(findings)

        return BootstrapValidationResult(
            executed_check_ids=tuple(completed_ids),
            findings=tuple(completed_findings),
        )

    @staticmethod
    def _normalized_check_id(check: Any) -> str:
        check_id = getattr(check, "check_id", None)
        if not isinstance(check_id, str) or not check_id.strip():
            raise ValueError("validation check_id must be a non-empty string")
        return check_id.strip()
