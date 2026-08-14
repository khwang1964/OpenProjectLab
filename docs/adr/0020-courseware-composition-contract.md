# ADR 0020: Courseware Composition Contract

- **Status:** Proposed
- **Date:** 2026-08-14
- **Milestone:** Milestone 5 — Composition Integration

## Context

OpenProjectLab（OPL）已建立並驗證共用 Generator architecture：`GenerateRequest` 是 canonical input boundary；`BaseGenerator.run(request)` 定義 validation → planning → execution lifecycle；`GenerationPlan` / `GenerationOperation` 是 planning boundary；`GenerationResult` 是 canonical execution result；filesystem、template rendering、dry-run、overwrite 與 manifest semantics 由共用 infrastructure 提供。

Milestone 5 已完成 Course / Week domain foundation，以及 Lab、Quiz、Assignment、Slides、Website vertical slices。這些 generator 已能獨立產生 deterministic output，但目前缺少正式 composition contract，描述高階 courseware intent 如何被拆成多個 generator requests，並以可預測、可測試、且不破壞既有 lifecycle 的方式執行。

若沒有此 contract，呼叫端容易把 orchestration 寫進 CLI、讓 generator 彼此呼叫、繞過 `BaseGenerator.run()`、依賴 plugin discovery 或 filesystem 的偶然順序，甚至錯誤宣稱跨 generator transaction / rollback。

因此，在加入 production orchestrator 前，必須先固定 Composition Layer 的責任、ordering、failure、dry-run、plugin interaction 與 result aggregation contract。

## Decision

OPL 將新增獨立的 **Courseware Composition Layer**。它負責把已驗證的高階 courseware intent 轉換成 deterministic ordered `GenerateRequest` sequence，解析對應 generator，並透過既有 canonical lifecycle 執行。

Canonical flow：

```text
Validated Courseware Intent
        ↓
Composition Layer
        ↓
Ordered GenerateRequest Sequence
        ↓
Generator Resolution
        ↓
BaseGenerator.run(request)
        ↓
GenerationResult
        ↓
Ordered Result Collection
```

Composition 是 orchestration boundary，不是新的 generator lifecycle、domain owner、renderer、filesystem abstraction 或 transaction manager。

### 1. Composition responsibilities

第一版 Composition Layer 只負責：

1. generator selection；
2. `GenerateRequest` construction；
3. deterministic request ordering；
4. generator resolution；
5. 透過 canonical lifecycle 執行 request；
6. ordered result aggregation；
7. failure context propagation。

Composition 不負責 template rendering、direct filesystem writes、manifest schema implementation、generator-specific validation/planning/execution、plugin discovery/validation implementation、hosting/deployment 或 cross-generator rollback。

### 2. Canonical generator lifecycle remains authoritative

Composition 不得自行重建 `validate_request() → plan() → execute()`。每個 request 必須經由 generator 的 canonical public lifecycle：

```python
generator.run(request)
```

或由既有 public wrapper 最終委派至同一 lifecycle。Composition 不得直接呼叫 internal lifecycle methods 建立旁路。

### 3. Generators must not call sibling generators

Generator 不得因 composition requirement 直接互相呼叫。

```text
Composition Layer
    ├── resolves CourseGenerator
    ├── resolves WeekGenerator
    ├── resolves LabGenerator
    ├── resolves QuizGenerator
    ├── resolves AssignmentGenerator
    ├── resolves SlidesGenerator
    └── resolves WebsiteGenerator
```

這保持每個 vertical slice 的獨立性，避免 circular dependency 與隱性 coupling。

### 4. Deterministic ordering

相同 validated composition input，在相同 configuration 與 generator availability 下，必須產生相同 generator selection、request ordering、targets、values 與 runtime options。

第一版 conceptual phase ordering：

```text
course
→ week(s)
→ learning materials
   ├── lab
   ├── quiz
   └── assignment
→ slides
→ website
```

此順序是第一版 composition contract 的可測試行為，不應被視為永久固定的 public SDK enumeration。實際 ordering 必須由 composition plan 明確表示，不得依賴 filesystem enumeration、set iteration、plugin discovery 或 entry-point enumeration 的偶然順序。同類 repeated items 保留 authored/domain ordering，除非後續 ADR 定義新的 canonical sort rule。

### 5. Composition input boundary

Composition input 必須足以明確決定 selected generators、每個 generator 的 target、`values`、`RuntimeOptions` 與 deterministic ordering。

