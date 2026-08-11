# OpenProjectLab Open Courseware Platform Architecture

> Status: Active and Evolving
> Milestone: 5 — Open Courseware Platform
> Last updated: 2026-08-11
> Scope: Courseware domain model, composition, generators, templates, artifacts, extension points, testing, documentation, and acceptance
> Audience: Maintainers, contributors, courseware authors, Generator developers, Plugin developers, and tooling developers

OpenProjectLab（OPL）Milestone 5 的目標，是在已穩定的 Generator Core Framework 與 Plugin SDK 上，建立可組合、可測試、可擴充的 **Open Courseware generation platform**。

Milestone 5 不重新設計 Milestone 3 Generator lifecycle，也不重新設計 Milestone 4 Plugin runtime。它在既有 `GenerateRequest → validate_request → plan → execute → GenerationResult` 與 `generator.sdk` extension boundary 上，新增課程內容的 domain、composition 與 artifact contracts。

目前 maturity：

- **Implemented**：minimum production `Course` / `Week` domain models 與 contract tests。
- **Existing**：built-in `course` / `week` Generators 與 canonical lifecycle。
- **Proposed**：Learning Material model、Lab、Quiz、Assignment、PPT、Website、composition orchestration、courseware-specific SDK exposure。

Roadmap 的 Milestone 5 planned features 仍為 Course Templates、Week Templates、Lab Generator、Quiz Generator、Assignment Generator、PPT Generator 與 Website Generator。

---

## 1. Goals

- 將 Course、Week 與未來 Learning Material 建模為清楚、可測試的 domain concepts。
- 讓課程內容由多個 Generator 組合，而不是建立單一巨型 Generator。
- 保留既有 `course`、`week` Generator 與 canonical lifecycle。
- 建立 Lab、Quiz、Assignment、PPT、Website 的共同 architecture boundary。
- 分離 Domain、Generator、Template、Artifact 與 Filesystem responsibilities。
- 保留 dry run、overwrite、manifest、deterministic output 與 structured result。
- 讓 built-in 與 third-party Generator 未來可以共享 documented extension boundaries。
- 為 Milestone 6 AI Integration 提供 structured courseware contract。

## 2. Non-Goals

Milestone 5 不應：

- 重新定義 `BaseGenerator.run()` canonical lifecycle。
- 建立第二套 request/result contract。
- 重新定義 Milestone 4 Entry Point、validation、registry 或 loader。
- 讓 Template 成為 domain source of truth。
- 讓 CLI 成為 courseware business-rule owner。
- 建立 LMS、學生帳號、成績簿或 submission backend。
- 將 AI content generation 納入 Milestone 5 core runtime。
- 將 hosting provider、marketplace 或 remote publishing 寫死進 core。

## 3. Existing Foundation

### Milestone 3 — Generator Core

Milestone 5 保留：

- `GenerateRequest`
- `RuntimeOptions`
- `GeneratorValidationError`
- `GenerationOperation`
- `GenerationPlan`
- `GenerationResult`
- canonical `BaseGenerator.run()`
- `validate_request → plan → execute`
- dry-run / overwrite / manifest semantics

Existing built-in Generators：

```text
bootstrap
course
week
```

### Milestone 4 — Plugin Ecosystem

Milestone 5 保留：

- stable `generator.sdk`
- third-party Generator validation
- canonical `openprojectlab.generators` Entry Point group
- transactional discovery / validation / registration
- installed third-party distribution E2E proof

## 4. Architecture Principles

- **Design First**
- **Documentation First**
- **Automation First**
- **Testing First**
- **Composition over Monolith**

## 5. High-Level Architecture

```text
User / Automation
        ↓
CLI / Application Layer
        ↓
Courseware Specification
        ↓
Validated Courseware Domain
        ↓
Composition / Orchestration
        ↓
Generator Registry
        ↓
Courseware Generators
        ↓
GenerationPlan
        ↓
Templates / Renderers
        ↓
Courseware Artifacts
        ↓
Filesystem + Manifest
        ↓
GenerationResult
```

Dependencies：

- Domain 不依賴 CLI、Template 或 filesystem。
- Template 不擁有 domain validation。
- Generator 將 validated intent 轉成 `GenerationPlan`。
- Filesystem 保持 safety responsibility。
- Plugin Generator 依賴 documented public SDK，不依賴 private courseware implementation。

## 6. Courseware Domain Model

Current minimum implemented hierarchy：

```text
Course
  └── Week
```

Future conceptual hierarchy：

