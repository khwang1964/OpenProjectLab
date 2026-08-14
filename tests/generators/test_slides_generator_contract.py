"""Contract tests for the proposed Slides Generator."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import pytest

from generator.core.exceptions import GeneratorValidationError
from generator.core.models import GenerateRequest, GenerationPlan, GenerationResult, RuntimeOptions
from generator.generators.base import BaseGenerator

pytest.importorskip(
    "generator.generators.slides_generator",
    reason="SlidesGenerator implementation lands in Step 5.6C",
)

from generator.generators.slides_generator import SlidesGenerator


def _slides() -> tuple[dict[str, object], ...]:
    return (
        {
            "title": "Learning Objectives",
            "content": (
                "Understand reactive systems.",
                "Explain asynchronous data flows.",
            ),
        },
        {
            "title": "Core Concepts",
            "content": (
                "Streams",
                "Backpressure",
                "Non-blocking execution",
            ),
        },
    )


_DEFAULT_SLIDES = object()


def _request(
    tmp_path: Path,
    *,
    generator_name: str = "slides",
    title: object = "Week 01: Reactive Programming",
    slides: object = _DEFAULT_SLIDES,
    dry_run: bool = True,
    overwrite: bool = False,
) -> GenerateRequest:
    return GenerateRequest(
        generator_name=generator_name,
        target=tmp_path / "course",
        values={
            "title": title,
            "slides": (_slides() if slides is _DEFAULT_SLIDES else slides),
            "record_manifest": False,
        },
        options=RuntimeOptions(
            dry_run=dry_run,
            overwrite=overwrite,
        ),
    )


def _generator(tmp_path: Path) -> SlidesGenerator:
    return SlidesGenerator(template_root=tmp_path / "templates")


def test_slides_generator_is_base_generator() -> None:
    assert issubclass(SlidesGenerator, BaseGenerator)


def test_slides_generator_has_canonical_identity() -> None:
    assert SlidesGenerator.name == "slides"


def test_slides_generator_accepts_minimum_valid_request(tmp_path: Path) -> None:
    generator = _generator(tmp_path)

    generator.validate_request(_request(tmp_path))


def test_slides_generator_rejects_wrong_generator_name(tmp_path: Path) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(
            _request(tmp_path, generator_name="week"),
        )

    assert exc_info.value.generator == "slides"
    assert exc_info.value.field == "generator_name"


@pytest.mark.parametrize("title", ["", "   "])
def test_slides_generator_rejects_empty_title(
    tmp_path: Path,
    title: str,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, title=title))

    assert exc_info.value.generator == "slides"
    assert exc_info.value.field == "title"


@pytest.mark.parametrize("title", [None, 3, True])
def test_slides_generator_rejects_non_string_title(
    tmp_path: Path,
    title: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, title=title))

    assert exc_info.value.field == "title"


@pytest.mark.parametrize(
    "slides",
    [
        (),
        [],
    ],
)
def test_slides_generator_rejects_empty_slides(
    tmp_path: Path,
    slides: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, slides=slides))

    assert exc_info.value.generator == "slides"
    assert exc_info.value.field == "slides"


@pytest.mark.parametrize(
    "slides",
    [
        None,
        "slide",
        b"slide",
        3,
        True,
    ],
)
def test_slides_generator_rejects_invalid_slides_collection(
    tmp_path: Path,
    slides: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, slides=slides))

    assert exc_info.value.field == "slides"


@pytest.mark.parametrize(
    "slide",
    [
        "slide",
        b"slide",
        3,
        True,
        None,
    ],
)
def test_slides_generator_rejects_non_mapping_slide(
    tmp_path: Path,
    slide: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, slides=(slide,)))

    assert exc_info.value.field in {"slides", "slide"}


@pytest.mark.parametrize("slide_title", ["", "   ", None, 3, True])
def test_slides_generator_rejects_invalid_slide_title(
    tmp_path: Path,
    slide_title: object,
) -> None:
    generator = _generator(tmp_path)
    slides = (
        {
            "title": slide_title,
            "content": ("content",),
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, slides=slides))

    assert exc_info.value.field in {"slides", "slide_title", "title"}


def test_slides_generator_rejects_missing_slide_title(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    slides = (
        {
            "content": ("content",),
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, slides=slides))

    assert exc_info.value.field in {"slides", "slide_title", "title"}


def test_slides_generator_rejects_missing_slide_content(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    slides = (
        {
            "title": "Section",
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, slides=slides))

    assert exc_info.value.field in {"slides", "content"}


@pytest.mark.parametrize(
    "content",
    [
        None,
        "single item",
        b"single item",
        3,
        True,
    ],
)
def test_slides_generator_rejects_invalid_slide_content_collection(
    tmp_path: Path,
    content: object,
) -> None:
    generator = _generator(tmp_path)
    slides = (
        {
            "title": "Section",
            "content": content,
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, slides=slides))

    assert exc_info.value.field in {"slides", "content"}


@pytest.mark.parametrize(
    "content",
    [
        ("valid", ""),
        ("valid", "   "),
        ("valid", 3),
        ("valid", True),
        ("valid", None),
    ],
)
def test_slides_generator_rejects_invalid_slide_content_item(
    tmp_path: Path,
    content: object,
) -> None:
    generator = _generator(tmp_path)
    slides = (
        {
            "title": "Section",
            "content": content,
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, slides=slides))

    assert exc_info.value.field in {"slides", "content"}


def test_slides_generator_accepts_title_only_slide(tmp_path: Path) -> None:
    generator = _generator(tmp_path)
    slides = (
        {
            "title": "Part II",
            "content": (),
        },
    )

    generator.validate_request(_request(tmp_path, slides=slides))


def test_slides_generator_preserves_slide_and_content_order(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    slides = (
        {
            "title": "Second",
            "content": ("b", "a", "c"),
        },
        {
            "title": "First",
            "content": ("c", "b", "a"),
        },
    )
    request = _request(tmp_path, slides=slides)

    generator.validate_request(request)
    plan = generator.plan(request)

    assert isinstance(plan, GenerationPlan)
    assert plan.generator_name == "slides"
    assert len(plan.operations) == 1

    context = plan.operations[0].context
    planned_slides = context["slides"]

    assert tuple(slide["title"] for slide in planned_slides) == (
        "Second",
        "First",
    )
    assert tuple(planned_slides[0]["content"]) == ("b", "a", "c")
    assert tuple(planned_slides[1]["content"]) == ("c", "b", "a")


def test_slides_plan_uses_generation_plan_as_canonical_boundary(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path)

    generator.validate_request(request)
    plan = generator.plan(request)

    assert isinstance(plan, GenerationPlan)
    assert plan.generator_name == "slides"
    assert len(plan.operations) == 1
    assert plan.operations[0].destination == request.target / "slides.md"


def test_slides_plan_uses_default_template(tmp_path: Path) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path)

    generator.validate_request(request)
    plan = generator.plan(request)

    assert len(plan.operations) == 1
    assert plan.operations[0].template_name == "slides/slides.md.j2"


def test_slides_plan_is_deterministic_for_same_request(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path)

    generator.validate_request(request)

    first = generator.plan(request)
    second = generator.plan(request)

    assert first == second


def test_slides_validation_does_not_mutate_request_values(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    slides = (
        {
            "title": "Overview",
            "content": ("first", "second"),
        },
    )
    request = _request(tmp_path, slides=slides)

    original_title = request.values["title"]
    original_slides = request.values["slides"]

    generator.validate_request(request)

    assert request.values["title"] == original_title
    assert request.values["slides"] is original_slides
    assert slides[0]["title"] == "Overview"
    assert slides[0]["content"] == ("first", "second")


def test_slides_plan_preserves_mapping_values_without_mutating_request(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    slide: dict[str, object] = {
        "title": "Overview",
        "content": ("first", "second"),
    }
    slides = (slide,)
    request = _request(tmp_path, slides=slides)

    generator.validate_request(request)
    plan = generator.plan(request)

    assert isinstance(plan.operations[0].context, Mapping)
    assert slide == {
        "title": "Overview",
        "content": ("first", "second"),
    }


def test_invalid_slides_request_fails_before_planning(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path, slides=())
    planning_called = False

    original_plan = generator.plan

    def tracking_plan(request: GenerateRequest) -> GenerationPlan:
        nonlocal planning_called
        planning_called = True
        return original_plan(request)

    monkeypatch.setattr(generator, "plan", tracking_plan)

    with pytest.raises(GeneratorValidationError):
        generator.run(request)

    assert planning_called is False
    assert not request.target.exists()


def test_slides_dry_run_preserves_no_filesystem_mutation(
    tmp_path: Path,
) -> None:
    template_root = tmp_path / "templates"
    template_file = template_root / "slides" / "slides.md.j2"
    template_file.parent.mkdir(parents=True)
    template_file.write_text(
        "# {{ title }}\n"
        "{% for slide in slides %}\n"
        "---\n\n"
        "## {{ slide.title }}\n"
        "{% for item in slide.content %}\n"
        "- {{ item }}\n"
        "{% endfor %}\n"
        "{% endfor %}",
        encoding="utf-8",
    )

    generator = SlidesGenerator(template_root=template_root)
    request = _request(tmp_path, dry_run=True)

    result = generator.run(request)

    assert isinstance(result, GenerationResult)
    assert result.generator_name == "slides"
    assert result.dry_run is True
    assert result.manifest_updated is False
    assert not request.target.exists()


def test_slides_contract_does_not_require_specialized_result_types() -> None:
    import generator.core.models as models

    assert not hasattr(models, "SlidesRequest")
    assert not hasattr(models, "SlidesPlan")
    assert not hasattr(models, "SlidesGenerationPlan")
    assert not hasattr(models, "SlidesResult")
    assert not hasattr(models, "SlidesGenerationResult")


def test_slides_contract_does_not_expand_public_sdk() -> None:
    import generator.sdk as sdk

    forbidden_symbols = {
        "Slide",
        "Slides",
        "SlideDeck",
        "SlidesGenerator",
        "SlidesRequest",
        "SlidesPlan",
        "SlidesResult",
        "PresentationRenderer",
    }

    assert forbidden_symbols.isdisjoint(set(dir(sdk)))