Composition 不得藉由 repository crawling 或任意 filesystem inspection 推測完整 course structure。

第一版不要求立即新增 public composition-specific request model；若後續 contract tests 證明有必要，再進行獨立 SDK review。

### 6. Composition plan boundary

Composition 在 execution 前應建立可檢查、deterministic 的 composition plan，其核心語意為 ordered `GenerateRequest` sequence。

兩層 planning 必須分離：

```text
Composition Plan
    ↓
ordered GenerateRequest(s)

Generator Plan
    ↓
GenerationOperation(s)
```

Composition planning 不得 render template 或寫 filesystem，也不得改變單一 generator 的 `GenerationPlan` contract。

### 7. Generator resolution

Composition 必須透過既有 generator resolution / registry boundary 取得 generator，不得建立第二套 plugin discovery、entry-point loading 或 validation mechanism。

Built-in 與符合既有 Plugin SDK contract 的 third-party generator，原則上應可經相同 resolution boundary 被 composition 使用。第一版可以 built-ins 作 acceptance baseline，但 architecture 不得阻止既有 plugin boundary 的後續接入。

### 8. Result aggregation

每個 generator execution 繼續回傳 canonical `GenerationResult`。Composition 以 ordered collection 保留 execution order：

```text
[
    GenerationResult(course),
    GenerationResult(week-01),
    GenerationResult(lab-01),
    ...
]
```

第一版不要求建立 public `CompositionResult` hierarchy。若 implementation 需要 internal aggregate object，它不得取代 `GenerationResult` 或未經 SDK review 成為 public API。

### 9. Failure semantics

Composition 採 **fail-fast** semantics。

當某一 generator execution 失敗：

1. 立即停止後續 generator execution；
2. 已完成的先前 side effects 不自動 rollback；
3. 尚未執行的 generators 不得執行；
4. 保留原始 exception chain；
5. diagnostic context 應指出失敗 generator 與 composition position/request context。

第一版明確不提供 cross-generator transaction。

```text
A succeeds
B succeeds
C fails
D not executed
```

A、B 的 side effects 保留；不得把此行為描述為 atomic composition。

### 10. Dry-run semantics

Composition 必須尊重 shared `RuntimeOptions.dry_run`。每個 derived request 必須保留 dry-run；generator lifecycle 仍可進行 validation/planning，但不得產生 persistent filesystem mutation 或 manifest write。Composition 不建立第二套 dry-run behavior。

### 11. Overwrite semantics

Composition 不得覆寫 generator 的 overwrite policy，也不得因 orchestration 隱式啟用 force。`RuntimeOptions.overwrite` 必須明確傳遞並由既有 generator/filesystem contract 執行。

### 12. Manifest semantics

Manifest ownership 維持既有 generator/shared infrastructure contract。Composition 不直接修改 manifest、不建立 composition-specific manifest schema，也不重複記錄 generator 已記錄的 artifacts。若未來需要 course-level provenance manifest，另立 ADR。

### 13. Website and Slides boundaries

`SlidesGenerator` 與 `WebsiteGenerator` 保持 projection role。Composition 可提供 structured input，但 Slides / Website 不成為 Course domain owner，也不得反向控制其他 generators。

### 14. Plugin boundary

Composition 不得破壞既有 Plugin SDK、validation、entry-point 與 distribution direction：不新增第二套 registry、不繞過 plugin validation、不以 discovery order 決定 composition order。第三方 generator 若被選用，仍須遵循 canonical generator contract。

### 15. Public SDK boundary

ADR 0020 不自動擴張 `generator.sdk`。第一版 composition implementation 優先保持 internal/application-layer API，直到 contract、integration 與 third-party use cases 穩定。任何新的 public composition symbol 都需要獨立 SDK review。

## Determinism contract

至少保證：

```text
same input
→ same selected generators
→ same request sequence
→ same request targets
→ same request values
→ same RuntimeOptions
→ same execution ordering
```

Composition 不保證外部 non-deterministic plugin implementation 的內部行為，但不得自行引入 ordering nondeterminism。

## Validation contract

Composition-level validation 應在任何 generator execution side effect 前拒絕可預先判定的 invalid state，例如：required generator 無法解析、缺少 required composition input、非法 ordering metadata、composition identity 衝突、可在 composition level 判定的 invalid target relationship。

Generator-specific field validation仍由各 generator 負責，不在 composition 複製。

## Immutability contract

