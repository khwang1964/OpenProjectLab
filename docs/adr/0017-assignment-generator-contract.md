# ADR 0017: Assignment Generator Contract

> Status: Proposed
> Date: 2026-08-13
> Milestone: 5 — Open Courseware Platform
> Step: 5.5A — Assignment Generator Contract Design
> Decision scope: canonical Assignment Generator identity, request values, validation, Week-scoped artifact layout, authored task structure, template boundary, planning/execution semantics, dry-run/overwrite behavior, manifest integration, determinism, and compatibility with existing Course/Week/Lab/Quiz contracts

## Context

OpenProjectLab（OPL）目前已完成：

```text
Milestone 3 — Generator Core Framework
Milestone 4 — Plugin Ecosystem
Milestone 5 / Step 5.1 — Open Courseware Platform Architecture
Milestone 5 / Step 5.2 — Minimum Course / Week Domain Contract
Milestone 5 / Step 5.3 — Lab Generator
Milestone 5 / Step 5.4 — Quiz Generator
```

ADR 0014 已接受 minimum production `Course` / `Week` domain models。

ADR 0015 與 ADR 0016 已建立兩個 concrete Week-scoped material Generator
vertical slices：

```text
Lab
Quiz
```

兩者共同證明 material-specific Generator 可以直接沿用 canonical lifecycle：

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

而不需要建立：

```text
LearningMaterial
Assessment
LabRequest
QuizRequest
LabPlan
QuizPlan
LabGenerationResult
QuizGenerationResult
```

等平行 abstraction。

Assignment 是下一個 learning material Generator。

Assignment 與 Lab / Quiz 有共同需求：

- 屬於明確 Week。
- 需要 explicit material identity。
- artifact layout 必須 deterministic。
- 必須使用 canonical Generator lifecycle。
- 必須遵守既有 dry-run、overwrite、filesystem 與 manifest semantics。
- template 不得擁有 business validation。
- 不應自動擴張 public Plugin SDK。

但 Assignment 也引入不同於 Quiz 的 authored-task concerns：

- learning objectives
- assignment instructions
- deliverables
- submission guidance
- optional resources
- deterministic ordering of structured sections

Assignment 第一版的責任是產生教材 artifact，而不是建立 submission/grading runtime。

如果沒有先固定 Assignment contract，直接實作容易造成：

- Assignment identity 被 title 或 output path 隱式決定。
- Assignment 被誤建模為 Quiz/Assessment subtype。
- deliverables 與 instructions 被 Template 格式反向決定。
- Generator 自行建立新的 request/result hierarchy。
- submission backend、grading、rubric engine 過早進入 Generator contract。
- Lab / Quiz / Assignment material conventions 分裂。
- courseware internal models 被誤當成 plugin-facing SDK。

因此，Assignment Generator 必須先以獨立 ADR 固定 minimum contract。

---

## Decision Drivers

1. 保護 Milestone 3 canonical Generator lifecycle。
2. 保護 ADR 0014 Course / Week domain invariants。
3. 延續 ADR 0015 / ADR 0016 material-generator pattern。
4. 明確分離 authored assignment content、presentation、planning 與 execution。
5. 讓 Assignment identity deterministic。
6. 讓 structured assignment sections 的 ordering deterministic。
7. 保持 dry-run / overwrite / manifest semantics。
8. 避免第一版引入 submission backend、grading engine 或 rubric engine。
9. 避免過早建立 `LearningMaterial` inheritance hierarchy。
10. 避免 accidental `generator.sdk` expansion。
11. 讓 contract 可以在 implementation 前由 automated tests 固定。
12. 為後續 composition / course assembly 建立一致 material contract。

---

## Decision

OPL 採用以下 Assignment Generator Contract。

### 1. Canonical Generator Identity

Assignment Generator canonical name：

```text
assignment
```

Production class 預期名稱：

```text
AssignmentGenerator
```

此名稱屬 built-in Generator identity，不代表 public SDK symbol。

不得建立平行 canonical identities：

```text
homework
exercise
task
week-assignment
assignment-v2
```

---

### 2. Assignment Belongs to One Week

Assignment 是 Week-scoped learning material。

Conceptual relationship：

