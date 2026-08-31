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
historical baseline。Acceptance merge、main synchronization 與
post-merge consistency verification 均已完成。

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
Acceptance merge、main synchronization 與 post-merge consistency
verification 均已完成。

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

# Step 8.5 --- Documentation & Bilingual User Manuals

Step 8.5 已完成兩套正式 v1.0 User Manual，各 13 個 paired chapters，並建立 structure、bilingual parity、functional parity 與 First 15 Minutes executable documentation automation。

Final local acceptance evidence：

``` text
English User Manual --- 13 chapters
zh-TW User Manual --- 13 chapters
Documentation automation --- Passed
First 15 Minutes --- 3 passed, 0 skipped
Full regression --- 1616 passed, 1 deselected
Coverage --- 90.55%
Required coverage --- 67.0% --- Passed
git diff --check / Ruff / Ruff Format / pre-commit --- Passed
```

Formal acceptance record：

``` text
docs/releases/v1.0-documentation-user-manuals-acceptance.md
```

Step 8.5 acceptance PR #120 已通過 GitHub Actions / CI，完成 squash merge、sync main 與 post-merge consistency verification，因此 Step 8.5 已正式 Accepted。

------------------------------------------------------------------------

# Step 8.6 --- Compatibility & Deprecation Policy

Step 8.6 已建立 v1.0 compatibility / deprecation governing policy，並完成
兩組 focused contract automation。Step 8.2 frozen public-contract
classification 仍是 Stable surface 的唯一 authoritative baseline；Step 8.6
不重新定義或擴張該 surface。

Governing policy：

``` text
docs/releases/v1.0-compatibility-deprecation-policy.md
```

核心 release-series rule：

``` text
1.0.x → compatibility-preserving fixes
1.x   → backward-compatible evolution
2.0   → intentional breaking Stable-contract changes
```

已完成 implementation sequence：

``` text
PR #122 — docs: define v1.0 compatibility and deprecation policy
PR #123 — test: define v1 compatibility policy contract
PR #124 — test: define v1 deprecation policy contract
```

Automation：

``` text
tests/compatibility/__init__.py
tests/compatibility/test_version_policy_contract.py
tests/compatibility/test_deprecation_policy_contract.py
```

目前已固定 Stable / Candidate / Experimental / Internal / Deferred 的相容性
責任、behavioral compatibility、Deprecated Stable lifecycle、major-version
removal boundary、migration guidance、EN/zh-TW functional parity、
documentation / CHANGELOG obligations，以及 emergency compatibility
exception evidence。

Step 8.6 policy automation 與 documentation / CHANGELOG alignment
已完成。完成態 repository 已使用實際 built wheel 設定
`OPL_TEST_WHEEL`，使 packaging / clean-install / First 15 Minutes
installed-user checks 不再因缺少 wheel 而 skip，並取得新的 local
acceptance regression evidence：

``` text
Full regression --- 1648 passed, 1 deselected
Wheel-related skips --- 0
Coverage --- 90.55%
Required coverage --- 67.0% --- Passed
```

這組 1648 / 90.55% 是 Step 8.6 completion-state 的 fresh local evidence，
不沿用 Step 8.5 的 1616 / 90.55% baseline。Formal acceptance record：

``` text
docs/releases/v1.0-compatibility-deprecation-policy-acceptance.md
```

Step 8.6 acceptance PR #126 已通過 GitHub Actions / CI，完成 squash
merge，merge commit 為
`f3ae0584e8b47b5ccf0d94fe1a7882868d899580`。Local `main`、`origin/main`
與 `HEAD` 已確認一致，working tree clean，post-merge consistency
verification 亦完成，因此 Step 8.6 已正式 Accepted。


------------------------------------------------------------------------

# Step 8.7 --- Support Matrix / Known Limitations

Step 8.7 已完成 evidence-based support governance 與 known-limitations
governance，並建立 focused contract automation。

Governing documents：

``` text
docs/reference/support-matrix.md
docs/releases/v1.0-known-limitations.md
```

Delivery sequence：

``` text
PR #128 — docs: define v1.0 support matrix and known limitations
PR #129 — test: define v1 support matrix contracts
PR #130 — docs: record v1.0 environment support evidence
```

Automation：

``` text
tests/support/test_support_matrix_contract.py
tests/support/test_known_limitations_contract.py
31 passed
```

Step 8.7 的 Supported claim 採 evidence-first 原則。完成態 environment
matrix 目前只承諾已有直接證據的組合：

``` text
Ubuntu (ubuntu-latest) + Python 3.14
    → GitHub Actions CI evidence

Windows + Python 3.14.5
    → maintainer-owned wheel-backed release verification
    → 1648 passed, 1 deselected
    → 90.55% coverage
```

其他 Python / OS combinations 即使可能可運作，也不構成 v1.0 support
commitment。

Known-limitations register 已明確區分 Supported、Experimental、Known
Limitation 與 Deferred，並記錄 live-provider AI、remote Marketplace、
Plugin distribution/trust、grading/scoring、Slides rendering、Website
hosting/deployment、cross-Generator rollback、Internal API、built-artifact
boundary 與 documentation-language boundary。

Step 8.7 completion-state acceptance evidence：

``` text
Focused support suite --- 31 passed
Full regression --- 1679 passed, 1 deselected
Coverage --- 90.55%
Required coverage --- 67.0% --- Passed
git diff --check --- Passed
Ruff / Ruff Format --- Passed
pre-commit --- Passed
```

這組 1679 / 90.55% 是 Step 8.7 completion-state 的 fresh acceptance
evidence，不沿用 Step 8.6 的 1648 / 90.55% baseline。

Formal acceptance record：

``` text
docs/releases/v1.0-support-matrix-known-limitations-acceptance.md
```

Step 8.7 acceptance PR #131 已通過 GitHub Actions / CI，完成 squash
merge、sync main 與 post-merge consistency verification，因此 Step 8.7
已正式 Accepted。


------------------------------------------------------------------------

# Step 8.8 --- Release Automation & Reproducibility

Step 8.8 已完成 release automation / reproducibility governing design 與
主要 automation slices，將 v1.0 release identity 固定為一致且可追溯的：

``` text
Version
    ↕
Commit SHA
    ↕
Git Tag
    ↕
Release Artifact
    ↕
GitHub Release
```

完成範圍包括 canonical version / tag / SHA consistency、artifact metadata
與 checksum validation、maintainer release workflow、GitHub Release
consistency、wheel-backed clean-install、semantic reproducibility，以及
maintainer release documentation。

Step 8.8.8 已從完成態 repository 重新取得 fresh full-regression
evidence：

``` text
Full regression --- 1777 passed, 1 deselected
Coverage --- 90.89%
Required coverage --- 67.0% --- Passed
```

這組 evidence 不沿用 Step 8.7 的 `1679 passed, 1 deselected` /
`90.55%` historical baseline。

Formal acceptance record 已建立：

``` text
docs/releases/v1.0-release-automation-reproducibility-acceptance.md
```

Step 8.8 acceptance PR #139 已通過兩項 GitHub Actions / CI checks，並以
commit `f7d1b5f8a24d0169ee4fb5cf7484c1101a88abf7` 完成 squash merge。
同步 `main` 後，wheel-backed post-merge full regression 以
`1777 passed, 1 deselected in 37.40s` 通過，coverage 為 `90.89%`；
pre-commit、`git diff --check`、clean-working-tree 與跨文件狀態一致性
亦完成驗證。因此 Step 8.8 已正式 Accepted。

------------------------------------------------------------------------

# 下一階段

Step 8.8 formal closure 已完成：

``` text
acceptance commit
    ↓
push
    ↓
acceptance PR
    ↓
GitHub Actions / CI
    ↓
squash merge
    ↓
sync main
    ↓
post-merge consistency verification
```

下一個 planned gate 為：

``` text
Step 8.9 --- Full Release-readiness Verification
```

Step 8.9 在本次 Step 8.8 closure 中仍維持 `Planned`，尚未提前開始。

------------------------------------------------------------------------

# Step 8.9 --- Full Release-readiness Verification

Step 8.9 已正式啟動 governing-design slice，新增：

``` text
docs/releases/v1.0-full-release-readiness-verification.md
```

這一階段整合 Steps 8.1–8.8 的 accepted evidence，驗證 public-contract、
compatibility/deprecation、support matrix/known limitations、EN/zh-TW
文件、First 15 Minutes、release artifacts、representative installed-user
E2E、full regression、coverage、quality gates 與 GitHub Actions / CI 是否
共同描述同一個完整 v1.0 release-candidate state。

Step 8.9 採 fail-closed 原則；任一 required gate 失敗或缺乏證據，都不能
以其他通過項目抵銷。此 governing-design slice 不建立 acceptance record、
不填入未來測試數字，也不建立或發布 `v1.0.0-rc.1`。

Planned sequence：

``` text
8.9.1 Governing design and verification inventory
8.9.2 Steps 8.1–8.8 closure-contract automation
8.9.3 Contract / policy / support consistency automation
8.9.4 Documentation and First 15 Minutes verification
8.9.5 Artifact-backed representative installed-user E2E
8.9.6 Integrated package / release identity verification
8.9.7 Full regression and local quality gates
8.9.8 GitHub Actions / CI verification
8.9.9 Formal acceptance and post-merge consistency
```

Step 8.9.1 governing design 已完成。Step 8.9.2 新增 Milestone 8
closure-contract automation，以 28 個 focused tests 驗證 Steps 8.1–8.8
governing documents、acceptance records、closure placeholders 與 Roadmap
terminal states，並找出及修正 Step 8.1 baseline 仍為 `Proposed` 的歷史
狀態落差。

Step 8.9.3 Contract / Policy / Support Consistency Automation 已完成，聚合
驗證 Step 8.2 public-contract freeze、Step 8.6 compatibility/deprecation
policy 與 Step 8.7 support matrix/known limitations；combined focused suite
為 50 passed，且 pre-commit passed。

Step 8.9.4 Documentation / First 15 Minutes Verification 已透過 PR #144
完成，squash merge commit 為
`234d683d9bae3a82cd2cda951d0926c1da1c9140`。Post-merge 使用目前 wheel
執行 documentation 與 release-readiness suites，結果為 116 passed、必要
wheel-backed skips 為 0，且 working tree clean。

Step 8.9.5 Artifact-backed Representative Installed-user E2E 已透過 PR #145
完成；Quality checks 與 Packaging artifact verification 均通過，squash
merge commit 為 `e34ce0d901c2c7a214c0785cdebeee1d3c63359b`。Post-merge
focused verification 結果為 64 passed、必要 skips 為 0，且 working tree
clean。

Step 8.9.6 Integrated Package / Release Identity Verification 已透過 PR
#146 完成，整合 canonical version、wheel/sdist filenames、metadata、console
entry point、artifact set、checksums、commit 與 release source identity，
且未建立 tag、GitHub Release 或 RC。

Step 8.9.7 Full Regression and Local Quality Gates 取得 fresh completion-state
evidence：

``` text
1822 passed, 22 skipped, 1 deselected
Coverage: 90.89%
Required coverage: 67.0% --- Passed
pre-commit --- Passed
git diff --check --- Passed
working tree --- Clean
```

22 個 skipped tests 已逐項審查，全部屬於等待 packaging / artifact gate
提供 `OPL_TEST_WHEEL`、`OPL_TEST_DIST_DIR` 或 `OPL_RELEASE_COMMIT_SHA`
的 artifact-backed tests，並非 disabled regression 或 unresolved failure。

Step 8.9.8 GitHub Actions / CI Verification 已透過 acceptance PR #147
完成；workflow run `32229975851` 的 `Quality checks` 與
`Packaging artifact verification` 均通過。PR #147 隨後 squash merged
為 commit `9b0566b3fc4d2b0b94ae5e775fdd3c86c0e79e03`。

目前正式進入 **Step 8.9.9 Formal Acceptance / Post-merge Consistency**。
尚待從 synchronized `main` 取得 main/origin identity、clean working tree、
post-merge consistency / regression 與跨文件 closure evidence，才能將
Step 8.9 正式標記為 `Accepted` 並進入 Step 8.10 RC Acceptance。

Formal acceptance record 已建立：

``` text
docs/releases/v1.0-full-release-readiness-verification-acceptance.md
```

Step 8.9.9 初次 post-merge verification 發現 closure-contract scope defect：
新建立的 Step 8.9 acceptance record 被錯誤納入 Steps 8.1–8.8 prior-release
debt scan。修正僅調整文件選擇範圍，不弱化既有 forbidden closure markers，
並新增 regression test 保護 Step 8.9 governing / acceptance records 不會再被
誤判為 prior-step debt。

修正證據：

``` text
PR #148 --- merged
Head commit --- 7593ee6f46c8b57162d74b663360bf6c9e0236a1
CI workflow --- 32232518973
Quality checks --- Passed
Packaging artifact verification --- Passed
Merge commit --- 0d1fdc5a22c0de38d3b3f806a7e85197a65e2e3d
Targeted closure-contract suite --- 29 passed
Full regression before merge --- 1823 passed, 22 skipped, 1 deselected
pre-commit --- Passed
git diff --check --- Passed
```

PR #148 merge 後，已在 synchronized `main` 上完成最終 Step 8.9.9
post-merge consistency verification。`HEAD`、local `main` 與 `origin/main`
皆解析為 `0d1fdc5a22c0de38d3b3f806a7e85197a65e2e3d`，working tree 在驗證前後均保持 clean。

最終 post-merge evidence：

``` text
Full regression --- 1823 passed, 22 skipped, 1 deselected
Failures / errors --- 0
Coverage --- 90.89%
Required coverage --- 67.0% --- Passed
git diff --check --- Passed
Ruff / Ruff Format --- Passed
pre-commit --- Passed
Post-merge consistency verification --- Completed
```

