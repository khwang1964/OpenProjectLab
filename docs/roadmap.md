# OpenProjectLab Roadmap

> Status: Active Last Updated: 2026-08-15

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

目前焦點：

> **Milestone 6 --- AI Integration**

Milestone 6 已完成 Design First 與主要 provider-independent AI
contracts，並已落地 AI core、structured validation、Courseware
mapping、Course Generation、Review、Documentation、Template Completion
與 Course Builder。

目前焦點已轉向：

> **Milestone 6 documentation alignment → formal acceptance → post-merge consistency**

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

# Milestone 6 --- AI Integration 🚧

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

## Step 6.12 --- Documentation Alignment and Acceptance 🚧

-   architecture / ADR / reference alignment
-   roadmap / HISTORY / CHANGELOG alignment
-   representative AI E2E
-   full regression / coverage
-   pre-commit / CI
-   `docs/milestones/milestone-6-acceptance.md`
-   post-merge consistency verification

## Deferred / Follow-Up Capabilities

-   AI Refactoring Assistant
-   AI CLI
-   provider marketplace / pluginized provider adapters
-   AI evaluation / provenance / usage accounting
-   caching / streaming / tool calling

這些不應阻擋 provider-independent core architecture 的
acceptance，除非後續 ADR 將其提升為 Milestone 6 exit criterion。

**Status:** Formal Acceptance In Progress

------------------------------------------------------------------------

# Milestone 7 --- Marketplace

## Planned Features

-   Template Packages
-   Plugin Marketplace
-   Community Repository
-   Shared Generators
-   Versioned Templates

------------------------------------------------------------------------

# Version Targets

  Version   Target
  --------- --------------------------------
  v0.2.x    Foundation
  v0.3.x    Documentation + Core Framework
  v0.4.x    Plugin Framework
  v0.5.x    Open Courseware
  v0.6.x    AI Integration
  v0.7.x    Marketplace
  v1.0.0    Stable Release

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
