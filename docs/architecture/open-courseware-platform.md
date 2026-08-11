# OpenProjectLab Open Courseware Platform Architecture

> Status: Proposed\
> Milestone: 5 --- Open Courseware Platform\
> Last updated: 2026-08-11\
> Scope: Courseware domain model, composition, generators, templates,
> artifacts, extension points, testing, documentation, and acceptance\
> Audience: Maintainers, contributors, courseware authors, Generator
> developers, Plugin developers, and tooling developers

OpenProjectLab（OPL）Milestone 5 的目標，是在已穩定的 Generator Core
Framework 與 Plugin SDK 上，建立可組合、可測試、可擴充的 **Open
Courseware generation platform**。

Milestone 5 不重新設計 Milestone 3 的 Generator lifecycle，也不重新設計
Milestone 4 的 Plugin runtime。它在既有
`GenerateRequest → validate_request → plan → execute → GenerationResult`
與 `generator.sdk` extension boundary 上，新增課程內容的
domain、composition 與 artifact contracts。

Roadmap 的 Milestone 5 planned features 為 Course Templates、Week
Templates、Lab Generator、Quiz Generator、Assignment Generator、PPT
Generator 與 Website Generator。凡尚未由程式碼、測試與已接受 ADR
支援的能力，均視為 **Proposed**。

------------------------------------------------------------------------

## 1. Goals

-   將 Course、Week 與 Learning Material 建模為清楚、可測試的 domain
    concepts。
-   讓課程內容由多個 Generator 組合，而不是建立單一巨型 Generator。
-   保留既有 `course`、`week` Generator 與 canonical lifecycle。
-   建立 Lab、Quiz、Assignment、PPT、Website 的共同 architecture
    boundary。
-   分離 Domain、Generator、Template、Artifact 與 Filesystem
    responsibilities。
-   保留 dry run、overwrite、manifest、deterministic output 與
    structured result。
-   讓 built-in 與 third-party Generator 使用同一公開 SDK boundary。
-   為 Milestone 6 AI Integration 提供 structured courseware
    contract，而不是讓 AI 直接修改 filesystem。

## 2. Non-Goals

Milestone 5 不應：

-   重新定義 `BaseGenerator.run()` canonical lifecycle。
-   建立第二套 request/result contract。
-   重新定義 Milestone 4 Entry Point、validation、registry 或 loader。
-   讓 Template 成為 domain source of truth。
-   讓 CLI 成為 courseware business-rule owner。
-   建立 LMS、學生帳號、成績簿或 submission backend。
-   將 AI content generation 納入 Milestone 5 exit criteria。
-   將 hosting provider、marketplace 或遠端 publishing 寫死進核心架構。

## 3. Existing Foundation

### Milestone 3 --- Generator Core

Milestone 5 保留：

-   `GenerateRequest`
-   `RuntimeOptions`
-   `GeneratorValidationError`
-   `GenerationOperation`
-   `GenerationPlan`
-   `GenerationResult`
-   canonical `BaseGenerator.run()`
-   `validate_request → plan → execute`
-   dry-run / overwrite / manifest semantics

既有核心 Generator：

``` text
bootstrap
course
lab
week
```

### Milestone 4 --- Plugin Ecosystem

Milestone 5 保留：

-   stable `generator.sdk`
-   third-party Generator validation
-   canonical `openprojectlab.generators` Entry Point group
-   transactional discovery / validation / registration
-   installed third-party distribution E2E proof

新 Courseware Generator 應建立在上述 contracts 上，不建立平行
framework。

## 4. Architecture Principles

OPL 繼續遵循：

-   **Design First**：先固定 domain、composition 與 ownership。
-   **Documentation First**：Architecture、ADR、reference 與 authoring
    guidance 同步。
-   **Automation First**：artifact structure 與 acceptance path 可由 CI
    驗證。
-   **Testing First**：implementation 前先建立 contract tests 與 failure
    semantics。
-   **Composition over Monolith**：Course 不由單一 Generator
    承擔所有教材行為。

## 5. High-Level Architecture

