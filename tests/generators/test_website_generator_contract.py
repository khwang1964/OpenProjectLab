"""Contract tests for the proposed Website Generator."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import pytest

from generator.core.exceptions import GeneratorValidationError
from generator.core.models import GenerateRequest, GenerationPlan, GenerationResult, RuntimeOptions
from generator.generators.base import BaseGenerator

pytest.importorskip(
    "generator.generators.website_generator",
    reason="WebsiteGenerator implementation lands in Step 5.7C",
)

from generator.generators.website_generator import WebsiteGenerator


def _pages() -> tuple[dict[str, object], ...]:
    return (
        {
            "path": "index.html",
            "title": "Home",
            "content": "Welcome to Modern Java in Action.",
        },
        {
            "path": "weeks/week-01.html",
            "title": "Week 01",
            "content": "Introduction to Modern Java.",
        },
    )


_DEFAULT_PAGES = object()


def _request(
    tmp_path: Path,
    *,
    generator_name: str = "website",
    title: object = "Modern Java in Action",
    pages: object = _DEFAULT_PAGES,
    dry_run: bool = True,
    overwrite: bool = False,
) -> GenerateRequest:
    return GenerateRequest(
        generator_name=generator_name,
        target=tmp_path / "course",
        values={
            "title": title,
            "pages": (_pages() if pages is _DEFAULT_PAGES else pages),
            "record_manifest": False,
        },
        options=RuntimeOptions(
            dry_run=dry_run,
            overwrite=overwrite,
        ),
    )


def _generator(tmp_path: Path) -> WebsiteGenerator:
    return WebsiteGenerator(template_root=tmp_path / "templates")


def test_website_generator_is_base_generator() -> None:
    assert issubclass(WebsiteGenerator, BaseGenerator)


def test_website_generator_has_canonical_identity() -> None:
    assert WebsiteGenerator.name == "website"


def test_website_generator_has_description() -> None:
    assert isinstance(WebsiteGenerator.description, str)
    assert WebsiteGenerator.description.strip()


def test_website_generator_accepts_minimum_valid_request(tmp_path: Path) -> None:
    generator = _generator(tmp_path)

    generator.validate_request(_request(tmp_path))


def test_website_generator_rejects_wrong_generator_name(tmp_path: Path) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(
            _request(tmp_path, generator_name="course"),
        )

    assert exc_info.value.generator == "website"
    assert exc_info.value.field == "generator_name"


@pytest.mark.parametrize("title", ["", "   "])
def test_website_generator_rejects_empty_site_title(
    tmp_path: Path,
    title: str,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, title=title))

    assert exc_info.value.generator == "website"
    assert exc_info.value.field == "title"


@pytest.mark.parametrize("title", [None, 3, True])
def test_website_generator_rejects_non_string_site_title(
    tmp_path: Path,
    title: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, title=title))

    assert exc_info.value.field == "title"


@pytest.mark.parametrize(
    "pages",
    [
        (),
        [],
    ],
)
def test_website_generator_rejects_empty_pages(
    tmp_path: Path,
    pages: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, pages=pages))

    assert exc_info.value.generator == "website"
    assert exc_info.value.field == "pages"


@pytest.mark.parametrize(
    "pages",
    [
        None,
        "index.html",
        b"index.html",
        bytearray(b"index.html"),
        {"path": "index.html"},
        3,
        True,
    ],
)
def test_website_generator_rejects_invalid_pages_collection(
    tmp_path: Path,
    pages: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, pages=pages))

    assert exc_info.value.field == "pages"


@pytest.mark.parametrize(
    "page",
    [
        "page",
        b"page",
        3,
        True,
        None,
    ],
)
def test_website_generator_rejects_non_mapping_page(
    tmp_path: Path,
    page: object,
) -> None:
    generator = _generator(tmp_path)
    pages = (
        {
            "path": "index.html",
            "title": "Home",
            "content": "Welcome.",
        },
        page,
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, pages=pages))

    assert exc_info.value.field in {"pages", "page"}


def test_website_generator_rejects_missing_page_path(tmp_path: Path) -> None:
    generator = _generator(tmp_path)
    pages = (
        {
            "title": "Home",
            "content": "Welcome.",
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, pages=pages))

    assert exc_info.value.field in {"pages", "page_path", "path"}


@pytest.mark.parametrize("page_path", ["", "   ", None, 3, True])
def test_website_generator_rejects_invalid_page_path(
    tmp_path: Path,
    page_path: object,
) -> None:
    generator = _generator(tmp_path)
    pages = (
        {
            "path": page_path,
            "title": "Home",
            "content": "Welcome.",
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, pages=pages))

    assert exc_info.value.field in {"pages", "page_path", "path"}


@pytest.mark.parametrize(
    "page_path",
    [
        "../index.html",
        "../../outside.html",
        r"..\outside.html",
        "/absolute.html",
        r"C:\temp\index.html",
    ],
)
def test_website_generator_rejects_unsafe_page_path(
    tmp_path: Path,
    page_path: str,
) -> None:
    generator = _generator(tmp_path)
    pages = (
        {
            "path": page_path,
            "title": "Home",
            "content": "Welcome.",
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, pages=pages))

    assert exc_info.value.field in {"pages", "page_path", "path"}


@pytest.mark.parametrize(
    "page_path",
    [
        "index.md",
        "index.txt",
        "index",
        "weeks/week-01.md",
    ],
)
def test_website_generator_rejects_non_html_page_path(
    tmp_path: Path,
    page_path: str,
) -> None:
    generator = _generator(tmp_path)
    pages = (
        {
            "path": page_path,
            "title": "Home",
            "content": "Welcome.",
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, pages=pages))

    assert exc_info.value.field in {"pages", "page_path", "path"}


def test_website_generator_rejects_duplicate_page_paths(tmp_path: Path) -> None:
    generator = _generator(tmp_path)
    pages = (
        {
            "path": "index.html",
            "title": "Home",
            "content": "Welcome.",
        },
        {
            "path": "index.html",
            "title": "Duplicate Home",
            "content": "Duplicate.",
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, pages=pages))

    assert exc_info.value.field in {"pages", "page_path", "path"}


def test_website_generator_rejects_duplicate_normalized_page_paths(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    pages = (
        {
            "path": "index.html",
            "title": "Home",
            "content": "Welcome.",
        },
        {
            "path": "./index.html",
            "title": "Duplicate Home",
            "content": "Duplicate.",
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, pages=pages))

    assert exc_info.value.field in {"pages", "page_path", "path"}


def test_website_generator_requires_index_page(tmp_path: Path) -> None:
    generator = _generator(tmp_path)
    pages = (
        {
            "path": "about.html",
            "title": "About",
            "content": "About this course.",
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, pages=pages))

    assert exc_info.value.field in {"pages", "page_path", "path"}


def test_website_generator_accepts_nested_relative_html_page(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    pages = (
        {
            "path": "index.html",
            "title": "Home",
            "content": "Welcome.",
        },
        {
            "path": "weeks/week-01.html",
            "title": "Week 01",
            "content": "Introduction.",
        },
    )

    generator.validate_request(_request(tmp_path, pages=pages))


def test_website_generator_rejects_missing_page_title(tmp_path: Path) -> None:
    generator = _generator(tmp_path)
    pages = (
        {
            "path": "index.html",
            "content": "Welcome.",
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, pages=pages))

    assert exc_info.value.field in {"pages", "page_title", "title"}


@pytest.mark.parametrize("page_title", ["", "   ", None, 3, True])
def test_website_generator_rejects_invalid_page_title(
    tmp_path: Path,
    page_title: object,
) -> None:
    generator = _generator(tmp_path)
    pages = (
        {
            "path": "index.html",
            "title": page_title,
            "content": "Welcome.",
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, pages=pages))

    assert exc_info.value.field in {"pages", "page_title", "title"}


def test_website_generator_rejects_missing_page_content(tmp_path: Path) -> None:
    generator = _generator(tmp_path)
    pages = (
        {
            "path": "index.html",
            "title": "Home",
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, pages=pages))

    assert exc_info.value.field in {"pages", "content"}


@pytest.mark.parametrize("content", [None, 3, True, (), []])
def test_website_generator_rejects_non_string_page_content(
    tmp_path: Path,
    content: object,
) -> None:
    generator = _generator(tmp_path)
    pages = (
        {
            "path": "index.html",
            "title": "Home",
            "content": content,
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, pages=pages))

    assert exc_info.value.field in {"pages", "content"}


def test_website_generator_accepts_empty_page_content(tmp_path: Path) -> None:
    generator = _generator(tmp_path)
    pages = (
        {
            "path": "index.html",
            "title": "Home",
            "content": "",
        },
    )

    generator.validate_request(_request(tmp_path, pages=pages))


def test_website_generator_accepts_unicode_and_multiline_content(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    pages = (
        {
            "path": "index.html",
            "title": "課程首頁",
            "content": "歡迎來到課程。\n第二行內容。\nEmoji: 🚀",
        },
    )

    generator.validate_request(_request(tmp_path, pages=pages))


def test_website_generator_preserves_page_order_in_plan(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    pages = (
        {
            "path": "index.html",
            "title": "Home",
            "content": "Home content.",
        },
        {
            "path": "weeks/week-02.html",
            "title": "Week 02",
            "content": "Second week.",
        },
        {
            "path": "weeks/week-01.html",
            "title": "Week 01",
            "content": "First week.",
        },
    )
    request = _request(tmp_path, pages=pages)

    generator.validate_request(request)
    plan = generator.plan(request)

    assert isinstance(plan, GenerationPlan)
    assert plan.generator_name == "website"
    assert tuple(operation.destination for operation in plan.operations) == (
        request.target / "site" / "index.html",
        request.target / "site" / "weeks" / "week-02.html",
        request.target / "site" / "weeks" / "week-01.html",
    )


def test_website_plan_uses_generation_plan_as_canonical_boundary(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path)

    generator.validate_request(request)
    plan = generator.plan(request)

    assert isinstance(plan, GenerationPlan)
    assert plan.generator_name == "website"
    assert len(plan.operations) == 2
    assert plan.operations[0].destination == request.target / "site" / "index.html"
    assert plan.operations[1].destination == (request.target / "site" / "weeks" / "week-01.html")


def test_website_plan_uses_one_operation_per_page(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path)

    generator.validate_request(request)
    plan = generator.plan(request)

    assert len(plan.operations) == len(request.values["pages"])


def test_website_plan_uses_default_template_for_every_page(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path)

    generator.validate_request(request)
    plan = generator.plan(request)

    assert {operation.template_name for operation in plan.operations} == {"website/page.html.j2"}


def test_website_plan_builds_deterministic_navigation(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path)

    generator.validate_request(request)
    plan = generator.plan(request)

    expected_navigation = (
        {
            "path": "index.html",
            "title": "Home",
        },
        {
            "path": "weeks/week-01.html",
            "title": "Week 01",
        },
    )

    for operation in plan.operations:
        context = operation.context
        assert tuple(context["navigation"]) == expected_navigation


def test_website_plan_provides_site_title_and_current_page_context(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path)

    generator.validate_request(request)
    plan = generator.plan(request)

    first_context = plan.operations[0].context
    second_context = plan.operations[1].context

    assert first_context["site_title"] == "Modern Java in Action"
    assert first_context["page"]["path"] == "index.html"
    assert first_context["page"]["title"] == "Home"
    assert first_context["page"]["content"] == "Welcome to Modern Java in Action."

    assert second_context["site_title"] == "Modern Java in Action"
    assert second_context["page"]["path"] == "weeks/week-01.html"
    assert second_context["page"]["title"] == "Week 01"
    assert second_context["page"]["content"] == "Introduction to Modern Java."


def test_website_plan_preserves_unicode_and_multiline_content(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    content = "歡迎來到課程。\n第二行內容。\nEmoji: 🚀"
    pages = (
        {
            "path": "index.html",
            "title": "課程首頁",
            "content": content,
        },
    )
    request = _request(
        tmp_path,
        title="現代 Java",
        pages=pages,
    )

    generator.validate_request(request)
    plan = generator.plan(request)

    context = plan.operations[0].context
    assert context["site_title"] == "現代 Java"
    assert context["page"]["title"] == "課程首頁"
    assert context["page"]["content"] == content


def test_website_plan_is_deterministic_for_same_request(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path)

    generator.validate_request(request)

    first = generator.plan(request)
    second = generator.plan(request)

    assert first == second


def test_website_validation_does_not_mutate_request_values(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    home: dict[str, object] = {
        "path": "index.html",
        "title": " Home ",
        "content": "Welcome.",
    }
    pages = (home,)
    request = _request(
        tmp_path,
        title=" Modern Java ",
        pages=pages,
    )

    original_title = request.values["title"]
    original_pages = request.values["pages"]

    generator.validate_request(request)

    assert request.values["title"] == original_title
    assert request.values["pages"] is original_pages
    assert home == {
        "path": "index.html",
        "title": " Home ",
        "content": "Welcome.",
    }


def test_website_planning_does_not_mutate_nested_page_mapping(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    home: dict[str, object] = {
        "path": "index.html",
        "title": " Home ",
        "content": "Welcome.",
    }
    pages = (home,)
    request = _request(
        tmp_path,
        title=" Modern Java ",
        pages=pages,
    )

    generator.validate_request(request)
    plan = generator.plan(request)

    assert isinstance(plan.operations[0].context, Mapping)
    assert home == {
        "path": "index.html",
        "title": " Home ",
        "content": "Welcome.",
    }


def test_website_plan_normalizes_display_text_without_mutating_request(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    pages = (
        {
            "path": "index.html",
            "title": " Home ",
            "content": "Welcome.",
        },
    )
    request = _request(
        tmp_path,
        title=" Modern Java ",
        pages=pages,
    )

    generator.validate_request(request)
    plan = generator.plan(request)

    context = plan.operations[0].context
    assert context["site_title"] == "Modern Java"
    assert context["page"]["title"] == "Home"
    assert request.values["title"] == " Modern Java "
    assert request.values["pages"][0]["title"] == " Home "


def test_invalid_website_request_fails_before_planning(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path, pages=())
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


def test_website_plan_does_not_create_filesystem_artifacts(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path)

    generator.validate_request(request)
    generator.plan(request)

    assert not request.target.exists()


def test_website_dry_run_preserves_no_filesystem_mutation(
    tmp_path: Path,
) -> None:
    template_root = tmp_path / "templates"
    template_file = template_root / "website" / "page.html.j2"
    template_file.parent.mkdir(parents=True)
    template_file.write_text(
        "<!doctype html>\n"
        "<html>\n"
        "<head><title>{{ page.title }}</title></head>\n"
        "<body>\n"
        "<h1>{{ page.title }}</h1>\n"
        "<p>{{ page.content }}</p>\n"
        "</body>\n"
        "</html>\n",
        encoding="utf-8",
    )

    generator = WebsiteGenerator(template_root=template_root)
    request = _request(tmp_path, dry_run=True)

    result = generator.run(request)

    assert isinstance(result, GenerationResult)
    assert result.generator_name == "website"
    assert result.dry_run is True
    assert result.manifest_updated is False
    assert not request.target.exists()


def test_website_contract_does_not_require_specialized_result_types() -> None:
    import generator.core.models as models

    assert not hasattr(models, "WebsiteRequest")
    assert not hasattr(models, "WebsitePlan")
    assert not hasattr(models, "WebsiteGenerationPlan")
    assert not hasattr(models, "WebsiteResult")
    assert not hasattr(models, "WebsiteGenerationResult")
    assert not hasattr(models, "WebsitePage")


def test_website_contract_does_not_expand_public_sdk() -> None:
    import generator.sdk as sdk

    forbidden_symbols = {
        "Website",
        "WebsitePage",
        "WebsiteGenerator",
        "WebsiteRequest",
        "WebsitePlan",
        "WebsiteResult",
        "StaticSite",
        "Navigation",
        "Deployment",
    }

    assert forbidden_symbols.isdisjoint(set(dir(sdk)))
