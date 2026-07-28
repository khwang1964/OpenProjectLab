# OpenProjectLab Development Documentation Style Guide

> Status: Active
> Audience: Maintainers, Contributors, Framework Developers
> Scope: Standards for writing and reviewing Development documentation

---

# Purpose

本文件定義 OpenProjectLab（OPL）所有 **Development 文件** 的撰寫規範。

Development Documentation 用於說明專案的開發、維護、測試與協作流程，確保所有參與者遵循一致的工程實務。

Development 文件主要回答：

> **如何開發、測試、維護與交付？**

而不是：

* 為什麼如此設計（Architecture）
* 系統提供哪些功能（Reference）
* 設計決策的背景（ADR）

---

# Development Principles

所有 Development 文件應遵循：

* Design First
* Documentation First
* Automation First
* Testing First

任何新的功能或流程，都應先完成設計與文件，再進行實作。

---

# Goals

Development 文件應：

* 定義開發流程。
* 建立一致的工程規範。
* 降低新成員的學習成本。
* 支援 Code Review。
* 支援 CI/CD。
* 提高專案可維護性。

---

# Non-Goals

Development 文件不應：

* 重複 Architecture 內容。
* 描述 Public API。
* 成為使用者操作手冊。
* 討論設計理念。
* 收錄大量程式碼實作。

---

# Scope

Development Documentation 包含但不限於：

* Development Workflow
* Coding Standard
* Testing Guide
* Contribution Guide
* Release Process
* Branch Strategy
* Git Workflow
* CI/CD Guide
* Code Review Checklist

---

# Standard Document Structure

建議所有 Development 文件採用以下章節：

```text
1. Purpose
2. Scope
3. Prerequisites
4. Workflow
5. Standards
6. Best Practices
7. Common Pitfalls
8. Automation
9. Verification
10. Related Documents
```

可依文件主題調整，但應維持整體一致性。

---

# Workflow

每份 Development 文件都應清楚描述工作流程。

建議使用流程圖或條列方式，例如：

```text
Requirement
    ↓
Design
    ↓
Documentation
    ↓
Implementation
    ↓
Tests
    ↓
Review
    ↓
CI
    ↓
Merge
```

若流程存在例外情況，應一併說明。

---

# Standards

Development 文件應定義：

* 命名規範
* 程式碼風格
* 文件格式
* Commit Message 規範
* Branch 命名
* Pull Request 要求

所有規範應具體且可執行，避免模糊描述。

---

# Best Practices

每份文件應整理推薦做法，例如：

* 小步驟提交（Small Commits）
* 保持文件與程式同步更新
* 優先撰寫測試
* 定期重構
* 優先使用自動化工具

Best Practices 應提供具體建議，而非抽象口號。

---

# Common Pitfalls

建議列出常見錯誤，例如：

* 未更新文件。
* 測試未涵蓋新功能。
* Commit 過於龐大。
* Branch 長期未同步。
* CI 失敗仍嘗試合併。

協助開發者避免重複犯錯。

---

# Automation

Development 文件應說明自動化流程，例如：

* pre-commit
* Ruff
* pytest
* GitHub Actions
* Release Automation

若有人工步驟，也應明確標示。

---

# Verification

每份 Development 文件都應定義如何驗證流程是否成功。

例如：

* 所有測試通過。
* CI 成功。
* pre-commit 無錯誤。
* 文件已更新。
* Code Review 完成。

驗證條件應可重複執行。

---

# Examples

建議提供實際範例，例如：

Commit Message：

```text
feat: add template validation
```

Branch：

```text
feature/template-validation
```

執行測試：

```powershell
python -m pytest
```

執行 pre-commit：

```powershell
pre-commit run --all-files
```

範例應保持與目前專案一致。

---

# Writing Style

Development 文件建議：

* 使用簡潔句子。
* 以步驟式說明為主。
* 優先條列式內容。
* 保持術語一致。
* 明確區分必要步驟與建議步驟。

避免過多背景介紹，使文件聚焦於實務操作。

---

# Cross References

Development 文件應建立相關文件連結。

建議包含：

## Related Architecture

相關設計理念。

## Related Reference

相關介面與規格。

## Related ADR

相關設計決策。

避免複製內容，應透過交叉引用建立完整文件網路。

---

# Review Checklist

## Structure

* [ ] Purpose 清楚。
* [ ] Scope 明確。
* [ ] Workflow 完整。

## Process

* [ ] Standards 已定義。
* [ ] Best Practices 已整理。
* [ ] Common Pitfalls 已列出。
* [ ] Automation 已說明。
* [ ] Verification 可執行。

## Quality

* [ ] 範例正確。
* [ ] 與目前流程一致。
* [ ] 術語一致。
* [ ] Related Documents 完整。

---

# Relationship with Other Documentation

| 文件類型 | 主要回答的問題 |
| ------------ | ----------- |
| Architecture | 為什麼這樣設計？ |
| Reference | 提供哪些功能與規格？ |
| Development | 如何開發、測試與維護？ |
| ADR | 為何做出這項設計決策？ |

Development Documentation 將設計與規格轉化為可執行的工程流程。

---

# Definition of Done

一份 Development 文件完成時應符合：

* Workflow 已定義。
* Standards 已建立。
* Automation 已描述。
* Verification 已定義。
* 範例可直接使用。
* Related Documents 已更新。
* 與目前專案流程一致。

---

# Future Evolution

未來可逐步擴充：

* Pair Programming Guide
* Security Development Lifecycle
* Dependency Management Guide
* Performance Review Guide
* Documentation Maintenance Guide
* Continuous Improvement Process

---

> **Development Documentation 是 OpenProjectLab 的工程實務手冊。它將設計原則與技術規格轉化為一致、可重複且可驗證的開發流程，確保每位貢獻者都能遵循相同的工程標準。**
