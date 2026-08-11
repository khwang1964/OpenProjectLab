# ADR 0014: Open Courseware Domain Contract

> Status: Proposed\
> Date: 2026-08-11\
> Milestone: 5 --- Open Courseware Platform\
> Decision scope: Course identity, Week identity, minimum courseware
> domain model, Learning Material composition, domain validation,
> serialization boundaries, and compatibility with existing Course/Week
> Generators

## Context

OpenProjectLab（OPL）已完成 Milestone 3 Generator Core Framework 與
Milestone 4 Plugin Ecosystem。

Milestone 5 的目標是在既有 Generator 與 Plugin contracts 上建立 Open
Courseware Platform。`docs/architecture/open-courseware-platform.md`
已提出以下 conceptual hierarchy：

``` text
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

OPL 已存在 `course` 與 `week` Generator，但目前 Generator
request、template context、filesystem layout 與 courseware domain
concept 尚未被定義為一個正式的 domain contract。

如果直接開始實作 Lab、Quiz、Assignment、PPT 或 Website
Generator，容易產生下列問題：

-   每個 Generator 自行定義 Course/Week identity。
-   `course.yaml` 或 template context 被誤當成 domain model。
-   Week ordering 與 duplicate semantics 不一致。
-   Generator、Template 與 Filesystem responsibility 混合。
-   新 domain model 破壞既有 `course` / `week` Generator。
-   Plugin Generator 必須依賴 private implementation 才能理解
    courseware。
-   未來 AI Integration 只能直接操作檔案，而缺乏 structured courseware
    boundary。

因此，在新增 Milestone 5 material Generators 前，必須先固定最小 Open
Courseware Domain Contract。

------------------------------------------------------------------------

## Decision Drivers

1.  保護 Milestone 3 canonical Generator lifecycle。
2.  保護既有 `course` / `week` Generator compatibility。
3.  建立穩定且 deterministic 的 Course / Week identity semantics。
4.  分離 serialization、domain、Generator request、template context 與
    filesystem artifact。
5.  避免為尚未實作的所有教材種類建立過度複雜的 class hierarchy。
6.  讓 Lab、Quiz、Assignment、Slides 與 Website 可以共享同一 composition
    vocabulary。
7.  讓 domain validation 在 filesystem mutation 前完成。
8.  讓第三方 Generator 未來可透過 documented/public boundary 擴充。
9.  為 Milestone 6 AI Integration 提供 structured input/output
    boundary。
10. 讓 domain contract 可由 automated contract tests 驗證。

------------------------------------------------------------------------

## Decision

OPL 採用以下 Open Courseware Domain Contract。

### 1. Course Is the Root Courseware Aggregate

`Course` 是 Milestone 5 courseware composition 的 root domain concept。

最小 conceptual shape：

``` python
@dataclass(frozen=True, slots=True)
class Course:
    course_id: str
    title: str
    language: str
    weeks: tuple["Week", ...]
```

此程式碼描述 contract shape，不要求 implementation 使用完全相同的
class/module。

最小 Course semantics：

-   `course_id`：stable machine-oriented identity。
-   `title`：human-readable display metadata。
-   `language`：courseware language metadata。
-   `weeks`：ordered Week collection。

Course 不直接執行 generation，也不直接寫 filesystem。

### 2. Course Identity Is Explicit

`course_id` 必須明確提供或由明確、可測試的 normalization boundary 產生。

不得使用下列資料作為唯一 Course identity：

-   display title
-   output directory basename
-   current working directory
-   template name
-   Python class name

`title` 可以修改，而不應自動改變既有 Course identity。

若既有 `course` Generator 使用不同欄位名稱，migration layer 可以映射到
`course_id`；不得為了新 domain contract 無條件破壞既有 request。

### 3. Week Has Stable Identity Within a Course

Week 的最小 conceptual shape：

``` python
@dataclass(frozen=True, slots=True)
class Week:
    number: int
    title: str
    materials: tuple["LearningMaterial", ...]