Roadmap、HISTORY、CHANGELOG、governing verification record 與 formal
acceptance record 已對齊同一 terminal state。因此 **Step 8.9 — Full
Release-readiness Verification 已正式 Accepted**。

下一個獨立 gate 為 **Step 8.10 — RC Acceptance**；Step 8.9 的 acceptance
不建立、不發布，也不預先接受 `v1.0.0-rc.1`。

------------------------------------------------------------------------

# Step 8.10 --- RC Acceptance

Step 8.9 已正式 Accepted 後，OPL 進入獨立的 Step 8.10 RC Acceptance
gate。此步驟不重新定義 Step 8.9 的 release-readiness 結論，而是將已驗證的
repository state 綁定到一個可稽核的 Release Candidate identity。

Governing contract：

``` text
docs/releases/v1.0-rc-acceptance.md
```

Automated contract：

``` text
tests/release_readiness/test_v1_rc_acceptance_contract.py
```

Step 8.10 已固定第一個 RC identity：

``` text
v1.0.0-rc.1
```

並明確保留 Python package metadata 所需的 prerelease normalization
boundary，同時維持 human-facing tag / release identity 為
`v1.0.0-rc.1`。

RC governing contract 固定下列核心要求：

-   Step 8.9 formal acceptance 是 Step 8.10 的必要前置條件。
-   RC Acceptance 與 `v1.0.0` GA Acceptance 為兩個獨立 gate。
-   RC Acceptance 採 fail-closed 原則。
-   approved source commit、package version、wheel / sdist metadata、
    checksums、tag 與 GitHub Release 必須描述同一個 RC。
-   artifact-backed verification 不可由 source-checkout-only success
    取代。
-   required artifact-backed skips 不得被視為 final RC evidence。
-   stale artifacts、retargeted published tag 或相同 RC identity 下替換
    artifact 均不允許。
-   RC 期間的變更維持在 release blocker / correctness /
    compatibility / packaging / security / documentation correctness /
    release-test automation 範圍。
-   不預先填入未來 test count、coverage、PR、CI、commit、tag、
    checksum 或 GitHub Release evidence。

目前 Step 8.10 delivery state：

``` text
8.10.1 RC Acceptance Baseline                   Completed
8.10.2 RC Acceptance Contract                   Completed
8.10.3 RC Contract Automation                   Completed
8.10.4 RC Build / Artifact Identity             Completed
8.10.5 RC Artifact-backed Verification          Completed
8.10.6 RC Full Regression / Local Quality Gates Completed
8.10.7 RC GitHub Actions / CI                   Completed
8.10.8 RC Creation / Publication Identity       Completed
8.10.9 Formal RC Acceptance / Post-merge        In Progress
```

Step 8.10.4 新增 governing design：

``` text
docs/releases/v1.0-rc-build-artifact-identity.md
```

並以 focused automation：

``` text
tests/release_readiness/test_v1_rc_build_artifact_identity.py
```

固定 RC package / release identity boundary：

``` text
Python package identity  --- 1.0.0rc1
Human-facing RC identity --- v1.0.0-rc.1
```

Minimum implementation 將 canonical `[project].version` 更新為
`1.0.0rc1`，並使 release identity layer 將 PEP 440 RC syntax
deterministically 映射為 `v1.0.0-rc.1`，同時保持 stable release tag mapping
不變。

Step 8.10.4 fresh artifact evidence：

``` text
Source commit --- 11a997c2b9787cdae34b15818c6170948e89b7fc
Wheel --- openprojectlab-1.0.0rc1-py3-none-any.whl
sdist --- openprojectlab-1.0.0rc1.tar.gz
Twine check --- Passed
Focused verification --- 70 passed, 0 skipped
Wheel SHA-256 --- 5c6a968b5d4225d758ecedc8fa15441c64812cc413ee62d302cf2521eb0b1629
sdist SHA-256 --- 34c2bcc33f0265a8f25d1770ea209472fbcdf12f803217e87574de3f08acef12
Checksum manifest verification --- Passed
```

初次 checksum-manifest verification 曾因 Windows PowerShell 5.1
`Set-Content -Encoding utf8` 產生 UTF-8 BOM 而失敗；改以無 BOM UTF-8
寫入 manifest 後，exact artifact/checksum verification 通過。這是 manifest
encoding issue，不是 artifact identity 或 checksum 計算 defect。

Step 8.10.4 完成時仍未建立或正式接受 `v1.0.0-rc.1`，也未預先接受
`v1.0.0` GA。

Step 8.10.5 隨後建立：

``` text
docs/releases/v1.0-rc-artifact-backed-verification.md
tests/release_readiness/test_v1_rc_artifact_backed_verification.py
```

此 slice 重用既有 packaging、First 15 Minutes、artifact-backed
installed-user E2E 與 integrated package/release identity suites，而不建立
第二套 clean-install framework。

Completion-state artifact-backed evidence：

``` text
Source commit --- 784a139b4afc91779d6b3c76fe35162a0e348261
Wheel --- openprojectlab-1.0.0rc1-py3-none-any.whl
sdist --- openprojectlab-1.0.0rc1.tar.gz
Installed distribution identity --- 1.0.0rc1
Source-checkout isolation --- Passed
Installed opl entry point --- Passed
Packaged runtime resources --- Passed
First 15 Minutes --- Passed
Representative installed-user E2E --- Passed
Integrated release identity --- Passed
Checksum manifest verification --- Passed
Focused completion suite --- 59 passed
Required artifact-backed skips --- 0
```

初次 completion run 因 `OPL_RELEASE_COMMIT_SHA` 仍指向 Step 8.10.4
歷史 source commit `11a997c2b9787cdae34b15818c6170948e89b7fc`，而目前
`HEAD` 已為 `784a139b4afc91779d6b3c76fe35162a0e348261`，因此 fail-closed identity check 正確失敗。
重新從目前 source fresh build RC artifacts、重建無 BOM checksum manifest，
並重新設定 `OPL_TEST_WHEEL`、`OPL_TEST_DIST_DIR`、
`OPL_TEST_CHECKSUM_MANIFEST` 與 `OPL_RELEASE_COMMIT_SHA` 後，
completion suite 取得 59 passed、0 required skips。

因此 Step 8.10.5 --- RC Artifact-backed Verification 已完成。仍未建立
`v1.0.0-rc.1` tag、GitHub Release 或正式 RC acceptance。

Step 8.10.6 隨後完成 RC Full Regression / Local Quality Gates，從目前
completion-state repository 取得 fresh local evidence：

``` text
Full regression --- 1881 passed, 1 deselected
Failures / errors --- 0
Coverage --- 90.90%
Required coverage --- 67.0% --- Passed
Required artifact-backed skips --- 0
git diff --check --- Passed
Ruff --- Passed
Ruff Format --- Passed
pre-commit --- Passed
```

這組 `1881 / 90.90%` 不沿用 Step 8.10.5 focused suite，也不以
source-only success 取代 artifact-backed evidence。Step 8.10.6 完成時仍未建立
`v1.0.0-rc.1` tag、GitHub Release 或正式 RC acceptance。

Step 8.10.7 RC GitHub Actions / CI 已完成。PR #152 的 required GitHub
Actions jobs：

``` text
Quality checks --- Passed
Packaging artifact verification --- Passed
```

均通過，並完成 squash merge、main synchronization 與 lightweight
post-merge RC consistency verification。

Step 8.10.8 建立 publication governing contract：

``` text
docs/releases/v1.0-rc-creation-publication-identity.md
```

並透過 contract PR #153 完成 reviewed publication boundary。PR #153 CI
通過後 squash merged，merge 後 synchronized `main` 的 approved publication
commit 為：

``` text
b5958edbbf0e3279ed74fa0e3aee13e893c5dfc8
```

從該 commit fresh rebuild final RC artifacts、通過 Twine、checksum 與
artifact-backed publication verification後，建立 annotated tag：

``` text
v1.0.0-rc.1
```

Remote peeled tag target 驗證為：

``` text
b5958edbbf0e3279ed74fa0e3aee13e893c5dfc8
```

因此 tag target 與 approved publication commit 一致。

GitHub Release 採 draft-first 建立，draft identity 驗證完成後才發布為
prerelease。最終 publication state：

``` text
Package version --- 1.0.0rc1
Release tag --- v1.0.0-rc.1
Target commit --- b5958edbbf0e3279ed74fa0e3aee13e893c5dfc8
Draft --- false
Prerelease --- true
Wheel --- openprojectlab-1.0.0rc1-py3-none-any.whl
Wheel SHA-256 --- 0dbea1bdbf972a91c25aeb84e5441cb308df866b269ab8f7feea8d099d93d337
sdist --- openprojectlab-1.0.0rc1.tar.gz
sdist SHA-256 --- 37e2593a4693b7f038da1b9f0b3ae83643fff2d989992a185a3cdc9022098ea2
SHA256SUMS.txt asset SHA-256 --- 0b56ca72ab9aec34afabcf3fb00d170522a923d4e0120df3bca6234061bb3c4f
Post-publication identity re-read --- Passed
```

因此 Step 8.10.8 --- RC Creation / Publication Identity 已完成。Published
`v1.0.0-rc.1` 現在是 immutable RC identity；不得 retarget tag 或在相同
RC identity 下替換 artifact bytes。

Step 8.10.9 Formal RC Acceptance / Post-merge 已啟動，新增：

``` text
docs/releases/v1.0-rc-acceptance-record.md
tests/release_readiness/test_v1_rc_formal_acceptance.py
```

Formal-acceptance candidate focused suite：

``` text
41 passed
```

Step 8.10.9 acceptance candidate 隨後透過 PR #154 完成 reviewed closure。
PR #154 required CI 通過後 squash merged，實際 acceptance merge commit：

``` text
d37a3d84161e66e98ebbff2aafaf1a14e27f865c
```

同步 `main` 後完成 post-merge consistency 與 cross-document terminal-state
alignment。Published RC identity 保持不變：

``` text
RC identity --- v1.0.0-rc.1
Published source SHA --- b5958edbbf0e3279ed74fa0e3aee13e893c5dfc8
Acceptance PR --- #154
Acceptance PR CI --- Passed
Acceptance squash merge --- Completed
main synchronization --- Completed
post-merge consistency verification --- Completed
cross-document terminal-state alignment --- Completed
Formal RC Acceptance --- Accepted
v1.0.0 GA Acceptance --- Not Accepted
```

因此 **Step 8.10 --- RC Acceptance 已正式 Accepted**，Milestone 8 的 RC
Acceptance lifecycle 完成。Acceptance merge commit 只記錄正式接受證據，
不會 retarget 已發布的 `v1.0.0-rc.1` 或替換其 artifact bytes。

下一個獨立 release gate 為 `v1.0.0` GA Acceptance。

------------------------------------------------------------------------

# v1.0 GA Acceptance

Step 8.10 RC Acceptance 正式完成後，OPL 進入獨立的 `v1.0.0` GA
Acceptance lifecycle。

GA.1 已完成 acceptance baseline 與 RC evidence review。Reviewed evidence
未發現已記錄且尚未解決的 GA blocker，也沒有目前 evidence 所要求的 GA
correction；相關結論明確限定於 reviewed evidence，而不是 universal
zero-defect claim。

GA.3 完成 stable version / artifact identity transition：

``` text
Canonical package version --- 1.0.0
Canonical GA tag mapping --- v1.0.0
```

Historical RC identity `1.0.0rc1 / v1.0.0-rc.1` 保持 immutable historical
evidence，不因 GA version transition 被改寫。

GA.4 Artifact-backed Verification 已完成。GA-specific coordination 與既有
integrated package identity、installed-user E2E、First 15 Minutes 等
artifact-backed authorities 共同驗證 stable wheel：

``` text
GA.4 focused artifact-backed suite --- 30 passed
Required GA artifact-backed skips --- 0
Installed distribution version --- 1.0.0
Source-checkout isolation --- Passed
Installed opl entry point --- Passed
Packaged runtime resources --- Passed
First 15 Minutes --- Passed
Representative installed-user E2E --- Passed
Integrated package / release identity --- Passed
Checksum manifest verification --- Passed
```

GA.5 隨後取得 fresh full-regression evidence：

``` text
Full regression --- 1980 passed, 4 skipped, 1 deselected
Failures / errors --- 0
Coverage --- 90.90%
Required coverage --- 67.0% --- Passed
```

4 個 skipped tests 全部來自 historical RC artifact-backed verification；
目前 artifact inputs 指向 `openprojectlab-1.0.0-py3-none-any.whl`，因此這些
RC tests 正確拒絕把 GA artifact 當成 RC evidence。它們不屬於 GA.4
required artifact-backed skips。

GA.5 的 local quality gates 隨後亦全部通過：

``` text
Required GA artifact-backed skips --- 0
git diff --check --- Passed
Ruff --- Passed
Ruff Format --- Passed
pre-commit --- Passed
```

因此 **GA.5 --- Full Regression / Local Quality Gates 已完成**。

GA.6 GitHub Actions / CI 隨後完成，required jobs 均通過：

``` text
Quality checks --- Passed
Packaging artifact verification --- Passed
```

GA.7 GA Creation / Publication Identity 亦已完成。Stable publication identity：

``` text
Canonical package version --- 1.0.0
Published tag --- v1.0.0
GitHub Release draft --- false
GitHub Release prerelease --- false
Draft-first verification --- Passed
Post-publication identity re-read --- Passed
```

Published stable identity 與 historical RC identity 保持分離；既有
`v1.0.0-rc.1` 不被 retarget 或改寫。

GA.8 Formal GA Acceptance / Post-merge 已完成。Pre-acceptance contract
suite 先以：

``` text
43 passed
```

通過；acceptance PR required CI 隨後全綠並完成 squash merge。同步
`main` 後，terminal-main identity 為：

