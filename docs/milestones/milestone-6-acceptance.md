# Milestone 6 Acceptance --- AI Integration
> **Status:** Accepted  **Milestone:** 6 --- AI Integration
> **Date:** 2026-08-15 **Acceptance Scope:** Provider-independent AI
> contracts, structured validation, Courseware integration, AI
> application services, Real Provider Adapter infrastructure,
> deterministic representative E2E, documentation alignment, regression,
> coverage, and CI **Related ADRs:** ADR 0021 --- AI Integration
> Contract; ADR 0022 --- AI Provider Adapter Contract

## 1. Purpose

本文件是 OpenProjectLab（OPL）Milestone 6 --- AI Integration 的 formal
acceptance record。

Milestone 6 的目標不是建立一條 AI 專用 generation pipeline，而是將 AI
能力納入既有 OPL architecture：

``` text
AI proposes.
Domain validates.
Generator plans.
Filesystem commits.
Tests verify.
```

Milestone 6 acceptance 必須證明 AI capability 沒有破壞 Milestone 5
已建立 的 Courseware
Domain、Generator、Composition、GenerationPlan、Filesystem 與
deterministic testing boundaries。

本文件目前為 **Accepted**。Step 6.10、Step 6.11 與 Step 6.12 已完成；
final local regression、coverage、pre-commit 與 acceptance PR GitHub Actions / CI
evidence 均已確認。merge 後仍需執行 post-merge consistency verification，
作為 Milestone 6 repository closure 的最後一致性檢查。

## 2. Accepted Architecture

Milestone 6 採用以下 canonical responsibility chain：

``` text
User / Application Intent
        ↓
AI Application Service
        ↓
AIRequest
        ↓
AIProvider
        ↓
Provider Adapter or FakeAIProvider
        ↓
AIResponse
        ↓
Structural Validation
        ↓
AI-to-Courseware Mapping
        ↓
Courseware Domain Validation
        ↓
Course / Week
        ↓
Courseware Composition
        ↓
Generator
        ↓
GenerationPlan
        ↓
Filesystem
```

永久 invariant：

-   AI output 一律視為 untrusted external input。
-   Provider-specific SDK / request / response / exception 不得污染
    Courseware Domain。
-   Generator 不直接呼叫 AI Provider。
-   AI Provider / AI service 不直接寫 production filesystem。
-   Prompt 不取代 structural 或 Domain validation。
-   AI metadata 預設不進入 Courseware Domain。
-   normal tests / pre-commit / core CI 不依賴 network、API key、paid
    provider account 或 live-provider availability。
-   existing non-AI workflows 保持可獨立運作。

## 3. Design and ADR Acceptance

Milestone 6 architecture 由以下正式決策固定：

### ADR 0021 --- AI Integration Contract

ADR 0021 已 `Accepted`，固定：

-   provider-independent `AIProvider` boundary；
-   `AIRequest` / `AIResponse` contracts；
-   validation-first AI integration；
-   Domain / Generator / Filesystem isolation；
-   deterministic `FakeAIProvider` testing strategy；
-   credential isolation；
-   no second AI generation pipeline。

### ADR 0022 --- AI Provider Adapter Contract

ADR 0022 已 `Accepted`，固定：

-   Real Provider Adapter infrastructure boundary；
-   provider SDK isolation；
-   injected client / transport testability；
-   finite timeout；
-   explicit provider-independent error conversion；
-   exception chaining；
-   no hidden automatic retry in the initial contract；
-   deterministic no-network adapter tests；
-   `ai_live` separation from normal automation。

## 4. Implemented Production Capabilities

Milestone 6 已建立：

-   immutable provider-independent `AIRequest`；
-   immutable provider-independent `AIResponse`；
-   runtime-checkable `AIProvider` protocol；
-   deterministic `FakeAIProvider`；
-   structured AI response validation；
-   `AIResponseValidationError`；
-   AI-to-Courseware `Course` / `Week` mapping；
-   `AICourseGenerationService`；
-   advisory `AIReviewFinding` / `AIReviewResult` and
    `AIReviewService`；
