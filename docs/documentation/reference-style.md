# OpenProjectLab Reference Documentation Style Guide

> Status: Active
> Audience: Maintainers, Contributors, Framework Developers, API Consumers
> Scope: Standards for writing and reviewing Reference documentation

---

# Purpose

本文件定義 OpenProjectLab（OPL）所有 **Reference 文件** 的撰寫規範。

Reference Documentation 是 Framework 的正式契約（Contract），負責描述公開功能、介面與行為，不討論設計理念或實作細節。

Reference 文件主要回答：

> **系統提供什麼？它如何運作？**

而不是：

* 為什麼如此設計（Architecture）
* 如何開發（Development）
* 如何教學（Tutorial）

---

# Design Principles

所有 Reference 文件應遵循：

* Accuracy First
* Consistency First
* Documentation First
* Testable Contracts

Reference 必須與程式碼及測試保持一致。

若程式與文件不同，以程式碼與測試為準，並立即更新文件。

---

# Goals

Reference 文件應：

* 定義 Public Contract。
* 描述公開 API。
* 說明 CLI 行為。
* 定義設定格式。
* 描述輸入與輸出。
* 說明錯誤行為。
* 提供可直接使用的範例。

---

# Non-Goals

Reference 文件不應：

* 解釋設計原因。
* 討論架構演進。
* 提供 Coding Style。
* 描述開發流程。
* 包含大量背景知識。

這些內容應分別放入：

* Architecture
* Development
* ADR

---

# Scope

Reference 文件適用於：

* CLI
* Configuration
* Template
* Filesystem
* Manifest
* Errors
* Plugin API
* SDK API（未來）

---

# Standard Document Structure

建議所有 Reference 文件使用一致章節：

```text
1. Purpose
2. Scope
3. Concepts
4. Public Contract
5. Parameters
6. Behaviour
7. Return Values / Results
8. Errors
9. Examples
10. Compatibility
11. Related Documents
```

並非所有章節都必須存在，但整體結構應保持一致。

---

# Public Contract

Reference 文件必須清楚定義：

* 公開功能
* 穩定介面
* 可依賴的行為
* 使用限制

Public Contract 一旦公開，即應考慮向後相容性。

---

# Behaviour Specification

每個功能至少應說明：

* 正常情況
* 邊界條件
* 錯誤情況
* 不保證的行為

例如：

```text
Input
↓

Validation
↓

Processing
↓

Output
```

避免使用：

> 「通常會……」

應改為：

> 「系統必須……」

---

# Parameters

所有公開參數應明確說明：

* 名稱
* 型別
* 是否必要
* 預設值
* 合法值
* 限制

例如：

| Parameter     | Type | Required | Description  |
| ------------- | ---- | -------- | ------------ |
| template_root | Path | Yes      | Template 根目錄 |

---

# Return Values

公開介面應描述：

* 回傳型別
* 成功結果
* 失敗結果
* 副作用

例如：

```text
Created
Updated
Skipped
Unchanged
```

若使用 Exception，應說明可能拋出的類型。

---

# Error Documentation

Reference 文件應描述：

* 可能錯誤
* 觸發條件
* 使用者可採取的動作

不要只列出 Exception 名稱。

例如：

| Error                 | Cause        |
| --------------------- | ------------ |
| ConfigurationError    | 設定格式錯誤       |
| TemplateNotFoundError | 找不到 Template |

詳細設計應連結至 Errors Reference。

---

# Examples

每份 Reference 文件都應包含可直接使用的範例。

例如：

CLI：

```powershell
opl list
```

Python：

```python
config = ProjectConfig.load(path)
```

YAML：

```yaml
paths:
  template_root: templates
```

範例應保持可執行或接近可執行。

---

# Compatibility

Reference 應說明：

* 最低支援版本
* 已棄用功能
* 相容性限制
* 未來可能變更

例如：

```text
Supported since v0.3.0
```

若尚未穩定，可標示：

```text
Experimental
```

---

# Naming Convention

Reference 文件使用小寫檔名與 kebab-case。

例如：

```text
cli.md
configuration.md
filesystem.md
template.md
errors.md
manifest.md
```

避免：

```text
CLI Reference Final.md
Filesystem Spec v2.md
```

---

# Writing Style

建議：

* 使用簡潔句子。
* 優先條列式。
* 一個段落一個概念。
* 使用一致術語。
* 避免模糊語句。

應描述：

> 系統提供什麼。

而不是：

> 作者希望未來如何設計。

---

# Current vs Planned

Reference 文件只應將已公開能力視為正式契約。

尚未完成的功能應明確標示：

```text
Planned
Experimental
Proposal
```

不得將未實作功能描述成既有能力。

---

# Cross References

Reference 文件應建立文件關聯。

建議包含：

## Related Architecture

設計理念。

## Related Development

開發流程。

## Related ADR

重大決策。

避免複製相同內容。

---

# Review Checklist

## Accuracy

* [ ] 與程式一致。
* [ ] 與測試一致。
* [ ] 範例正確。

## Structure

* [ ] Purpose 清楚。
* [ ] Public Contract 完整。
* [ ] Behaviour 明確。
* [ ] Errors 已描述。

## Consistency

* [ ] 術語一致。
* [ ] 命名一致。
* [ ] 格式一致。

## Quality

* [ ] 不包含設計討論。
* [ ] 不包含開發流程。
* [ ] Related Documents 完整。

---

# Relationship with Other Documentation

| 文件類型 | 主要回答的問題 |
| ------------ | ---------- |
| Architecture | 為什麼這樣設計？ |
| Reference | 提供哪些功能與規格？ |
| Development | 如何開發與維護？ |
| ADR | 為何做出這項決策？ |

Reference 是 Framework 的正式使用契約。

---

# Definition of Done

一份 Reference 文件完成時應符合：

* Public Contract 已定義。
* Behaviour 已描述。
* Errors 已說明。
* 範例完整。
* Related Documents 已更新。
* 與程式及測試一致。

---

# Future Evolution

未來可加入：

* API Versioning Guidelines
* Schema Documentation Rules
* JSON / YAML Formatting Standards
* SDK Documentation Standards
* Automatic Reference Validation
* Documentation Lint Rules

---

> **Reference Documentation 是 OpenProjectLab 的正式技術契約。它描述系統目前提供的能力，而不是未來可能提供的能力。**
