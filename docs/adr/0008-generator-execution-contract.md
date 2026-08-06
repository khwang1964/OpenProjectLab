# ADR 0008: Generator Execution Contract

* **Status:** Proposed
* **Date:** 2026-08-06
* **Decision Makers:** OpenProjectLab Maintainers
* **Related ADRs:**

  * ADR 0002 – Generator Lifecycle
  * ADR 0004 – Remove Generator-specific Result Types
  * ADR 0006 – Generator Planning Lifecycle
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

然而，目前仍缺少一份正式文件，定義 **Generator 的完整執行生命週期（Execution Lifecycle）**。

如果沒有明確的 Execution Contract，未來新增 Generator 或 Plugin 時可能會：

* 繞過 Validation。
* 在 Planning 階段直接寫入檔案。
* 在失敗後留下部分輸出。
* 更新 Manifest 的時機不一致。
* 造成不同 Generator 擁有不同執行流程。

因此需要建立一份正式的 Execution Contract。

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

# Proposed Lifecycle

```text
generate()

    │

    ├── validate(request)

    │

    ├── create_generation_plan(request)

    │

    ├── execute(plan)

    │

    └── return GenerationResult
```

`generate()` 應為唯一公開入口（Public Entry Point）。

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
* 驗證 Template 是否存在
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

* 回傳 Framework Exception
* 保留 Exception Chaining
* Partial Failure 行為由 Filesystem Contract 定義

---

# Framework Responsibilities

Framework（Base Generator）負責：

* 控制 Lifecycle
* 呼叫順序
* Exception Propagation
* Dry Run 行為
* Result Aggregation

Framework 不負責：

* 課程內容
* Template Context
* Generator-specific Validation Rules

---

# Generator Responsibilities

Concrete Generator 應只負責：

* Validation Rules
* Generation Planning
* Domain-specific Rendering
* Generator Metadata

Concrete Generator 不應：

* 改變生命週期
* 直接控制流程
* 繞過 Validation
* 在 Planning 階段寫入檔案

---

# Expected Public Contract

未來建議 Base Generator 提供固定骨架：

```text
generate()
    ├── validate()
    ├── create_generation_plan()
    ├── execute()
    └── return GenerationResult
```

Hook 名稱可調整，但生命週期不得改變。

---

# Testing Requirements

所有 Generator 必須通過共同 Execution Contract 測試。

至少涵蓋：

* Validation 先於 Planning。
* Planning 先於 Execution。
* Validation Failure 不產生副作用。
* Planning Failure 不產生副作用。
* Dry Run 不寫入檔案。
* Execution 回傳 GenerationResult。
* Bootstrap、Course、Week 使用相同 Lifecycle。

---

# Migration Strategy

現有內建 Generator：

* Bootstrap Generator
* Course Generator
* Week Generator

應逐步收斂至共同 Execution Skeleton。

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
* Generator 可自由發揮的空間降低。
* 新增 Hook 時需維護向後相容。

---

# Code Review Checklist

* [ ] `generate()` 為唯一 Public Entry Point。
* [ ] Validation 發生於任何副作用之前。
* [ ] Planning 不直接操作 Filesystem。
* [ ] Execution 為唯一副作用階段。
* [ ] Dry Run 不修改 Persistent State。
* [ ] 回傳 `GenerationResult`。
* [ ] Bootstrap、Course、Week 遵循相同生命週期。
* [ ] Exception Propagation 一致。
* [ ] Architecture、Tests、Implementation 保持同步。

---

# Status

本 ADR 定義 Generator Execution Contract，作為後續 Base Generator Skeleton、Filesystem Integration、Plugin Generator API 與 Execution Framework 的設計依據。
