# OpenProjectLab 發展歷程（History）

## 專案起源

OpenProjectLab（OPL）最初的目標，是建立一套能快速產生專案骨架的工具。
隨著專案逐步發展，OPL 的定位逐漸由 Project Generator 演進為 **Project
Engineering Platform**。

------------------------------------------------------------------------

# 發展理念

OPL 的核心理念：

-   Design First
-   Documentation First
-   Automation First
-   Testing First

------------------------------------------------------------------------

# 發展歷程

## Bootstrap / Generator / Configuration / Template / Upgrade Framework

OPL 逐步建立 project generation、configuration、Jinja2 templates、
upgrade/manifest/backup/rollback 與 repository quality/governance
foundations。

------------------------------------------------------------------------

## Generator Core Framework（Milestone 3）

Milestone 3 將 Generator Framework 收斂為共享 canonical lifecycle：

``` text
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
registration、legacy PluginManager removal、third-party example
distribution， 並以真實 installed-distribution E2E 完成 acceptance。

Formal acceptance：

``` text
docs/milestones/milestone-4-acceptance.md
452 passed
Coverage: 85.90%
```

------------------------------------------------------------------------

## Open Courseware Platform（Milestone 5）

Milestone 5 開始把 OPL 從一般 project engineering framework 擴充為
structured courseware generation platform。

### Step 5.1 --- Architecture

建立：

``` text
docs/architecture/open-courseware-platform.md
```

固定 Domain / Generator / Template / Artifact / Filesystem
responsibility boundaries，並保留 Milestone 3 Generator lifecycle 與
Milestone 4 Plugin runtime。

### Step 5.2 --- Course / Week Domain Contract

ADR 0014 定義並接受 minimum Course / Week domain contract。

Production：

``` text
generator/courseware/models.py
```

完成 immutable `Course` / `Week` models、positive Week validation、bool
rejection、duplicate Week rejection 與 deterministic Week ordering。

### Step 5.3 --- Lab Generator

Lab 是第一個 concrete Learning Material Generator vertical slice。

完整演進：

``` text
PR #44 — docs: design lab generator contract
PR #45 — test: define lab generator contract
PR #46 — feat: implement lab generator contract
PR #47 — feat: integrate lab generator
```

ADR 0015 接受的核心 contract：

-   canonical generator identity `lab`
-   Lab 屬於單一 Week
-   explicit `lab_id`
-   minimum request values: `week`, `lab_id`, `title`
-   deterministic `week-{week:02d}/lab/{lab_id}/README.md`
-   canonical `GenerationPlan`
-   canonical `GenerationResult`
-   existing dry-run / overwrite / manifest semantics
-   no Lab-specific result/plan types
-   no `LearningMaterial` hierarchy
-   no accidental `generator.sdk` expansion

Production / integration：

``` text
generator/generators/lab_generator.py
templates/lab/README.md
generator/cli/main.py
```

Tests：

``` text
tests/generators/test_lab_generator_contract.py
tests/generators/test_lab_generator_integration.py
tests/integration/test_lab_cli.py
```

Lab 已完成 design → contract tests → implementation → integration →
documentation acceptance 閉環。

### Step 5.4 --- Quiz Generator

Quiz 是第二個 concrete Learning Material Generator vertical slice。

完整演進：

``` text
PR #49 — docs: design quiz generator contract
PR #50 — test: define quiz generator contract
PR #51 — feat: implement quiz generator contract
PR #52 — feat: integrate quiz generator
```

ADR 0016 接受的核心 contract：

-   canonical generator identity `quiz`
-   Quiz 屬於單一 Week
-   explicit Week-scoped `quiz_id`
-   minimum request values: `week`, `quiz_id`, `title`, `questions`
-   explicit/unique Question IDs
-   ordered choices and deterministic rendering
-   correct answer must resolve to one choice
-   deterministic `week-{week:02d}/quiz/{quiz_id}/README.md`
-   learner-facing artifact does not expose answer-key data
-   canonical `GenerationPlan` / `GenerationResult`
-   existing dry-run / overwrite / manifest semantics
-   CLI structured input through `--questions-file` JSON
-   no scoring/grading runtime, QuestionBank, randomization, or SDK
    expansion

Production / integration：

``` text
generator/generators/quiz_generator.py
templates/quiz/README.md.j2
generator/cli/main.py
tests/generators/test_quiz_generator_contract.py
tests/generators/test_quiz_generator_integration.py
tests/integration/test_quiz_cli.py
```

Quiz 已完成 design → contract tests → implementation → integration →
documentation acceptance 閉環。

### Step 5.5 --- Assignment Generator

Assignment 是第三個 concrete Week-scoped material Generator vertical
slice。

完整演進：

``` text
PR #54 — docs: design assignment generator contract
PR #55 — test: define assignment generator contract
PR #56 — feat: implement assignment generator contract
PR #57 — feat: integrate assignment generator
```

ADR 0017 接受的核心 contract：

-   canonical generator identity `assignment`
-   Assignment 屬於單一 Week
-   explicit Week-scoped `assignment_id`
-   minimum request values: `week`, `assignment_id`, `title`
-   ordered objectives / deliverables / resources
-   authored instructions / submission guidance
-   deterministic `week-{week:02d}/assignment/{assignment_id}/README.md`
-   canonical `GenerationPlan` / `GenerationResult`
-   existing dry-run / overwrite / filesystem / manifest semantics
-   CLI structured input through `--content-file` JSON
-   no grading/scoring/rubric runtime or submission backend
-   no Assignment-specific request/result hierarchy or SDK expansion

Production / integration：

``` text
generator/generators/assignment_generator.py
templates/assignment/README.md.j2
generator/cli/main.py
tests/generators/test_assignment_generator_contract.py
tests/generators/test_assignment_generator_integration.py
tests/integration/test_assignment_cli.py
```

Assignment 已完成 design → contract tests → implementation → integration
→ documentation acceptance 閉環。

### Step 5.6 --- Slides Generator

Slides 是第一個 presentation-source Generator vertical slice。

完整演進：

``` text
PR #59 — docs: design slides generator contract
PR #60 — test: define slides generator contract
PR #61 — feat: implement slides generator contract
PR #62 — feat: integrate slides generator
```

ADR 0018 接受的核心 contract：

-   canonical generator identity `slides`
-   required deck `title` and ordered `slides`
-   each slide requires a non-empty `title` and ordered `content`
-   deterministic canonical artifact `<target>/slides.md`
-   canonical `GenerationPlan` / `GenerationResult`
-   existing dry-run / overwrite / filesystem / manifest semantics
-   CLI structured input through `--slides-file` JSON
-   built-in `list` / legacy `--list` exposure
-   no Slides-specific request/result hierarchy or SDK expansion
-   PPTX / PDF / HTML rendering remains a future renderer capability

Production / integration：

``` text
generator/generators/slides_generator.py
templates/slides/slides.md.j2
generator/cli/main.py
tests/generators/test_slides_generator_contract.py
tests/generators/test_slides_generator_integration.py
tests/integration/test_slides_cli.py
```

Slides 已完成 design → contract tests → implementation → integration →
documentation acceptance 閉環。

### Step 5.7 --- Website Generator

Website 是 Milestone 5 的 deterministic static-publishing projection
vertical slice。

完整演進：

``` text
PR #64 — docs: design website generator contract
PR #65 — test: define website generator contract
PR #66 — feat: implement website generator contract
PR #67 — feat: integrate website generator
```

ADR 0019 接受的核心 contract：

-   canonical generator identity `website`
-   required site `title` and ordered `pages`
-   each page uses an explicit safe relative `.html` path
-   normalized page paths must be unique
-   canonical `index.html` entry page is required
-   deterministic multi-page output under `<target>/site/`
-   deterministic navigation follows authored page ordering
-   canonical `GenerationPlan` / `GenerationResult`
-   existing dry-run / overwrite / filesystem / manifest semantics
-   CLI structured input through `--pages-file` JSON
-   built-in `list` / legacy `--list` exposure
-   no Website-specific request/result hierarchy or SDK expansion
-   hosting, deployment, CMS, analytics, asset pipelines, and Markdown
    conversion remain outside core scope

Production / integration：

``` text
generator/generators/website_generator.py
templates/website/page.html.j2
generator/cli/main.py
tests/generators/test_website_generator_contract.py
tests/generators/test_website_generator_integration.py
tests/integration/test_website_cli.py
```

Website 已完成 design → contract tests → implementation → integration →
documentation acceptance 閉環。

------------------------------------------------------------------------

### Step 5.8 --- Courseware Composition Integration

ADR 0020 已完成 design → contract tests → implementation →
representative integration：

``` text
PR #69 — docs: design courseware composition contract
PR #70 — test: define courseware composition contract
PR #71 — feat: implement courseware composition contract
PR #72 — test: integrate courseware composition
```

Production / tests：

``` text
generator/courseware/composition.py
tests/courseware/test_composition_contract.py
tests/courseware/test_composition_integration.py
```

第一版 Composition 固定 deterministic sequential
ordering、GeneratorRegistry preflight、canonical
`BaseGenerator.run(request)`、ordered `GenerationResult`
aggregation、fail-fast / no cross-generator rollback，以及 shared
dry-run / overwrite / manifest semantics。Representative integration
已涵蓋 Course、Week、 Lab、Quiz、Assignment、Slides 與 Website，且未擴張
`generator.sdk`。

------------------------------------------------------------------------

### Step 5.9 --- Milestone 5 Representative E2E

PR #74 建立 Milestone 5 的 representative end-to-end acceptance
boundary。

測試：

``` text
tests/integration/test_courseware_composition_e2e.py
```

Representative flow 使用 production `CoursewareComposer`、既有
`GeneratorRegistry` 與 production Course / Week / Lab / Quiz /
Assignment / Slides / Website generators，驗證：

-   deterministic generator execution ordering
-   complete representative artifact membership
-   manifest generator provenance
-   reproducible user-facing artifact content
-   composition-wide dry-run 不留下 persistent project repository

這個 E2E 不建立第二套 orchestration，也不擴張 public SDK；它把 Milestone
5 既有 domain、generator、projection 與 composition contracts 串成完整
acceptance evidence。

------------------------------------------------------------------------

### Step 5.10 --- Formal Acceptance and Closure

Milestone 5 已完成 formal acceptance 與 post-merge consistency
alignment。

``` text
PR #75 — docs: accept milestone 5 open courseware platform
PR #76 — docs: align milestone 5 post-merge status
```

Formal acceptance baseline：

``` text
867 passed
Coverage: 88.76%
Required coverage: 67.0%
```

Milestone 5 因此正式關閉，開發焦點轉向 Milestone 6。

------------------------------------------------------------------------

## AI Integration（Milestone 6）

Milestone 6 在既有 Courseware Domain、Composition、GenerationPlan 與
Filesystem boundaries 上加入 provider-independent AI
capability，而不建立 第二套 generation pipeline。

核心原則：

``` text
AI proposes.
Domain validates.
Generator plans.
Filesystem commits.
Tests verify.
```

### Step 6.1 --- AI Integration Architecture and Contract

``` text
PR #77 — docs: design ai integration architecture
```

建立 `docs/architecture/ai-integration.md` 與 ADR 0021，固定：

-   AI Provider / Application / Domain / Generator / Filesystem
    boundaries
-   provider-specific SDK isolation
-   credential isolation
-   structured-output-first strategy
-   AI output as untrusted external input
-   deterministic `FakeAIProvider` core testing strategy
-   no real-provider dependency in normal CI

ADR 0021 已依目前 implementation evidence 對齊為 Accepted。

### Step 6.2 --- AI Core Contracts

``` text
PR #78 — feat: establish ai core contracts
```

完成：

-   immutable `AIRequest`
-   immutable `AIResponse`
-   runtime-checkable `AIProvider`
-   deterministic `FakeAIProvider`
-   no-network / no-credential core contract tests

### Step 6.3 --- Structured Response Validation

``` text
PR #79 — feat: establish ai response validation contract
```

建立 `AIResponseValidationError` 與 mapping-shaped structural
validation， 驗證 required fields / field types，同時保持 validation 與
Courseware Domain、 Filesystem side effects 分離。

### Step 6.4 --- AI-to-Courseware Mapping

``` text
PR #80 — feat: establish ai courseware mapping contract
```

將 validated AI response 映射為 production `Course` / `Week`，保持
deterministic Week ordering、provider metadata isolation，以及
structural validation failure 與 Domain invariant failure 的語意分離。

### Step 6.5 --- AI Course Generation Service

``` text
PR #81 — feat: establish ai course generation service
```

建立 `AICourseGenerationService`，以 injected `AIProvider` 串接既有
validation / mapping boundary；不直接依賴 filesystem、CLI 或 real
Provider。

### Step 6.6 --- AI Review

``` text
PR #82 — feat: establish ai review contract
```

建立 immutable `AIReviewFinding` / `AIReviewResult` 與
`AIReviewService`。 Review 保持 advisory，不直接修改 Courseware Domain
或 Filesystem。

### Step 6.7 --- AI Documentation

``` text
PR #83 — feat: establish ai documentation contract
```

建立 immutable `AIDocumentDraft` 與 `AIDocumentationService`，支援
structured Markdown / plain-text draft，同時保持 provider-independent、
deterministic、non-mutating behavior。

### Step 6.8 --- AI Template Completion

``` text
PR #84 — feat: establish ai template completion contract
```

建立 immutable `AITemplateCompletionResult` 與
`AITemplateCompletionService`， 保留 deterministic context-key
ordering，並保持與 Jinja rendering / Filesystem mutation 分離。

### Step 6.9 --- AI Course Builder

``` text
PR #85 — feat: establish ai course builder contract
```

建立 immutable `AICourseBuildRequest` 與 high-level `AICourseBuilder`，
將 course specification 轉換成 provider-independent
`AIRequest`，重用既有 AI-to-Courseware mapping，並加入 requested
week-count completeness validation。

### Step 6.10 --- Real Provider Adapter

Step 6.10 已完成 provider adapter contract、第一個 concrete provider、
deterministic no-network tests 與 live-test separation。

完成內容：

-   ADR 0022 --- AI Provider Adapter Contract Accepted
-   minimum provider-independent AI provider error hierarchy
-   `generator/ai/providers/` infrastructure boundary
-   first concrete `OpenAIProviderAdapter`
-   injected-client deterministic adapter tests
-   credential non-leakage / exception chaining / timeout / provider
    failure tests
-   finite timeout 與 initial no-hidden-retry policy
-   `ai_live` opt-in marker
-   normal pytest / pre-commit / core CI 排除 live-provider dependency
-   無 `OPENAI_API_KEY` 時 explicit live smoke test 以 skip 結束
-   paid/live OpenAI invocation 保留為 optional operational verification

核心 isolation boundary：

``` text
Normal pytest / pre-commit / core CI
        ↓
