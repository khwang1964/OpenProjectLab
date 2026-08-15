# OpenProjectLab Roadmap

> Status: Active
> Last Updated: 2026-08-15

------------------------------------------------------------------------

# Vision

OpenProjectLab（OPL）的目標不是建立一個單純的 Project Generator，而是打造一個以
**Design First、Documentation First、Automation First、Testing First** 為核心的
**Project Engineering Platform**。

------------------------------------------------------------------------

# Current Status

Milestone 3 Generator Core Framework 與 Milestone 4 Plugin Ecosystem 已完成。

Milestone 4 final acceptance baseline：

```text
452 passed
Coverage: 85.90%
Required coverage: 67.0%
```

Milestone 5 — Open Courseware Platform 已完成正式 acceptance 與 post-merge consistency alignment。

Milestone 5 completion baseline：

```text
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

> **Milestone 6 — AI Integration**

Milestone 6 目前進入 Design First 階段，先建立 AI Integration Architecture 與 ADR 0021，再進入 AI core contract tests 與 implementation。

------------------------------------------------------------------------

# Milestone 1 — Foundation ✅

**Status:** Completed

------------------------------------------------------------------------

# Milestone 2 — Framework Foundation ✅

**Status:** Completed

------------------------------------------------------------------------

# Milestone 2.5 — Documentation Standardization ✅

**Status:** Completed

------------------------------------------------------------------------

# Milestone 3 — Core Framework ✅

完成：

- `GenerateRequest` / `RuntimeOptions`
- `GeneratorValidationError`
- `GenerationOperation` / `GenerationPlan`
- `GenerationResult`
- canonical `BaseGenerator.run()`
- `validate_request → plan → execute`
- legacy Generator lifecycle removal
- cross-generator contract tests
- architecture / reference / ADR alignment

**Status:** Completed

------------------------------------------------------------------------

# Milestone 4 — Plugin Ecosystem ✅

完成 stable `generator.sdk`、Plugin validation、canonical
`openprojectlab.generators` Entry Point runtime、transactional registration、
legacy PluginManager removal、third-party example distribution 與 installed
distribution E2E acceptance。

Acceptance：

- `docs/milestones/milestone-4-acceptance.md`
- 452 tests passed
- 85.90% coverage
- CI / pre-commit / Ruff / coverage gates Green

**Status:** Completed

Future Plugin distribution/compatibility evolution remains separate from the
Milestone 5 Open Courseware work.

------------------------------------------------------------------------

# Milestone 5 — Open Courseware Platform ✅

目標：

在已穩定的 Generator Core 與 Plugin SDK 上建立可組合、可測試、可擴充的
Open Courseware generation platform。

## Completed Foundation

### Step 5.1 — Architecture ✅

- `docs/architecture/open-courseware-platform.md`
- responsibility / composition / artifact boundaries
- Design First implementation sequence

### Step 5.2 — Minimum Course / Week Domain Contract ✅

- ADR 0014 Accepted
- immutable production `Course` / `Week` models
- domain contract tests
- deterministic Week ordering
- duplicate Week rejection
- existing Course/Week Generator compatibility preserved

### Step 5.3 — Material Generators 🚧

#### Lab Generator ✅

- ADR 0015 Accepted
- canonical generator name: `lab`
- explicit Week-scoped `lab_id`
- required `week`, `lab_id`, `title`
- deterministic `week-{week:02d}/lab/{lab_id}/README.md`
- canonical `GenerationPlan` / `GenerationResult`
- dry-run / overwrite / manifest integration
- built-in generator export
- CLI `lab` command and `list` exposure
- contract, generator integration, and CLI integration tests
- no `LearningMaterial` base class
- no accidental `generator.sdk` expansion

Merged implementation sequence:

```text
#44 design
#45 contract tests
#46 minimum implementation
#47 integration
```

#### Quiz Generator ✅

- ADR 0016 Accepted
- canonical generator name: `quiz`
- explicit Week-scoped `quiz_id`
- required `week`, `quiz_id`, `title`, `questions`
- structured single-answer multiple-choice question contract
- explicit and unique Question IDs
- deterministic question / choice ordering
- deterministic `week-{week:02d}/quiz/{quiz_id}/README.md`
- learner-facing README does not expose correct-answer data
- canonical `GenerationPlan` / `GenerationResult`
- dry-run / overwrite / manifest integration
- CLI `quiz` command and `list` / legacy `--list` exposure
- structured CLI input through `--questions-file` JSON
- contract, generator integration, template, and CLI integration tests
- no scoring / grading runtime
- no QuestionBank or randomization
- no accidental `generator.sdk` expansion

Merged implementation sequence:

```text
#49 design
#50 contract tests
#51 minimum implementation
#52 integration
```


#### Assignment Generator ✅

- ADR 0017 Accepted
- canonical generator name: `assignment`
- explicit Week-scoped `assignment_id`
- required `week`, `assignment_id`, `title`
- optional ordered `objectives`, `deliverables`, and `resources`
- optional authored `instructions` and `submission` guidance
- deterministic `week-{week:02d}/assignment/{assignment_id}/README.md`
- canonical `GenerationPlan` / `GenerationResult`
- dry-run / overwrite / manifest integration
- CLI `assignment` command and `list` / legacy `--list` exposure
- structured CLI input through `--content-file` JSON
- contract, template, generator integration, and CLI integration tests
- no grading / scoring / rubric runtime
- no submission backend
- no accidental `generator.sdk` expansion

Merged implementation sequence:

```text
#54 design
#55 contract tests
#56 minimum implementation
#57 integration
```


#### Slides Generator ✅

- ADR 0018 Accepted
- canonical generator name: `slides`
- required deck `title` and ordered `slides`
- deterministic canonical artifact `<target>/slides.md`
- canonical `GenerationPlan` / `GenerationResult`
- dry-run / overwrite / manifest integration
- canonical template `templates/slides/slides.md.j2`
- CLI `slides` command and `list` / legacy `--list` exposure
- structured CLI input through `--slides-file` JSON
- contract, template, generator integration, and CLI integration tests
- no PPTX / PDF / HTML rendering in the core generator
- no accidental `generator.sdk` expansion

Merged implementation sequence:

```text
#59 design
#60 contract tests
#61 minimum implementation
#62 integration
```


#### Website Generator ✅

- ADR 0019 Accepted
- canonical generator name: `website`
- required site `title` and ordered `pages`
- each page requires a safe relative `.html` path, non-empty title, and authored content
- required canonical entry page `index.html`
- deterministic multi-page output under `<target>/site/`
- deterministic navigation ordering derived from page ordering
- canonical `GenerationPlan` / `GenerationResult`
- dry-run / overwrite / manifest integration
- canonical template `templates/website/page.html.j2`
- CLI `website` command and `list` / legacy `--list` exposure
- structured CLI input through `--pages-file` JSON
- contract, template, generator integration, and CLI integration tests
- no hosting / deployment / CMS / asset pipeline in the core generator
- no accidental `generator.sdk` expansion

Merged implementation sequence:

```text
#64 design
#65 contract tests
#66 minimum implementation
#67 integration
```

### Step 5.4 — Courseware Composition Integration ✅

- ADR 0020 Accepted
- production `generator/courseware/composition.py`
- deterministic ordered `GenerateRequest` composition
- existing `GeneratorRegistry` preflight / resolution boundary
- canonical `BaseGenerator.run(request)` execution
- ordered `GenerationResult` aggregation
- fail-fast semantics without cross-generator rollback
- dry-run / overwrite propagation
- representative Course / Week / Lab / Quiz / Assignment / Slides / Website integration
- no public SDK expansion
- no composition CLI, parallel execution, or second manifest/plugin infrastructure

Merged implementation sequence:

```text
#69 design
#70 contract tests
#71 minimum implementation
#72 representative integration
```

### Step 5.5 — Representative E2E ✅

- `tests/integration/test_courseware_composition_e2e.py`
- production `CoursewareComposer` and production built-in generators
- representative Course / Week / Lab / Quiz / Assignment / Slides / Website flow
- exact artifact membership verification
- manifest generator provenance verification
- reproducible user-facing artifact verification
- composition-wide dry-run non-persistence
- PR #74

### Step 5.6 — Formal Milestone Acceptance ✅

- `docs/milestones/milestone-5-acceptance.md`
- roadmap / HISTORY / CHANGELOG alignment
- final full-regression and coverage baseline
- pre-commit / CI acceptance gates

## Acceptance and Closure

- `docs/milestones/milestone-5-acceptance.md`
- formal roadmap / HISTORY / CHANGELOG alignment
- representative E2E acceptance evidence
- full regression / coverage acceptance
- CI / pre-commit acceptance gates
- post-merge consistency alignment

Merged closure sequence:

```text
#74 representative E2E
#75 formal Milestone 5 acceptance
#76 post-merge consistency alignment
```

**Status:** Completed

------------------------------------------------------------------------

# Milestone 6 — AI Integration 🚧

目標：

在 Milestone 5 已穩定的 structured Courseware Domain、Composition、
GenerationPlan 與 Filesystem boundaries 上，加入可替換、可驗證、可測試的
AI capability，而不建立第二套 generation pipeline。

核心原則：

```text
AI proposes.
Domain validates.
Generator plans.
Filesystem commits.
Tests verify.
```

## Step 6.1 — AI Integration Architecture and Contract 🚧

目前進行中：

- `docs/architecture/ai-integration.md`
- ADR 0021 — AI Integration Contract (`Proposed`)
- Provider-independent `AIProvider` boundary design
- `AIRequest` / `AIResponse` conceptual contracts
- structured-output validation boundary
- Courseware Domain / Generator / Filesystem separation
- credential isolation
- deterministic `FakeAIProvider` testing strategy
- no real-provider dependency in core CI

## Planned Implementation Sequence

```text
Architecture / ADR
    ↓
