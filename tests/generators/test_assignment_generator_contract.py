"""Contract tests for the proposed Assignment Generator."""

from __future__ import annotations

from pathlib import Path

import pytest

from generator.core.exceptions import GeneratorValidationError
from generator.core.models import GenerateRequest, GenerationPlan, GenerationResult, RuntimeOptions
from generator.generators.base import BaseGenerator

pytest.importorskip(
    "generator.generators.assignment_generator",
    reason="AssignmentGenerator implementation lands in Step 5.5C",
)

from generator.generators.assignment_generator import AssignmentGenerator

_DEFAULT_OBJECTIVES = object()
_DEFAULT_INSTRUCTIONS = object()
_DEFAULT_DELIVERABLES = object()
_DEFAULT_RESOURCES = object()
_DEFAULT_SUBMISSION = object()


def _request(
    tmp_path: Path,
    *,
    generator_name: str = "assignment",
    week: object = 4,
    assignment_id: object = "streams-homework",
    title: object = "Streams Homework",
    objectives: object = _DEFAULT_OBJECTIVES,
    instructions: object = _DEFAULT_INSTRUCTIONS,
    deliverables: object = _DEFAULT_DELIVERABLES,
    resources: object = _DEFAULT_RESOURCES,
    submission: object = _DEFAULT_SUBMISSION,
    dry_run: bool = True,
    overwrite: bool = False,
) -> GenerateRequest:
    values: dict[str, object] = {
        "week": week,
        "assignment_id": assignment_id,
        "title": title,
        "record_manifest": False,
    }

    if objectives is not _DEFAULT_OBJECTIVES:
        values["objectives"] = objectives
    if instructions is not _DEFAULT_INSTRUCTIONS:
        values["instructions"] = instructions
    if deliverables is not _DEFAULT_DELIVERABLES:
        values["deliverables"] = deliverables
    if resources is not _DEFAULT_RESOURCES:
        values["resources"] = resources
    if submission is not _DEFAULT_SUBMISSION:
        values["submission"] = submission

    return GenerateRequest(
        generator_name=generator_name,
        target=tmp_path / "course",
        values=values,
        options=RuntimeOptions(
            dry_run=dry_run,
            overwrite=overwrite,
        ),
    )


def _generator(tmp_path: Path) -> AssignmentGenerator:
    return AssignmentGenerator(template_root=tmp_path / "templates")


def test_assignment_generator_is_base_generator() -> None:
    assert issubclass(AssignmentGenerator, BaseGenerator)


def test_assignment_generator_has_canonical_identity() -> None:
    assert AssignmentGenerator.name == "assignment"


def test_assignment_generator_accepts_minimum_valid_request(tmp_path: Path) -> None:
    generator = _generator(tmp_path)

    generator.validate_request(_request(tmp_path))


def test_assignment_generator_rejects_wrong_generator_name(tmp_path: Path) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, generator_name="week"))

    assert exc_info.value.generator == "assignment"
    assert exc_info.value.field == "generator_name"


@pytest.mark.parametrize("week", [0, -1, -10])
def test_assignment_generator_rejects_non_positive_week(
    tmp_path: Path,
    week: int,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, week=week))

    assert exc_info.value.generator == "assignment"
    assert exc_info.value.field == "week"


@pytest.mark.parametrize("week", [True, False])
def test_assignment_generator_rejects_bool_week(
    tmp_path: Path,
    week: bool,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, week=week))

    assert exc_info.value.field == "week"


@pytest.mark.parametrize("week", ["4", 4.0, None])
def test_assignment_generator_rejects_non_integer_week(
    tmp_path: Path,
    week: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, week=week))

    assert exc_info.value.field == "week"


@pytest.mark.parametrize("assignment_id", ["", "   "])
def test_assignment_generator_rejects_empty_assignment_id(
    tmp_path: Path,
    assignment_id: str,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, assignment_id=assignment_id))

    assert exc_info.value.generator == "assignment"
    assert exc_info.value.field == "assignment_id"