```

Week identity 至少由其 parent Course scope 與 `number` 決定。

Invariants：

-   `number` 必須是正整數。
-   `bool` 不得被視為合法 Week number。
-   同一 Course 中不得存在重複 Week number。
-   Week ordering 依 `number` deterministic。
-   `title` 不構成唯一 identity。
-   output directory name 不構成 domain identity。

### 4. Existing Week Validation Is Preserved

既有 Week Generator 已具有 Week number validation 與 canonical
lifecycle。

Milestone 5 domain validation 不取代 Generator request validation。

兩者責任：

``` text
Domain validation
    → Course composition 是否成立

Generator request validation
    → 某 Generator invocation 是否符合其 contract
```

例如 duplicate Week number 是 Course composition concern；單一 `week`
request 的 `week` 值是否合法仍由既有 Generator validation 保護。

### 5. Learning Material Is a Composition Concept

Milestone 5 定義 `Learning Material` 作為 Course/Week 下的 composition
vocabulary。

初始 material kinds：

``` text
lecture
lab
quiz
assignment
slides
website
```

本 ADR **不要求**立即建立：

-   `LearningMaterial` base class
-   inheritance hierarchy
-   public enum
-   public SDK protocol

只有在實際 Generator contracts 證明需要時，才新增對應 public/private
types。

### 6. Material Identity Must Be Explicit Within Its Scope

若同一 Week 允許同 kind 的多個 material，必須具有 explicit `material_id`
或等價 identity。

不得只以 display title 推導 identity。

若初始 Generator contract 限制某 Week 每種 material 最多一個，則
`(week, kind)` 可以暫時形成唯一 composition slot；此限制必須由對應
Generator/ADR/tests 明確固定，而不是隱含假設。

### 7. Slides and Website Are Projections

`slides` 與 `website` 在 conceptual hierarchy 中代表
presentation/publishing projection，不是新的 Course root domain。

它們應由 structured Course/Week/Material intent 產生：

``` text
Validated Courseware Domain
        ↓
Projection Generator
        ↓
GenerationPlan
        ↓
Slides / Website Artifacts
```

不得以反向掃描任意 filesystem output 來猜測 canonical Course domain
作為主要 contract。

### 8. Serialization Is Not the Domain Model

`course.yaml`、JSON、TOML 或其他 configuration format 是
serialization/input representation。

正確 boundary：

``` text
Raw serialized input
        ↓
Parse / structural validation
        ↓
Domain construction
        ↓
Domain validation
        ↓
Generator request / composition
```

不得讓 Template、Generator、Website renderer 等各自讀取 raw mapping
並建立互相不一致的 business rules。

### 9. Filesystem Paths Are Not Domain Identity

Domain model 不使用以下資訊作為 canonical identity：

-   absolute output root
-   generated directory path
-   template filesystem path
-   current working directory

Path mapping 屬於 Generator planning / artifact / filesystem
responsibility。

概念：

``` text
Week(number=3)
        ↓
Week Generator
        ↓
GenerationPlan
        ↓
weeks/week-03/
```

`weeks/week-03/` 是 artifact mapping，不是 Week domain object 本身。

### 10. Domain Models Should Be Immutable by Default

正式 implementation 若建立 Course/Week value models，應優先使用
immutable semantics。

理由：

-   deterministic planning
-   easier testing
-   safer composition
-   避免 Template/Generator 隱式修改 shared domain state
-   future AI pipeline 可以明確產生新的 validated state，而不是任意
    mutation

Implementation 可以採 frozen dataclass 或等價設計；本 ADR 不固定具體
Python mechanism。

### 11. Domain Validation Happens Before Mutation

可由完整 courseware composition 判定的錯誤，應在 filesystem mutation
前發現。

至少包括：

-   invalid Course identity
-   invalid Week number
-   duplicate Week number
-   invalid material identity
-   duplicate material identity/slot
-   unsupported composition relationship

Domain validation failure 不得產生 partial courseware filesystem
mutation。

此規則不代表整個多 Generator execution 已具有 rollback
transaction；cross-generator execution atomicity 仍是獨立議題。

### 12. Ordering Is Deterministic

Course 的 Week ordering 必須 deterministic。

Canonical rule：

``` text
ascending Week.number
```

若未來 material ordering 需要公開 contract，必須由對應 composition
contract 明確定義。

不得依賴：

-   filesystem enumeration
-   set ordering
-   plugin discovery incidental ordering
-   creation timestamp
-   random identifier

### 13. Domain Does Not Own Presentation

Course/Week domain 不決定：

-   Markdown heading layout
-   HTML structure
-   PPT theme
-   website navigation markup
-   output directory formatting
-   Jinja template implementation

這些屬於 Template、Projection Generator 或 Artifact planning。

Domain 可以提供 presentation 所需的 structured semantic data，但不直接
render。

### 14. Domain Does Not Own Runtime Infrastructure

Courseware domain 不依賴：

-   CLI parser
-   Generator Registry
-   Plugin loader
-   Filesystem service
-   Jinja environment
-   Git
-   network service
-   AI provider

依賴方向必須保持：

``` text
Application / Composition
        ↓
