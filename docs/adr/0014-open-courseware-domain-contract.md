# ADR 0014: Open Courseware Domain Contract

> Status: Accepted
> Date: 2026-08-11
> Milestone: 5 — Open Courseware Platform
> Decision scope: Course identity, Week identity, minimum courseware domain model, Learning Material composition, domain validation, serialization boundaries, and compatibility with existing Course/Week Generators

## Context

OpenProjectLab（OPL）已完成 Milestone 3 Generator Core Framework 與 Milestone 4 Plugin Ecosystem。

Milestone 5 的目標是在既有 Generator 與 Plugin contracts 上建立 Open Courseware Platform。`docs/architecture/open-courseware-platform.md` 已提出 Course → Week → Learning Material 的 conceptual hierarchy。

OPL 已存在 `course` 與 `week` Generator。PR #41 建立了 Open Courseware domain contract tests，PR #42 建立了 minimum production `Course` / `Week` domain models 並把測試遷移到 production models。

目前 accepted implementation baseline：

```text
Course
- explicit course_id
- title
- language
- immutable weeks tuple
- duplicate Week number rejection
- deterministic Week ordering

Week
- positive integer number
- bool rejected
- title
- immutable value semantics
```

Milestone 5 尚未實作 LearningMaterial hierarchy、Lab、Quiz、Assignment、PPT、Website、Orchestrator 或 courseware-specific public SDK。

因此，本 ADR 接受 minimum Course/Week domain contract，同時保留其餘 courseware capabilities 為 Proposed。

---

## Decision Drivers

1. 保護 Milestone 3 canonical Generator lifecycle。
2. 保護既有 `course` / `week` Generator compatibility。
3. 建立穩定且 deterministic 的 Course / Week identity semantics。
4. 分離 serialization、domain、Generator request、template context 與 filesystem artifact。
5. 避免為尚未實作的教材種類建立過度複雜 class hierarchy。
6. 讓後續 Lab、Quiz、Assignment、Slides 與 Website 共享一致的 Course/Week vocabulary。
7. 讓 domain validation 在 filesystem mutation 前完成。
8. 保留未來 public SDK 擴充空間。
9. 為 Milestone 6 AI Integration 提供 structured domain boundary。
10. 讓 contract 可以由 automated tests 驗證。

---

## Decision

OPL 接受以下 Open Courseware Domain Contract。

### 1. Course Is the Root Courseware Aggregate

Production `Course` 是 Milestone 5 courseware composition 的 root domain concept。

Canonical minimum shape：

```python
@dataclass(frozen=True, slots=True)
class Course:
    course_id: str
    title: str
    language: str
    weeks: tuple[Week, ...] = ()
```

Contract：

- `course_id` 是 stable machine-oriented identity。
- `title` 是 human-readable display metadata。
- `language` 是 courseware language metadata。
- `weeks` 是 deterministic ordered Week collection。
- Course 不直接執行 generation。
- Course 不直接寫 filesystem。

### 2. Course Identity Is Explicit

`course_id`：

- 必須非空。
- construction 時進行 whitespace normalization。
- 不由 title、output directory、working directory、template name 或 Python class name 隱式決定。

`title` 可以變更而不改變 Course identity。

### 3. Week Has Stable Identity Within a Course

Production `Week` minimum shape：

```python
@dataclass(frozen=True, slots=True)
class Week:
    number: int
    title: str
```

Contract：

- `number` 必須是 `int`。
- `bool` 不合法。
- `number > 0`。
- 同一 Course 不得有重複 Week number。
- Course 內 Weeks 依 number ascending deterministic ordering。
- `title` 不是 canonical identity。
- output directory name 不是 domain identity。

### 4. Existing Week Generator Validation Is Preserved

Domain validation 不取代 Generator request validation。

```text
Domain validation
    → Course composition 是否成立

Generator request validation
    → 某次 Generator invocation 是否成立
```

既有 Week Generator 的正整數與 bool rejection contract 保持有效。

### 5. Learning Material Remains a Composition Concept

Milestone 5 使用 Learning Material 作為 composition vocabulary，但此 ADR **不接受**任何下列 production/public API：

- `LearningMaterial` base class
- inheritance hierarchy
- public enum
- public SDK protocol

Lecture、Lab、Quiz、Assignment、Slides、Website 仍屬後續 Proposed work。

### 6. Material Identity Is Deferred

未來 material identity 必須 explicit 或由明確 unique-slot contract 定義。