AI core contract tests
    ↓
AIRequest / AIResponse / AIProvider
    ↓
FakeAIProvider
    ↓
Structured response validation
    ↓
AI-to-Courseware mapping
    ↓
AI-assisted Courseware generation
    ↓
AI Review
    ↓
Real Provider Adapter
    ↓
Representative AI E2E
    ↓
Milestone 6 Acceptance
```

## Planned Features

- AI-assisted Content Generation
- AI Review
- AI Documentation
- AI Template Completion
- AI Course Builder
- AI Refactoring Assistant

**Status:** Design In Progress

------------------------------------------------------------------------

# Milestone 7 — Marketplace

## Planned Features

- Template Packages
- Plugin Marketplace
- Community Repository
- Shared Generators
- Versioned Templates

------------------------------------------------------------------------

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

------------------------------------------------------------------------

# Definition of Done

每個 Milestone 完成時應符合：

- Architecture 完成
- Reference 完成
- Tests 通過
- Documentation 更新
- CI 通過
- pre-commit 通過
- CHANGELOG 更新
- 必要時新增 ADR
- Acceptance / Exit Criteria 有明確紀錄

------------------------------------------------------------------------

# Long-Term Vision

OpenProjectLab 最終目標是成為一個可持續演進的 **Project Engineering Platform**，
協助開發者建立高品質、可維護、可擴充且具有完整工程治理能力的專案，而不只是產生程式碼。

> **Build projects with engineering discipline, not just code generation.**
