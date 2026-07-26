from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto

from generator.core.context import GeneratorContext


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

    def run(self, context: GeneratorContext) -> None:
        """依序執行驗證、準備、產生、後處理與清理。"""
        try:
            self.validate(context)
            self.state = GeneratorState.VALIDATED
            self.prepare(context)
            self.state = GeneratorState.PREPARED
            self.generate(context)
            self.state = GeneratorState.GENERATED
            self.post_generate(context)
            self.state = GeneratorState.COMPLETED
        except Exception:
            self.state = GeneratorState.FAILED
            raise
        finally:
            self.cleanup(context)

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
