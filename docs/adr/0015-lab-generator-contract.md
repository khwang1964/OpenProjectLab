# ADR 0015: Lab Generator Contract

> Status: Proposed
> Date: 2026-08-11
> Milestone: 5 — Open Courseware Platform
> Step: 5.3A — Lab Generator Contract Design
> Decision scope: canonical Lab Generator identity, request values, validation, artifact layout, template boundary, planning/execution semantics, dry-run/overwrite behavior, manifest integration, and compatibility with existing Course/Week/domain contracts

## Context

OpenProjectLab（OPL）已完成：

```text
Milestone 3 — Generator Core Framework
Milestone 4 — Plugin Ecosystem
Milestone 5 / Step 5.1 — Open Courseware Platform Architecture
Milestone 5 / Step 5.2 — Minimum Course / Week Domain Contract
```

ADR 0014 已接受 minimum production `Course` / `Week` domain models。現有 built-in `course` / `week` Generators 仍使用 canonical：

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

Milestone 5 Step 5.3 開始新增 Learning Material generators。第一個 material generator 為 Lab。

若未先固定 Lab contract，直接實作容易造成：

- Lab identity 被 title 或 filesystem path 隱式決定。
- Lab request 與 Week request 使用不一致的 Week semantics。
- Lab generator 自行建立平行 lifecycle 或 result type。
- Template 負責 business validation。
- Dry-run、overwrite、manifest semantics 與 existing generators 分歧。
- Artifact layout 在實作後才被動固定。
- 未來 Quiz / Assignment 各自發明不同 material conventions。
- Private courseware domain types 被誤當成 plugin-facing SDK。

因此，Lab Generator 必須先以獨立 ADR 固定最小 contract。

---

## Decision Drivers

1. 保護 Milestone 3 canonical Generator lifecycle。
2. 保護 ADR 0014 Course/Week domain invariants。
3. 讓 Lab 成為第一個可複製的 material-generator pattern。
4. 保持 request、domain、template、artifact、filesystem responsibility 分離。
5. 讓 artifact layout deterministic。
6. 保留 dry-run / overwrite / manifest semantics。
7. 避免過早建立 `LearningMaterial` inheritance hierarchy。
8. 避免 accidental `generator.sdk` expansion。
9. 為 Quiz / Assignment contracts 建立一致先例。
10. 讓 contract 可以在 implementation 前由 automated tests 固定。

---

## Decision

OPL 採用以下 Lab Generator Contract。

### 1. Canonical Generator Identity

Lab Generator canonical name：

```text
lab
```

Production class 預期名稱：

```text
LabGenerator
```

此名稱屬 built-in Generator identity，不代表 public SDK symbol。

不得另外建立：

```text
laboratory
course-lab
week-lab
lab-v2
```

作為平行 canonical identities。

### 2. Lab Belongs to One Week

Lab 是 Week-scoped learning material。

Conceptual relationship：

```text
Course
  └── Week
       └── Lab
```

Lab 不成為新的 root aggregate。

Lab invocation 必須明確提供 Week identity；不得由：

- current directory
- output directory basename
- template path
- implicit sequence number

猜測 Week。

### 3. Lab Identity Is Explicit Within a Week

第一版 Lab contract 採 explicit `lab_id`。

Conceptual identity：

```text
(Course scope, Week number, lab_id)
```

對單次 generator request，至少必須提供：

```text
week
lab_id
title
```

`title` 不構成 canonical Lab identity。

`lab_id` 應為 non-empty machine-oriented string，並在 validation boundary normalization。

本 ADR 不固定跨整個 Course 的 global Lab uniqueness；identity scope 為 Week。

### 4. GenerateRequest Remains the Input Boundary

Lab Generator 不建立第二套 request type。

Canonical request：

```python
GenerateRequest(
    generator_name="lab",
    target=...,
    values={
        "week": 3,
        "lab_id": "streams-practice",
        "title": "Streams Practice",
        ...
    },
    options=RuntimeOptions(...),
)
```

Required values：

```text
week
lab_id
title
```

Optional values 初始允許：

```text
objectives
instructions
starter_files
expected_outputs
validation_steps
template
record_manifest
```

但 optional values 只有在 tests/implementation 實際支援時才算 implemented contract。

### 5. Week Validation Aligns with ADR 0014

`week`：

- 必須是 `int`
- `bool` rejected
- 必須 `> 0`

Lab Generator 必須在自己的 request validation 中防禦性驗證 Week value。

這不取代 `Week` domain model，也不要求 request 必須直接攜帶 `Week` object。

### 6. Lab ID Validation

`lab_id`：

- 必須是 string
- trim 後不可為空
- 不得包含 absolute path semantics
- 不得包含 `..` path traversal component
- 不得以 path separator 建立 nested artifact layout