``` text
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

依賴規則：

-   Domain 不依賴 CLI、Template 或 filesystem。
-   Template 不擁有 domain validation。
-   Generator 將 validated intent 轉成 `GenerationPlan`。
-   Filesystem 保持安全寫入責任。
-   Plugin Generator 依賴 `generator.sdk`，不依賴 private courseware
    implementation。

## 6. Courseware Domain Model

最小 composition hierarchy：

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

這是 conceptual model，不代表所有項目都必須立即成為 public Python
class。

## 7. Course Contract

Course 表示課程層級 identity 與組織資訊。

概念：

``` python
@dataclass(frozen=True, slots=True)
class Course:
    course_id: str
    title: str
    language: str
    weeks: tuple["Week", ...]
```

Invariants：

-   `course_id` 是穩定 domain identity。
-   `title` 不作為唯一 identity。
-   Week ordering deterministic。
-   Course 不以 output path 作為 identity。
-   Course 不直接執行 generation。

未來 metadata（objectives、prerequisites、license、instructors
等）應依實際 contract 演進，不預先全部加入。

## 8. Week Contract

概念：

``` python
@dataclass(frozen=True, slots=True)
class Week:
    number: int
    title: str
    materials: tuple["LearningMaterial", ...]
```

Invariants：

-   `number` 為正整數。
-   同一 Course 不得有重複 Week number。
-   ordering 不依賴 filesystem enumeration。
-   title 修改不應隱式改變 canonical identity。
-   既有 `week` Generator contract 必須被保留。

## 9. Learning Material

Learning Material 是概念分類，不要求立即建立 inheritance hierarchy。

初始 kinds：

``` text
lecture
lab
quiz
assignment
slides
website
```

共同 metadata 可包含 material identity、title、kind、language、week 與
content reference。正式 enum/dataclass/protocol 應由 ADR 與 tests 決定。

## 10. Domain vs Artifact

必須區分：

**Domain** 描述課程內容：

``` text
Course
Week 03
Lab: Streams Practice
Quiz: Functional Programming
```

**Artifact** 描述要產生的輸出：

``` text
README.md
weeks/week-03/lecture.md
weeks/week-03/lab/README.md
weeks/week-03/quiz.md
slides/week-03.pptx
site/week-03/index.html
```

Domain object 不等於 output path。

## 11. Courseware Specification

YAML/JSON 等格式只是 serialization/input boundary，不是 domain model。

``` text
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

不要讓所有 layer 任意讀取未驗證的 `course.yaml` mapping。

## 12. Composition Boundary

概念：

``` text
Courseware Composition
    ↓
Course Generator
    ↓
Week Generator(s)
    ↓
Material Generator(s)
    ├── Lab
    ├── Quiz
    ├── Assignment
    ├── PPT
    └── Website
```

Composition layer 可以協調 Generator，但每個 Generator 仍透過正式
`run(request)` lifecycle 執行。

若引入 Orchestrator，其責任限於：

-   選擇 Generator。
-   建立 requests。
-   決定 deterministic execution order。
-   聚合 structured results。
-   提供跨 Generator failure context。

Orchestrator 不直接 render template、寫 filesystem、重做 registry/plugin
loading，或呼叫 private Generator methods。

## 13. Generator Responsibility

每個 Courseware Generator 維持：

``` text
validate_request
    ↓
plan
    ↓
execute
    ↓
GenerationResult
```

應負責：

-   generator-specific validation
-   deterministic planning
-   template selection/context
-   artifact definition
-   dry-run / overwrite semantics
-   structured result

不應負責 CLI parsing、Git、deployment、學生資料、AI service、plugin
discovery 或自行建立 filesystem safety rules。

## 14. Planned Generator Set

``` text
course       Existing
week         Existing
lab          Implemented
quiz         Proposed
assignment   Proposed
ppt          Proposed
website      Proposed
```

`course` 與 `week` 應演進而非重寫。新 canonical names 必須由 ADR/tests
固定。

## 15. Lecture, Lab, Quiz, Assignment

**Lecture**：主要教學內容；source intent 與 Markdown/HTML/PPT 等
presentation format 分離。

