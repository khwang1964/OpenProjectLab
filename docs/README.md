# OpenProjectLab Documentation

歡迎來到 **OpenProjectLab（OPL）文件中心**。

OpenProjectLab 是一套以軟體工程方法為核心的 **Project Engineering Platform**，協助開發者建立、測試、維護並持續演進具備良好工程品質的專案。

本文件中心記錄 OPL 的：

* 系統架構
* 核心框架
* 開發流程
* CLI 與設定參考
* 架構決策
* 專案歷史與發展方向

> **程式碼說明系統如何運作；文件說明系統為什麼這樣設計。**

---

## 文件導覽

### 🚀 Getting Started

第一次接觸 OpenProjectLab，建議先閱讀：

1. [專案首頁](../README.md)
2. [CLI Reference](reference/cli.md)
3. [Configuration Reference](reference/configuration.md)
4. [Development Workflow](development/development-workflow.md)

這些文件將協助您理解 OPL 的基本定位、命令列工具、設定方式與開發流程。

---

## 🏗 Architecture

Architecture 文件說明 OpenProjectLab 的設計理念、責任邊界與元件互動方式。

| 文件 | 說明 |
| ------------------------------------------------------------------ | ----------------------- |
| [Architecture Overview](architecture/overview.md) | 系統整體架構與核心元件 |
| [Generator Framework](architecture/generator-framework.md) | Generator 的責任、生命週期與擴充方式 |
| [Configuration Framework](architecture/configuration-framework.md) | 設定載入、驗證與路徑管理 |
| [Template Framework](architecture/template-framework.md) | Template 的組織、渲染與輸出流程 |
| [Generator Registry](architecture/registry.md) | Generator 註冊、查詢與解析 |
| [SDK](architecture/sdk.md) | Generator 與擴充功能開發介面 |

Architecture 文件主要回答：

* 為什麼系統採用這樣的設計？
* 各元件的責任是什麼？
* 元件之間如何合作？
* 未來功能應如何擴充？

---

## 🧭 Development Guide

Development Guide 定義所有貢獻者共同遵循的工程流程。

| 文件 | 說明 |
| ------------------------------------------------------------- | -------------------------- |
| [Development Workflow](development/development-workflow.md) | 從需求到 Merge 的完整流程 |
| [Coding Style](development/coding-style.md) | Python 與專案程式風格 |
| [Testing Guide](development/testing.md) | 測試分類、執行方式與品質要求 |
| [Code Review Checklist](development/code-review-checklist.md) | Pull Request 與 Review 檢查項目 |
| [Branching Strategy](development/branching-strategy.md) | 分支命名與合併策略 |
| [Release Process](development/release-process.md) | 版本發布與變更管理流程 |

所有重要功能都應同步提供：

1. Architecture
2. Documentation
3. Implementation
4. Tests
5. Automation
6. Code Review Checklist

---

## 📖 Reference

Reference 文件提供實際操作與格式查詢。

| 文件 | 說明 |
| ----------------------------------------------------- | ------------------- |
| [CLI Reference](reference/cli.md) | `opl` 命令、子命令與參數 |
| [Configuration Reference](reference/configuration.md) | YAML 設定結構與欄位 |
| [Template Reference](reference/template.md) | Template 目錄、格式與使用方式 |
| [API Reference](reference/api.md) | Python API 與公開介面 |

Reference 著重於：

* 可用命令
* 設定格式
* 欄位定義
* 輸入與輸出
* 錯誤行為
* 使用範例

---

## 📝 Architecture Decision Records

OpenProjectLab 使用 **Architecture Decision Record（ADR）** 記錄重要設計決策。

| 文件 | 說明 |
| -------------------------------------------------------------- | ------------ |
| [ADR Index](adr/README.md) | ADR 編號、狀態與導覽 |
| [ADR-0001: Project Philosophy](adr/0001-project-philosophy.md) | OPL 核心工程原則 |

每份 ADR 應包含：

* Context
* Decision
* Alternatives
* Consequences
* Status

ADR 的目的不是描述程式碼，而是保留：

> 為什麼我們當時做出這個決定？

---

## 🛣 Project Governance

下列文件記錄 OpenProjectLab 的演進與治理方式。

| 文件 | 說明 |
| ---------------------------------------- | ---------- |
| [Roadmap](roadmap.md) | 未來版本與里程碑 |
| [History](HISTORY.md) | 專案演進歷史 |
| [Changelog](../CHANGELOG.md) | 各版本功能與修正紀錄 |
| [Contributing](../CONTRIBUTING.md) | 貢獻方式與基本規則 |
| [Code of Conduct](../CODE_OF_CONDUCT.md) | 社群協作與行為準則 |
| [Security Policy](../SECURITY.md) | 安全性問題回報流程 |

---

## 文件分類原則

OPL 文件依用途分成四個層次。

### 1. Landing Page

代表文件：

```text
README.md
```

用途：

* 專案定位
* 核心能力
* 快速開始
* 文件入口

README 不應承載過多實作細節。

### 2. Architecture

代表目錄：

```text
docs/architecture/
```

用途：

* 系統設計
* 元件責任
* 資料與控制流程
* 設計取捨
* 擴充原則

### 3. Development Guide

代表目錄：

```text
docs/development/
```

用途：

* 開發流程
* 測試策略
* 分支策略
* Code Review
* Release Process

### 4. Reference

代表目錄：

```text
docs/reference/
```

用途：

* CLI 命令
* 設定欄位
* Template 格式
* API 使用方式

---

## 文件生命週期

文件必須與程式碼同步演進。

```text
需求
  │
  ▼
架構設計
  │
  ▼
更新文件
  │
  ▼
實作程式
  │
  ▼
新增或更新測試
  │
  ▼
Automation Check
  │
  ▼
Code Review
  │
  ▼
Merge
```

以下變更通常必須同步更新文件：

* 新增 CLI 命令
* 修改設定格式
* 新增 Generator
* 修改 Template 行為
* 新增公開 API
* 修改目錄結構
* 調整開發流程
* 變更相容性或升級規則

---

## 文件品質標準

所有正式文件應符合以下要求：

* 使用清楚且一致的標題層級。
* 每份文件具有明確目的。
* 不重複複製其他文件的大段內容。
* 使用相對路徑連結。
* 所有命令範例應可實際執行。
* 功能狀態應明確區分為已完成、開發中或規劃中。
* 文件名稱與路徑大小寫必須完全一致。
* 使用 UTF-8 編碼。
* 與目前程式碼及 Repository 結構一致。

---

## 文件更新 Checklist

修改文件前，請確認：

* [ ] 文件放置於正確分類。
* [ ] 文件名稱與內容目的相符。
* [ ] 連結使用正確的相對路徑。
* [ ] 沒有引用不存在的命令或功能。
* [ ] 程式碼範例符合目前版本。
* [ ] 文件與 Architecture 決策一致。
* [ ] README 只保留摘要，不重複完整內容。
* [ ] `git diff --check` 通過。
* [ ] `pre-commit run --all-files` 通過。
* [ ] `python -m pytest` 通過。

---

## Documentation Philosophy

OpenProjectLab 遵循四項核心原則：

### Design First

先理解問題、定義責任與設計介面，再開始實作。

### Documentation First

設計文件是開發的一部分，不是功能完成後才補上的附件。

### Automation First

可自動驗證的工作不應長期依賴人工操作。

### Testing First

重要行為必須由測試保護，讓系統可以安全演進。

---

> **好的文件不是程式碼的附錄，而是可持續維護的工程資產。**
