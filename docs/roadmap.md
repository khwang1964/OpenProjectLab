# OpenProjectLab Roadmap

> Status: Active Last Updated: 2026-08-20

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

> **v1.1.4 Marketplace CLI Implementation next**

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

# Milestone 8 --- v1.0 Stabilization & Release Readiness ✅

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

## Step 8.4 --- Packaging / Installation / Distribution ✅

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
Packaging suite --- 29 passed, 0 skipped
Wheel --- openprojectlab-0.6.0-py3-none-any.whl
sdist --- openprojectlab-0.6.0.tar.gz
```

Final local acceptance evidence：

``` text
1558 passed, 1 deselected
Coverage: 90.55%
Required coverage: 67.0% --- Passed
git diff --check --- Passed
Ruff / Ruff Format --- Passed
pre-commit --- Passed
GitHub Actions / CI --- Passed
```

不得依賴 developer checkout、editable-only imports、undeclared
dependencies、`PYTHONPATH`、legacy repository-level `templates/`
或未追蹤 本機檔案。

**Status:** Accepted

Step 8.4 artifact-path CI is now automated and verified on GitHub Actions:

``` text
GitHub Quality checks --- Passed
GitHub Packaging artifact verification --- Passed
```

## Step 8.5 --- Documentation & Bilingual User Manuals ✅

v1.0 now provides two formal User Manuals:

``` text
docs/user-guide/en/
docs/user-guide/zh-TW/
```

Both manuals contain 13 paired chapters covering README/navigation, concepts, installation, quick start, configuration, CLI, generators, courseware, plugins, AI integration, Marketplace, troubleshooting, and upgrading. Functional parity is protected by automated documentation tests.

The First 15 Minutes workflow is executable against the built wheel through `OPL_TEST_WHEEL` and the Step 8.4 clean-install pattern. Final local acceptance evidence:

``` text
English User Manual --- 13 chapters
zh-TW User Manual --- 13 chapters
Documentation structure/parity/functional checks --- Passed
First 15 Minutes --- 3 passed, 0 skipped
Full regression --- 1616 passed, 1 deselected
Coverage --- 90.55%
Required coverage --- 67.0% --- Passed
git diff --check / Ruff / Ruff Format / pre-commit --- Passed
```

Formal acceptance record:

``` text
docs/releases/v1.0-documentation-user-manuals-acceptance.md
```

Closure evidence:

``` text
Acceptance PR --- #120 merged
GitHub Actions / CI --- Passed
Squash merge --- Completed
main synchronization --- Completed
Post-merge consistency verification --- Completed
```

**Status:** Accepted

## Step 8.6 --- Compatibility & Deprecation Policy ✅

Governing policy：

``` text
docs/releases/v1.0-compatibility-deprecation-policy.md
```

正式 compatibility / deprecation governance 定義：

``` text
1.0.x → compatibility-preserving fixes
1.x   → backward-compatible evolution
2.0   → intentional breaking Stable-contract changes
```

Stable contract 的移除或破壞性修改必須遵循明確 deprecation / migration
path。Step 8.2 frozen classifications remain authoritative；Step 8.6 不建立
第二份 Stable-surface inventory。

Completed implementation sequence：

``` text
PR #122 — docs: define v1.0 compatibility and deprecation policy
PR #123 — test: define v1 compatibility policy contract
PR #124 — test: define v1 deprecation policy contract
```

Automation：

``` text
tests/compatibility/__init__.py
tests/compatibility/test_version_policy_contract.py
tests/compatibility/test_deprecation_policy_contract.py
```

Current delivery status：

``` text
8.6.1 Governing compatibility/deprecation design   Complete
8.6.2 Compatibility policy contract tests          Complete
8.6.3 Deprecation policy contract tests            Complete
8.6.4 Documentation / CHANGELOG integration        Complete
8.6.5 Full regression + coverage                   Passed
8.6.6 Formal Step 8.6 acceptance                   Accepted
```

Final local regression evidence：

``` text
Full regression --- 1648 passed, 1 deselected
Wheel-related skips --- 0
Coverage --- 90.55%
Required coverage --- 67.0% --- Passed
```

完成態 repository 使用實際 built wheel 與 `OPL_TEST_WHEEL` 執行
packaging / clean-install / First 15 Minutes installed-user paths，因此
這組 1648 / 90.55% 為 Step 8.6 的 fresh local acceptance evidence，
不沿用 Step 8.5 baseline。

Formal acceptance record：

``` text
docs/releases/v1.0-compatibility-deprecation-policy-acceptance.md
```

已固定 Deprecated Stable lifecycle、major-version removal boundary、
migration guidance、EN/zh-TW user-facing migration parity、documentation /
CHANGELOG obligations，以及 emergency compatibility exception evidence。

Closure evidence：

``` text
Acceptance PR --- #126 merged
GitHub Actions / CI --- Passed
Acceptance merge commit --- f3ae0584e8b47b5ccf0d94fe1a7882868d899580
Squash merge --- Completed
main synchronization --- Completed
Post-merge consistency verification --- Completed
```

Step 8.6 已正式 Accepted。下一個 active slice 為 Step 8.7 ---
Support Matrix / Known Limitations。

**Status:** Accepted

## Step 8.7 --- Support Matrix / Known Limitations ✅

Governing documents：

``` text
docs/reference/support-matrix.md
docs/releases/v1.0-known-limitations.md
```

Formal acceptance candidate：

``` text
docs/releases/v1.0-support-matrix-known-limitations-acceptance.md
```

Step 8.7 已完成 evidence-based support governance、known-limitation
register、focused automation 與 exact environment evidence population。

Completed delivery sequence：

``` text
PR #128 — docs: define v1.0 support matrix and known limitations
PR #129 — test: define v1 support matrix contracts
PR #130 — docs: record v1.0 environment support evidence
```

Focused automation：

``` text
tests/support/test_support_matrix_contract.py
tests/support/test_known_limitations_contract.py
31 passed
```

Current explicit environment support evidence：

``` text
Ubuntu (ubuntu-latest) + Python 3.14
    → Supported through GitHub Actions CI