``` text
HEAD == origin/main == d13382c359873c2a9eb8fb9cf6d39e32636d5fc1
```

最終 post-merge full regression：

``` text
2004 passed, 4 skipped, 1 deselected
Failures / errors --- 0
Coverage --- 90.90%
Required coverage --- 67.0% --- Passed
pre-commit --- Passed
Post-merge consistency verification --- Completed
```

4 個 skips 仍為 historical RC artifact-backed tests 正確拒絕 GA wheel，
不構成 GA-required skip 或 acceptance blocker。

因此 GA lifecycle terminal state 為：

``` text
GA.1 --- Completed
GA.2 --- Completed
GA.3 --- Completed
GA.4 --- Completed
GA.5 --- Completed
GA.6 --- Completed
GA.7 --- Completed
GA.8 --- Completed
Formal v1.0.0 GA Acceptance --- Accepted
```

Published `v1.0.0` tag、stable GitHub Release 與 GA artifact source identity
保持 immutable；GA.8 acceptance merge 不 retarget tag，也不替換已發布
artifact bytes。

------------------------------------------------------------------------

# v1.1 Planning Baseline

OpenProjectLab `v1.0.0` 已完成 stable publication、Formal GA Acceptance、
post-merge consistency 與 repository branch hygiene。`v1.0.0` tag 與既有
artifact/source identity 保持 immutable。

2026-08-20，專案開始 v1.1 Planning Baseline，以 **Operational CLI
Expansion** 作為 proposed release theme。此 baseline 僅啟動設計、文件與
fail-closed planning automation，不宣告 AI CLI 或 Marketplace CLI 已完成。

Governing contract：

``` text
docs/releases/v1.1-planning-baseline.md
```

目前狀態：

``` text
v1.0.0 GA lifecycle --- Completed
Repository hygiene --- Completed
v1.1 Planning Baseline --- In Progress
Marketplace CLI --- Not Started
AI CLI --- Not Started
Formal v1.1 Acceptance --- Not Accepted
```

v1.1 必須維持 Step 8.2 frozen Stable subset 與 Step 8.6 compatibility /
deprecation policy。Marketplace CLI 僅能建立於 deterministic local
Marketplace contracts；AI CLI 僅能建立於 provider-independent AI
boundary。Remote Marketplace、automatic activation、signing/trust、
dependency resolution、ratings/reviews、monetization、AI Provider
Marketplace、AI Refactoring Assistant、streaming/tool calling 與
generalized cross-Generator rollback 繼續保持 Deferred。

Planning baseline 不預填未來 test count、coverage、PR、CI、commit、tag、
checksum、release 或 acceptance evidence。

Governing baseline 隨後透過 PR #164 完成reviewed integration。Required
Quality checks 與 Packaging artifact verification 均通過，PR #164 squash
merge commit 為：

``` text
33c367b989014c34c162f326ee825f3fe8f4c8e6
```

同步 `main` 並完成lightweight post-merge consistency verification後，
專案開始獨立的v1.1.1 Planning Baseline acceptance closure：

``` text
v1.1 Planning Baseline --- In Progress
v1.1.1 Acceptance Closure --- In Progress
Formal v1.1 Planning Baseline Acceptance --- Not Accepted
Marketplace CLI --- Not Started
AI CLI --- Not Started
Formal v1.1 Acceptance --- Not Accepted
```

Acceptance PR required CI、squash merge、main synchronization、post-merge
consistency與terminal documentation alignment仍為Pending，不得由PR #164
或更早的passing evidence替代。

Acceptance candidate 隨後透過 PR #165 完成reviewed closure。Required CI
通過後，PR #165 squash merge commit 為：

``` text
97dac1eca516e7b91e2f5bdfbe6da84b7a32215c
```

同步 `main` 後，post-merge focused planning/acceptance suite 以 `15 passed`
完成；`git diff --check`、pre-commit與working-tree consistency亦通過。
Terminal documentation alignment完成後，v1.1.1 terminal state為：

``` text
v1.1 governing baseline PR #164 --- Merged
v1.1 acceptance PR #165 --- Merged
v1.1.1 Planning Baseline --- Accepted
Formal v1.1 Planning Baseline Acceptance --- Accepted
Marketplace CLI --- Not Started
AI CLI --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.2 CLI Public Contract Design
```

Planning acceptance只接受scope、non-goals、compatibility boundary與delivery
sequence，不代表任何CLI implementation或v1.1 release acceptance。

## v1.1.2 --- CLI Public Contract Design

完成 v1.1.1 terminal alignment 後，專案開始 v1.1.2 CLI Public Contract
Design。新增 governing design：

``` text
docs/releases/v1.1-cli-public-contract.md
```

此 slice 先固定所有後續 v1.1 CLI 共用的 compatibility 與設計邊界：既有
10 個 reviewed v1 command、installed `opl` entry point、legacy
`opl --list`、既有 required arguments，以及 generation commands 的
`--dry-run`、`--force`、`--no-manifest` 均繼續受保護。

`opl marketplace ...` 與 `opl ai ...` 目前僅是 reserved command-family
identity。v1.1.2 不得把兩者註冊到 production parser；Marketplace CLI
contract 屬於 v1.1.3、implementation 屬於 v1.1.4，AI CLI contract 屬於
v1.1.5、implementation 屬於 v1.1.6。

Exit-code design 只保留目前已驗證的 broad contract：成功為 `0`，argparse
usage failure 或 production-handled validation/runtime/filesystem failure 為
`2`。本階段不宣告更細的 Stable exit taxonomy、exact human-readable error
wording 或 production `--json` schema。

新增 fail-closed design automation：

``` text
tests/integration/test_v1_1_cli_public_contract.py
```

Focused v1/v1.1 CLI public-contract suite 已完成：

``` text
40 passed
Failures / errors --- 0
```

此 focused evidence 不替代尚未執行的 full regression、coverage、local
quality gates、PR、CI、merge、main synchronization 或 post-merge
consistency。Current state 保持：

``` text
v1.1.1 Planning Baseline --- Accepted
v1.1.2 CLI Public Contract Design --- In Progress
v1.0 CLI Stable Surface --- Preserved
Marketplace CLI Contract --- Not Started
Marketplace CLI Implementation --- Not Started
AI CLI Contract --- Not Started
AI CLI Implementation --- Not Started
Formal v1.1 CLI Public Contract Acceptance --- Not Accepted
Formal v1.1 Acceptance --- Not Accepted
```

Governing design 隨後透過 PR #167 完成 reviewed integration。Required CI
run `32360278259` 成功，PR #167 squash merge commit 為：

``` text
2727bba27a1438b949870f9dee7df4aa16d43244
```

此 merge 只完成 governing design，不等同 formal acceptance。專案接著建立
`docs/releases/v1.1-cli-public-contract-acceptance.md` 與 fail-closed
acceptance automation，開始 v1.1.2 acceptance closure。Acceptance-state
focused/full-regression/quality execution、acceptance PR/CI/merge、main
synchronization、post-merge consistency 與 terminal documentation alignment
仍為 Pending；Formal v1.1 CLI Public Contract Acceptance 與 Formal v1.1
Acceptance 均保持 `Not Accepted`。

Acceptance-state focused suite 隨後以 `48 passed` 完成；full regression 為
`2008 passed, 32 skipped, 1 deselected in 22.37s`，required 67.0% coverage
gate、`git diff --check` 與 pre-commit 均通過。Acceptance PR #168 required
CI run `32362619408` 成功，並於 2026-08-20T11:13:17Z squash merge 為：

``` text
044e80ae39b01b5006663e44ea4db0f4a98a8482
```

此時仍須同步 `main`、完成 post-merge focused/quality consistency 與 clean
working-tree verification，之後才能執行 terminal documentation alignment。
因此 Formal v1.1 CLI Public Contract Acceptance 目前仍為 `Not Accepted`。

Local `main` 隨後與 `origin/main` 同步至 acceptance merge
`044e80ae39b01b5006663e44ea4db0f4a98a8482`，working tree clean；已發布
`v1.0.0` tag target 仍為
`d469b41b898d80811a14a423d08b09d0b51bc189`。Main synchronization gate 已
完成，剩餘 gate 為 post-merge focused/local consistency 與 terminal
documentation alignment。

Synchronized-main post-merge focused CLI acceptance suite 隨後以
`48 passed in 0.22s` 通過。Post-merge local quality gates 與最終 clean-tree
consistency 尚待確認，因此 terminal Accepted alignment 仍未開始。

最終 `git diff --check`、pre-commit、pytest hook 與 clean working tree 均
通過，完成 post-merge consistency 與 terminal documentation alignment。
v1.1.2 terminal state 為：

``` text
v1.1.2 CLI Public Contract Design --- Accepted
Formal v1.1 CLI Public Contract Acceptance --- Accepted
Marketplace CLI Contract --- Not Started
Marketplace CLI Implementation --- Not Started
AI CLI Contract --- Not Started
AI CLI Implementation --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.3 Marketplace CLI Contract
```

## v1.1.3 --- Marketplace CLI Contract

完成 v1.1.2 terminal alignment 後，專案開始 v1.1.3 Marketplace CLI
Contract。新增 governing design：

``` text
docs/releases/v1.1-marketplace-cli-contract.md
```

此 slice 僅設計 deterministic、local-first Marketplace CLI contract。
Proposed command surface 為 `versions`、`inspect`、`verify` 與 `install`；既有
repository 沒有全域列舉能力，因此本階段不虛構 `opl marketplace list`。

Catalog 與 payload 均由明確本機路徑提供。Artifact 使用 exact
`namespace/name@MAJOR.MINOR.PATCH` coordinate；verification pipeline 固定為
exact repository lookup、local acquisition 與 SHA-256 integrity
verification。Installation 維持 in-memory、non-activating、non-persistent；
`--dry-run` 不呼叫 installer。Remote access、dependency resolution、automatic
activation、trust/signing、ratings/reviews 與 monetization 仍為 Deferred。

新增 fail-closed contract automation：

``` text
tests/integration/test_v1_1_marketplace_cli_contract.py
```

Local verification 已完成：

``` text
Focused Marketplace contract suite --- 35 passed
Pre-commit --- Passed
Full regression --- 2018 passed, 32 skipped, 1 deselected in 23.05s
Failures / errors --- 0
```

上述證據允許建立 governing contract PR，但不等同 contract acceptance 或
implementation。Current state 保持：

``` text
v1.1.3 Marketplace CLI Contract --- In Progress
Marketplace CLI Contract --- Not Accepted
Marketplace CLI Implementation --- Not Started
AI CLI Contract --- Not Started
AI CLI Implementation --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Governing PR #170 --- Merged
Governing merge --- 5f63bd3dc438ba1ea5e10b8225c761964c1819bc
Governing required CI evidence --- Pending confirmation
main synchronization --- Completed
Next --- v1.1.3 Acceptance Closure
```

Governing contract PR #170 隨後完成 squash merge，merge commit 為：

``` text
5f63bd3dc438ba1ea5e10b8225c761964c1819bc
```

Local `main` 與 `origin/main` 已同步至此 commit，working tree clean。專案接著
新增 `docs/releases/v1.1-marketplace-cli-contract-acceptance.md` 與
fail-closed acceptance automation，開始獨立的 v1.1.3 Acceptance Closure。

Governing merge 不等同 contract acceptance。Fresh acceptance-state focused
suite、full regression、coverage、local quality gates、acceptance PR/CI/merge、
main synchronization、post-merge consistency 與 terminal documentation
alignment 仍為 Pending；Marketplace CLI production implementation 仍為 Not
Started。

Fresh acceptance-state execution 隨後完成 focused suite `84 passed`，以及
full regression `1533 passed, 11 skipped, 1 deselected in 11.00s`；兩者皆為
zero failures/errors。Pre-commit 的全部 hooks（包含 Ruff、Ruff Format 與
pytest）亦通過。

目前 supplied evidence 未包含 required coverage 結果、`git diff --check`
輸出或 PR #170 governing required CI 結果，因此三者維持 Pending
confirmation，不由成功的 pytest 或 pre-commit 間接推定。Acceptance
PR/CI/merge、post-merge consistency 與 terminal alignment 亦尚未完成。

``` text
v1.1.3 governing contract PR #170 --- Merged
Governing merge --- 5f63bd3dc438ba1ea5e10b8225c761964c1819bc
main synchronization --- Completed
v1.1.3 Acceptance Closure --- In Progress
Acceptance-state focused suite --- 84 passed
Acceptance-state full regression --- 1533 passed, 11 skipped, 1 deselected
Acceptance-state execution time --- 11.00s
Acceptance-state pre-commit --- Passed
Required coverage / git diff --check --- Pending confirmation
Acceptance PR / CI / merge --- Pending
Marketplace CLI Contract --- Not Accepted
Marketplace CLI Implementation --- Not Started
Formal v1.1 Acceptance --- Not Accepted
```

Acceptance PR #171 subsequently passed its required CI and was squash merged
as `02ed8569bbd5a6c12632783186220954b2b99f12`. After synchronizing `main`, the
post-merge focused suite, local quality gates, repository consistency checks,
and terminal documentation alignment completed successfully. No production
Marketplace CLI implementation was introduced by this acceptance closure.

The v1.1.3 terminal state is therefore:

``` text
v1.1.3 Marketplace CLI Contract --- Accepted
Marketplace CLI Contract Acceptance --- Accepted
Acceptance PR #171 --- Merged
Acceptance merge --- 02ed8569bbd5a6c12632783186220954b2b99f12
Marketplace CLI Implementation --- Not Started
AI CLI Contract --- Not Started
AI CLI Implementation --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.4 Marketplace CLI Implementation
```

## v1.1.4 --- Marketplace CLI Implementation

