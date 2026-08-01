# OpenProjectLab Documentation Hub

> Status: Active
> Audience: Users, contributors, maintainers, and framework developers
> Scope: Documentation navigation, organization, conventions, and maintenance

歡迎來到 **OpenProjectLab（OPL）** 文件中心。

本文件是整個 Documentation System 的入口，提供文件導覽、閱讀順序、維護原則，以及各類文件的定位。

Documentation 是 OPL Framework 的一部分，而不是附屬品。

---

# Documentation Philosophy

OpenProjectLab 採用以下四項核心工程原則：

* **Design First**
* **Documentation First**
* **Automation First**
* **Testing First**

每一項功能都應同步完成：

* 架構設計（Architecture）
* 使用規格（Reference）
* 程式實作（Implementation）
* 自動化測試（Testing）
* 文件更新（Documentation）

Documentation 並不是專案完成後才補上的工作，而是設計流程的一部分。

---

# Documentation Architecture

整個 Documentation System 分為數個不同層級，每一層都有不同目的。

```text
docs/
│
├── README.md                 ← Documentation Hub
│
├── architecture/
│
├── reference/
│
├── development/
│
├── adr/
│
├── HISTORY.md
├── ROADMAP.md
└── CHANGELOG.md
```

---

# Documentation Layers

## Architecture

回答：

> 為什麼要這樣設計？

內容包括：

* System Architecture
* Framework Design
* Component Responsibilities
* Design Decisions
* Layer Boundaries
* Future Evolution

適合：

* Maintainers
* Contributors
* Framework Developers

---

## Reference

回答：

> 系統提供哪些功能？

內容包括：

* CLI Reference
* Template Reference
* Configuration Reference
* Filesystem Reference
* Error Reference

Reference 文件描述的是：

* Public Contract
* API
* Command
* Configuration
* Schema
* Expected Behaviour

Reference 不討論設計理由。

---

## Development

回答：

> 如何開發與維護？

內容包括：

* Development Workflow
* Coding Standard
* Testing Guide
* Review Checklist
* Release Process

適合：

* Contributors
* Reviewers
* Maintainers

---

## ADR

Architecture Decision Records（ADR）記錄重要設計決策。

每份 ADR 都應說明：

* 問題背景
* 可行方案
* 最終決策
* 決策理由
* 影響分析

ADR 不應被修改歷史，而應記錄當時的決策。

---

## Project Documents

專案治理文件包括：

* HISTORY
* ROADMAP
* CHANGELOG

三者用途不同：

| 文件 | 用途 |
| --------- | ------ |
| CHANGELOG | 每次版本變更 |
| HISTORY | 專案演進歷史 |
| ROADMAP | 未來發展方向 |

---

# Recommended Reading Order

第一次接觸 OpenProjectLab，建議依照以下順序閱讀：

```text
Repository README
        │
        ▼
Documentation Hub
        │
        ▼
Architecture Overview
        │
        ▼
Filesystem Architecture
        │
        ▼
Template Architecture
        │
        ▼
Reference Documents
        │
        ▼
Development Guides
```

不同角色可依需求閱讀不同文件。

---

# Documentation Matrix

| 我想知道...       | 建議閱讀                    |
| ------------- | ----------------------- |
| 專案目標          | Repository README       |
| 系統設計          | architecture/           |
| CLI 用法        | reference/cli.md        |
| Template 使用方式 | reference/template.md   |
| Filesystem 規格 | reference/filesystem.md |
| 開發流程          | development/            |
| 設計決策          | adr/                    |
| 專案演進          | HISTORY.md              |
| 未來規劃          | ROADMAP.md              |
| 每版修改          | CHANGELOG.md            |

---

# Documentation Principles

所有文件應遵循以下原則。

## Single Responsibility

每份文件應只有一個主要目的。

例如：

* Architecture 不討論 CLI 教學。
* Reference 不討論設計理念。
* Development 不描述 API。

---

## Stable Structure

所有文件應採用一致結構，例如：

1. Purpose
2. Scope
3. Concepts
4. Specification
5. Examples
6. Testing
7. Related Documents

保持一致可降低閱讀成本。

---

## Cross References

避免重複內容。

應透過 Related Documents 建立文件關聯，而不是大量複製內容。

例如：

* Template Reference → Template Architecture
* Errors Reference → Error Handling Architecture
* Filesystem Reference → Filesystem Architecture

---

## Living Documentation

Documentation 應與程式同步演進。

任何 Public Contract 的修改，都應同步更新相關文件。

不得讓程式與文件長期不一致。

---

# Documentation Workflow

新增功能時建議遵循以下流程：

```text
Requirement
      │
      ▼
Architecture Design
      │
      ▼
Reference Specification
      │
      ▼
Implementation
      │
      ▼
Tests
      │
      ▼
Documentation Review
      │
      ▼
Code Review
      │
      ▼
Merge
```

Documentation 與 Implementation 應同步完成。

---

# Documentation Maintenance

以下情況應同步更新 Documentation：

* 新增 Public API
* 修改 CLI 行為
* 修改 Configuration Schema
* 修改 Template Contract
* 新增 Generator
* 修改 Architecture
* 新增 ADR
* 發布新版本

若修改會影響使用者，CHANGELOG 應同步更新。

---

# Documentation Review Checklist

每份文件在合併前建議確認：

## Content

* [ ] 文件目的明確。
* [ ] 範圍清楚。
* [ ] 使用一致術語。
* [ ] 範例正確。
* [ ] 沒有重複內容。

## Structure

* [ ] 標題層級一致。
* [ ] Related Documents 完整。
* [ ] 文件位置正確。
* [ ] 命名一致。

## Quality

* [ ] 與目前程式一致。
* [ ] 與測試一致。
* [ ] 未描述尚未實作功能為既有功能。
* [ ] 已區分 Proposal 與 Current Implementation。

---

# Future Documentation

Documentation 將持續擴充，包括：

* Architecture Overview
* Filesystem Architecture
* Generator Framework
* Configuration Framework
* Template Framework
* Error Handling Architecture
* CLI Reference
* SDK Reference
* Plugin Architecture
* Plugin Reference

Documentation 的演進將與 Framework 一起成長。

---

# Related Documents

## Architecture

* architecture/overview.md
* architecture/filesystem.md
* architecture/template.md

## Reference

* reference/filesystem.md
* reference/template.md
* reference/errors.md

## Development

* development/development-workflow.md
* development/code-review-checklist.md

## Project

* HISTORY.md
* ROADMAP.md
* CHANGELOG.md

---

> **Documentation 是 OpenProjectLab 的正式工程資產。每一項功能都應同時具備設計、文件、測試與實作，才能形成可長期維護的 Framework。**