Windows + Python 3.14.5
    → Supported through maintainer-owned wheel-backed verification
    → Step 8.6 evidence: 1648 passed, 1 deselected; 90.55% coverage
```

No broader Python-version or operating-system support is implied.

Current delivery status：

``` text
8.7.1 Support-matrix governing design              Complete
8.7.2 Known-limitations governing design           Complete
8.7.3 Support-matrix contract tests                Complete
8.7.4 Known-limitations contract tests             Complete
8.7.5 Populate exact environment evidence          Complete
8.7.6 Full regression + quality gates              Complete
8.7.7 Formal Step 8.7 acceptance                   Accepted
```

Completion-state local acceptance evidence：

``` text
Focused support suite --- 31 passed
Full regression --- 1679 passed, 1 deselected
Coverage --- 90.55%
Required coverage --- 67.0% --- Passed
git diff --check --- Passed
Ruff / Ruff Format --- Passed
pre-commit --- Passed
```

Closure evidence：

``` text
Acceptance PR --- #131 merged
GitHub Actions / CI --- Passed
Squash merge --- Completed
main synchronization --- Completed
Post-merge consistency verification --- Completed
```

Step 8.7 is formally Accepted. The active Milestone 8 focus now moves to
Step 8.8 --- Release Automation & Reproducibility.

**Status:** Accepted

## Step 8.8 --- Release Automation & Reproducibility ✅

Step 8.8 已完成 governing design、release identity / artifact / workflow /
GitHub Release / semantic reproducibility contracts、maintainer release
documentation，以及 completion-state local verification。

Release identity 維持單一可追溯關係：

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

已完成的 release-readiness automation boundary 包括：

- canonical version / tag / commit consistency
- clean release-artifact selection and metadata validation
- checksum generation / verification
- verification-before-publication workflow contract
- GitHub Release identity / asset consistency
- wheel-backed clean-install verification
- semantic reproducibility verification
- maintainer release runbook and abort/correction procedures
- fresh completion-state full regression and coverage verification

Step 8.8 completion-state local acceptance evidence：

``` text
Full regression --- 1777 passed, 1 deselected
Coverage --- 90.89%
Required coverage --- 67.0% --- Passed
```

這組 `1777 / 90.89%` 是 Step 8.8 完成態 repository 的 fresh evidence，
不沿用 Step 8.7 的 `1679 / 90.55%` baseline。

Formal acceptance record：

``` text
docs/releases/v1.0-release-automation-reproducibility-acceptance.md
```

Formal closure evidence：

``` text
Acceptance PR --- #139 merged
GitHub Actions / CI --- Passed (2 successful, 0 failing)
Merge commit --- f7d1b5f8a24d0169ee4fb5cf7484c1101a88abf7
Squash merge --- Completed
main synchronization --- Completed
Post-merge wheel-backed regression --- 1777 passed, 1 deselected in 37.40s
Post-merge coverage --- 90.89%
pre-commit --- Passed
git diff --check --- Passed
Post-merge consistency verification --- Completed
```

Step 8.8 已正式 Accepted。下一個 planned gate 為 Step 8.9 --- Full
Release-readiness Verification；本次 closure 不提前宣告 Step 8.9 已開始。

**Status:** Accepted

## Step 8.9 --- Full Release-readiness Verification

Step 8.9 將 Steps 8.1–8.8 的 accepted contracts 整合為完整、
artifact-backed、可稽核的 v1.0 release-readiness decision。

Governing design：

``` text
docs/releases/v1.0-full-release-readiness-verification.md
```

Planned delivery sequence：

``` text
8.9.1 Governing design and verification inventory       Completed
8.9.2 Steps 8.1–8.8 closure-contract automation          Completed
8.9.3 Contract / policy / support consistency            Completed
8.9.4 Documentation / First 15 Minutes verification      Completed
8.9.5 Artifact-backed representative installed-user E2E  Completed
8.9.6 Integrated package / release identity verification Completed
8.9.7 Full regression and local quality gates            Completed
8.9.8 GitHub Actions / CI verification                   Completed
8.9.9 Formal acceptance and post-merge consistency       Completed
```

Final verification gates include：

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

Step 8.9 不建立或發布 `v1.0.0-rc.1`，也不預先核准 Step 8.10 RC
Acceptance。通過 Step 8.9 僅代表 repository 已準備進入 RC Acceptance。

Step 8.9.2 closure-contract automation passed 28 focused tests and corrected
the Step 8.1 release-readiness baseline status from `Proposed` to `Accepted`.

Step 8.9.3 combined release-readiness coverage passed 50 focused tests, and
pre-commit passed. The active slice is now Step 8.9.4, which reuses the
accepted Step 8.5 documentation suites and requires a current wheel for the
First 15 Minutes installed-user path. Required wheel-backed skips do not count
as completion evidence.

Step 8.9.4 completed through PR #144 and squash merge commit
`234d683d9bae3a82cd2cda951d0926c1da1c9140`. The post-merge current-wheel
documentation and release-readiness suite passed 116 tests with zero required
skips, and the working tree was clean.

Step 8.9.5 now verifies one representative installed-user journey from the
configured wheel in a fresh environment outside the source checkout, including
installed identity, console entry point, generated artifact, and invalid-command
behavior.

Step 8.9.5 completed through PR #145 and squash merge commit
`e34ce0d901c2c7a214c0785cdebeee1d3c63359b`. Both required GitHub Actions
jobs passed. Post-merge artifact-backed verification passed 64 focused tests
with zero required skips, and the working tree was clean.

Step 8.9.6 completed through PR #146 and established integrated canonical
version, wheel/sdist identity, distribution metadata, artifact-set, checksum,
commit, and release-source consistency without creating a tag, GitHub Release,
or RC.

Step 8.9.7 then completed the fresh local completion-state regression:

``` text
1822 passed, 22 skipped, 1 deselected
Coverage: 90.89%
Required coverage: 67.0% --- Passed
pre-commit --- Passed
git diff --check --- Passed
working tree --- Clean
```

All 22 skips were reviewed as expected artifact-backed tests requiring
`OPL_TEST_WHEEL`, `OPL_TEST_DIST_DIR`, or `OPL_RELEASE_COMMIT_SHA`; they do
not represent disabled regressions.

Step 8.9.8 completed through acceptance PR #147. GitHub Actions workflow
`32229975851` passed both required jobs:

``` text
Quality checks --- Passed
Packaging artifact verification --- Passed
```

PR #147 was squash merged as
`9b0566b3fc4d2b0b94ae5e775fdd3c86c0e79e03`.

Step 8.9.9 is now active. Local `main` synchronization, post-merge consistency
verification, acceptance-record closure, and the explicit Step 8.9 `Accepted`
transition remain required before Step 8.10 may begin.

The first Step 8.9.9 post-merge run exposed a closure-contract scope defect:
the active Step 8.9 acceptance record was being scanned as if it were prior
Steps 8.1–8.8 closure debt. The scope was corrected without weakening the
forbidden-marker policy.

Closure-scope correction evidence:

``` text
PR #148 --- merged
Head commit --- 7593ee6f46c8b57162d74b663360bf6c9e0236a1
CI run --- 32232518973
Quality checks --- Passed
Packaging artifact verification --- Passed
Merge commit --- 0d1fdc5a22c0de38d3b3f806a7e85197a65e2e3d
Targeted closure-contract suite --- 29 passed
Full regression before merge --- 1823 passed, 22 skipped, 1 deselected
pre-commit / git diff --check --- Passed
```

Final Step 8.9.9 post-merge verification completed from synchronized `main`
at commit `0d1fdc5a22c0de38d3b3f806a7e85197a65e2e3d`.

``` text
HEAD == main == origin/main
Full regression --- 1823 passed, 22 skipped, 1 deselected
Coverage --- 90.89%
Required coverage --- 67.0% --- Passed
git diff --check --- Passed
Ruff / Ruff Format --- Passed
pre-commit --- Passed
Working tree --- Clean
Post-merge consistency verification --- Completed
```

Formal acceptance record:

``` text
docs/releases/v1.0-full-release-readiness-verification-acceptance.md
```

Step 8.9 is formally Accepted. It authorizes entry into Step 8.10 but does not
create or accept an RC.

**Status:** Accepted

## Step 8.10 --- RC Acceptance 🚧

Step 8.9 formal acceptance 已完成，因此 Step 8.10 已正式啟動。
Step 8.10 將 repository-level release readiness 轉換為實際 RC
acceptance contract，但仍不預先建立或接受 RC。

Governing contract：

``` text
docs/releases/v1.0-rc-acceptance.md
```

Contract automation：

``` text
tests/release_readiness/test_v1_rc_acceptance_contract.py
```

目前 delivery sequence：

``` text
8.10.1 RC Acceptance Baseline                  Completed
8.10.2 RC Acceptance Contract                  Completed
8.10.3 RC Contract Automation                  Completed
8.10.4 RC Build / Artifact Identity            Completed
8.10.5 RC Artifact-backed Verification         Completed
8.10.6 RC Full Regression / Local Quality Gates Completed
8.10.7 RC GitHub Actions / CI                  Completed
8.10.8 RC Creation / Publication Identity      Completed
8.10.9 Formal RC Acceptance / Post-merge       Completed
```

Milestone 8 completion 的 target：

``` text
v1.0.0-rc.1
```

Step 8.10 固定 RC acceptance 與 GA acceptance 分離，並採 fail-closed
原則。RC identity 必須使下列 release identity 保持一致：

``` text
canonical RC version
    ↕