No provider API key
No paid AI account
No live provider availability
No provider network dependency
```

ADR 0022 的 acceptance 不要求真實付費 Provider call；Step 6.10 的
engineering completion 以 concrete adapter、deterministic tests、
live-test separation、documentation alignment 與 regression/CI 為準。

### Step 6.11 --- Representative deterministic AI E2E

Step 6.11 已建立 Milestone 6 的 representative deterministic acceptance
path：

``` text
AICourseBuildRequest
        ↓
AICourseBuilder
        ↓
FakeAIProvider
        ↓
AIResponse
        ↓
Structural Validation / Mapping
        ↓
Course / Week
        ↓
CoursewareComposer
        ↓
Production Generators
        ↓
GenerationPlan
        ↓
Filesystem
```

Representative E2E 驗證：

-   production `AICourseBuilder`
-   deterministic `FakeAIProvider`
-   production `Course` / `Week`
-   production `CoursewareComposer`
-   production Course / Week Generators
-   deterministic artifact membership/content
-   reproducible output across repeated runs
-   composition dry-run leaves no persistent project output
-   invalid AI response fails before filesystem side effects
-   no network / no API key / no paid invocation

Step 6.11 integration test 與 full regression 已通過；目前已知
regression baseline 為：

``` text
1119 passed
```

這個 baseline 是 Step 6.11 verification evidence；Step 6.12 formal
acceptance 隨後以最終 regression、coverage 與 CI evidence 完成收束。

### Milestone 6 Current Boundary

目前已完成：

-   provider-independent AI core
-   主要 application contracts
-   Real Provider Adapter infrastructure
-   deterministic no-network OpenAI adapter tests
-   live-provider test separation
-   representative deterministic AI → Domain → Composition → Filesystem
    E2E

Step 6.12 formal acceptance 與 post-merge consistency alignment 已完成：

-   `docs/milestones/milestone-6-acceptance.md`
-   final regression: 1119 passed, 1 deselected
-   total coverage: 90.23%
-   required coverage: 67.0% --- Passed
-   acceptance PR GitHub Actions / CI --- Passed
-   squash merge completed
-   post-merge consistency verification completed

Milestone 6 因此正式關閉。

Paid/live OpenAI invocation 不是 Milestone 6 core acceptance
的必要條件。 AI Refactoring Assistant、AI
CLI、evaluation、provenance、usage accounting、 caching、streaming 與
tool calling 保留為後續 capability。

------------------------------------------------------------------------

## Marketplace（Milestone 7）

Milestone 7 在既有 Generator Core、Plugin SDK、Courseware、AI 與
Filesystem boundaries 上建立 deterministic Marketplace artifact
ecosystem。

核心原則：

``` text
Marketplace distributes.
Contracts validate.
Existing OPL pipelines execute.
```

### Step 7.1 --- Marketplace Architecture and ADR 0023

建立 `docs/architecture/marketplace.md` 與 ADR 0023，固定 common
artifact
identity、version、type、compatibility、distribution、integrity，以及
discovery / acquisition / installation / activation responsibility
boundaries。

### Step 7.2--7.3 --- Artifact Contract and Models

完成 Marketplace artifact contract tests 與 minimum immutable production
models，包括：

``` text
ArtifactIdentity
ArtifactVersion
ArtifactType
ArtifactCoordinate
CompatibilityRequirement
DistributionMetadata
IntegrityMetadata
MarketplaceArtifact
```

### Step 7.4 --- Repository / Index Contract

建立 deterministic in-memory repository / index，支援 exact coordinate
lookup、available-version ordering、duplicate-coordinate rejection 與
explicit not-found semantics。

### Step 7.5 --- Integrity and Acquisition

建立 deterministic SHA-256 integrity verification 與 no-network
in-memory artifact acquisition boundary。Acquisition 只取得
bytes；Integrity verification 獨立執行，mismatch 在 installation
前失敗。

### Step 7.6 --- Installation Integration

建立 immutable installation result 與 deterministic in-memory
installer。 Installation 與 Activation 明確分離，不自動執行 Plugin
registration、 Entry Point discovery、Generator execution 或 Courseware
output。

### Step 7.7 --- Template Packages

建立 Template Package contract，重用 Marketplace artifact
identity/version， 並加入 safe relative path、path traversal
rejection、duplicate name/path rejection、deterministic ordering 與
immutable manifest semantics。

### Step 7.8 --- Representative Marketplace E2E

Representative path：

``` text
InMemoryMarketplaceRepository
        ↓
