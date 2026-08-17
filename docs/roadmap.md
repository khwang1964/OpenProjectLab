# OpenProjectLab Roadmap

> Status: Active Last Updated: 2026-08-17

------------------------------------------------------------------------

# Vision

OpenProjectLab（OPL）的目標不是建立一個單純的 Project
Generator，而是打造一個以 **Design First、Documentation
First、Automation First、Testing First** 為核心的 **Project Engineering
Platform**。

------------------------------------------------------------------------

# Current Status

Milestone 3 Generator Core Framework 與 Milestone 4 Plugin Ecosystem
已完成。

Milestone 4 final acceptance baseline：

``` text
452 passed
Coverage: 85.90%
Required coverage: 67.0%
```

Milestone 5 --- Open Courseware Platform 已完成正式 acceptance 與
post-merge consistency alignment。

Milestone 5 completion baseline：

``` text
Course / Week domain foundation
    ↓
Lab / Quiz / Assignment generators
    ↓
Slides / Website projections
    ↓
Courseware Composition
    ↓
Representative E2E
    ↓
Milestone 5 formal acceptance
    ↓
Post-merge consistency verification
```

Milestone 6 --- AI Integration 已完成 formal acceptance 與 post-merge
consistency alignment。

Milestone 6 completion baseline：

``` text
1119 passed, 1 deselected
Coverage: 90.23%
Required coverage: 67.0%
CI: Passed
```

目前焦點：

> **Milestone 8 --- Step 8.3 Accepted; merge closeout in progress**

------------------------------------------------------------------------

# Milestone 1 --- Foundation ✅

**Status:** Completed

------------------------------------------------------------------------

# Milestone 2 --- Framework Foundation ✅

**Status:** Completed

------------------------------------------------------------------------

# Milestone 2.5 --- Documentation Standardization ✅

**Status:** Completed

------------------------------------------------------------------------

# Milestone 3 --- Core Framework ✅

完成：

-   `GenerateRequest` / `RuntimeOptions`
-   `GeneratorValidationError`
-   `GenerationOperation` / `GenerationPlan`
-   `GenerationResult`
-   canonical `BaseGenerator.run()`
-   `validate_request → plan → execute`
-   legacy Generator lifecycle removal
-   cross-generator contract tests
-   architecture / reference / ADR alignment

**Status:** Completed

------------------------------------------------------------------------

# Milestone 4 --- Plugin Ecosystem ✅

完成 stable `generator.sdk`、Plugin validation、canonical
`openprojectlab.generators` Entry Point runtime、transactional
registration、 legacy PluginManager removal、third-party example
distribution 與 installed distribution E2E acceptance。

Acceptance：

-   `docs/milestones/milestone-4-acceptance.md`
-   452 tests passed
-   85.90% coverage
-   CI / pre-commit / Ruff / coverage gates Green

**Status:** Completed

Future Plugin distribution/compatibility evolution remains separate from
the Milestone 5 Open Courseware work.

------------------------------------------------------------------------

# Milestone 5 --- Open Courseware Platform ✅

目標：

在已穩定的 Generator Core 與 Plugin SDK 上建立可組合、可測試、可擴充的
Open Courseware generation platform。

## Completed Foundation

### Step 5.1 --- Architecture ✅

-   `docs/architecture/open-courseware-platform.md`
-   responsibility / composition / artifact boundaries
-   Design First implementation sequence

### Step 5.2 --- Minimum Course / Week Domain Contract ✅

-   ADR 0014 Accepted
-   immutable production `Course` / `Week` models
-   domain contract tests
-   deterministic Week ordering
-   duplicate Week rejection
-   existing Course/Week Generator compatibility preserved

### Step 5.3 --- Material Generators 🚧

#### Lab Generator ✅

-   ADR 0015 Accepted
-   canonical generator name: `lab`
-   explicit Week-scoped `lab_id`
-   required `week`, `lab_id`, `title`
-   deterministic `week-{week:02d}/lab/{lab_id}/README.md`
-   canonical `GenerationPlan` / `GenerationResult`
-   dry-run / overwrite / manifest integration
-   built-in generator export
-   CLI `lab` command and `list` exposure
-   contract, generator integration, and CLI integration tests
-   no `LearningMaterial` base class
-   no accidental `generator.sdk` expansion

Merged implementation sequence:

