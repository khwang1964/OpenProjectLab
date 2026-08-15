from __future__ import annotations

import pytest

from generator.ai.errors import AIResponseValidationError
from generator.ai.models import AIResponse
from generator.ai.review import map_review_response


def _response(content: object) -> AIResponse:
    return AIResponse(
        content=content,
        metadata={"provider": "fake"},
    )


@pytest.mark.parametrize(
    "content",
    [
        None,
        "not-a-mapping",
        42,
        [],
    ],
)
def test_map_review_response_rejects_non_mapping_content(
    content: object,
) -> None:
    with pytest.raises(AIResponseValidationError):
        map_review_response(_response(content))


def test_map_review_response_rejects_missing_findings() -> None:
    with pytest.raises(
        AIResponseValidationError,
        match="findings",
    ):
        map_review_response(_response({}))


def test_map_review_response_rejects_non_list_findings() -> None:
    with pytest.raises(
        AIResponseValidationError,
        match="findings",
    ):
        map_review_response(
            _response(
                {
                    "findings": "invalid",
                }
            )
        )


def test_map_review_response_rejects_non_mapping_finding() -> None:
    with pytest.raises(
        AIResponseValidationError,
        match="finding",
    ):
        map_review_response(
            _response(
                {
                    "findings": ["invalid"],
                }
            )
        )


@pytest.mark.parametrize(
    "missing_field",
    [
        "category",
        "severity",
        "message",
        "recommendation",
    ],
)
def test_map_review_response_rejects_missing_finding_field(
    missing_field: str,
) -> None:
    finding = {
        "category": "clarity",
        "severity": "warning",
        "message": "Ambiguous wording.",
        "recommendation": "Clarify the wording.",
    }
    finding.pop(missing_field)

    with pytest.raises(
        AIResponseValidationError,
        match=missing_field,
    ):
        map_review_response(
            _response(
                {
                    "findings": [finding],
                }
            )
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("category", 123),
        ("severity", 123),
        ("message", 123),
        ("recommendation", 123),
    ],
)
def test_map_review_response_rejects_wrong_finding_field_type(
    field: str,
    value: object,
) -> None:
    finding = {
        "category": "clarity",
        "severity": "warning",
        "message": "Ambiguous wording.",
        "recommendation": "Clarify the wording.",
    }
    finding[field] = value

    with pytest.raises(
        AIResponseValidationError,
        match=field,
    ):
        map_review_response(
            _response(
                {
                    "findings": [finding],
                }
            )
        )


@pytest.mark.parametrize(
    "severity",
    [
        "debug",
        "critical",
        "",
    ],
)
def test_map_review_response_rejects_unknown_severity(
    severity: str,
) -> None:
    with pytest.raises(
        AIResponseValidationError,
        match="severity",
    ):
        map_review_response(
            _response(
                {
                    "findings": [
                        {
                            "category": "clarity",
                            "severity": severity,
                            "message": "Ambiguous wording.",
                            "recommendation": "Clarify the wording.",
                        }
                    ],
                }
            )
        )


def test_review_validation_failure_has_no_filesystem_side_effect(
    tmp_path,
) -> None:
    with pytest.raises(AIResponseValidationError):
        map_review_response(_response(None))

    assert list(tmp_path.iterdir()) == []
