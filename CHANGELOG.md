# 變更紀錄（CHANGELOG）

本文件記錄 **OpenProjectLab（OPL）** 各版本的重要變更。

本專案參考 **Keep a Changelog** 的精神維護版本變更紀錄，並規劃採用 **Semantic Versioning（SemVer）** 作為正式版本編號規範。

---

# 尚未發佈（Unreleased）

## 新增（Added）

* 建立 Repository Governance 文件：

  * `CONTRIBUTING.md`
  * `SECURITY.md`
  * `CODE_OF_CONDUCT.md`
* 新增 Repository Audit 機制。
* 新增 Repository Structure 測試。
* 新增 Ruff Policy 文件。
* 新增 Template Workflow 測試流程。

## 變更（Changed）

* 強化 GitHub Actions Workflow。
* 改善 Template Test Workflow。
* 統一 Repository 品質檢查流程。
* 更新專案治理文件。

## 重構（Refactored）

* `generator.core.upgrade` 採用 `StrEnum` 改善列舉型別設計。
* 調整 CLI 與測試程式碼以符合 Ruff 建議。

## 修正（Fixed）

* 修正 pre-commit 執行流程。
* 修正 Ruff 格式檢查問題。
* 修正 Repository Governance 相關文件。

---

# v0.2.0

> OpenProjectLab 第一個正式里程碑版本。

## 專案目標

建立 OpenProjectLab 的核心框架，作為可持續發展的專案產生器（Project Generator Framework），並建立一致的開發流程、文件架構與測試基礎。

## 新增（Added）

### 核心架構

* 建立 Generator Framework。
* 建立 CLI 架構。
* 建立 Bootstrap Generator。
* 建立 Configuration Framework。
* 建立 Template Framework。

### 文件

* 建立 README。
* 建立 Architecture 文件。
* 建立 Configuration 文件。
* 建立 ADR（Architecture Decision Records）。
* 建立 Development Guide。

### 測試

* 建立 pytest 測試架構。
* 建立 CLI Integration Tests。
* 建立 Template Tests。
* 建立 Coverage 基礎。

### 開發工具

* 導入 Ruff。
* 導入 pre-commit。
* 導入 GitHub Actions。
* 建立 CI Workflow。

---

## 後續演進

v0.2.0 發布後，專案持續朝下列方向演進：

* Repository Professionalization
* Repository Governance
* Documentation First
* Automation First
* Testing First
* Upgrade Framework
* CI/CD 強化
* 品質檢查流程改善

上述內容將於未來正式版本中陸續發布。

---

# 版本命名原則

目前 OpenProjectLab 採用以下版本策略：

* Git Tag 表示正式版本。
* `main` 為主要開發分支。
* 功能完成並驗證後建立正式版本。
* 未正式發布的內容統一記錄於 **Unreleased**。

未來將依 Semantic Versioning 規範使用：

* Major：重大架構調整或不相容變更。
* Minor：新增功能且保持相容。
* Patch：錯誤修正與維護更新。

---

# 相關文件

完整的專案演進、設計背景與發展歷程，請參閱：

* `docs/HISTORY.md`
* `docs/ROADMAP.md`
* `README.md`
* `CONTRIBUTING.md`
* `SECURITY.md`
* `CODE_OF_CONDUCT.md`
