# ADR 0021: AI Integration Contract

> **Status:** Accepted
> **Milestone:** 6 — AI Integration
> **Date:** 2026-08-15
> **Decision Owners:** OpenProjectLab Maintainers
> **Related Architecture:** `docs/architecture/ai-integration.md`

## Context

OpenProjectLab（OPL）在 Milestone 5 完成 Open Courseware Platform 的核心能力，包括 Courseware Domain、Generator Contracts、Composition、Generation Plan，以及代表性 End-to-End 驗證。

Milestone 6 將加入 AI Integration，使 OPL 能支援：

- AI-assisted Content Generation
- AI Review
- AI Documentation
- AI Template Completion
- AI Course Builder
- AI Refactoring Assistant

AI Integration 會引入新的外部依賴與不確定性：

- Provider-specific SDK
- Network dependency
- Authentication credential
- Provider availability
- Rate limit
- Timeout
- Non-deterministic output
- Malformed structured output
- Provider-specific metadata
- Usage cost
- Sensitive context transmission

如果 AI capability 直接整合到 Generator、Courseware Domain 或 Filesystem，OPL 將可能失去目前已建立的重要架構特性：

- Provider independence
- Deterministic testing
- Domain isolation
- Controlled filesystem side effects
- Replaceable infrastructure
- Stable Generator contracts
- CI without external credentials

因此 Milestone 6 必須先建立一個正式 AI Integration Contract。

本 ADR 定義 AI Provider、Application Layer、Courseware Domain、Generator、Filesystem、Credential、Failure Handling 與 Testing 之間的責任邊界。

---

## Decision

OPL 採用以下 AI Integration Contract：

> **AI Provider 是可替換的 Infrastructure dependency。所有 AI output 都必須視為不可信外部輸入，經過結構驗證與 Courseware Domain validation 後，才能進入既有 Composition → GenerationPlan → Filesystem pipeline。**

核心原則：

```text
AI proposes.
Domain validates.
Generator plans.
Filesystem commits.
Tests verify.
```

OPL 不建立 AI 專用的第二套 generation pipeline。

---

## 1. Architectural Boundary

AI Integration 的正式 pipeline 為：

```text
User / Application Intent
        ↓
AI Application Service
        ↓
AIRequest
        ↓
AIProvider Protocol
        ↓
Provider Adapter
        ↓
External AI Provider
        ↓
Provider Adapter
        ↓
AIResponse
        ↓
Structural Validation
        ↓
AI-to-Domain Mapping
        ↓
Courseware Domain Validation
        ↓
Courseware Domain Objects
        ↓
Courseware Composition
        ↓
GenerationPlan
        ↓
Filesystem
```

這個依賴方向是本 ADR 的核心決策。

---

## 2. AIProvider Is a Protocol Boundary

OPL 必須定義 Provider-independent AI Provider contract。

概念：

```python
from typing import Protocol


class AIProvider(Protocol):
    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        ...
```

Application code 依賴：

```text
AIProvider
```

而不是直接依賴：

```text
Vendor SDK
Vendor Client
Vendor Request
Vendor Response
Vendor Exception
```

---

## 3. Provider-Specific APIs Must Remain in Adapters

Provider-specific implementation 必須限制在 Provider Adapter boundary。

例如：

```text
OPL AIRequest
    ↓
Provider Adapter
    ↓
Provider-specific Request
```

以及：

```text
Provider-specific Response
    ↓
Provider Adapter
    ↓
OPL AIResponse
```

Provider-specific types 不得進入：

- Courseware Domain
- Generator contracts
- GenerationPlan
- Filesystem contracts
- Public Courseware models

---

## 4. Courseware Domain Must Not Depend on AI

Courseware Domain 必須保持 AI-independent。

禁止：

```text
Courseware Domain
        ↓
AIProvider
```

禁止：

```text
Course
Week
Lab
Quiz
Assignment
        ↓
Provider SDK
```

Domain Model 不應保存 Provider Client、Provider Request、Provider Response 或 Credential。

這確保：

- 非 AI workflow 繼續存在。
- Domain tests 不需要 AI。
- Courseware contracts 不隨 Provider SDK 演進。
- AI capability 可以移除或替換而不破壞 Domain。

---

## 5. Generator Must Not Invoke AI Providers Directly

Generator 不得直接執行：

