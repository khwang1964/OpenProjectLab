from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto

from generator.core.context import GeneratorContext


class GeneratorState(Enum):
    CREATED = auto()
    VALIDATED = auto()
    PREPARED = auto()
    GENERATED = auto()
    COMPLETED = auto()
    FAILED = auto()


class BaseGenerator(ABC):
    name = "base"

    def __init__(self):
        self.state = GeneratorState.CREATED

    def run(self, context: GeneratorContext):
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

    def validate(self, context):
        if context.output_dir.exists() and any(context.output_dir.iterdir()) and not context.force:
            raise FileExistsError(f"輸出目錄非空：{context.output_dir}")

    def prepare(self, context):
        pass

    @abstractmethod
    def generate(self, context): ...
    def post_generate(self, context):
        pass

    def cleanup(self, context):
        pass
