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
        """Run the canonical validation, planning, and execution lifecycle."""
        self.validate_request(request)
        plan = self.plan(request)
        return self.execute(request, plan)

    def validate(self, context: GeneratorContext) -> None:
        """驗證輸出目錄是否可安全寫入。"""
        output_dir = context.output_dir
        if output_dir.exists() and any(output_dir.iterdir()) and not context.force:
            raise FileExistsError(f"輸出目錄非空：{output_dir}")

    def prepare(self, context: GeneratorContext) -> None:
        """執行可選的產生前準備工作。"""
        return None

    @abstractmethod
    def generate(self, context: GeneratorContext) -> None:
        """執行主要內容產生流程。"""

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