第一版推薦 machine-readable format：

```text
streams-practice
collections-lab
concurrency-basics
```

本 ADR 不要求立即建立全域 slug utility；若專案已有 canonical normalization utility，implementation 應優先 reuse。

### 7. Title Validation

`title`：

- 必須是 string
- trim 後不可為空
- 是 display metadata
- 不參與 Lab identity
- 不直接決定 output path

### 8. Artifact Layout Is Deterministic

第一版 Lab artifact root：

```text
week-{week:02d}/lab/{lab_id}/
```

Required primary artifact：

```text
README.md
```

Example：

```text
week-03/
  lab/
    streams-practice/
      README.md
```

Canonical primary destination：

```text
<target>/week-03/lab/streams-practice/README.md
```

Artifact path 必須由 validated Week number + validated `lab_id` 決定，不由 title 決定。

### 9. Starter Files Are Additional Planned Artifacts

若 request 支援 starter files，它們屬於同一 Lab artifact root：

```text
week-03/lab/streams-practice/starter/
```

第一版 contract 不要求 starter files 必須實作；若加入，必須：

- 由 `GenerationPlan` 明確列出
- 保持 deterministic ordering
- 遵守 output-root containment
- 遵守 overwrite policy
- dry-run 不寫 filesystem

不得在 `execute()` 中臨時發現未列於 plan 的任意 starter files。

### 10. Template Boundary

Default primary template 概念：

```text
lab/README.md.j2
```

Template 負責 presentation：

- headings
- Markdown layout
- rendering optional sections

Template 不負責：

- Week validation
- Lab ID validation
- path safety
- overwrite decision
- registry/plugin lookup
- filesystem mutation

### 11. Template Context

Recommended structured context：

```python
{
    "week": {
        "number": 3,
    },
    "lab": {
        "id": "streams-practice",
        "title": "Streams Practice",
        "objectives": (...),
        "instructions": (...),
        "expected_outputs": (...),
        "validation_steps": (...),
    },
}
```

Implementation 可以在既有 renderer constraints 下採 flat mapping，但對 author-facing keys 的穩定化必須有 tests/docs。

### 12. Validation Happens Before Planning Mutation

`validate_request()` 至少驗證：

- `generator_name == "lab"`
- valid template root according to existing generator conventions
- `week` valid
- `lab_id` valid
- `title` valid
- optional collection/value shapes if supported

Invalid request：

```text
validate_request
    ✕
plan not called
execute not called
filesystem unchanged
```

### 13. Planning Uses GenerationPlan

Lab Generator `plan()` 必須回傳 canonical `GenerationPlan`。

第一版 minimum plan：

```text
1 operation
destination:
<target>/week-{week:02d}/lab/{lab_id}/README.md
```

若 starter files supported，所有輸出都必須出現在 same `GenerationPlan`。

不得建立：

```text
LabPlan
LabGenerationPlan
MaterialPlan
```

作為 parallel planning abstraction。

### 14. Execute Uses Existing Filesystem / Renderer Boundaries

`execute()`：

- consume validated request + plan
- use existing TemplateRenderer / FileSystem patterns
- obey dry-run / overwrite
- return `GenerationResult`

不得：

- redo CLI parsing
- bypass plan
- write arbitrary unplanned paths
- redefine filesystem safety
- return Lab-specific result type

### 15. Dry Run Semantics

Dry run：

- performs validation
- builds complete plan
- evaluates predictable conflicts according to existing semantics
- does not create Lab directory/files
- does not persist manifest changes
- returns structured `GenerationResult` with `dry_run=True`

### 16. Overwrite Semantics

Lab primary content is treated as author-relevant courseware artifact。

因此 default behavior must not silently overwrite existing output when overwrite is disabled.

Existing project overwrite semantics remain canonical；Lab Generator 不建立 special overwrite flag。

### 17. Manifest Integration

若 `record_manifest=True`：

- reuse existing GenerationManifest integration pattern
- record planned/executed Lab artifacts using existing manifest schema
- no Lab-specific manifest format

Dry run不得 persist manifest mutation。

### 18. Failure Semantics

Validation failures use existing generator validation/error boundaries。

Template/filesystem failures follow existing execution error translation patterns。

本 ADR 不新增：

```text
LabValidationError
LabPlanError
LabExecutionError
```

除非 existing exception hierarchy 明確需要 future specialization。

### 19. No LearningMaterial Base Class Yet

Lab 是 material concept，但本 ADR 不建立：

- `LearningMaterial`
- `MaterialKind`
- shared material protocol
- material registry

Lab 先以 concrete generator contract 驗證真正需要的 shared abstractions。

Quiz / Assignment 若出現重複 contract，再由後續 ADR 考慮抽象化。