**Lab**：實作活動，可包含 objectives、instructions、starter
files、expected outputs 與 validation steps。

**Quiz**：評量 artifact；不負責學生作答或 grading backend。

**Assignment**：較完整學習任務，可包含 constraints、deliverables、rubric
與 starter resources；submission/LMS 不屬於 core scope。

## 16. PPT / Slides Projection

PPT Generator 是 presentation projection：

``` text
Structured Courseware Content
        ↓
Slides Generation Plan
        ↓
Presentation Template / Renderer
        ↓
Presentation Artifact
```

PPT 不應成為 Course domain owner。若未來支援 PPTX/HTML slides，應共享
content intent。

## 17. Website Projection

Website Generator 是 publishing projection：

``` text
Course / Week / Materials
        ↓
Website Projection
        ↓
Navigation + Pages + Assets
        ↓
Static Website
```

初始方向是 deterministic static
output。Hosting、authentication、analytics、CMS 不屬於 Milestone 5
core。

## 18. Template Boundary

Template 負責 presentation，不負責 business rules。

Template 可以使用 validated context、決定 layout 與 presentation
structure。

Template 不應：

-   決定 Week 是否合法。
-   查詢 Registry。
-   修改 filesystem。
-   執行 network request。
-   動態安裝 dependency。
-   成為 Course identity source of truth。

## 19. Template Context

Template Context 應明確、結構化且可測試，例如：

``` python
{
    "course": {
        "id": "modern-java",
        "title": "Modern Java",
        "language": "zh-TW",
    },
    "week": {
        "number": 3,
        "title": "Streams",
    },
}
```

若 context keys 成為 author-facing contract，必須提供 reference 與
tests。

## 20. Artifact and Filesystem Boundary

優先使用既有 `GenerationOperation` / `GenerationPlan`，不要建立平行
courseware operation model。

所有輸出仍使用既有 filesystem safety：

-   output-root containment
-   overwrite policy
-   path traversal protection
-   directory semantics
-   dry run
-   deterministic writes
-   error translation

## 21. Source vs Derived Artifacts

Milestone 5 應逐步區分：

**Author-owned/source**：

``` text
course metadata
lecture source
lab source
assignment source
```

**Derived/generated**：

``` text
static website
generated slides
indexes
navigation
```

此 distinction 影響 overwrite、regeneration 與 Milestone 6 AI
integration；若成為 public contract，應由 ADR 固定。

## 22. Validation Layers

``` text
Input / Configuration Validation
        ↓
Domain Validation
        ↓
Generator Request Validation
        ↓
Filesystem Safety Validation
```

例如：

-   duplicate Week → domain/composition validation
-   wrong `generator_name` → request validation
-   path traversal → filesystem validation
-   missing template → planning/template boundary

所有可預期 validation 應在 filesystem mutation 前完成。

## 23. Determinism

相同 validated input、configuration 與 templates 應得到 deterministic：

-   Generator selection
-   execution order
-   plans
-   artifact paths
-   navigation order
-   manifest records
-   result ordering

不得依賴 filesystem enumeration、偶然 plugin discovery order、random IDs
或未定義的 wall-clock state。

## 24. Dry Run and Overwrite

所有新 Generator 必須保留既有 dry-run 與 overwrite semantics。

Dry run：

-   完成 validation。
-   建立完整 plan。
-   檢查可預期 conflict。
-   不修改 filesystem/persistent manifest。
-   回傳 structured result。

Overwrite：

-   不靜默覆寫 author-owned content。
-   derived artifacts 的 regeneration policy 必須明確。
-   behavior 必須有 contract tests。

## 25. Manifest Integration

Courseware artifacts 繼續使用既有 manifest/audit direction。

若新增 courseware-specific metadata，應 additive 設計，不讓每個 Material
Generator 建立自己的 manifest format。

## 26. Plugin Extension Boundary

第三方 Courseware Generator 透過 Milestone 4 Plugin SDK 接入：

``` text
third-party generator
    ↓
generator.sdk
    ↓
openprojectlab.generators
    ↓
existing validation / registry / loader
```

