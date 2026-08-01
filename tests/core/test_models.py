"""Test the core runtime models used by generation workflows."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from generator.core.models import (
    GenerateRequest,
    GenerationOperation,
    GenerationPlan,
    GenerationResult,
    RuntimeOptions,
    WritePolicy,
    WriteResult,
    WriteStatus,
)


class TestRuntimeOptions:
    """Test runtime option defaults, policies, and immutability."""

    def test_defaults(self) -> None:
        """Use safe runtime defaults when no options are specified."""
        options = RuntimeOptions()

        assert options.dry_run is False
        assert options.overwrite is False
        assert options.verbose is False
        assert options.force is False
        assert options.write_policy is WritePolicy.CREATE_ONLY

    def test_overwrite_selects_overwrite_policy(self) -> None:
        """Select the overwrite policy when overwrite is enabled."""
        options = RuntimeOptions(overwrite=True)

        assert options.write_policy is WritePolicy.OVERWRITE

    def test_instance_is_immutable(self) -> None:
        """Prevent runtime options from being modified after creation."""
        options = RuntimeOptions()

        with pytest.raises(FrozenInstanceError):
            options.dry_run = True  # type: ignore[misc]


class TestGenerateRequest:
    """Test generator request validation and normalization."""

    def test_normalizes_name_target_and_values(self) -> None:
        """Normalize request fields and copy the supplied value mapping."""
        source = {"course_name": "Modern Java"}

        request = GenerateRequest(
            generator_name=" course ",
            target=Path("courses/java"),
            values=source,
        )

        source["course_name"] = "Changed"

        assert request.generator_name == "course"
        assert request.target == Path("courses/java")
        assert request.values["course_name"] == "Modern Java"

    def test_accepts_string_target(self) -> None:
        """Convert a string target into a pathlib Path instance."""
        request = GenerateRequest(
            generator_name="course",
            target="courses/java",  # type: ignore[arg-type]
        )

        assert request.target == Path("courses/java")

    def test_values_are_read_only(self) -> None:
        """Prevent callers from modifying request values after creation."""
        request = GenerateRequest(
            generator_name="course",
            target=Path("courses/java"),
            values={"weeks": 16},
        )

        with pytest.raises(TypeError):
            request.values["weeks"] = 18  # type: ignore[index]

    @pytest.mark.parametrize(
        "generator_name",
        ["", " ", "\t"],
    )
    def test_rejects_empty_generator_name(
        self,
        generator_name: str,
    ) -> None:
        """Reject an empty or whitespace-only generator name."""
        with pytest.raises(
            ValueError,
            match="generator_name 不可為空",
        ):
            GenerateRequest(
                generator_name=generator_name,
                target=Path("output"),
            )


class TestGenerationOperation:
    """Test generation operation validation and normalization."""

    def test_normalizes_fields(self) -> None:
        """Normalize operation fields and copy the template context."""
        source_context = {"week": 1}

        operation = GenerationOperation(
            template_name=" week/README.md.j2 ",
            destination=Path("week-01/README.md"),
            context=source_context,
            write_policy=WritePolicy.SKIP_EXISTING,
        )

        source_context["week"] = 2

        assert operation.template_name == "week/README.md.j2"
        assert operation.destination == Path("week-01/README.md")
        assert operation.context["week"] == 1
        assert operation.write_policy is WritePolicy.SKIP_EXISTING

    def test_accepts_string_destination(self) -> None:
        """Convert a string destination into a pathlib Path instance."""
        operation = GenerationOperation(
            template_name="README.md.j2",
            destination="README.md",  # type: ignore[arg-type]
        )

        assert operation.destination == Path("README.md")

    def test_context_is_read_only(self) -> None:
        """Prevent callers from modifying template context after creation."""
        operation = GenerationOperation(
            template_name="README.md.j2",
            destination=Path("README.md"),
            context={"project_name": "OpenProjectLab"},
        )

        with pytest.raises(TypeError):
            operation.context["project_name"] = "Changed"  # type: ignore[index]

    def test_rejects_empty_template_name(self) -> None:
        """Reject an empty or whitespace-only template name."""
        with pytest.raises(
            ValueError,
            match="template_name 不可為空",
        ):
            GenerationOperation(
                template_name=" ",
                destination=Path("README.md"),
            )

    def test_rejects_empty_destination(self) -> None:
        """Reject a destination representing an empty current-path value."""
        with pytest.raises(
            ValueError,
            match="destination 不可為空",
        ):
            GenerationOperation(
                template_name="README.md.j2",
                destination=Path(),
            )


class TestGenerationPlan:
    """Test generation plan ordering, validation, and immutability."""

    def test_preserves_operation_order(self) -> None:
        """Preserve the deterministic order supplied by the generator."""
        first = GenerationOperation(
            template_name="README.md.j2",
            destination=Path("README.md"),
        )
        second = GenerationOperation(
            template_name="course.yaml.j2",
            destination=Path("course.yaml"),
        )

        plan = GenerationPlan(
            generator_name="bootstrap",
            operations=(first, second),
        )

        assert plan.operations == (first, second)
        assert plan.destinations() == (
            Path("README.md"),
            Path("course.yaml"),
        )

    def test_converts_operations_to_tuple(self) -> None:
        """Store operation collections as immutable tuples."""
        operation = GenerationOperation(
            template_name="README.md.j2",
            destination=Path("README.md"),
        )

        plan = GenerationPlan(
            generator_name="bootstrap",
            operations=[operation],  # type: ignore[arg-type]
        )

        assert plan.operations == (operation,)
        assert isinstance(plan.operations, tuple)

    def test_rejects_duplicate_destinations(self) -> None:
        """Reject multiple operations targeting the same destination."""
        first = GenerationOperation(
            template_name="first.j2",
            destination=Path("README.md"),
        )
        second = GenerationOperation(
            template_name="second.j2",
            destination=Path("README.md"),
        )

        with pytest.raises(
            ValueError,
            match="重複的 destination",
        ):
            GenerationPlan(
                generator_name="course",
                operations=(first, second),
            )

    @pytest.mark.parametrize(
        "generator_name",
        ["", " ", "\t"],
    )
    def test_rejects_empty_generator_name(
        self,
        generator_name: str,
    ) -> None:
        """Reject an empty or whitespace-only plan generator name."""
        with pytest.raises(
            ValueError,
            match="generator_name 不可為空",
        ):
            GenerationPlan(generator_name=generator_name)


class TestWriteResult:
    """Test filesystem write-result normalization."""

    def test_normalizes_path(self) -> None:
        """Convert a string write-result path into pathlib Path."""
        result = WriteResult(
            path="README.md",  # type: ignore[arg-type]
            status=WriteStatus.CREATED,
        )

        assert result.path == Path("README.md")

    def test_preserves_status(self) -> None:
        """Preserve the filesystem status assigned to a write result."""
        result = WriteResult(
            path=Path("README.md"),
            status=WriteStatus.UNCHANGED,
        )

        assert result.status is WriteStatus.UNCHANGED

    def test_instance_is_immutable(self) -> None:
        """Prevent a write result from being modified after creation."""
        result = WriteResult(
            path=Path("README.md"),
            status=WriteStatus.CREATED,
        )

        with pytest.raises(FrozenInstanceError):
            result.status = WriteStatus.UPDATED  # type: ignore[misc]


class TestGenerationResult:
    """Test aggregation and classification of generation write results."""

    def test_groups_paths_by_status(self) -> None:
        """Group affected paths according to their write status."""
        result = GenerationResult(
            generator_name="course",
            writes=(
                WriteResult(
                    Path("README.md"),
                    WriteStatus.CREATED,
                ),
                WriteResult(
                    Path("course.yaml"),
                    WriteStatus.UPDATED,
                ),
                WriteResult(
                    Path("notes.md"),
                    WriteStatus.SKIPPED,
                ),
                WriteResult(
                    Path("LICENSE"),
                    WriteStatus.UNCHANGED,
                ),
            ),
        )

        assert result.created == (Path("README.md"),)
        assert result.updated == (Path("course.yaml"),)
        assert result.skipped == (Path("notes.md"),)
        assert result.unchanged == (Path("LICENSE"),)

    def test_counts_matching_statuses(self) -> None:
        """Count write results with a requested status."""
        result = GenerationResult(
            generator_name="bootstrap",
            writes=(
                WriteResult(
                    Path("README.md"),
                    WriteStatus.CREATED,
                ),
                WriteResult(
                    Path("LICENSE"),
                    WriteStatus.CREATED,
                ),
                WriteResult(
                    Path("course.yaml"),
                    WriteStatus.SKIPPED,
                ),
            ),
        )

        assert result.count(WriteStatus.CREATED) == 2
        assert result.count(WriteStatus.SKIPPED) == 1
        assert result.count(WriteStatus.UPDATED) == 0

    def test_returns_all_affected_paths_in_order(self) -> None:
        """Return all paths in the original write-result order."""
        result = GenerationResult(
            generator_name="course",
            writes=(
                WriteResult(
                    Path("README.md"),
                    WriteStatus.CREATED,
                ),
                WriteResult(
                    Path("course.yaml"),
                    WriteStatus.UPDATED,
                ),
            ),
        )

        assert result.affected_paths == (
            Path("README.md"),
            Path("course.yaml"),
        )

    def test_converts_writes_and_warnings_to_tuples(self) -> None:
        """Store writes and warnings as immutable tuple collections."""
        write = WriteResult(
            Path("README.md"),
            WriteStatus.CREATED,
        )

        result = GenerationResult(
            generator_name="week",
            writes=[write],  # type: ignore[arg-type]
            warnings=["檔案已存在"],  # type: ignore[arg-type]
            dry_run=True,
        )

        assert result.writes == (write,)
        assert result.warnings == ("檔案已存在",)
        assert result.dry_run is True
        assert result.manifest_updated is False

    def test_defaults_to_empty_result_collections(self) -> None:
        """Use empty immutable collections for a result without writes."""
        result = GenerationResult(generator_name="week")

        assert result.writes == ()
        assert result.warnings == ()
        assert result.created == ()
        assert result.updated == ()
        assert result.skipped == ()
        assert result.unchanged == ()
        assert result.affected_paths == ()

    @pytest.mark.parametrize(
        "generator_name",
        ["", " ", "\t"],
    )
    def test_rejects_empty_generator_name(
        self,
        generator_name: str,
    ) -> None:
        """Reject an empty or whitespace-only result generator name."""
        with pytest.raises(
            ValueError,
            match="generator_name 不可為空",
        ):
            GenerationResult(generator_name=generator_name)

    def test_instance_is_immutable(self) -> None:
        """Prevent a generation result from changing after creation."""
        result = GenerationResult(generator_name="course")

        with pytest.raises(FrozenInstanceError):
            result.dry_run = True  # type: ignore[misc]
