# ADR 0016: Quiz Generator Contract

> Status: Proposed
> Date: 2026-08-13
> Milestone: 5 — Open Courseware Platform
> Step: 5.4A — Quiz Generator Contract Design
> Decision scope: canonical Quiz Generator identity, request values, validation, assessment artifact layout, template boundary, answer-key representation, planning/execution semantics, dry-run/overwrite behavior, manifest integration, determinism, and compatibility with existing Course/Week/Lab contracts

## Context

OpenProjectLab（OPL）目前已完成：

```text
Milestone 3 — Generator Core Framework
Milestone 4 — Plugin Ecosystem
Milestone 5 / Step 5.1 — Open Courseware Platform Architecture
Milestone 5 / Step 5.2 — Minimum Course / Week Domain Contract
Milestone 5 / Step 5.3 — Lab Generator
```

ADR 0014 已接受 minimum production `Course` / `Week` domain models，並將 Quiz 定義為後續的 Week-scoped assessment artifact。

ADR 0015 已建立第一個 learning-material Generator pattern：

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

Lab Generator 已證明 material-specific generator 不需要重新建立：

```text
LabRequest
LabPlan
LabGenerationResult
LearningMaterial
```

等平行 abstraction。

Quiz 是下一個 learning material generator。

Quiz 與 Lab 有共同需求：

- 屬於明確 Week。
- 需要 explicit material identity。
- artifact layout 必須 deterministic。
- 必須使用 canonical Generator lifecycle。
- 必須遵守既有 dry-run、overwrite、filesystem 與 manifest semantics。
- template 不得擁有 business validation。
- 不應自動擴張 public Plugin SDK。

但 Quiz 也首次引入 assessment-specific concerns：

- questions
- answer choices
- correct answers
- explanations
- answer-key visibility
- deterministic question ordering

如果沒有先固定 Quiz contract，直接實作容易造成：

- Quiz identity 被 title 或 output path 隱式決定。
- Question representation 被 Template 格式反向決定。
- answer key 與 learner-facing artifact 混合。
- Quiz Generator 自行建立新的 request/result types。
- 問題順序受到 randomization 或 mapping ordering 影響。
- scoring、grading、question bank、adaptive testing 過早進入 Generator contract。
- Lab 與 Quiz material conventions 分裂。
- courseware internal models 被誤當成 plugin-facing SDK。

因此，Quiz Generator 必須先以獨立 ADR 固定 minimum contract。

---

## Decision Drivers

1. 保護 Milestone 3 canonical Generator lifecycle。
2. 保護 ADR 0014 Course / Week domain invariants。
3. 延續 ADR 0015 已建立的 material-generator pattern。
4. 明確分離 assessment content、presentation、artifact planning 與 execution。
5. 讓 Quiz identity 與 Question identity deterministic。
6. 讓 learner-facing artifact 與 answer-key semantics 明確。
7. 保持 dry-run / overwrite / manifest semantics。
8. 避免在第一版引入 scoring engine、question bank 或 adaptive testing。
9. 避免過早建立 `LearningMaterial` / `Assessment` inheritance hierarchy。
10. 避免 accidental `generator.sdk` expansion。
11. 讓 contract 可以在 implementation 前由 automated tests 固定。
12. 為後續 Assignment / assessment tooling 建立一致先例。

---

## Decision

OPL 採用以下 Quiz Generator Contract。

### 1. Canonical Generator Identity

Quiz Generator canonical name：

```text
quiz
```

Production class 預期名稱：

```text
QuizGenerator
```

此名稱屬 built-in Generator identity，不代表 public SDK symbol。

不得建立以下平行 canonical identities：

```text
assessment
test
week-quiz
course-quiz
quiz-v2
```

---

### 2. Quiz Belongs to One Week

Quiz 是 Week-scoped assessment material。

Conceptual relationship：

```text
Course
  └── Week
       ├── Lab
       └── Quiz
```

Quiz 不成為新的 root aggregate。

Quiz invocation 必須明確提供 Week identity。

不得由以下資訊推測 Week：

- current working directory
- output directory basename
- template path
- filesystem enumeration
- previous generator invocation
- implicit sequence number

---

### 3. Quiz Identity Is Explicit Within a Week

第一版 Quiz contract 採 explicit：

```text
quiz_id
```

Conceptual identity：

