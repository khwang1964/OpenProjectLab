# OpenProjectLab Roadmap

> Status: Active
> Last Updated: 2026-08-06

---

# Vision

OpenProjectLab（OPL）的目標不是建立一個單純的 Project Generator，而是打造一個以 **Design First、Documentation First、Automation First、Testing First** 為核心的 **Project Engineering Platform**。

所有 Roadmap 均以此願景為基礎，逐步提升 Framework 的成熟度、可維護性與可擴充性。

---

# Guiding Principles

所有新功能均應遵循：

* Design First
* Documentation First
* Automation First
* Testing First

每項重要功能完成時，應同步提供：

* Architecture
* Reference
* Tests
* Code Review Checklist
* CHANGELOG（必要時）
* ADR（重大設計變更）

---

# Current Status

目前已完成：

* GitHub Repository Professionalization
* CLI Framework
* Generator Framework（Bootstrap、Course、Week）
* Configuration Framework
* Manifest Framework
* Upgrade Framework
* Repository Governance
* CI / GitHub Actions
* Ruff / pre-commit
* Unit Tests
* Integration Tests
* Documentation Foundation
* Shared `GenerationResult` Contract
* Shared `GenerateRequest` and `RuntimeOptions` Contract
* Structured Generator Validation Contract
* Shared `GenerationOperation` and `GenerationPlan` Contract
* Canonical `BaseGenerator.run()` Execution Lifecycle
* Legacy `GeneratorContext` Lifecycle Removal
* Generator SDK Public Export Cleanup
* Cross-generator Contract Tests

目前正處於：

> **Milestone 4 — Plugin Ecosystem / Plugin SDK（Design First）**

---

# Milestone 1 — Foundation ✅

完成基礎 Framework：

* Project Structure
* CLI
* Configuration
* Registry
* Generator 基礎架構
* Testing Infrastructure
* Repository Structure

**Status:** Completed

---

# Milestone 2 — Framework Foundation ✅

建立核心工程能力：

* Upgrade Framework
* Manifest
* Repository Audit
* GitHub Professionalization
* CI
* Governance Documents
* Testing
* Architecture Documents

**Status:** Completed

---

# Milestone 2.5 — Documentation Standardization ✅

建立完整 Documentation Architecture。

## Goals

建立一致且可長期維護的 Documentation System。

## Planned Deliverables

### Documentation Hub

* docs/documentation/README.md

### Documentation Standards

* architecture-style.md
* reference-style.md
* development-style.md
* writing-style.md
* document-layout.md

### Architecture Documents

* Architecture Overview
* Filesystem
* Template
* Error Handling
* Generator Framework
* Configuration Framework

### Reference Documents

* CLI
* Configuration
* Template
* Filesystem
* Errors

### Development Documents

* Development Workflow
* Coding Standard
* Testing Guide
* Code Review Checklist

**Target Outcome**

Documentation 成為 Framework 的正式組成，而非附屬產物。

**Status:** Completed

---

# Milestone 3 — Core Framework ✅

建立真正可重用且由契約保護的 Framework Core。

## Completed Features

### Shared Generator Contracts

* `GenerateRequest` 與 `RuntimeOptions` 共用輸入契約
* `GeneratorValidationError` 結構化驗證契約
* `GenerationOperation` 與 `GenerationPlan` 共用規劃契約
* `GenerationResult` 共用輸出契約

### Canonical Execution Lifecycle

* `BaseGenerator.run()` 作為 Framework 控制的唯一執行入口
* 固定生命週期：`validate_request → plan → execute → GenerationResult`
* Validation 與 Planning 維持 Zero Side Effects
* Dry Run 使用相同 Plan 且不修改 Persistent State
* Execution Failure 保留一致的 Exception Propagation

### Legacy Lifecycle Removal

* 移除 `BaseGenerator` 的 Legacy `GeneratorContext` hooks：
  * `validate(context)`
  * `prepare(context)`
  * `generate(context)`
  * `post_generate(context)`
  * `cleanup(context)`
* Generator SDK 停止公開 `GeneratorContext`
* Legacy Lifecycle Removal Contract Tests 完成
* Bootstrap、Course、Week Generator 行為維持一致

### Quality and Documentation

* ADR 0005～0009 完成 Generator Contract 演進紀錄
* Generator Architecture 與 CHANGELOG 同步
* Cross-generator Contract Tests 完成
* Ruff、pytest、Coverage、pre-commit 與 GitHub Actions 通過

## Completion Result

Milestone 3 已完成以下完整閉環：

```text
Design
  ↓
Documentation
  ↓
Contract Tests
  ↓
Implementation
  ↓
Code Review
  ↓
CI and Merge
```

**Status:** Completed

---

# Milestone 4 — Plugin Ecosystem 🚧

建立穩定、可版本化且不依賴核心私有模組的 Plugin Architecture。

## Current Focus

* Plugin SDK Architecture ADR
* Public Generator SDK Boundary
* Plugin Compatibility Contract
* Plugin Discovery and Registration

## Planned Features

* Plugin API
* Plugin Registry
* Plugin Discovery
* Plugin Metadata
* Version Compatibility
* Plugin Isolation

目標：

任何人都能透過穩定 SDK 開發自己的 OPL Plugin，而不需要修改核心 Framework。

**Status:** In Progress

---

# Milestone 5 — Open Courseware Platform

擴充為教材產生平台。

## Planned Features

* Course Templates
* Week Templates
* Lab Generator
* Quiz Generator
* Assignment Generator
* PPT Generator
* Website Generator

支援完整 Open Courseware Workflow。

---

# Milestone 6 — AI Integration

整合 AI Workflow。

## Planned Features

* AI-assisted Content Generation
* AI Review
* AI Documentation
* AI Template Completion
* AI Course Builder
* AI Refactoring Assistant

---

# Milestone 7 — Marketplace

建立可分享的生態系。

## Planned Features

* Template Packages
* Plugin Marketplace
* Community Repository
* Shared Generators
* Versioned Templates

---

# Version Targets

| Version | Target                         |
| ------- | ------------------------------ |
| v0.2.x  | Foundation                     |
| v0.3.x  | Documentation + Core Framework |
| v0.4.x  | Plugin Framework               |
| v0.5.x  | Open Courseware                |
| v0.6.x  | AI Integration                 |
| v0.7.x  | Marketplace                    |
| v1.0.0  | Stable Release                 |

---

# Definition of Done

每個 Milestone 完成時應符合：

* Architecture 完成
* Reference 完成
* Tests 通過
* Documentation 更新
* CI 通過
* pre-commit 通過
* CHANGELOG 更新
* 必要時新增 ADR

---

# Long-Term Vision

OpenProjectLab 最終目標是成為一個可持續演進的 **Project Engineering Platform**，協助開發者建立高品質、可維護、可擴充且具有完整工程治理能力的專案，而不只是產生程式碼。

---

> **Build projects with engineering discipline, not just code generation.**
