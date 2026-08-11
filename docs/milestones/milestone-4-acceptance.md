# Milestone 4 Acceptance Review --- Plugin Ecosystem

> Status: Accepted / Completed Milestone: 4 --- Plugin Ecosystem /
> Plugin SDK Review Date: 2026-08-11 Baseline: `main` after PR #37
> Acceptance Commit: `13eac54` ---
> `test: validate installed example plugin entry point (#37)`

------------------------------------------------------------------------

## 1. Purpose

本文件是 OpenProjectLab（OPL）Milestone 4 的正式 Exit Criteria 與
Acceptance Record。

Milestone 4 的目標是：

> 讓第三方開發者可以透過穩定的 Public SDK 與標準 Python packaging
> metadata 開發、封裝、安裝、發現與載入 OPL Generator
> Plugin，而不需要修改核心 Framework 或依賴 host private
> implementation。

本 Acceptance Review 不新增新的 runtime contract。

它確認 Milestone 4 已完成的
architecture、tests、documentation、automation 與 migration work
是否足以關閉此 Milestone。

------------------------------------------------------------------------

## 2. Acceptance Decision

**Decision: ACCEPTED**

Milestone 4 已達成目前定義的核心目標，正式狀態更新為：

``` text
Milestone 4 — Plugin Ecosystem
Status: Completed
```

Milestone 4 建立的 canonical third-party Plugin flow：

``` text
Third-Party Python Distribution
        ↓
generator.sdk
        ↓
BaseGenerator subclass
        ↓
openprojectlab.generators
        ↓
importlib.metadata Entry Point discovery
        ↓
EntryPoint.load()
        ↓
validate_plugin_generator()
        ↓
entry_point.name == generator.name
        ↓
transactional preflight
        ↓
GeneratorRegistry
```

任何 Plugin contract failure 必須在 Registry mutation 前停止，因此正式
runtime 保持：

``` text
no partial registration
```

------------------------------------------------------------------------

## 3. Exit Criteria

### 3.1 Public SDK Boundary --- PASS

第三方 Plugin 的正式 dependency boundary 已收斂為：

``` text
generator.sdk
```

已建立：

-   Public SDK façade；
-   Public export contract tests；
-   third-party-style Generator contract tests；
-   Plugin authoring documentation；
-   example Plugin 的 SDK-only import contract。

第三方 Plugin 不應依賴：

``` text
generator.core.*
generator.generators.*
generator.plugins.*
```

**Result: PASS**

------------------------------------------------------------------------

### 3.2 Generator Lifecycle Contract --- PASS

Milestone 4 沿用 Milestone 3 已接受的 canonical lifecycle：

``` text
GenerateRequest
    ↓
validate_request()
    ↓
plan()
    ↓
GenerationPlan
    ↓
execute()
    ↓
GenerationResult
```

`BaseGenerator.run()` 仍由 Framework 控制。

Plugin architecture 沒有建立第二套 execution lifecycle。

**Result: PASS**

------------------------------------------------------------------------

### 3.3 Plugin Validation Contract --- PASS

ADR 0011 已建立正式 Plugin validation boundary。

Plugin Generator 必須：

-   resolve 成 class；
-   繼承 `BaseGenerator`；
-   不是 `BaseGenerator` 本身；
-   為 concrete class；
-   提供合法 public name；
-   支援 zero-argument construction。

Plugin-facing validation failure 使用：

``` text
PluginError
```

Validation 與 Registry mutation 保持分離。

**Result: PASS**

------------------------------------------------------------------------

### 3.4 Registry and Transaction Semantics --- PASS

Plugin loading 已建立：

``` text
load all
    ↓
validate all
    ↓
identity-check all
    ↓
preflight all
    ↓
register all
```

已由 contract / integration tests 保護：

-   invalid candidate 不造成 partial registration；
-   later load failure 不造成 partial registration；
-   duplicate batch identity 在 mutation 前失敗；
-   existing Registry collision 在 mutation 前失敗；
-   failure 後既有 Registry state 保持不變。

**Result: PASS**

------------------------------------------------------------------------

### 3.5 Python Entry Point Contract --- PASS

ADR 0012 已將 Python Entry Points 定義為 Plugin SDK v1 的正式
distribution discovery contract。

Canonical group：

``` text
openprojectlab.generators
```

正式 object contract：