After v1.1.3 terminal alignment, the project started v1.1.4 with a Design
First implementation baseline. This initial slice introduces no production
parser registration or command handler. It records the exact adapter
architecture, implementation sequence, test matrix, bilingual documentation
impact, executable-demo boundary, and Code Review Checklist before product
code is allowed to begin.

The production audit confirmed that `MarketplaceRepository` has an internal
deterministic `list_artifacts()` operation. The accepted CLI contract remains
narrower: it exposes only `versions`, `inspect`, `verify`, and `install`.
Therefore internal global enumeration does not authorize or imply an
`opl marketplace list` command.

``` text
v1.1.3 Marketplace CLI Contract --- Accepted
v1.1.4 Marketplace CLI Implementation --- In Progress
Implementation baseline / architecture --- Complete
Internal catalog and parsing adapters --- Complete
Implementation PR #174 --- Merged
Implementation merge --- 0ac32017b1420464c7c52a2b63993fc4e27a63b4
Production parser registration --- Not Started
Marketplace CLI command handlers --- Not Started
EN / zh-TW Marketplace CLI manuals --- Not Started
Canonical executable use-case demo extension --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.4.3 versions / inspect
```

Implementation PR #174 passed required CI and was squash merged as
`0ac32017b1420464c7c52a2b63993fc4e27a63b4`. After synchronizing `main`, the
focused post-merge adapter verification and repository consistency gates
passed. Terminal documentation alignment therefore completes v1.1.4.2 without
registering the production parser, adding command handlers, or expanding the
accepted command inventory. The next active slice is v1.1.4.3 `versions /
inspect`.

The project subsequently started v1.1.4.3 with internal `versions` and
`inspect` query services only. They reuse strict v1.1.4.2 parsing and the
existing repository operations, do not use global enumeration, and do not
acquire, verify, install, render final output, or register the production
parser. Current state is `v1.1.4.3 versions / inspect --- In Progress`.

Implementation PR #176 subsequently passed required CI and was squash merged
as `d1fbfbbd60c9d7ae14efdff443ff550032f279c2`. After synchronizing `main`, the
focused versions/inspect suite, Marketplace regression, production-parser
absence check, and repository consistency gates passed. Terminal documentation
alignment completes v1.1.4.3 with this state:

``` text
v1.1.4 Marketplace CLI Implementation --- In Progress
v1.1.4.3 versions / inspect --- Complete
Implementation PR #176 --- Merged
Implementation merge --- d1fbfbbd60c9d7ae14efdff443ff550032f279c2
Production Parser Registration --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.4.4 verify / Safe Payload Acquisition
```

The project subsequently started v1.1.4.4 with safe local payload acquisition
and SHA-256 verification only. Absolute, drive-prefixed, traversing, missing,
directory, and root-escaping references fail before installation. Network
fallback, installation, activation, final rendering, and production parser
registration remain outside this slice.

Implementation PR #178 subsequently passed required CI and was squash merged
as `ec0a77cd19d8783e2877228ece0a9e006579436e`. After synchronizing `main`, the
focused safe-verification suite, Marketplace regression, production-parser
absence check, and repository consistency gates passed. Terminal documentation
alignment completes v1.1.4.4 with this state:

``` text
v1.1.4 Marketplace CLI Implementation --- In Progress
v1.1.4.4 verify / Safe Payload Acquisition --- Complete
Implementation PR #178 --- Merged
Implementation merge --- ec0a77cd19d8783e2877228ece0a9e006579436e
Installation --- Not Started
Production Parser Registration --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.4.5 install / dry-run / No-partial-state
```

The project subsequently started v1.1.4.5 with internal installation
orchestration only. Lookup, safe acquisition, and integrity verification must
complete before the existing installer is called. Dry-run returns verified
evidence without installation, and all earlier failure paths leave installer
state unchanged. Activation, persistence, final rendering, and production
parser registration remain outside this slice.

Implementation PR #180 subsequently passed required CI and was squash merged
as `4de1347edc09d959cd8b00d6acc6f459defd938e`. After synchronizing `main`, the
focused Marketplace implementation suite completed with `83 passed, 1
skipped`; the production-parser absence check remained `False`. Terminal
documentation alignment completes v1.1.4.5 with this state:

``` text
v1.1.4 Marketplace CLI Implementation --- In Progress
v1.1.4.5 install / dry-run / No-partial-state --- Complete
Implementation PR #180 --- Merged
Implementation merge --- 4de1347edc09d959cd8b00d6acc6f459defd938e
Production Parser Registration --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.4.6 Deterministic JSON and Diagnostics
```

The project subsequently started v1.1.4.6 with internal rendering and
diagnostic adapters only. Successful human output is isolated to stdout;
handled diagnostics are isolated to stderr with exit code `2`. JSON success
uses one compact, deterministic UTF-8 schema-version-1 object and handled
failures emit no success JSON document. Production parser registration remains
outside this slice.

Implementation PR #182 subsequently passed required CI and was squash merged
as `b415f7f02f9c81d92341a010c449ff619d97b8cd`. After synchronizing `main`, the
focused JSON/diagnostics and Marketplace implementation checks passed, and the
production-parser absence check remained `False`. Terminal documentation
alignment completes v1.1.4.6 with this state:

``` text
v1.1.4 Marketplace CLI Implementation --- In Progress
v1.1.4.6 Deterministic JSON and Diagnostics --- Complete
Implementation PR #182 --- Merged
Implementation merge --- b415f7f02f9c81d92341a010c449ff619d97b8cd
Production Parser Registration --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.4.7 Production Parser Registration
```

The project subsequently started v1.1.4.7 and registered the accepted
deterministic-local Marketplace command family in the production parser. The
inventory is exactly `versions`, `inspect`, `verify`, and `install`; no global
Marketplace `list` command exists. Handlers reuse the reviewed catalog,
query, safe verification, installation, JSON, and diagnostic adapters while
preserving every v1 command and legacy `opl --list` behavior. This slice does
not add activation, persistence, remote access, or AI CLI behavior.

Implementation PR #184 subsequently passed required CI and was squash merged
as `85f8ec822270fd3c993fc0b23fa70367681bcb0c`. After synchronizing `main`, the
production parser and documentation functional-parity smoke completed with `33
passed`; the working tree and repository consistency gates remained clean.
Terminal documentation alignment completes v1.1.4.7 with this state:

``` text
v1.1.4 Marketplace CLI Implementation --- In Progress
v1.1.4.7 Production Parser Registration --- Complete
Implementation PR #184 --- Merged
Implementation merge --- 85f8ec822270fd3c993fc0b23fa70367681bcb0c
Marketplace CLI Command Handlers --- Complete
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.4.8 EN / zh-TW User Manual Updates
```

The project subsequently started v1.1.4.8 with functional EN / zh-TW
Marketplace CLI documentation parity. Both manuals cover the exact production
inventory, identity/coordinate syntax, explicit local catalog and payload-root
inputs, deterministic JSON, dry-run, failure-before-side-effect behavior,
non-activation, and Deferred remote/trust/dependency capabilities. Executable
documentation automation keeps the examples aligned with production behavior.

Documentation PR #186 subsequently passed required CI and was squash merged
as `6a3a98d22ed2e2a995bb8d497ae5f7ff5607a0b4`. After synchronizing `main`, the
bilingual structure, parity, functional-parity, executable-documentation, and
production-parser smoke remained green. Terminal documentation alignment
completes v1.1.4.8 with this state:

``` text
v1.1.4 Marketplace CLI Implementation --- In Progress
v1.1.4.8 EN / zh-TW User Manual Updates --- Complete
Documentation PR #186 --- Merged
Documentation merge --- 6a3a98d22ed2e2a995bb8d497ae5f7ff5607a0b4
EN / zh-TW Marketplace CLI Manuals --- Complete
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.4.9 Full Regression / CI / Formal Acceptance
```

The project subsequently started v1.1.4.9 from synchronized `main` at
`f7910d51c49c74614381491458414739c47d5d74`. The acceptance-candidate full
regression completed with `2150 passed, 33 skipped, 1 deselected` in 23.77s
and 90.74% total coverage; the Marketplace-focused regression completed with
`160 passed, 1 skipped` in 1.07s. The skips are explicit platform or
artifact-gate conditions rather than failures.

The Formal v1.1 acceptance record and fail-closed automation are now proposed
for review. This evidence establishes acceptance-candidate readiness only;
Formal v1.1 Acceptance remains Not Accepted until the acceptance PR, required
CI, squash merge, synchronized `main`, post-merge verification, and terminal
documentation alignment are complete.

Acceptance PR #188 subsequently passed required CI and was squash merged as
`a89d0d4e7b8fd068c1c4e2b841489bf211efbf28`. After synchronizing `main`, the
post-merge focused verification completed with `56 passed` in 0.30s and the
full regression completed with `2158 passed, 33 skipped, 1 deselected` in
23.41s with 90.74% total coverage. The exact Marketplace inventory remained
`versions`, `inspect`, `verify`, and `install`; local quality and working-tree
consistency gates remained clean.

Terminal documentation alignment therefore completes v1.1.4.9 and closes the
Marketplace CLI implementation acceptance sequence without skipping the
remaining v1.1 delivery stages:

``` text
v1.1.4 Marketplace CLI Implementation --- Complete
v1.1.4.9 Full Regression / CI / Formal Acceptance --- Complete
Marketplace CLI Acceptance PR #188 --- Merged
Acceptance merge --- a89d0d4e7b8fd068c1c4e2b841489bf211efbf28
Marketplace CLI Implementation Acceptance --- Accepted
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.5 AI CLI Contract
```

The project subsequently started v1.1.5 as a design-only AI CLI contract.
The proposed surface maps exactly to the existing course generation, review,
documentation, and template-completion application services. Each workflow
accepts one explicit UTF-8 JSON request and requires exactly one execution
source: a deterministic local response file or an explicitly selected live
provider. Local response-file execution is the Stable core path; live-provider
invocation remains Experimental, opt-in, credential-isolated, and outside
normal deterministic CI.

No `ai` parser registration, handler, provider registry, credential schema,
filesystem mutation, chat workflow, refactoring assistant, streaming, tool
calling, or autonomous action is implemented by this contract slice.

------------------------------------------------------------------------

# 我們的願景

OpenProjectLab 的目標不是建立更多程式，而是建立：

> **更容易維護、更容易理解、更容易演進的軟體工程文化。**

> Build projects, not just code.
------------------------------------------------------------------------

## v1.1.5 AI CLI Contract Terminal Alignment

``` text
v1.1.5 AI CLI Contract --- Accepted
Contract PR #190 --- Merged
Contract merge --- cf3da5a937bda4a478b5530660cfc0054e2e42c2
Post-merge contract verification --- 70 passed
AI CLI Production Registration --- Not Started
v1.1.6 AI CLI Implementation --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6 AI CLI Implementation
```

------------------------------------------------------------------------

## v1.1.6 AI CLI Implementation Baseline

    v1.1.5 AI CLI Contract --- Accepted
    v1.1.6 AI CLI Implementation --- In Progress
    v1.1.6.1 Implementation Baseline --- In Progress
    generator/cli/ai.py --- Not Implemented
    AI CLI Shared Infrastructure --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.2 Shared Request / Local-response Infrastructure
------------------------------------------------------------------------

## v1.1.6.1 AI CLI Implementation Baseline Terminal Alignment

    v1.1.6.1 Implementation Baseline --- Accepted
    Baseline PR #192 --- Merged
    Baseline merge --- 7520da65963d935257f476ea5e0bdd79bd519e3f
    Post-merge verification --- 75 passed
    v1.1.6 AI CLI Implementation --- In Progress
    AI CLI Shared Infrastructure --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.2 Shared Request / Local-response Infrastructure

------------------------------------------------------------------------

## v1.1.6.2 AI CLI Shared Infrastructure

    v1.1.6.1 Implementation Baseline --- Accepted
    v1.1.6.2 Shared Request / Local-response Infrastructure --- In Progress
    AI CLI course handler --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.3 course handler

------------------------------------------------------------------------

## v1.1.6.2 AI CLI Shared Infrastructure Terminal Alignment

    v1.1.6.2 Shared Request / Local-response Infrastructure --- Accepted
    Implementation PR #194 --- Merged
    Implementation merge --- 746bff69df824a6fa56051ccd80beb43acf93e73
    Post-merge verification --- 91 passed
    v1.1.6 AI CLI Implementation --- In Progress
    AI CLI course handler --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.3 course handler

------------------------------------------------------------------------

## v1.1.6.3 AI CLI Course Handler

    v1.1.6.2 Shared Request / Local-response Infrastructure --- Accepted
    v1.1.6.3 course handler --- In Progress
    course service --- AICourseGenerationService.generate_course(request)
    course JSON projection --- Deterministic
    AI CLI review handler --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.4 review handler

### Code Review Checklist

- Existing AICourseGenerationService and mapper remain authoritative.
- JSON keys and Week ordering are deterministic.
- Failure emits no success output.
- No filesystem mutation, credentials, or network access is introduced.
- The production ai parser remains unregistered.

------------------------------------------------------------------------

## v1.1.6.3 AI CLI Course Handler Terminal Alignment

    v1.1.6.3 course handler --- Accepted
    Implementation PR #196 --- Merged
    Implementation merge --- 58abbabbccf3bd54ea54032ecc5c73a34bb0f0f2
    Post-merge verification --- 109 passed
    v1.1.6 AI CLI Implementation --- In Progress
    AI CLI review handler --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.4 review handler

------------------------------------------------------------------------

## v1.1.6.4 AI CLI Review Handler

    v1.1.6.3 course handler --- Accepted
    v1.1.6.4 review handler --- In Progress
    review service --- AIReviewService.review(request)
    review JSON projection --- Deterministic / ordered
    AI CLI document handler --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.5 document handler

### Code Review Checklist

