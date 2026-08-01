# OpenProjectLab Documentation Writing Style Guide

> Status: Active
> Audience: Maintainers, Contributors, Documentation Authors
> Scope: Common writing standards for all OpenProjectLab documentation

---

# Purpose

本文件定義 OpenProjectLab（OPL）所有文件的共同寫作規範。

無論文件屬於：

* Architecture
* Reference
* Development
* ADR
* README
* Governance

皆應遵循本文件所定義的寫作原則，以建立一致、清晰且易於維護的 Documentation System。

---

# Documentation Principles

所有文件應遵循：

* Clarity First
* Consistency First
* Simplicity First
* Maintainability First

文件的目的在於協助讀者理解，而不是展現作者的寫作風格。

---

# Audience

撰寫文件前，應先確認主要讀者。

常見讀者包括：

* 使用者
* Framework Developer
* Contributor
* Maintainer
* Reviewer
* Future Maintainer

避免同一份文件同時滿足所有讀者，必要時拆分為不同文件。

---

# Writing Style

建議：

* 使用完整句子。
* 使用主動語態。
* 一個段落聚焦一個概念。
* 保持簡潔。
* 避免重複。

例如：

✔

> Generator 建立 Generation Plan。

✘

> Generator 可能會在某些情況下嘗試建立一份 Generation Plan。

---

# Terminology

同一概念應使用固定術語。

例如：

| 建議用語 | 避免混用 |
| --------- | --------------------- |
| Generator | Generator、產生器、模組（混用） |
| Template | 樣板、Template（混用） |
| Manifest | Manifest File、資訊檔（混用） |
| Plugin | Extension、外掛（混用） |

若需定義新術語，應在首次出現時說明。

---

# Document Structure

建議每份文件包含：

```text
Title

Purpose

Scope

Main Content

Examples（如適用）

Related Documents
```

大型文件可增加章節，但整體結構應保持一致。

---

# Headings

使用 Markdown 標題：

```text
# Level 1

## Level 2

### Level 3
```

原則：

* 每份文件僅使用一個 `#` 標題。
* 避免跳過層級，例如直接從 `#` 跳至 `###`。
* 標題應簡潔且具描述性。

---

# Lists

優先使用條列式整理資訊。

適用於：

* Requirements
* Steps
* Features
* Rules
* Checklists

避免將多個概念寫成冗長段落。

---

# Tables

適合用於：

* 比較
* 規格
* 對照
* 支援矩陣

例如：

| Item     | Description            |
| -------- | ---------------------- |
| CLI      | Command Line Interface |
| Template | Project Template       |

避免過度複雜的表格。

---

# Code Blocks

所有程式碼均應使用 Markdown Code Fence。

應標示語言，例如：

````text
```python
```

```yaml
```

```powershell
```
````

若只是顯示指令，可使用：

```powershell
python -m pytest
```

---

# Diagrams

建議使用 Mermaid。

例如：

```text
Project
    ↓
Generator
    ↓
Template
    ↓
Filesystem
```

圖表應：

* 保持簡潔。
* 聚焦單一概念。
* 與文字互補。

避免過於龐大的流程圖。

---

# Examples

若文件描述操作或規格，應提供實際範例。

例如：

YAML：

```yaml
paths:
  template_root: templates
```

CLI：

```powershell
opl list
```

Python：

```python
config = ProjectConfig.load(path)
```

範例應保持與目前版本一致。

---

# Notes and Warnings

可使用固定格式提醒讀者。

例如：

**Note**

補充說明。

**Warning**

重要限制或風險。

避免大量使用警告，降低閱讀效果。

---

# Cross References

不要複製大量內容。

應透過 Related Documents 建立文件關聯。

例如：

## Related Architecture

* `docs/architecture/template.md`

## Related Reference

* `docs/reference/template.md`

## Related Development

* `docs/development/testing.md`

---

# File Naming

所有文件使用：

* 小寫
* kebab-case
* `.md`

例如：

```text
filesystem.md
template.md
writing-style.md
development-workflow.md
```

避免：

```text
Template Guide.md
Filesystem_v2.md
README-final.md
```

---

# Language Guidelines

建議：

* 使用一致語言。
* 避免口語化。
* 避免模糊描述。

例如：

✔

> 系統必須驗證設定檔。

✘

> 系統通常會驗證設定檔。

使用：

* 「必須（Must）」
* 「應（Should）」
* 「可以（May）」

表示不同層級的要求。

---

# Version Awareness

若文件涉及版本資訊，應明確標示。

例如：

```text
Supported since v0.3.0
```

或：

```text
Experimental
```

避免讓讀者誤認所有功能皆已正式支援。

---

# Review Checklist

完成文件後建議確認：

## Content

* [ ] Purpose 清楚。
* [ ] Scope 明確。
* [ ] 術語一致。
* [ ] 範例正確。

## Formatting

* [ ] Markdown 格式一致。
* [ ] Heading 正確。
* [ ] Code Block 已標示語言。
* [ ] 表格易於閱讀。

## Quality

* [ ] 無重複內容。
* [ ] 無拼字錯誤。
* [ ] Related Documents 已更新。
* [ ] 與目前版本一致。

---

# Relationship with Other Documentation

| 文件類型 | 主要回答的問題 |
| ------------- | ---------- |
| Architecture | 為什麼這樣設計？ |
| Reference | 提供哪些功能與規格？ |
| Development | 如何開發與維護？ |
| ADR | 為何做出設計決策？ |
| Writing Style | 如何撰寫一致的文件？ |

Writing Style 為所有文件提供共同的語言與格式標準。

---

# Definition of Done

一份文件完成時應符合：

* 結構符合文件類型。
* 用語一致。
* Markdown 格式正確。
* 範例可用。
* Related Documents 已更新。
* 經過文件審查。

---

# Future Evolution

未來可逐步加入：

* Markdown Lint Rules
* Mermaid Style Guide
* Terminology Glossary
* Inclusive Language Guidelines
* Internationalization Guidelines
* Documentation Automation Rules

---

> **良好的文件風格不是追求華麗，而是讓任何讀者都能快速找到資訊、正確理解內容，並在專案演進過程中持續維持一致性。**
