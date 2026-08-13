# OpenProjectLab 發展歷程（History）

## 專案起源

OpenProjectLab（OPL）最初的目標，是建立一套能快速產生專案骨架的工具。
隨著專案逐步發展，OPL 的定位逐漸由 Project Generator 演進為
**Project Engineering Platform**。

------------------------------------------------------------------------

# 發展理念

OPL 的核心理念：

- Design First
- Documentation First
- Automation First
- Testing First

------------------------------------------------------------------------

# 發展歷程

## Bootstrap / Generator / Configuration / Template / Upgrade Framework

OPL 逐步建立 project generation、configuration、Jinja2 templates、
upgrade/manifest/backup/rollback 與 repository quality/governance foundations。

------------------------------------------------------------------------

## Generator Core Framework（Milestone 3）

Milestone 3 將 Generator Framework 收斂為共享 canonical lifecycle：

```text
GenerateRequest
    ↓
validate_request
    ↓
plan
    ↓
execute
    ↓
GenerationResult
```

完成 `GenerateRequest`、`RuntimeOptions`、`GeneratorValidationError`、
`GenerationPlan`、`GenerationResult`、legacy lifecycle removal，以及
Bootstrap/Course/Week cross-generator contract tests。

------------------------------------------------------------------------

## Plugin SDK and Plugin Ecosystem（Milestone 4）

Milestone 4 建立 stable `generator.sdk`、Plugin validation、
`openprojectlab.generators` canonical Entry Point runtime、transactional
registration、legacy PluginManager removal、third-party example distribution，
並以真實 installed-distribution E2E 完成 acceptance。

Formal acceptance：

```text
docs/milestones/milestone-4-acceptance.md
452 passed
Coverage: 85.90%
```

------------------------------------------------------------------------

## Open Courseware Platform（Milestone 5）

Milestone 5 開始把 OPL 從一般 project engineering framework 擴充為
structured courseware generation platform。

### Step 5.1 — Architecture

建立：

```text
docs/architecture/open-courseware-platform.md
```

固定 Domain / Generator / Template / Artifact / Filesystem responsibility
boundaries，並保留 Milestone 3 Generator lifecycle 與 Milestone 4 Plugin
runtime。

### Step 5.2 — Course / Week Domain Contract

ADR 0014 定義並接受 minimum Course / Week domain contract。

Production：

```text
generator/courseware/models.py
```

完成 immutable `Course` / `Week` models、positive Week validation、bool
rejection、duplicate Week rejection 與 deterministic Week ordering。

### Step 5.3 — Lab Generator

Lab 是第一個 concrete Learning Material Generator vertical slice。

完整演進：

```text
PR #44 — docs: design lab generator contract
PR #45 — test: define lab generator contract
PR #46 — feat: implement lab generator contract
PR #47 — feat: integrate lab generator
```

ADR 0015 接受的核心 contract：

- canonical generator identity `lab`
- Lab 屬於單一 Week
- explicit `lab_id`
- minimum request values: `week`, `lab_id`, `title`
- deterministic `week-{week:02d}/lab/{lab_id}/README.md`
- canonical `GenerationPlan`
- canonical `GenerationResult`
- existing dry-run / overwrite / manifest semantics
- no Lab-specific result/plan types
- no `LearningMaterial` hierarchy
- no accidental `generator.sdk` expansion

Production / integration：

```text
generator/generators/lab_generator.py
templates/lab/README.md
generator/cli/main.py
```

Tests：

```text
tests/generators/test_lab_generator_contract.py
tests/generators/test_lab_generator_integration.py
tests/integration/test_lab_cli.py
```

Lab 已完成 design → contract tests → implementation → integration →
documentation acceptance 閉環。

### Step 5.4 — Quiz Generator

Quiz 是第二個 concrete Learning Material Generator vertical slice。

完整演進：

```text
PR #49 — docs: design quiz generator contract
PR #50 — test: define quiz generator contract
PR #51 — feat: implement quiz generator contract
PR #52 — feat: integrate quiz generator
```

ADR 0016 接受的核心 contract：

- canonical generator identity `quiz`
- Quiz 屬於單一 Week
- explicit Week-scoped `quiz_id`
- minimum request values: `week`, `quiz_id`, `title`, `questions`
- explicit/unique Question IDs
- ordered choices and deterministic rendering
- correct answer must resolve to one choice
- deterministic `week-{week:02d}/quiz/{quiz_id}/README.md`
- learner-facing artifact does not expose answer-key data
- canonical `GenerationPlan` / `GenerationResult`
- existing dry-run / overwrite / manifest semantics
- CLI structured input through `--questions-file` JSON
- no scoring/grading runtime, QuestionBank, randomization, or SDK expansion

Production / integration：

```text
generator/generators/quiz_generator.py
templates/quiz/README.md.j2
generator/cli/main.py
tests/generators/test_quiz_generator_contract.py
tests/generators/test_quiz_generator_integration.py
tests/integration/test_quiz_cli.py
```

Quiz 已完成 design → contract tests → implementation → integration →
documentation acceptance 閉環。


### Step 5.5 — Assignment Generator

Assignment 是第三個 concrete Week-scoped material Generator vertical slice。

完整演進：

```text
PR #54 — docs: design assignment generator contract
PR #55 — test: define assignment generator contract
PR #56 — feat: implement assignment generator contract
PR #57 — feat: integrate assignment generator
```

ADR 0017 接受的核心 contract：

- canonical generator identity `assignment`
- Assignment 屬於單一 Week
- explicit Week-scoped `assignment_id`
- minimum request values: `week`, `assignment_id`, `title`
- ordered objectives / deliverables / resources
- authored instructions / submission guidance
- deterministic `week-{week:02d}/assignment/{assignment_id}/README.md`
- canonical `GenerationPlan` / `GenerationResult`
- existing dry-run / overwrite / filesystem / manifest semantics
- CLI structured input through `--content-file` JSON
- no grading/scoring/rubric runtime or submission backend
- no Assignment-specific request/result hierarchy or SDK expansion

Production / integration：

```text
generator/generators/assignment_generator.py
templates/assignment/README.md.j2
generator/cli/main.py
tests/generators/test_assignment_generator_contract.py
tests/generators/test_assignment_generator_integration.py
tests/integration/test_assignment_cli.py
```

Assignment 已完成 design → contract tests → implementation → integration →
documentation acceptance 閉環。

------------------------------------------------------------------------

# 下一階段

Milestone 5 持續進行。

下一個 Milestone 5 vertical slice：

```text
PPT / Slides Generator
```

之後再進入 Website、composition integration 與
Milestone 5 acceptance。

------------------------------------------------------------------------

# 我們的願景

OpenProjectLab 的目標不是建立更多程式，而是建立：

> **更容易維護、更容易理解、更容易演進的軟體工程文化。**

> Build projects, not just code.