```text
(Course scope, Week number, quiz_id)
```

單次 Quiz Generator request 至少必須提供：

```text
week
quiz_id
title
questions
```

`title` 不構成 canonical Quiz identity。

`quiz_id` 是 machine-oriented identity。

Quiz identity scope 為 Week。

本 ADR 不要求 `quiz_id` 在整個 Course 中 globally unique。

---

### 4. GenerateRequest Remains the Input Boundary

Quiz Generator 不建立新的 request type。

Canonical request：

```python
GenerateRequest(
    generator_name="quiz",
    target=...,
    values={
        "week": 3,
        "quiz_id": "streams-basics",
        "title": "Streams Basics Quiz",
        "questions": (...),
        ...
    },
    options=RuntimeOptions(...),
)
```

Required values：

```text
week
quiz_id
title
questions
```

Optional values 初始可包括：

```text
instructions
answer_key
template
record_manifest
```

但 optional values 只有在 tests 與 implementation 實際支援後，才屬 implemented contract。

Quiz Generator 不建立：

```text
QuizGenerateRequest
QuizRequest
AssessmentRequest
```

作為 canonical invocation type。

---

### 5. Week Validation Aligns with ADR 0014

`week`：

- 必須是 `int`
- `bool` rejected
- 必須 `> 0`

Quiz Generator 必須在 request validation boundary 防禦性驗證 Week value。

這不取代 production `Week` domain model，也不要求 request 直接攜帶 `Week` instance。

---

### 6. Quiz ID Validation

`quiz_id`：

- 必須是 string
- trim 後不可為空
- 不得具有 absolute path semantics
- 不得包含 `..` path traversal component
- 不得使用 path separator 建立 nested artifact layout
- 不由 title 自動推導作為 canonical identity

推薦 machine-readable format：

```text
streams-basics
collections-review
concurrency-checkpoint
```

本 ADR 不要求建立新的 global slug utility。

若已有 canonical normalization utility，implementation 應優先 reuse。

---

### 7. Title Validation

`title`：

- 必須是 string
- trim 後不可為空
- 是 display metadata
- 不參與 Quiz identity
- 不直接決定 output path

修改 title 不應改變 Quiz canonical artifact location。

---

### 8. Questions Are Explicit Input

Quiz 第一版必須以 explicit question collection 作為輸入。

Conceptual representation：

```python
questions = (
    {
        "id": "q1",
        "prompt": "...",
        "choices": (...),
        "correct_answer": "...",
        "explanation": "...",
    },
    ...
)
```

本 ADR 固定 question semantics，但不要求立即建立 public `Question` domain class。

第一版 minimum Question contract：

```text
id
prompt
choices
correct_answer
```

`explanation` 可以是 optional。

只有 implementation 與 tests 實際支援的欄位屬 implemented contract。

---

### 9. Question Identity Is Explicit Within a Quiz

每一個 Question 必須具有 explicit：

```text
id
```

Conceptual identity：

```text
(quiz_id, question_id)
```

Question ID：

- 必須為 string
- trim 後不可為空
- 在同一 Quiz 中必須 unique
- 不由 question position 隱式決定
- 不由 prompt text 產生 canonical identity

例如：

```text
q1
q2
streams-01
reduce-01
```

Question ordering 與 Question identity 是不同概念。

重新排序 Question 不得改變 Question identity。

---

### 10. Duplicate Question IDs Are Invalid

同一 Quiz 不得包含：

```text
q1
q1
```

兩個 Question。

Duplicate Question ID 必須在 planning/filesystem mutation 前被拒絕。

不得採：

```text
last one wins
```

或靜默覆寫方式。

---

### 11. Question Prompt Validation

`prompt`：

- 必須是 string
- trim 後不可為空
- 是 learner-facing content
- 不構成 Question identity

Template 可以決定 prompt 的 Markdown presentation。

Template 不負責判斷 prompt 是否存在。

---

### 12. First Version Uses Single-Answer Multiple Choice

Quiz Generator 第一版 minimum assessment shape 採：

```text
single-answer multiple-choice
```

每個 Question 至少有：

```text
id
prompt
choices
correct_answer
```

本 ADR 不要求第一版支援：

- multi-select
- true / false special type
- fill-in-the-blank
- free response
- coding assessment
- file upload
- rubric scoring
- partial credit

