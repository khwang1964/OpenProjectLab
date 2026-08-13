"""Quiz generator implementation for OpenProjectLab."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from generator.core.exceptions import GeneratorValidationError
from generator.core.filesystem import FileSystem
from generator.core.generation_manifest import GenerationManifest
from generator.core.models import (
    GenerateRequest,
    GenerationOperation,
    GenerationPlan,
    GenerationResult,
    WriteResult,
)
from generator.core.template import TemplateRenderer
from generator.generators.base import BaseGenerator


class QuizGenerator(BaseGenerator):
    """Generate a Week-scoped OpenProjectLab quiz scaffold."""

    name = "quiz"
    description = "Generate an OpenProjectLab quiz scaffold"

    def __init__(
        self,
        template_root: Path | None = None,
        output_root: Path | None = None,
        *,
        filesystem: FileSystem | None = None,
    ) -> None:
        """Initialize the generator and its filesystem dependencies."""
        super().__init__()
        self._template_root = Path(template_root) if template_root else None
        self._output_root = Path(output_root) if output_root else None
        self._filesystem = filesystem or FileSystem()

    def validate_request(self, request: GenerateRequest) -> None:
        """Validate a Quiz request before planning."""
        self._validate_generator_name(request.generator_name)
        self._resolve_template_root()
        self._validate_week(request.values.get("week"))
        self._validate_quiz_id(request.values.get("quiz_id"))
        self._validate_title(request.values.get("title"))
        self._validate_questions(request.values.get("questions"))

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Build an immutable plan for Quiz template output."""
        ctx = dict(request.values)
        template_name = str(ctx.get("template_name", "quiz/README.md.j2"))
        output_name = Path(ctx.get("output_name", "README.md"))

        week = self._validate_week(ctx.get("week"))
        quiz_id = self._validate_quiz_id(ctx.get("quiz_id"))
        title = self._validate_title(ctx.get("title"))
        questions = self._validate_questions(ctx.get("questions"))

        ctx["week"] = week
        ctx["week_padded"] = f"{week:02d}"
        ctx["quiz_id"] = quiz_id
        ctx["title"] = title
        ctx["questions"] = questions

        output = request.target / f"week-{week:02d}" / "quiz" / quiz_id / output_name

        operation = GenerationOperation(
            template_name=template_name,
            destination=output,
            context=ctx,
            write_policy=request.options.write_policy,
        )

        return GenerationPlan(
            generator_name=self.name,
            operations=(operation,),
        )

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Execute a previously validated Quiz generation plan."""
        template_root = self._resolve_template_root()
        renderer = TemplateRenderer(template_root)

        writes: list[WriteResult] = []
        manifest = None

        if bool(request.values.get("record_manifest", True)):
            manifest = GenerationManifest.load(
                request.target,
                filesystem=self._filesystem,
            )
            manifest.set_project(name=request.values.get("course_name"))

        for operation in plan.operations:
            content = renderer.render(
                operation.template_name,
                operation.context,
            )

            if manifest is not None:
                manifest.record(
                    operation.destination,
                    generator=self.name,
                    template=operation.template_name,
                    metadata={
                        "week": operation.context.get("week"),
                        "quiz_id": operation.context.get("quiz_id"),
                        "title": operation.context.get("title"),
                    },
                )

            write_result = self._filesystem.write_text(
                operation.destination,
                content,
                overwrite=request.options.overwrite,
                dry_run=request.options.dry_run,
            )
            writes.append(write_result)

        if manifest is not None:
            manifest.save(dry_run=request.options.dry_run)

        return GenerationResult(
            generator_name=self.name,
            writes=tuple(writes),
            dry_run=request.options.dry_run,
            manifest_updated=(manifest is not None and not request.options.dry_run),
        )

    def generate(self, request: GenerateRequest) -> GenerationResult:
        """Generate through the canonical framework lifecycle."""
        return self.run(request)

    def _resolve_template_root(self) -> Path:
        """Resolve the template root."""
        if self._template_root is None:
            raise GeneratorValidationError(
                generator=self.name,
                field="template_root",
                message="未提供 template_root",
            )
        return self._template_root

    def _validate_generator_name(self, generator_name: str) -> None:
        """Reject requests addressed to a different generator."""
        if generator_name != self.name:
            raise GeneratorValidationError(
                generator=self.name,
                field="generator_name",
                message=(f"generator_name 必須是 {self.name!r}，收到 {generator_name!r}"),
            )

    @classmethod
    def _validate_week(cls, value: object) -> int:
        """Validate and return a positive integer week number."""
        if isinstance(value, bool) or not isinstance(value, int):
            raise GeneratorValidationError(
                generator=cls.name,
                field="week",
                message="week 必須是整數",
            )
        if value <= 0:
            raise GeneratorValidationError(
                generator=cls.name,
                field="week",
                message="week 必須大於 0",
            )
        return value

    @classmethod
    def _validate_quiz_id(cls, value: object) -> str:
        """Validate and normalize a Week-scoped Quiz identity."""
        if not isinstance(value, str):
            raise GeneratorValidationError(
                generator=cls.name,
                field="quiz_id",
                message="quiz_id 必須是字串",
            )

        quiz_id = value.strip()
        if not quiz_id:
            raise GeneratorValidationError(
                generator=cls.name,
                field="quiz_id",
                message="quiz_id 不可為空",
            )

        path = Path(quiz_id)
        if path.is_absolute() or ".." in path.parts or "/" in quiz_id or "\\" in quiz_id:
            raise GeneratorValidationError(
                generator=cls.name,
                field="quiz_id",
                message="quiz_id 不可包含路徑語意",
            )

        return quiz_id

    @classmethod
    def _validate_title(cls, value: object) -> str:
        """Validate and normalize a Quiz display title."""
        if not isinstance(value, str):
            raise GeneratorValidationError(
                generator=cls.name,
                field="title",
                message="title 必須是字串",
            )

        title = value.strip()
        if not title:
            raise GeneratorValidationError(
                generator=cls.name,
                field="title",
                message="title 不可為空",
            )

        return title

    @classmethod
    def _validate_questions(
        cls,
        value: object,
    ) -> tuple[dict[str, object], ...]:
        """Validate and normalize the ordered single-answer question collection."""
        if isinstance(value, (str, bytes, bytearray, Mapping)) or not isinstance(value, Sequence):
            raise GeneratorValidationError(
                generator=cls.name,
                field="questions",
                message="questions 必須是非空的有序集合",
            )

        if not value:
            raise GeneratorValidationError(
                generator=cls.name,
                field="questions",
                message="questions 不可為空",
            )

        normalized: list[dict[str, object]] = []
        seen_ids: set[str] = set()

        for item in value:
            question = cls._validate_question(item)
            question_id = question["id"]

            if question_id in seen_ids:
                raise GeneratorValidationError(
                    generator=cls.name,
                    field="question_id",
                    message=f"question id 不可重複：{question_id!r}",
                )

            seen_ids.add(question_id)
            normalized.append(question)

        return tuple(normalized)

    @classmethod
    def _validate_question(cls, value: object) -> dict[str, object]:
        """Validate one single-answer multiple-choice question."""
        if not isinstance(value, Mapping):
            raise GeneratorValidationError(
                generator=cls.name,
                field="questions",
                message="每個 question 必須是 mapping",
            )

        question_id = cls._validate_question_text(
            value.get("id"),
            field="question_id",
        )
        prompt = cls._validate_question_text(
            value.get("prompt"),
            field="prompt",
        )
        choices = cls._validate_choices(value.get("choices"))
        correct_answer = value.get("correct_answer")

        if correct_answer not in choices:
            raise GeneratorValidationError(
                generator=cls.name,
                field="correct_answer",
                message="correct_answer 必須對應 choices 中的一個選項",
            )

        question: dict[str, object] = {
            "id": question_id,
            "prompt": prompt,
            "choices": choices,
            "correct_answer": correct_answer,
        }

        if "explanation" in value:
            explanation = value.get("explanation")
            if not isinstance(explanation, str):
                raise GeneratorValidationError(
                    generator=cls.name,
                    field="explanation",
                    message="explanation 必須是字串",
                )
            question["explanation"] = explanation

        return question

    @classmethod
    def _validate_question_text(
        cls,
        value: object,
        *,
        field: str,
    ) -> str:
        """Validate and normalize a required question string field."""
        if not isinstance(value, str):
            raise GeneratorValidationError(
                generator=cls.name,
                field=field,
                message=f"{field} 必須是字串",
            )

        normalized = value.strip()
        if not normalized:
            raise GeneratorValidationError(
                generator=cls.name,
                field=field,
                message=f"{field} 不可為空",
            )

        return normalized

    @classmethod
    def _validate_choices(cls, value: object) -> tuple[object, ...]:
        """Validate an ordered choices collection with at least two entries."""
        if isinstance(value, (str, bytes, bytearray, Mapping)) or not isinstance(value, Sequence):
            raise GeneratorValidationError(
                generator=cls.name,
                field="choices",
                message="choices 必須是有序集合",
            )

        choices = tuple(value)
        if len(choices) < 2:
            raise GeneratorValidationError(
                generator=cls.name,
                field="choices",
                message="choices 至少需要兩個選項",
            )

        return choices