``` text
#44 design
#45 contract tests
#46 minimum implementation
#47 integration
```

#### Quiz Generator ✅

-   ADR 0016 Accepted
-   canonical generator name: `quiz`
-   explicit Week-scoped `quiz_id`
-   required `week`, `quiz_id`, `title`, `questions`
-   structured single-answer multiple-choice question contract
-   explicit and unique Question IDs
-   deterministic question / choice ordering
-   deterministic `week-{week:02d}/quiz/{quiz_id}/README.md`
-   learner-facing README does not expose correct-answer data
-   canonical `GenerationPlan` / `GenerationResult`
-   dry-run / overwrite / manifest integration
-   CLI `quiz` command and `list` / legacy `--list` exposure
-   structured CLI input through `--questions-file` JSON
-   contract, generator integration, template, and CLI integration tests
-   no scoring / grading runtime
-   no QuestionBank or randomization
-   no accidental `generator.sdk` expansion

Merged implementation sequence:

``` text
#49 design
#50 contract tests
#51 minimum implementation
#52 integration
```

#### Assignment Generator ✅

-   ADR 0017 Accepted
-   canonical generator name: `assignment`
-   explicit Week-scoped `assignment_id`
-   required `week`, `assignment_id`, `title`
-   optional ordered `objectives`, `deliverables`, and `resources`
-   optional authored `instructions` and `submission` guidance
-   deterministic `week-{week:02d}/assignment/{assignment_id}/README.md`
-   canonical `GenerationPlan` / `GenerationResult`
-   dry-run / overwrite / manifest integration
-   CLI `assignment` command and `list` / legacy `--list` exposure
-   structured CLI input through `--content-file` JSON
-   contract, template, generator integration, and CLI integration tests
-   no grading / scoring / rubric runtime
-   no submission backend
-   no accidental `generator.sdk` expansion

Merged implementation sequence:

``` text
#54 design
#55 contract tests
#56 minimum implementation
#57 integration
```

#### Slides Generator ✅

-   ADR 0018 Accepted
-   canonical generator name: `slides`
-   required deck `title` and ordered `slides`
-   deterministic canonical artifact `<target>/slides.md`
-   canonical `GenerationPlan` / `GenerationResult`
-   dry-run / overwrite / manifest integration
-   canonical template `templates/slides/slides.md.j2`
-   CLI `slides` command and `list` / legacy `--list` exposure
-   structured CLI input through `--slides-file` JSON
-   contract, template, generator integration, and CLI integration tests
-   no PPTX / PDF / HTML rendering in the core generator
-   no accidental `generator.sdk` expansion

Merged implementation sequence:

``` text
#59 design
#60 contract tests
#61 minimum implementation
#62 integration
```

#### Website Generator ✅

-   ADR 0019 Accepted
-   canonical generator name: `website`
-   required site `title` and ordered `pages`
-   each page requires a safe relative `.html` path, non-empty title,
    and authored content
-   required canonical entry page `index.html`
-   deterministic multi-page output under `<target>/site/`
-   deterministic navigation ordering derived from page ordering
-   canonical `GenerationPlan` / `GenerationResult`
-   dry-run / overwrite / manifest integration
-   canonical template `templates/website/page.html.j2`
-   CLI `website` command and `list` / legacy `--list` exposure
-   structured CLI input through `--pages-file` JSON
-   contract, template, generator integration, and CLI integration tests
-   no hosting / deployment / CMS / asset pipeline in the core generator
-   no accidental `generator.sdk` expansion

Merged implementation sequence:

``` text
#64 design
#65 contract tests
#66 minimum implementation
#67 integration
```

### Step 5.4 --- Courseware Composition Integration ✅

-   ADR 0020 Accepted
-   production `generator/courseware/composition.py`
-   deterministic ordered `GenerateRequest` composition
-   existing `GeneratorRegistry` preflight / resolution boundary
-   canonical `BaseGenerator.run(request)` execution
-   ordered `GenerationResult` aggregation
-   fail-fast semantics without cross-generator rollback
-   dry-run / overwrite propagation
-   representative Course / Week / Lab / Quiz / Assignment / Slides /
    Website integration
-   no public SDK expansion
-   no composition CLI, parallel execution, or second manifest/plugin
    infrastructure

Merged implementation sequence:

