"""Contract tests for the proposed Lab Generator."""

from __future__ import annotations

from pathlib import Path

import pytest

from generator.core.exceptions import GeneratorValidationError
from generator.core.models import GenerateRequest, GenerationPlan, GenerationResult, RuntimeOptions

pytest.importorskip(
    "generator.generators.lab_generator",
    reason="LabGenerator implementation lands in Step 5.3C",
)

from generator.generators.lab_generator import LabGenerator


def _request(
    tmp_path: Path,
    *,
    generator_name: str = "lab",
    week: object = 3,
    lab_id: object = "streams-practice",
    title: object = "Streams Practice",
    dry_run: bool = True,
    overwrite: bool = False,
) -> GenerateRequest:
    return GenerateRequest(
        generator_name=generator_name,
        target=tmp_path / "course",
        values={
            "week": week,
            "lab_id": lab_id,
            "title": title,
            "record_manifest": False,
        },
        options=RuntimeOptions(
            dry_run=dry_run,
            overwrite=overwrite,
        ),
    )


def _generator(tmp_path: Path) -> LabGenerator:
    return LabGenerator(template_root=tmp_path / "templates")


def test_lab_generator_has_canonical_identity() -> None:
    assert LabGenerator.name == "lab"


def test_lab_generator_accepts_minimum_valid_request(tmp_path: Path) -> None:
    generator = _generator(tmp_path)

    generator.validate_request(_request(tmp_path))


@pytest.mark.parametrize("week", [0, -1, -10])
def test_lab_generator_rejects_non_positive_week(
    tmp_path: Path,
    week: int,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, week=week))

    assert exc_info.value.generator == "lab"
    assert exc_info.value.field == "week"


@pytest.mark.parametrize("week", [True, False])
def test_lab_generator_rejects_bool_week(
    tmp_path: Path,
    week: bool,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, week=week))

    assert exc_info.value.generator == "lab"
    assert exc_info.value.field == "week"


@pytest.mark.parametrize("week", ["3", 3.0, None])
def test_lab_generator_rejects_non_integer_week(
    tmp_path: Path,
    week: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, week=week))

    assert exc_info.value.field == "week"


@pytest.mark.parametrize("lab_id", ["", "   "])
def test_lab_generator_rejects_empty_lab_id(
    tmp_path: Path,
    lab_id: str,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, lab_id=lab_id))

    assert exc_info.value.generator == "lab"
    assert exc_info.value.field == "lab_id"


@pytest.mark.parametrize(
    "lab_id",
    [
        "../streams",
        "labs/streams",
        r"labs\streams",
        "/absolute",
    ],
)
def test_lab_generator_rejects_path_like_lab_id(
    tmp_path: Path,
    lab_id: str,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, lab_id=lab_id))

    assert exc_info.value.field == "lab_id"


@pytest.mark.parametrize("lab_id", [None, 3, True])
def test_lab_generator_rejects_non_string_lab_id(
    tmp_path: Path,
    lab_id: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, lab_id=lab_id))

    assert exc_info.value.field == "lab_id"


@pytest.mark.parametrize("title", ["", "   "])
def test_lab_generator_rejects_empty_title(
    tmp_path: Path,
    title: str,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, title=title))

    assert exc_info.value.generator == "lab"
    assert exc_info.value.field == "title"


@pytest.mark.parametrize("title", [None, 3, True])
def test_lab_generator_rejects_non_string_title(
    tmp_path: Path,
    title: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, title=title))

    assert exc_info.value.field == "title"


def test_lab_generator_rejects_wrong_generator_name(tmp_path: Path) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(
            _request(tmp_path, generator_name="week"),
        )

    assert exc_info.value.generator == "lab"
    assert exc_info.value.field == "generator_name"


def test_lab_plan_uses_generation_plan_as_canonical_boundary(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path)

    generator.validate_request(request)
    plan = generator.plan(request)

    assert isinstance(plan, GenerationPlan)
    assert plan.generator_name == "lab"
    assert len(plan.operations) == 1
    assert plan.operations[0].destination == (
        request.target / "week-03" / "lab" / "streams-practice" / "README.md"
    )


def test_lab_plan_destination_does_not_depend_on_title(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    original = _request(tmp_path, title="Streams Practice")
    renamed = _request(tmp_path, title="Stream Processing Lab")

    generator.validate_request(original)
    generator.validate_request(renamed)

    original_plan = generator.plan(original)
    renamed_plan = generator.plan(renamed)

    assert original_plan.operations[0].destination == renamed_plan.operations[0].destination


def test_invalid_lab_request_fails_before_planning(
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


def test_lab_dry_run_preserves_no_filesystem_mutation(
    tmp_path: Path,
) -> None:
    template_root = tmp_path / "templates"
    template_file = template_root / "lab" / "README.md.j2"
    template_file.parent.mkdir(parents=True)
    template_file.write_text(
        "# {{ title }}\n\nWeek {{ week }}\n",
        encoding="utf-8",
    )

    generator = LabGenerator(template_root=template_root)
    request = _request(tmp_path, dry_run=True)

    result = generator.run(request)

    assert isinstance(result, GenerationResult)
    assert result.generator_name == "lab"
    assert result.dry_run is True
    assert result.manifest_updated is False
    assert not request.target.exists()