此 ADR 不固定 material identity class、field 或 cardinality。

### 7. Slides and Website Are Projections

Slides / Website 仍被視為 projection，不是 Course root domain。

```text
Validated Courseware Domain
        ↓
Projection Generator
        ↓
GenerationPlan
        ↓
Slides / Website Artifacts
```

此 architecture rule 已接受；具體 Generator 尚未實作。

### 8. Serialization Is Not the Domain Model

YAML / JSON / TOML 等只屬 input/serialization representation。

```text
Raw input
  ↓
Parse / structural validation
  ↓
Domain construction
  ↓
Domain validation
  ↓
Generator request / composition
```

### 9. Filesystem Paths Are Not Domain Identity

Course / Week identity 不依賴 absolute path、generated directory、template path 或 working directory。

Path mapping 屬於 Generator planning / artifact / filesystem responsibility。

### 10. Domain Models Are Immutable

Production Course / Week 採 immutable value semantics。

這支援：

- deterministic planning
- safer composition
- simpler testing
- no hidden Template/Generator mutation

### 11. Domain Validation Happens Before Mutation

目前 minimum domain validation涵蓋：

- invalid/empty `course_id`
- invalid Week number
- duplicate Week number

這些錯誤在 domain construction 時發生，且不需要 filesystem mutation。

Material-level validation仍屬 future work。

### 12. Ordering Is Deterministic

Course Weeks canonical ordering：

```text
ascending Week.number
```

不得依賴 filesystem enumeration、set ordering、plugin discovery order、timestamp 或 random identifiers。

### 13. Domain Does Not Own Presentation

Course/Week domain 不決定：

- Markdown layout
- HTML structure
- PPT theme
- website markup
- output directory formatting
- Jinja implementation

### 14. Domain Does Not Own Runtime Infrastructure

Courseware domain 不依賴：

- CLI parser
- Generator Registry
- Plugin loader
- Filesystem service
- Jinja environment
- Git
- network service
- AI provider

### 15. Existing Course/Week Generators Evolve, Not Rewrite

Canonical built-in generator identities仍為：

```text
course
week
```

不建立 `CourseV2Generator` / `WeekV2Generator`。

### 16. GenerateRequest Remains the Generator Input Boundary

本 ADR 不建立第二套 Generator invocation protocol。

既有 Generator integration 繼續使用：

```text
GenerateRequest
RuntimeOptions
```

Production Course/Week domain models目前不會自動成為 GenerateRequest mandatory fields。

### 17. GenerationPlan Remains the Planning Boundary

本 ADR 不新增 parallel courseware plan type。

```text
Validated Domain
  ↓
GenerateRequest / mapping
  ↓
Generator
  ↓
GenerationPlan
  ↓
Execution
  ↓
GenerationResult
```

### 18. Public SDK Exposure Remains Deferred

Course / Week production models目前位於 internal courseware package，**沒有加入 `generator.sdk`**。

若未來 third-party courseware Generator 需要 stable domain types，必須另行：

1. ADR。
2. SDK export contract changes。
3. public export tests。
4. third-party compatibility tests。
5. plugin authoring documentation。

---

## Accepted Implementation

Current production implementation：

```text
generator/courseware/__init__.py
generator/courseware/models.py
```

Current contract tests：

```text
tests/courseware/__init__.py
tests/courseware/test_domain_contract.py
```

Accepted behaviors：

- explicit/non-empty Course identity
- Course title independent from identity
- Week positive integer validation
- Week bool rejection
- duplicate Week rejection
- deterministic Week ordering
- immutable Course/Week models
- existing Course/Week Generator lifecycle preserved
- `GenerationPlan` remains canonical planning boundary
- invalid Week Generator request fails before planning
- dry-run remains filesystem-mutation-free

---

## Minimum Domain Vocabulary

| Concept | Status | Meaning |
| --- | --- | --- |
| Course | Implemented | Courseware root aggregate |
| Week | Implemented | Ordered teaching unit |
| Learning Material | Proposed | Composition concept |
| Lecture | Proposed | Primary instructional material |
| Lab | Proposed | Hands-on activity |
| Quiz | Proposed | Assessment artifact |
| Assignment | Proposed | Extended learning task |
| Slides | Proposed | Presentation projection |
| Website | Proposed | Publishing projection |

---

## Compatibility with Existing Contracts

### Generator lifecycle

Unchanged:

```text
BaseGenerator.run()
validate_request → plan → execute
GenerationResult
```

### Course Generator

