# ADR 0008: Generator Execution Contract

* **Status:** Accepted
* **Date:** 2026-08-06
* **Decision Makers:** OpenProjectLab Maintainers
* **Related ADRs:**

  * ADR 0002 – Generator Lifecycle
  * ADR 0004 – Remove Generator-specific Result Types
  * ADR 0006 – Generator Validation Contract
  * ADR 0007 – Generation Plan Contract
* **Related Documents:**

  * `docs/architecture/generator.md`
  * `docs/architecture/filesystem.md`
  * `docs/reference/filesystem.md`

---

# Context

OpenProjectLab（OPL）已完成數個重要演進：

* 建立共用 `GenerationResult` 契約。
* 導入 Generator Planning Lifecycle。
* 建立 Generator Validation Contract。
* 將 Bootstrap、Course 與 Week Generator 統一至相同的 Result Model。

目前 OPL 已具備共用 `GenerateRequest`、`GenerationPlan` 與 `GenerationResult`，並已在 `BaseGenerator.run()` 中建立實際執行骨架。本 ADR 正式定義並接受 **Generator 的完整執行生命週期（Execution Lifecycle）**，以避免既有與未來 Generator 產生不一致的執行順序。

如果沒有明確的 Execution Contract，未來新增 Generator 或 Plugin 時可能會：

* 繞過 Validation。
* 在 Planning 階段直接寫入檔案。
* 在失敗後留下部分輸出。
* 更新 Manifest 的時機不一致。
* 造成不同 Generator 擁有不同執行流程。

因此需要將現有行為收斂為正式且可測試的 Execution Contract。

---

# Decision

所有 Generator 必須遵循相同的 Execution Lifecycle：

```text
GenerateRequest
        │
        ▼
Validation
        │
        ▼
Generation Planning
        │
        ▼
Execution
        │
        ▼
GenerationResult
```

Framework 必須負責控制整個生命週期。

具體 Generator 只能實作各階段的業務邏輯，不得改變執行順序。

---

# Canonical Lifecycle

```text
run(request)
    │
    ├── validate_request(request)
    │
    ├── plan(request)
    │
    ├── execute(request, plan)
    │
    └── return GenerationResult
```

`BaseGenerator.run()` 是 Framework 控制的 canonical execution entry point。

Concrete Generator 應透過以下 hooks 提供專屬行為：

* `validate_request(request)`
* `plan(request)`
* `execute(request, plan)`

Concrete Generator 不應覆寫 `run()`，因為這可能繞過 validation、planning、
dry-run 語意與 result contract。

---

# Stage Responsibilities

## 1. Validation

目的：

驗證所有輸入是否符合 Generator 契約。

不得：

* 建立目錄
* 建立檔案
* 更新 Manifest
* 修改任何外部狀態

可以：

* 驗證參數
* 驗證 Metadata
* 驗證 Template Root 與必要 Template
* 驗證設定是否合法

Validation Failure 必須保證 **Zero Side Effects**。

---

## 2. Generation Planning

目的：

建立完整且可執行的 Generation Plan。

Plan 至少應描述：

* Destination Paths
* Template Mapping
* Write Policy
* Runtime Options
* 預計產生的檔案

Planning 應保持可預測與可測試。

不得直接操作 Filesystem。

---

## 3. Execution

Execution 根據 Generation Plan 執行實際工作。

包括：

* Template Rendering
* Filesystem Writing
* Manifest 更新（如適用）
* GenerationResult 建立

Execution 是唯一允許產生外部副作用的階段。

---

## 4. Result

Execution 完成後回傳：

```python
GenerationResult
```

所有內建 Generator 必須遵循相同 Result Contract。

不得再回傳 Generator-specific Result Types。

---

# Dry Run

Dry Run 必須完整執行：

* Validation
* Planning

可以執行：

* Template Resolution
* 衝突檢查

不得：

* 建立目錄
* 寫入檔案
* 修改 Manifest
* 更新任何 Persistent State

Dry Run 回傳的 `GenerationResult` 應完整描述預計操作。

---

# Failure Semantics

Validation Failure

* 停止流程
* 不建立 Plan
* 無任何副作用

Planning Failure

* 停止流程
* 不進入 Execution
* 無任何副作用

Execution Failure

* 向上傳遞具語意的 Framework Exception
* 保留原始 Exception Chaining
* 不重新啟動 lifecycle
* Partial Failure 行為由 Filesystem Contract 定義

---

