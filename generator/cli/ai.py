"""Shared, unregistered infrastructure for the v1.1 AI CLI."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from generator.ai.documentation import AIDocumentDraft
from generator.ai.documentation_service import AIDocumentationService
from generator.ai.models import AIRequest, AIResponse
from generator.ai.protocols import AIProvider
from generator.ai.review import AIReviewResult
from generator.ai.review_service import AIReviewService
from generator.ai.service import AICourseGenerationService
from generator.ai.template_completion import AITemplateCompletionResult
from generator.ai.template_completion_service import AITemplateCompletionService
from generator.courseware.models import Course

from .ai_provider import ClientFactory, resolve_experimental_provider

_TASK_BY_COMMAND = {
    "course": "courseware.generate",
    "review": "courseware.review",
    "document": "documentation.generate",
    "template": "template.complete",
}
_REQUEST_FIELDS = frozenset({"schema_version", "instructions", "context", "response_contract"})


def _load_json_object(path: Path, *, label: str) -> dict[str, object]:
    if not path.is_file():
        raise ValueError(f"{label} path must identify a readable regular file")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"{label} file must be readable UTF-8") from exc
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} file must contain valid JSON") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} JSON root must be an object")
    return value


def _load_ai_request(path: Path, *, command: str) -> AIRequest:
    try:
        task = _TASK_BY_COMMAND[command]
    except KeyError as exc:
        raise ValueError(f"unsupported AI command: {command}") from exc

    value = _load_json_object(path, label="request")
    unknown = frozenset(value) - _REQUEST_FIELDS
    if unknown:
        raise ValueError("request JSON contains unknown root fields")

    schema_version = value.get("schema_version")
    if isinstance(schema_version, bool) or schema_version != 1:
        raise ValueError("request schema_version must be integer 1")

    instructions = value.get("instructions")
    if not isinstance(instructions, str) or not instructions.strip():
        raise ValueError("request instructions must be a non-empty string")

    context = value.get("context")
    if not isinstance(context, dict):
        raise ValueError("request context must be an object")

    response_contract = value.get("response_contract")
    if response_contract is not None and (
        not isinstance(response_contract, str) or not response_contract.strip()
    ):
        raise ValueError("request response_contract must be a non-empty string")

    return AIRequest(
        task=task,
        instructions=instructions,
        context=context.copy(),
        response_contract=response_contract,
    )


def _load_local_response(path: Path) -> AIResponse:
    content = _load_json_object(path, label="response")
    return AIResponse(content=content, metadata={"source": "local-response"})


class _LocalResponseProvider:
    """Return one validated local response without network or credentials."""

    def __init__(self, *, response: AIResponse) -> None:
        self._response = response
        self._requests: list[AIRequest] = []

    @property
    def requests(self) -> tuple[AIRequest, ...]:
        return tuple(self._requests)

    def generate(self, request: AIRequest) -> AIResponse:
        self._requests.append(request)
        return self._response


@dataclass(frozen=True, slots=True)
class ExperimentalProviderOptions:
    """Injected configuration for one explicitly selected live provider."""

    client_factory: ClientFactory | None
    api_key: str | None
    model: str
    timeout_seconds: float


class _JsonObjectProvider:
    """Normalize provider text into the structured mapping required by services."""

    def __init__(self, *, provider: AIProvider) -> None:
        self._provider = provider

    def generate(self, request: AIRequest) -> AIResponse:
        response = self._provider.generate(request)
        content = response.content
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError as exc:
                raise ValueError("provider response must contain valid JSON") from exc
        if not isinstance(content, dict):
            raise ValueError("provider response JSON root must be an object")
        return AIResponse(content=content, metadata=response.metadata)


def _provider_for_args(
    args: argparse.Namespace,
    *,
    experimental_options: ExperimentalProviderOptions | None,
) -> tuple[AIProvider, str]:
    response_path = getattr(args, "response", None)
    provider_name = getattr(args, "provider", None)
    if (response_path is None) == (provider_name is None):
        raise ValueError("exactly one of response or provider must be selected")
    if response_path is not None:
        response = _load_local_response(response_path)
        return _LocalResponseProvider(response=response), "local-response"
    if experimental_options is None:
        raise ValueError("experimental provider options are required")
    provider = resolve_experimental_provider(
        name=provider_name,
        client_factory=experimental_options.client_factory,
        api_key=experimental_options.api_key,
        model=experimental_options.model,
        timeout_seconds=experimental_options.timeout_seconds,
    )
    normalized_name = provider_name.strip().lower()
    return _JsonObjectProvider(provider=provider), f"provider:{normalized_name}"


def _course_result(course: Course) -> dict[str, object]:
    return {
        "course_id": course.course_id,
        "title": course.title,
        "language": course.language,
        "weeks": [{"number": week.number, "title": week.title} for week in course.weeks],
    }


def _handle_ai_course(
    args: argparse.Namespace,
    *,
    experimental_options: ExperimentalProviderOptions | None = None,
) -> int:
    """Run the deterministic local-response course application service."""
    request = _load_ai_request(args.request, command="course")
    provider, source = _provider_for_args(args, experimental_options=experimental_options)
    course = AICourseGenerationService(provider=provider).generate_course(request)
    result = _course_result(course)

    if args.json:
        document = {
            "schema_version": 1,
            "command": "course",
            "source": source,
            "result": result,
        }
        print(
            json.dumps(
                document,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
        )
        return 0

    print(f"課程：{course.title}")
    print(f"課程代號：{course.course_id}")
    print(f"語言：{course.language}")
    print("週次：")
    for week in course.weeks:
        print(f"  {week.number}. {week.title}")
    return 0


def _review_result(result: AIReviewResult) -> dict[str, object]:
    return {
        "findings": [
            {
                "category": finding.category,
                "severity": finding.severity,
                "message": finding.message,
                "recommendation": finding.recommendation,
            }
            for finding in result.findings
        ]
    }


def _handle_ai_review(
    args: argparse.Namespace,
    *,
    experimental_options: ExperimentalProviderOptions | None = None,
) -> int:
    """Run the deterministic local-response review application service."""
    request = _load_ai_request(args.request, command="review")
    provider, source = _provider_for_args(args, experimental_options=experimental_options)
    review = AIReviewService(provider=provider).review(request)
    result = _review_result(review)

    if args.json:
        document = {
            "schema_version": 1,
            "command": "review",
            "source": source,
            "result": result,
        }
        print(
            json.dumps(
                document,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
        )
        return 0

    print(f"檢閱發現：{len(review.findings)}")
    for index, finding in enumerate(review.findings, start=1):
        print(f"  {index}. [{finding.severity}] {finding.category}")
        print(f"     訊息：{finding.message}")
        print(f"     建議：{finding.recommendation}")
    return 0


def _document_result(draft: AIDocumentDraft) -> dict[str, object]:
    return {
        "title": draft.title,
        "format": draft.format,
        "content": draft.content,
    }


def _handle_ai_document(
    args: argparse.Namespace,
    *,
    experimental_options: ExperimentalProviderOptions | None = None,
) -> int:
    """Run the deterministic local-response documentation service."""
    request = _load_ai_request(args.request, command="document")
    provider, source = _provider_for_args(args, experimental_options=experimental_options)
    draft = AIDocumentationService(provider=provider).generate(request)
    result = _document_result(draft)

    if args.json:
        document = {
            "schema_version": 1,
            "command": "document",
            "source": source,
            "result": result,
        }
        print(
            json.dumps(
                document,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
        )
        return 0

    print(f"文件：{draft.title}")
    print(f"格式：{draft.format}")
    print("內容：")
    print(draft.content)
    return 0


def _template_result(result: AITemplateCompletionResult) -> dict[str, object]:
    return {
        "template_name": result.template_name,
        "content": result.content,
        "context_keys": list(result.context_keys),
    }


def _handle_ai_template(
    args: argparse.Namespace,
    *,
    experimental_options: ExperimentalProviderOptions | None = None,
) -> int:
    """Run the deterministic local-response template completion service."""
    request = _load_ai_request(args.request, command="template")
    provider, source = _provider_for_args(args, experimental_options=experimental_options)
    completion = AITemplateCompletionService(provider=provider).complete(request)
    result = _template_result(completion)

    if args.json:
        document = {
            "schema_version": 1,
            "command": "template",
            "source": source,
            "result": result,
        }
        print(
            json.dumps(
                document,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
        )
        return 0

    print(f"模板：{completion.template_name}")
    print("內容：")
    print(completion.content)
    print("Context keys：")
    for key in completion.context_keys:
        print(f"  - {key}")
    return 0