Exact Artifact Lookup
        ↓
InMemoryArtifactAcquirer
        ↓
Integrity Verification
        ↓
InMemoryArtifactInstaller
        ↓
Template Package Contract
```

E2E 驗證 deterministic happy path、exact coordinate、repository
not-found、 missing payload、integrity mismatch-before-install、no
partial installation state，以及 no public network / no
generated-project filesystem persistence。

### Step 7.9 --- Formal Acceptance

Final local acceptance baseline：

``` text
1315 passed, 1 deselected
Coverage: 89.89%
Required coverage: 67.0% --- Passed
```

ADR 0023 已依 implementation 與 test evidence 轉為 `Accepted`。
Milestone 7 acceptance PR 已通過 GitHub Actions / CI，完成 squash
merge， 並完成 post-merge consistency verification。Local `main` 與
`origin/main` 已確認同步，working tree clean。

Remote Marketplace、Community Repository hosting、Marketplace CLI、 real
package-manager integration、signing/publisher identity、sandbox/trust、
dependency solver、lock-file/cache、ratings/reviews、monetization 與 AI
Provider Marketplace 仍屬後續 capability。

------------------------------------------------------------------------

## v1.0 Stabilization & Release Readiness（Milestone 8）

Milestone 7 完成後，OPL 正式從主要 capability expansion 轉入第一個
stable release 的 stabilization 階段。

Milestone 8 是 **v1.0 前最後一個 engineering milestone**，核心目標不是再
增加大型功能，而是確認目前已建立的能力是否足以形成可維護的 stable
compatibility commitment。

Milestone 8 的演進方向：

``` text
Release Readiness Baseline
        ↓