未來如有需求，可由 follow-up ADR 擴充 question type contract。

---

### 13. Choices Must Be Deterministic

`choices`：

- 必須是 finite ordered collection
- 至少包含兩個 choices
- choice ordering 必須保留
- Generator 不得自動 randomize
- Template 不得自行 shuffle

相同 request 必須得到相同 choice ordering。

第一版 contract 不要求 randomization。

---

### 14. Correct Answer Must Resolve to One Choice

`correct_answer` 必須唯一對應 `choices` 中的一個 choice。

不得接受：

- missing correct answer
- answer 不存在於 choices
- ambiguous equivalent key
- multiple correct answers under single-answer contract

Invalid correct answer 必須在 generation mutation 前失敗。

本 ADR 不固定未來 multi-answer representation。

---

### 15. Explanation Is Optional Presentation Content

Question 可以提供：

```text
explanation
```

若存在：

- 必須是 string
- 可用於 answer-key artifact
- 不構成 Question identity
- 不影響 canonical artifact path

Quiz Generator 不負責產生新的 explanation content。

---

### 16. Generator Does Not Author Questions

Quiz Generator 的責任是：

```text
validate
plan
render
execute
```

不是：

```text
invent questions
generate distractors
infer correct answers
rewrite questions
grade learners
```

若未來 AI 產生 Quiz Content：

```text
AI/content composition
        ↓
validated Quiz request
        ↓
QuizGenerator
```

AI authoring 與 deterministic artifact generation 必須維持不同 responsibility。

---

### 17. Artifact Layout Is Deterministic

第一版 Quiz artifact root：

```text
week-{week:02d}/quiz/{quiz_id}/
```

Required learner-facing artifact：

```text
README.md
```

Canonical primary destination：

```text
<target>/week-{week:02d}/quiz/{quiz_id}/README.md
```

Example：

```text
week-03/
  quiz/
    streams-basics/
      README.md
```

Artifact path 必須由：

```text
validated week
+
validated quiz_id
```

決定。

不得由 title、question count 或 template filename 決定。

---

### 18. Answer Key Is a Separate Assessment Concern

Quiz content 具有 learner-facing content 與 answer-key content 的差異。

第一版 contract 將 answer key 視為 optional generated artifact。

若：

```text
answer_key = True
```

或 implementation 採等效 explicit option，則可規劃：

```text
ANSWER_KEY.md
```

Example：

```text
week-03/
  quiz/
    streams-basics/
      README.md
      ANSWER_KEY.md
```

若 answer-key generation 尚未在第一 implementation 實作，則此能力保持 Proposed。

不得在未經明確 contract 的情況下把正確答案意外暴露於 learner-facing `README.md`。

---

### 19. Learner Artifact and Answer Key Have Separate Templates

Default learner template：

```text
quiz/README.md.j2
```

若 answer-key artifact implemented，可使用：

```text
quiz/ANSWER_KEY.md.j2
```

這兩者屬 presentation boundary。

Template 不負責：

- Question ID uniqueness validation
- correct answer validation
- Week validation
- Quiz ID validation
- path safety
- overwrite decisions
- artifact ownership
- filesystem mutation

---

### 20. Template Context

Recommended structured context：

```python
{
    "week": {
        "number": 3,
    },
    "quiz": {
        "id": "streams-basics",
        "title": "Streams Basics Quiz",
        "instructions": "...",
        "questions": (
            {
                "id": "q1",
                "prompt": "...",
                "choices": (...),
                "correct_answer": "...",
                "explanation": "...",
            },
        ),
    },
}
```

Implementation 可以在既有 renderer constraints 下使用 flat mapping。

但 template-author-facing keys 一旦成為 tested/documented contract，就不得無意變更。

---

### 21. Validation Happens Before Planning Mutation

`validate_request()` 至少驗證：

```text
generator_name == "quiz"
valid template root according to existing conventions
valid week
valid quiz_id
valid title
questions is a supported collection
questions is non-empty
each question has valid id
question IDs are unique
each prompt is valid
each choices collection is valid
each correct_answer resolves to exactly one choice
optional explanation shape if supported
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

### 22. Planning Uses Canonical GenerationPlan

Quiz Generator `plan()` 必須回傳：

```text
GenerationPlan
```

第一版 minimum plan：

```text
1 operation

