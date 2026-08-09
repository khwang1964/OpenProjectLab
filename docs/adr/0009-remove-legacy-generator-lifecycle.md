# ADR 0009：移除 Legacy Generator Lifecycle

- **狀態（Status）：** Accepted
- **日期（Date）：** 2026-08-06
- **決策者（Deciders）：** OpenProjectLab Architecture Team
- **技術主題（Technical Story）：** 完成 Generator Execution Contract 遷移並移除 Legacy Generator Lifecycle
- **取代（Supersedes）：** 無
- **被取代（Superseded by）：** 無

---

# 背景（Context）

OpenProjectLab 已完成 Generator Framework 的核心架構重整：

- ADR 0005：Generator Input Contract
- ADR 0006：Generator Validation Contract
- ADR 0007：Generation Plan Contract
- ADR 0008：Generator Execution Contract

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

上述流程已由共同契約（Contract）與測試完整保護，包括：

- Generator Validation Contract
- Generation Plan Contract
- Generator Execution Contract

`run()` 已成為 Framework 唯一管理 Generator 執行流程的入口（Canonical Execution Entry Point）。

早期版本保留的 Legacy Generator Lifecycle：

```text
validate(context)
prepare(context)
generate(context)
post_generate(context)
cleanup(context)
```

已完成歷史任務，並造成 Framework 同時存在兩套 Generator Lifecycle，因此決定正式移除。

---

# 問題（Problem Statement）

Legacy Generator Lifecycle 造成下列問題：

## 一、Framework 同時存在兩套生命週期

Framework 同時提供：

- GenerateRequest Lifecycle（Canonical）
- GeneratorContext Lifecycle（Legacy）

容易造成 API 與文件上的混淆。

---

## 二、Generator 擴充點不明確

新的 Generator 作者容易產生疑問：

- 是否仍需實作 `generate()`？
- 是否可以覆寫 `run()`？
- `GeneratorContext` 是否仍屬正式 API？

增加 Framework 的學習成本。

---

## 三、維護成本增加

保留 Legacy Lifecycle 必須同步維護：

- 文件
- Architecture
- Migration Guide
- Code Review Checklist
- Compatibility Layer

但已不再提供實際功能價值。

---

## 四、增加測試負擔

每一個 Legacy API 都需要：

- 相容性測試
- 文件同步
- Review
- Migration 支援

形成長期技術債。

---

# 決策（Decision）

OpenProjectLab 正式採用單一 Generator Execution Lifecycle：

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

Generator 的正式擴充點僅保留：

- `validate_request()`
- `plan()`
- `execute()`

`run()` 仍由 Framework 控制，不建議覆寫。

---

# Legacy Lifecycle 移除結果

本 ADR 所定義之 Legacy Generator Lifecycle 已完成移除。

BaseGenerator 已移除下列 Legacy Hooks：

- `validate(context)`
- `prepare(context)`
- `generate(context)`
- `post_generate(context)`
- `cleanup(context)`

目前 Framework 已不再提供 `GeneratorContext` Lifecycle 作為 Generator Execution API。

Canonical Generator Execution Lifecycle 維持如下：

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

Generator 的正式擴充點僅保留：

- `validate_request()`
- `plan()`
- `execute()`

---

# 相容性分析（Compatibility Analysis）

## 內建 Generator

BootstrapGenerator、CourseGenerator 與 WeekGenerator 已全面採用 Canonical Execution Lifecycle，因此行為保持不變。

## CLI

CLI 已使用：

- GenerateRequest
- GenerationResult

因此不受此次重構影響。

## Contract Tests

既有：

- Validation Contract
- Generation Plan Contract
- Execution Contract

皆維持不變。

新增 Legacy Lifecycle Removal Contract Tests 後，完成整體生命週期保護。

## 第三方 Generator

第三方 Generator 應透過：

- `validate_request()`
- `plan()`
- `execute()`

實作 Generator，而不再依賴 `GeneratorContext` Lifecycle。

---

# Migration Strategy

Migration 已依四個階段完成。

## Phase 1：Architecture

✔ 完成 ADR 0009，定義 Legacy Generator Lifecycle Removal。

---

## Phase 2：Migration Tests

✔ 完成 Legacy Generator Lifecycle Removal Contract Tests。

確認：

- Legacy API 不再參與 Canonical Execution。
- Canonical Lifecycle 維持一致。

---

## Phase 3：Implementation

