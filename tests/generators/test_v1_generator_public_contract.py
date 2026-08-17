"""Freeze the OpenProjectLab v1 public Generator core contract."""

from pathlib import Path

import pytest

from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationOperation,
    GenerationPlan,
    GenerationResult,
    RuntimeOptions,
    WritePolicy,
    WriteResult,
    WriteStatus,
)


class RecordingGenerator(BaseGenerator):
    """Record the canonical BaseGenerator lifecycle for contract verification."""

    name = "recording"

    def __init__(self) -> None:
        super().__init__()
        self.calls: list[str] = []

    def validate_request(self, request: GenerateRequest) -> None:
        """Record validation before planning."""
        assert request.generator_name == self.name
        self.calls.append("validate")

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Record planning and return a deterministic empty plan."""
        assert request.generator_name == self.name
        self.calls.append("plan")
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Record execution and return the shared result contract."""
        assert request.generator_name == self.name
        assert plan.generator_name == self.name
        self.calls.append("execute")
        return GenerationResult(generator_name=self.name)


def test_generate_request_normalizes_public_fields(tmp_path: Path) -> None:
    """Normalize generator identity and target through the public request contract."""
    request = GenerateRequest(
        generator_name="  demo  ",
        target=tmp_path / "course",
        values={"week": 1},
    )

    assert request.generator_name == "demo"
    assert request.target == Path(tmp_path / "course")
    assert request.values == {"week": 1}
    assert request.options == RuntimeOptions()


def test_generate_request_values_are_read_only(tmp_path: Path) -> None:
    """Protect request values from mutation after construction."""
    request = GenerateRequest(
        generator_name="demo",
        target=tmp_path,
        values={"week": 1},
    )

    with pytest.raises(TypeError):
        request.values["week"] = 2


@pytest.mark.parametrize(
    ("options", "expected"),
    [
        (RuntimeOptions(), WritePolicy.CREATE_ONLY),
        (RuntimeOptions(overwrite=False), WritePolicy.CREATE_ONLY),
        (RuntimeOptions(overwrite=True), WritePolicy.OVERWRITE),
    ],
)
def test_runtime_options_map_to_write_policy(
    options: RuntimeOptions,
    expected: WritePolicy,
) -> None:
    """Freeze the v1 RuntimeOptions-to-WritePolicy mapping."""
    assert options.write_policy is expected


def test_runtime_options_defaults_are_stable() -> None:
    """Freeze the reviewed v1 RuntimeOptions defaults."""
    options = RuntimeOptions()

    assert options.dry_run is False
    assert options.overwrite is False
    assert options.verbose is False
    assert options.force is False


def test_generation_operation_normalizes_and_freezes_context() -> None:
    """Normalize operation fields and expose read-only context."""
    operation = GenerationOperation(
        template_name="  README.md.j2  ",
        destination="week-01/README.md",
        context={"title": "Week 01"},
        write_policy=WritePolicy.SKIP_EXISTING,
    )

    assert operation.template_name == "README.md.j2"
    assert operation.destination == Path("week-01/README.md")
    assert operation.context == {"title": "Week 01"}
    assert operation.write_policy is WritePolicy.SKIP_EXISTING

    with pytest.raises(TypeError):
        operation.context["title"] = "Changed"


def test_generation_plan_preserves_operation_order() -> None:
    """Preserve authored operation ordering in the public plan contract."""
    first = GenerationOperation(
        template_name="first.j2",
        destination="first.md",
    )
    second = GenerationOperation(
        template_name="second.j2",
        destination="second.md",
    )

    plan = GenerationPlan(
        generator_name="demo",
        operations=[first, second],
    )

    assert plan.operations == (first, second)
    assert plan.destinations() == (
        Path("first.md"),
        Path("second.md"),
    )


def test_generation_plan_rejects_duplicate_destinations() -> None:
    """Reject ambiguous plans containing duplicate destination paths."""
    first = GenerationOperation(
        template_name="first.j2",
        destination="README.md",
    )
    second = GenerationOperation(
        template_name="second.j2",
        destination="README.md",
    )

    with pytest.raises(ValueError):
        GenerationPlan(
            generator_name="demo",
            operations=(first, second),
        )


def test_generation_result_exposes_status_path_projections() -> None:
    """Freeze the v1 status-specific result projections and ordering."""
    writes = (
        WriteResult(Path("created.md"), WriteStatus.CREATED),
        WriteResult(Path("updated.md"), WriteStatus.UPDATED),
        WriteResult(Path("skipped.md"), WriteStatus.SKIPPED),
        WriteResult(Path("unchanged.md"), WriteStatus.UNCHANGED),
    )

    result = GenerationResult(
        generator_name="demo",
        writes=writes,
        warnings=["warning"],
        dry_run=True,
        manifest_updated=True,
    )

    assert result.writes == writes
    assert result.warnings == ("warning",)
    assert result.dry_run is True
    assert result.manifest_updated is True

    assert result.created == (Path("created.md"),)
    assert result.updated == (Path("updated.md"),)
    assert result.skipped == (Path("skipped.md"),)
    assert result.unchanged == (Path("unchanged.md"),)
    assert result.affected_paths == (
        Path("created.md"),
        Path("updated.md"),
        Path("skipped.md"),
        Path("unchanged.md"),
    )


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (WriteStatus.CREATED, 2),
        (WriteStatus.UPDATED, 1),
        (WriteStatus.SKIPPED, 0),
        (WriteStatus.UNCHANGED, 0),
    ],
)
def test_generation_result_count(
    status: WriteStatus,
    expected: int,
) -> None:
    """Count write results by the shared v1 WriteStatus contract."""
    result = GenerationResult(
        generator_name="demo",
        writes=(
            WriteResult("a.md", WriteStatus.CREATED),
            WriteResult("b.md", WriteStatus.CREATED),
            WriteResult("c.md", WriteStatus.UPDATED),
        ),
    )

    assert result.count(status) == expected


def test_base_generator_run_enforces_canonical_lifecycle(
    tmp_path: Path,
) -> None:
    """Run validation, planning, and execution in the canonical v1 order."""
    generator = RecordingGenerator()
    request = GenerateRequest(
        generator_name=generator.name,
        target=tmp_path,
    )

    result = generator.run(request)

    assert generator.calls == [
        "validate",
        "plan",
        "execute",
    ]
    assert result == GenerationResult(generator_name=generator.name)