<target>/week-{week:02d}/quiz/{quiz_id}/README.md
```

若 answer key supported：

```text
2 operations

README.md
ANSWER_KEY.md
```

所有 artifacts 必須在 execution 前出現在 canonical plan。

不得建立：

```text
QuizPlan
QuizGenerationPlan
AssessmentPlan
```

作為 parallel planning abstraction。

---

### 23. Plan Ordering Is Deterministic

若 Quiz 產生多個 artifacts，canonical operation ordering 必須 deterministic。

推薦：

```text
README.md
ANSWER_KEY.md
additional explicitly planned artifacts
```

不得依賴：

- filesystem enumeration order
- dictionary iteration from uncontrolled input
- random ordering
- plugin registration order
- current time

---

### 24. Execute Uses Existing Infrastructure Boundaries

`execute()`：

- consumes validated request + canonical plan
- uses existing renderer/filesystem patterns
- obeys dry-run
- obeys overwrite semantics
- obeys manifest semantics
- returns `GenerationResult`

不得：

- redo CLI parsing
- bypass plan
- write arbitrary unplanned files
- infer additional questions
- randomize choices
- implement grading
- redefine filesystem security
- return Quiz-specific result type

---

### 25. GenerationResult Remains Canonical

Quiz Generator 回傳：

```text
GenerationResult
```

不得建立：

```text
QuizGenerationResult
AssessmentResult
QuizResult
```

作為 parallel generator result contract。

Assessment results produced by a future learner/grading system are不同概念，不屬於本 Generator contract。

---

### 26. Dry Run Semantics

Dry run：

- performs complete request validation
- builds complete GenerationPlan
- performs rendering/planning required by existing lifecycle
- evaluates predictable conflicts according to existing semantics
- does not create Quiz directories
- does not create learner artifact
- does not create answer key
- does not persist manifest mutation
- returns canonical `GenerationResult` with `dry_run=True`

Dry run 不得只跳過 execution 而略過 validation。

---

### 27. Overwrite Semantics

Quiz artifacts 是 author-relevant courseware content。

Default behavior：

```text
overwrite disabled
→ existing artifact is not silently replaced
```

Quiz Generator 重用 existing RuntimeOptions overwrite contract。

不得加入 Quiz-specific：

```text
--overwrite-quiz
--replace-assessment
force_quiz
```

等第二套 overwrite semantics。

---

### 28. Manifest Integration

若：

```text
record_manifest=True
```

Quiz Generator：

- reuse existing GenerationManifest integration
- record Quiz artifacts using existing schema
- preserve deterministic manifest ordering
- does not introduce Quiz-specific manifest file
- does not persist manifest mutation during dry-run

Answer-key artifact 若 implemented，也必須由同一 manifest contract 記錄。

---

### 29. Failure Semantics

Validation failures使用 existing generator validation/error boundaries。

Template/filesystem failures遵循 existing execution error translation。

本 ADR 不新增：

```text
QuizValidationError
QuizQuestionError
QuizPlanError
QuizExecutionError
```

除非 future exception architecture證明需要 specialization。

Error message 可以包含：

- quiz_id
- question_id
- invalid field

但程式契約不應依賴完整 error message text。

---

### 30. Determinism

相同：

```text
validated request
+
template
+
configuration
```

必須得到 deterministic：

- artifact root
- question ordering
- choice ordering
- plan operations
- operation ordering
- template selection
- rendered content
- manifest ordering
- GenerationResult paths

Quiz Generator 不得依賴：

- random shuffle
- random IDs
- wall-clock time
- filesystem enumeration
- incidental mapping/set ordering
- plugin discovery order

---

### 31. No Randomization in Generator Contract

Randomized question order 或 randomized choices 是 assessment delivery concern，不是 minimum artifact Generator responsibility。

因此第一版 Quiz Generator 不提供：

```text
shuffle_questions
shuffle_choices
random_seed
```

若未來需要 deterministic seeded randomization，必須另行設計 contract。

這避免：

```text
same request
→ different artifact
```

破壞 generation determinism。

---

### 32. No Scoring Engine

本 ADR 不實作：

- learner response collection
- scoring
- grade calculation
- pass/fail threshold
- partial credit
- attempt history
- submission persistence
- gradebook integration

Quiz Generator 產生 assessment artifact，不執行 assessment session。

Conceptual boundary：

```text
Quiz content
    ↓