✔ 完成 BaseGenerator 重構。

包括：

- 移除 Legacy Hooks。
- 簡化 BaseGenerator。
- 移除 SDK 對 `GeneratorContext` 的公開匯出。
- 更新 Generator Architecture。

---

## Phase 4：Cleanup

✔ 完成：

- Architecture 更新。
- CHANGELOG 更新。
- Migration Guide 更新。
- 文件同步。
- Code Review Checklist 驗證。

---

# Alternatives Considered

## 保留 Legacy Lifecycle

優點：

- 最大相容性。

缺點：

- API 重複。
- 維護成本持續增加。

不採用。

---

## Deprecated，但永久保留

優點：

- Migration 成本較低。

缺點：

- 長期仍須維護兩套 API。

不採用。

---

## 完全移除（採用）

優點：

- 單一 Generator Execution Model。
- Framework API 更精簡。
- 文件一致性提升。
- 長期維護成本降低。
- Plugin API 更容易設計。

---

# Consequences

## 正面影響

- Framework API 更精簡。
- Generator Extension Points 更清楚。
- Architecture 更一致。
- Documentation 更容易維護。
- 長期維護成本降低。

## 負面影響

- 第三方 Generator 必須完成 Migration。
- Legacy API 不再提供。

---

# Implementation Result

本 ADR 已完成下列實作：

1. ✔ 移除 Legacy Generator Lifecycle。
2. ✔ 簡化 BaseGenerator。
3. ✔ 更新 Generator SDK Public API。
4. ✔ 更新 Architecture Documentation。
5. ✔ 更新 CHANGELOG。
6. ✔ Repository 驗證完成。

---

# Testing Requirements

Implementation PR 已完成驗證：

- ✔ Legacy Removal Contract Tests
- ✔ Generator Execution Contract Tests
- ✔ BaseGenerator Lifecycle Tests
- ✔ Built-in Generator Lifecycle Contract Tests
  - Bootstrap、Course、Week 均繼承 `BaseGenerator`
  - Built-in Generator 均不覆寫 `run()`
- ✔ Bootstrap Generator Tests
- ✔ Course Generator Tests
- ✔ Week Generator Tests
- ✔ CLI Integration Tests
- ✔ Repository 全部測試
- ✔ Ruff
- ✔ pre-commit
- ✔ `git diff --check`

---

# Code Review Checklist

- [x] Legacy Lifecycle 已完全移除。
- [x] `run()` 為唯一 Execution Entry Point。
- [x] Execution Lifecycle 順序未改變。
- [x] Validation 不產生副作用。
- [x] Planning 不產生副作用。
- [x] Execution 為唯一允許副作用的階段。
- [x] Dry Run 行為維持不變。
- [x] `GenerationResult` 契約未改變。
- [x] 內建 Generator 行為維持一致。
- [x] Architecture 已更新。
- [x] Migration Guide 已更新。
- [x] CHANGELOG 已更新。
- [x] Contract Tests 全數通過。
- [x] Repository 全部測試通過。
- [x] Ruff 通過。
- [x] pre-commit 通過。

---

# Implementation Result Summary

本 ADR 已完成實作，並建立 OpenProjectLab 唯一正式的 Generator Execution Lifecycle。

主要成果包括：

- BaseGenerator 已移除 Legacy Generator Lifecycle。
- `GeneratorContext` 不再作為 Generator Execution API。
- Generator SDK 不再公開 `GeneratorContext`。
- Legacy Lifecycle Removal Contract Tests 已建立並驗證。
- Canonical Execution Lifecycle 維持：

```text
run()
    ↓
validate_request()
    ↓
plan()
    ↓
execute()
    ↓
GenerationResult
```

本次重構未改變 Bootstrap、Course 與 Week Generator 的既有行為，並維持 Validation Contract、Generation Plan Contract 與 Execution Contract 的一致性。

---

# 參考文件（References）

- ADR 0005：Generator Input Contract
- ADR 0006：Generator Validation Contract
- ADR 0007：Generation Plan Contract
- ADR 0008：Generator Execution Contract
- `generator/generators/base.py`
- `tests/generators/test_base_generator_lifecycle.py`
- `tests/generators/test_generator_execution_contract.py`
- `tests/generators/test_legacy_generator_lifecycle_removal.py`
- `tests/generators/test_builtin_generator_lifecycle_contract.py`
- `docs/architecture/generator.md`