若 Milestone 5 需要新增 public SDK symbols：

1.  ADR。
2.  public export tests。
3.  third-party-style contract tests。
4.  plugin authoring docs。
5.  backward compatibility review。

## 27. Capability Metadata

未來 composition 可能需要：

``` text
courseware:lab
courseware:quiz
projection:slides
projection:website
```

但 capability metadata 目前不是既有 public contract。Milestone 5
不應在沒有 ADR 前假設它已存在。

## 28. Failure and Atomicity

單一 Generator 使用既有 lifecycle guarantees。

跨 Generator composition 是否提供全 course rollback 尚未決定。初始
architecture：

-   planning/validation 儘量在 write 前完成。
-   execution order deterministic。
-   failure 指出失敗 Generator/stage。
-   不宣稱 cross-generator transaction，除非正式實作並測試。

若需要 cross-generator atomicity，應另立 ADR。

## 29. Composition Result

Composition 應保留各 Generator 的 `GenerationResult`。

不要輕易新增 generator-specific result hierarchy。若真的需要 aggregate
result，必須先證明既有 collection/application result
無法表達，並避免重蹈已移除 generator-specific result types 的問題。

## 30. Localization and Accessibility

Localization 初始原則：

-   language 是 structured metadata。
-   domain identity 不依賴 translated title。
-   output path 不直接使用未正規化 display title。
-   fallback deterministic。

Website/Slides templates 應保留 accessibility 空間，例如 semantic
headings、alt text、navigation 與 presentation labels。完整 WCAG
compliance 若成為 exit criterion，應另外定義自動化檢查。

## 31. Licensing and Security

Courseware architecture 應保留 course-level license 與 resource
attribution metadata，但不自動推斷第三方內容授權。

安全原則：

-   Template 預設不做 network fetch。
-   Output path 受 containment 保護。
-   Third-party Generator 仍是 executable-code trust boundary。
-   Website output 不注入 secrets。
-   Course metadata 不視為 executable code。

## 32. AI Boundary

Milestone 6 才是 AI Integration。

Milestone 5 應建立：

``` text
AI
  ↓
Structured Courseware Intent
  ↓
Validated Domain
  ↓
Existing Generator Lifecycle
```

而不是：

``` text
AI
  ↓
Direct Filesystem Mutation
```

## 33. Testing Strategy

### Domain tests

-   Course identity
-   Week numbering
-   duplicate rejection
-   material identity
-   deterministic ordering

### Generator contract tests

-   canonical lifecycle
-   validation before writes
-   deterministic plan
-   dry run
-   overwrite
-   structured result

### Composition tests

-   deterministic Generator order
-   request mapping
-   failure propagation
-   result aggregation

### Template tests

-   required context
-   stable output
-   missing-template behavior
-   localization fallback

### Integration tests

-   Course + Week
-   Week + Lab
-   Week + Quiz
-   Week + Assignment
-   Course → Website
-   Course/Week → Slides

### E2E acceptance

-   generate representative course
-   inspect artifact tree
-   dry run
-   regenerate under overwrite policy
-   verify manifest/results
-   verify third-party extension path where applicable

## 34. Representative Acceptance Fixture

保持小而完整：

``` text
sample-course
├── Week 1
│   ├── Lecture
│   ├── Lab
│   └── Quiz
└── Week 2
    ├── Lecture
    └── Assignment
```

Acceptance 最終應涵蓋 README、week
artifacts、Lab、Quiz、Assignment、Slides 與 static Website。

## 35. Test Isolation

核心測試使用：

-   `tmp_path`
-   local templates
-   local fixtures
-   fake/plugin fixtures when appropriate

核心 CI 不依賴 network、external LMS、cloud storage、hosted website 或
AI API。

## 36. Documentation Requirements

Milestone 5 每個新增 feature 必須同步評估：

-   `docs/architecture/open-courseware-platform.md`
-   ADR
-   Generator/CLI/Errors Reference
-   Courseware authoring guide
-   Template authoring guide
-   Plugin authoring（若 SDK 變更）
-   `docs/roadmap.md`
-   `docs/HISTORY.md`
-   `CHANGELOG.md`
-   `docs/milestones/milestone-5-acceptance.md`