- Existing AIReviewService and mapper remain authoritative.
- Finding order and JSON keys are deterministic.
- Failure emits no success output.
- No filesystem mutation, credentials, or network access is introduced.
- The production ai parser remains unregistered.

------------------------------------------------------------------------

## v1.1.6.4 AI CLI Review Handler Terminal Alignment

    v1.1.6.4 review handler --- Accepted
    Implementation PR #198 --- Merged
    Implementation merge --- b78d68b86f7829c48c4bdc696d09a721bdcb35c5
    Post-merge verification --- 113 passed
    v1.1.6 AI CLI Implementation --- In Progress
    AI CLI document handler --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.5 document handler

------------------------------------------------------------------------

## v1.1.6.5 AI CLI Document Handler

    v1.1.6.4 review handler --- Accepted
    v1.1.6.5 document handler --- In Progress
    document service --- AIDocumentationService.generate(request)
    document JSON projection --- Deterministic / non-persistent
    AI CLI template handler --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.6 template handler

### Code Review Checklist

- Existing AIDocumentationService and mapper remain authoritative.
- Title, format, and content projection is deterministic.
- Handler returns content but never writes a documentation file.
- Failure emits no success output.
- No filesystem mutation, credentials, or network access is introduced.
- The production ai parser remains unregistered.

------------------------------------------------------------------------

## v1.1.6.5 AI CLI Document Handler Terminal Alignment

    v1.1.6.5 document handler --- Accepted
    Implementation PR #200 --- Merged
    Implementation merge --- 86d8cee44fdbcdb3785155218fecb5c016994cf0
    Post-merge verification --- 118 passed
    v1.1.6 AI CLI Implementation --- In Progress
    AI CLI template handler --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.6 template handler

------------------------------------------------------------------------

## v1.1.6.6 AI CLI Template Handler

    v1.1.6.5 document handler --- Accepted
    v1.1.6.6 template handler --- In Progress
    template service --- AITemplateCompletionService.complete(request)
    template projection --- Deterministic / non-applying / non-persistent
    Experimental live-provider boundary --- Not Started
    AI CLI Production Registration --- Not Started
    Formal v1.1 Acceptance --- Not Accepted
    Next --- v1.1.6.7 Experimental provider opt-in boundary

### Code Review Checklist

- Existing AITemplateCompletionService and mapper remain authoritative.
- Template name, content, and context-key ordering are deterministic.
- Handler never applies or persists template content.
- Failure emits no success output.
- No credentials or network access is introduced.
- The production ai parser remains unregistered.

<!-- v1.1.6.6-template-handler-terminal-alignment-pr202 -->

## v1.1.6.6 AI CLI Template Handler Terminal Alignment

v1.1.6.6 Template Handler --- Accepted
Implementation PR #202 --- Merged
Implementation merge --- 1ecf3c0b843385c2deee3e849e8f1b9fbd6463bf
Post-merge focused verification --- 123 passed
v1.1.6 AI CLI Implementation --- In Progress
Experimental Provider Opt-in Boundary --- Not Started
AI CLI Production Registration --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6.7 Experimental Provider Opt-in Boundary

The template handler remains unregistered production infrastructure. The
terminal alignment does not register the i parser, resolve a live provider,
apply generated template content, or mutate the filesystem through AI output.

<!-- v1.1.6.7-experimental-provider-opt-in-boundary -->

## v1.1.6.7 Experimental Provider Opt-in Boundary

v1.1.6.7 Experimental Provider Opt-in Boundary --- In Progress
Provider Resolution --- Injection Only
Supported Experimental Provider --- openai
SDK Import / Environment Lookup --- Deferred to Composition Root
Provider Handler Wiring --- Not Started
AI CLI Production Registration --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6.7 Implementation Verification / PR / CI

The candidate introduces an explicit, fail-closed provider resolver. Unknown
providers, absent client factories, and absent API keys fail before client
construction. Existing deterministic local-response handlers remain unchanged.

<!-- v1.1.6.7-provider-opt-in-terminal-alignment-pr204 -->

## v1.1.6.7 Experimental Provider Opt-in Boundary Terminal Alignment

v1.1.6.7 Experimental Provider Opt-in Boundary --- Accepted
Implementation PR #204 --- Merged
Implementation merge --- ac8f88ce8ab0cdb708671411459910a57c7fa1d2
Post-merge focused verification --- 78 passed
Provider Resolution --- Injection Only
Provider Handler Wiring --- Not Started
AI CLI Production Registration --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6.8 Provider Handler Wiring

The accepted boundary supports only explicit provider selection through an
injected client factory. It does not own SDK import, environment lookup,
automatic fallback, handler wiring, or production parser registration.

<!-- v1.1.6.8-provider-handler-wiring -->

## v1.1.6.8 Provider Handler Wiring

v1.1.6.8 Provider Handler Wiring --- In Progress
Provider Source Selection --- Fail Closed
Provider Text Normalization --- Strict JSON Object
SDK Import / Environment Lookup --- Not Owned
AI CLI Production Registration --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6.8 Implementation Verification / PR / CI

<!-- v1.1.6.8-provider-handler-terminal-alignment-pr206 -->

## v1.1.6.8 Provider Handler Wiring Terminal Alignment

v1.1.6.8 Provider Handler Wiring --- Accepted
Implementation PR #206 --- Merged
Implementation merge --- 70ac918d139b0ac010eae400935ec2f4979e67de
Post-merge focused verification --- 76 passed
Provider Source Selection --- Fail Closed
Provider Text Normalization --- Strict JSON Object
AI CLI Production Registration --- Not Started
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6.9 Production Parser Registration

<!-- v1.1.6.9-production-parser-registration -->

## v1.1.6.9 AI CLI Production Parser Registration

v1.1.6.8 Provider Handler Wiring --- Accepted
v1.1.6.9 Production Parser Registration --- In Progress
Exact AI Command Inventory --- course / review / document / template
Stable Local-response Execution --- Registered
Experimental Provider Composition --- Fail Closed / Injection Required
SDK Import / Environment Lookup --- Not Owned
AI CLI Implementation Acceptance --- Not Accepted
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6.9 Implementation Verification / PR / CI

This candidate registers the exact four-command AI parser in the production
composition root. It preserves deterministic local-response execution and
the existing exit-2 diagnostic boundary. Provider execution remains an
explicit Experimental path and cannot acquire credentials, import an SDK,
select a provider, or initiate fallback implicitly.
------------------------------------------------------------------------

<!-- v1.1.6.9-parser-registration-terminal-alignment -->

## v1.1.6.9 AI CLI Production Parser Registration Terminal Alignment

PR #208 completed production registration of the governed AI CLI parser and
was squash merged as:

``` text
2befa064c8172fe2dab05c06d3737935d38642be
```

Terminal state:

``` text
v1.1.6.8 Provider Handler Wiring --- Accepted
v1.1.6.9 Production Parser Registration --- Accepted
Exact AI Command Inventory --- course / review / document / template
Stable Local-response Execution --- Registered
Experimental Provider Composition --- Fail Closed / Injection Required
SDK Import / Environment Lookup --- Not Owned
AI CLI Implementation Acceptance --- Not Accepted
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6.10 EN / zh-TW User Manual Parity
```

The merge exposes the exact four AI subcommands through the production parser
without changing the accepted execution boundaries. Local-response execution
remains deterministic. Experimental provider execution remains explicit,
injection-only, and fail-closed; parser registration does not own credential
lookup, SDK import, implicit provider selection, or network fallback.

The next slice is documentation-only parity work for the English and
Traditional Chinese (Taiwan) User Manuals. Full AI CLI implementation
acceptance remains a later independent gate.

------------------------------------------------------------------------

<!-- v1.1.6.10-ai-cli-user-manual-parity-pre-acceptance -->

## v1.1.6.10 AI CLI EN / zh-TW User Manual Parity — Pre-acceptance

After v1.1.6.9 Production Parser Registration reached Accepted, the project
started the bilingual AI CLI documentation gate.

The English and Traditional Chinese (Taiwan) CLI manuals now document the same
governed surface:

``` text
opl ai course
opl ai review
opl ai document
opl ai template
```

Both manuals preserve the same Stable / Experimental boundary: deterministic
local-response execution is Stable; provider execution is explicit,
injection-only, and fail-closed. They also align exit-code 2 / stderr /
no-success-output semantics, non-mutating filesystem/repository behavior, and
explicitly reject automatic SDK import, automatic credential lookup, implicit
provider selection, and network fallback.

Local evidence:

``` text
v1.1.6.10 EN / zh-TW User Manual Parity --- In Progress
Documentation parity implementation --- Completed
Parity automation --- Passed
Focused documentation verification --- 80 passed
pre-commit --- Passed
AI CLI Implementation Acceptance --- Not Accepted
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6.10 PR / CI / Post-merge Acceptance
```

This is pre-acceptance evidence only. PR / CI / squash merge / synchronized
main / post-merge consistency / terminal alignment remain required before
v1.1.6.10 can transition to Accepted.

------------------------------------------------------------------------

<!-- v1.1.6.10-ai-cli-user-manual-parity-terminal-alignment -->

## v1.1.6.10 AI CLI EN / zh-TW User Manual Parity Terminal Alignment

Documentation PR #210 passed required CI and was squash merged as:

``` text
e982c0cad94511a649e0701ec0682855cd3db8ea
```

After synchronizing `main` with `origin/main`, the bilingual documentation
suite passed 80 tests and pre-commit passed again. The terminal state is:

``` text
v1.1.6.9 Production Parser Registration --- Accepted
v1.1.6.10 EN / zh-TW User Manual Parity --- Accepted
Documentation PR #210 --- Merged
Documentation merge --- e982c0cad94511a649e0701ec0682855cd3db8ea
Documentation required CI --- Passed
Post-merge documentation verification --- 80 passed
Post-merge pre-commit --- Passed
Post-merge consistency verification --- Passed
AI CLI Implementation Acceptance --- Not Accepted
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6.11 Full Regression / AI CLI Implementation Acceptance
```

The accepted bilingual manuals preserve the exact AI CLI command inventory,
Stable local-response path, Experimental provider boundary, failure semantics,
and non-mutating behavior. They do not expand the production runtime surface
and do not pre-accept the broader AI CLI implementation or v1.1 release.

------------------------------------------------------------------------

<!-- v1.1.6.11-ai-cli-implementation-acceptance-candidate -->

## v1.1.6.11 AI CLI Implementation Acceptance Candidate

The acceptance candidate starts from synchronized `main` at:

``` text
4dc6070158290be72d9dbfb6d6008a65d9dd1965
```

All implementation slices v1.1.6.1 through v1.1.6.10 are already Accepted.
This slice adds the formal acceptance record and fail-closed automation, then
requires fresh focused/full regression, coverage, local quality gates, PR/CI,
merge, synchronized-main verification, and terminal alignment.

``` text
v1.1.6.11 Full Regression / AI CLI Implementation Acceptance --- In Progress
AI CLI Implementation Acceptance --- Not Accepted
Formal v1.1 Acceptance --- Not Accepted
```

------------------------------------------------------------------------

<!-- v1.1.6.11-local-evidence -->

## v1.1.6.11 Fresh Local Acceptance Evidence

``` text
Focused AI CLI / acceptance verification --- ============================= 118 passed in 1.11s =============================
Full regression --- =============== 2277 passed, 33 skipped, 1 deselected in 27.11s ===============
Total coverage --- 91.17%
Required coverage threshold --- 67.0% --- Passed
pre-commit --- Passed
git diff --check --- Passed
AI CLI Implementation Acceptance --- Not Accepted
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.6.11 Acceptance PR / CI / Post-merge Closure
```

------------------------------------------------------------------------

<!-- v1.1.6.11-terminal-alignment -->

## v1.1.6.11 AI CLI Implementation Acceptance Terminal Alignment

PR #212 passed required CI and was squash merged as:

``` text
a6f2161d0affba59cae19cbe4deb5f7b6cd91b84
```

Fresh synchronized-main post-merge evidence:

``` text
Focused verification --- ============================= 47 passed in 1.06s ==============================
Full regression --- =============== 2277 passed, 33 skipped, 1 deselected in 27.57s ===============
Total coverage --- 91.17%
Required coverage --- 67.0% --- Passed
git diff --check --- Passed
pre-commit --- Passed
Post-merge consistency verification --- Passed
```

Terminal state:

``` text
v1.1.6.11 Full Regression / AI CLI Implementation Acceptance --- Accepted
AI CLI Implementation Acceptance --- Accepted
Formal v1.1 Acceptance --- Not Accepted
Next --- next v1.1 roadmap slice
```

------------------------------------------------------------------------

<!-- v1.1.7-documentation-parity-pre-acceptance -->

## v1.1.7 Documentation / EN-zh-TW Parity — Pre-acceptance

``` text
v1.1.6 AI CLI Implementation --- Accepted
v1.1.7 Documentation / EN-zh-TW Parity --- In Progress
Release-level parity design --- Defined
Release-level parity automation --- Added
Documentation regression --- 97 passed, 3 skipped in 0.43s
git diff --check --- Passed
pre-commit --- Passed
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.7 PR / CI / Post-merge Acceptance
```

The release-level documentation gate coordinates the existing bilingual User
Manual structural parity, functional parity, Marketplace CLI documentation,
AI CLI parity, and First 15 Minutes / onboarding authorities.

This is pre-acceptance evidence only. Required CI, squash merge, synchronized
main, post-merge consistency verification, and terminal alignment remain
mandatory before v1.1.7 can become Accepted.

### Code Review Checklist

- [x] EN / zh-TW top-level chapter sets match.
- [x] Stable v1 CLI inventory remains symmetric.
- [x] Marketplace command inventory remains symmetric.
- [x] `opl marketplace list` is explicitly rejected in both languages.
- [x] AI command inventory remains symmetric.
- [x] Existing structural / functional parity authorities remain present.
- [x] First 15 Minutes / onboarding authority remains present.
- [x] Documentation regression passes.
- [x] `git diff --check` passes.
- [x] pre-commit passes.
- [x] Formal v1.1 Acceptance remains Not Accepted.

