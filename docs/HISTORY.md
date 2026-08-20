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

------------------------------------------------------------------------

# 我們的願景

OpenProjectLab 的目標不是建立更多程式，而是建立：

> **更容易維護、更容易理解、更容易演進的軟體工程文化。**

> Build projects, not just code.