-   immutable `AIDocumentDraft` and `AIDocumentationService`；
-   immutable `AITemplateCompletionResult` and
    `AITemplateCompletionService`；
-   immutable `AICourseBuildRequest` and `AICourseBuilder`；
-   provider-independent AI provider error hierarchy；
-   first concrete `OpenAIProviderAdapter`；
-   deterministic generic provider-adapter coverage；
-   deterministic no-network OpenAI adapter coverage；
-   opt-in `ai_live` smoke-test boundary。

## 5. Provider Adapter Acceptance

Step 6.10 --- Real Provider Adapter 已完成。

Acceptance evidence 包括：

-   concrete adapter implements the existing `AIProvider` boundary；
-   provider SDK types remain adapter-private；
-   provider-specific responses normalize into `AIResponse`；
-   recognized provider failures map into OPL AI errors；
-   timeout maps to `AITimeoutError`；
-   exception chaining is preserved；
-   unexpected programming errors are not indiscriminately hidden；
-   credentials remain outside `AIRequest`, `AIResponse`, Domain,
    Template Context, `GenerationPlan`, generated courseware, and normal
    diagnostics；
-   deterministic adapter tests require no network or API key；
-   live-provider tests are opt-in；
-   missing live credentials skip live verification rather than fail
    core verification。

Paid/live OpenAI invocation is optional operational verification and is
not a Milestone 6 core acceptance requirement.

## 6. Representative Deterministic AI E2E

Step 6.11 已建立 representative acceptance path：

``` text
AICourseBuildRequest
        ↓
AICourseBuilder
        ↓
FakeAIProvider
        ↓
AIResponse
        ↓
Structural Validation / Mapping
        ↓
Course / Week
        ↓
CoursewareComposer
        ↓
Production Generators
        ↓
GenerationPlan
        ↓
Filesystem
```

Representative E2E 驗證：

-   production `AICourseBuilder`；
-   deterministic `FakeAIProvider`；
-   production Courseware Domain；
-   production `CoursewareComposer`；
-   production Course / Week generators；
-   deterministic artifact membership and content；
-   reproducibility across repeated runs；
-   composition-wide dry-run non-persistence；
-   invalid AI response fails before filesystem side effects；
-   no network；
-   no API key；
-   no paid invocation。

Step 6.11 full-regression evidence：

``` text
1119 passed
```

Step 6.12 已重新執行 full regression；最終 local acceptance evidence 為
`1119 passed, 1 deselected`，total coverage 為 `90.23%`，高於 required
coverage `67.0%`。

## 7. Security Acceptance

Milestone 6 保護以下 security boundaries：

-   credentials 不 hard-code 或 commit；
-   credentials 不進入 Courseware Domain；
-   credentials 不進入 Template Context 或 `GenerationPlan`；
-   credentials 不寫入 generated courseware；
-   normal logs / exceptions 不應暴露 credentials；
-   AI request context 遵循 minimal-context principle；
-   AI output 在 validation 前不具有 production filesystem authority；
-   Provider Adapter 不執行 Git、Generator 或 plugin installation side
    effects；
-   Tool Calling 不屬於本 milestone core contract。

## 8. Deterministic Testing Acceptance

Milestone 6 automated verification 的核心原則：

``` text
No network
No API key
No paid account
No live-provider dependency
Deterministic fixtures / fake clients
```

Core verification 應涵蓋：

-   AI model contracts；
-   provider protocol compatibility；
-   structured response validation；
-   AI-to-Courseware mapping；
-   application services；
-   provider-independent errors；
-   generic provider-adapter contract；
-   OpenAI adapter no-network behavior；
-   credential isolation；
-   representative deterministic AI E2E；
-   existing non-AI regression suite。

`ai_live` tests 必須保持 opt-in 並與 core acceptance gates 分離。

## 9. Compatibility and Regression

Milestone 6 是 additive architecture change。

沒有使用 AI 的既有 workflow 不得要求：

-   Provider configuration；
-   API key；
-   live AI account；
-   network；
-   successful external AI invocation。

Milestone 5 canonical boundaries 必須保持：