Existing `course` identity remains canonical.

### Week Generator

Existing `week` identity remains canonical and continues enforcing its own request validation.

### Plugin SDK

No change.

`openprojectlab.generators` remains canonical Plugin Entry Point group.

### Plugin Distribution

No change.

ADR 0013 remains **Future Plugin Evolution / Proposed** and is not part of Milestone 5 domain implementation.

---

## Consequences

### Positive

- Course/Week terminology與 identity 已固定。
- Domain validation可在 infrastructure mutation前執行。
- Existing Generator lifecycle保持穩定。
- 後續 material Generators 有一致 parent domain。
- AI / Website / Slides 未來可依賴 structured domain，而不是 filesystem guessing。

### Costs

- Application/composition layer未來需要負責 domain ↔ Generator request mapping。
- Domain與 Generator validation會保留 defensive overlap。
- Public plugin-facing courseware SDK 尚未提供。

### Risks

- 過早擴張 Course/Week 欄位。
- 把 internal domain package誤當成 stable SDK。
- 在 Lab/Quiz/Assignment implementation 時建立不必要 inheritance hierarchy。

Mitigation：

- minimum model only
- contract tests first
- public SDK changes require separate ADR
- architecture/doc review before new abstractions

---

## Rejected Alternatives

1. **Use `course.yaml` as the domain model** — rejected because serialization would leak across layers。
2. **Let each Generator define Course/Week independently** — rejected because identity/validation would drift。
3. **Replace `GenerateRequest` immediately** — rejected because it reopens Milestone 3 input contract without need。
4. **Create LearningMaterial hierarchy now** — rejected due insufficient concrete requirements。
5. **Use output paths as identity** — rejected because artifact layout must remain independently evolvable。
6. **Rewrite Course/Week Generators** — rejected because Milestone 5 extends the stable core。

---

## Test Strategy

Current tests verify：

- Course identity
- Course empty identity rejection
- Week positive integer behavior
- Week non-positive rejection
- Week bool rejection
- duplicate Week rejection
- deterministic ordering
- title != identity
- immutable domain models
- existing Course/Week planning boundary
- validation before planning
- dry-run mutation safety

Future material/projection tests are not implied to be implemented by this ADR。

---

## Documentation Changes

Acceptance requires synchronization of：

- `docs/architecture/open-courseware-platform.md`
- `docs/adr/0014-open-courseware-domain-contract.md`
- `docs/adr/README.md`

No ADR 0013 change is required。

---

## Code Review Checklist

### Architecture

- [ ] Course/Week domain does not redefine Generator lifecycle.
- [ ] Courseware domain does not redefine Plugin runtime.
- [ ] Domain remains independent from CLI/filesystem/templates.
- [ ] Serialization is not domain source of truth.
- [ ] No parallel request/plan/result framework is introduced.

### Identity

- [ ] Course identity remains explicit.
- [ ] Week identity remains Course-scoped and deterministic.
- [ ] Display title is not canonical identity.
- [ ] Filesystem path is not canonical identity.
- [ ] Duplicate Week numbers are rejected.

### Compatibility

- [ ] Existing `course` / `week` Generator identities remain canonical.
- [ ] `GenerateRequest` / `RuntimeOptions` remain unchanged.
- [ ] `GenerationPlan` / `GenerationResult` remain canonical.
- [ ] No accidental `generator.sdk` expansion occurs.

### Tests

- [ ] Domain contract tests remain green.
- [ ] Existing Course/Week tests remain green.
- [ ] Week bool/non-positive validation remains tested.
- [ ] Duplicate Week and deterministic ordering remain tested.
- [ ] Dry-run remains mutation-free.

### Documentation

- [ ] Architecture marks Course/Week domain as Implemented.
- [ ] ADR index marks ADR 0014 Accepted.
- [ ] Lab/Quiz/Assignment/PPT/Website remain Proposed.
- [ ] ADR 0013 remains Future Plugin Evolution / Proposed.

### Automation

- [ ] `git diff --check`
- [ ] `ruff check generator tests`
- [ ] `ruff format --check generator tests`
- [ ] `pre-commit run --all-files`
- [ ] `python -m pytest`
- [ ] coverage gate
- [ ] CI green

---

## Status

**Accepted**

The minimum Course/Week Open Courseware Domain Contract is implemented and covered by contract tests. Learning Material, Lab, Quiz, Assignment, Slides, Website, composition orchestration, and public SDK exposure remain future Milestone 5 work.