```text
Course
  └── Week
       ├── Lab
       ├── Quiz
       └── Assignment
```

Assignment 不成為新的 root aggregate。

Invocation 必須明確提供 Week identity。

不得由 current working directory、template path、output basename、previous
generator invocation 或 implicit sequence 推測 Week。

---

### 3. Assignment Identity Is Explicit Within a Week

第一版採 explicit：

```text
assignment_id
```

Conceptual identity：

```text
(Course scope, Week number, assignment_id)
```

單次 request 至少必須提供：

```text
week
assignment_id
title
```

`title` 是 display metadata，不構成 canonical identity。

`assignment_id` 是 machine-oriented identity，scope 為 Week。

本 ADR 不要求 `assignment_id` 在整個 Course 中 globally unique。

---

### 4. GenerateRequest Remains the Input Boundary

Assignment Generator 不建立新的 request type。

Canonical request：

```python
GenerateRequest(
    generator_name="assignment",
    target=...,
    values={
        "week": 4,
        "assignment_id": "streams-homework",
        "title": "Streams Homework",
        "objectives": (...),
        "instructions": "...",
        "deliverables": (...),
        ...,
    },
    options=RuntimeOptions(...),
)
```

Required values：

```text
week
assignment_id
title
```

Optional structured values 初始可包括：

```text
course_name
objectives
instructions
deliverables
resources
submission
template
record_manifest
```

只有 tests 與 implementation 實際支援的 optional values 才屬 implemented
contract。

不得建立：

```text
AssignmentRequest
AssignmentGenerateRequest
LearningTaskRequest
```

作為 canonical invocation type。

---

### 5. Week Validation Aligns with ADR 0014

`week`：

- 必須是 `int`
- `bool` rejected
- 必須 `> 0`

Assignment Generator 必須在 request validation boundary 防禦性驗證。

---

### 6. Assignment ID Validation

`assignment_id`：

- 必須是 string
- trim 後不可為空
- 不得具有 absolute path semantics
- 不得包含 `..` path traversal component
- 不得使用 path separator 建立 nested artifact layout
- 不由 title 自動推導 canonical identity

推薦 machine-readable format：

```text
streams-homework
collections-assignment
concurrency-practice
```

若已有 canonical normalization/path-safety utility，implementation 應優先 reuse。

---

### 7. Title Validation

`title`：

- 必須是 string
- trim 後不可為空
- 是 display metadata
- 不參與 Assignment identity
- 不直接決定 output path

修改 title 不應改變 canonical artifact location。

---

### 8. Assignment Content Is Authored Input

Assignment Generator 的責任是：

```text
validate
plan
render
execute
```

不是：

```text
invent assignment tasks
infer learning objectives
generate solutions
grade submissions
score learners
```

若未來由 AI/composition layer 產生 Assignment content：

```text
AI/content composition
        ↓
validated Assignment request
        ↓
AssignmentGenerator
```

content authoring 與 deterministic artifact generation 必須維持不同 responsibility。

---

### 9. Objectives Are Optional Ordered Content

若提供 `objectives`：

- 必須是 finite ordered collection
- 每一項必須是 non-empty string
- ordering 必須保留
- Generator 不得自動排序
- Template 不得自行重排

相同 request 必須產生相同 objective ordering。

第一版不要求建立 Objective domain class。

---

### 10. Instructions Are Optional Authored Content

若提供 `instructions`：

- 必須是 string
- trim 後不可為空
- 是 learner-facing authored content
- 不構成 Assignment identity
- 不影響 canonical artifact path

Generator 不負責改寫或補完 instructions。

---

### 11. Deliverables Are Optional Ordered Content

若提供 `deliverables`：

- 必須是 finite ordered collection
- 每一項必須是 non-empty string
- ordering 必須保留
- Generator 不得自動排序或 deduplicate

Deliverable ordering 屬 authored content semantics。

第一版不要求建立 Deliverable domain class。

---

### 12. Resources Are Optional Ordered References

若 implementation 支援 `resources`：

- 必須是 finite ordered collection
- 每一項至少必須可 deterministically render
- ordering 必須保留
- Generator 不負責下載或解析 remote resource
- remote availability 不屬 generation contract

第一版可以只支援 string references。

更豐富的 resource model 必須由 follow-up ADR 定義。

