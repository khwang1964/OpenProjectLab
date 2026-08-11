# OpenProjectLab 發展歷程（History）

## 專案起源

OpenProjectLab（OPL）最初的目標，是建立一套能快速產生專案骨架的工具。

隨著專案逐步發展，我們發現真正需要解決的，不只是「建立專案」，而是「如何讓專案能長期維護」。

因此，OPL 的定位逐漸由 Project Generator 演進為 **Project Engineering
Platform**。

------------------------------------------------------------------------

# 發展理念

OPL 的核心理念逐步確立為：

-   Design First
-   Documentation First
-   Automation First
-   Testing First

這四項原則成為所有功能設計與開發流程的基礎。

------------------------------------------------------------------------

# 發展歷程

## Bootstrap Framework

建立第一個可自動產生專案骨架的 Generator。

------------------------------------------------------------------------

## Generator Framework

將不同 Generator 統一納入 Registry 管理，提供一致的擴充架構。

目前包含：

-   Bootstrap Generator
-   Course Generator
-   Week Generator

------------------------------------------------------------------------

## Configuration Framework

建立 YAML 設定管理機制，支援：

-   專案設定
-   路徑設定
-   Generator 設定
-   Plugin 預留設定

------------------------------------------------------------------------

## Template Framework

導入 Jinja2 Template，將模板與程式邏輯分離，提升維護性與重用性。

------------------------------------------------------------------------

## Upgrade Framework

建立專案升級能力，包括：

-   Manifest
-   Preview
-   Backup
-   Rollback
-   SHA-256 驗證
-   Upgrade Report

讓既有專案也能安全演進。

------------------------------------------------------------------------

## 品質工程

逐步導入：

-   Ruff
-   pre-commit
-   pytest
-   Coverage
-   GitHub Actions
-   Repository Audit

形成完整的品質管理流程。

------------------------------------------------------------------------

## Repository Governance

建立：

-   README
-   LICENSE
-   CHANGELOG
-   CONTRIBUTING
-   CODE_OF_CONDUCT
-   SECURITY

讓 Repository 符合專業開源專案的治理要求。

------------------------------------------------------------------------

## Generator Core Framework（Milestone 3）

Milestone 3 將 Generator Framework
從多個歷史介面，收斂為一套由共享模型、
架構文件與契約測試共同保護的核心生命週期。

完成項目包括：

-   `GenerateRequest` 與 `RuntimeOptions` 共用輸入契約
-   `GeneratorValidationError` 結構化驗證契約
-   `GenerationOperation` 與 `GenerationPlan` 共用規劃契約
-   `GenerationResult` 共用結果契約
-   `BaseGenerator.run()` canonical execution lifecycle
-   `validate_request → plan → execute → GenerationResult`
-   Legacy `GeneratorContext` lifecycle removal
-   Generator SDK public export cleanup
-   Bootstrap、Course、Week cross-generator contract tests

此階段依序完成 ADR 0005～0009、契約測試、production refactor
與文件同步， 並以 Ruff、pytest、Coverage、pre-commit 與 GitHub Actions
作為合併品質閘門。

------------------------------------------------------------------------

## Legacy Generator Lifecycle Removal

早期 `BaseGenerator` 同時保留：

-   `validate(context)`
-   `prepare(context)`
-   `generate(context)`
-   `post_generate(context)`
-   `cleanup(context)`

隨著 `GenerateRequest`、`GenerationPlan` 與 `GenerationResult`
契約成熟， 上述 Legacy Lifecycle 已不再參與正式執行流程。

OPL 最終移除這些 hooks，並將 Generator 的正式擴充點收斂為：

-   `validate_request()`
-   `plan()`
-   `execute()`

`BaseGenerator.run()` 成為唯一由 Framework 控制的執行入口。

------------------------------------------------------------------------

## Plugin SDK and Plugin Ecosystem（Milestone 4）

Milestone 4 將第三方 Generator 擴充能力從既有 internal / transitional
implementation， 收斂為正式 Public Plugin SDK 與 Python Entry Point
architecture。

核心設計由：

-   ADR 0010 --- Plugin SDK Public Contract
-   ADR 0011 --- Plugin Validation Contract
-   ADR 0012 --- Plugin Entry Point Contract

共同定義。

正式第三方 Plugin dependency boundary：

``` text
generator.sdk
```

正式 installed Plugin flow：

``` text
Installed Python Distribution
        ↓
openprojectlab.generators
        ↓
EntryPoint.load()
        ↓
validate_plugin_generator()
        ↓
metadata/runtime identity check
        ↓
preflight all
        ↓
register all
```

Milestone 4 完成項目包括：

-   `generator.sdk` Public Plugin SDK contract
-   Public SDK export / third-party-style contract tests
-   Plugin discovery、validation、loader 與 Registry boundaries
-   `PluginError` Plugin-facing error contract
-   concrete `BaseGenerator` subclass validation
-   Plugin naming contract
-   zero-argument construction contract
-   `openprojectlab.generators` canonical Entry Point group
-   one Entry Point → one `BaseGenerator` subclass
-   `entry_point.name == generator.name`
-   validate-all-before-register transaction semantics
-   no-partial-registration guarantee
-   Registry collision preflight
-   legacy `PluginManager` / `PluginDescriptor` removal
-   `docs/plugin-authoring.md`
-   `examples/plugins/hello-generator/`
-   standalone example Plugin tests
-   host-side example architecture tests
-   real installed-distribution Entry Point E2E validation

Step 4E-3 最終使用 temporary target 執行真實 package
installation，並透過 `importlib.metadata` 發現 `hello-plugin`，再交給
canonical Plugin runtime 驗證與註冊。

Milestone 4 acceptance baseline：

``` text
452 passed
Coverage: 85.90%
Required coverage: 67.0%
```

最終 E2E acceptance 已 merge 至 `main`：

``` text
13eac54 test: validate installed example plugin entry point (#37)
```

Milestone 4 的正式 Acceptance / Exit Criteria 記錄於：

``` text
docs/milestones/milestone-4-acceptance.md
```

Milestone 4 因此正式完成。

------------------------------------------------------------------------

# 下一階段

Milestone 2.5：

-   Documentation Standardization（Completed）

Milestone 3：

-   Generator Core Framework（Completed）

Milestone 4：

-   Plugin SDK and Plugin Ecosystem（Completed）

Milestone 5：

-   Open Courseware Platform（Next / Planning）

Milestone 6：

-   AI Integration

------------------------------------------------------------------------

# 我們的願景

OpenProjectLab 的目標不是建立更多程式，而是建立：

> **更容易維護、更容易理解、更容易演進的軟體工程文化。**

------------------------------------------------------------------------

> Build projects, not just code.