```python
provider.generate(...)
```

AI workflow 應在 Generator 之前完成。

正式方向：

```text
AI Workflow
    ↓
Validated Courseware Domain Input
    ↓
Generator / Composition
```

Generator 繼續負責 deterministic generation lifecycle。

這保護既有 Generator contract：

```text
Validate
  ↓
Plan
  ↓
Generate
```

而不將以下責任加入 Generator：

- Authentication
- Network
- Retry
- Provider selection
- AI response parsing
- AI schema repair

---

## 6. AI Must Not Write Directly to Filesystem

AI Provider、raw AI response handler 與 AI Review service 不得直接修改 production filesystem。

禁止：

```python
response = provider.generate(request)

Path("README.md").write_text(
    response.content,
    encoding="utf-8",
)
```

正式 pipeline 必須保持：

```text
AIResponse
    ↓
Validation
    ↓
Domain
    ↓
Composition
    ↓
GenerationPlan
    ↓
Filesystem
```

這確保既有：

- output policy
- path safety
- conflict handling
- dry-run behavior
- deterministic planning
- filesystem testing

不會因加入 AI 而被繞過。

---

## 7. AIRequest Is an OPL Contract

AI request 必須使用 Provider-independent OPL model。

初步概念：

```python
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class AIRequest:
    task: str
    instructions: str
    context: Mapping[str, object]
    response_contract: str | None = None
```

正式欄位由後續 Contract Tests 決定。

`AIRequest` 不得直接包含：

- API key
- Authentication header
- Provider SDK object
- HTTP client
- Provider session
- Filesystem handle

---

## 8. AIResponse Is an OPL Contract

Provider Adapter 必須將 Provider-specific response 正規化為 OPL `AIResponse`。

概念：

```python
@dataclass(frozen=True, slots=True)
class AIResponse:
    content: object
    metadata: Mapping[str, object]
```

`AIResponse` 可以包含 Provider-independent operational metadata，例如：

- provider identifier
- model identifier
- finish state
- usage metadata
- correlation identifier

這些 metadata 不屬於 Courseware Domain。

---

## 9. AI Output Is Always Untrusted Input

所有 AI output 必須視為外部不可信資料。

以下情況都不能直接接受：

- JSON 可以 parse
- Provider 宣告 structured output
- Provider 回傳成功 HTTP status
- Model 宣稱符合 schema
- Prompt 明確要求特定格式

AI output 必須經過：

```text
Transport Validation
        ↓
Structural Validation
        ↓
Semantic / Domain Validation
```

只有成功建立合法 Domain Object 後，資料才被視為 OPL-valid courseware。

---

## 10. Structured Output First

Milestone 6 的 AI integration 優先使用 structured output。

例如 Course Builder 應優先取得類似：

```json
{
  "title": "Modern Java",
  "description": "...",
  "weeks": []
}
```

而不是依賴自然語言段落的 heuristic parsing。

Structured output 是以下能力的基礎：

- Contract testing
- Schema validation
- Domain mapping
- Provider replacement
- Error diagnostics
- Evolution/versioning

---

## 11. Validation Has Three Responsibilities

### Transport Validation

Provider Adapter 負責確認：

- Provider invocation 成功。
- Provider response 存在。
- Response 可以轉換成 OPL representation。

### Structural Validation

AI Integration Layer 負責確認：

- required fields
- data types
- collection structure
- expected response shape

### Domain Validation

Courseware Domain 負責：

- Course invariant
- Week invariant
- Lab invariant
- Quiz invariant
- Assignment invariant
- Relationship invariant

AI Layer 不得複製 Courseware Domain validation。

---

## 12. Mapping Boundary

AI response 不直接等同於 Courseware Domain Object。

採用：

```text
AIResponse
    ↓
Validated AI DTO
    ↓
Mapper
    ↓
Courseware Domain
```

AI-specific operational metadata 不得進入：

```text
Course
Week
Lab
Quiz
Assignment
```

除非未來經過獨立 ADR 正式建立 provenance contract。

---

## 13. Prompt Is Not a Contract

Prompt 屬於 AI interaction mechanism。

Prompt 不取代：

- structural validation
- domain validation
- generator validation
- filesystem policy

例如 Prompt：

```text
Generate exactly 16 weeks.
```

仍必須有正式程式驗證：

```text
number of weeks == expected contract
```