@pytest.mark.parametrize("assignment_id", [None, 4, True])
def test_assignment_generator_rejects_non_string_assignment_id(
    tmp_path: Path,
    assignment_id: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, assignment_id=assignment_id))

    assert exc_info.value.field == "assignment_id"


@pytest.mark.parametrize(
    "assignment_id",
    [
        "../streams",
        "assignment/streams",
        r"assignment\streams",
        "/absolute",
    ],
)
def test_assignment_generator_rejects_path_like_assignment_id(
    tmp_path: Path,
    assignment_id: str,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, assignment_id=assignment_id))

    assert exc_info.value.field == "assignment_id"


@pytest.mark.parametrize("title", ["", "   "])
def test_assignment_generator_rejects_empty_title(
    tmp_path: Path,
    title: str,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, title=title))

    assert exc_info.value.generator == "assignment"
    assert exc_info.value.field == "title"


@pytest.mark.parametrize("title", [None, 4, True])
def test_assignment_generator_rejects_non_string_title(
    tmp_path: Path,
    title: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, title=title))

    assert exc_info.value.field == "title"


@pytest.mark.parametrize("objectives", ["one objective", 3, True, None])
def test_assignment_generator_rejects_invalid_objectives_collection(
    tmp_path: Path,
    objectives: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, objectives=objectives))

    assert exc_info.value.field == "objectives"


@pytest.mark.parametrize(
    "objectives",
    [
        ("valid", ""),
        ("valid", "   "),
        ("valid", 3),
        ("valid", True),
        ("valid", None),
    ],
)
def test_assignment_generator_rejects_invalid_objective_item(
    tmp_path: Path,
    objectives: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, objectives=objectives))

    assert exc_info.value.field == "objectives"


@pytest.mark.parametrize("instructions", ["", "   ", 3, True, None])
def test_assignment_generator_rejects_invalid_instructions(
    tmp_path: Path,
    instructions: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, instructions=instructions))

    assert exc_info.value.field == "instructions"


@pytest.mark.parametrize("deliverables", ["README.md", 3, True, None])
def test_assignment_generator_rejects_invalid_deliverables_collection(
    tmp_path: Path,
    deliverables: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, deliverables=deliverables))

    assert exc_info.value.field == "deliverables"


@pytest.mark.parametrize(
    "deliverables",
    [
        ("README.md", ""),
        ("README.md", "   "),
        ("README.md", 3),
        ("README.md", True),
        ("README.md", None),
    ],
)
def test_assignment_generator_rejects_invalid_deliverable_item(
    tmp_path: Path,
    deliverables: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, deliverables=deliverables))

    assert exc_info.value.field == "deliverables"


@pytest.mark.parametrize("resources", ["reference", 3, True, None])
def test_assignment_generator_rejects_invalid_resources_collection(
    tmp_path: Path,
    resources: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, resources=resources))

    assert exc_info.value.field == "resources"


@pytest.mark.parametrize(
    "resources",
    [
        ("docs/reference.md", ""),
        ("docs/reference.md", "   "),
        ("docs/reference.md", 3),
        ("docs/reference.md", True),
        ("docs/reference.md", None),
    ],
)
def test_assignment_generator_rejects_invalid_resource_item(
    tmp_path: Path,
    resources: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, resources=resources))

    assert exc_info.value.field == "resources"


@pytest.mark.parametrize("submission", ["", "   ", 3, True, None])
def test_assignment_generator_rejects_invalid_submission_guidance(
    tmp_path: Path,
    submission: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, submission=submission))

    assert exc_info.value.field == "submission"


def test_assignment_generator_accepts_supported_optional_content(tmp_path: Path) -> None:
    generator = _generator(tmp_path)
    request = _request(
        tmp_path,
        objectives=("Use stream pipelines.", "Choose terminal operations."),
        instructions="Complete the tasks.",
        deliverables=("src/StreamsHomework.java", "README.md"),
        resources=("docs/streams.md", "examples/streams.java"),
        submission="Submit the requested files.",
    )

    generator.validate_request(request)