``` text
#69 design
#70 contract tests
#71 minimum implementation
#72 representative integration
```

### Step 5.5 --- Representative E2E ✅

-   `tests/integration/test_courseware_composition_e2e.py`
-   production `CoursewareComposer` and production built-in generators
-   representative Course / Week / Lab / Quiz / Assignment / Slides /
    Website flow
-   exact artifact membership verification
-   manifest generator provenance verification
-   reproducible user-facing artifact verification
-   composition-wide dry-run non-persistence
-   PR #74

### Step 5.6 --- Formal Milestone Acceptance ✅

-   `docs/milestones/milestone-5-acceptance.md`
-   roadmap / HISTORY / CHANGELOG alignment
-   final full-regression and coverage baseline
-   pre-commit / CI acceptance gates

## Acceptance and Closure

-   `docs/milestones/milestone-5-acceptance.md`
-   formal roadmap / HISTORY / CHANGELOG alignment
-   representative E2E acceptance evidence
-   full regression / coverage acceptance
-   CI / pre-commit acceptance gates
-   post-merge consistency alignment

Merged closure sequence:

``` text
#74 representative E2E
#75 formal Milestone 5 acceptance
#76 post-merge consistency alignment
```

**Status:** Completed

------------------------------------------------------------------------

# Milestone 6 --- AI Integration ✅

目標：

在 Milestone 5 已穩定的 structured Courseware Domain、Composition、
GenerationPlan 與 Filesystem boundaries 上，加入可替換、可驗證、可測試的
AI capability，而不建立第二套 generation pipeline。

核心原則：

``` text
AI proposes.
Domain validates.
Generator plans.
Filesystem commits.
Tests verify.
```

## Step 6.1 --- AI Integration Architecture and Contract ✅

-   `docs/architecture/ai-integration.md`
-   ADR 0021 --- AI Integration Contract
-   Provider / Domain / Generator / Filesystem responsibility boundaries
-   credential isolation
-   deterministic testing strategy
-   PR #77

## Step 6.2 --- AI Core Contracts ✅

-   immutable `AIRequest` / `AIResponse`
-   runtime-checkable `AIProvider`
-   deterministic `FakeAIProvider`
-   core contract tests
-   PR #78

## Step 6.3 --- Structured Response Validation ✅

-   `AIResponseValidationError`
-   mapping-shaped structural validation
-   required-field / type validation
-   immutable/no-side-effect failure semantics
-   PR #79

## Step 6.4 --- AI-to-Courseware Mapping ✅

-   AI structured response → production `Course` / `Week`
-   deterministic Week ordering
-   Domain invariant ownership preserved
-   provider metadata excluded from Domain
-   PR #80

## Step 6.5 --- AI Course Generation Service ✅

-   injected `AIProvider`
-   provider invocation → existing Courseware mapper
-   deterministic Fake-provider application tests
-   PR #81

## Step 6.6 --- AI Review Contract and Service ✅

-   immutable `AIReviewFinding` / `AIReviewResult`
-   structured severity / finding validation
-   advisory-only `AIReviewService`
-   no Courseware or filesystem mutation
-   PR #82

## Step 6.7 --- AI Documentation Contract and Service ✅

-   immutable `AIDocumentDraft`
-   structured markdown / text draft validation
-   `AIDocumentationService`
-   no direct repository/document filesystem mutation
-   PR #83

## Step 6.8 --- AI Template Completion Contract and Service ✅

-   immutable `AITemplateCompletionResult`
-   deterministic context-key ordering
-   `AITemplateCompletionService`
-   no direct Jinja render or filesystem mutation
-   PR #84

## Step 6.9 --- AI Course Builder ✅

-   immutable `AICourseBuildRequest`
-   high-level `AICourseBuilder`
-   provider-independent `AIRequest` construction
-   existing Courseware mapping reuse
-   explicit requested `week_count` completeness rule
-   existing Domain validation preserved
-   PR #85

## Step 6.10 --- Real Provider Adapter ✅

-   ADR 0022 --- AI Provider Adapter Contract Accepted
-   existing `AIProvider` remains the application boundary
-   provider-specific SDK / request / response types remain
    adapter-private