Model 是否遵守 Prompt 不能成為 correctness guarantee。

---

## 14. Prompt Ownership

Prompt construction 屬於 AI Application Layer。

Prompt 不應散落在：

- CLI
- Generator
- Filesystem
- Courseware Domain
- Provider Adapter

建議 responsibility：

```text
Task Definition
     +
Domain Context
     +
Response Contract
     ↓
Prompt / Request Builder
     ↓
AIRequest
```

Provider Adapter 負責 transport adaptation，而不是定義 OPL 教學需求。

---

## 15. Prompt Versioning

當 Prompt 成為 production behavior 的重要部分後，應允許版本化。

例如：

```text
course-builder-v1
quiz-review-v1
assignment-draft-v2
```

Prompt versioning 未要求立即實作，但 architecture 不應阻礙：

- regression evaluation
- rollback
- provider comparison
- reproducibility analysis

---

## 16. Provider Selection Belongs to Composition Root

Provider 選擇應由 Application Composition Root 或 configuration 完成。

概念：

```python
provider = build_ai_provider(
    ai_config
)

service = AIService(
    provider=provider,
)
```

不得由 Generator 或 Domain 自行選 Provider。

---

## 17. Credential Isolation

Provider credential 屬於 runtime infrastructure configuration。

Credential 不得：

- hard-code
- commit
- 保存於 Domain
- 保存於 `AIRequest.context`
- 保存於 Template Context
- 保存於 GenerationPlan
- 寫入 generated courseware
- 出現在一般 error message
- 出現在一般 log

建議 lifecycle：

```text
Runtime Environment / Secret Store
        ↓
Provider Configuration
        ↓
Provider Adapter
```

Credential 在這個 boundary 結束。

---

## 18. Minimal Context Principle

AI invocation 只應傳送完成 task 必要的資料。

例如產生 Quiz 可能需要：

```text
Course objective
Week objective
Topic
Difficulty
Quiz contract
```

不應預設傳送：

```text
Entire repository
Git history
CI files
Environment variables
Credentials
Private configuration
Unrelated user files
```

這是 security、cost 與 prompt-quality 的共同要求。

---

## 19. AI Exception Hierarchy

Milestone 6 應建立 Provider-independent error hierarchy。

建議：

```text
OpenProjectLabError
└── AIError
    ├── AIConfigurationError
    ├── AIProviderError
    ├── AIAuthenticationError
    ├── AIRateLimitError
    ├── AITimeoutError
    ├── AIUnavailableError
    ├── AIResponseError
    └── AIResponseValidationError
```

正式類別由 Contract Test 與 implementation PR 決定。

---

## 20. Provider Exceptions Must Be Converted

Provider-specific exception 不得穿透 Provider Adapter。

例如：

```python
try:
    ...
except VendorTimeoutError as exc:
    raise AITimeoutError(
        "AI provider request timed out."
    ) from exc
```

Exception chaining 必須保留。

這讓：

- CLI
- SDK
- tests
- higher application layers

不需要了解 Provider-specific exception hierarchy。

---

## 21. Do Not Hide Programming Errors

不得使用：

```python
except Exception as exc:
    raise AIProviderError(...) from exc
```

包裝所有錯誤。

這會錯誤地將：

- `TypeError`
- `AttributeError`
- `AssertionError`
- implementation defects

偽裝成 provider failure。

Adapter 只應轉換它能明確辨識的 Provider / transport failure。

---

## 22. Retry Is an Application/Infrastructure Concern

Retry 不屬於 Courseware Domain 或 Generator。

可能可以 Retry：

- transient network failure
- provider unavailable
- timeout
- rate limit

通常不可 Retry：

- invalid credential
- invalid request
- structural schema violation
- domain validation failure
- unsupported operation

正式 retry policy 若加入，必須定義：

- eligible failures
- maximum attempts
- backoff
- cancellation
- cost effect
- logging
- idempotency

Milestone 6 第一個 implementation 不要求自動 retry。

---

## 23. Timeout Is Required for Real Providers

Real Provider Adapter 不應允許無限等待。

Provider-specific timeout 必須轉換成 OPL：

```text
AITimeoutError
```

Timeout value 屬於 application/infrastructure configuration。

---

## 24. Streaming Is Not Part of Initial Core Contract

初始 Provider contract 採用：

```text
AIRequest → AIResponse
```