``` text
one Entry Point
    ↓
one type[BaseGenerator]
```

正式 identity contract：

``` text
entry_point.name == generator_class.name
```

不支援 factory、instance、module 或 arbitrary callable 作為 v1 Entry
Point target。

**Result: PASS**

------------------------------------------------------------------------

### 3.6 Legacy Runtime Removal --- PASS

Legacy：

``` text
generator/core/plugin.py
PluginManager
PluginDescriptor
```

已完成 caller inventory、architecture removal tests 與獨立 removal PR。

Canonical runtime 已完全收斂至：

``` text
generator.plugins
```

並由 architecture test 防止 production source 重新 import legacy
`generator.core.plugin` path。

**Result: PASS**

------------------------------------------------------------------------

### 3.7 Plugin Authoring Documentation --- PASS

已建立：

``` text
docs/plugin-authoring.md
docs/architecture/sdk.md
docs/architecture/plugin-sdk-contract-inventory.md
```

並同步：

``` text
README.md
docs/HISTORY.md
docs/roadmap.md
CHANGELOG.md
```

Plugin authoring guide 已涵蓋：

-   Public SDK imports；
-   `BaseGenerator` contract；
-   naming；
-   zero-argument constructor；
-   Entry Point declaration；
-   metadata/runtime identity；
-   transaction guarantee；
-   PluginError boundary；
-   testing；
-   compatibility expectations；
-   security/trust boundary。

**Result: PASS**

------------------------------------------------------------------------

### 3.8 Example Third-Party Plugin --- PASS

已建立：

``` text
examples/plugins/hello-generator/
```

包含：

``` text
pyproject.toml
README.md
src/opl_hello_plugin/
tests/
```

Example Plugin：

-   只依賴 `generator.sdk`；
-   宣告 `openprojectlab.generators`；
-   使用 `hello-plugin` 作為 metadata/runtime identity；
-   支援 zero-argument construction；
-   實作 canonical planning/execution contract；
-   有 standalone tests；
-   有 host-side architecture contract tests。

**Result: PASS**

------------------------------------------------------------------------

### 3.9 Installed Distribution End-to-End Validation --- PASS

Step 4E-3 已驗證真正 installed Python distribution，而不是只使用 fake
Entry Point 或 source-path simulation。

測試流程：

``` text
examples/plugins/hello-generator
        ↓
pip install --target <temporary directory>
        ↓
real distribution metadata
        ↓
importlib.metadata
        ↓
openprojectlab.generators
        ↓
hello-plugin
        ↓
EntryPoint.load()
        ↓
canonical Plugin validation
        ↓
transactional registration
        ↓
GeneratorRegistry
```

此測試使用 temporary target，不污染 active development environment。

同時確認 Plugin loading 不執行：

``` text
run()
plan()
execute()
```

**Result: PASS**

------------------------------------------------------------------------

## 4. Architecture Decisions

Milestone 4 的主要 architecture decisions：

``` text
ADR 0010 — Plugin SDK Public Contract
ADR 0011 — Plugin Validation Contract
ADR 0012 — Plugin Entry Point Contract
```

三者共同建立：

``` text
Public SDK boundary
        +
Plugin structural validation
        +
installed-distribution discovery
        +
identity validation
        +
transactional registration
```

Milestone 4 acceptance 不修改上述 accepted contracts。

------------------------------------------------------------------------

## 5. Verification Evidence

Milestone 4 最終 acceptance baseline：

``` text
452 passed
Total coverage: 85.90%
Required coverage: 67.0%
```

已執行的 quality gates 包括：

``` text
Plugin subsystem pytest
full pytest
coverage gate
Ruff
Ruff format
pre-commit
git diff --check
GitHub Actions CI
```

PR #37 已 merge 至 `main`：

``` text
13eac54 test: validate installed example plugin entry point (#37)
```

因此 installed-distribution E2E proof 已成為 `main` baseline。

------------------------------------------------------------------------

## 6. Documentation Exit Criteria