## 37. ADR Plan

第一份建議 ADR：

``` text
docs/adr/0014-open-courseware-domain-contract.md
```

應固定：

-   Course identity
-   Week identity
-   minimum domain model
-   material composition semantics
-   domain validation boundary
-   serialization vs domain separation
-   existing Course/Week migration compatibility

後續只有在具體 decision 形成時，才考慮 composition/artifact
ADR；不要預先建立沒有實際決策需求的 ADR。

## 38. Proposed Implementation Sequence

### Step 5.1 --- Architecture

-   本文件
-   existing Course/Week contract inventory
-   terminology / ownership
-   Code Review Checklist

### Step 5.2 --- Domain Contract

-   ADR 0014
-   domain contract tests
-   minimum models（若 ADR 決定需要）
-   Course/Week alignment

### Step 5.3 --- Material Generators

依最小可驗證順序：

``` text
Lab
Quiz
Assignment
```

每個 feature 同步
Architecture、Tests、Implementation、Documentation、Code Review
Checklist。

### Step 5.4 --- Presentation Projection

PPT/Slides contract。

### Step 5.5 --- Website Projection

Deterministic static Website contract。

### Step 5.6 --- Composition Integration

Course → Week → Materials → Projections。

### Step 5.7 --- Milestone Acceptance

-   representative E2E
-   third-party extension validation where applicable
-   full tests / coverage
-   CI / pre-commit
-   references
-   roadmap / HISTORY / CHANGELOG
-   milestone acceptance document

Step 編號是 architecture proposal；若正式採用，應同步 roadmap。

## 39. Current Limitations

Architecture 階段以下均視為 Proposed，除非現有 code/tests 已證明：

-   formal Course domain model
-   formal Week domain model beyond current request contract
-   LearningMaterial model
-   Lab / Quiz / Assignment Generators
-   PPT / Website Generators
-   Courseware Orchestrator
-   composition result
-   capability metadata
-   courseware-specific public SDK
-   static-site publishing
-   LMS integration
-   AI generation

## 40. Architecture Invariants

1.  Milestone 3 canonical Generator lifecycle 不被重新定義。
2.  Milestone 4 Plugin SDK/runtime contract 不被重新定義。
3.  Domain 不依賴 CLI/filesystem。
4.  Template 不擁有 domain validation。
5.  Generator 將 validated intent 轉成 deterministic `GenerationPlan`。
6.  Courseware output 使用既有 filesystem safety boundary。
7.  Dry run / overwrite semantics 對新 Generator 一致。
8.  Composition 不透過 private Generator methods。
9.  Plugin extension 只依賴 documented public SDK。
10. Website/PPT 是 projection，不是 Course domain owner。
11. AI 不成為 Milestone 5 core runtime dependency。
12. Proposed capability 不描述為 implemented。
13. 新 feature 同步 architecture、tests、documentation 與 Code Review
    Checklist。

## 41. Code Review Checklist

### Architecture

-   [ ] 符合 Milestone 5 Open Courseware scope。
-   [ ] 未重新定義 Milestone 3 lifecycle。
-   [ ] 未重新定義 Milestone 4 Plugin runtime。
-   [ ] Domain、Generator、Template、Artifact、Filesystem ownership
    清楚。
-   [ ] 新 abstraction 有實際 contract 需求。
-   [ ] Website/PPT 未成為 domain owner。
-   [ ] AI-specific behavior 未侵入 Milestone 5 core。

### Domain

-   [ ] Course identity 清楚。
-   [ ] Week identity/ordering 清楚。
-   [ ] Duplicate identity 有 validation。
-   [ ] Domain 不保存不必要 infrastructure state。
-   [ ] Serialization 不等於 domain。
-   [ ] 新欄位有 contract/migration consideration。

### Generator

-   [ ] 使用 canonical `run(request)`。
-   [ ] Validation 先於 planning/execution。
-   [ ] Plan deterministic。
-   [ ] Dry run 無 filesystem mutation。
-   [ ] Overwrite 與既有 framework 一致。
-   [ ] 回傳 `GenerationResult`。
-   [ ] 未建立不必要 generator-specific result type。
-   [ ] 未直接解析 CLI arguments。