------------------------------------------------------------------------

<!-- v1.1.7-documentation-parity-terminal-alignment -->

## v1.1.7 Documentation / EN-zh-TW Parity Terminal Alignment

``` text
v1.1.7 Documentation / EN-zh-TW Parity --- Accepted
Documentation PR #214 --- Merged
Documentation merge --- eafc65cd849ffbe546e2228e1027cca4863452a7
Documentation PR required CI --- Passed
main synchronization after documentation merge --- Completed
Post-merge focused documentation verification --- 60 passed in 0.21s
Post-merge documentation regression --- 97 passed, 3 skipped in 0.60s
Post-merge git diff --check --- Passed
Post-merge pre-commit --- Passed
Post-merge consistency verification --- Passed
Terminal documentation alignment --- Completed
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.8 Reliability / Artifact-backed Verification
```

The release-level bilingual documentation contract is terminally aligned with
the merged implementation and existing structural, functional, Marketplace,
AI CLI, and First 15 Minutes / onboarding authorities.

------------------------------------------------------------------------

<!-- v1.1.8-reliability-artifact-backed-terminal-alignment -->

## v1.1.8 Reliability / Artifact-backed Verification Terminal Alignment

``` text
v1.1.8 Reliability / Artifact-backed Verification --- Accepted
Implementation / Evidence PR #216 --- Merged
Implementation merge --- 19103257e7fe405f8d38ad4e43fd549e78867bde
Required CI --- Passed
main synchronization --- Completed
Repository canonical identity --- 1.0.0
v1.1 candidate identity --- 1.1.0rc1
v1.1 candidate tag --- v1.1.0-rc.1
Candidate build source SHA --- 19103257e7fe405f8d38ad4e43fd549e78867bde
Candidate build boundary --- Passed
Artifact identity verification --- Passed
Checksum verification --- Passed
Clean-installed user verification --- Passed
Marketplace installed-user verification --- Passed
AI Stable installed-user verification --- Passed
First 15 Minutes installed-wheel verification --- Passed
Full regression --- Passed
Required coverage --- Passed
git diff --check --- Passed
pre-commit --- Passed
Post-merge consistency verification --- Passed
Terminal documentation alignment --- Completed
Formal v1.1 Acceptance --- Not Accepted
Next --- v1.1.9 Formal v1.1 Acceptance
```

The repository keeps the immutable v1.0 canonical identity (`1.0.0`).
The v1.1 release candidate is produced only through the temporary candidate
build boundary as `1.1.0rc1`; the repository source identity itself is not
mutated.

PR #216 passed required CI, squash merged, and was followed by synchronized-main
artifact identity, clean-install, installed-user, First 15 Minutes, full
regression, coverage, and local quality verification.

This terminal closure accepts v1.1.8 only. Formal v1.1 Acceptance remains a
separate v1.1.9 gate.

### Code Review Checklist

- [x] PR #216 merge identity is recorded.
- [x] Repository canonical identity remains `1.0.0`.
- [x] Candidate identity remains `1.1.0rc1`.
- [x] Candidate tag remains `v1.1.0-rc.1`.
- [x] Candidate source SHA matches the PR #216 merge baseline.
- [x] Candidate build uses the temporary build boundary.
- [x] Wheel / sdist identity and checksums passed.
- [x] Clean-installed `opl` behavior passed.
- [x] Marketplace installed-user verification passed.
- [x] AI Stable installed-user verification passed.
- [x] First 15 Minutes installed-wheel verification passed.
- [x] Full regression / required coverage passed.
- [x] `git diff --check` / pre-commit passed.
- [x] Formal v1.1 Acceptance remains Not Accepted.
- [x] Next gate is v1.1.9 Formal v1.1 Acceptance.

------------------------------------------------------------------------

<!-- v1.1.9-formal-acceptance-pre-acceptance -->

## v1.1.9 Formal v1.1 Acceptance — Pre-acceptance

``` text
v1.1.8 Reliability / Artifact-backed Verification --- Accepted
v1.1.9 Formal v1.1 Acceptance --- In Progress
Acceptance record / automation --- Defined
Focused formal-acceptance verification --- 35 passed, 20 skipped in 0.12s
Full regression --- 2312 passed, 53 skipped, 1 deselected
Total coverage --- 91.17%
Required coverage threshold --- 67.0% --- Passed
git diff --check --- Passed
pre-commit --- Passed
Acceptance PR required CI --- Pending
Acceptance squash merge --- Pending
main synchronization --- Pending
Post-merge consistency verification --- Pending
Terminal acceptance alignment --- Pending
Formal v1.1 Acceptance --- Not Accepted
Next --- Formal Acceptance PR / CI
```

The local formal-acceptance gates have passed. This pre-acceptance alignment
does not itself accept v1.1.

Required PR CI, squash merge, synchronized-main verification, post-merge
consistency, and terminal acceptance alignment remain mandatory before Formal
v1.1 Acceptance may transition to Accepted.

### Code Review Checklist

- [x] v1.1.8 predecessor remains Accepted.
- [x] Formal acceptance record exists and remains fail closed.
- [x] Focused formal-acceptance verification passes.
- [x] Full regression passes with `2312 passed, 53 skipped, 1 deselected`.
- [x] Total coverage is `91.17%`.
- [x] Required coverage threshold `67.0%` passes.
- [x] `git diff --check` passes.
- [x] pre-commit passes.
- [ ] Formal Acceptance PR required CI passes.
- [ ] Acceptance PR squash merge completes.
- [ ] main synchronization completes.
- [ ] Post-merge consistency verification passes.
- [ ] Terminal acceptance alignment completes.
- [ ] Formal v1.1 Acceptance transitions to Accepted.

------------------------------------------------------------------------

<!-- v1.1.9-formal-acceptance-terminal-alignment -->

## v1.1.9 Formal v1.1 Acceptance Terminal Alignment

``` text
v1.1.9 Formal v1.1 Acceptance --- Accepted
Formal v1.1 Acceptance --- Accepted
Acceptance PR #218 --- Merged
Acceptance merge --- c740613f5ac29d696962545afb2ee0f5b0c8c630
Acceptance PR required CI --- Passed
main synchronization --- Completed
Post-merge consistency verification --- Passed
Terminal acceptance alignment --- Completed
Full regression --- 2312 passed, 53 skipped, 1 deselected
Total coverage --- 91.17%
Required coverage threshold --- 67.0% --- Passed
Repository historical identity --- 1.0.0
v1.1 candidate identity --- 1.1.0rc1
v1.1 candidate tag --- v1.1.0-rc.1
v1.1 --- Terminally Accepted
Next --- Post-v1.1 Roadmap Planning
```

------------------------------------------------------------------------

<!-- post-v1.1-roadmap-planning-history -->

# Post-v1.1 Roadmap Planning

Following terminal acceptance of OpenProjectLab v1.1 at merge
`9997e9d85ed3672451c6c538d464d07a93d3d9cb`, the project entered its next-version planning cycle.

The planning process currently selects **v1.2** as the next version boundary
because the candidate workstreams are expected to evolve existing Stable v1.x
contracts without requiring an intentional breaking release.

This selection establishes a planning boundary only. It does not accept v1.2
and does not authorize implementation.

## Candidate Workstreams

- Bootstrap Framework maturity;
- AI-assisted project and course generation;
- Marketplace production workflow;
- Developer and release automation.

## Planning Boundary

``` text
v1.1 --- Terminally Accepted
        ↓
Post-v1.1 Roadmap Planning --- In Progress
        ↓
Next Version Boundary --- v1.2
        ↓
Next Version Decision --- Not Yet Accepted
        ↓
v1.2 Implementation --- Not Started
```

v2.0 remains out of scope unless a future architecture decision demonstrates
that a Stable-contract break is necessary and cannot be avoided through
backward-compatible v1.x evolution.

## Acceptance Boundary

The next-version decision remains fail closed until:

- governing planning design is reviewed;
- planning tests pass;
- roadmap / HISTORY / CHANGELOG alignment passes;
- focused planning verification passes;
- full regression / required coverage passes;
- required CI passes;
- planning PR squash merge completes;
- main synchronization completes;
- post-merge consistency verification passes;
- terminal planning acceptance completes.

Current state:

``` text
Next Version Boundary --- v1.2
Release Type --- Backward-compatible feature release
Next Version Decision --- Not Yet Accepted
v1.2 Planning Baseline --- In Progress
v1.2 Implementation --- Not Started
```
------------------------------------------------------------------------

<!-- post-v1.1-roadmap-planning-acceptance -->

## Post-v1.1 Roadmap Planning Acceptance

``` text
Post-v1.1 Roadmap Planning --- Accepted
Planning PR #220 --- Merged
Planning merge --- 8459d3f42a08dc4364624215a77ec58c04b7539f
Planning PR required CI --- Passed
main synchronization --- Completed
Post-merge consistency verification --- Passed
Focused post-merge verification --- 10 passed
Full regression --- 2322 passed, 56 skipped, 1 deselected
Total coverage --- 91.17%
Required coverage --- 67.0% --- Passed
Next Version Boundary --- v1.2
Release Type --- Backward-compatible feature release
Next Version Decision --- Accepted
v1.2 Planning Baseline --- Accepted
v1.2 Implementation --- Not Started
Next --- v1.2 Design Baseline / Workstream Prioritization
```

This closes the Post-v1.1 planning cycle and formally selects v1.2 as the next backward-compatible feature-release boundary. Implementation remains blocked pending the next Design First contract.

------------------------------------------------------------------------

<!-- v1.2-planning-baseline-history -->

# v1.2 Planning Baseline

Following acceptance of Post-v1.1 Roadmap Planning, OpenProjectLab entered
the v1.2 planning-baseline phase from merge `55781b43f7b661a48338601cb22a4d69a120c584`.

The planning priority is:

1. Bootstrap Framework maturity;
2. Developer / Release Automation;
3. AI-assisted Project / Course Generation;
4. Marketplace Production Workflow.

The proposed first implementation slice is
`v1.2.1 --- Bootstrap Framework Design Baseline`.

This is a planning decision only.

``` text
v1.2 Planning Baseline --- In Progress
Workstream Priority --- Proposed
First Implementation Slice --- Proposed: v1.2.1 Bootstrap Framework Design Baseline
v1.2 Planning Baseline --- Not Accepted
v1.2 Implementation --- Not Started
```

No v1.2 implementation is authorized until planning acceptance and a
separate Design First contract are complete.

------------------------------------------------------------------------

<!-- v1.2-planning-baseline-acceptance-history -->

# v1.2 Planning Baseline Acceptance

OpenProjectLab accepted the v1.2 Planning Baseline after Planning PR #222
merged as `cc710f57141f7766acbb4e1ff3feb1884549ea2e`.

Post-merge consistency verification passed with the focused planning suite at
`10 passed`.

``` text
v1.2 Planning Baseline --- Accepted
Planning PR #222 --- Merged
Planning merge --- cc710f57141f7766acbb4e1ff3feb1884549ea2e
Focused post-merge verification --- 10 passed
v1.2 Implementation --- Not Started
Next --- v1.2.1 Bootstrap Framework Design Baseline
```

The accepted next slice is the v1.2.1 Bootstrap Framework Design Baseline.
Implementation remains blocked until that Design First contract is accepted.

------------------------------------------------------------------------

<!-- v1.2.1-bootstrap-framework-design-history -->

# v1.2.1 Bootstrap Framework Design Baseline

在 v1.2 Planning Baseline 正式接受後，OpenProjectLab 進入第一個
v1.2 Design First slice：Bootstrap Framework maturity。

本階段建立：

``` text
docs/releases/v1.2.1-bootstrap-framework-design.md
docs/architecture/bootstrap-framework.md
tests/release_readiness/test_v1_2_1_bootstrap_framework_design.py
```

Architecture boundary 定義：

- `BootstrapPlan`：deterministic / inspectable bootstrap plan；
- `BootstrapStep`：重用既有 Generator lifecycle 的 orchestration step；
- `BootstrapResult`：observable execution evidence；
- `plan`：mutation-free；
- `dry-run`：mutation-free execution preview；
- `apply`：explicit mutation phase；
- committed filesystem mutation 必須重用既有 filesystem abstraction；
- Bootstrap orchestration 必須 compose existing generators；
- validation 為 inspection-only；
- validation failure 不隱含 automatic rollback；
- generalized rollback 不在 v1.2.1 scope；
- Checkpoint / Resume 維持 Deferred；
- Stable Bootstrap CLI surface 尚未接受。

Current state:

``` text
v1.2.1 Bootstrap Framework Design Baseline --- In Progress
Architecture Contract --- Defined
Checkpoint / Resume --- Deferred
CLI Boundary --- Not Accepted
v1.2.1 Bootstrap Framework Design Baseline --- Not Accepted
v1.2 Implementation --- Not Started
```

本階段只建立 architecture、contract、tests 與 lifecycle evidence，
不授權 Bootstrap Framework implementation。

------------------------------------------------------------------------

<!-- v1.2.1-bootstrap-framework-design-acceptance-history -->

# v1.2.1 Bootstrap Framework Design Acceptance

OpenProjectLab formally accepted the v1.2.1 Bootstrap Framework Design
Baseline after Design PR #224 squash merged as `f9f98b35aef679d2521498d6246c201906a3e721`.

``` text
Focused post-merge verification --- 9 passed
v1.2.1 Bootstrap Framework Design Baseline --- Accepted
Checkpoint / Resume --- Deferred
CLI Boundary --- Not Accepted
v1.2 Implementation --- Not Started
```

------------------------------------------------------------------------

