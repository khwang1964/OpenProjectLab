# ADR 0009：移除 Legacy Generator Lifecycle

* **狀態（Status）：** Proposed
* **日期（Date）：** 2026-08-06
* **決策者（Deciders）：** OpenProjectLab Architecture Team
* **技術主題（Technical Story）：** 完成 Generator Execution Contract 遷移，移除 Legacy Generator Lifecycle
* **取代（Supersedes）：** 無
* **被取代（Superseded by）：** 無

---

# 背景（Context）

截至目前為止，OpenProjectLab 已逐步完成 Generator Framework 的核心架構重整：

* ADR 0005：Generator Input Contract
* ADR 0006：Generator Validation Contract
* ADR 0007：Generation Plan Contract
* ADR 0008：Generator Execution Contract

目前所有內建 Generator 均透過 `BaseGenerator.run()` 執行共同生命週期，其標準流程如下：

```text
GenerateRequest
        │
        ▼
validate_request()
        │
        ▼
plan()
        │
        ▼
execute()
        │
        ▼
GenerationResult
```

上述流程已由共同契約（Contract）與測試保護，包括：

* Execution Contract Tests
* Validation Contract Tests
* Generation Plan Contract Tests

目前 `run()` 已成為 Framework 唯一管理 Generator 執行流程的入口（Canonical Execution Entry Point）。

然而，`BaseGenerator` 仍保留早期版本的 Legacy Lifecycle：

```text
validate(context)
prepare(context)
generate(context)
post_generate(context)
cleanup(context)
```

此生命週期已不再參與目前 Generator Framework 的主要執行流程，其存在目的僅為維持舊版 API 相容性。

---

# 問題（Problem Statement）

## 一、Framework 同時存在兩套生命週期

目前 Framework 同時提供：

* GenerateRequest Lifecycle（正式）
* GeneratorContext Lifecycle（Legacy）

兩者皆可視為 Generator API，容易造成架構混淆。

---

## 二、Generator 擴充點不夠明確

新的 Generator 作者可能產生下列疑問：

* 是否仍需實作 `generate()`？
* 是否可以覆寫 `run()`？
* `GeneratorContext` 是否仍為正式 API？

上述問題皆增加 Framework 的學習成本。

---

## 三、增加維護成本

保留 Legacy Lifecycle 必須同步維護：

* 文件
* Architecture
* Code Review Checklist
* Migration Guide
* Compatibility 說明

但對目前 Framework 已無實際功能價值。

---

## 四、增加測試成本

每一個 Legacy API 都需要：

* 相容性測試
* 文件維護
* Review
* Migration 支援

長期而言將增加技術債。

---

# 決策（Decision）

OpenProjectLab 採用單一 Generator Execution Lifecycle。

正式生命週期如下：

```text
run(request)
        │
        ▼
validate_request(request)
        │
        ▼
plan(request)
        │
        ▼
execute(request, plan)
        │
        ▼
GenerationResult
```

Framework 保證上述執行順序不可改變。

Concrete Generator 僅允許透過下列方法進行客製化：

* `validate_request()`
* `plan()`
* `execute()`

不建議覆寫：

```text
run()
```

因為覆寫可能繞過：

* Validation
* Planning
* Dry Run
* GenerationResult
* Framework 控制流程

---

# Legacy Lifecycle 處理策略

本 ADR 建議於後續 Implementation PR 中移除下列方法：

* `validate(context)`
* `prepare(context)`
* `generate(context)`
* `post_generate(context)`
* `cleanup(context)`

移除後：

* `GeneratorContext` 不再作為 Generator Execution API。
* `GenerateRequest` 成為唯一正式輸入模型。
* `GenerationPlan` 成為唯一規劃模型。
* `GenerationResult` 成為唯一輸出模型。

---

# 相容性分析（Compatibility Analysis）

## 內建 Generator

目前：

* BootstrapGenerator
* CourseGenerator
* WeekGenerator

皆已透過：

```text
run()
→ validate_request()
→ plan()
→ execute()
```

執行。

因此預期：

**不需修改 Generator 行為。**

---

## CLI