# Framework Responsibilities

Framework（Base Generator）負責：

* 控制 Lifecycle
* 呼叫順序
* Exception Propagation
* Lifecycle ordering
* Exception Propagation
* Canonical entry-point semantics

Framework 不負責：

* 課程內容
* Template Context
* Generator-specific Validation Rules

---

# Generator Responsibilities

Concrete Generator 應只負責：

* Validation Rules
* Generation Planning
* Domain-specific Rendering 與寫入協調
* Generator Metadata

Concrete Generator 不應：

* 改變生命週期
* 直接控制流程
* 繞過 Validation
* 在 Planning 階段寫入檔案

---

# Public Contract

目前 `BaseGenerator` 提供以下固定骨架：

```text
run(request)
    ├── validate_request(request)
    ├── plan(request)
    ├── execute(request, plan)
    └── return GenerationResult
```

此順序由 Framework 擁有，Concrete Generator 只能實作各階段 hooks，不得改變生命週期。

---

# Testing Requirements

所有 Generator 必須通過共同 Execution Contract 測試。目前已建立 `tests/generators/test_generator_execution_contract.py`，驗證 canonical lifecycle ordering 與 failure boundaries。

至少涵蓋：

* Validation 先於 Planning。
* Planning 先於 Execution。
* Validation Failure 不產生副作用。
* Planning Failure 不產生副作用。
* Dry Run 不寫入檔案。
* Execution 回傳 GenerationResult。
* `run()` 將 `plan()` 建立的同一份 `GenerationPlan` 傳入 `execute()`。
* Dry Run 走過完整 lifecycle，但不修改 filesystem 或 manifest。
* Execution Failure 不會重新啟動 lifecycle。
* Bootstrap、Course、Week 使用相同 Lifecycle。

---


# Compatibility Decision

`BaseGenerator` 目前暫時保留以下 legacy `GeneratorContext` hooks：

* `validate(context)`
* `prepare(context)`
* `generate(context)`
* `post_generate(context)`
* `cleanup(context)`

這些 hooks **不屬於** canonical `GenerateRequest` execution contract，也不會由
`run(GenerateRequest)` 呼叫。

保留這些方法的目的，是避免在本 ADR 中同時引入破壞性 API 移除。移除或正式標示
deprecated 必須由後續獨立 ADR、migration tests 與 implementation PR 處理。

本決策不新增 runtime warning，也不改變既有 CLI 或內建 Generator 行為。

---

# Migration Strategy

現有內建 Generator：

* Bootstrap Generator
* Course Generator
* Week Generator

已透過 `BaseGenerator.run()` 收斂至共同 Execution Skeleton。後續工作聚焦於移除或隔離 legacy lifecycle，而不是重新設計 canonical lifecycle。

未來 Plugin Generator 必須遵循相同 Contract。

---

# Consequences

## Positive

* Generator 行為一致。
* Framework 可維護性提高。
* Dry Run 行為一致。
* Plugin 更容易整合。
* Execution 可測試。
* Lifecycle 更容易文件化。

## Trade-offs

* Framework 控制力增加。
* Legacy lifecycle 暫時形成相容性負擔。
* Generator 可自由發揮的空間降低。
* 新增 Hook 時需維護向後相容。

---

# Code Review Checklist

* [x] `run(GenerateRequest)` 為 canonical execution entry point。
* [x] Lifecycle 順序固定為 `validate_request → plan → execute`。
* [x] Validation 發生於任何副作用之前。
* [x] Planning 不直接操作 Filesystem。
* [x] Execution 為唯一允許執行或模擬副作用的階段。
* [x] Dry Run 走過完整 lifecycle 且不修改 Persistent State。
* [x] `execute()` 接收 `plan()` 建立的同一份 `GenerationPlan`。
* [x] 回傳共用 `GenerationResult`。
* [x] Execution Contract tests 已覆蓋 lifecycle ordering 與 failure boundaries。
* [x] Legacy `GeneratorContext` lifecycle 被標示為 compatibility-only。
* [x] Architecture、Tests、Implementation 保持同步。

---

# Status

本 ADR 已接受 `BaseGenerator.run()` 作為 canonical execution entry point，並由 `tests/generators/test_generator_execution_contract.py` 驗證 lifecycle ordering、failure boundaries 與 dry-run zero-side-effect semantics。

Legacy `GeneratorContext` lifecycle 仍暫時保留，後續移除需由獨立 ADR 與 migration work 處理。