<!-- v1.2.2-bootstrap-planning-core-history -->

# v1.2.2 Bootstrap Planning Core

OpenProjectLab 進入 Bootstrap Framework 的第一個 implementation-oriented
Design First slice：Bootstrap Planning Core。

本階段建立 `BootstrapStep`、`BootstrapPlan`、`BootstrapPlanner` 的 governing
contract 與 architecture，但仍不開始 production implementation。

``` text
Planning-core architecture --- Defined
GeneratorRegistry reuse --- Required
Generator lifecycle preservation --- Required
Filesystem Mutation --- Forbidden
Generator Execution --- Forbidden
Network Access --- Forbidden
Plugin Activation --- Forbidden
dry-run execution --- Not Started
apply execution --- Not Started
checkpoint / resume --- Deferred
CLI Boundary --- Not Accepted
v1.2.2 Bootstrap Planning Core --- Not Accepted
v1.2 Implementation --- Not Started
```

------------------------------------------------------------------------

<!-- v1.2.2-bootstrap-planning-core-acceptance-history -->

# v1.2.2 Bootstrap Planning Core Acceptance

OpenProjectLab formally accepted the v1.2.2 Bootstrap Planning Core Design
First contract after Design PR #226 squash merged as `c76c1b931da7d0aaf13792546b451c46f4769fe0`.

``` text
v1.2.2 Bootstrap Planning Core --- Accepted
BootstrapStep / BootstrapPlan / BootstrapPlanner --- Accepted
Deterministic ordering --- Accepted
Equivalent-plan behavior --- Accepted
GeneratorRegistry reuse --- Accepted
Generator lifecycle preservation --- Accepted
Mutation-free planning --- Accepted
dry-run execution --- Not Started
apply execution --- Not Started
validation runtime --- Not Started
checkpoint / resume --- Deferred
generalized rollback --- Deferred
CLI Boundary --- Not Accepted
v1.2 Implementation --- Not Started
Next --- Bootstrap Planning Core implementation slice
```

------------------------------------------------------------------------

<!-- v1.2.2.1-bootstrap-planning-core-terminal-history -->

# v1.2.2.1 Bootstrap Planning Core Implementation

OpenProjectLab completed the first production implementation slice of the
Bootstrap Planning Core in Implementation PR #228, squash merged as
`528f356a3160af5445a9e4b4193ee5e62029653e`.

Completed implementation evidence:

- immutable `BootstrapStep`;
- immutable `BootstrapPlan`;
- deterministic `BootstrapPlanner`;
- descriptive `ExpectedEffect`;
- deterministic step ordering;
- equivalent-plan behavior;
- reuse of existing `GeneratorRegistry.names()` lookup boundary;
- no generator instantiation or execution;
- no filesystem mutation;
- no network access;
- no plugin activation.

``` text
dry-run --- Not Started
apply --- Not Started
validation runtime --- Not Started
checkpoint / resume --- Deferred
generalized rollback --- Deferred
CLI Boundary --- Not Accepted
Next --- v1.2.3 Dry-run Execution Preview Design First slice
```
------------------------------------------------------------------------

<!-- v1.2.3-dry-run-execution-preview-history -->

# v1.2.3 Dry-run Execution Preview Design First

OpenProjectLab entered the v1.2.3 Design First slice after terminal alignment
of the v1.2.2 Bootstrap Planning Core.

The design proposes immutable `BootstrapDryRunStep` and
`BootstrapDryRunPreview` values plus a projection-only
`BootstrapDryRunExecutor`. The existing `BootstrapPlan` remains authoritative.
Preview ordering and equivalent-preview behavior must be deterministic, while
expected effects remain descriptive data only.

Generator instantiation/execution, filesystem and governance-artifact writes,
network access, and plugin activation remain forbidden. Failure must produce
zero partial state. Apply, validation runtime, checkpoint/resume, generalized
rollback, Stable CLI syntax, and production implementation remain outside this
slice.


------------------------------------------------------------------------

<!-- v1.2.3-dry-run-execution-preview-acceptance-history -->

# v1.2.3 Dry-run Execution Preview Design Acceptance

Design PR #230 passed required CI and squash merged as
`5f26cf2526ff39de381129d76791d0c28d06c91a`. Synchronized-main focused
verification passed with 11 tests. The deterministic, mutation-free dry-run
preview design is terminally accepted while production implementation remains
Not Started.


------------------------------------------------------------------------

<!-- v1.2.3-dry-run-execution-preview-terminal-history -->

# v1.2.3 Dry-run Execution Preview Minimum Implementation

Implementation PR #232 passed required CI and squash merged as
`ac4cd405098d1179eb5dc5cb7e32f3e9590bb98f`. The minimum production slice added immutable
`BootstrapDryRunStep` and `BootstrapDryRunPreview` values plus the
projection-only `BootstrapDryRunExecutor.preview(plan)` boundary. Post-merge
focused verification passed with 19 tests. Apply, validation runtime, and the
Stable Bootstrap CLI remain outside this slice.

------------------------------------------------------------------------

<!-- v1.2.4-bootstrap-apply-execution-history -->

# v1.2.4 Bootstrap Apply Execution Design First

OpenProjectLab entered the apply Design First slice after terminal completion
of the deterministic, mutation-free v1.2.3 dry-run preview. The proposed apply
boundary reuses the authoritative BootstrapPlan, existing Generator lifecycle,
and existing filesystem abstraction. It defines deterministic sequential
execution and fail-fast partial-state evidence without claiming generalized
rollback or transaction-wide atomicity.


------------------------------------------------------------------------

<!-- v1.2.4-bootstrap-apply-execution-acceptance-history -->

# v1.2.4 Bootstrap Apply Execution Design Acceptance

Design PR #234 passed required CI and squash merged as `1e0f7ebba9b98dd1c6bfa5edad52efa1bae7f0b6`.
Synchronized-main focused verification passed with 9 tests. The sequential,
fail-fast apply design is terminally accepted while production implementation
remains Not Started.


------------------------------------------------------------------------

<!-- v1.2.4-bootstrap-apply-execution-terminal-history -->

# v1.2.4 Bootstrap Apply Execution Minimum Implementation

Implementation PR #236 passed required CI and squash merged as
`1fbf799bd6bc687592a46788fc98f2dda1b79907`. The minimum production slice added immutable apply-step and
aggregate results, sequential `BootstrapApplyExecutor.apply(plan)`, existing
Generator lifecycle reuse, and fail-fast partial-state evidence. Post-merge
focused verification passed with 30 tests. Generalized rollback, validation,
checkpoint/resume, and Stable CLI syntax remain outside this slice.

------------------------------------------------------------------------

<!-- v1.2.5-bootstrap-validation-runtime-history -->

# v1.2.5 Bootstrap Validation Runtime Design First

OpenProjectLab entered the inspection-only validation Design First slice after
terminal completion of v1.2.4 apply execution. The design separates invalid
state findings from fail-closed check errors, requires deterministic check and
finding order, and forbids silent repair, re-apply, and automatic rollback.


------------------------------------------------------------------------

<!-- v1.2.5-bootstrap-validation-runtime-acceptance-history -->

# v1.2.5 Bootstrap Validation Runtime Design Acceptance

Design PR #238 passed required CI and squash merged as `eadc9b96a0a7f4231331da162ee9c586cd9613e6`.
Synchronized-main focused verification passed with 9 tests. The inspection-only
validation design is terminally accepted while implementation remains separate.


------------------------------------------------------------------------

<!-- v1.2.5-bootstrap-validation-runtime-terminal-history -->

# v1.2.5 Bootstrap Validation Runtime Minimum Implementation

Implementation PR #240 passed required CI and squash merged as
`902256c2dbb7ec384abe31decdeeb555240a85ce`. The minimum production slice added immutable validation contracts,
ordered inspection-only checks, severity-derived validity, and fail-closed
completed evidence. Post-merge focused verification passed with 20 tests.
Repair, rollback, checkpoint/resume, parallel validation, and Stable CLI syntax
remain outside this slice.


------------------------------------------------------------------------

<!-- v1.2.6-bootstrap-runtime-integration-design-history -->

# v1.2.6 Bootstrap Runtime Integration Design First

Defined explicit runtime modes, exactly-once planning, authoritative plan reuse,
ordered fail-closed phases, and closed CLI/SDK/repair/rollback surfaces.


------------------------------------------------------------------------

<!-- v1.2.6-bootstrap-runtime-integration-acceptance-history -->

# v1.2.6 Bootstrap Runtime Integration Design Acceptance

Design PR #242 passed required CI and squash merged as `4045a21514e912548456569a272a983f32ba5c4b`.
Synchronized-main focused verification passed with 10 tests. The integration
design is terminally accepted while production implementation remains separate.


------------------------------------------------------------------------

<!-- v1.2.6-bootstrap-runtime-integration-terminal-history -->

# v1.2.6 Bootstrap Runtime Integration Minimum Implementation

Implementation PR #244 passed required CI and squash merged as
`f126238de83fc4fe12f4cb6de1d281fccd4281d0`. The minimum production slice coordinates preview, apply, and
apply-and-validate with one authoritative plan, deterministic sequential phase
ordering, and fail-closed propagation. Post-merge focused verification passed
with 18 tests. CLI and public SDK expansion, repair, rollback,
checkpoint/resume, and parallel execution remain deferred.


------------------------------------------------------------------------

<!-- v1.2.6-bootstrap-runtime-integration-implementation-closure-history -->

# v1.2.6 Bootstrap Runtime Integration Implementation Accepted

Terminal evidence PR #245 passed required CI and squash merged as
`c4971d97dc193a75eddad76faf1ea1c36c222fd5`. Synchronized-main post-merge consistency verification passed with
19 focused tests. The minimum implementation is Accepted / Completed while
all previously deferred CLI, SDK, repair, rollback, checkpoint/resume, and
parallel-execution boundaries remain unchanged.


------------------------------------------------------------------------

<!-- v1.2.7-bootstrap-cli-runtime-wiring-design-history -->

# v1.2.7 Bootstrap CLI/runtime Wiring Design First

Opened a Design First slice for an explicit experimental adapter from the
canonical `generator.cli.main` Bootstrap command to the accepted internal
runtime. Existing behavior remains unchanged without opt-in; production wiring
has not started.


------------------------------------------------------------------------

<!-- v1.2.7-bootstrap-cli-runtime-wiring-acceptance-history -->

# v1.2.7 Bootstrap CLI/runtime Wiring Design Accepted

Design PR #247 passed required CI and squash merged as `a254574d7fc9570402f445518f00714ce5e644e0`.
Synchronized-main post-merge verification passed with 9 tests. The canonical
entrypoint, compatibility, opt-in mapping, failure, deferred-surface, and code
review contracts are accepted. Production CLI wiring remains not started.


------------------------------------------------------------------------

<!-- v1.2.7-bootstrap-cli-runtime-wiring-terminal-history -->

# v1.2.7 Bootstrap CLI/runtime Wiring Minimum Implementation

Implementation PR #249 passed required CI and squash merged as
`ea8dcb3df06679ad2cea84eab228db0c97373b4f`. The canonical CLI now has explicit experimental runtime and
validation opt-ins while preserving the existing handler without opt-in.
Post-merge focused verification passed with 16 tests. Stable public option
names, SDK/serialization, repair, rollback, checkpoint/resume, and parallel
execution remain deferred.


------------------------------------------------------------------------

<!-- v1.2.7-bootstrap-cli-runtime-wiring-implementation-closure-history -->

# v1.2.7 Bootstrap CLI/runtime Wiring Implementation Accepted

Terminal evidence PR #250 passed required CI and squash merged as
`fe66ca9c5fd751937f5feeaa7c1bae8b7285b719`. Synchronized-main post-merge consistency verification passed with
27 focused tests. The minimum experimental CLI/runtime wiring is Accepted /
Completed while legacy behavior and all deferred public or advanced lifecycle
boundaries remain unchanged.

------------------------------------------------------------------------

<!-- v1.2.8-bootstrap-cli-public-contract-design-history -->

# v1.2.8 Bootstrap CLI Public Contract Stabilization --- Design First

Started the Design First contract for stabilizing the observable Bootstrap CLI
surface after v1.2.7. The design fixes parsing, exit-status, output-channel,
validation-failure, compatibility, and deferred-scope boundaries without adding
production behavior.

------------------------------------------------------------------------

<!-- v1.2.8-bootstrap-cli-public-contract-acceptance-history -->

# v1.2.8 Bootstrap CLI Public Contract Design Accepted

Design PR #252 passed required CI and squash merged as `262cdf6b76f811a158579c58ec9fcbeb25dec6fd`.
Synchronized-main verification passed with 10 focused tests. The parsing,
exit-status, output-channel, validation-failure, compatibility, and safety
contract is terminally accepted while production stabilization remains Not
Started.

------------------------------------------------------------------------

<!-- v1.2.8-bootstrap-cli-public-contract-terminal-alignment-history -->

# v1.2.8 Bootstrap CLI Public Contract Implementation Alignment

Implementation PR #254 passed required CI and squash merged as
`1d36d568ca0b09cde2f8e12418bfdb63e72f14e2`. Synchronized-main verification passed with 38 focused tests. The
stable `--runtime` alias, exit-status mapping, output-channel ownership, and
legacy compatibility are implemented. Formal implementation acceptance remains
pending the terminal-alignment merge and its post-merge verification.

------------------------------------------------------------------------

<!-- v1.2.8-bootstrap-cli-public-contract-implementation-closure-history -->

# v1.2.8 Bootstrap CLI Public Contract Fully Accepted

Terminal-alignment PR #255 passed required CI and squash merged as
`6d9b96cb651a0423ffdeb75094a645b99f4786b5`. Synchronized-main verification passed with 39 focused
tests. The stable `--runtime` interface, exit-status mapping, output-channel
ownership, and legacy compatibility are Accepted / Completed. SDK, JSON,
repair, rollback, and advanced lifecycle behavior remain deferred.