-   minimum provider-independent error hierarchy established
-   runtime credential isolation preserved
-   finite timeout behavior established
-   no hidden automatic retry in the initial adapter contract
-   first concrete `OpenAIProviderAdapter` implemented
-   deterministic provider contract / credential / error tests
-   deterministic no-network OpenAI adapter tests
-   `ai_live` marker registered for explicit live-provider verification
-   live tests excluded from normal pytest / pre-commit /
    credential-free CI
-   missing `OPENAI_API_KEY` skips explicit live smoke verification
-   paid/live OpenAI invocation is optional operational verification and
    is not required for ADR 0022 acceptance or Step 6.10 completion

Implementation sequence:

``` text
ADR 0022
    ↓
Provider Adapter Contract Tests
    ↓
Provider-independent Error Contract
    ↓
OpenAI Provider Adapter
    ↓
No-network OpenAI Adapter Tests
    ↓
Live-test Separation
    ↓
Documentation / Regression / CI
```

**Step 6.10 Status:** Completed

## Step 6.11 --- Representative AI E2E ✅

-   `tests/integration/test_ai_courseware_e2e.py`
-   production `AICourseBuilder`
-   deterministic `FakeAIProvider`
-   production `Course` / `Week`
-   production `CoursewareComposer`
-   production Course / Week Generators
-   deterministic artifact membership and content
-   reproducibility across repeated runs
-   composition-wide dry-run non-persistence
-   invalid AI response fails before filesystem side effects
-   no network / no API key / no paid invocation
-   Step 6.11 verification baseline: 1119 passed

Representative acceptance path:

``` text
Course Specification
        ↓
AICourseBuilder
        ↓
FakeAIProvider
        ↓
AIResponse
        ↓
Validation / Mapping
        ↓
Courseware Domain
        ↓
Courseware Composition
        ↓
GenerationPlan
        ↓
Filesystem
```

**Step 6.11 Status:** Completed

## Step 6.12 --- Documentation Alignment and Acceptance ✅

Completed acceptance evidence:

-   architecture / ADR / reference alignment
-   roadmap / HISTORY / CHANGELOG alignment
-   representative deterministic AI E2E
-   `docs/milestones/milestone-6-acceptance.md`
-   final regression: 1119 passed, 1 deselected
-   total coverage: 90.23%
-   required coverage: 67.0% --- Passed
-   acceptance PR GitHub Actions / CI --- Passed
-   squash merge completed
-   post-merge consistency verification completed

**Step 6.12 Status:** Completed

## Deferred / Follow-Up Capabilities

-   AI Refactoring Assistant
-   AI CLI
-   provider marketplace / pluginized provider adapters
-   AI evaluation / provenance / usage accounting
-   caching / streaming / tool calling

這些不應阻擋 provider-independent core architecture 的
acceptance，除非後續 ADR 將其提升為 Milestone 6 exit criterion。

**Status:** Completed

------------------------------------------------------------------------

# Milestone 7 --- Marketplace ✅

目標：

在既有 Generator Core、Plugin SDK、Courseware、AI 與 Filesystem
boundaries 上建立可發佈、可發現、可驗證、可安裝與可版本化的 Marketplace
ecosystem，而不建立第二套 execution framework。

核心原則：

``` text
Marketplace distributes.
Contracts validate.
Existing OPL pipelines execute.
```

## Step 7.1 --- Marketplace Architecture and Artifact Contract ✅

-   `docs/architecture/marketplace.md`
-   ADR 0023 --- Marketplace Artifact Contract
-   common Marketplace artifact identity / version / type contract
-   OPL compatibility / distribution / integrity boundaries
-   installation separated from activation
-   existing Plugin SDK / Generator lifecycle preserved
-   no accidental `generator.sdk` expansion

## Step 7.2 --- Artifact Contract Tests ✅

-   `tests/marketplace/test_artifact_contract.py`
-   identity / version / type / coordinate validation
-   compatibility requirement validation
-   distribution / integrity metadata validation
-   immutability and deterministic behavior

## Step 7.3 --- Minimum Artifact Models ✅

-   production `generator/marketplace/models.py`
-   immutable `MarketplaceArtifact`
-   immutable identity / version / coordinate models
-   deterministic compatibility requirement

## Step 7.4 --- Repository / Index Contract ✅

-   deterministic `InMemoryMarketplaceRepository`
-   exact coordinate lookup
-   deterministic available-version ordering
-   explicit not-found semantics
-   duplicate-coordinate rejection
-   no network dependency