### 20. No Public SDK Expansion

本 ADR 不將：

```text
Lab
LabGenerator
Course
Week
```

自動加入 `generator.sdk`。

Built-in Generator implementation 可以使用 internal modules。

若 third-party plugin 需要 courseware-specific stable types，必須另立 SDK ADR/change。

### 21. CLI Integration Is Deferred from the Core Contract

本 ADR 固定 Generator contract，不要求同一 PR 立即加入 CLI command。

建議 implementation sequence：

```text
contract tests
    ↓
LabGenerator
    ↓
template/integration tests
    ↓
CLI registration/integration
    ↓
documentation acceptance
```

若現有 built-in registration requires CLI/list exposure才能完整運作，該 integration 必須有獨立 tests。

### 22. Determinism

相同 validated request + template + configuration 必須得到 deterministic：

- artifact root
- plan operations
- operation ordering
- template selection
- manifest ordering
- `GenerationResult` paths

不得依賴：

- filesystem enumeration order
- random IDs
- wall-clock time
- incidental plugin order

---

## Canonical Minimum Request

```python
GenerateRequest(
    generator_name="lab",
    target=output_root,
    values={
        "week": 3,
        "lab_id": "streams-practice",
        "title": "Streams Practice",
        "record_manifest": False,
    },
    options=RuntimeOptions(
        dry_run=False,
        overwrite=False,
    ),
)
```

Expected primary artifact：

```text
<output_root>/week-03/lab/streams-practice/README.md
```

---

## Validation Matrix

| Field / Concern | Valid | Invalid |
| --- | --- | --- |
| generator name | `lab` | other names |
| week | positive `int` | bool, zero, negative, non-int |
| lab_id | non-empty safe string | empty, whitespace, absolute/path traversal |
| title | non-empty string | empty, whitespace, non-string |
| target | existing canonical target semantics | path violations handled by existing boundaries |
| template | existing/default Lab template | missing/invalid template handled by planning/template boundary |

---

## Compatibility

### ADR 0014 Course / Week Domain

Preserved。

Lab does not mutate Course/Week domain models and does not redefine their identity。

### Existing Week Generator

Preserved。

Lab uses the same positive integer Week semantic but remains a separate generator invocation。

### GenerateRequest

Preserved without public structural change。

### GenerationPlan

Preserved as canonical artifact planning boundary。

### GenerationResult

Preserved as canonical result type。

### Plugin SDK

No change。

### Plugin Distribution

No change。

ADR 0013 remains Future Plugin Evolution / Proposed。

---

## Alternatives Considered

### A. Use Lab title as identity

Rejected。

Reasons：

- renaming title would move artifacts
- display metadata would become machine identity
- unstable references

### B. One Lab per Week without `lab_id`

Rejected。

A Week may reasonably contain multiple Labs，therefore `(week, kind)` is too restrictive。

### C. Add `Lab` domain model immediately

Rejected for Step 5.3A。

The generator contract should first prove which Lab fields belong in domain vs request/template context。

### D. Create LearningMaterial base class first

Rejected。

Insufficient evidence before Lab/Quiz/Assignment concrete contracts exist。

### E. Put Lab directly under Course root

Rejected。

Lab is Week-scoped courseware material。

### F. Let template choose output path

Rejected。

Artifact planning belongs to Generator / `GenerationPlan`。

### G. Create Lab-specific result/plan types

Rejected。

Would violate stable Milestone 3 contracts。

---

## Consequences

### Positive

- First material Generator gets an explicit stable contract。
- Quiz / Assignment can reuse proven patterns。
- Artifact layout deterministic。
- Week semantics stay aligned with ADR 0014。
- No unnecessary shared material hierarchy。
- Existing runtime contracts remain unchanged。

### Costs

- Some validation duplicates Week defensive rules。
- `lab_id` becomes an explicit author/tooling responsibility。
- CLI/template authoring docs must later document request fields/layout。

### Risks

- Future material generators may reveal a better shared abstraction。
- Initial artifact layout may need migration if course root conventions evolve。
- Optional fields could accidentally become public contract without tests。

Mitigation：

- keep ADR status Proposed until contract tests + implementation
- treat only tested/documented optional fields as implemented
- use follow-up ADR for breaking artifact/layout changes

---

## Implementation Plan

### Step 5.3A — Design

```text
docs/adr/0015-lab-generator-contract.md
docs/adr/README.md
docs/architecture/open-courseware-platform.md
```

### Step 5.3B — Contract Tests

Proposed tests：

```text
tests/generators/test_lab_generator_contract.py
```

Cover：

- canonical name
- required fields
- Week validation
- Lab ID validation
- title validation
- deterministic destination
- `GenerationPlan`
- validation before planning
- dry-run safety
- overwrite behavior

