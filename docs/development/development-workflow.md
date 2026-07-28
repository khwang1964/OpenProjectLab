# OpenProjectLab Development Workflow

> Status: Active
> Audience: Contributors, maintainers, reviewers

本文件定義 OpenProjectLab（OPL）的標準開發流程。

OPL 採用 **Design First、Documentation First、Automation First、Testing First** 的工程方法，目標是在功能演進的同時，維持系統的一致性、可測試性與可維護性。

---

# 核心原則

所有功能開發都應遵循以下四項原則：

## Design First

在開始撰寫程式之前，先回答：

* 要解決什麼問題？
* 為什麼需要這個功能？
* 它屬於哪一個 Framework？
* 是否會影響現有架構？

必要時應更新：

* Architecture 文件
* ADR（Architecture Decision Record）

---

## Documentation First

設計完成後，先更新文件，再開始實作。

需要同步更新的文件可能包括：

* README（若影響使用方式）
* Architecture
* Development Guide
* CLI Reference
* Configuration Reference
* Template Reference
* Changelog

文件與程式碼必須保持同步。

---

## Automation First

所有可以自動驗證的工作，都應交由工具完成。

目前 OPL 使用：

* Ruff（程式碼品質）
* pre-commit（提交前檢查）
* pytest（功能測試）
* pytest-cov（覆蓋率）
* GitHub Actions（持續整合）

不應依賴人工反覆執行相同檢查。

---

## Testing First

每一項重要功能都應有對應測試。

建議至少涵蓋：

* 正常流程
* 錯誤流程
* 邊界條件
* 回歸測試

修正 Bug 時，應先新增可重現問題的測試，再修正程式。

---

# 開發生命週期

所有功能建議遵循以下流程：

```text
Issue
  │
  ▼
Architecture Design
  │
  ▼
Documentation Update
  │
  ▼
Implementation
  │
  ▼
Unit / Integration Tests
  │
  ▼
pre-commit
  │
  ▼
Code Review
  │
  ▼
Merge
```

---

# Pull Request Checklist

送出 PR 前，請確認：

* [ ] 功能目的明確。
* [ ] 已更新相關文件。
* [ ] 已新增或更新測試。
* [ ] `pre-commit run --all-files` 通過。
* [ ] `python -m pytest` 通過。
* [ ] 未引入無關變更。
* [ ] Commit Message 符合專案規範。

完整的 Review 規範請參閱：

* [Code Review Checklist](code-review-checklist.md)

---

# Commit Message Convention

建議使用 Conventional Commits：

```text
feat: add week generator template support
fix: resolve configuration path handling
docs: update architecture overview
test: add registry unit tests
refactor: simplify generator lifecycle
chore: update development workflow
```

每次 Commit 應聚焦單一主題，避免混合多種不相關修改。

---

# Branch Strategy

建議使用下列命名方式：

```text
main
feature/<topic>
fix/<topic>
docs/<topic>
refactor/<topic>
test/<topic>
```

例如：

```text
feature/plugin-loader
docs/readme-v3
fix/config-loader
```

---

# Code Review 原則

Review 不只是檢查程式是否能執行，更應確認：

* 是否符合 Architecture？
* 是否增加不必要耦合？
* 是否破壞既有行為？
* 是否具有足夠測試？
* 是否同步更新文件？

若需要重大架構調整，應先討論設計，再修改程式。

---

# Release Gate

在合併到 `main` 前，至少應完成：

* 文件更新
* 測試通過
* pre-commit 通過
* Code Review 完成
* Changelog 更新（如適用）

---

# 持續改善

Development Workflow 不是固定不變的規範。

隨著 OPL 演進，我們會透過：

* ADR
* Retrospective
* Issue 討論
* Pull Request Review

持續調整流程，使工程品質與開發效率同步提升。

---

> **流程不是限制，而是讓團隊能持續交付高品質軟體的共同語言。**