## Step 7.5 --- Integrity and Acquisition ✅

-   deterministic SHA-256 integrity verification
-   explicit integrity mismatch failure
-   deterministic `InMemoryArtifactAcquirer`
-   acquisition returns bytes only
-   integrity and acquisition kept separate
-   no network / filesystem side effects

## Step 7.6 --- Installation Integration ✅

-   immutable structured installation result
-   deterministic `InMemoryArtifactInstaller`
-   duplicate-install rejection
-   installation remains separate from activation
-   no Plugin registration / Generator execution / Courseware output

## Step 7.7 --- Template Packages ✅

-   immutable `TemplateEntry`
-   immutable `TemplatePackageManifest`
-   immutable `TemplatePackage`
-   Marketplace artifact identity/version reused
-   safe relative paths and traversal rejection
-   duplicate name/path rejection
-   deterministic template/resource ordering
-   no Jinja execution or Generator runtime

## Step 7.8 --- Representative Marketplace E2E ✅

-   `tests/integration/test_marketplace_e2e.py`
-   production repository → acquisition → integrity → installation
    composition
-   exact-coordinate representative flow
-   deterministic repeated-run behavior
-   repository / acquisition / integrity failure-before-install behavior
-   no partial installation state
-   no public network
-   no generated-project filesystem persistence
-   no Plugin activation or Generator execution

## Step 7.9 --- Documentation Alignment and Formal Acceptance ✅

Completed local acceptance evidence：

``` text
1315 passed, 1 deselected
Coverage: 89.89%
Required coverage: 67.0% --- Passed
```

Documentation alignment：

-   `docs/architecture/marketplace.md`
-   ADR 0023 → Accepted
-   ADR index
-   roadmap
-   HISTORY
-   CHANGELOG
-   `docs/milestones/milestone-7-acceptance.md`

Completed closure gates：

-   acceptance PR GitHub Actions / CI --- Passed
-   squash merge --- Completed
-   post-merge consistency verification --- Completed
-   local `main` synchronized with `origin/main`

## Deferred / Follow-Up Capabilities

-   remote Marketplace service
-   Community Repository hosting
-   Marketplace CLI
-   real package-manager integration
-   Marketplace-driven Plugin / Generator activation
-   artifact signing / publisher identity
-   sandbox / trust policy
-   general-purpose dependency resolver
-   lock-file / cache policy
-   ratings / reviews
-   monetization / payment
-   AI Provider Marketplace

**Status:** Completed

------------------------------------------------------------------------

# Milestone 8 --- v1.0 Stabilization & Release Readiness 🚧

目標：

將 Milestone 1--7 已建立的 capability
收斂成可公開承諾、可安裝、可文件化、 可維護且可重現驗證的 v1.0 stable
release，而不是再建立新的主要平台能力。

核心原則：

``` text
Do not add what v1.0 does not need.
Audit what v1.0 already has.
Stabilize what v1.0 promises.
Document what v1.0 supports.
Automate what v1.0 must verify.
Release only what v1.0 can maintain.
```

Milestone 8 是 **v1.0 前最後一個 engineering milestone**，並採用
feature-freeze mindset。非 release-blocking 的新功能應移入 v1.1+
backlog。

## Step 8.1 --- Release Readiness Baseline ✅

建立：

``` text
docs/releases/v1.0-release-readiness.md
```

Step 8.1 定義：

-   Milestone 8 scope 與 release-readiness gates
-   Stable / Candidate / Experimental / Internal / Deferred contract
    classification
-   public contract inventory
-   feature-freeze boundary
-   bilingual User Manual requirement
-   compatibility / deprecation policy requirements
-   support matrix / known limitations requirements
-   packaging / clean-install verification
-   release automation / reproducibility requirements
-   RC 與 GA 的 acceptance separation

**Status:** Completed

Step 8.1 已建立並對齊 Milestone 8 的 governing release-readiness
baseline；後續 contract freeze、packaging、documentation 與 release
gates 依此執行。

## Step 8.2 --- Public Contract Audit & Freeze ✅

Audit 並分類：