Domain + Generator contracts
        ↓
Planning / Rendering / Filesystem
```

而不是 Domain 反向依賴 infrastructure。

### 15. Existing Course/Week Generators Evolve, Not Rewrite

Milestone 5 不建立 `CourseV2Generator` 或 `WeekV2Generator` 作為預設
migration strategy。

既有：

``` text
course
week
```

仍是 canonical built-in Generator identities。

Migration 原則：

1.  inventory 現有 request/template/output contracts。
2.  新增 domain contract tests。
3.  建立最小 adapter/mapping。
4.  保留既有 lifecycle。
5.  只有在明確 incompatibility 時才建立 migration/deprecation decision。
6.  compatibility change 必須有 tests 與 documentation。

### 16. GenerateRequest Remains the Generator Input Boundary

本 ADR 不建立第二套 Generator invocation protocol。

既有 Generator integration 仍使用 `GenerateRequest` 與
`RuntimeOptions`。

Course/Week domain objects若正式實作，可以：

-   在 application/composition layer 建立。
-   被轉換為 generator-specific values/context。
-   或在後續 ADR 中以明確方式納入 request contract。

在沒有後續 ADR 前，不得直接修改 public `GenerateRequest` contract
以塞入新的 mandatory domain object。

### 17. GenerationPlan Remains the Artifact Planning Boundary

Courseware domain 不新增平行的 `CoursewarePlan` 來取代
`GenerationPlan`。

預設流程：

``` text
Validated Domain
        ↓
GenerateRequest / Composition Mapping
        ↓
Generator
        ↓
GenerationPlan
        ↓
Execution
        ↓
GenerationResult
```

只有既有 `GenerationPlan` 無法表達實際需求時，才可透過新 ADR 擴充。

### 18. Public SDK Exposure Is Deferred

本 ADR 不自動把 Course、Week 或 Learning Material models 加入
`generator.sdk`。

若 third-party courseware Generator 需要依賴正式 domain
types，必須另行：

-   決定哪些 symbols 是 public。
-   更新 ADR 0010 public SDK contract。
-   新增 public export tests。
-   新增 third-party-style compatibility tests。
-   更新 Plugin authoring docs。

在此之前，Milestone 5 implementation 不得把 private domain module 假裝成
stable Plugin API。

------------------------------------------------------------------------

## Minimum Domain Vocabulary

  -----------------------------------------------------------------------
  Concept                 Meaning                 Identity
  ----------------------- ----------------------- -----------------------
  Course                  Courseware root         explicit `course_id`
                          aggregate

  Week                    Ordered teaching unit   Course scope + positive
                                                  `number`

  Learning Material       Material composition    explicit material
                          concept                 identity or documented
                                                  unique slot

  Lecture                 Primary instructional   material contract
                          material

  Lab                     Hands-on activity       material contract

  Quiz                    Assessment artifact     material contract

  Assignment              Extended learning task  material contract

  Slides                  Presentation projection projection identity

  Website                 Publishing projection   projection identity
  -----------------------------------------------------------------------

此表固定 terminology，不代表所有 concept 已具有 public Python type。

------------------------------------------------------------------------

## Validation Model

建議 validation pipeline：

``` text
Serialized Input
        ↓
Structural Validation
        ↓
Course Construction
        ↓
Course Domain Validation
        ↓
Composition Mapping
        ↓
Generator Request Validation
        ↓
