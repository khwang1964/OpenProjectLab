# OpenProjectLab Roadmap

> Status: Active
> Last Updated: 2026-08-04

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

目前正處於：

> **Milestone 3 — Core Framework / Generation Plan Contract（Design First）**

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

# Milestone 3 — Core Framework 🚧

建立真正可重用的 Framework Core。

## Planned Features

### Template Engine

* Template Resolver
* Template Renderer
* Template Validation
* Include
* Filters

### Filesystem Framework

* Path Validation
* Write Policy
* Atomic Write
* Dry Run
* File Ownership

### Error Framework

* Exception Hierarchy
* Exit Codes
* Structured Errors

### Generator Pipeline

* Generation Plan
* Validation
* Pipeline Execution

## Current Progress

* `GenerationResult` 共用輸出契約：Completed
* `GenerateRequest`／`RuntimeOptions` 共用輸入契約：Completed
* `GeneratorValidationError` 結構化驗證契約：Completed
* Generation Plan provenance 與 usage audit：Completed
* ADR 0007 Generation Plan Contract：Proposed
* Generator Architecture 與 ADR 索引同步：In Progress
* Bootstrap Generation Plan 垂直切片：Planned（ADR 接受後開始）
* Course／Week Generation Plan 遷移：Planned
* SDK plan API、CLI preview 與 dry-run lifecycle：Planned

## Design Gate

在 ADR 0007 完成審查並標示為 `Accepted` 前，不進行 Generation Plan 的
production code、Generator、SDK 或 CLI 整合。

**Status:** In Progress

---

# Milestone 4 — Plugin Ecosystem

建立 Plugin Architecture。

## Planned Features

* Plugin API
* Plugin Registry
* Plugin Discovery
* Plugin Metadata
* Version Compatibility
* Plugin Isolation

目標：

任何人都能開發自己的 OPL Plugin。

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