### Templates / Artifacts

-   [ ] Template 只處理 presentation。
-   [ ] Context 明確可測。
-   [ ] Output paths deterministic。
-   [ ] Conflicts 在 write 前發現。
-   [ ] 使用既有 filesystem safety。
-   [ ] Source/derived ownership 已評估。
-   [ ] Website/PPT output 可重現。

### Plugins / SDK

-   [ ] Third-party extension 不修改 core registry。
-   [ ] Plugin 只依賴 `generator.sdk`。
-   [ ] 新 public symbol 有 ADR/export tests/docs。
-   [ ] 不依賴 private plugin implementation。
-   [ ] Entry Point 保持 `openprojectlab.generators`。

### Tests

-   [ ] Domain invariants 有 unit tests。
-   [ ] Generator lifecycle 有 contract tests。
-   [ ] Validation failure 不產生 writes。
-   [ ] Dry run / overwrite 有測試。
-   [ ] Deterministic plan/output 有測試。
-   [ ] Composition 有 integration tests。
-   [ ] Template context 有測試。
-   [ ] Representative course 有 E2E。
-   [ ] Tests 不依賴 network/AI/hosted service。

### Documentation

-   [ ] Architecture 已同步。
-   [ ] 必要 ADR 已更新。
-   [ ] References 已同步。
-   [ ] Courseware/Template authoring 已同步。
-   [ ] Plugin authoring 已同步（若 SDK 變更）。
-   [ ] CLI/Errors Reference 已同步（若適用）。
-   [ ] Roadmap / HISTORY / CHANGELOG 已同步。
-   [ ] Milestone acceptance 已同步。

### Automation

-   [ ] `git diff --check`。
-   [ ] `ruff check generator tests`（若有 Python 變更）。
-   [ ] `ruff format --check generator tests`（若有 Python 變更）。
-   [ ] Targeted / integration / E2E tests。
-   [ ] `pre-commit run --all-files`。
-   [ ] `python -m pytest`。
-   [ ] Coverage gate。
-   [ ] CI 可重現 acceptance path。

## 42. Step 5.1 Acceptance Criteria

Step 5.1 完成時：

-   Open Courseware Platform architecture 已文件化。
-   Milestone 3 / 4 preserved boundaries 已記錄。
-   Course / Week / Learning Material terminology 已定義。
-   Domain、Generator、Template、Artifact、Filesystem ownership 已分離。
-   Existing Course/Week migration direction 已記錄。
-   Lab / Quiz / Assignment / PPT / Website 明確標示 Proposed。
-   Composition boundary 已定義，但未過早承諾 implementation class。
-   Test strategy、documentation strategy 與 Code Review Checklist
    已建立。
-   沒有 runtime code change。

## 43. Related Documents

-   `docs/roadmap.md`
-   `docs/architecture/generator.md`
-   `docs/architecture/plugin-sdk-contract-inventory.md`
-   `docs/adr/0005-generator-input-contract.md`
-   `docs/adr/0006-generator-validation-contract.md`
-   `docs/adr/0007-generation-plan-contract.md`
-   `docs/adr/0008-generator-execution-contract.md`
-   `docs/adr/0009-remove-legacy-generator-lifecycle.md`
-   `docs/adr/0010-plugin-sdk-public-contract.md`
-   `docs/adr/0011-plugin-validation-contract.md`
-   `docs/adr/0012-plugin-entry-point-contract.md`
-   `docs/milestones/milestone-4-acceptance.md`
-   `docs/HISTORY.md`
-   `CHANGELOG.md`

下一個建議 decision document：

``` text
docs/adr/0014-open-courseware-domain-contract.md
```

------------------------------------------------------------------------

> **Milestone 5 的核心不是增加更多彼此獨立的 Generator，而是讓
> Course、Week、Learning Materials 與 presentation projections 能在既有
> Generator/Plugin contracts 上被可靠地組合、驗證、測試與產生。**
