from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto

from generator.core.models import (
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
)


class GeneratorState(Enum):
    """表示 Generator 執行生命週期狀態。"""

    CREATED = auto()
    VALIDATED = auto()
    PREPARED = auto()
    GENERATED = auto()
    COMPLETED = auto()
    FAILED = auto()


class BaseGenerator(ABC):
    """定義所有 Generator 共用的執行生命週期。"""

    name = "base"

    def __init__(self) -> None:
        """建立尚未執行的 Generator。"""
        self.state = GeneratorState.CREATED

    def run(self, request: GenerateRequest) -> GenerationResult:
        """Run the framework-controlled generator execution lifecycle.

        The lifecycle order is fixed:

        1. validate the request
        2. build an immutable generation plan
        3. execute or simulate the plan
        4. return a shared GenerationResult

        Concrete generators should customize the lifecycle through
        validate_request(), plan(), and execute() rather than overriding
        this method.
        """
        self.validate_request(request)
        plan = self.plan(request)
        return self.execute(request, plan)

    def validate_request(self, request: GenerateRequest) -> None:
        """Validate a generation request before planning."""
        del request

    @abstractmethod
    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Build an immutable generation plan without filesystem mutation."""

    @abstractmethod
    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Execute or simulate a previously validated generation plan."""