Streaming 不納入第一版核心契約。

如果未來需要 streaming，應另行設計：

```text
AIStreamEvent
```

避免 streaming semantics 過早污染 Application 與 Domain。

---

## 25. Tool Calling Is Out of Scope for Initial Contract

初始 AI Integration 不允許模型直接執行 OPL tools。

尤其不得提供：

```text
write_file
delete_file
shell_execute
git_commit
git_push
plugin_install
```

作為可自動執行的 AI capability。

若未來加入 Tool Calling，必須建立獨立 ADR，至少定義：

- Tool Registry
- Permission model
- Input validation
- Execution isolation
- Audit trail
- Side-effect policy
- Tests

---

## 26. FakeAIProvider Is a First-Class Contract Implementation

OPL 必須建立 deterministic `FakeAIProvider`。

Fake Provider 用於：

- Unit Tests
- Contract Tests
- Integration Tests
- Representative E2E
- CI

概念：

```python
class FakeAIProvider:
    def __init__(
        self,
        responses: tuple[AIResponse, ...],
    ) -> None:
        self._responses = list(responses)
        self.requests: list[AIRequest] = []

    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        self.requests.append(request)
        return self._responses.pop(0)
```

實際 interface 由 Contract Tests 決定。

---

## 27. Core Tests Must Not Use Real AI Providers

以下 automation：

```text
pre-commit
pytest
CI
Contract Tests
Integration Tests
Representative E2E
```

不得要求：

- Internet access
- AI API key
- Paid model account
- External provider availability
- Stable natural-language generation

這是本 ADR 的強制規則。

---

## 28. Live Provider Tests Must Be Separate

未來的真實 Provider integration test 必須與一般 CI 分離。

Live tests 應：

- opt-in
- clearly marked
- credential-aware
- timeout-limited
- cost-aware
- not run during normal pre-commit
- not compare exact free-form text

例如可考慮：

```text
pytest marker: ai_live
```

實際 marker 另行決定。

---

## 29. Determinism Boundary

Production AI output 可以是非決定性的。

OPL test suite 必須保持 deterministic。

因此：

```text
Fake Provider response
        ↓
Validation
        ↓
Domain
        ↓
GenerationPlan
```

必須完全可重複。

不應使用真實模型自然語言作為 regression oracle。

---

## 30. AI Review Is Advisory

AI Review 可以產生：

```text
AIReviewResult
├── findings
├── categories
├── severity
└── recommendations
```

但 AI Review 初期不得：

- 修改原 Domain
- 修改 Filesystem
- 自動 apply recommendation
- 取代 Domain validation
- 取代人工審查

Review capability 是 advisory。

---

## 31. AI Course Builder Produces Domain-Compatible Data

AI Course Builder 的目標不是直接產生 repository files。

正式方向：

```text
Course Specification
        ↓
AI Course Builder
        ↓
Structured Course Draft
        ↓
Validation
        ↓
Courseware Domain
```

接著才進入既有：

```text
Composition
    ↓
GenerationPlan
    ↓
Filesystem
```

---

## 32. AI Refactoring Produces Proposals First

初期 AI Refactoring Assistant 應產生：

```text
Refactoring Proposal
```

而不是直接修改正式 courseware。

未來若支援 apply operation，也必須重新進入：

```text
Validation
    ↓
Domain
    ↓
GenerationPlan
```

---

## 33. Invalid AI Output Must Fail Before Side Effects

如果 AI response 無法通過 structural validation：

```text
AIResponseValidationError
```

此時不得：

- 建立 partial production Domain state
- 建立 production GenerationPlan
- 修改 production Filesystem

採用：

```text
Validate before side effect
```

原則。

---

## 34. Domain Validation Failures Remain Domain Failures

如果 AI output 結構正確，但轉換成 Domain 時違反 Courseware invariant：

```text
AI Response
    ↓
Structural Validation succeeds
    ↓
Domain Construction
    ↓
Domain Validation fails
```

此 failure 不應全部包裝為 generic `AIError`。

Domain exception 應保留其語意。

AI 是資料來源，不是 Domain authority。

---

## 35. Partial Responses Are Rejected by Default

如果 use case 要求完整結果，partial response 必須失敗。

例如要求 16 weeks，但 AI 只回傳 12 weeks：

```text
structurally parseable
```