-   CLI
-   Generator lifecycle / request / plan / result
-   `generator.sdk`
-   Plugin SDK / Entry Point / validation / registration
-   Course / Week Domain
-   built-in Generators
-   Courseware Composition
-   AI provider-independent contracts
-   Marketplace contracts
-   Configuration
-   Filesystem-visible behavior
-   Errors / exceptions
-   generated artifact layouts
-   installation entry points

只有具備 implementation、tests、documentation 與明確 compatibility
semantics 的 capability 才可升級為 Stable。

已建立：

``` text
docs/releases/v1.0-public-contract-audit.md
docs/releases/v1.0-public-contract-freeze-acceptance.md
```

Dedicated v1 freeze tests 已涵蓋
SDK、Generator、Plugin、CLI、Courseware、 built-in
artifacts、Composition、AI、Marketplace、Configuration、
Filesystem、Errors 與 Packaging metadata / console entry point。

Step 8.2 audit 已記錄 packaging resource finding：repository-level
`templates/` 必須在 Step 8.4 透過 built artifact / clean-install 驗證，
目前不得提前宣稱為 packaged-resource guarantee。

Final acceptance evidence：

``` text
1469 passed, 1 deselected
Coverage: 90.33%
Required coverage: 67.0% --- Passed
git diff --check --- Passed
Ruff / Ruff Format --- Passed
pre-commit --- Passed
GitHub Actions / CI --- Passed
```

**Status:** Accepted

## Step 8.3 --- Reliability / Regression Hardening ✅

Governing design：

``` text
docs/releases/v1.0-reliability-hardening.md
```

已完成 reliability hardening：

-   Filesystem / Write Policy
-   Generator lifecycle
-   Courseware Composition
-   Plugin loading / registration
-   Marketplace
-   AI
-   CLI / structured input
-   representative reliability E2E

已建立：

``` text
tests/core/test_v1_filesystem_reliability.py
tests/generators/test_v1_generator_reliability.py
tests/courseware/test_v1_composition_reliability.py
tests/plugins/test_v1_plugin_reliability.py
tests/marketplace/test_v1_marketplace_reliability.py
tests/ai/test_v1_ai_reliability.py
tests/integration/test_v1_cli_reliability.py
tests/integration/test_v1_reliability_e2e.py
```

Consolidated targeted reliability evidence：

``` text
66 passed
```

Step 8.3 不建立新的 v1.0 product scope，也不引入 cross-Generator
rollback / generalized transaction promise。Final acceptance
必須從完成態 repository 重新取得 full regression、coverage、quality
gates 與 CI evidence，不重用 Step 8.2 baseline。

Formal acceptance record：

``` text
docs/releases/v1.0-reliability-hardening-acceptance.md
```

Final acceptance evidence：

``` text
Targeted reliability suite: 66 passed
Full regression: 1535 passed, 1 deselected
Coverage: 90.54%
Required coverage: 67.0% --- Passed
git diff --check --- Passed
Ruff / Ruff Format --- Passed
pre-commit --- Passed
GitHub Actions / CI --- Passed
```

**Status:** Accepted

## Step 8.4 --- Packaging / Installation / Distribution 🚧

Governing design：

``` text
docs/releases/v1.0-packaging-installation.md
```

Formal acceptance record：

``` text
docs/releases/v1.0-packaging-installation-acceptance.md
```

Step 8.4 已完成 package-resource production fix，將 runtime templates 從
repository-level `templates/` 遷移為唯一 canonical source：

``` text
generator/resources/templates/
```

CLI default template resolution 已改由 package-resource boundary 提供，
explicit template-root override behavior 維持不變。

Local installed-user verification：

``` text
Build wheel / sdist --- Passed
twine check --- Passed
Wheel runtime resources --- Passed
Clean-wheel installation --- Passed
Installed generator import --- Passed
Installed opl list --- Passed
Installed representative generation --- Passed
Legacy repository templates dependency --- Removed
```

Final local acceptance evidence：

``` text
1558 passed, 1 deselected
Coverage: 90.55%
Required coverage: 67.0% --- Passed
git diff --check --- Passed
Ruff / Ruff Format --- Passed
pre-commit --- Passed
GitHub Actions / CI --- Pending
```

不得依賴 developer checkout、editable-only imports、undeclared
dependencies、`PYTHONPATH`、legacy repository-level `templates/`
或未追蹤 本機檔案。

**Status:** Local Acceptance Passed --- GitHub Actions / CI Pending

## Step 8.5 --- Documentation & Bilingual User Manuals

