"""Courseware composition orchestration for OpenProjectLab."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from generator.core.models import GenerateRequest, GenerationResult
from generator.generators.base import BaseGenerator
from generator.plugins.registry import GeneratorRegistry


class CoursewareComposer:
    """Coordinate deterministic execution of ordered generator requests."""

    def __init__(self, registry: GeneratorRegistry) -> None:
        """Create a composer backed by the existing generator registry."""
        self._registry = registry

    def plan(
        self,
        requests: Sequence[GenerateRequest],
    ) -> tuple[GenerateRequest, ...]:
        """Build an immutable composition plan while preserving authored order."""
        self._validate_requests(requests)
        return tuple(requests)

    def run(
        self,
        requests: Sequence[GenerateRequest],
    ) -> tuple[GenerationResult, ...]:
        """Resolve all generators, then execute the plan sequentially."""
        plan = self.plan(requests)

        # Preflight every resolution before any generator executes. This avoids
        # filesystem side effects when a later required generator is missing.
        resolved = tuple((request, self._resolve(request.generator_name)) for request in plan)

        results: list[GenerationResult] = []
        for request, generator in resolved:
            try:
                results.append(generator.run(request))
            except Exception as exc:
                # Preserve the original exception type when its message already
                # identifies the failing generator. Otherwise add composition
                # context while retaining the original exception as the cause.
                if request.generator_name in str(exc):
                    raise
                raise RuntimeError(
                    f"courseware composition failed for generator {request.generator_name!r}"
                ) from exc

        return tuple(results)

    def _resolve(self, generator_name: str) -> BaseGenerator:
        """Resolve and instantiate a generator through the shared registry."""
        generator_class = self._registry.get(generator_name)
        return generator_class()

    @staticmethod
    def _validate_requests(requests: object) -> None:
        """Validate the minimum ordered GenerateRequest sequence contract."""
        if isinstance(requests, (str, bytes, bytearray, Mapping)):
            raise TypeError("composition requests must be an ordered GenerateRequest sequence")

        if not isinstance(requests, Sequence):
            raise TypeError("composition requests must be an ordered GenerateRequest sequence")

        for request in requests:
            if not isinstance(request, GenerateRequest):
                raise TypeError("composition requests must contain only GenerateRequest values")