QuizGenerator
    ↓
Quiz artifact
```

而不是：

```text
learner submission
    ↓
grading engine
```

後者屬未來 assessment runtime。

---

### 33. No Question Bank Yet

本 ADR 不建立：

```text
QuestionBank
QuestionRepository
QuestionRegistry
QuestionStore
```

Question collection 直接由 validated request 提供。

只有在多個 generator/use case 證明需要 reusable question storage 後，才建立新的 architecture。

---

### 34. No Assessment Base Class Yet

本 ADR 不建立：

```text
Assessment
LearningMaterial
QuestionBase
AssessmentItem
MaterialKind
```

等 production inheritance hierarchy。

Lab + Quiz contracts 現在可以用來觀察真正重複的 semantics。

Shared abstraction 應由 concrete duplication 證明，而不是預先猜測。

---

### 35. No Public SDK Expansion

本 ADR 不將以下 symbols 自動加入：

```text
Quiz
Question
QuizGenerator
Assessment
Course
Week
```

至：

```text
generator.sdk
```

Built-in implementation 可以依賴 internal courseware / generator modules。

若 future third-party courseware plugin 需要 stable assessment contracts，必須另立 SDK ADR，包括：

- export contract
- compatibility tests
- plugin integration tests
- author documentation
- versioning policy

---

### 36. CLI Integration Is Deferred From Core Contract

ADR 0016 固定 Generator contract。

不要求同一 Design PR 加入：

```text
opl quiz
```

建議 sequence：

```text
ADR 0016
    ↓
contract tests
    ↓
QuizGenerator implementation
    ↓
template/integration tests
    ↓
CLI registration/integration
    ↓
documentation acceptance
```

CLI integration 應有獨立 tests。

---

## Canonical Minimum Request

```python
GenerateRequest(
    generator_name="quiz",
    target=output_root,
    values={
        "week": 3,
        "quiz_id": "streams-basics",
        "title": "Streams Basics Quiz",
        "questions": (
            {
                "id": "q1",
                "prompt": "Which operation is intermediate?",
                "choices": (
                    "map",
                    "collect",
                    "count",
                    "reduce",
                ),
                "correct_answer": "map",
            },
        ),
        "record_manifest": False,
    },
    options=RuntimeOptions(
        dry_run=False,
        overwrite=False,
    ),
)
```

Expected minimum primary artifact：

```text
<output_root>/week-03/quiz/streams-basics/README.md
```

---

## Validation Matrix

| Field / Concern | Valid | Invalid |
| --- | --- | --- |
| generator name | `quiz` | any other generator identity |
| week | positive `int` | bool, zero, negative, non-int |
| quiz_id | non-empty safe string | empty, whitespace, absolute/path traversal |
| title | non-empty string | empty, whitespace, non-string |
| questions | non-empty ordered collection | empty, unsupported type |
| question id | unique non-empty string | duplicate, empty, non-string |
| prompt | non-empty string | empty, whitespace, non-string |
| choices | ordered collection with at least 2 choices | missing, insufficient, unsupported shape |
| correct_answer | exactly one existing choice | missing or not represented by a choice |
| explanation | supported optional string | invalid type when provided |
| target | existing canonical target semantics | existing filesystem/path boundaries apply |
| template | existing/default Quiz template | missing/invalid template handled by canonical boundaries |

---

## Artifact Contract

### Minimum

```text
<target>/
└── week-03/
    └── quiz/
        └── streams-basics/
            └── README.md
```

### Optional Answer-Key Evolution

```text
<target>/
└── week-03/
    └── quiz/
        └── streams-basics/
            ├── README.md
            └── ANSWER_KEY.md
```

Only artifacts supported by tests/implementation are considered implemented contract.

---

## Architecture Boundary

```text
Course / Week domain
        ↓
Application / composition
        ↓
GenerateRequest
        ↓
QuizGenerator
        ↓
validate_request
        ↓
GenerationPlan
        ↓
TemplateRenderer
        ↓
Filesystem execution
        ↓
GenerationResult
```

Assessment authoring systems may exist above this boundary：

```text
Human / AI / Question source
        ↓
validated question data
        ↓
