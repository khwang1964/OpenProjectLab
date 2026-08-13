# OpenProjectLab Roadmap

> Status: Active
> Last Updated: 2026-08-13

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

目前焦點：

> **Milestone 5 — Open Courseware Platform**

Milestone 5 已完成 Course/Week foundation，以及 Lab、Quiz、Assignment 三個 material-generator vertical slices：

```text
Open Courseware Architecture
    ↓
ADR 0014 Course / Week Domain Contract
    ↓
Course / Week production domain models
    ↓
ADR 0015 Lab Generator Contract
    ↓
Lab contract tests
    ↓
LabGenerator
    ↓
Lab CLI / template / manifest integration
    ↓
Lab documentation acceptance
    ↓
ADR 0016 Quiz Generator Contract
    ↓
Quiz contract tests
    ↓
QuizGenerator
    ↓
Quiz CLI / template / manifest integration
    ↓
Quiz documentation acceptance
```

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

# Milestone 5 — Open Courseware Platform 🚧

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

#### Next

## Remaining Planned Features

- PPT / Slides Generator
- Website Generator
- composition integration
- Milestone 5 representative E2E and acceptance document

**Status:** In Progress

------------------------------------------------------------------------

# Milestone 6 — AI Integration

## Planned Features

- AI-assisted Content Generation
- AI Review
- AI Documentation
- AI Template Completion
- AI Course Builder
- AI Refactoring Assistant

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