-   Courseware Domain owns Domain invariants；
-   `BaseGenerator.run(GenerateRequest)` remains canonical；
-   Composition uses existing registry / generator lifecycle；
-   `GenerationPlan` remains the planning boundary；
-   Filesystem policy remains outside AI；
-   dry-run / overwrite / manifest semantics remain owned by existing
    OPL subsystems。

## 10. Documentation Alignment

Step 6.12 已確認以下文件一致：

-   `docs/architecture/ai-integration.md`
-   `docs/architecture/open-courseware-platform.md`
-   `docs/adr/0021-ai-integration-contract.md`
-   `docs/adr/0022-ai-provider-adapter-contract.md`
-   `docs/adr/README.md`
-   `docs/roadmap.md`
-   `docs/HISTORY.md`
-   `CHANGELOG.md`
-   `docs/milestones/milestone-6-acceptance.md`

文件不得再將 Step 6.10、Step 6.11 或 Step 6.12 描述為 pending。

## 11. Final Acceptance Gates

本文件轉為 `Accepted` 前已執行：

``` powershell
git diff --check
ruff check generator tests
ruff format --check generator tests
pre-commit run --all-files
python -m pytest
```

並確認：

-   full pytest 全綠；
-   repository coverage 不低於 67.0% policy；
-   normal test run 排除 `ai_live`；
-   core verification 不要求 `OPENAI_API_KEY`；
-   GitHub Actions / CI 全綠；
-   documentation consistency review 通過。

### Final Evidence

Step 6.12 final local regression：

``` text
Final tests: 1119 passed, 1 deselected
Final total coverage: 90.23%
Required coverage: 67.0%
Coverage gate: PASSED
```

Acceptance PR CI evidence：

``` text
GitHub Actions / CI: PASSED
0 cancelled, 0 failing, 1 successful, 0 skipped, 0 pending
CI/Quality checks (pull_request): PASSED
```

本地 full regression、coverage gate 與 acceptance PR CI 均已完成。

## 12. Deferred Capabilities

以下不是 Milestone 6 core acceptance blocker：

-   final public provider runtime configuration schema；
-   paid/live OpenAI operational invocation；
-   AI Refactoring Assistant；
-   AI CLI；
-   AI evaluation framework；
-   AI provenance；
-   AI usage accounting / billing；
-   AI response caching；
-   AI streaming；
-   AI tool calling；
-   Provider Adapter plugin extension point。

這些能力若進入正式 scope，應依 Design First / ADR / contract-test
workflow 個別設計。

## 13. Acceptance Criteria

Milestone 6 可正式接受，當且僅當：

-   [x] AI Integration architecture 已建立。
-   [x] ADR 0021 已 Accepted。
-   [x] Provider-independent AI contracts 已實作。
-   [x] deterministic `FakeAIProvider` 已實作。
-   [x] structured response validation 已實作。
-   [x] AI-to-Courseware mapping 已實作。
-   [x] AI Course Generation Service 已實作。
-   [x] AI Review 已實作。
-   [x] AI Documentation 已實作。
-   [x] AI Template Completion 已實作。
-   [x] AI Course Builder 已實作。
-   [x] ADR 0022 已 Accepted。
-   [x] first concrete Real Provider Adapter 已實作。
-   [x] provider-independent error conversion 已實作。
-   [x] deterministic no-network provider tests 已建立。
-   [x] `ai_live` separation 已建立。
-   [x] representative deterministic AI E2E 已建立。
-   [x] invalid AI output fails before production filesystem side
    effects。
-   [x] existing Courseware / Generator / Composition boundaries 保持。
-   [x] Step 6.11 full regression 已達 1119 passed。
-   [x] Step 6.12 Completed。
-   [x] final full-regression / coverage evidence 記錄完成。
-   [x] GitHub Actions / CI acceptance gate 全綠。
-   [ ] post-merge consistency verification 完成。

## 14. Rollback and Isolation

如果未來 concrete Provider Adapter 需要替換：

1.  可移除或替換 provider-specific adapter；
2.  可移除 provider-specific dependency / configuration；
3.  保留 `AIProvider`, `AIRequest`, `AIResponse`；
4.  保留 provider-independent application services；
5.  保留 `FakeAIProvider` 與 deterministic tests；
6.  保留 Courseware Domain / Generator / Composition contracts；
7.  不需要 Courseware migration，因為 provider-specific state 不存入
    Courseware Domain。