GenerateRequest
```

Quiz Generator itself remains deterministic infrastructure.

---

## Compatibility

### ADR 0014 Course / Week Domain

Preserved。

Quiz is Week-scoped and does not mutate Course / Week production models。

### ADR 0015 Lab Generator Contract

Preserved。

Quiz follows the same material-generator principles：

- explicit Week
- explicit material identity
- canonical GenerateRequest
- canonical GenerationPlan
- canonical GenerationResult
- deterministic artifact layout
- no automatic SDK expansion
- no premature LearningMaterial hierarchy

Quiz-specific assessment semantics are added without modifying Lab behavior。

### Existing Week Generator

Preserved。

Quiz uses the same positive integer Week semantics but is a separate generator invocation。

### GenerateRequest

Preserved without structural public change。

### RuntimeOptions

Preserved。

Dry-run and overwrite retain existing canonical semantics。

### GenerationPlan

Preserved as canonical planning boundary。

### GenerationResult

Preserved as canonical execution result。

### Manifest

Existing manifest contract is reused。

### Plugin SDK

No change。

### Plugin Distribution

No change。

ADR 0013 remains Future Plugin Evolution / Proposed。

---

## Alternatives Considered

### A. Use Quiz title as identity

Rejected。

Reasons：

- title changes would move artifact path
- display metadata would become machine identity
- references would be unstable

---

### B. One Quiz per Week without `quiz_id`

Rejected。

A Week may contain：

```text
pre-quiz
checkpoint
review
final-week-quiz
```

Therefore `(week, quiz)` alone is too restrictive。

---

### C. Use question position as Question identity

Rejected。

Question position changes when ordering changes。

Stable identity must survive reorder。

---

### D. Automatically generate Question IDs

Rejected as canonical contract。

Automatic IDs based on array indexes or prompt content introduce unstable identity semantics。

---

### E. Randomize questions during generation

Rejected。

It violates deterministic Generator output and mixes assessment-delivery behavior into artifact generation。

---

### F. Embed correct answers directly in learner README

Rejected as mandatory behavior。

Learner-facing assessment content and answer key have different visibility concerns。

Answer-key representation must remain explicit。

---

### G. Add `Quiz` and `Question` domain classes immediately

Rejected for Step 5.4A。

The first concrete Quiz contract should demonstrate which fields require reusable production domain types。

---

### H. Create `Assessment` hierarchy first

Rejected。

There is insufficient concrete evidence for the abstraction。

---

### I. Create Quiz-specific Request / Plan / Result

Rejected。

Would reopen stable Milestone 3 contracts without architectural need。

---

### J. Add scoring and grading now

Rejected。

Those features belong to assessment runtime rather than deterministic artifact generation。

---

### K. Introduce QuestionBank now

Rejected。

Storage/reuse requirements have not yet been demonstrated。

---

## Consequences

### Positive

- Quiz receives an explicit stable generator contract。
- Lab and Quiz now establish two concrete material-generator examples。
- Assessment artifact identity is deterministic。
- Question identity and ordering semantics are explicit。
- Learner artifact and answer-key concerns remain separated。
- Existing generator lifecycle remains unchanged。
- No premature assessment runtime architecture is introduced。
- Future AI quiz authoring has a clear deterministic downstream boundary。
- Contract tests can be written before production implementation。

### Costs

- Quiz request validation is more complex than Lab validation。
- Question IDs become an explicit author/tooling responsibility。
- Question representation must be documented carefully。
- Answer-key behavior may require an additional template/artifact。

### Risks

- Future question types may require richer representation。
- Correct-answer representation may need evolution for multi-select questions。
- Lab + Quiz may reveal enough duplication to justify a shared material model later。
- Answer-key artifact conventions may evolve with publishing needs。

Mitigation：

- minimum single-answer contract first
- contract tests before implementation
- future question types require explicit follow-up design
- shared abstractions only after concrete duplication is demonstrated
- breaking artifact or identity changes require follow-up ADR

---

## Implementation Plan

### Step 5.4A — Design

Create:

```text
docs/adr/0016-quiz-generator-contract.md
```

Synchronize:

```text
docs/adr/README.md
```

No production implementation in this step。

---

### Step 5.4B — Contract Tests

Create:

```text
tests/generators/test_quiz_generator_contract.py
```

Tests must initially define the contract independently of implementation completion。

Minimum contract tests should cover：

```text
canonical generator identity
BaseGenerator compatibility
GenerateRequest boundary
Week validation
bool Week rejection
quiz_id validation
title validation
non-empty questions
Question ID validation
duplicate Question ID rejection
prompt validation
choice validation
correct-answer validation
deterministic planning
canonical artifact path
dry-run semantics
GenerationResult compatibility
no Quiz-specific request/result contract
```

---

### Step 5.4C — Implementation

Expected production additions:

```text
generator/generators/quiz_generator.py
templates/quiz/README.md.j2
```

Potential answer-key support only if explicitly covered by the accepted implementation scope:

```text
templates/quiz/ANSWER_KEY.md.j2
```

Update built-in exports/registration only where required by existing architecture。

---

### Step 5.4D — Integration

Create:

```text
tests/generators/test_quiz_generator_integration.py
tests/integration/test_quiz_cli.py
```

Integration should verify:

```text
real template rendering
real filesystem output
canonical path
question ordering
choice ordering
dry-run mutation safety
overwrite behavior
manifest behavior where applicable
CLI registration
opl list exposure
```

---

### Step 5.4E — Documentation Acceptance

Synchronize:

```text
docs/architecture/open-courseware-platform.md
docs/adr/0016-quiz-generator-contract.md
docs/adr/README.md
docs/roadmap.md
docs/HISTORY.md
CHANGELOG.md
```

Status changes:

```text
ADR 0016
Proposed
    ↓