approved source commit
    ↕
wheel / sdist metadata
    ↕
artifact checksums
    ↕
RC tag
    ↕
GitHub Release
```

RC 階段原則上只接受：

-   release blockers
-   correctness defects
-   compatibility defects
-   installation / packaging defects
-   security defects
-   documentation correctness fixes
-   release/test automation defects

Step 8.10 governing contract 明確要求 artifact-backed evidence；source-only
success、stale artifacts 或 required artifact-backed skips 都不能取代 RC
acceptance evidence。

Step 8.10.4 已完成 canonical RC build / artifact identity verification。

Governing design：

``` text
docs/releases/v1.0-rc-build-artifact-identity.md
```

Focused automation：

``` text
tests/release_readiness/test_v1_rc_build_artifact_identity.py
```

Completion evidence：

``` text
Canonical package version --- 1.0.0rc1
Canonical RC tag mapping --- v1.0.0-rc.1
Source commit --- 11a997c2b9787cdae34b15818c6170948e89b7fc
Fresh wheel --- openprojectlab-1.0.0rc1-py3-none-any.whl
Fresh sdist --- openprojectlab-1.0.0rc1.tar.gz
Twine check --- Passed
Focused RC build / identity verification --- 70 passed, 0 skipped
Wheel SHA-256 --- 5c6a968b5d4225d758ecedc8fa15441c64812cc413ee62d302cf2521eb0b1629
sdist SHA-256 --- 34c2bcc33f0265a8f25d1770ea209472fbcdf12f803217e87574de3f08acef12
Checksum manifest verification --- Passed
```

Step 8.10.4 的 verification 仍為 pre-publication；沒有建立或移動 Git tag，
沒有建立 GitHub Release，也沒有正式接受 RC。

Step 8.10.5 已完成 RC Artifact-backed Verification。

Governing design：

``` text
docs/releases/v1.0-rc-artifact-backed-verification.md
```

RC-specific coordination automation：

``` text
tests/release_readiness/test_v1_rc_artifact_backed_verification.py
```

Completion-state artifact-backed evidence：

``` text
Source commit --- 784a139b4afc91779d6b3c76fe35162a0e348261
Configured wheel --- openprojectlab-1.0.0rc1-py3-none-any.whl
Configured sdist --- openprojectlab-1.0.0rc1.tar.gz
Installed distribution identity --- 1.0.0rc1
Source-checkout isolation --- Passed
Installed opl entry point --- Passed
Packaged runtime resources --- Passed
First 15 Minutes --- Passed
Representative installed-user E2E --- Passed
Integrated release identity --- Passed
Checksum manifest verification --- Passed
Focused completion suite --- 59 passed
Required artifact-backed skips --- 0
```

初次 completion run 正確拒絕了 stale
`OPL_RELEASE_COMMIT_SHA=11a997c2b9787cdae34b15818c6170948e89b7fc`，
因其與目前 build source `HEAD=784a139b4afc91779d6b3c76fe35162a0e348261` 不一致。重新 fresh build、
重新產生 checksum manifest 並重新綁定四個 artifact inputs 後，59 個
artifact-backed tests 全部通過。這證明 commit-binding gate 維持
fail-closed，而不是放寬 source/artifact identity。

Step 8.10.5 仍為 pre-publication verification；沒有建立或移動
`v1.0.0-rc.1` tag，沒有建立 GitHub Release，也沒有正式接受 RC。

Step 8.10.6 已完成 RC Full Regression / Local Quality Gates。

Completion-state local evidence：

``` text
Full regression --- 1881 passed, 1 deselected
Failures / errors --- 0
Coverage --- 90.90%
Required coverage --- 67.0% --- Passed
Required artifact-backed skips --- 0
git diff --check --- Passed
Ruff --- Passed
Ruff Format --- Passed
pre-commit --- Passed
```

這組 `1881 / 90.90%` 是 Step 8.10.6 completion-state 的 fresh local
evidence；它是在四個 RC artifact inputs 仍綁定目前 fresh RC artifact set
的狀態下取得，不沿用 Step 8.10.5 的 focused `59 passed` evidence。

Step 8.10.6 仍為 pre-publication local quality gate；沒有建立或移動
`v1.0.0-rc.1` tag，沒有建立 GitHub Release，也沒有正式接受 RC。

Step 8.10.7 RC GitHub Actions / CI 已完成；PR #152 的 required
GitHub Actions jobs `Quality checks` 與 `Packaging artifact verification`
均通過，並完成 squash merge / main synchronization。

Step 8.10.8 RC Creation / Publication Identity 隨後完成。Publication
contract：

``` text
docs/releases/v1.0-rc-creation-publication-identity.md
```

Publication identity evidence：

``` text
Canonical package version --- 1.0.0rc1
Canonical RC tag --- v1.0.0-rc.1
Approved publication commit --- b5958edbbf0e3279ed74fa0e3aee13e893c5dfc8
Verified peeled tag target --- b5958edbbf0e3279ed74fa0e3aee13e893c5dfc8
Published wheel --- openprojectlab-1.0.0rc1-py3-none-any.whl
Published wheel SHA-256 --- 0dbea1bdbf972a91c25aeb84e5441cb308df866b269ab8f7feea8d099d93d337
Published sdist --- openprojectlab-1.0.0rc1.tar.gz
Published sdist SHA-256 --- 37e2593a4693b7f038da1b9f0b3ae83643fff2d989992a185a3cdc9022098ea2
Published checksum manifest --- SHA256SUMS.txt
Checksum-manifest asset SHA-256 --- 0b56ca72ab9aec34afabcf3fb00d170522a923d4e0120df3bca6234061bb3c4f
GitHub Release draft-first validation --- Passed
GitHub Release published --- Yes
GitHub Release draft --- false
GitHub Release prerelease --- true
Post-publication identity re-read --- Passed
```

Published `v1.0.0-rc.1` is now immutable under the accepted release contract;
the tag must not be moved and the published artifact bytes must not be replaced
under the same RC identity.

Step 8.10.9 Formal RC Acceptance / Post-merge is now active. Formal
acceptance candidate record：

``` text
docs/releases/v1.0-rc-acceptance-record.md
```

Formal-acceptance automation：

``` text
tests/release_readiness/test_v1_rc_formal_acceptance.py
```

Candidate focused verification：

``` text
41 passed
```

Step 8.10.9 completed through acceptance PR #154. The PR passed required
CI, was squash merged as `d37a3d84161e66e98ebbff2aafaf1a14e27f865c`, `main` was synchronized, and
post-merge consistency plus cross-document terminal-state alignment completed.

Terminal Step 8.10 state:

``` text
RC identity --- v1.0.0-rc.1
Published source SHA --- b5958edbbf0e3279ed74fa0e3aee13e893c5dfc8
Acceptance PR --- #154
Acceptance merge SHA --- d37a3d84161e66e98ebbff2aafaf1a14e27f865c
Formal RC Acceptance --- Accepted
v1.0.0 GA Acceptance --- Not Accepted
```

The acceptance merge does not change the immutable published RC tag target or
artifact identity.

RC validation 完成並取得正式 acceptance evidence 後，才進入獨立的：

``` text
v1.0.0 GA
```

**Status:** Accepted


## v1.0.0 GA Acceptance 🚧

The independent GA acceptance lifecycle is now active after accepted
`v1.0.0-rc.1`.

Current delivery sequence:

``` text
GA.1  GA Acceptance Baseline / RC Evidence Review     Completed
GA.2  GA Acceptance Contract + Automation             Completed
GA.3  GA Version / Artifact Identity                  Completed
GA.4  GA Artifact-backed Verification                 Completed
GA.5  Full Regression / Local Quality Gates           Completed
GA.6  GitHub Actions / CI                             Completed
GA.7  GA Creation / Publication Identity              Completed
GA.8  Formal GA Acceptance / Post-merge               Completed
```

GA.3 established the stable package identity:

``` text
Package version --- 1.0.0
GA tag mapping --- v1.0.0
```

GA.4 completion evidence:

``` text
Focused artifact-backed suite --- 30 passed
Required GA artifact-backed skips --- 0
Installed distribution version --- 1.0.0
Source-checkout isolation --- Passed
Installed opl entry point --- Passed
Runtime resources --- Passed
First 15 Minutes --- Passed
Representative installed-user E2E --- Passed
Integrated package / release identity --- Passed
Checksum manifest verification --- Passed
```

GA.5 fresh full-regression evidence:

``` text
1980 passed, 4 skipped, 1 deselected
Failures / errors --- 0
Coverage --- 90.90%
Required coverage --- 67.0% --- Passed
```

The four skips are historical RC artifact-backed tests that correctly refuse
to interpret the configured GA wheel as RC evidence. They are not GA required
artifact-backed skips.

Current release boundary:

``` text
v1.0.0 tag --- Published
GA GitHub Release --- Published stable / non-prerelease
GA.7 publication identity --- Completed
Formal v1.0.0 GA Acceptance --- Accepted
```

GA.5 Full Regression / Local Quality Gates is complete. Fresh completion-state
evidence includes:

``` text
Full regression --- 1980 passed, 4 skipped, 1 deselected
Failures / errors --- 0
Coverage --- 90.90%
Required coverage --- 67.0% --- Passed
Required GA artifact-backed skips --- 0
git diff --check --- Passed
Ruff --- Passed
Ruff Format --- Passed
pre-commit --- Passed
```

GA.6 GitHub Actions / CI completed with the required Quality checks and
Packaging artifact verification jobs passing.

GA.7 GA Creation / Publication Identity completed with stable `v1.0.0`,
draft-first non-prerelease GitHub Release validation, stable publication, and
post-publication identity re-read.

GA.8 Formal GA Acceptance / Post-merge completed after the pre-acceptance
contract suite passed with `43 passed`, required CI passed, the acceptance
change was squash merged, and synchronized `main` reached:

``` text
HEAD == origin/main == d13382c359873c2a9eb8fb9cf6d39e32636d5fc1
```

Final post-merge verification:

``` text
2004 passed, 4 skipped, 1 deselected
Failures / errors --- 0
Coverage --- 90.90%
Required coverage --- 67.0% --- Passed
pre-commit --- Passed
Post-merge consistency verification --- Completed
```

The four skips are historical RC artifact-backed checks rejecting the GA wheel
and are not GA-required skips.

Formal `v1.0.0` GA Acceptance is now **Accepted**.

**Status:** Accepted

## Milestone 8 Deferred / v1.1+ Candidates

Milestone 7 已明確 deferred 的 remote Marketplace、Marketplace CLI、
signing / publisher identity、sandbox / trust、dependency resolver、
ratings / reviews、monetization、AI Provider Marketplace 等能力，不因
Milestone 8 啟動而自動成為 v1.0 blocker。

Milestone 6 deferred 的 AI Refactoring Assistant、AI CLI、evaluation、
provenance / usage accounting、caching、streaming 與 tool calling 亦維持
v1.1+ candidate，除非後續 release-readiness decision 明確提升其優先級。

**Status:** Deferred / v1.1+

------------------------------------------------------------------------

# Milestone 9 --- v1.1 Operational CLI Expansion 🚧

目標：

在已接受的 v1.0 Stable contract 上，以 backward-compatible、additive
方式提供 AI 與 Marketplace 的操作型 CLI，同時維持 deterministic core、
network-independent verification 與明確 Deferred boundary。

Governing contract：

``` text
docs/releases/v1.1-planning-baseline.md
docs/releases/v1.1-cli-public-contract.md
docs/releases/v1.1-cli-public-contract-acceptance.md
```

Planned delivery sequence：

``` text
v1.1.1 Planning Baseline                         Accepted
v1.1.2 CLI Public Contract Design                Accepted
v1.1.3 Marketplace CLI Contract                  Accepted
v1.1.4 Marketplace CLI Implementation            Complete
v1.1.5 AI CLI Contract                           In Progress
v1.1.6 AI CLI Implementation                     Not Started
v1.1.7 Documentation / EN-zh-TW Parity           Not Started
v1.1.8 Reliability / Artifact-backed Verification Not Started
v1.1.9 Formal v1.1 Acceptance                    Not Accepted
```

Current release boundary：

``` text
v1.0.0 GA lifecycle --- Completed
Repository hygiene --- Completed
v1.1 governing baseline PR #164 --- Merged
v1.1 acceptance PR #165 --- Merged
v1.1.1 Planning Baseline --- Accepted
Formal v1.1 Planning Baseline Acceptance --- Accepted
v1.0 CLI Stable Surface --- Preserved
v1.1.2 CLI Public Contract Design --- Accepted
v1.1.2 governing design PR #167 --- Merged
v1.1.2 governing CI --- Passed
v1.1.2 Acceptance Closure --- Completed
Acceptance-state focused suite --- 48 passed
Acceptance-state full regression --- 2008 passed, 32 skipped, 1 deselected
Required coverage --- 67.0% --- Passed
Acceptance-state local quality gates --- Passed
Acceptance PR #168 --- Merged
Acceptance CI run 32362619408 --- Passed
Acceptance merge --- 044e80ae39b01b5006663e44ea4db0f4a98a8482
main synchronization --- Completed
Synchronized main SHA --- 044e80ae39b01b5006663e44ea4db0f4a98a8482
Working tree --- Clean
v1.0.0 tag target --- d469b41b898d80811a14a423d08b09d0b51bc189
Post-merge focused suite --- 48 passed in 0.22s
Post-merge local quality gates --- Passed
Post-merge consistency --- Completed
Terminal documentation alignment --- Completed
Focused v1/v1.1 CLI public-contract suite --- 40 passed
Formal v1.1 CLI Public Contract Acceptance --- Accepted
v1.1.3 Marketplace CLI Contract --- Accepted
Marketplace CLI Implementation --- Not Started
AI CLI Contract --- Not Started
AI CLI Implementation --- Not Started
Marketplace CLI --- Not Started
AI CLI --- Not Started
Formal v1.1 Acceptance --- Not Accepted
v1.1.3 governing contract document --- Added
v1.1.3 fail-closed contract automation --- Added
Focused Marketplace contract suite --- 35 passed
v1.1.3 pre-commit --- Passed
v1.1.3 full regression --- 2018 passed, 32 skipped, 1 deselected in 23.05s
v1.1.3 governing PR #170 --- Merged
Governing merge --- 5f63bd3dc438ba1ea5e10b8225c761964c1819bc
Governing required CI evidence --- Passed
main synchronization --- Completed
Marketplace CLI Contract Acceptance --- Accepted
Acceptance PR #171 --- Merged
Acceptance merge --- 02ed8569bbd5a6c12632783186220954b2b99f12
Post-merge consistency --- Completed
Terminal documentation alignment --- Completed
Next --- v1.1.4 Marketplace CLI Implementation
```

v1.1.4 has started with an implementation baseline only. Production
`marketplace` registration and command handlers remain Not Started. The
accepted command inventory remains exactly `versions`, `inspect`, `verify`,
and `install`; internal `list_artifacts()` does not authorize an
`opl marketplace list` command.

``` text
v1.1.4.1 Implementation Baseline / Architecture        Complete
v1.1.4.2 Internal Catalog and Parsing Adapters          Complete
v1.1.4.3 versions / inspect                             Complete
v1.1.4.4 verify / Safe Payload Acquisition              Complete
v1.1.4.5 install / dry-run / No-partial-state           Complete
v1.1.4.6 Deterministic JSON and Diagnostics             Complete
v1.1.4.7 Production Parser Registration                 Complete
v1.1.4.8 EN / zh-TW User Manual Updates                 Complete
v1.1.4.9 Full Regression / CI / Formal Acceptance       Complete
Marketplace CLI Implementation                         Complete
Formal v1.1 Acceptance                                  Not Accepted
Implementation PR #174                                  Merged
Implementation merge                                    0ac32017b1420464c7c52a2b63993fc4e27a63b4
Implementation PR #176                                  Merged
Implementation merge                                    d1fbfbbd60c9d7ae14efdff443ff550032f279c2
Implementation PR #178                                  Merged
Implementation merge                                    ec0a77cd19d8783e2877228ece0a9e006579436e
Implementation PR #180                                  Merged
Implementation merge                                    4de1347edc09d959cd8b00d6acc6f459defd938e
Implementation PR #182                                  Merged
Implementation merge                                    b415f7f02f9c81d92341a010c449ff619d97b8cd
Implementation PR #184                                  Merged
Implementation merge                                    85f8ec822270fd3c993fc0b23fa70367681bcb0c
Production Parser Registration                          Complete
Marketplace CLI Command Handlers                        Complete
Marketplace CLI Implementation Acceptance               Accepted
Documentation PR #186                                  Merged
Documentation merge                                    6a3a98d22ed2e2a995bb8d497ae5f7ff5607a0b4
EN / zh-TW Marketplace CLI Manuals                     Complete
Acceptance baseline                                    f7910d51c49c74614381491458414739c47d5d74
Acceptance-candidate full regression                   2150 passed, 33 skipped, 1 deselected
Acceptance-candidate total coverage                    90.74%
Acceptance-candidate Marketplace-focused regression    160 passed, 1 skipped
Acceptance PR #188                                      Merged
Acceptance merge                                        a89d0d4e7b8fd068c1c4e2b841489bf211efbf28
Post-merge focused verification                         56 passed
Post-merge full regression                              2158 passed, 33 skipped, 1 deselected
Post-merge total coverage                               90.74%
Marketplace CLI Implementation Acceptance               Accepted
Formal v1.1 Acceptance                                  Not Accepted
Next --- v1.1.5 AI CLI Contract
```

v1.1.5 contract state:

``` text
v1.1.5 AI CLI Contract                           In Progress
Proposed AI command inventory                    course / review / document / template
AI CLI Production Registration                  Not Started
AI CLI Implementation                           Not Started
Live-provider invocation                        Experimental / opt-in
Deterministic local response-file path           Proposed Stable core
Formal v1.1 Acceptance                           Not Accepted
Next --- v1.1.5 governing contract PR
```

Governing contract PR #170 已 squash merge 為
`5f63bd3dc438ba1ea5e10b8225c761964c1819bc`，local `main` 與
`origin/main` 已同步，working tree clean。v1.1.3 現進入獨立的 Acceptance
Closure；此狀態不代表 production implementation 或 formal acceptance。

``` text
v1.1.3 governing contract PR #170 --- Merged
Governing merge --- 5f63bd3dc438ba1ea5e10b8225c761964c1819bc
main synchronization --- Completed
Acceptance record and automation --- Added
Governing required CI evidence --- Passed
Acceptance-state focused suite --- 84 passed
Acceptance-state full regression --- 1533 passed, 11 skipped, 1 deselected
Acceptance-state execution time --- 11.00s
Acceptance-state failures / errors --- 0
Acceptance-state pre-commit --- Passed
Acceptance-state required coverage evidence --- Passed
Acceptance-state git diff --check --- Passed
Acceptance PR #171 --- Merged
Acceptance merge --- 02ed8569bbd5a6c12632783186220954b2b99f12
Acceptance PR required CI --- Passed
main synchronization after acceptance merge --- Completed
Post-merge focused suite --- Passed
Post-merge local quality gates --- Passed
Post-merge consistency --- Completed
Terminal documentation alignment --- Completed
Marketplace CLI Contract Acceptance --- Accepted
Marketplace CLI Implementation --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.4 Marketplace CLI Implementation
```

Remote Marketplace、automatic activation、signing/trust、dependency
resolution、ratings/reviews、monetization、AI Provider Marketplace、AI
Refactoring Assistant、streaming/tool calling 與 generalized transaction
rollback 仍維持 Deferred，不因 v1.1 planning 啟動而自動成為 committed
scope。

PR #164 已通過 required CI 並 squash merge 為
`33c367b989014c34c162f326ee825f3fe8f4c8e6`。同步 `main` 與
post-merge consistency verification 完成後，v1.1.1 進入獨立的
acceptance closure。Acceptance PR #165 required CI 通過並 squash merge 為
`97dac1eca516e7b91e2f5bdfbe6da84b7a32215c`；main synchronization、
post-merge focused verification 與 terminal documentation alignment 隨後
完成。因此 Formal v1.1 Planning Baseline Acceptance 現為 `Accepted`，但
Formal v1.1 Acceptance 仍為 `Not Accepted`。

v1.1.2 governing design 已建立 v1.0 CLI preservation、additive command
families、exit/stdout/stderr、machine-readable output 與
failure-before-side-effect boundary。Focused v1/v1.1 CLI public-contract suite
以 `40 passed` 完成；`marketplace` 與 `ai` 仍未註冊到 production parser，
其 dedicated contract 與 implementation slices 均維持 `Not Started`。

此結果不預先宣告 full regression、coverage、local quality gates、PR、CI、
merge、main synchronization 或 post-merge evidence。

**Status:** v1.1.2 CLI Public Contract Design Accepted

PR #167 已通過 required CI run `32360278259`，並 squash merge 為
`2727bba27a1438b949870f9dee7df4aa16d43244`。目前進入獨立的 v1.1.2
acceptance closure；acceptance PR/CI/merge、main synchronization、post-merge
consistency 與 terminal alignment 尚未完成，因此 Formal v1.1 CLI Public
Contract Acceptance 仍為 `Not Accepted`。

Acceptance-state focused/full-regression/local-quality gates 已通過。
Acceptance PR #168 required CI run `32362619408` 通過，並 squash merge 為
`044e80ae39b01b5006663e44ea4db0f4a98a8482`。Main synchronization、
post-merge consistency 與 terminal alignment 仍為 Pending，因此 Formal
v1.1 CLI Public Contract Acceptance 尚未 Accepted。

Local `main` 與 `origin/main` 已同步至
`044e80ae39b01b5006663e44ea4db0f4a98a8482`，working tree clean，且
`v1.0.0` tag target 保持
`d469b41b898d80811a14a423d08b09d0b51bc189`。下一個 gate 為 post-merge
focused/local consistency verification。

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
  v1.1.0    Operational CLI Expansion

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
------------------------------------------------------------------------

## v1.1.5 AI CLI Contract Terminal Alignment

``` text
v1.1.5 AI CLI Contract --- Accepted
Contract PR #190 --- Merged
Contract merge --- cf3da5a937bda4a478b5530660cfc0054e2e42c2
Post-merge contract verification --- 70 passed
AI CLI Production Registration --- Not Started
v1.1.6 AI CLI Implementation --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6 AI CLI Implementation
```

------------------------------------------------------------------------

## v1.1.6 AI CLI Implementation Baseline

    v1.1.5 AI CLI Contract --- Accepted
    v1.1.6 AI CLI Implementation --- In Progress
    v1.1.6.1 Implementation Baseline --- In Progress
    generator/cli/ai.py --- Not Implemented
    AI CLI Shared Infrastructure --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.2 Shared Request / Local-response Infrastructure
------------------------------------------------------------------------

## v1.1.6.1 AI CLI Implementation Baseline Terminal Alignment

    v1.1.6.1 Implementation Baseline --- Accepted
    Baseline PR #192 --- Merged
    Baseline merge --- 7520da65963d935257f476ea5e0bdd79bd519e3f
    Post-merge verification --- 75 passed
    v1.1.6 AI CLI Implementation --- In Progress
    AI CLI Shared Infrastructure --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.2 Shared Request / Local-response Infrastructure

------------------------------------------------------------------------

## v1.1.6.2 AI CLI Shared Infrastructure

    v1.1.6.1 Implementation Baseline --- Accepted
    v1.1.6.2 Shared Request / Local-response Infrastructure --- In Progress
    AI CLI course handler --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.3 course handler

------------------------------------------------------------------------

## v1.1.6.2 AI CLI Shared Infrastructure Terminal Alignment

    v1.1.6.2 Shared Request / Local-response Infrastructure --- Accepted
    Implementation PR #194 --- Merged
    Implementation merge --- 746bff69df824a6fa56051ccd80beb43acf93e73
    Post-merge verification --- 91 passed
    v1.1.6 AI CLI Implementation --- In Progress
    AI CLI course handler --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.3 course handler

------------------------------------------------------------------------

## v1.1.6.3 AI CLI Course Handler

    v1.1.6.2 Shared Request / Local-response Infrastructure --- Accepted
    v1.1.6.3 course handler --- In Progress
    course service --- AICourseGenerationService.generate_course(request)
    course JSON projection --- Deterministic
    AI CLI review handler --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.4 review handler

### Code Review Checklist

- Existing AICourseGenerationService and mapper remain authoritative.
- JSON keys and Week ordering are deterministic.
- Failure emits no success output.
- No filesystem mutation, credentials, or network access is introduced.
- The production ai parser remains unregistered.

------------------------------------------------------------------------

## v1.1.6.3 AI CLI Course Handler Terminal Alignment

    v1.1.6.3 course handler --- Accepted
    Implementation PR #196 --- Merged
    Implementation merge --- 58abbabbccf3bd54ea54032ecc5c73a34bb0f0f2
    Post-merge verification --- 109 passed
    v1.1.6 AI CLI Implementation --- In Progress
    AI CLI review handler --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.4 review handler

------------------------------------------------------------------------

## v1.1.6.4 AI CLI Review Handler

    v1.1.6.3 course handler --- Accepted
    v1.1.6.4 review handler --- In Progress
    review service --- AIReviewService.review(request)
    review JSON projection --- Deterministic / ordered
    AI CLI document handler --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.5 document handler

### Code Review Checklist

- Existing AIReviewService and mapper remain authoritative.
- Finding order and JSON keys are deterministic.
- Failure emits no success output.
- No filesystem mutation, credentials, or network access is introduced.
- The production ai parser remains unregistered.

------------------------------------------------------------------------

## v1.1.6.4 AI CLI Review Handler Terminal Alignment

    v1.1.6.4 review handler --- Accepted
    Implementation PR #198 --- Merged
    Implementation merge --- b78d68b86f7829c48c4bdc696d09a721bdcb35c5
    Post-merge verification --- 113 passed
    v1.1.6 AI CLI Implementation --- In Progress
    AI CLI document handler --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.5 document handler

------------------------------------------------------------------------

## v1.1.6.5 AI CLI Document Handler

    v1.1.6.4 review handler --- Accepted
    v1.1.6.5 document handler --- In Progress
    document service --- AIDocumentationService.generate(request)
    document JSON projection --- Deterministic / non-persistent
    AI CLI template handler --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.6 template handler

### Code Review Checklist

- Existing AIDocumentationService and mapper remain authoritative.
- Title, format, and content projection is deterministic.
- Handler returns content but never writes a documentation file.
- Failure emits no success output.
- No filesystem mutation, credentials, or network access is introduced.
- The production ai parser remains unregistered.

------------------------------------------------------------------------

## v1.1.6.5 AI CLI Document Handler Terminal Alignment

    v1.1.6.5 document handler --- Accepted
    Implementation PR #200 --- Merged
    Implementation merge --- 86d8cee44fdbcdb3785155218fecb5c016994cf0
    Post-merge verification --- 118 passed
    v1.1.6 AI CLI Implementation --- In Progress
    AI CLI template handler --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.6 template handler

------------------------------------------------------------------------

## v1.1.6.6 AI CLI Template Handler

    v1.1.6.5 document handler --- Accepted
    v1.1.6.6 template handler --- In Progress
    template service --- AITemplateCompletionService.complete(request)
    template projection --- Deterministic / non-applying / non-persistent
    Experimental live-provider boundary --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.7 Experimental provider opt-in boundary

### Code Review Checklist

- Existing AITemplateCompletionService and mapper remain authoritative.
- Template name, content, and context-key ordering are deterministic.
- Handler never applies or persists template content.
- Failure emits no success output.
- No credentials or network access is introduced.
- The production ai parser remains unregistered.

<!-- v1.1.6.6-template-handler-terminal-alignment-pr202 -->

## v1.1.6.6 AI CLI Template Handler Terminal Alignment

v1.1.6.6 Template Handler --- Accepted
Implementation PR #202 --- Merged
Implementation merge --- 1ecf3c0b843385c2deee3e849e8f1b9fbd6463bf
Post-merge focused verification --- 123 passed
v1.1.6 AI CLI Implementation --- In Progress
Experimental Provider Opt-in Boundary --- Not Started
AI CLI Production Registration --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6.7 Experimental Provider Opt-in Boundary

The template handler remains unregistered production infrastructure. The
terminal alignment does not register the i parser, resolve a live provider,
apply generated template content, or mutate the filesystem through AI output.

<!-- v1.1.6.7-experimental-provider-opt-in-boundary -->

## v1.1.6.7 Experimental Provider Opt-in Boundary

v1.1.6.7 Experimental Provider Opt-in Boundary --- In Progress
Provider Resolution --- Injection Only
Supported Experimental Provider --- openai
SDK Import / Environment Lookup --- Deferred to Composition Root
Provider Handler Wiring --- Not Started
AI CLI Production Registration --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6.7 Implementation Verification / PR / CI

The candidate introduces an explicit, fail-closed provider resolver. Unknown
providers, absent client factories, and absent API keys fail before client
construction. Existing deterministic local-response handlers remain unchanged.

<!-- v1.1.6.7-provider-opt-in-terminal-alignment-pr204 -->

## v1.1.6.7 Experimental Provider Opt-in Boundary Terminal Alignment

v1.1.6.7 Experimental Provider Opt-in Boundary --- Accepted
Implementation PR #204 --- Merged
Implementation merge --- ac8f88ce8ab0cdb708671411459910a57c7fa1d2
Post-merge focused verification --- 78 passed
Provider Resolution --- Injection Only
Provider Handler Wiring --- Not Started
AI CLI Production Registration --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6.8 Provider Handler Wiring

The accepted boundary supports only explicit provider selection through an
injected client factory. It does not own SDK import, environment lookup,
automatic fallback, handler wiring, or production parser registration.

<!-- v1.1.6.8-provider-handler-wiring -->

## v1.1.6.8 Provider Handler Wiring

v1.1.6.8 Provider Handler Wiring --- In Progress
Provider Source Selection --- Fail Closed
Provider Text Normalization --- Strict JSON Object
SDK Import / Environment Lookup --- Not Owned
AI CLI Production Registration --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6.8 Implementation Verification / PR / CI

<!-- v1.1.6.8-provider-handler-terminal-alignment-pr206 -->

## v1.1.6.8 Provider Handler Wiring Terminal Alignment

v1.1.6.8 Provider Handler Wiring --- Accepted
Implementation PR #206 --- Merged
Implementation merge --- 70ac918d139b0ac010eae400935ec2f4979e67de
Post-merge focused verification --- 76 passed
Provider Source Selection --- Fail Closed
Provider Text Normalization --- Strict JSON Object
AI CLI Production Registration --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6.9 Production Parser Registration

<!-- v1.1.6.9-production-parser-registration -->

## v1.1.6.9 AI CLI Production Parser Registration

v1.1.6.8 Provider Handler Wiring --- Accepted
v1.1.6.9 Production Parser Registration --- Accepted
Exact AI Command Inventory --- course / review / document / template
Stable Local-response Execution --- Registered
Experimental Provider Composition --- Fail Closed / Injection Required
SDK Import / Environment Lookup --- Not Owned
Implementation PR #208 --- Merged
Implementation merge --- 2befa064c8172fe2dab05c06d3737935d38642be
Post-merge consistency verification --- Passed
AI CLI Implementation Acceptance --- Not Accepted
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6.10 EN / zh-TW User Manual Parity

Production parser registration is now terminally aligned with merged
implementation evidence. The exact four-command surface is available through
the production parser, while provider execution remains an explicit,
fail-closed Experimental composition path.

<!-- v1.1.6.10-ai-cli-user-manual-parity -->

## v1.1.6.10 AI CLI EN / zh-TW User Manual Parity

v1.1.6.9 Production Parser Registration --- Accepted
v1.1.6.10 EN / zh-TW User Manual Parity --- Not Started
AI CLI Implementation Acceptance --- Not Accepted
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6.10 Documentation Design / Parity Automation
