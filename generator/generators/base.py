from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto

from generator.core.context import GeneratorContext
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

    def validate(self, context: GeneratorContext) -> None:
        """Validate a legacy GeneratorContext execution.

        This hook is retained temporarily for compatibility and is not part
        of the canonical GenerateRequest execution contract.
        """
        output_dir = context.output_dir
        if output_dir.exists() and any(output_dir.iterdir()) and not context.force:
            raise FileExistsError(f"輸出目錄非空：{output_dir}")

    def prepare(self, context: GeneratorContext) -> None:
        """Prepare a legacy GeneratorContext execution.

        This compatibility hook is not used by run(GenerateRequest).
        """
        return None

    @abstractmethod
    def generate(self, context: GeneratorContext) -> None:
        """Execute the legacy GeneratorContext generation hook.

        This abstract method is retained temporarily for compatibility.
        New generator execution should use run(GenerateRequest), plan(),
        and execute().
        """

    def post_generate(self, context: GeneratorContext) -> None:
        """執行可選的產生後處理工作。"""
        return None

    def cleanup(self, context: GeneratorContext) -> None:
        """執行可選的資源清理工作。"""
        return None

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