不代表：

```text
contract valid
```

預設 policy：

```text
Incomplete required output → explicit failure
```

只有 use case 明確宣告允許 partial result 時才可接受。

---

## 36. Automatic Response Repair Is Deferred

初始 contract 採用：

```text
Generate
    ↓
Validate
    ↓
Accept or Fail
```

不採用預設：

```text
Generate
    ↓
Fail
    ↓
Repair
    ↓
Fail
    ↓
Repair indefinitely
```

Automatic response repair 增加：

- cost
- non-determinism
- retry ambiguity
- diagnostics complexity

未來若需要，必須建立清楚的 repair policy。

---

## 37. Logging Must Avoid Sensitive Content

一般 AI logs 可以包含：

- task identifier
- provider identifier
- model identifier
- request correlation ID
- duration
- validation result
- retry count

一般 logs 不應預設包含：

- API key
- authorization header
- full sensitive prompt
- full private context
- raw credential
- unreviewed complete provider response

---

## 38. AI Metadata Does Not Belong to Domain by Default

以下 operational metadata：

```text
provider
model
token usage
latency
finish reason
request ID
```

預設屬於 AI Application Result / Infrastructure。

不加入：

```text
Course
Week
Lab
Quiz
Assignment
```

如果未來需要 provenance，應建立新的正式 contract。

---

## 39. AI Integration May Later Become a Plugin Extension

OPL 已具有 Plugin ecosystem。

未來 Provider Adapter 可以成為 Plugin extension：

```text
Third-party Plugin
        ↓
AIProvider implementation
        ↓
AIProvider Protocol
```

但先決條件是 `AIProvider` contract 穩定。

本 ADR 不要求第一個 Provider implementation 必須透過 Plugin system。

---

## 40. Public SDK Exposure Is Deferred

初期 AI module 不自動成為 Stable Public SDK。

在 export AI contract 前，必須確認：

- stable request contract
- stable response contract
- exception contract
- compatibility policy
- provider extension mechanism
- documentation
- tests

Public API stabilization 應獨立審查。

---

## 41. Initial Implementation Scope

本 ADR 的最小 contract 已完成並持續演進。

### Core contracts

```text
generator/ai/
├── __init__.py
├── models.py
├── protocols.py
├── errors.py
├── validation.py
└── testing.py
```

### Provider-independent application capabilities

後續依同一 contract 落地：

```text
courseware.py
service.py
review.py
review_service.py
documentation.py
documentation_service.py
template_completion.py
template_completion_service.py
course_builder.py
```

這些 production contracts 均保持：

- no network requirement in core tests
- no API key requirement in core CI
- deterministic `FakeAIProvider`
- structural validation before Domain integration
- no direct production filesystem mutation from AI services

第一個 concrete Provider Adapter 已由 ADR 0022 後續落地；ADR 0021 的
provider-independent core contract 本身仍不依賴真實 Provider SDK。

---

## 42. Representative E2E Requirement

Milestone 6 acceptance 前必須至少建立一條 deterministic AI E2E。

建議：

```text
Course Specification
        ↓
AICourseBuilder
        ↓
FakeAIProvider
        ↓
AIResponse
        ↓
Structural Validation
        ↓
Courseware Domain
        ↓
Composition
        ↓
GenerationPlan
        ↓
Filesystem
```

此測試必須：

- 不需要 network
- 不需要 API key
- 不產生成本
- deterministic
- 驗證 AI boundary
- 驗證 Domain boundary
- 驗證既有 generation pipeline

---

## 43. Consequences

### Positive

此決策提供：

- Provider independence
- Stable Domain boundary
- Stable Generator lifecycle
- Deterministic CI
- Replaceable AI infrastructure
- Credential isolation
- Testable failure handling
- Controlled filesystem side effects
- Future Plugin integration
- Future multi-provider support

AI 能力可以逐步增加，而不需要重寫 OPL Core。

### Negative

此設計比直接：

```python
client.generate(prompt)
```

增加更多結構：

- request model
- response model
- provider protocol
- adapter
- validation
- mapping
- fake provider
- error conversion

初期開發速度會稍慢。

但是這些邊界是為了避免 AI-specific complexity 擴散到整個 OPL。

### Trade-off

我們選擇：

```text
Explicit contracts
```

而不是：

```text
Minimal initial code
```

