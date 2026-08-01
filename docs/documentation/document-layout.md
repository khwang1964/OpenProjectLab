# OpenProjectLab Documentation Layout Guide

> Status: Active
> Audience: Maintainers, Contributors, Documentation Authors
> Scope: Documentation directory structure and organization rules

---

# Purpose

本文件定義 OpenProjectLab（OPL）文件系統的目錄結構、分類方式與放置原則。

其目標是建立一致、可擴充且易於維護的 Documentation Information Architecture（IA），讓所有文件都能依據內容性質放置於正確位置，而非依個人習慣建立目錄。

本文件主要回答：

> **一份文件應該放在哪裡？**

---

# Documentation Philosophy

OPL Documentation 採用分層式資訊架構，而非依時間或作者分類。

主要原則如下：

* Single Responsibility
* Logical Organization
* Stable Structure
* Easy Navigation
* Minimal Duplication

每份文件應有單一主要目的（Single Source of Truth）。

---

# Top-Level Layout

建議的 `docs/` 目錄如下：

```text
docs/
│
├── README.md
│
├── architecture/
├── reference/
├── development/
├── documentation/
├── adr/
│
├── HISTORY.md
├── ROADMAP.md
├── CHANGELOG.md
│
└── assets/
```

其中：

* `README.md`：Documentation Hub
* `architecture/`：設計文件
* `reference/`：技術規格
* `development/`：開發流程
* `documentation/`：文件治理與寫作規範
* `adr/`：Architecture Decision Records
* `assets/`：圖片、流程圖與其他共用資源

---

# Directory Responsibilities

## architecture/

說明：

* 系統設計
* 元件架構
* Layer 設計
* Framework Architecture

例如：

```text
architecture/
    overview.md
    filesystem.md
    template.md
    configuration.md
    generator.md
    plugin.md
```

Architecture 不描述操作方式。

---

## reference/

提供正式技術規格。

例如：

```text
reference/
    cli.md
    configuration.md
    template.md
    filesystem.md
    manifest.md
    errors.md
```

Reference 不討論設計理念。

---

## development/

提供開發與維護流程。

例如：

```text
development/
    workflow.md
    coding-standard.md
    testing.md
    release.md
    contribution.md
    code-review.md
```

Development 聚焦工程實務。

---

## documentation/

Documentation Governance。

例如：

```text
documentation/
    README.md
    architecture-style.md
    reference-style.md
    development-style.md
    writing-style.md
    document-layout.md
```

此目錄不放功能文件，而是放置文件標準。

---

## adr/

Architecture Decision Records。

例如：

```text
adr/
    ADR-0001-project-layout.md
    ADR-0002-template-engine.md
```

ADR 記錄重大設計決策，不作為設計文件的替代品。

---

## assets/

共用資源。

例如：

```text
assets/
    diagrams/
    images/
    logos/
```

建議依資源類型再細分子目錄。

---

# Root Documents

部分文件應固定放置於 `docs/` 根目錄。

| 文件           | 目的                |
| ------------ | ----------------- |
| README.md    | Documentation Hub |
| ROADMAP.md   | 未來規劃              |
| HISTORY.md   | 專案歷史              |
| CHANGELOG.md | 版本變更              |

避免將治理文件散落於其他子目錄。

---

# File Placement Rules

新增文件時，應先判斷其主要目的。

| 問題 | 放置位置 |
| -------- | -------------- |
| 為什麼這樣設計？ | architecture/ |
| 提供哪些功能？ | reference/ |
| 如何開發？ | development/ |
| 如何撰寫文件？ | documentation/ |
| 為何做出此決策？ | adr/ |

若同時涉及多種內容，應拆分為多份文件，而非合併於同一份。

---

# Naming Convention

所有檔名應：

* 使用小寫
* 使用 kebab-case
* 使用 `.md`

例如：

```text
generator.md
coding-standard.md
document-layout.md
```

避免：

```text
Generator Guide.md
CodingStandard.md
Document Layout V2.md
```

---

# Cross References

Documentation 應形成可導航的網路。

建議每份文件最後加入：

```text
Related Architecture

Related Reference

Related Development

Related ADR
```

交叉引用應避免循環與重複。

---

# Directory Growth Strategy

新增子目錄前，應確認：

* 是否已有適合位置。
* 是否具備長期維護價值。
* 是否能容納多份文件。

避免僅為單一文件建立新目錄。

---

# Documentation Lifecycle

文件生命週期建議如下：

```text
Draft
    ↓
Review
    ↓
Approved
    ↓
Published
    ↓
Maintained
    ↓
Archived
```

過時文件應標示或移至適當位置，不應直接刪除。

---

# Documentation Governance

新增文件時，建議遵循：

1. 確認文件類型。
2. 選擇正確目錄。
3. 遵循對應 Style Guide。
4. 建立 Related Documents。
5. 更新 `docs/README.md`（如有必要）。

Documentation 的資訊架構應與專案架構同步演進。

---

# Review Checklist

## Placement

* [ ] 放置於正確目錄。
* [ ] 未與現有文件重複。
* [ ] 命名符合規範。

## Structure

* [ ] 文件類型正確。
* [ ] 已遵循對應 Style Guide。
* [ ] Related Documents 已更新。

## Governance

* [ ] Documentation Hub 已更新（如需要）。
* [ ] 新增目錄具合理性。
* [ ] 未破壞整體資訊架構。

---

# Relationship with Other Documentation

| 文件 | 目的 |
| --------------------- | ------------------- |
| architecture-style.md | Architecture 文件寫作規範 |
| reference-style.md | Reference 文件寫作規範 |
| development-style.md | Development 文件寫作規範 |
| writing-style.md | 共通寫作規範 |
| document-layout.md | 文件目錄與資訊架構規範 |

本文件負責定義「放哪裡」，其他 Style Guide 則定義「怎麼寫」。

---

# Definition of Done

Documentation Layout 完成時應符合：

* 目錄結構清楚。
* 文件分類一致。
* 放置原則明確。
* 命名規範一致。
* Cross References 可維護。
* Governance 流程完整。

---

# Future Evolution

未來可逐步加入：

* Documentation Versioning Strategy
* Multi-language Documentation Layout
* Generated Documentation Directory
* API Documentation Integration
* Search and Index Guidelines
* Documentation Quality Metrics

---

> **良好的文件架構應該讓貢獻者在新增文件前就知道它應該放在哪裡，讓讀者在閱讀時也能自然找到相關內容。Documentation Layout 是整個 Documentation System 的資訊架構基礎。**