Composition planning 不得修改 caller-provided input：不得原地排序 collection、修改 nested mappings、把 derived fields 寫回 domain objects，或用 mutable shared context 在 executions 間傳遞隱性 state。Derived request data 應建立新的 immutable 或 logically immutable representation。

## Concurrency

第一版採 deterministic sequential execution，不加入 parallel execution。原因包括 artifact collision、manifest concurrency、plugin thread-safety 與 deterministic failure ordering 尚未正式建模。未來若要 parallelize，必須先定義 dependency graph、artifact conflict、manifest concurrency 與 deterministic result ordering。

## Security and path safety

Composition 不得降低 individual generator 的 path safety contract，也不得藉 composition 建立 arbitrary absolute output escape、repository crawling 或繞過 generator validation。個別 generator 的 path validation仍是最終 generator-specific boundary。

## Alternatives considered

### Alternative A — Generator-to-generator chaining

拒絕。會形成 generator coupling、lifecycle ownership 不清、測試困難、plugin substitution 困難，並增加 circular dependency 風險。

### Alternative B — Put orchestration directly in CLI

拒絕。CLI 會變成 architecture owner，composition 無法被其他 application layer reuse，且 presentation concerns 與 orchestration 混合。

### Alternative C — Create a giant CoursewareGenerator

拒絕。會破壞既有 vertical slices、重複 generator responsibilities、降低 plugin extensibility，並把 composition 誤當單一 generator。

### Alternative D — Cross-generator transactional rollback

第一版拒絕。現有 filesystem / manifest contract 沒有完整 transaction，overwrite rollback 需要 snapshot semantics，plugin side effects 也不保證可逆。未來若有需求另立 transaction ADR。

### Alternative E — Parallel execution by default

第一版拒絕。dependency、artifact collision、manifest concurrency 與 plugin thread-safety 尚未定義。

### Alternative F — Immediately publish Composition API in `generator.sdk`

拒絕。composition 尚在第一個 implementation cycle，public compatibility cost 過早，third-party composition use cases 尚未驗證。

## Consequences

### Positive

- 保留既有 canonical generator lifecycle。
- Courseware workflow 可從 isolated generators 演進到 deterministic composition。
- CLI 不成為 orchestration architecture owner。
- Built-in 與 plugin generators 可共享 resolution direction。
- failure behavior 明確且可測試。
- 不虛構 transaction / rollback guarantee。
- dry-run、overwrite、filesystem 與 manifest semantics 維持單一來源。
- 為 Milestone 5 representative E2E acceptance 建立基礎。

### Negative

- 第一版 sequential execution 不是最高效能。
- partial failure 會留下已完成 artifacts。
- 尚無 cross-generator dependency graph。
- 尚無 public composition SDK。
- caller 必須提供足夠 structured intent，不能依賴 repository crawling 推測。
- transactional composition 或 parallel execution 需要後續 ADR。

## Migration plan

### Phase 1 — Design

1. 接受 ADR 0020 的 composition boundaries。
2. 在 `docs/adr/README.md` 登錄 ADR 0020。
3. 明確記錄 composition 不取代 generator lifecycle。

### Phase 2 — Contract tests

建議新增：

```text
tests/courseware/test_composition_contract.py
```

至少驗證 deterministic request sequence、authored ordering、generator resolution、canonical `run()` usage、ordered results、fail-fast、no execution after failure、exception context、dry-run / overwrite propagation、no direct filesystem writes、immutability 與 no accidental SDK expansion。

Contract tests 必須先於 production implementation merge。

### Phase 3 — Minimum implementation

預期 implementation location：

```text
generator/courseware/composition.py
```

實際 module / symbol name 由 contract-test branch 最終確認。第一版不加入 parallel execution、rollback、repository crawling、deployment、新 plugin system 或 public SDK expansion。

### Phase 4 — Integration / representative E2E

建立 representative flow：

```text
Course / Week
→ material generator(s)
→ Slides
→ Website
```

驗證 deterministic output、dry-run、overwrite、manifest compatibility、application/CLI boundary 與 failure semantics。

### Phase 5 — Acceptance

同步 architecture、roadmap、HISTORY、CHANGELOG、regression baseline、coverage gate 與 CI，最後將 ADR `Proposed → Accepted`。

## Test strategy

### Contract tests

核心測試至少包含：

