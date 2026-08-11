# OpenProjectLab Roadmap

> Status: Active
> Last Updated: 2026-08-11

---

# Vision

OpenProjectLab（OPL）的目標不是建立一個單純的 Project Generator，而是打造一個以 **Design First、Documentation First、Automation First、Testing First** 為核心的 **Project Engineering Platform**。

---

# Current Status

已完成 Milestone 3 Generator Core Framework，以及 Milestone 4 的主要 Plugin runtime foundation。

目前 Milestone 4 已完成：

* Plugin SDK Contract Inventory
* ADR 0010 — Plugin SDK Public Contract
* Public `generator.sdk` façade 與 contract tests
* Plugin discovery / registry / loader
* ADR 0011 — Plugin Validation Contract
* Plugin validation implementation
* validate-all-before-register integration
* Registry membership preflight
* ADR 0012 — Plugin Entry Point Contract
* canonical `openprojectlab.generators` Entry Point discovery
* Entry Point metadata/runtime identity validation
* transactional Entry Point batch loading
* legacy `generator.core.plugin.PluginManager` removal
* Plugin runtime architecture tests

目前焦點：

> **Milestone 4 — Plugin Authoring & Ecosystem Alignment**

---

# Milestone 1 — Foundation ✅

**Status:** Completed

---

# Milestone 2 — Framework Foundation ✅

**Status:** Completed

---

# Milestone 2.5 — Documentation Standardization ✅

**Status:** Completed

---

# Milestone 3 — Core Framework ✅

完成：

* `GenerateRequest` / `RuntimeOptions`
* `GeneratorValidationError`
* `GenerationOperation` / `GenerationPlan`
* `GenerationResult`
* canonical `BaseGenerator.run()`
* `validate_request → plan → execute`
* legacy Generator lifecycle removal
* cross-generator contract tests
* architecture / reference / ADR alignment

**Status:** Completed

---

# Milestone 4 — Plugin Ecosystem 🚧

目標：

任何人都能透過穩定 SDK 開發自己的 OPL Plugin，而不需要修改核心 Framework。

## Completed Foundation

### Public SDK

* stable `generator.sdk` dependency boundary
* Public SDK export tests
* third-party-style Generator contract tests

### Validation

* centralized Plugin Generator validator
* concrete `BaseGenerator` subclass requirement
* naming contract
* zero-argument construction contract
* `PluginError` boundary

### Entry Point Runtime

* `openprojectlab.generators` canonical group
* one Entry Point → one Generator class
* Entry Point name == Generator name
* transactional load / validate / preflight / register
* no-partial-registration guarantee
* existing Registry preservation on failure

### Legacy Cleanup

* legacy `generator.core.plugin.PluginManager` removed
* legacy `PluginDescriptor` removed
* architecture tests prevent reintroduction

## Current Focus

### Plugin Authoring

* `docs/plugin-authoring.md`
* packaging example
* SDK-only authoring examples
* third-party Plugin testing guidance

## Remaining Planned Features

* Example third-party Plugin distribution
* Plugin metadata model
* Version compatibility policy / metadata
* Plugin compatibility diagnostics
* Plugin isolation strategy
* Public reference documentation refinement

**Status:** In Progress

---

# Milestone 5 — Open Courseware Platform

## Planned Features

* Course Templates
* Week Templates
* Lab Generator
* Quiz Generator
* Assignment Generator
* PPT Generator
* Website Generator

---

# Milestone 6 — AI Integration

## Planned Features

* AI-assisted Content Generation
* AI Review
* AI Documentation
* AI Template Completion
* AI Course Builder
* AI Refactoring Assistant

---

# Milestone 7 — Marketplace

## Planned Features

* Template Packages
* Plugin Marketplace
* Community Repository
* Shared Generators
* Versioned Templates

---

# Version Targets

| Version | Target |
| --- | --- |
| v0.2.x | Foundation |
| v0.3.x | Documentation + Core Framework |
| v0.4.x | Plugin Framework |
| v0.5.x | Open Courseware |
| v0.6.x | AI Integration |
| v0.7.x | Marketplace |
| v1.0.0 | Stable Release |

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

> **Build projects with engineering discipline, not just code generation.**