```text
Course
  └── Week
       └── Learning Material
            ├── Lecture
            ├── Lab
            ├── Quiz
            ├── Assignment
            ├── Slides
            └── Website Projection
```

`Course` / `Week` 已 Implemented。Learning Material 與其 subtypes 仍 Proposed。

## 7. Course Contract — Implemented

Production model：

```python
@dataclass(frozen=True, slots=True)
class Course:
    course_id: str
    title: str
    language: str
    weeks: tuple[Week, ...] = ()
```

Implemented invariants：

- `course_id` 非空並 normalization。
- `title` 不作為唯一 identity。
- weeks 強制 immutable tuple semantics。
- duplicate Week number rejected。
- Weeks 依 number deterministic ascending ordering。
- Course 不直接執行 generation。
- Course 不直接寫 filesystem。

Production location：

```text
generator/courseware/models.py
```

## 8. Week Contract — Implemented

Production model：

```python
@dataclass(frozen=True, slots=True)
class Week:
    number: int
    title: str
```

Implemented invariants：

- `number` 必須是 int。
- `bool` rejected。
- `number > 0`。
- title 不構成 canonical identity。
- output path 不構成 domain identity。
- immutable value semantics。

Existing Week Generator validation仍保留自己的 defensive validation。

## 9. Learning Material — Proposed

Learning Material 是 conceptual composition vocabulary。

Potential kinds：

```text
lecture
lab
quiz
assignment
slides
website
```

目前尚未建立：

- `LearningMaterial` production model
- base class
- enum
- protocol
- public SDK surface

不得將此 section 解讀成 implemented API。

## 10. Domain vs Artifact

Domain：

```text
Course
Week 03
```

Artifact：

```text
README.md
weeks/week-03/README.md
```

Future artifacts may include：

```text
weeks/week-03/lab/
weeks/week-03/quiz/
slides/week-03.pptx
site/week-03/index.html
```

Domain object 不等於 output path。

## 11. Courseware Specification

YAML/JSON 等只是 serialization/input boundary。

```text
raw configuration
    ↓
validated structured values
    ↓
courseware domain
    ↓
generator request
    ↓
GenerationPlan
```

## 12. Composition Boundary — Proposed

```text
Courseware Composition
    ↓
Course Generator
    ↓
Week Generator(s)
    ↓
Material Generator(s)
```

Orchestrator class 尚未實作，也不是目前 accepted API。

## 13. Generator Responsibility

每個 Courseware Generator 持續使用：

```text
validate_request
    ↓
plan
    ↓
execute
    ↓
GenerationResult
```

不建立 parallel lifecycle。

## 14. Generator Status

```text
course       Existing
week         Existing
lab          Proposed
quiz         Proposed
assignment   Proposed
ppt          Proposed
website      Proposed
```

Course/Week domain models implemented，不代表 Course/Week Generators 已被重寫。

## 15. Presentation / Material Features — Proposed

Lecture、Lab、Quiz、Assignment、PPT/Slides、Website 均仍為 Proposed。

PPT/Website 應是 projections，而不是 Course domain owner。

## 16. Template Boundary

Template 負責 presentation，不負責：

- domain identity
- Week validation
- Registry lookup
- filesystem mutation
- network fetch
- dependency installation

## 17. Artifact / Filesystem Boundary

Courseware output 繼續使用 existing：

- `GenerationOperation`
- `GenerationPlan`
- filesystem containment
- overwrite policy
- dry run
- manifest
- error semantics

## 18. Validation Layers

```text
Input / Configuration Validation
        ↓
Domain Validation
        ↓
Generator Request Validation
        ↓
Filesystem Safety Validation
```

Current implemented domain validation：

- non-empty Course identity
- valid Week number
- duplicate Week rejection

Material-level validation仍 Proposed。

## 19. Determinism

Implemented Course Weeks deterministic ordering：

```text
ascending Week.number
```

Future composition亦必須 deterministic。

## 20. Dry Run / Overwrite

Existing Generator dry-run / overwrite semantics remain canonical。

Course/Week domain models本身不執行 filesystem mutation。

## 21. Plugin Extension Boundary

ADR 0014 **沒有**新增 `Course` / `Week` 到 `generator.sdk`。

若未來 third-party courseware Generator 需要 stable domain types，必須另立 public SDK decision。

## 22. AI Boundary

Milestone 6 AI Integration 應依賴 structured courseware contracts，不應直接 mutation filesystem。

## 23. Testing Strategy

Current implemented contract tests cover：

- Course explicit identity
- empty identity rejection
- title != identity
- Week positive integer validation
- bool rejection
- duplicate Week rejection
- deterministic ordering
- immutable models
- existing Course/Week `GenerationPlan` boundary
- validation-before-planning
- dry-run mutation safety