## v1.2.9 Bootstrap SDK Runtime Public Contract Design First opened

- Defined the proposed `generator.sdk.bootstrap_runtime` surface.
- Preserved existing generator/plugin SDK exports and CLI process boundaries.
- Kept production implementation explicitly Not Started.

## v1.2.9 Bootstrap SDK Runtime Public Contract terminally accepted

- Accepted the design after PR #257 merged as `28cd71b1a415e876a09fcac15c9fd2e9dc5d8f93`.
- Verified synchronized main with 11 post-merge focused tests.
- Preserved production implementation as Not Started.

## v1.2.9 Bootstrap SDK Runtime implementation aligned

- Recorded implementation PR #259 and merge `ae2d6908f2e573c6e155a1b6a6991390bf385b57`.
- Verified the synchronized implementation with 25 focused tests.
- Kept final implementation acceptance pending a separate closure.

## v1.2.9 Bootstrap SDK Runtime implementation accepted

- Accepted implementation PR #259 (`ae2d6908f2e573c6e155a1b6a6991390bf385b57`).
- Accepted alignment PR #260 (`ab4e85e988c2c257a5354c6f93fa3e808ea6175f`) after synchronized-main verification.
- Closed the slice with 26 focused tests and preserved all deferred boundaries.

## v1.2.9 Bootstrap SDK Runtime final consistency completed

- Recorded acceptance PR #261 and merge `e8be09dcaa081e61b585dc456d2673a17290c0b5`.
- Reconciled the closure gates with completed pre-commit, regression, CI, and post-merge evidence.

## v1.3.0 Bootstrap SDK Serialization Contract Design First opened

- Defined a closed versioned JSON envelope and deterministic encoding boundary.
- Required strict non-executing decode and preserved SDK/CLI compatibility.
- Kept production implementation explicitly Not Started.

## v1.3.0 Bootstrap SDK Serialization Contract terminally accepted

- Accepted Design PR #263 and merge `0ef961e52860434d6631f76859f0cc7c8dbd8af9`.
- Verified synchronized main with 11 post-merge focused tests.
- Preserved production implementation as Not Started.

## v1.3.0 Bootstrap SDK Serialization implementation aligned

- Recorded implementation PR #265 and merge `0407b4986d60578183546e98f5dc57aff890f4a7`.
- Verified synchronized main with 30 focused tests and preserved deferred boundaries.
- Kept terminal implementation acceptance in a separate closure.

## v1.3.0 Bootstrap SDK Serialization implementation accepted

- Accepted implementation PR #265 (`0407b4986d60578183546e98f5dc57aff890f4a7`).
- Accepted alignment PR #266 (`bcf53936c5dfc16473c0e571ed8aceb8b747a549`) after synchronized-main verification.
- Closed the slice with 31 focused tests and preserved deferred boundaries.

## v1.3.0 Bootstrap SDK Serialization Final Consistency

- Formally closed the minimum serialization implementation after Acceptance PR
  #267 passed required CI and squash merged as `8ac7edec84b89b9aaaacb3fa1f9f4d039678b661`.
- Recorded the acceptance candidate at `32 passed`, full regression at
  `2553 passed, 56 skipped, 1 deselected`, and coverage at `90.94%`.
- Synchronized local `main` with `origin/main` and completed the post-merge
  focused verification with `32 passed` on a clean working tree.
- Marked closure gates `Passed / Completed`, preserved strict decoding,
  compatibility, and deferred boundaries, and kept the next roadmap slice
  pending explicit Design First definition.

<!-- v1.3.1-developer-release-automation-design-history -->

## v1.3.1 Developer / Release Automation design

- Started a Design First slice for deterministic release-evidence validation and lifecycle consistency checking.
- Preserved Pending versus Accepted / Completed boundaries and the two-PR acceptance workflow.
- Design PR #269 passed required CI and squash merged as `53cda269e2077e20941bfc2e64ed1cba59972b1d`.
- Synchronized-main post-merge focused verification — 5 passed
- Design review — Passed / Completed
- Production implementation — Not Started

<!-- v1.3.1-release-automation-implementation-alignment -->

## v1.3.1 Developer / Release Automation implementation alignment

- Minimum implementation merged through PR #271 as `0c8f615c72dd6cd023761f88a9e0a9d1e1eb6b6f`.
- Focused post-merge verification — 4 passed, no warnings.
- Full regression — 2564 passed, 56 skipped, 1 deselected.
- Coverage — 90.88%; required coverage 67.0% passed.
- Formal implementation acceptance — Accepted / Completed.
- Alignment PR #272 passed required CI and squash merged as `ea0e7dc25b8d4c5ed60e0fb673d48ff4230e64b4`.
- Alignment synchronized-main post-merge verification — 11 passed.
- Production expansion beyond models and fail-closed validation remains deferred.

<!-- v1.3.2-repository-github-evidence-adapters-design-history -->

## v1.3.2 Repository / GitHub Evidence Adapters design proposed

A Design First slice now proposes deterministic, read-only repository and
GitHub evidence adapters for the v1.3.1 validation core.

The proposal does not authorize implementation or any merge, tag, release,
publication, branch deletion, force-push, reset, credential, CLI, or SDK
expansion. Design review, CI, post-merge verification, and terminal design
acceptance remain pending.

<!-- v1.3.2-repository-github-evidence-adapters-design-acceptance-history -->

## v1.3.2 Repository / GitHub Evidence Adapters design accepted

PR #274 established the read-only repository and GitHub evidence adapter
contract and merged as `5fb07fc3a4f7d775328f01e0049430c7163e1cd9`.

Required CI passed, and synchronized-main focused verification completed with
6 passed. The Design First slice is Accepted / Completed. Production
implementation remains Not Started, and all mutation and publication
operations remain deferred.

<!-- v1.3.2-repository-github-evidence-adapters-implementation-alignment-history -->

## v1.3.2 Repository / GitHub Evidence Adapters implementation alignment

The minimum read-only adapter implementation merged through PR #276 as
`a87251ed7714f6516ca19023d585bb3043744661`. Its synchronized-main focused
verification passed 7 tests. Mutation and implicit merge authorization remain deferred.

- Implementation acceptance — Pending terminal-alignment merge and post-merge verification.

<!-- v1.3.2-repository-github-evidence-adapters-implementation-closure-history -->

## v1.3.2 Repository / GitHub Evidence Adapters implementation accepted

Alignment PR #277 merged as `ec52e25dfbe911033e0b049701fb1df3171c1268`.
Required CI passed, and synchronized-main post-merge verification passed 24 tests.

- Implementation acceptance — Accepted / Completed.
- Mutation and implicit merge authorization remain deferred.

<!-- v1.3.3-release-evidence-verification-orchestration-design-history -->

## v1.3.3 Release Evidence Verification Orchestration design proposed

The next Design First slice composes v1.3.1 validation and v1.3.2 read-only
observations into one deterministic verification contract. It grants no mutation,
test-execution, CLI, SDK, release, or publication authority.

- Design review — Pending.
- Production implementation — Not Started.

<!-- v1.3.3-release-evidence-verification-orchestration-design-acceptance-history -->

## v1.3.3 Release Evidence Verification Orchestration design accepted

PR #279 merged the Design First contract as
`1b3c2e732cf13f384d87efdfc5cc85ff1fdc52aa`. Required CI passed, and
synchronized-main focused verification completed with 6 passed.

- Design acceptance — Accepted / Completed.
- Production implementation — Not Started.

<!-- v1.3.3-release-evidence-verification-orchestration-implementation-history -->

## v1.3.3 Release Evidence Verification Orchestration implementation

The accepted v1.3.3 design now has its minimum production implementation.
Implementation acceptance remains pending.

<!-- v1.3.3-release-evidence-verification-orchestration-implementation-alignment-history -->

    ## v1.3.3 Release Evidence Verification Orchestration implementation aligned

    PR #281 merged the minimum implementation as
    `1441c362923f16d704f817e302ef22fbb829782a`. Required CI passed, and
    synchronized-main focused verification completed with 36 passed.

    - Implementation acceptance — Awaiting terminal-alignment merge and verification.

<!-- v1.3.3-release-evidence-verification-orchestration-implementation-closure-history -->

    ## v1.3.3 Release Evidence Verification Orchestration implementation accepted

    Alignment PR #282 merged as `86ad4406107e90fbec5dcfb2fe57dae407695eec`.
    Required CI passed, and synchronized-main verification completed with 41 passed.

    - Implementation acceptance — Accepted / Completed.

<!-- v1.3.4-read-only-verification-runtime-wiring-design-history -->

    ## v1.3.4 Read-only Verification Runtime Wiring design proposed

    The Design First proposal defines a minimum internal composition root and an exact
    read-command boundary for the accepted release-evidence workflow.

    - Design review — Pending.
    - Production implementation — Not Started.

<!-- v1.3.4-read-only-verification-runtime-wiring-design-acceptance-history -->

    ## v1.3.4 Read-only Verification Runtime Wiring design accepted

    PR #284 merged the Design First contract as
    `247e899f6034e7159a843056c40290b3c42b7dce`. Required CI passed, and
    synchronized-main verification completed with 6 passed.

    - Design acceptance — Accepted / Completed.
    - Production implementation — Not Started.

<!-- v1.3.4-read-only-verification-runtime-wiring-implementation-history -->

    ## v1.3.4 Read-only Verification Runtime Wiring implementation

    The accepted design now has its minimum internal production implementation.
    Implementation acceptance remains pending.

<!-- v1.3.4-read-only-verification-runtime-wiring-implementation-alignment-history -->

    ## v1.3.4 Read-only Verification Runtime Wiring implementation aligned

    PR #286 merged the minimum implementation as
    `8e944d73f241523f8e82c4cb5792501d76ad7ae1`. Required CI passed, and
    synchronized-main focused verification completed with 37 passed.

    - Status — Implemented / Awaiting implementation acceptance.
    - Next — terminal-alignment merge, verification, and separate closure PR.

<!-- v1.3.4-read-only-verification-runtime-wiring-implementation-closure-history -->

    ## v1.3.4 Read-only Verification Runtime Wiring implementation accepted

    Alignment PR #287 merged as `89d16d61f5be0559faf0e87f8740a19378ac0717`.
    Required CI passed, and synchronized-main verification completed with 42 passed.

    - Implementation acceptance — Accepted / Completed.

<!-- v1.3.5-read-only-verification-invocation-design-history -->

    ## v1.3.5 Read-only Verification Invocation Boundary design proposed

    The Design First proposal defines one internal, caller-authorized invocation that
    reuses the accepted read-only runtime without adding discovery or mutation.

    - Design review — Pending.
    - Production implementation — Not Started.

<!-- v1.3.5-v1.3.7-read-only-verification-delivery-train-history -->

        ## v1.3.5–v1.3.7 Read-only Verification delivery train proposed

        The Design First train groups three dependent read-only capabilities while
        preserving separate merge verification and final acceptance closure.

        - Production implementation — Not Started for every train capability.

<!-- v1.3.6-deterministic-verification-io-contracts-design-history -->

            ## v1.3.6 Deterministic Verification I/O Contracts — Design First

            - Status — Proposed / Pending design review.
            - Production implementation — Not Started.

<!-- v1.3.7-opt-in-verification-cli-preview-design-history -->

            ## v1.3.7 Opt-in Read-only Verification CLI Preview — Design First

            - Status — Proposed / Pending design review.
            - Production implementation — Not Started.

<!-- v1.3.5-v1.3.7-delivery-train-design-acceptance-history -->

        ## v1.3.5–v1.3.7 Read-only Verification train design accepted

        PR #289 merged the three-capability Design Train as `aada1068cd4452b264ba612deff7deab455cfb31`. Required CI
        passed, and synchronized-main focused verification completed with 22 passed.

        - Design acceptance — Accepted / Completed.
        - Production implementation — Not Started.

<!-- v1.3.5-v1.3.7-read-only-verification-delivery-train-implementation-history -->
## v1.3.5-v1.3.7 Read-only Verification Delivery Train — Implemented

- Added stateless invocation, deterministic request/report I/O, and the opt-in
  read-only CLI preview.
- Terminal alignment and implementation acceptance remain pending.

<!-- v1.3.5-v1.3.7-read-only-verification-delivery-train-terminal-alignment-history -->
## v1.3.5-v1.3.7 Delivery Train — Terminal Alignment Pending

- PR #291 merged and synchronized-main verification completed with 134 passed.
- Implementation acceptance awaits terminal-alignment merge and verification.

<!-- v1.3.5-v1.3.7-read-only-verification-delivery-train-acceptance-history -->
## v1.3.5-v1.3.7 Delivery Train — Accepted / Completed

- PR #291 implementation verification completed with 134 passed.
- PR #292 terminal-alignment verification completed with 9 passed.
- Implementation acceptance is Accepted / Completed.

<!-- v1.3.8-v1.3.10-verification-request-usability-stable-cli-design-train-history -->
## v1.3.8-v1.3.10 Verification Request Usability and Stable CLI — Design First

- Proposed canonical request serialization, offline request validation, and stable
  release-evidence CLI contracts.
- Production implementation — Not Started.

<!-- v1.3.8-v1.3.10-verification-request-usability-stable-cli-design-acceptance-history -->
## v1.3.8-v1.3.10 Design Train — Accepted / Completed

- Design PR #294 merged at `cf76f779a0554c3268b648b131a794f83152e21f` with required CI passed.
- Synchronized-main design verification completed with 14 passed.
- Production implementation — Not Started.

<!-- v1.3.8-v1.3.10-verification-request-usability-stable-cli-implementation-history -->
## v1.3.8-v1.3.10 Implementation

- Production implementation completed; terminal acceptance remains pending.
