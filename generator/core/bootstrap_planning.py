"""Deterministic, side-effect-free Bootstrap planning primitives."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import PurePath
from typing import Any

from generator.core.exceptions import GeneratorNotFoundError, ValidationError
from generator.core.registry import GeneratorRegistry

type FrozenScalar = str | int | float | bool | None

type FrozenValue = FrozenScalar | tuple["FrozenValue", ...] | tuple[tuple[str, "FrozenValue"], ...]

type FrozenMapping = tuple[tuple[str, FrozenValue], ...]


def _freeze_value(value: Any) -> FrozenValue:
    """Convert supported planning values into deterministic immutable data."""
    if value is None or isinstance(value, str | int | float | bool):
        return value

    if isinstance(value, Mapping):
        return tuple(
            (str(key), _freeze_value(item))
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        )

    if isinstance(value, (list, tuple)):
        return tuple(_freeze_value(item) for item in value)

    if isinstance(value, (set, frozenset)):
        frozen = tuple(_freeze_value(item) for item in value)
        return tuple(sorted(frozen, key=repr))

    if isinstance(value, PurePath):
        return str(value)

    raise TypeError(f"Unsupported bootstrap planning value: {type(value).__name__}")


def _freeze_mapping(values: Mapping[str, Any] | None) -> FrozenMapping:
    """Return a stable immutable representation of a string-keyed mapping."""
    if values is None:
        return ()

    return tuple(
        (str(key), _freeze_value(value))
        for key, value in sorted(values.items(), key=lambda pair: str(pair[0]))
    )


@dataclass(frozen=True, slots=True, order=True)
class ExpectedEffect:
    """Describe one future apply-phase effect without performing it."""

    kind: str
    target: str
    metadata: FrozenMapping = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Normalize and validate effect fields."""
        kind = self.kind.strip().lower()
        target = self.target.strip()

        if not kind:
            raise ValueError("effect kind must not be empty")
        if not target:
            raise ValueError("effect target must not be empty")

        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "target", target)
        object.__setattr__(
            self,
            "metadata",
            _freeze_mapping(dict(self.metadata))
            if isinstance(self.metadata, Mapping)
            else tuple(self.metadata),
        )

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> ExpectedEffect:
        """Construct an effect from descriptive mapping data."""
        try:
            kind = str(value["kind"])
            target = str(value["target"])
        except KeyError as exc:
            raise ValueError("Expected effect requires 'kind' and 'target'") from exc

        metadata = value.get("metadata")
        if metadata is not None and not isinstance(metadata, Mapping):
            raise TypeError("effect metadata must be a mapping")

        return cls(
            kind=kind,
            target=target,
            metadata=_freeze_mapping(metadata),
        )


@dataclass(frozen=True, slots=True)
class BootstrapStep:
    """Describe one ordered bootstrap planning step without executing it."""

    step_id: str
    generator_id: str
    normalized_inputs: FrozenMapping = field(default_factory=tuple)
    expected_effects: tuple[ExpectedEffect, ...] = ()
    mutation_allowed: bool = False

    def __post_init__(self) -> None:
        """Normalize and validate step fields."""
        step_id = self.step_id.strip()
        generator_id = self.generator_id.strip().lower()

        if not step_id:
            raise ValueError("step_id must not be empty")
        if not generator_id:
            raise ValueError("generator_id must not be empty")

        object.__setattr__(self, "step_id", step_id)
        object.__setattr__(self, "generator_id", generator_id)
        object.__setattr__(
            self,
            "normalized_inputs",
            _freeze_mapping(dict(self.normalized_inputs))
            if isinstance(self.normalized_inputs, Mapping)
            else tuple(self.normalized_inputs),
        )
        object.__setattr__(
            self,
            "expected_effects",
            tuple(self.expected_effects),
        )


@dataclass(frozen=True, slots=True)
class BootstrapPlan:
    """Represent a deterministic, inspectable bootstrap planning result."""

    normalized_intent: FrozenMapping
    steps: tuple[BootstrapStep, ...]
    expected_effects: tuple[ExpectedEffect, ...]

    def __post_init__(self) -> None:
        """Normalize immutable plan collections and validate identities."""
        object.__setattr__(
            self,
            "normalized_intent",
            _freeze_mapping(dict(self.normalized_intent))
            if isinstance(self.normalized_intent, Mapping)
            else tuple(self.normalized_intent),
        )
        object.__setattr__(self, "steps", tuple(self.steps))
        object.__setattr__(
            self,
            "expected_effects",
            tuple(self.expected_effects),
        )

        step_ids = tuple(step.step_id for step in self.steps)
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("BootstrapPlan contains duplicate step_id values")

    @property
    def generator_ids(self) -> tuple[str, ...]:
        """Return planned generator identities in deterministic order."""
        return tuple(step.generator_id for step in self.steps)


class BootstrapPlanner:
    """Build deterministic bootstrap plans without side effects."""

    def __init__(self, registry: GeneratorRegistry) -> None:
        self._registry = registry

    def plan(
        self,
        *,
        intent: Mapping[str, Any] | None,
        generator_names: Sequence[str],
        inputs_by_generator: Mapping[str, Mapping[str, Any]] | None = None,
        effects_by_generator: (
            Mapping[
                str,
                Sequence[ExpectedEffect | Mapping[str, Any]],
            ]
            | None
        ) = None,
    ) -> BootstrapPlan:
        """Build a deterministic plan without creating or executing generators."""
        normalized_names = tuple(sorted(name.strip().lower() for name in generator_names))

        if any(not name for name in normalized_names):
            raise ValidationError("Generator name must not be empty")

        if len(normalized_names) != len(set(normalized_names)):
            raise ValidationError("Bootstrap plan must not contain duplicate generators")

        available = set(self._registry.names())
        unknown = tuple(name for name in normalized_names if name not in available)
        if unknown:
            raise GeneratorNotFoundError("Unknown Generator(s): " + ", ".join(unknown))

        normalized_inputs_source = {
            key.strip().lower(): value for key, value in (inputs_by_generator or {}).items()
        }
        normalized_effects_source = {
            key.strip().lower(): value for key, value in (effects_by_generator or {}).items()
        }

        steps: list[BootstrapStep] = []
        all_effects: list[ExpectedEffect] = []

        for index, generator_id in enumerate(normalized_names, start=1):
            inputs = _freeze_mapping(normalized_inputs_source.get(generator_id))
            effects = tuple(
                self._normalize_effect(effect)
                for effect in normalized_effects_source.get(
                    generator_id,
                    (),
                )
            )
            effects = tuple(sorted(effects))

            step = BootstrapStep(
                step_id=f"{index:04d}:{generator_id}",
                generator_id=generator_id,
                normalized_inputs=inputs,
                expected_effects=effects,
                mutation_allowed=bool(effects),
            )
            steps.append(step)
            all_effects.extend(effects)

        return BootstrapPlan(
            normalized_intent=_freeze_mapping(intent),
            steps=tuple(steps),
            expected_effects=tuple(all_effects),
        )

    @staticmethod
    def _normalize_effect(
        effect: ExpectedEffect | Mapping[str, Any],
    ) -> ExpectedEffect:
        """Normalize descriptive expected-effect input."""
        if isinstance(effect, ExpectedEffect):
            return effect
        if isinstance(effect, Mapping):
            return ExpectedEffect.from_mapping(effect)
        raise TypeError("Expected effects must be ExpectedEffect values or mappings")
