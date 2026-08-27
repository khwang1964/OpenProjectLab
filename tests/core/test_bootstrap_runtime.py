"""Tests for deterministic Bootstrap runtime integration."""

from pathlib import PurePath

import pytest

from generator.core.bootstrap_apply import BootstrapApplyResult
from generator.core.bootstrap_dry_run import BootstrapDryRunPreview
from generator.core.bootstrap_planning import BootstrapPlan
from generator.core.bootstrap_runtime import (
    BootstrapRuntimeCoordinator,
    BootstrapRuntimeMode,
    BootstrapRuntimeRequest,
)
from generator.core.bootstrap_validation import (
    BootstrapValidationRequest,
    BootstrapValidationResult,
)


class _Planner:
    def __init__(self, plan: BootstrapPlan, calls: list[str]) -> None:
        self.plan_value = plan
        self.calls = calls

    def plan(self, request: object) -> BootstrapPlan:
        assert request == {"project": "demo"}
        self.calls.append("plan")
        return self.plan_value


class _DryRun:
    def __init__(self, plan: BootstrapPlan, calls: list[str]) -> None:
        self.plan = plan
        self.calls = calls

    def preview(self, plan: BootstrapPlan) -> BootstrapDryRunPreview:
        assert plan is self.plan
        self.calls.append("preview")
        return BootstrapDryRunPreview(steps=(), expected_effects=())


class _Apply:
    def __init__(self, plan: BootstrapPlan, calls: list[str]) -> None:
        self.plan = plan
        self.calls = calls

    def apply(self, plan: BootstrapPlan) -> BootstrapApplyResult:
        assert plan is self.plan
        self.calls.append("apply")
        return BootstrapApplyResult()


class _Validator:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def validate(self, request: BootstrapValidationRequest) -> BootstrapValidationResult:
        assert request.apply_result == BootstrapApplyResult()
        self.calls.append("validate")
        return BootstrapValidationResult()


def _coordinator(calls: list[str]) -> tuple[BootstrapRuntimeCoordinator, BootstrapPlan]:
    plan = BootstrapPlan(normalized_intent=(), steps=(), expected_effects=())
    return (
        BootstrapRuntimeCoordinator(
            planner=_Planner(plan, calls),
            dry_run=_DryRun(plan, calls),  # type: ignore[arg-type]
            apply_executor=_Apply(plan, calls),  # type: ignore[arg-type]
            validator=_Validator(calls),  # type: ignore[arg-type]
        ),
        plan,
    )


def test_preview_only_plans_and_previews_same_plan() -> None:
    calls: list[str] = []
    coordinator, plan = _coordinator(calls)
    result = coordinator.execute(
        BootstrapRuntimeRequest({"project": "demo"}, BootstrapRuntimeMode.PREVIEW)
    )
    assert calls == ["plan", "preview"]
    assert result.plan is plan
    assert result.preview is not None
    assert result.apply_result is result.validation_result is None


def test_apply_only_plans_then_applies() -> None:
    calls: list[str] = []
    coordinator, plan = _coordinator(calls)
    result = coordinator.execute(
        BootstrapRuntimeRequest({"project": "demo"}, BootstrapRuntimeMode.APPLY)
    )
    assert calls == ["plan", "apply"]
    assert result.plan is plan
    assert result.apply_result == BootstrapApplyResult()
    assert result.preview is result.validation_result is None


def test_apply_and_validate_has_closed_order_and_apply_evidence() -> None:
    calls: list[str] = []
    coordinator, plan = _coordinator(calls)
    result = coordinator.execute(
        BootstrapRuntimeRequest(
            {"project": "demo"},
            BootstrapRuntimeMode.APPLY_AND_VALIDATE,
            BootstrapValidationRequest(PurePath("project")),
        )
    )
    assert calls == ["plan", "apply", "validate"]
    assert result.plan is plan
    assert result.apply_result == BootstrapApplyResult()
    assert result.validation_result == BootstrapValidationResult()


@pytest.mark.parametrize("failure_phase", ("plan", "apply", "validate"))
def test_phase_failure_stops_later_phases(failure_phase: str) -> None:
    calls: list[str] = []
    coordinator, _ = _coordinator(calls)
    dependency = {
        "plan": coordinator._planner,
        "apply": coordinator._apply,
        "validate": coordinator._validator,
    }[failure_phase]
    method = {"plan": "plan", "apply": "apply", "validate": "validate"}[failure_phase]
    setattr(dependency, method, lambda *args: (_ for _ in ()).throw(RuntimeError(failure_phase)))
    with pytest.raises(RuntimeError, match=failure_phase):
        coordinator.execute(
            BootstrapRuntimeRequest(
                {"project": "demo"},
                BootstrapRuntimeMode.APPLY_AND_VALIDATE,
                BootstrapValidationRequest(PurePath("project")),
            )
        )
    expected = {"plan": [], "apply": ["plan"], "validate": ["plan", "apply"]}
    assert calls == expected[failure_phase]


def test_request_rejects_implicit_or_misplaced_validation() -> None:
    with pytest.raises(TypeError, match="BootstrapRuntimeMode"):
        BootstrapRuntimeRequest({}, "apply")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="requires"):
        BootstrapRuntimeRequest({}, BootstrapRuntimeMode.APPLY_AND_VALIDATE)
    with pytest.raises(ValueError, match="only valid"):
        BootstrapRuntimeRequest(
            {}, BootstrapRuntimeMode.PREVIEW, BootstrapValidationRequest(PurePath("p"))
        )
