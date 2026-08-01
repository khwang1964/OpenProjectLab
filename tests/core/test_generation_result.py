"""Test the GenerationResult runtime contract."""

from pathlib import Path

import pytest

from generator.core.models import GenerationResult, WriteResult, WriteStatus


@pytest.fixture
def generation_result() -> GenerationResult:
    """Return a result containing every supported write status."""
    return GenerationResult(
        generator_name="bootstrap",
        writes=(
            WriteResult(
                path=Path("output/created.txt"),
                status=WriteStatus.CREATED,
            ),
            WriteResult(
                path=Path("output/updated.txt"),
                status=WriteStatus.UPDATED,
            ),
            WriteResult(
                path=Path("output/skipped.txt"),
                status=WriteStatus.SKIPPED,
            ),
            WriteResult(
                path=Path("output/unchanged.txt"),
                status=WriteStatus.UNCHANGED,
            ),
        ),
        warnings=("Example warning",),
        dry_run=True,
        manifest_updated=True,
    )


def test_generation_result_normalizes_generator_name() -> None:
    """Generator names should be stripped during initialization."""
    result = GenerationResult(generator_name="  bootstrap  ")

    assert result.generator_name == "bootstrap"


def test_generation_result_rejects_empty_generator_name() -> None:
    """An empty generator name should be rejected."""
    with pytest.raises(ValueError, match="generator_name 不可為空"):
        GenerationResult(generator_name="   ")


def test_generation_result_normalizes_writes_to_tuple() -> None:
    """Write results should be stored as an immutable tuple."""
    write = WriteResult(
        path=Path("output/README.md"),
        status=WriteStatus.CREATED,
    )

    result = GenerationResult(
        generator_name="bootstrap",
        writes=[write],  # type: ignore[arg-type]
    )

    assert result.writes == (write,)
    assert isinstance(result.writes, tuple)


def test_generation_result_normalizes_warnings_to_tuple() -> None:
    """Warnings should be stored as an immutable tuple."""
    result = GenerationResult(
        generator_name="bootstrap",
        warnings=["First warning", "Second warning"],  # type: ignore[arg-type]
    )

    assert result.warnings == (
        "First warning",
        "Second warning",
    )
    assert isinstance(result.warnings, tuple)


def test_created_returns_created_paths(
    generation_result: GenerationResult,
) -> None:
    """The created property should return only created paths."""
    assert generation_result.created == (Path("output/created.txt"),)


def test_updated_returns_updated_paths(
    generation_result: GenerationResult,
) -> None:
    """The updated property should return only updated paths."""
    assert generation_result.updated == (Path("output/updated.txt"),)


def test_skipped_returns_skipped_paths(
    generation_result: GenerationResult,
) -> None:
    """The skipped property should return only skipped paths."""
    assert generation_result.skipped == (Path("output/skipped.txt"),)


def test_unchanged_returns_unchanged_paths(
    generation_result: GenerationResult,
) -> None:
    """The unchanged property should return only unchanged paths."""
    assert generation_result.unchanged == (Path("output/unchanged.txt"),)


def test_affected_paths_preserves_write_order(
    generation_result: GenerationResult,
) -> None:
    """Affected paths should preserve the original write-result order."""
    assert generation_result.affected_paths == (
        Path("output/created.txt"),
        Path("output/updated.txt"),
        Path("output/skipped.txt"),
        Path("output/unchanged.txt"),
    )


@pytest.mark.parametrize(
    ("status", "expected_count"),
    [
        (WriteStatus.CREATED, 1),
        (WriteStatus.UPDATED, 1),
        (WriteStatus.SKIPPED, 1),
        (WriteStatus.UNCHANGED, 1),
    ],
)
def test_count_returns_number_of_matching_write_results(
    generation_result: GenerationResult,
    status: WriteStatus,
    expected_count: int,
) -> None:
    """The count method should count results matching one status."""
    assert generation_result.count(status) == expected_count


def test_count_returns_zero_when_status_is_absent() -> None:
    """The count method should return zero for an absent status."""
    result = GenerationResult(
        generator_name="bootstrap",
        writes=(
            WriteResult(
                path=Path("output/README.md"),
                status=WriteStatus.CREATED,
            ),
        ),
    )

    assert result.count(WriteStatus.UPDATED) == 0


def test_empty_generation_result_has_no_affected_paths() -> None:
    """A result without writes should expose empty path collections."""
    result = GenerationResult(generator_name="bootstrap")

    assert result.writes == ()
    assert result.created == ()
    assert result.updated == ()
    assert result.skipped == ()
    assert result.unchanged == ()
    assert result.affected_paths == ()


def test_generation_result_preserves_execution_metadata(
    generation_result: GenerationResult,
) -> None:
    """Execution metadata should remain available to callers."""
    assert generation_result.warnings == ("Example warning",)
    assert generation_result.dry_run is True
    assert generation_result.manifest_updated is True


def test_affected_paths_is_immutable(
    generation_result: GenerationResult,
) -> None:
    """Affected paths should be exposed as an immutable tuple."""
    assert isinstance(generation_result.affected_paths, tuple)