Milestone 4 關閉時應保持下列文件一致：

  Document                                               Acceptance
  ------------------------------------------------------ ------------
  `docs/adr/0010-plugin-sdk-public-contract.md`          PASS
  `docs/adr/0011-plugin-validation-contract.md`          PASS
  `docs/adr/0012-plugin-entry-point-contract.md`         PASS
  `docs/architecture/sdk.md`                             PASS
  `docs/architecture/plugin-sdk-contract-inventory.md`   PASS
  `docs/plugin-authoring.md`                             PASS
  `README.md`                                            PASS
  `docs/HISTORY.md`                                      PASS
  `docs/roadmap.md`                                      PASS
  `CHANGELOG.md`                                         PASS
  `docs/milestones/milestone-4-acceptance.md`            PASS

------------------------------------------------------------------------

## 7. Deferred Work

以下工作具有價值，但不屬於 Milestone 4 核心 exit blocker，因此移至後續
Milestone / future Plugin evolution：

-   richer Plugin metadata model；
-   explicit Plugin/host version compatibility metadata；
-   compatibility diagnostics；
-   Plugin isolation / sandbox strategy；
-   marketplace / package catalog；
-   richer Plugin management UX；
-   additional third-party example packages；
-   Public SDK evolution beyond v1。

這些工作若改變 Plugin SDK v1 compatibility surface，必須使用新的 ADR 與
migration strategy。

------------------------------------------------------------------------

## 8. Milestone 4 Definition of Done

### Architecture

-   [x] Public SDK boundary 已定義。
-   [x] Plugin validation boundary 已定義。
-   [x] Python Entry Point contract 已定義。
-   [x] Registry transaction semantics 已定義。
-   [x] legacy Plugin runtime 已移除。
-   [x] canonical runtime 為單一路徑。

### Testing

-   [x] SDK public export tests。
-   [x] third-party-style SDK contract tests。
-   [x] Plugin validation tests。
-   [x] Registry contract tests。
-   [x] Plugin loading integration tests。
-   [x] Entry Point contract tests。
-   [x] transactional Entry Point integration tests。
-   [x] legacy removal architecture tests。
-   [x] example third-party Plugin tests。
-   [x] real installed-distribution E2E test。
-   [x] full repository suite Green。
-   [x] coverage gate Green。

### Documentation

-   [x] ADR 0010。
-   [x] ADR 0011。
-   [x] ADR 0012。
-   [x] SDK architecture。
-   [x] Plugin authoring guide。
-   [x] example Plugin README。
-   [x] contract inventory updated。
-   [x] Roadmap updated。
-   [x] History updated。
-   [x] Changelog updated。
-   [x] Milestone acceptance record。

### Automation

-   [x] Ruff。
-   [x] Ruff format。
-   [x] pre-commit。
-   [x] pytest。
-   [x] Coverage。
-   [x] GitHub Actions CI。
-   [x] `git diff --check`。

------------------------------------------------------------------------

## 9. Code Review Checklist

### Acceptance Integrity

-   [ ] Acceptance document only claims behavior already merged to
    `main`.
-   [ ] `452 passed / 85.90%` matches the final reported acceptance run.
-   [ ] PR #37 / commit `13eac54` is recorded as the E2E acceptance
    baseline.
-   [ ] Deferred work is not incorrectly presented as completed.
-   [ ] Milestone 4 is marked Completed consistently across Roadmap,
    History, and Changelog.

### Architecture

-   [ ] `generator.sdk` remains the third-party dependency boundary.
-   [ ] `openprojectlab.generators` remains the canonical Entry Point
    group.
-   [ ] Entry Point identity contract remains documented.
-   [ ] no-partial-registration remains an explicit invariant.
-   [ ] legacy PluginManager is not reintroduced.

### Documentation

-   [ ] Roadmap moves Milestone 4 from In Progress to Completed.
-   [ ] History records the completed Plugin Ecosystem evolution.
-   [ ] Changelog records example Plugin and installed-distribution E2E
    validation.
-   [ ] Milestone 5 becomes the next active milestone.

### Quality

-   [ ] `git diff --check` passes.
-   [ ] `pre-commit run --all-files` passes.
-   [ ] `python -m pytest` passes.
-   [ ] CI passes before merge.

------------------------------------------------------------------------

## 10. Final Acceptance

Milestone 4 is accepted as complete.

OPL now has a tested third-party Generator Plugin path that begins at a
real installed Python distribution and ends at the canonical
`GeneratorRegistry`, while keeping Plugin authors on the versioned
`generator.sdk` boundary.

The project may now proceed to:

``` text
Milestone 5 — Open Courseware Platform
```

without requiring additional Milestone 4 runtime work as an exit
condition.