---

### 13. Submission Guidance Is Content, Not a Submission Backend

若 implementation 支援 `submission`：

- 它是 learner-facing guidance/content
- 不代表 OPL 接收學生 submission
- 不建立 upload endpoint
- 不建立 LMS integration
- 不建立 submission persistence
- 不建立 due-date scheduler

第一版可將 submission guidance 表示為 non-empty string。

---

### 14. Artifact Layout Is Deterministic

第一版 Assignment artifact root：

```text
week-{week:02d}/assignment/{assignment_id}/
```

Required learner-facing artifact：

```text
README.md
```

Canonical primary destination：

```text
<target>/week-{week:02d}/assignment/{assignment_id}/README.md
```

Example：

```text
week-04/
  assignment/
    streams-homework/
      README.md
```

Artifact path 必須由：

```text
validated week
+
validated assignment_id
```

決定。

不得由 title、deliverable count、template filename 或 current directory 決定。

---

### 15. Default Template Boundary

Default template：

```text
assignment/README.md.j2
```

Template 是 presentation boundary。

Template 不負責：

- Week validation
- Assignment ID validation
- path safety
- structured collection validation
- overwrite decisions
- artifact ownership
- filesystem mutation
- manifest mutation

---

### 16. Template Context

Recommended structured context：

```python
{
    "week": {
        "number": 4,
    },
    "assignment": {
        "id": "streams-homework",
        "title": "Streams Homework",
        "objectives": (...),
        "instructions": "...",
        "deliverables": (...),
        "resources": (...),
        "submission": "...",
    },
}
```

Implementation 可以在既有 renderer constraints 下使用 flat mapping。

但 template-author-facing keys 一旦成為 tested/documented contract，就不得無意變更。

---

### 17. Validation Happens Before Planning Mutation

`validate_request()` 至少驗證：

```text
generator_name == "assignment"
valid template root according to existing conventions
valid week
valid assignment_id
valid title
optional objectives shape
optional instructions shape
optional deliverables shape
optional resources shape if implemented
optional submission shape if implemented
```

Invalid request：

```text
validate_request
    ✕
plan not called
execute not called
filesystem unchanged
```

---

### 18. Planning Uses Canonical GenerationPlan

Assignment Generator 必須實作：

```python
plan(request: GenerateRequest) -> GenerationPlan
```

不得建立：

```text
AssignmentPlan
AssignmentGenerationPlan
LearningTaskPlan
```

作為 canonical planning type。

Minimum plan：

```text
GenerationPlan
  generator_name = "assignment"
  target = request.target
  artifacts =
    week-04/assignment/streams-homework/README.md
```

若未來增加 solution/rubric 等 artifact，必須先有明確 contract。

---

### 19. Execution Uses Canonical GenerationResult

`execute(plan, request)`：

```text
GenerationPlan
    ↓
render
    ↓
filesystem write
    ↓
manifest update
    ↓
GenerationResult
```

不得建立：

```text
AssignmentResult
AssignmentGenerationResult
LearningTaskResult
```

作為 built-in canonical result。

---

### 20. Dry-Run Has No Side Effects

若：

```text
request.options.dry_run == True
```

則：

```text
validate
plan
predict result
```

可以發生。

不得發生：

```text
mkdir
write README.md
write manifest
overwrite file
```

Dry-run result 必須仍是 canonical `GenerationResult`。

---

### 21. Overwrite Semantics Reuse Existing Contract

Assignment Generator 不建立自己的 overwrite policy。

沿用：

```text
RuntimeOptions.overwrite
```

若 artifact 已存在且 overwrite disabled：

```text
fail
```

若 overwrite enabled：

```text
replace according to canonical filesystem semantics
```

不得自動 rename：

```text
assignment-2
assignment-copy
assignment-new
```

---

### 22. Manifest Integration Reuses Existing Schema

若：

```text
record_manifest == True
```

且非 dry-run，Assignment Generator 應使用既有 manifest infrastructure。

不得建立：

```text
assignment-manifest.yaml
```

或 Assignment-specific manifest subsystem。

Recommended metadata：

```yaml
generator: assignment
metadata:
  week: 4
  assignment_id: streams-homework
  title: Streams Homework
```