如果 Milestone 6 acceptance 發現 regression，應修正或回退 Milestone 6
implementation，而不是放寬既有 Domain / Generator / Filesystem
contracts。

## 15. Code Review Checklist

### Architecture

-   [x] AI capability 沒有建立第二套 generation pipeline。
-   [x] Courseware Domain 不依賴 Provider SDK。
-   [x] Generator 不直接呼叫 AI Provider。
-   [x] AI Provider / service 不直接寫 production filesystem。
-   [x] Provider-specific types 留在 adapter boundary。
-   [x] existing Composition / GenerationPlan pipeline 保持 canonical。

### Contracts and Validation

-   [x] `AIRequest` / `AIResponse` 保持 provider-independent。
-   [x] AI output 被視為 untrusted input。
-   [x] structural validation 在 Domain integration 前執行。
-   [x] Domain validation 仍由 Courseware Domain 擁有。
-   [x] incomplete / invalid output 明確失敗。
-   [x] Prompt 未被當成 executable validation contract。

### Provider and Security

-   [x] Adapter implements existing `AIProvider`。
-   [x] finite timeout 已定義。
-   [x] provider errors 明確轉換並保留 chaining。
-   [x] unexpected programming errors 未被隱藏。
-   [x] credentials 未進入 models / Domain / generated output。
-   [x] normal logs / errors 不洩漏 credentials。
-   [x] live-provider invocation 保持 opt-in。

### Testing

-   [x] core tests 不需要 network。
-   [x] core tests 不需要 API key。
-   [x] `FakeAIProvider` deterministic。
-   [x] provider adapter tests deterministic。
-   [x] representative AI E2E deterministic。
-   [x] E2E 驗證 reproducibility。
-   [x] E2E 驗證 dry-run non-persistence。
-   [x] invalid AI response no-side-effect behavior 有驗證。
-   [x] non-AI regression suite 全綠。

### Documentation

-   [x] AI architecture 已同步。
-   [x] ADR 0021 / 0022 status 與 implementation 一致。
-   [x] ADR index 已同步。
-   [x] Roadmap 已同步。
-   [x] HISTORY 已同步。
-   [x] CHANGELOG 已同步。
-   [x] 本 acceptance record 已填入 final evidence。

### Automation

-   [x] `git diff --check` 通過。
-   [x] Ruff 通過。
-   [x] Ruff Format 通過。
-   [x] `pre-commit run --all-files` 通過。
-   [x] `python -m pytest` 通過。
-   [x] Coverage \>= 67.0%。
-   [x] GitHub Actions / CI 全綠。
-   [x] core CI 不依賴 live AI provider。

## 16. Acceptance Decision

目前決策：

``` text
Milestone 6 --- AI Integration
Status: Accepted
Local regression: 1119 passed, 1 deselected
Total coverage: 90.23%
Required coverage: 67.0%
Coverage gate: PASSED
GitHub Actions / CI: PASSED
```

architecture、contracts、provider adapter、representative E2E、Step 6.12
documentation alignment、final local regression、coverage gate 與 acceptance PR
CI 均已完成，因此 Milestone 6 formal acceptance 已成立。

merge 後仍需執行 post-merge consistency verification，以確認 `main`、
`origin/main` 與 acceptance documentation 完全一致；該檢查屬 repository
closure verification，不回溯否定已取得的 formal acceptance evidence。

------------------------------------------------------------------------

## Summary

Milestone 6 將 AI 納入 OPL，而沒有讓 AI 成為既有工程規則的例外。

核心責任鏈保持：

``` text
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

Step 6.10 已證明 real-provider infrastructure 可以被隔離、測試且不污染
Domain；Step 6.11 已證明 AI-generated structured course data 可以透過
production Domain、Composition、Generator 與 Filesystem pipeline 形成
deterministic courseware output。

Step 6.12 已將文件與 automation evidence 正式收束；Milestone 6 formal
acceptance 已完成。下一個動作是 merge 後執行 post-merge consistency
verification，而不是再新增新的 AI architecture。