Production tests：

```text
tests/courseware/test_domain_contract.py
```

Future Lab/Quiz/Assignment/PPT/Website tests 尚未存在。

## 24. Documentation Requirements

每個新增 feature 同步：

- architecture
- ADR when needed
- contract tests
- implementation
- reference / authoring docs
- Code Review Checklist
- CI / pre-commit / coverage

## 25. Current Milestone 5 Sequence

### Step 5.1 — Architecture ✅

Completed by architecture + ADR design PR。

### Step 5.2 — Minimum Domain Contract ✅

Completed baseline：

```text
PR #41 — contract tests
PR #42 — production Course / Week domain models
ADR 0014 — Accepted
```

### Step 5.3 — Material Generators

Next proposed sequence：

```text
Lab
Quiz
Assignment
```

### Step 5.4 — Presentation Projection

PPT/Slides contract。

### Step 5.5 — Website Projection

Static Website contract。

### Step 5.6 — Composition Integration

Course → Week → Materials → Projections。

### Step 5.7 — Milestone Acceptance

Representative E2E + docs + CI + coverage + acceptance record。

## 26. Architecture Invariants

1. Milestone 3 Generator lifecycle 不重新定義。
2. Milestone 4 Plugin runtime 不重新定義。
3. Course/Week domain 不依賴 CLI/filesystem。
4. Template 不擁有 domain validation。
5. `GenerationPlan` 保持 planning boundary。
6. Dry run / overwrite semantics 保持 canonical。
7. Plugin extension 不依賴 private courseware implementation。
8. Website/PPT 是 projection。
9. AI 不成為 Milestone 5 runtime dependency。
10. Proposed capabilities 不描述為 Implemented。

## 27. Code Review Checklist

### Architecture

- [ ] Change fits Milestone 5 scope.
- [ ] No Generator lifecycle redefinition.
- [ ] No Plugin runtime redefinition.
- [ ] Domain / Generator / Template / Artifact / Filesystem ownership is clear.
- [ ] Proposed features are not represented as implemented.

### Domain

- [ ] Course identity remains explicit.
- [ ] Week validation remains aligned with ADR 0014.
- [ ] Duplicate Week rejection remains.
- [ ] Week ordering remains deterministic.
- [ ] Domain models remain immutable.
- [ ] No infrastructure dependency enters domain models.

### Generator

- [ ] Existing `course` / `week` identities remain canonical.
- [ ] `GenerateRequest` / `GenerationPlan` / `GenerationResult` remain canonical.
- [ ] No unnecessary generator-specific result types.
- [ ] No CLI parsing in domain/generator internals.

### Plugins / SDK

- [ ] No accidental `generator.sdk` expansion.
- [ ] `openprojectlab.generators` remains canonical Entry Point.
- [ ] Public courseware SDK requires separate decision/tests/docs.

### Tests

- [ ] Domain contract tests pass.
- [ ] Existing Course/Week tests pass.
- [ ] Determinism and validation remain tested.
- [ ] Dry-run mutation safety remains tested.
- [ ] New feature gets contract + integration tests.

### Documentation

- [ ] Architecture synchronized.
- [ ] ADR synchronized.
- [ ] ADR index synchronized.
- [ ] Roadmap/HISTORY/CHANGELOG updated at appropriate stage.
- [ ] Authoring/reference docs updated when behavior becomes user-facing.

### Automation

- [ ] `git diff --check`
- [ ] `ruff check generator tests`
- [ ] `ruff format --check generator tests`
- [ ] targeted tests
- [ ] `pre-commit run --all-files`
- [ ] `python -m pytest`
- [ ] coverage gate
- [ ] CI green

## 28. Related Documents

- `docs/roadmap.md`
- `docs/architecture/generator.md`
- `docs/architecture/plugin-sdk-contract-inventory.md`
- `docs/adr/0010-plugin-sdk-public-contract.md`
- `docs/adr/0011-plugin-validation-contract.md`
- `docs/adr/0012-plugin-entry-point-contract.md`
- `docs/adr/0013-plugin-distribution-contract.md`
- `docs/adr/0014-open-courseware-domain-contract.md`
- `tests/courseware/test_domain_contract.py`
- `generator/courseware/models.py`

---

> **Milestone 5 現在已有第一個 production courseware domain boundary：Course / Week。下一步才是以這個 accepted domain contract 為基礎設計 Lab Generator，而不是擴張尚未需要的 domain hierarchy。**
