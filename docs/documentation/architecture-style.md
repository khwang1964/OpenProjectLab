# OpenProjectLab Architecture Documentation Style Guide

> Status: Active
> Audience: Maintainers, Contributors, Framework Developers
> Scope: Standards for writing and reviewing Architecture documentation

---

# Purpose

本文件定義 OpenProjectLab（OPL）所有 **Architecture 文件** 的撰寫規範。

目標是建立一致、可維護且易於擴充的 Architecture Documentation，讓所有架構文件具有相同的結構、深度與品質。

Architecture 文件主要回答：

> **為什麼這樣設計？**

而不是：

* 如何使用（Reference）
* 如何開發（Development）
* 如何操作（User Guide）

---

# Design Principles

所有 Architecture 文件應遵循：

* Design First
* Documentation First
* Automation First
* Testing First

Architecture 應先於實作完成，並在實作演進時持續同步更新。

---

# Goals

Architecture 文件應：

* 說明設計目標。
* 定義系統邊界。
* 描述元件責任。
* 解釋設計取捨。
* 提供未來演進方向。
* 作為 Code Review 與 Design Review 的依據。

---

# Non-Goals

Architecture 文件不應：

* 成為使用手冊。
* 成為 API Reference。
* 成為 Coding Style。
* 包含大量 Implementation Details。
* 重複 Development Guide 的內容。

---

# Standard Document Structure

所有 Architecture 文件建議採用以下章節順序：

```text
1. Purpose
2. Scope
3. Goals
4. Non-Goals
5. Responsibilities
6. High-Level Architecture
7. Components
8. Dependency Direction
9. Data Flow / Control Flow
10. Extension Points
11. Current Implementation
12. Future Evolution
13. Related Documents
```

可依主題增減章節，但應保持一致性。

---

# Responsibilities

Architecture 文件應清楚定義：

* 本元件負責什麼。
* 本元件不負責什麼。
* 與其他元件的邊界。
* 對外提供的能力。

若責任不清楚，應優先修正文件，而非增加更多實作細節。

---

# Diagrams

每份 Architecture 文件至少應包含一張高層架構圖。

建議優先使用 Mermaid。

可視需要加入：

* Flowchart
* Component Diagram
* Sequence Diagram
* State Diagram

圖表應協助理解系統，而非追求複雜度。

---

# Dependency Direction

Architecture 文件應明確描述依賴方向。

例如：

```text
CLI
  ↓
Application
  ↓
Framework
  ↓
Infrastructure
```

不得產生循環依賴。

若存在例外情況，應說明原因。

---

# Code Examples

Architecture 文件中的程式碼應以概念為主。

適合：

* Interface
* Protocol
* Dataclass
* API Skeleton
* Pseudocode

避免：

* 大量商業邏輯。
* 完整函式實作。
* 與正式程式碼重複。

若需要完整 API，應放在 Reference 文件。

---

# Proposal vs Current Implementation

Architecture 文件必須區分：

## Current Implementation

目前程式碼已實作且經測試驗證的能力。

## Proposal

尚未完成但已確認方向的設計。

## Future Evolution

可能的未來發展，不代表已決定實作。

避免將提案描述成既有功能。

---

# Naming Convention

Architecture 文件使用小寫檔名與 kebab-case。

例如：

```text
filesystem.md
template.md
generator.md
configuration.md
plugin.md
error-handling.md
```

避免：

```text
Filesystem Design V2.md
Generator Notes.md
Architecture_Final.md
```

---

# Writing Style

建議採用：

* 簡潔句子。
* 一個段落只討論一個概念。
* 使用一致術語。
* 優先使用條列式說明。
* 避免含糊描述。

例如：

* 「Generator 負責建立 Generation Plan。」
* 「Filesystem Layer 不直接決定 Template。」

---

# Cross References

每份 Architecture 文件應包含 Related Documents。

建議分類：

## Related Architecture

同層 Architecture 文件。

## Related Reference

對應的 Reference 規格。

## Related Development

實作與維護流程。

## ADR

相關設計決策。

避免在不同文件中大量複製內容。

---

# Review Checklist

Architecture 文件完成後建議確認：

## Purpose

* [ ] 文件目的清楚。
* [ ] 適用範圍明確。

## Design

* [ ] Goals 完整。
* [ ] Non-Goals 完整。
* [ ] Responsibilities 清楚。
* [ ] Boundary 清楚。
* [ ] Dependency Direction 正確。

## Documentation

* [ ] 圖表完整。
* [ ] 命名一致。
* [ ] Proposal 與 Current 已區分。
* [ ] Related Documents 完整。

## Engineering

* [ ] 與程式實作一致。
* [ ] 與測試一致。
* [ ] 未描述未實作功能為既有功能。
* [ ] 必要時已建立 ADR。

---

# Relationship with Other Documentation

| 文件類型 | 主要回答的問題 |
| ------------ | ----------- |
| Architecture | 為什麼這樣設計？ |
| Reference | 提供哪些介面與規格？ |
| Development | 如何開發與維護？ |
| ADR | 為何做出這項設計決策？ |

Architecture 是整個 Documentation System 的設計基礎。

---

# Definition of Done

一份 Architecture 文件完成時應符合：

* 結構符合本文件規範。
* 設計邊界清楚。
* 依賴方向正確。
* 圖表完整。
* Related Documents 已更新。
* 已完成 Review。
* 與目前程式碼一致。

---

# Future Evolution

本文件將隨著 OPL Framework 演進而持續更新。

未來可加入：

* Diagram Standards
* Architecture Decision Templates
* Layering Guidelines
* Naming Standards
* Review Automation
* Documentation Lint Rules

---

> **Architecture Documentation 是 OPL 的設計契約（Design Contract），其價值在於建立一致的設計語言，而不是描述每一行程式碼。**