1. composition produces ordered requests；
2. same input produces same composition plan；
3. caller input is not mutated；
4. generators execute in declared order；
5. every execution uses canonical lifecycle；
6. results preserve execution order；
7. failure stops later executions；
8. original exception remains preserved/chained；
9. dry-run propagates to every request；
10. overwrite policy propagates without implicit force；
11. composition does not directly write files；
12. plugin/registry discovery order does not determine composition order；
13. no composition-specific public SDK symbols are required。

### Integration tests

建議新增：

```text
tests/courseware/test_composition_integration.py
```

驗證 real built-in generators 的 representative composition。

### CLI / E2E tests

若 Composition 在 Milestone 5 提供 CLI entry point，再新增：

```text
tests/integration/test_courseware_composition_cli.py
```

CLI contract 應在 integration phase 明確定義，不由本 ADR 預先擴張。

### Regression gates

每個 phase 必須通過：

```text
ruff
ruff format
git diff --check
pre-commit
pytest
coverage gate
CI
```

## Documentation changes

實作與 acceptance 過程同步更新：

```text
docs/adr/README.md
docs/architecture/open-courseware-platform.md
docs/roadmap.md
docs/HISTORY.md
CHANGELOG.md
```

Architecture 文件必須清楚區分 composition responsibilities、generator responsibilities、plugin/registry boundary、failure semantics、non-transactional guarantee 與 dry-run semantics。

## Rollback plan

ADR 0020 在 `Proposed` 階段可移除未接受的 composition implementation/tests 而不影響既有 generators。

若 implementation 已 merge 但尚未 acceptance：

1. 停止新增 composition consumers；
2. revert composition-specific production integration；
3. 保留各 generator vertical slice；
4. 不修改 `BaseGenerator` lifecycle 以遷就失敗的 composition design；
5. 必要時以新 ADR 取代 ADR 0020。

Composition rollback 不應要求回退 Course、Week、Lab、Quiz、Assignment、Slides 或 Website generators。

## Code Review Checklist

### Architecture

- [ ] Composition 是 orchestration layer，不是新的 generator lifecycle。
- [ ] 所有 generator execution 經 canonical `BaseGenerator.run(request)` boundary。
- [ ] Generator 不直接呼叫 sibling generator。
- [ ] Composition 不直接 render template 或寫 filesystem。
- [ ] Composition 不重做 manifest infrastructure。
- [ ] Composition 不建立第二套 plugin discovery / registry。
- [ ] Website / Slides 維持 projection role。
- [ ] 第一版沒有宣稱 transaction / rollback。
- [ ] 第一版沒有加入 parallel execution。

### Contract

- [ ] Request selection 與 ordering deterministic。
- [ ] Authored repeated-item ordering 被保留。
- [ ] Composition planning 不修改 caller input。
- [ ] Result aggregation 保留 execution order。
- [ ] Failure semantics 為 fail-fast，且保留原始 exception context。
- [ ] Dry-run 與 overwrite policy 正確傳遞。
- [ ] Generator-specific validation 沒有被複製到 composition。

### Plugin / SDK

- [ ] 使用既有 generator resolution boundary。
- [ ] 不依賴 plugin discovery order 決定 composition order。
- [ ] 不繞過 plugin validation。
- [ ] 沒有意外新增 `generator.sdk` public symbols。
- [ ] 若 public API 有變更，已有獨立 ADR / SDK review。

### Testing

- [ ] Contract tests 先於 production implementation。
- [ ] Determinism、immutability、fail-fast、no-execution-after-failure、dry-run 有直接測試。
- [ ] Representative built-in integration 有測試。
- [ ] Full regression suite、coverage gate 與 CI 通過。

### Documentation

- [ ] ADR index 已同步。
- [ ] Open Courseware architecture、Roadmap、HISTORY、CHANGELOG 已同步。
- [ ] Acceptance 後 ADR status 已由 `Proposed` 改為 `Accepted`。

## Decision summary

OPL 採用獨立 Courseware Composition Layer，將高階 courseware intent deterministic 地轉換為 ordered `GenerateRequest` sequence，透過既有 generator resolution boundary 解析 generator，並以 canonical `BaseGenerator.run(request)` lifecycle sequentially 執行。

Composition 負責 orchestration，不負責 rendering、filesystem、manifest implementation、plugin discovery 或 generator-specific lifecycle。第一版採 deterministic sequential execution、ordered `GenerationResult` aggregation 與 fail-fast semantics；不提供 cross-generator rollback、parallel execution、repository crawling 或 public SDK expansion。

此 contract 為 Milestone 5 Composition Integration 與後續 representative E2E acceptance 的架構基礎。