Public Contract Audit & Freeze
        ↓
Reliability / Regression Hardening
        ↓
Packaging / Installation / Distribution
        ↓
Documentation & Bilingual User Manuals
        ↓
Compatibility & Deprecation Policy
        ↓
Support Matrix / Known Limitations
        ↓
Release Automation & Reproducibility
        ↓
Full Release-readiness Verification
        ↓
RC Acceptance
```

此階段採用 feature-freeze mindset。只有 correctness、security、
compatibility、reliability、installation、packaging、documentation
correctness、testing、automation 或其他 release blocker 所需要的變更，
才應進入 v1.0 stabilization scope；其他改善應移入 v1.1+ backlog。

v1.0 User Manual 將維護兩個正式版本：

``` text
docs/user-guide/en/
docs/user-guide/zh-TW/
```

English 與 Traditional Chinese (Taiwan) 版本必須保持 functional
documentation parity，並涵蓋 concepts、installation、quick start、
configuration、CLI、generators、courseware、plugins、AI integration、
Marketplace、troubleshooting 與 upgrading。

Milestone 8 completion 的意義是 OPL 已準備建立：

``` text
v1.0.0-rc.1
```

RC validation 通過後，才進入：

``` text
v1.0.0 GA
```

因此 Milestone 8 與 v1.0 GA acceptance 為兩個不同 gate。

------------------------------------------------------------------------

# Milestone 8 目前進度

Step 8.1 --- Release Readiness Baseline 已建立
`docs/releases/v1.0-release-readiness.md`，固定 v1.0 scope、contract
classification、feature-freeze、release gates、雙語 User Manual、
compatibility / deprecation、support matrix、known
limitations、packaging / clean-install、release automation 與 RC / GA
separation。

Step 8.2 --- Public Contract Audit & Freeze 已完成主要 contract-freeze
implementation，並以 dedicated v1 tests 保護下列 public surface：

``` text
generator.sdk
Generator public lifecycle / contracts
Plugin Entry Point / validation / registration
CLI command surface
Course / Week Domain
built-in Generator identities / reviewed artifact paths
Courseware Composition
provider-independent AI contracts
Marketplace contracts
configuration verified subset
filesystem verified subset
public error hierarchy
packaging metadata / console entry point
```

正式 audit 文件：

``` text
docs/releases/v1.0-public-contract-audit.md
```

正式 acceptance 文件：

``` text
docs/releases/v1.0-public-contract-freeze-acceptance.md
```

Step 8.2 亦記錄一項必須帶入 Step 8.4 的 packaging finding：
repository-level `templates/` 目前不應在尚未完成 built-artifact /
clean-install verification 前被宣稱為 release-ready packaged resources。

Step 8.2 已完成 final local quality gate：

``` text
1469 passed, 1 deselected
Coverage: 90.33%
Required coverage: 67.0% --- Passed
git diff --check --- Passed
Ruff / Ruff Format --- Passed
pre-commit --- Passed
```

Step 8.2 的 final local acceptance evidence 與 GitHub Actions / CI
均已通過：

``` text
1469 passed, 1 deselected
Coverage: 90.33%
Required coverage: 67.0% --- Passed
GitHub Actions / CI --- Passed
```

因此 Step 8.2 --- Public Contract Audit & Freeze 已正式 Accepted。這組
1469 / 90.33% 為 Step 8.2 自己的 acceptance evidence，不重用 Milestone 7
historical baseline。後續只需完成 squash merge、sync main 與 post-merge
consistency verification。

------------------------------------------------------------------------

# Step 8.3 --- Reliability / Regression Hardening

Step 8.3 已建立 governing design：

``` text
docs/releases/v1.0-reliability-hardening.md
```

並完成下列 reliability hardening slices：

``` text
Filesystem / Write Policy
Generator Lifecycle
Courseware Composition
Plugin Loading / Registration
Marketplace
AI
CLI / Structured Input
Representative Reliability E2E
```

核心原則維持：

``` text
Protect frozen v1.0 contracts.
Fail predictably.
Preserve existing state.
Fail before avoidable side effects.
Keep deterministic behavior deterministic.
Do not invent cross-Generator rollback.
```

Consolidated Step 8.3 reliability suite：

``` text
66 passed
```

這 66 tests 是 Step 8.3 targeted reliability evidence；正式 acceptance
仍需由完成態 repository 重新執行 full regression、coverage、
`git diff --check`、Ruff、Ruff Format、pre-commit 與 GitHub Actions /
CI，不能沿用 Step 8.2 的 1469 / 90.33% 作為 Step 8.3 final evidence。

Formal acceptance record：

``` text
docs/releases/v1.0-reliability-hardening-acceptance.md
```

Step 8.3 final acceptance evidence：

``` text
Targeted reliability suite: 66 passed
Full regression: 1535 passed, 1 deselected
Coverage: 90.54%
Required coverage: 67.0% --- Passed
git diff --check --- Passed
Ruff / Ruff Format --- Passed
pre-commit --- Passed
GitHub Actions / CI --- Passed
```

因此 Step 8.3 --- Reliability / Regression Hardening 已正式 Accepted。
後續只需完成 squash merge、sync main 與 post-merge consistency
verification。

目前狀態：

``` text
Reliability implementation      Complete
Targeted reliability suite      66 passed
Final local quality gate        Passed
Regression                      1535 passed, 1 deselected
Coverage                        90.54% (required 67.0%)
GitHub Actions / CI             Passed
Formal Step 8.3 acceptance      Accepted
```

------------------------------------------------------------------------

# Step 8.4 --- Packaging / Installation / Distribution

Step 8.4 已建立 governing design：

``` text
docs/releases/v1.0-packaging-installation.md
```

並建立 formal acceptance record：

``` text
docs/releases/v1.0-packaging-installation-acceptance.md
```

Step 8.2 所揭露的 repository-level `templates/` packaging risk 已在 Step
8.4 透過 Red Phase 實際重現：source checkout 可取得 templates， 但初始
wheel / clean-install runtime 無法取得 built-in Generator 所需 runtime
resources。

Production fix 將 runtime templates 遷移為 package-owned canonical
resource：

``` text
generator/resources/templates/
```

並以 `package_template_root()` 建立單一 runtime resource resolution
boundary。CLI default template root 不再依賴 repository root；explicit
template-root override behavior 保持。

Legacy repository-level runtime template tree 已在 isolation
verification 通過後移除。Template regression、Generator / CLI
integration、 package-resource contracts 與 clean-wheel installed-user
workflow 均已通過。

Local packaging / installation evidence：

``` text
Wheel build --- Passed
sdist build --- Passed
twine check --- Passed
Wheel resource inspection --- Passed
Clean-wheel installation --- Passed
Installed generator import --- Passed
Installed opl list --- Passed
Installed representative generation --- Passed
Legacy templates dependency --- Removed
Packaging suite --- 29 passed, 0 skipped
Wheel --- openprojectlab-0.6.0-py3-none-any.whl
sdist --- openprojectlab-0.6.0.tar.gz
```

Step 8.4 final local quality gate：

``` text
1558 passed, 1 deselected
Coverage: 90.55%
Required coverage: 67.0% --- Passed
git diff --check --- Passed
Ruff / Ruff Format --- Passed
pre-commit --- Passed
GitHub Actions / CI --- Passed
```

目前狀態：

``` text
Packaging implementation        Complete
Package-resource migration      Complete
Clean-install verification      Passed
Final local quality gate        Passed
Regression                      1558 passed, 1 deselected
Coverage                        90.55% (required 67.0%)
GitHub Actions / CI             Passed
GitHub Quality checks            Passed
GitHub Packaging artifact verification
                                 Passed
Formal Step 8.4 acceptance      Accepted
```

Step 8.4 acceptance PR 已通過 GitHub Actions / CI，因此 Step 8.4
正式標示為 **Accepted**。

------------------------------------------------------------------------

# 下一階段

Step 8.4 已完成正式 acceptance；squash merge、sync main 與 post-merge
consistency verification 後， 開發焦點轉入：

``` text
Step 8.5 --- Documentation & Bilingual User Manuals
```

------------------------------------------------------------------------

# 我們的願景

OpenProjectLab 的目標不是建立更多程式，而是建立：

> **更容易維護、更容易理解、更容易演進的軟體工程文化。**

> Build projects, not just code.
