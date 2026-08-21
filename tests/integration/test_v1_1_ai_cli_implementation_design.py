"""Govern the v1.1 AI CLI implementation baseline."""

from __future__ import annotations

import inspect
from pathlib import Path

from generator.ai.documentation_service import AIDocumentationService
from generator.ai.review_service import AIReviewService
from generator.ai.service import AICourseGenerationService
from generator.ai.template_completion_service import AITemplateCompletionService
from generator.ai.testing import FakeAIProvider
from generator.cli.main import build_parser

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "docs" / "releases" / "v1.1-ai-cli-implementation.md"
TRACKERS = (
    ROOT / "docs" / "roadmap.md",
    ROOT / "docs" / "HISTORY.md",
    ROOT / "CHANGELOG.md",
)
PRODUCTION_MODULE = ROOT / "generator" / "cli" / "ai.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(path: Path) -> str:
    return " ".join(_read(path).split())


def _commands() -> frozenset[str]:
    for action in build_parser()._actions:
        choices = getattr(action, "choices", None)
        if isinstance(choices, dict) and "list" in choices:
            return frozenset(choices)
    raise AssertionError("CLI registry not found")


def test_baseline_precedes_product_implementation() -> None:
    baseline = _read(BASELINE)
    assert "**Status:** Accepted --- Baseline Complete" in baseline
    assert "v1.1.6.1 --- Implementation Baseline / Executable Design Tests" in baseline
    assert "Baseline PR #192 --- Merged" in baseline
    assert "7520da65963d935257f476ea5e0bdd79bd519e3f" in baseline
    assert "Post-merge verification --- 75 passed" in baseline
    assert "**AI CLI Production Registration:** Not Started" in baseline
    assert "**Formal v1.1 Acceptance:** Not Accepted" in baseline
    assert not PRODUCTION_MODULE.exists()
    assert "ai" not in _commands()


def test_exact_existing_service_methods_are_reused() -> None:
    expected = {
        AICourseGenerationService: "generate_course",
        AIReviewService: "review",
        AIDocumentationService: "generate",
        AITemplateCompletionService: "complete",
    }
    for service, method_name in expected.items():
        assert tuple(inspect.signature(service).parameters) == ("provider",)
        parameters = tuple(inspect.signature(getattr(service, method_name)).parameters)
        assert parameters == ("self", "request")


def test_testing_provider_stays_out_of_production_plan() -> None:
    prose = _normalized(BASELINE)
    assert inspect.isclass(FakeAIProvider)
    assert "Production code must not import FakeAIProvider" in prose
    assert "production-local deterministic provider boundary" in prose


def test_fail_closed_boundaries_are_explicit() -> None:
    prose = _normalized(BASELINE)
    for text in (
        "There is no implicit provider",
        "Validation completes before provider invocation or success output",
        "emit no success document on stdout",
        "does not mutate the filesystem",
        "Chat, agents, streaming, tool calling",
    ):
        assert text in prose


def test_trackers_start_v1_1_6_without_claiming_registration() -> None:
    for tracker in TRACKERS:
        prose = _normalized(tracker).lower()
        assert "v1.1.6 ai cli implementation --- in progress" in prose
        assert "v1.1.6.1 implementation baseline --- accepted" in prose
        assert "baseline pr #192 --- merged" in prose
        assert "7520da65963d935257f476ea5e0bdd79bd519e3f" in prose
        assert "post-merge verification --- 75 passed" in prose
        assert "ai cli production registration --- not started" in prose
        assert "formal v1.1 acceptance --- not accepted" in prose
        assert "next --- v1.1.6.2 shared request / local-response infrastructure" in prose