metadata 必須保持：

```text
serializable
minimal
stable
```

不應將完整 instructions、deliverables 或 resources 複製進 manifest。

---

### 23. Determinism Is Required

相同：

```text
request
template set
filesystem state
```

必須產生相同：

```text
artifact paths
artifact ordering
objective ordering
deliverable ordering
resource ordering
rendered content
manifest metadata
```

Assignment Generator 不得：

- randomize sections
- 自動 shuffle deliverables
- 使用 current time 決定 artifact path
- 使用 UUID 決定 canonical identity
- 依 filesystem enumeration 決定 ordering

---

### 24. Assignment Does Not Introduce a Grading Runtime

第一版 Assignment Generator 不負責：

```text
student submissions
grading
scoring
rubric evaluation
late policy execution
deadline enforcement
feedback workflow
LMS synchronization
```

這些屬 future assessment/submission architecture。

即使 Assignment README 包含 submission guidance，也不表示上述 runtime 已實作。

---

### 25. Rubric and Solution Artifacts Remain Future Work

第一版 minimum artifact contract 只要求：

```text
README.md
```

以下能力保持 Proposed：

```text
RUBRIC.md
SOLUTION.md
starter-code packaging
submission schema
automated grading config
```

若未來需要，應由 follow-up ADR 固定 visibility、ownership 與 artifact semantics。

---

### 26. No LearningMaterial Hierarchy Yet

本 ADR 不建立：

```text
LearningMaterial
Assessment
AssignmentMaterial
TaskMaterial
```

production inheritance hierarchy。

目前保持：

```text
Course
Week
```

為 minimum domain model。

Material-specific behavior 仍由 Generator contract 表達。

---

### 27. No Automatic Public SDK Expansion

Assignment Generator implementation 不得因 built-in feature 自動修改：

```text
generator.sdk
```

public contract。

除非 follow-up ADR 明確決定，否則：

```text
AssignmentGenerator
Assignment
Deliverable
Rubric
```

不自動成為 public plugin-facing symbols。

---

### 28. CLI Integration Follows Existing Pattern

當 Assignment CLI integration 實作時，預期 command shape：

```text
opl assignment <project_slug>
  --week <N>
  --assignment-id <ID>
  --title <TITLE>
  ...
```

structured content 的 CLI transport 應保持 deterministic 且可測試。

若 objectives / deliverables 等資料超出適合 inline flags 的複雜度，
implementation 可採 explicit structured input file，但其格式必須由 tests 固定。

CLI 不得重新實作 Assignment business validation。

---

### 29. Failure Atomicity Reuses Existing Infrastructure

Assignment Generator 不建立新的 transaction subsystem。

應 reuse：

```text
validation-before-plan
plan-before-execute
filesystem abstraction
manifest abstraction
existing failure semantics
```

若未來 multi-artifact Assignment 需要更強 transaction guarantee，應由 filesystem /
generation execution contract 層處理，而不是 Assignment-specific workaround。

---

### 30. Compatibility With Existing Generators

Assignment implementation 不得破壞：

```text
BootstrapGenerator
CourseGenerator
WeekGenerator
LabGenerator
QuizGenerator
plugin loading
plugin validation
public SDK
```

Assignment 是 additive built-in material Generator。

---

## Canonical Flow

Assignment Generator canonical flow：

```text
GenerateRequest
      ↓
validate_request
      ↓
validated week / assignment_id / title / authored content
      ↓
plan
      ↓
GenerationPlan
      ↓
render assignment/README.md.j2
      ↓
execute
      ↓
filesystem
      ↓
manifest
      ↓
GenerationResult
```

---

## Example Request

```python
request = GenerateRequest(
    generator_name="assignment",
    target=course_root,
    values={
        "week": 4,
        "assignment_id": "streams-homework",
        "title": "Streams Homework",
        "objectives": (
            "Use stream pipelines to transform collections.",
            "Choose appropriate terminal operations.",
        ),
        "instructions": "Complete the tasks and submit the requested files.",
        "deliverables": (
            "src/main/java/example/StreamsHomework.java",
            "README.md",
        ),
        "record_manifest": True,
    },
    options=RuntimeOptions(
        dry_run=False,
        overwrite=False,
    ),
)
```