### Step 5.3C — Minimum Implementation

Proposed：

```text
generator/generators/lab_generator.py
templates/lab/README.md.j2
```

Only fields proven by contract tests。

### Step 5.3D — Integration

Potential：

- built-in generator registration
- CLI/list integration
- manifest behavior
- template rendering
- full filesystem integration tests

### Step 5.3E — Acceptance

- ADR 0015 → Accepted
- architecture Lab status → Implemented
- authoring/reference docs
- roadmap/HISTORY alignment as appropriate

---

## Test Strategy

### Contract tests

Must prove：

- generator identity is exactly `lab`
- valid minimum request accepted
- invalid Week values rejected
- bool Week rejected
- empty/path-like `lab_id` rejected
- empty title rejected
- plan destination deterministic
- plan type is `GenerationPlan`
- validation failure prevents planning/execution
- dry-run creates no Lab filesystem artifacts
- result type is `GenerationResult`

### Integration tests

Once implementation exists：

- default template renders
- expected `README.md` created
- overwrite false protects existing artifact
- overwrite true follows existing semantics
- manifest integration follows existing schema
- built-in registry/CLI exposure behaves consistently

### Regression

Run existing：

```text
tests/courseware/
tests/generators/
tests/plugins/
```

plus full suite。

---

## Documentation Changes

This design PR synchronizes：

```text
docs/adr/0015-lab-generator-contract.md
docs/adr/README.md
docs/architecture/open-courseware-platform.md
```

Later implementation/acceptance should also consider：

```text
docs/roadmap.md
docs/HISTORY.md
authoring/reference documentation
```

---

## Rollback Plan

Before ADR acceptance：

- remove/revise proposed Lab contract
- no compatibility promise exists beyond merged design history

After acceptance：

- breaking canonical name, request fields, identity semantics, or artifact layout requires new ADR / migration decision
- do not silently rewrite accepted ADR history

---

## Code Review Checklist

### Architecture

- [ ] Lab remains Week-scoped.
- [ ] Lab does not become Course root.
- [ ] No LearningMaterial hierarchy is introduced prematurely.
- [ ] Generator lifecycle remains canonical.
- [ ] Template does not own validation/path policy.

### Identity / Validation

- [ ] `lab` is the only canonical generator name.
- [ ] Week uses positive-int / bool-rejection semantics.
- [ ] `lab_id` is explicit, non-empty, and path-safe.
- [ ] title is display metadata, not identity.
- [ ] validation completes before filesystem mutation.

### Planning / Execution

- [ ] `GenerationPlan` is used.
- [ ] primary destination is deterministic.
- [ ] all writes are represented by plan operations.
- [ ] `GenerationResult` is returned.
- [ ] dry-run and overwrite reuse existing semantics.
- [ ] manifest reuses existing format.

### Compatibility

- [ ] ADR 0014 remains intact.
- [ ] Course/Week Generator identities remain canonical.
- [ ] `GenerateRequest` is not redefined.
- [ ] no accidental `generator.sdk` expansion.
- [ ] Plugin runtime/distribution contracts are unchanged.

### Tests

- [ ] contract tests exist before implementation.
- [ ] invalid Week / bool cases covered.
- [ ] invalid `lab_id` cases covered.
- [ ] invalid title covered.
- [ ] deterministic plan destination covered.
- [ ] validation-before-planning covered.
- [ ] dry-run mutation safety covered.
- [ ] full regression suite passes.

### Documentation

- [ ] ADR index includes ADR 0015 Proposed.
- [ ] architecture marks Lab as Contract Proposed, not Implemented.
- [ ] future Quiz/Assignment remain Proposed.
- [ ] implementation status is not overstated.

### Automation

- [ ] `git diff --check`
- [ ] `ruff check generator tests`
- [ ] `ruff format --check generator tests`
- [ ] targeted tests
- [ ] `pre-commit run --all-files`
- [ ] `python -m pytest`
- [ ] coverage gate
- [ ] CI green

---

## Acceptance Criteria

ADR 0015 may move from **Proposed** to **Accepted** only when：

1. Lab contract tests exist and pass。
2. Production `LabGenerator` implements the accepted minimum request contract。
3. Deterministic artifact layout is tested。
4. dry-run / overwrite behavior is tested。
5. existing Course/Week/domain contracts remain green。
6. no accidental public SDK change occurs。
7. architecture/reference docs match implementation。
8. full CI and coverage gates pass。

---

## Status

**Proposed**

The Lab Generator contract is designed but not yet implemented. Lab is the first concrete Learning Material Generator; Quiz, Assignment, PPT/Slides, Website, shared LearningMaterial abstractions, orchestration, and public courseware SDK remain future work.