因為 OPL 的目標是長期可維護的 Project Engineering Platform，而不是單次 AI prototype。

---

## 44. Rejected Alternative: Direct Provider SDK in Generator

### Alternative

```text
Generator
    ↓
Vendor SDK
```

### Rejected Because

這會造成：

- Generator/provider coupling
- Network-dependent Generator tests
- API credential requirements
- Provider types leaking into core
- Difficult provider replacement
- Non-AI workflows becoming AI-aware

---

## 45. Rejected Alternative: AI Writes Files Directly

### Alternative

```text
AIResponse
    ↓
Filesystem
```

### Rejected Because

這會繞過：

- Domain contract
- Composition
- GenerationPlan
- path policy
- filesystem safety
- deterministic testing

並增加未驗證 AI output 直接造成 repository mutation 的風險。

---

## 46. Rejected Alternative: Provider Types as Domain Models

### Alternative

直接將 Provider response object 傳入 Courseware Domain。

### Rejected Because

這會：

- 綁定 Provider SDK
- 污染 Domain
- 破壞 serialization/testing
- 增加 SDK upgrade impact
- 阻礙 multi-provider architecture

---

## 47. Rejected Alternative: Real Provider in Core CI

### Alternative

Contract Tests 與 E2E 直接呼叫真實 AI Provider。

### Rejected Because

會造成：

- flaky CI
- external outage dependency
- cost
- credential management
- rate-limit failure
- non-deterministic regression results

因此 Fake Provider 是核心測試策略。

---

## 48. Rejected Alternative: Prompt-Only Validation

### Alternative

假設 Prompt 足以保證：

```text
correct structure
correct week count
valid quizzes
valid assignments
```

### Rejected Because

Prompt 是 probabilistic instruction，不是 executable contract。

OPL correctness 必須由程式契約與 Domain validation 保證。

---

## 49. Compatibility

Milestone 6 AI Integration 必須是 additive。

沒有使用 AI 的現有 workflow 應繼續：

```text
Courseware Input
    ↓
Generator / Composition
    ↓
GenerationPlan
    ↓
Filesystem
```

不得因加入 AI 而要求：

- Provider config
- API key
- AI SDK
- Internet

才能執行既有 OPL 功能。

---

## 50. Testing Requirements

任何符合本 ADR 的 AI feature 至少應測試：

### Contract

- `AIRequest`
- `AIResponse`
- `AIProvider`
- Fake Provider compatibility

### Validation

- valid response
- malformed response
- missing field
- wrong field type
- incomplete response
- domain-invalid response

### Failure

- provider error
- timeout
- authentication error
- rate limit
- unavailable provider
- unexpected programming error

### Security

- credential not exposed in exception
- credential not exposed in repr
- credential not inserted into Domain
- credential not required by Fake Provider

### Architecture

- Generator has no provider dependency
- Domain has no provider dependency
- AI response cannot bypass validation
- invalid response has no filesystem side effect

---

## 51. Documentation Requirements

Implementing this ADR requires synchronizing:

```text
docs/architecture/ai-integration.md
docs/architecture/open-courseware-platform.md
docs/adr/README.md
docs/roadmap.md
```

As implementation grows, also update as applicable:

```text
docs/reference/*
docs/HISTORY.md
CHANGELOG.md
SDK documentation
CLI documentation
configuration documentation
```

---

## 52. Code Review Checklist

### Architecture

- [ ] AI capability follows the defined application boundary.
- [ ] Courseware Domain does not depend on AI Provider.
- [ ] Generator does not directly invoke Provider SDK.
- [ ] Provider-specific types remain inside adapters.
- [ ] AI does not directly write production files.
- [ ] Existing OPL generation pipeline remains canonical.

### Contracts

- [ ] `AIRequest` is Provider-independent.
- [ ] `AIResponse` is Provider-independent.
- [ ] `AIProvider` protocol has minimal responsibility.
- [ ] AI operational metadata is separate from Domain data.
- [ ] Public API exposure has been reviewed separately.

### Validation

- [ ] AI output is treated as untrusted.
- [ ] Structural validation exists.
- [ ] Domain validation remains owned by Domain.
- [ ] Prompt is not used as a substitute for validation.
- [ ] Incomplete required output fails explicitly.
- [ ] Failure occurs before filesystem side effects.

### Provider