v1.0 必須提供兩套正式 User Manual：

``` text
docs/user-guide/en/
docs/user-guide/zh-TW/
```

兩個版本至少涵蓋：

-   README / navigation
-   concepts
-   installation
-   quick start
-   configuration
-   CLI
-   generators
-   courseware
-   plugins
-   AI integration
-   Marketplace
-   troubleshooting
-   upgrading

English 與 Traditional Chinese (Taiwan) 必須維持 functional
documentation parity。

Quick Start 應建立 First 15 Minutes representative onboarding
flow，並在可行 範圍內轉為 executable documentation smoke test。

**Status:** Planned

## Step 8.6 --- Compatibility & Deprecation Policy

建立正式 compatibility / deprecation governance，定義：

``` text
1.0.x → compatibility-preserving fixes
1.x   → backward-compatible evolution
2.0   → intentional breaking public-contract changes
```

Stable contract 的移除或破壞性修改必須遵循明確 deprecation / migration
path。

**Status:** Planned

## Step 8.7 --- Support Matrix / Known Limitations

建立：

``` text
docs/reference/support-matrix.md
docs/releases/v1.0-known-limitations.md
```

Supported 必須有 CI、automated tests 或明確 release verification
evidence。

文件應清楚區分：

``` text
Supported
Experimental
Known Limitation
Deferred
```

**Status:** Planned

## Step 8.8 --- Release Automation & Reproducibility

建立 maintainer release process，並確保：

``` text
Version
  ↕
Commit SHA
  ↕
Git Tag
  ↕
Release Artifact
  ↕
GitHub Release
```

保持一致且可追溯。

Automation 應涵蓋可合理自動化的 version verification、quality gates、
documentation checks、package build、clean-install smoke tests 與
release artifact validation。

**Status:** Planned

## Step 8.9 --- Full Release-readiness Verification

Final verification 至少包括：

``` text
git diff --check
Ruff
Ruff Format
pre-commit
full pytest
coverage
documentation checks
package validation
clean-install smoke tests
GitHub Actions / CI
```

並建立 representative installed-user E2E。

**Status:** Planned

## Step 8.10 --- RC Acceptance

Milestone 8 completion 的 target：

``` text
v1.0.0-rc.1
```

RC acceptance 與 GA acceptance 分離。

RC 階段原則上只接受：

-   release blockers
-   correctness defects
-   compatibility defects
-   installation / packaging defects
-   security defects
-   documentation correctness fixes
-   release/test automation defects

RC validation 通過後才進入：

``` text
v1.0.0 GA
```

**Status:** Planned

## Milestone 8 Deferred / v1.1+ Candidates

Milestone 7 已明確 deferred 的 remote Marketplace、Marketplace CLI、
signing / publisher identity、sandbox / trust、dependency resolver、
ratings / reviews、monetization、AI Provider Marketplace 等能力，不因
Milestone 8 啟動而自動成為 v1.0 blocker。

Milestone 6 deferred 的 AI Refactoring Assistant、AI CLI、evaluation、
provenance / usage accounting、caching、streaming 與 tool calling 亦維持
v1.1+ candidate，除非後續 release-readiness decision 明確提升其優先級。

**Status:** In Progress

------------------------------------------------------------------------

# Version Targets

  Version   Target
  --------- -------------------------------------
  v0.2.x    Foundation
  v0.3.x    Documentation + Core Framework
  v0.4.x    Plugin Framework
  v0.5.x    Open Courseware
  v0.6.x    AI Integration
  v0.7.x    Marketplace
  v1.0.0    Stabilization → RC → Stable Release

------------------------------------------------------------------------

# Definition of Done

每個 Milestone 完成時應符合：

-   Architecture 完成
-   Reference 完成
-   Tests 通過
-   Documentation 更新
-   CI 通過
-   pre-commit 通過
-   CHANGELOG 更新
-   必要時新增 ADR
-   Acceptance / Exit Criteria 有明確紀錄

------------------------------------------------------------------------

# Long-Term Vision

OpenProjectLab 最終目標是成為一個可持續演進的 **Project Engineering
Platform**，
協助開發者建立高品質、可維護、可擴充且具有完整工程治理能力的專案，而不只是產生程式碼。

> **Build projects with engineering discipline, not just code
> generation.**