def test_assignment_generator_preserves_structured_content_order(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    request = _request(
        tmp_path,
        objectives=("objective-b", "objective-a", "objective-c"),
        deliverables=("deliverable-b", "deliverable-a", "deliverable-c"),
        resources=("resource-b", "resource-a", "resource-c"),
    )

    generator.validate_request(request)
    plan = generator.plan(request)

    assert isinstance(plan, GenerationPlan)
    assert plan.generator_name == "assignment"
    assert len(plan.operations) == 1

    context = plan.operations[0].context
    assert tuple(context["objectives"]) == (
        "objective-b",
        "objective-a",
        "objective-c",
    )
    assert tuple(context["deliverables"]) == (
        "deliverable-b",
        "deliverable-a",
        "deliverable-c",
    )
    assert tuple(context["resources"]) == (
        "resource-b",
        "resource-a",
        "resource-c",
    )


def test_assignment_plan_uses_generation_plan_as_canonical_boundary(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path)

    generator.validate_request(request)
    plan = generator.plan(request)

    assert isinstance(plan, GenerationPlan)
    assert plan.generator_name == "assignment"
    assert len(plan.operations) == 1
    assert plan.operations[0].destination == (
        request.target / "week-04" / "assignment" / "streams-homework" / "README.md"
    )


def test_assignment_plan_uses_default_template(tmp_path: Path) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path)

    generator.validate_request(request)
    plan = generator.plan(request)

    assert len(plan.operations) == 1
    assert plan.operations[0].template_name == "assignment/README.md.j2"


def test_assignment_plan_destination_does_not_depend_on_title(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    original = _request(tmp_path, title="Streams Homework")
    renamed = _request(tmp_path, title="Stream Processing Practice")

    generator.validate_request(original)
    generator.validate_request(renamed)

    original_plan = generator.plan(original)
    renamed_plan = generator.plan(renamed)

    assert original_plan.operations[0].destination == renamed_plan.operations[0].destination


def test_assignment_plan_is_deterministic_for_same_request(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    request = _request(
        tmp_path,
        objectives=("first", "second"),
        deliverables=("one", "two"),
    )

    generator.validate_request(request)

    first = generator.plan(request)
    second = generator.plan(request)

    assert first == second


def test_invalid_assignment_request_fails_before_planning(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path, week=0)
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


def test_assignment_dry_run_preserves_no_filesystem_mutation(
    tmp_path: Path,
) -> None:
    template_root = tmp_path / "templates"
    template_file = template_root / "assignment" / "README.md.j2"
    template_file.parent.mkdir(parents=True)
    template_file.write_text(
        "# {{ title }}\n\nWeek {{ week }}\n",
        encoding="utf-8",
    )

    generator = AssignmentGenerator(template_root=template_root)
    request = _request(tmp_path, dry_run=True)

    result = generator.run(request)

    assert isinstance(result, GenerationResult)
    assert result.generator_name == "assignment"
    assert result.dry_run is True
    assert result.manifest_updated is False
    assert not request.target.exists()


def test_assignment_contract_does_not_require_specialized_result_types() -> None:
    import generator.core.models as models

    assert not hasattr(models, "AssignmentRequest")
    assert not hasattr(models, "AssignmentPlan")
    assert not hasattr(models, "AssignmentGenerationPlan")
    assert not hasattr(models, "AssignmentResult")
    assert not hasattr(models, "AssignmentGenerationResult")


def test_assignment_contract_does_not_expand_public_sdk() -> None:
    import generator.sdk as sdk

    forbidden_symbols = {
        "Assignment",
        "AssignmentGenerator",
        "AssignmentRequest",
        "AssignmentPlan",
        "AssignmentResult",
        "Deliverable",
        "Rubric",
    }

    assert forbidden_symbols.isdisjoint(set(dir(sdk)))