CLI 已全面使用：

* GenerateRequest
* GenerationResult

因此：

**CLI 不受影響。**

---

## Contract Tests

目前已有：

* Validation Contract
* Execution Contract
* Generation Plan Contract

皆不依賴 Legacy Lifecycle。

因此：

**既有 Contract Tests 不需修改。**

---

## 第三方 Generator

若外部 Generator 仍依賴：

```text
generate(context)
```

則需依 Migration Guide 遷移至：

* `validate_request()`
* `plan()`
* `execute()`

---

# Migration Strategy

Migration 分為四個階段。

## Phase 1：Architecture（本 ADR）

完成 Legacy Lifecycle Removal 設計。

---

## Phase 2：Migration Tests

新增：

* Legacy Lifecycle Removal Contract Tests
* Compatibility Tests

確認：

* Legacy API 已不再使用
* Canonical Lifecycle 不受影響

---

## Phase 3：Implementation

重構 `BaseGenerator`：

* 移除 Legacy Hooks
* 簡化 BaseGenerator
* 移除 Compatibility Code
* 更新 Architecture

---

## Phase 4：Cleanup

完成：

* 文件更新
* CHANGELOG
* Migration Guide
* Architecture
* Code Review Checklist

---

# 替代方案（Alternatives Considered）

## 方案一：永久保留 Legacy Lifecycle

### 優點

* 最大相容性。

### 缺點

* 長期維護成本高。
* API 持續重複。
* 增加 Framework 複雜度。

**不採用。**

---

## 方案二：Deprecated，但永久保留

### 優點

* 降低短期 Migration 成本。

### 缺點

* 長期仍須維護兩套 API。

**不採用。**

---

## 方案三：完成 Migration 後正式移除（採用）

### 優點

* Framework 僅保留一套 Execution Lifecycle。
* API 更簡潔。
* Architecture 更一致。
* 文件更容易維護。
* 測試更單純。

---

# 影響（Consequences）

## 正面影響

* Framework API 更精簡。
* Generator 擴充點更清楚。
* 文件一致性提升。
* 長期維護成本降低。
* Plugin API 更容易設計。

---

## 負面影響

* 第三方 Generator 需完成 Migration。
* Legacy API 將不再可用。

---

# Implementation Plan

後續實作 PR 預計完成：

1. 移除 Legacy Lifecycle。
2. 簡化 BaseGenerator。
3. 更新 Architecture。
4. 更新 CHANGELOG。
5. 更新 Migration Guide。
6. 執行完整 Repository 驗證。

---

# Testing Requirements

Implementation PR 必須驗證：

* Legacy Removal Contract Tests
* Execution Contract Tests
* BaseGenerator Lifecycle Tests
* Bootstrap Generator Tests
* Course Generator Tests
* Week Generator Tests
* CLI Integration Tests
* Repository 全部測試
* Ruff
* pre-commit
* `git diff --check`

---

# Code Review Checklist

* [ ] Legacy Lifecycle 已完全移除。
* [ ] `run()` 仍為唯一 Execution Entry Point。
* [ ] Execution Lifecycle 順序未改變。
* [ ] Validation 不產生副作用。
* [ ] Planning 不產生副作用。
* [ ] Execution 為唯一允許副作用的階段。
* [ ] Dry Run 行為維持不變。
* [ ] `GenerationResult` 契約未改變。
* [ ] 內建 Generator 行為維持一致。
* [ ] Architecture 已更新。
* [ ] Migration Guide 已更新。
* [ ] CHANGELOG 已更新。
* [ ] Contract Tests 全數通過。
* [ ] Repository 全部測試通過。
* [ ] Ruff 通過。
* [ ] pre-commit 通過。

---

# 參考文件（References）

* ADR 0005：Generator Input Contract
* ADR 0006：Generator Validation Contract
* ADR 0007：Generation Plan Contract
* ADR 0008：Generator Execution Contract
* `generator/generators/base.py`
* `tests/generators/test_base_generator_lifecycle.py`
* `tests/generators/test_generator_execution_contract.py`
* `docs/architecture/generator.md`