- [ ] Provider Adapter isolates SDK-specific types.
- [ ] Provider errors are translated explicitly.
- [ ] Exception chaining is preserved.
- [ ] Programming bugs are not masked as Provider errors.
- [ ] Timeout behavior is explicit.
- [ ] Retry behavior is explicit.

### Security

- [ ] Credentials are not committed.
- [ ] Credentials are not stored in Domain.
- [ ] Credentials are not included in `AIRequest.context`.
- [ ] Credentials are not written to generated output.
- [ ] Credentials are not exposed in logs or errors.
- [ ] Provider receives only required context.

### Testing

- [ ] Unit tests require no network.
- [ ] Contract tests require no network.
- [ ] CI requires no AI API key.
- [ ] Fake Provider is deterministic.
- [ ] Invalid output cases are tested.
- [ ] Provider failures are tested.
- [ ] Domain validation failure is tested.
- [ ] No-side-effect failure is tested.
- [ ] Live Provider tests are separated from core CI.

### Documentation and Automation

- [ ] AI architecture document is synchronized.
- [ ] ADR index is updated.
- [ ] Open Courseware architecture is synchronized.
- [ ] Roadmap is synchronized.
- [ ] Changelog is updated when implementation lands.
- [ ] `git diff --check` passes.
- [ ] `pre-commit run --all-files` passes.
- [ ] `python -m pytest` passes.
- [ ] Coverage remains above repository policy.

---

## 53. Acceptance Criteria

ADR 0021 的 acceptance criteria 已滿足，因此狀態為 `Accepted`：

- AI Integration Architecture 已建立並完成 review。
- Provider boundary 已由 runtime-checkable `AIProvider` contract 落地。
- Domain / Generator / Filesystem boundaries 已由 implementation 與 tests 保護。
- Credential isolation policy 已固定，core tests / CI 不要求 API key。
- deterministic testing strategy 已由 `FakeAIProvider` 落地。
- `AIRequest` / `AIResponse` contracts 已實作並測試。
- structured validation 與 AI-to-Courseware mapping 已實作。
- related architecture、ADR index 與 roadmap 進行一致性同步。
- repository quality gates 持續作為每個 AI PR 的 merge 條件。

ADR Acceptance 不代表 Milestone 6 formal acceptance；Real Provider Adapter
已由後續 ADR 0022 與 Step 6.10 落地。

---

## 54. Follow-Up Work

ADR 0021 的 architecture decision 維持不變；implementation status 已演進至
Milestone 6 representative E2E。

```text
ADR 0021 Accepted
        ↓
AI Core Contracts ✅
        ↓
FakeAIProvider ✅
        ↓
Structured Response Validation ✅
        ↓
AI-to-Courseware Mapping ✅
        ↓
AI Course Generation Service ✅
        ↓
AI Review ✅
        ↓
AI Documentation ✅
        ↓
AI Template Completion ✅
        ↓
AI Course Builder ✅
        ↓
Real Provider Adapter / ADR 0022 ✅
        ↓
Representative deterministic AI E2E ✅
        ↓
Milestone 6 Formal Acceptance 🚧
```

已完成的 follow-up infrastructure：

1. Real Provider Adapter contract / ADR 0022。
2. Provider-independent provider error conversion 與 timeout behavior。
3. credential isolation 與 injected-client adapter boundary。
4. live provider tests 與 core CI separation。
5. representative deterministic AI → Domain → Composition → Filesystem E2E。

目前剩餘工作是 Milestone 6 formal acceptance record、final regression /
coverage / CI evidence 與 post-merge consistency verification。

Paid/live provider invocation 維持 optional operational verification，不是
ADR 0021 或 Milestone 6 core acceptance 的必要條件。

---

## Decision Summary

OpenProjectLab adopts a Provider-independent, validation-first AI architecture.

The permanent boundaries are:

```text
AI Provider
    ≠
Courseware Domain

AI Provider
    ≠
Generator

AI Provider
    ≠
Filesystem

AI Response
    ≠
Domain Object

Prompt
    ≠
Validation Contract
```

The canonical pipeline is:

```text
AI proposes
    ↓
OPL validates
    ↓
Domain accepts
    ↓
Generator plans
    ↓
Filesystem commits
    ↓
Tests verify
```

This preserves the engineering guarantees established before Milestone 6 while allowing AI capabilities to evolve independently.