Generation Planning
        ↓
Filesystem Safety Validation
        ↓
Execution
```

### Domain validation examples

-   empty/invalid `course_id`
-   non-positive Week number
-   boolean Week number
-   duplicate Week number
-   duplicate material identity
-   unsupported parent/child relationship

### Not domain validation

-   output path escapes root → filesystem
-   missing template file → planning/template
-   wrong generator name → Generator request
-   duplicate plugin runtime identity → Plugin registry
-   incompatible plugin distribution → Future Plugin Evolution

------------------------------------------------------------------------

## Compatibility with Existing Contracts

### Generator lifecycle

Preserved without redefinition:

``` text
BaseGenerator.run()
validate_request → plan → execute
GenerationResult
```

### Course Generator

Existing `course` identity remains canonical.

Domain integration must be additive/migratory and test existing behavior
before changing output semantics.

### Week Generator

Existing `week` identity remains canonical.

Existing positive-integer validation remains valid and should align with
the domain invariant.

### Plugin SDK

No change in this ADR.

`openprojectlab.generators` remains the canonical Plugin Entry Point
group.

### Plugin Distribution

No change in this ADR.

ADR 0013 belongs to **Future Plugin Evolution**, not Milestone 5 Open
Courseware Platform.

------------------------------------------------------------------------

## Consequences

### Positive

-   Courseware terminology becomes consistent.
-   New material Generators share Course/Week semantics.
-   Domain validation can occur before writes.
-   Templates remain presentation-only.
-   Existing Generator lifecycle is preserved.
-   Future Website/PPT/AI capabilities receive structured input.
-   Public SDK expansion can be deliberate instead of accidental.

### Costs

-   Application/composition layer may require mapping between serialized
    input, domain objects, and `GenerateRequest`.
-   Existing Course/Week contracts must be inventoried before
    implementation.
-   Some validation appears at multiple defensive layers by design.
-   Public courseware SDK exposure is delayed until its compatibility
    needs are known.

### Risks

-   Over-modeling the domain before concrete Generator requirements.
-   Accidentally treating conceptual classes in this ADR as mandatory
    implementation names.
-   Duplicating validation inconsistently between domain and Generator
    layers.
-   Breaking existing Course/Week output while introducing domain
    integration.

Mitigation：

-   keep minimum model small
-   contract tests first
-   adapter/migration before rewrite
-   architecture/ADR review before public SDK changes

------------------------------------------------------------------------

## Rejected Alternatives

### 1. Use `course.yaml` as the domain model

Rejected because serialization structure would leak into every layer and
become difficult to evolve safely.

### 2. Let each Generator define Course/Week independently

Rejected because identity, validation and ordering would drift across
Lab/Quiz/Assignment/PPT/Website.

### 3. Replace `GenerateRequest` with domain objects immediately

Rejected because it would unnecessarily reopen the accepted Milestone 3
public input contract.

### 4. Create a deep LearningMaterial inheritance hierarchy now

Rejected because actual requirements for all material kinds are not yet
proven.

### 5. Use output paths as Week/material identity

Rejected because presentation/filesystem layout must remain evolvable
independently from domain identity.

### 6. Rewrite existing Course/Week Generators

Rejected because Milestone 5 should extend the stable core, not bypass
or duplicate it.

------------------------------------------------------------------------

## Test Contract

Before domain implementation is considered accepted, tests should prove
at least:

### Course

-   valid explicit Course identity
-   invalid/empty identity rejected
-   title is not identity
-   deterministic Week ordering

### Week

-   positive integer accepted
-   zero/negative rejected
-   `bool` rejected
-   duplicate number rejected within Course
-   title change does not change Week identity

### Materials

-   documented identity rule
-   duplicate identity/slot rejected
-   material ordering deterministic when relevant

### Boundaries

-   domain construction does not write filesystem
-   domain does not require CLI
-   domain does not require Plugin loader/registry
-   serialization mapping is separately testable
-   existing `course`/`week` lifecycle tests remain green

### Integration

-   valid Course can map into existing Course/Week generation flow
-   invalid composition fails before writes
-   dry run remains mutation-free
-   `GenerationPlan` remains the planning boundary
-   `GenerationResult` remains the execution result boundary

------------------------------------------------------------------------

## Documentation Contract

Any PR implementing or changing this ADR must evaluate and update as
applicable:

-   `docs/architecture/open-courseware-platform.md`
-   `docs/architecture/generator.md`
-   `docs/adr/0014-open-courseware-domain-contract.md`
-   ADR index
-   Courseware authoring/reference docs
-   Generator reference
-   CLI/Errors reference if behavior changes
-   Plugin authoring docs if public SDK changes
-   `docs/roadmap.md`
-   `docs/HISTORY.md`
-   `CHANGELOG.md`
-   Milestone 5 acceptance documentation

------------------------------------------------------------------------

## Code Review Checklist

### Architecture

-   [ ] Courseware domain does not redefine Generator lifecycle.
-   [ ] Courseware domain does not redefine Plugin runtime.
-   [ ] Domain is independent of CLI/filesystem/templates.
-   [ ] Serialization is not treated as domain source of truth.
-   [ ] No unnecessary parallel request/plan/result framework was added.

### Identity

-   [ ] Course identity is explicit and stable.
-   [ ] Week identity is Course-scoped and deterministic.
-   [ ] Display title is not used as canonical identity.
-   [ ] Filesystem path is not used as canonical identity.
-   [ ] Duplicate identities are rejected before writes.

### Compatibility

-   [ ] Existing `course` Generator remains canonical.
-   [ ] Existing `week` Generator remains canonical.
-   [ ] Existing Week validation semantics remain valid.
-   [ ] `GenerateRequest` / `RuntimeOptions` remain compatible.
-   [ ] `GenerationPlan` / `GenerationResult` remain canonical.
-   [ ] No accidental `generator.sdk` expansion occurred.

### Tests

-   [ ] Domain invariants have unit/contract tests.
-   [ ] Duplicate Week/material tests exist.
-   [ ] `bool` Week number is rejected.
-   [ ] Deterministic ordering is tested.
-   [ ] Invalid domain does not cause filesystem mutation.
-   [ ] Existing Course/Week tests remain green.
-   [ ] Integration mapping into Generator flow is tested.

### Documentation

-   [ ] Architecture is synchronized.
-   [ ] ADR index is synchronized.
-   [ ] Reference/authoring docs are synchronized where applicable.
-   [ ] Roadmap/HISTORY/CHANGELOG are updated at the appropriate
    implementation/acceptance stage.
-   [ ] Proposed behavior is not documented as implemented.

### Automation

-   [ ] `git diff --check`
-   [ ] targeted domain tests
-   [ ] existing Course/Week tests
-   [ ] `ruff check generator tests`
-   [ ] `ruff format --check generator tests`
-   [ ] `pre-commit run --all-files`
-   [ ] `python -m pytest`
-   [ ] coverage gate
-   [ ] CI green

------------------------------------------------------------------------

## Acceptance Criteria

ADR 0014 can move from **Proposed** to **Accepted** when:

1.  Course/Week identity semantics are approved.
2.  Domain vs serialization vs artifact boundaries are approved.
3.  Existing Course/Week compatibility strategy is approved.
4.  Learning Material remains minimal and does not over-specify
    implementation.
5.  Domain contract tests exist and pass.
6.  Existing Generator lifecycle tests remain green.
7.  Architecture and ADR index are synchronized.
8.  No unreviewed public SDK expansion is introduced.

------------------------------------------------------------------------

## Follow-up

After this ADR is accepted, recommended sequence:

``` text
Contract tests
    ↓
Minimum domain implementation
    ↓
Existing Course/Week integration
    ↓
Lab Generator contract
    ↓
Quiz Generator contract
    ↓
Assignment Generator contract
    ↓
PPT / Website projection contracts
    ↓
Composition integration
    ↓
Milestone 5 acceptance
```

Any new public SDK surface, cross-generator transaction semantics, or
composition protocol should receive a separate design decision rather
than being silently added to this ADR.

------------------------------------------------------------------------

## Status

**Proposed**

This ADR defines the proposed Milestone 5 Open Courseware Domain
Contract. It does not claim that the Course/Week domain models or new
material Generators are already implemented.