Expected primary artifact：

```text
week-04/assignment/streams-homework/README.md
```

---

## Validation Examples

### Valid

```text
week = 4
assignment_id = streams-homework
title = Streams Homework
```

### Invalid Week

```text
week = 0
week = -1
week = True
```

### Invalid Assignment ID

```text
assignment_id = ""
assignment_id = "../escape"
assignment_id = "nested/path"
```

### Invalid Title

```text
title = ""
title = "   "
```

### Invalid Objectives

```text
objectives = "single string instead of collection"
objectives = ("valid", "")
```

### Invalid Deliverables

```text
deliverables = 3
deliverables = ("README.md", "   ")
```

---

## Alternatives Considered

### Alternative A — Reuse Quiz Generator

Rejected。

Assignment 是 authored learning task，不是 single-answer assessment artifact。

---

### Alternative B — Model Assignment as Lab subtype

Rejected。

Lab 的 hands-on activity semantics 與 Assignment 的 authored deliverable/submission
guidance 不應以 inheritance 強制耦合。

---

### Alternative C — Introduce LearningMaterial Base Class Now

Rejected for Milestone 5 minimum scope。

Lab、Quiz、Assignment 三個 vertical slices 可以先提供足夠 evidence，再決定是否值得
抽象共同 production model。

---

### Alternative D — Introduce AssignmentRequest / AssignmentResult

Rejected。

這會破壞 Milestone 3 canonical request/result contract。

---

### Alternative E — Add Submission and Grading Backend in First Version

Rejected。

這會把 deterministic artifact generation 與 learner runtime 混合。

---

### Alternative F — Make Rubric Mandatory

Rejected。

Rubric 並非所有 Assignment 的 minimum requirement，且 rubric evaluation semantics 尚未
定義。

---

### Alternative G — Derive assignment_id From Title

Rejected。

Title 是 mutable display metadata，不適合作 canonical identity。

---

## Consequences

### Positive

- Assignment identity 明確且 deterministic。
- 延續 Lab / Quiz material-generator architecture。
- 不破壞 canonical Generator lifecycle。
- authored content 與 artifact generation responsibility 分離。
- dry-run / overwrite / manifest semantics 一致。
- structured section ordering 可測試。
- 不會過早引入 grading/submission runtime。
- 不會 accidental 擴張 public SDK。
- 為後續 composition 與 course assembly 提供第三個 concrete material pattern。

### Negative

- 第一版不提供 submission backend。
- 第一版不提供 grading/rubric engine。
- 第一版不提供 starter-code packaging contract。
- 第一版不建立 reusable LearningMaterial abstraction。
- richer structured content 可能需要後續 ADR。

### Accepted Trade-off

OPL 優先選擇：

```text
small deterministic authored-material contract
```

而不是：

```text
premature assignment platform abstraction
```

---

## Migration Plan

### Phase 1 — Contract Tests

新增：

```text
tests/generators/test_assignment_generator_contract.py
```

先固定：

- canonical identity
- required request values
- validation
- deterministic path
- structured optional content semantics
- canonical plan/result
- dry-run
- overwrite
- manifest metadata
- determinism
- SDK non-expansion

### Phase 2 — Minimum Implementation

新增：

```text
generator/generators/assignment_generator.py
templates/assignment/README.md.j2
```

只實作 contract tests 所要求的 minimum behavior。

### Phase 3 — Integration

整合：

```text
generator/cli/main.py
built-in generator list
real template rendering
real filesystem
manifest
dry-run
overwrite
```

新增：

```text
tests/generators/test_assignment_generator_integration.py
tests/integration/test_assignment_cli.py
```

### Phase 4 — Documentation Acceptance

更新：

```text
docs/adr/0017-assignment-generator-contract.md
docs/adr/README.md
docs/architecture/open-courseware-platform.md
docs/roadmap.md
docs/HISTORY.md
CHANGELOG.md
```

完成 regression / CI 後，將 ADR 0017：

```text
Proposed
```

改為：

```text
Accepted
```

---

## Test Strategy

### Contract Tests

至少覆蓋：

