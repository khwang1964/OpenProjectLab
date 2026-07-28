"""Define immutable runtime models for generation workflows."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any


class WritePolicy(str, Enum):
    """Define how an existing destination should be handled."""

    CREATE_ONLY = "create-only"
    OVERWRITE = "overwrite"
    SKIP_EXISTING = "skip-existing"


class WriteStatus(str, Enum):
    """Describe the outcome of a filesystem write operation."""

    CREATED = "created"
    UPDATED = "updated"
    SKIPPED = "skipped"
    UNCHANGED = "unchanged"


def _immutable_mapping(
    values: Mapping[str, Any] | None,
) -> Mapping[str, Any]:
    """Return a shallow, read-only copy of a mapping."""
    return MappingProxyType(dict(values or {}))


@dataclass(frozen=True, slots=True)
class RuntimeOptions:
    """Represent options affecting one generator execution."""

    dry_run: bool = False
    overwrite: bool = False
    verbose: bool = False
    force: bool = False

    @property
    def write_policy(self) -> WritePolicy:
        """Return the effective write policy."""
        if self.overwrite:
            return WritePolicy.OVERWRITE

        return WritePolicy.CREATE_ONLY


@dataclass(frozen=True, slots=True)
class GenerateRequest:
    """Describe one generator request."""

    generator_name: str
    target: Path
    values: Mapping[str, Any] = field(default_factory=dict)
    options: RuntimeOptions = field(default_factory=RuntimeOptions)

    def __post_init__(self) -> None:
        """Normalize and validate request fields."""
        normalized_name = self.generator_name.strip()

        if not normalized_name:
            raise ValueError("generator_name 不可為空")

        object.__setattr__(self, "generator_name", normalized_name)
        object.__setattr__(self, "target", Path(self.target))
        object.__setattr__(
            self,
            "values",
            _immutable_mapping(self.values),
        )


@dataclass(frozen=True, slots=True)
class GenerationOperation:
    """Describe one planned template-to-file operation."""

    template_name: str
    destination: Path
    context: Mapping[str, Any] = field(default_factory=dict)
    write_policy: WritePolicy = WritePolicy.CREATE_ONLY

    def __post_init__(self) -> None:
        """Normalize and validate operation fields."""
        normalized_template = self.template_name.strip()
        destination = Path(self.destination)

        if not normalized_template:
            raise ValueError("template_name 不可為空")

        if str(destination) in {"", "."}:
            raise ValueError("destination 不可為空")

        object.__setattr__(
            self,
            "template_name",
            normalized_template,
        )
        object.__setattr__(
            self,
            "destination",
            destination,
        )
        object.__setattr__(
            self,
            "context",
            _immutable_mapping(self.context),
        )


@dataclass(frozen=True, slots=True)
class GenerationPlan:
    """Describe all operations planned by a generator."""

    generator_name: str
    operations: tuple[GenerationOperation, ...] = ()

    def __post_init__(self) -> None:
        """Normalize and validate generation-plan fields."""
        normalized_name = self.generator_name.strip()
        operations = tuple(self.operations)

        if not normalized_name:
            raise ValueError("generator_name 不可為空")

        destinations = tuple(operation.destination for operation in operations)

        if len(destinations) != len(set(destinations)):
            raise ValueError("GenerationPlan 不可包含重複的 destination")

        object.__setattr__(
            self,
            "generator_name",
            normalized_name,
        )
        object.__setattr__(
            self,
            "operations",
            operations,
        )

    def destinations(self) -> tuple[Path, ...]:
        """Return planned destinations in operation order."""
        return tuple(operation.destination for operation in self.operations)


@dataclass(frozen=True, slots=True)
class WriteResult:
    """Describe the result of one filesystem write operation."""

    path: Path
    status: WriteStatus

    def __post_init__(self) -> None:
        """Normalize the result path."""
        object.__setattr__(self, "path", Path(self.path))


@dataclass(frozen=True, slots=True)
class GenerationResult:
    """Describe the result of one generator execution."""

    generator_name: str
    writes: tuple[WriteResult, ...] = ()
    warnings: tuple[str, ...] = ()
    dry_run: bool = False
    manifest_updated: bool = False

    def __post_init__(self) -> None:
        """Normalize and validate result fields."""
        normalized_name = self.generator_name.strip()

        if not normalized_name:
            raise ValueError("generator_name 不可為空")

        object.__setattr__(
            self,
            "generator_name",
            normalized_name,
        )
        object.__setattr__(
            self,
            "writes",
            tuple(self.writes),
        )
        object.__setattr__(
            self,
            "warnings",
            tuple(self.warnings),
        )

    @property
    def created(self) -> tuple[Path, ...]:
        """Return files created during execution."""
        return self._paths_with_status(WriteStatus.CREATED)

    @property
    def updated(self) -> tuple[Path, ...]:
        """Return files updated during execution."""
        return self._paths_with_status(WriteStatus.UPDATED)

    @property
    def skipped(self) -> tuple[Path, ...]:
        """Return files skipped during execution."""
        return self._paths_with_status(WriteStatus.SKIPPED)

    @property
    def unchanged(self) -> tuple[Path, ...]:
        """Return files whose content was unchanged."""
        return self._paths_with_status(WriteStatus.UNCHANGED)

    @property
    def affected_paths(self) -> tuple[Path, ...]:
        """Return all paths referenced by write results."""
        return tuple(result.path for result in self.writes)

    def count(self, status: WriteStatus) -> int:
        """Count results matching a write status."""
        return sum(result.status is status for result in self.writes)

    def _paths_with_status(
        self,
        status: WriteStatus,
    ) -> tuple[Path, ...]:
        """Return paths matching a write status."""
        return tuple(result.path for result in self.writes if result.status is status)


def normalize_operations(
    operations: Sequence[GenerationOperation],
) -> tuple[GenerationOperation, ...]:
    """Convert an operation sequence into an immutable tuple."""
    return tuple(operations)