Accepted
```

only after production implementation and integration contracts pass。

---

## Test Strategy

### Contract Tests

Must verify architecture before implementation details。

Required categories：

#### Identity

- generator canonical name is `quiz`
- valid `quiz_id`
- empty/unsafe `quiz_id` rejected
- title does not determine identity

#### Week

- positive integer accepted
- zero rejected
- negative rejected
- bool rejected
- non-int rejected

#### Question Collection

- non-empty ordered collection accepted
- empty collection rejected
- deterministic order preserved

#### Question Identity

- non-empty Question ID accepted
- duplicate IDs rejected
- question position does not define identity

#### Question Content

- non-empty prompt required
- at least two choices
- correct answer must resolve to exactly one choice

#### Lifecycle

- validation happens before planning
- planning happens before execution
- invalid input produces no filesystem mutation
- canonical `GenerationPlan`
- canonical `GenerationResult`

#### Artifact Layout

Expected:

```text
week-03/quiz/streams-basics/README.md
```

Artifact path independent from title。

#### Determinism

Same request produces same：

- plan
- operation order
- question order
- choice order
- output path

#### Dry Run

Dry run:

- validates
- plans
- produces no Quiz files
- produces no directory
- does not mutate manifest

---

## Documentation Requirements

Every Quiz Generator implementation change must synchronize relevant:

```text
ADR
architecture
tests
implementation
Code Review Checklist
```

Before ADR acceptance, specifically review:

```text
docs/architecture/open-courseware-platform.md
docs/adr/README.md
docs/roadmap.md
docs/HISTORY.md
CHANGELOG.md
```

No documentation should claim Quiz as Implemented until integration tests and production implementation exist。

---

## Code Review Checklist

### Architecture

- [ ] Quiz follows canonical `BaseGenerator` lifecycle.
- [ ] `GenerateRequest` remains canonical invocation boundary.
- [ ] `GenerationPlan` remains canonical planning boundary.
- [ ] `GenerationResult` remains canonical result type.
- [ ] No `QuizRequest`, `QuizPlan`, or `QuizGenerationResult` is introduced.
- [ ] Quiz remains Week-scoped.
- [ ] Quiz does not become a root aggregate.
- [ ] Template does not own business validation.
- [ ] Filesystem does not own assessment semantics.
- [ ] CLI does not reimplement Quiz validation.
- [ ] No unnecessary `LearningMaterial` or `Assessment` hierarchy is introduced.

### Identity

- [ ] `quiz` is the single canonical built-in identity.
- [ ] `quiz_id` is explicit.
- [ ] `quiz_id` is independent from title.
- [ ] Quiz identity is Week-scoped.
- [ ] Question IDs are explicit.
- [ ] Question IDs are unique within one Quiz.
- [ ] Question position is not Question identity.
- [ ] Filesystem paths are not domain identity.

### Questions

- [ ] Questions are an ordered collection.
- [ ] Empty questions are rejected.
- [ ] Prompt validation is explicit.
- [ ] Choices use an ordered representation.
- [ ] At least two choices are required.
- [ ] Correct answer resolves to exactly one choice.
- [ ] Duplicate Question IDs are rejected.
- [ ] Question ordering is deterministic.
- [ ] Choice ordering is deterministic.
- [ ] Generator does not invent Question content.

### Assessment Boundary

- [ ] Learner artifact and answer-key concerns are explicit.
- [ ] Correct answers are not accidentally exposed in learner output.
- [ ] No scoring engine is introduced.
- [ ] No learner submission model is introduced.
- [ ] No gradebook integration is introduced.
- [ ] No QuestionBank is introduced without a separate design decision.
- [ ] No randomization is introduced into canonical generation.

### Paths and Templates

- [ ] Artifact root is `week-{week:02d}/quiz/{quiz_id}/`.
- [ ] Primary artifact is `README.md`.
- [ ] Artifact path is independent from title.
- [ ] Default template follows existing template conventions.
- [ ] Every written artifact exists in `GenerationPlan`.
- [ ] No arbitrary execution-time paths are introduced.
- [ ] Existing filesystem containment rules are preserved.

### Runtime

- [ ] Dry-run performs validation and planning.
- [ ] Dry-run produces no filesystem mutation.
- [ ] Dry-run produces no manifest mutation.
- [ ] Existing overwrite semantics are reused.
- [ ] Existing manifest semantics are reused.
- [ ] Existing error boundaries are reused.
- [ ] No Quiz-specific runtime flags duplicate canonical options.

### Determinism

- [ ] Same validated request gives same artifact path.
- [ ] Same validated request gives same Question order.
- [ ] Same validated request gives same Choice order.
- [ ] Plan ordering is deterministic.
- [ ] Manifest ordering is deterministic.
- [ ] No random identifiers are generated.
- [ ] No wall-clock values affect output.
- [ ] No filesystem enumeration order affects output.

### Compatibility

- [ ] ADR 0014 Course / Week semantics remain unchanged.
- [ ] ADR 0015 Lab Generator behavior remains unchanged.
- [ ] Existing Course / Week / Lab generators remain green.
- [ ] No accidental `generator.sdk` expansion occurs.
- [ ] Plugin Entry Point contract remains unchanged.
- [ ] Plugin validation/loading contracts remain unchanged.

### Tests

- [ ] Contract tests exist before implementation acceptance.
- [ ] Valid request behavior is tested.
- [ ] Invalid Week behavior is tested.
- [ ] Bool Week rejection is tested.
- [ ] Quiz ID validation is tested.
- [ ] Empty title rejection is tested.
- [ ] Empty Question collection rejection is tested.
- [ ] Duplicate Question IDs are tested.
- [ ] Choice validation is tested.
- [ ] Correct-answer validation is tested.
- [ ] Deterministic plan is tested.
- [ ] Artifact path is tested.
- [ ] Dry-run mutation safety is tested.
- [ ] Integration rendering is tested.
- [ ] CLI integration is tested before acceptance.
- [ ] Existing Lab tests remain green.

### Documentation

- [ ] ADR 0016 accurately describes implemented vs proposed capability.
- [ ] ADR index is synchronized.
- [ ] Open Courseware architecture is synchronized at acceptance.
- [ ] Roadmap is synchronized at acceptance.
- [ ] HISTORY is synchronized at acceptance.
- [ ] CHANGELOG is synchronized at acceptance.
- [ ] Public docs do not claim unsupported question types.
- [ ] Public docs do not claim scoring/grading capability.

### Automation

- [ ] `git diff --check`
- [ ] `ruff check generator tests`
- [ ] `ruff format --check generator tests`
- [ ] `pre-commit run --all-files`
- [ ] `python -m pytest`
- [ ] coverage gate passes
- [ ] GitHub CI is green

---

## Status

**Proposed**

ADR 0016 defines the Quiz Generator contract before implementation.

Acceptance requires:

```text
contract tests
    ↓
QuizGenerator implementation
    ↓
template integration
    ↓
CLI integration
    ↓
full regression suite
    ↓
documentation synchronization
```

Only after those gates pass should ADR 0016 become **Accepted**.