- generator name is `assignment`
- generator name mismatch rejected
- Week positive integer validation
- bool Week rejected
- Assignment ID required
- blank Assignment ID rejected
- path-like Assignment ID rejected
- title required
- blank title rejected
- optional objectives validation
- optional instructions validation
- optional deliverables validation
- deterministic objective/deliverable ordering
- deterministic artifact path
- canonical `GenerationPlan`
- canonical `GenerationResult`
- dry-run no side effects
- overwrite behavior
- manifest integration
- deterministic repeated planning
- no Assignment-specific request/plan/result types
- no accidental SDK expansion

### Integration Tests

至少覆蓋：

```text
real template
real renderer
real filesystem
real manifest
CLI list
CLI assignment command
dry-run
overwrite
invalid request error translation
```

### Regression Tests

必須保持：

```text
Course tests green
Week tests green
Lab tests green
Quiz tests green
Plugin tests green
SDK tests green
CLI tests green
full pytest green
ruff green
pre-commit green
coverage gate green
```

---

## Documentation Changes

本 ADR Proposed 階段同步：

```text
docs/adr/0017-assignment-generator-contract.md
docs/adr/README.md
```

implementation / acceptance 階段再同步：

```text
docs/architecture/open-courseware-platform.md
docs/roadmap.md
docs/HISTORY.md
CHANGELOG.md
```

在 implementation 完成前，不得將 Assignment 標示為 Implemented。

---

## Rollback Plan

若 Assignment implementation 發現 contract 不足：

1. 保留 ADR 0017 作為歷史設計紀錄。
2. 在尚未 Accepted 前可修訂 Proposed contract。
3. 若已 Accepted，使用 follow-up ADR supersede，不直接改寫歷史決策。
4. 移除未接受的 Assignment implementation 時，不得破壞 canonical generator
   lifecycle。
5. 不以 rollback 為理由引入 Assignment-specific request/result compatibility layer。

---

## Code Review Checklist

### Architecture

- [ ] `assignment` 是唯一 canonical Assignment Generator identity。
- [ ] Assignment 明確屬於一個 Week。
- [ ] Assignment identity 使用 explicit `assignment_id`。
- [ ] 未建立 `LearningMaterial` / `AssignmentMaterial` hierarchy。
- [ ] 未建立 Assignment-specific request / plan / result hierarchy。
- [ ] 未把 submission/grading runtime 放進 Generator。

### Validation

- [ ] `week` 驗證符合 ADR 0014。
- [ ] `bool` Week rejected。
- [ ] `assignment_id` 為 non-empty safe string。
- [ ] path traversal / nested path rejected。
- [ ] `title` 為 non-empty string。
- [ ] optional structured collections 若支援則有明確 validation。
- [ ] invalid request 在 filesystem mutation 前失敗。

### Planning / Execution

- [ ] 使用 canonical `GenerationPlan`。
- [ ] 使用 canonical `GenerationResult`。
- [ ] artifact path deterministic。
- [ ] dry-run 無 side effects。
- [ ] overwrite semantics reuse existing infrastructure。
- [ ] manifest reuse existing schema。
- [ ] structured ordering deterministic。

### Template

- [ ] default template 為 `assignment/README.md.j2`。
- [ ] Template 只負責 presentation。
- [ ] Template 不負責 validation / path / filesystem policy。
- [ ] template context 有 tests 固定。

### Compatibility

- [ ] Bootstrap / Course / Week / Lab / Quiz regression green。
- [ ] Plugin tests green。
- [ ] SDK tests green。
- [ ] CLI tests green。
- [ ] 無 accidental `generator.sdk` expansion。

### Documentation / Automation

- [ ] ADR index 已加入 0017。
- [ ] contract tests 在 implementation 前建立。
- [ ] integration tests 覆蓋 real template/filesystem/manifest。
- [ ] architecture / roadmap / HISTORY / CHANGELOG 在 acceptance 時同步。
- [ ] pre-commit 與 CI 全綠後才接受 ADR。

---

## Status

**Proposed**

ADR 0017 defines the Assignment Generator contract before implementation.

Acceptance requires:

```text
contract tests
    ↓
AssignmentGenerator implementation
    ↓
template integration
    ↓
CLI integration
    ↓
full regression suite
    ↓
documentation synchronization
```

Only after those gates pass should ADR 0017 become **Accepted**.
