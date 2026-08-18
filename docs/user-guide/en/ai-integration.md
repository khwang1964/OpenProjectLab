# AI Integration

OpenProjectLab provides provider-independent AI contracts for AI-assisted courseware workflows. Provider invocation is deliberately separated from OPL domain validation and Generator execution.

## Core contracts

The AI core exposes:

```text
AIRequest
AIResponse
AIProvider
```

`AIRequest` is immutable and contains `task`, `instructions`, `context`, and optional `response_contract`.

`AIResponse` contains flexible `content` plus provider `metadata`.

`AIProvider` is a runtime-checkable protocol:

```python
def generate(request: AIRequest) -> AIResponse:
    ...
```

This keeps downstream OPL code independent of a vendor SDK.

## Provider boundary

A provider adapter translates:

```text
OPL AIRequest / AIResponse
        ↕
provider-specific API
```

Credentials, HTTP behavior, retries, model names, and vendor exceptions should remain outside the courseware domain model.

## Course generation

`AICourseGenerationService` performs:

```text
AIRequest
→ AIProvider.generate()
→ AIResponse
→ validated course mapping
→ Course
```

The result is the same `Course` domain model used by non-AI courseware.

AI-generated content is untrusted structured input until mapping and validation succeed:

```text
AI output ≠ validated OPL domain object
```

## Other AI-assisted services

The repository contains AI-oriented services for courseware assistance, documentation, review, and template completion. They share the provider-independent boundary but may use different response contracts.

Their existence does not imply that every capability is a stable end-user CLI command.

## CLI and configuration boundaries

The documented v1.0 CLI has no general `ai` command, so this manual does not invent `opl ai ...`.

Likewise, generic OPL YAML configuration should not be assumed to configure every provider. API keys, endpoints, model identifiers, timeouts, and retry policies belong to the chosen adapter/deployment unless an explicit OPL contract says otherwise. Never commit provider secrets to repositories.

## Testing

Normal contract tests should use deterministic test providers rather than live network services. This allows request, mapping, failure, and orchestration tests to run in CI without external credentials.

Live provider tests, when used, should remain a separately controlled integration boundary.

## AI and Generators

Responsibilities remain separate:

```text
AI service   → propose/produce structured content
Generator    → validate request → plan artifacts → execute writes
```

A provider adapter should not bypass Generator validation or become a hidden filesystem writer.

### Checklist

- Use `AIRequest` / `AIResponse` at the provider boundary.
- Implement `AIProvider` rather than coupling domain code to a vendor SDK.
- Validate AI output before creating OPL domain values.
- Keep provider metadata separate from courseware state.
- Do not bypass Generator planning for writes.
- Keep secrets out of repositories/examples.
- Prefer deterministic test providers in normal CI.
- Do not assume `opl ai` exists.

## Next step

Continue with [Marketplace](marketplace.md).
