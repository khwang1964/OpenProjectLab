# Changelog

## Unreleased

### Added

#### Milestone 7 --- Marketplace

-   Added the Marketplace architecture and ADR 0023 --- Marketplace
    Artifact Contract.
-   Added immutable Marketplace artifact identity, version, type,
    coordinate, compatibility, distribution, and integrity models.
-   Added deterministic Marketplace artifact contract tests.
-   Added deterministic in-memory Marketplace repository / index lookup.
-   Added exact-coordinate lookup, deterministic version ordering,
    duplicate-coordinate rejection, and explicit not-found errors.
-   Added deterministic SHA-256 integrity verification.
-   Added deterministic in-memory artifact acquisition returning bytes
    without activation or filesystem side effects.
-   Added immutable structured installation results and deterministic
    in-memory installation contract.
-   Added Template Package, manifest, and safe relative-path contracts.
-   Added duplicate template/resource name/path rejection and
    deterministic package ordering.
-   Added the representative deterministic Marketplace E2E across
    repository, acquisition, integrity verification, installation, and
    Template Package boundaries.
-   Added `docs/milestones/milestone-7-acceptance.md`.

#### Milestone 6 --- AI Integration

-   Added the AI Integration architecture and ADR 0021 --- AI
    Integration Contract.
-   Added immutable provider-independent `AIRequest` and `AIResponse`
    contracts.
-   Added the runtime-checkable `AIProvider` protocol and deterministic
    `FakeAIProvider`.
-   Added structured AI response validation and
    `AIResponseValidationError`.
-   Added AI-to-Courseware mapping into production `Course` / `Week`
    domain objects.
-   Added `AICourseGenerationService` as the provider-independent AI
    course generation application boundary.
-   Added immutable `AIReviewFinding` / `AIReviewResult` contracts and
    advisory `AIReviewService`.
-   Added immutable `AIDocumentDraft` and `AIDocumentationService`.
-   Added immutable `AITemplateCompletionResult` and
    `AITemplateCompletionService`.
-   Added immutable `AICourseBuildRequest` and high-level
    `AICourseBuilder`.
-   Added deterministic AI contract and application tests that require
    no network, API key, paid model account, or real Provider SDK.
-   Added explicit boundaries preventing AI services from bypassing
    Courseware Domain validation or directly mutating the production
    filesystem.
-   Added ADR 0022 --- AI Provider Adapter Contract and accepted the
    provider adapter infrastructure boundary.
-   Added the minimum provider-independent AI provider error hierarchy
    and explicit provider failure conversion.
-   Added the first concrete `OpenAIProviderAdapter` behind the existing
    `AIProvider` protocol.
-   Added deterministic generic provider-adapter contract, credential,
    and error tests.
-   Added deterministic no-network OpenAI adapter contract, credential,
    and error tests.
-   Added the opt-in `ai_live` marker and live OpenAI smoke-test
    boundary.
-   Added default live-test exclusion so normal pytest, pre-commit, and
    core CI remain credential-free and cost-free.
-   Added the Milestone 6 representative deterministic AI-to-courseware
    E2E.
-   Added E2E coverage across `AICourseBuilder`, `FakeAIProvider`,
    Course/Week Domain, `CoursewareComposer`, production generators, and
    filesystem output.
-   Added E2E verification for reproducibility, dry-run non-persistence,
    and fail-before-side-effect behavior for invalid AI output.

#### Milestone 5 --- Open Courseware Platform

-   Added the Open Courseware Platform architecture and responsibility
    boundaries.
-   Added ADR 0014 and minimum production `Course` / `Week` domain
    models.
-   Added Course/Week domain contract tests for identity, validation,
    immutability, duplicate rejection, and deterministic ordering.
-   Added ADR 0015 --- Lab Generator Contract.
-   Added `LabGenerator` as the first concrete material Generator.
-   Added the canonical `lab` built-in Generator identity.
-   Added deterministic Lab output at
    `week-{week:02d}/lab/{lab_id}/README.md`.
-   Added the default Lab README template.
-   Added Lab contract tests, generator integration tests, and CLI
    integration tests.
-   Added the `lab` CLI command and Lab exposure through built-in
    generator listing.
-   Added Lab manifest integration using the existing manifest schema.
-   Added ADR 0016 --- Quiz Generator Contract.
-   Added `QuizGenerator` as the second concrete material Generator.
-   Added canonical `quiz` built-in Generator identity and Week-scoped
    `quiz_id`.
-   Added structured single-answer multiple-choice question validation
    with explicit Question IDs, ordered choices, and correct-answer
    membership validation.
-   Added deterministic Quiz output at
    `week-{week:02d}/quiz/{quiz_id}/README.md`.
-   Added the learner-facing Quiz README template without answer-key
    exposure.
-   Added Quiz contract tests, generator integration tests, and CLI
    integration tests.
-   Added the `quiz` CLI command and built-in `list` / legacy `--list`
    exposure.
-   Added structured Quiz CLI input through `--questions-file` JSON.
-   Added Quiz manifest integration using the existing manifest schema.
-   Added ADR 0017 --- Assignment Generator Contract.
-   Added `AssignmentGenerator` as the third concrete Week-scoped
    material Generator.
-   Added canonical `assignment` built-in identity and explicit
    Week-scoped `assignment_id`.
-   Added ordered Assignment objectives, deliverables, and resources
    plus authored instructions and submission guidance.
-   Added deterministic Assignment output at
    `week-{week:02d}/assignment/{assignment_id}/README.md`.
-   Added the Assignment README template.
-   Added Assignment contract tests, generator integration tests, and
    CLI integration tests.
-   Added the `assignment` CLI command and built-in `list` / legacy
    `--list` exposure.
-   Added structured Assignment CLI input through `--content-file` JSON.
-   Added Assignment manifest integration using the existing manifest
    schema.
-   Added ADR 0018 --- Slides Generator Contract.
-   Added `SlidesGenerator` as the first presentation-source Generator.
-   Added canonical `slides` built-in identity and deterministic
    `<target>/slides.md` output.
-   Added the canonical `templates/slides/slides.md.j2` template and
    manifest registration.
-   Added Slides contract tests, generator integration tests, template
    tests, and CLI integration tests.
-   Added the `slides` CLI command and built-in `list` / legacy `--list`
    exposure.
-   Added structured Slides CLI input through `--slides-file` JSON.
-   Added Slides manifest integration using the existing manifest
    schema.
-   Added ADR 0019 --- Website Generator Contract.
-   Added `WebsiteGenerator` as the deterministic static Website
    publishing projection.
-   Added canonical `website` built-in identity and ordered multi-page
    HTML generation.
-   Added the canonical `templates/website/page.html.j2` template and
    manifest registration.
-   Added deterministic Website output under `<target>/site/`, including
    required `index.html`.
-   Added Website contract tests, generator integration tests, template
    tests, and CLI integration tests.
-   Added the `website` CLI command and built-in `list` / legacy
    `--list` exposure.
-   Added structured Website CLI input through `--pages-file` JSON.
-   Added Website manifest integration using the existing manifest
    schema.
-   Added ADR 0020 --- Courseware Composition Contract.
-   Added `generator/courseware/composition.py` as the deterministic
    courseware orchestration layer.
-   Added ordered `GenerateRequest` composition, existing-registry
    preflight, canonical generator execution, and ordered
    `GenerationResult` aggregation.
-   Added fail-fast composition semantics without cross-generator
    rollback.
-   Added composition contract and representative integration coverage
    across Course, Week, Lab, Quiz, Assignment, Slides, and Website.
-   Added Milestone 5 representative E2E coverage for a complete
    composed courseware repository.
-   Added E2E verification of exact artifact membership, generator
    execution ordering, manifest provenance, reproducible user-facing
    output, and composition-wide dry-run behavior.
-   Added `docs/milestones/milestone-5-acceptance.md` as the formal
    Milestone 5 acceptance record.

#### Milestone 4 --- Plugin Ecosystem

-   Added ADR 0010 through ADR 0012 for the Plugin SDK, validation, and
    Entry Point contracts.
-   Added the stable `generator.sdk` public façade.
-   Added canonical `openprojectlab.generators` Entry Point
    discovery/loading.
-   Added Plugin validation, registry preflight, and transactional
    registration.
-   Added the SDK-only example third-party Plugin distribution.
-   Added real installed-distribution E2E validation.
-   Added `docs/milestones/milestone-4-acceptance.md`.

### Changed

-   Marked ADR 0023 --- Marketplace Artifact Contract as Accepted after
    artifact models, repository/index, integrity/acquisition,
    installation, Template Package, representative E2E, full regression,
    and coverage gates completed locally.

-   Completed Milestone 7 Marketplace implementation through the
    representative deterministic E2E while preserving separation between
    installation and activation.

-   Preserved existing Plugin SDK, Entry Point, Generator lifecycle,
    Courseware Domain, Filesystem, and AI boundaries without Marketplace
    public-SDK expansion.

-   Kept remote Marketplace, Community Repository hosting, Marketplace
    CLI, real package-manager integration, signing/publisher identity,
    sandbox/trust, dependency solving, lock-file/cache, ratings/reviews,
    monetization, and AI Provider Marketplace as deferred capabilities.

-   Marked ADR 0021 --- AI Integration Contract as Accepted after the
    architecture, provider boundary, deterministic Fake-provider
    strategy, structural validation, Courseware mapping, and
    provider-independent application contracts were established.

-   Updated Milestone 6 status from Design First to active
    implementation.

-   Preserved Courseware Domain, Generator, Composition, GenerationPlan,
    and Filesystem boundaries while adding AI capabilities.

-   Kept provider-specific SDK types, credentials, network access, and
    live-provider behavior outside the core AI contracts and normal CI.

-   Kept AI Review advisory, AI Documentation non-mutating, Template
    Completion independent of rendering/filesystem mutation, and Course
    Builder independent of real providers and direct filesystem writes.

-   Completed Real Provider Adapter infrastructure and live-test
    separation without requiring a paid/live provider invocation for
    core acceptance.

-   Completed the representative deterministic AI-to-filesystem E2E.

-   Marked Milestone 6 --- AI Integration as formally Accepted and
    Completed.

-   Completed post-merge documentation consistency alignment.

-   Moved active development focus to Milestone 7 Marketplace planning.

-   Marked ADR 0020 --- Courseware Composition Contract as Accepted
    after design, contract, implementation, and representative
    integration gates completed.

-   Updated Open Courseware architecture to mark deterministic
    courseware composition as Implemented.

-   Preserved canonical `BaseGenerator.run(request)`, existing
    registry/plugin resolution, filesystem, manifest, dry-run,
    overwrite, and `GenerationResult` boundaries for composition.

-   Preserved `generator.sdk` without adding composition-specific public
    symbols.

-   Marked ADR 0019 --- Website Generator Contract as Accepted after
    design, contract, implementation, integration, regression,
    documentation, and CI gates completed.

-   Updated Open Courseware architecture to mark Website and
    deterministic static-site publishing as Implemented while
    composition orchestration remains Proposed.

-   Preserved `GenerateRequest`, `GenerationPlan`, `GenerationResult`,
    dry-run, overwrite, manifest, filesystem, and renderer boundaries
    for Website.

-   Preserved `generator.sdk` without adding Website-specific public
    symbols.

-   Marked ADR 0018 --- Slides Generator Contract as Accepted after
    design, contract, implementation, integration, regression,
    documentation, and CI gates completed.

-   Updated Open Courseware architecture to mark Slides as Implemented
    while Website, composition orchestration, and PPTX / PDF / HTML
    rendering remain Proposed.

-   Preserved `GenerateRequest`, `GenerationPlan`, `GenerationResult`,
    dry-run, overwrite, manifest, filesystem, and renderer boundaries
    for Slides.

-   Preserved `generator.sdk` without adding Slides-specific public
    symbols.

-   Marked ADR 0016 --- Quiz Generator Contract as Accepted after
    design, contract, implementation, integration, regression, and CI
    gates completed.

-   Marked ADR 0017 --- Assignment Generator Contract as Accepted after
    design, contract, implementation, integration, regression,
    documentation, and CI gates completed.

-   Updated Open Courseware architecture to mark Assignment as
    Implemented while PPT/Slides, Website, shared LearningMaterial
    abstractions, composition orchestration, grading/scoring/rubric
    runtime, submission backend, starter-code packaging, and
    courseware-specific SDK expansion remain Proposed.

-   Updated Open Courseware architecture to mark Quiz as Implemented
    while Assignment, PPT/Slides, Website, shared LearningMaterial
    abstractions, composition orchestration, answer-key generation,
    assessment runtime, and courseware-specific SDK exposure remain
    Proposed.

-   Preserved `GenerateRequest`, `GenerationPlan`, `GenerationResult`,
    dry-run, overwrite, manifest, filesystem, and renderer boundaries
    for Quiz.

-   Preserved `generator.sdk` without adding Quiz-specific public
    symbols.

-   Marked ADR 0015 --- Lab Generator Contract as Accepted after
    contract, implementation, integration, and CI gates completed.

-   Updated Open Courseware architecture to mark Lab as Implemented
    while Quiz, Assignment, PPT/Slides, Website, shared LearningMaterial
    abstractions, composition orchestration, and courseware-specific SDK
    exposure remain Proposed.

-   Updated the Milestone 5 roadmap from planning to active
    implementation.

-   Preserved `GenerateRequest`, `GenerationPlan`, `GenerationResult`,
    dry-run, overwrite, manifest, filesystem, and renderer boundaries
    for Lab.

-   Preserved `generator.sdk` without adding Course/Week/Lab-specific
    public symbols.

-   Marked Milestone 4 --- Plugin Ecosystem as Completed and moved
    active development focus to Milestone 5.

### Removed

-   Removed the legacy `generator.core.plugin.PluginManager`.
-   Removed the legacy internal `PluginDescriptor` runtime path.

### Migration

-   Existing Course/Week Generator contracts remain unchanged.
-   Lab callers should use canonical generator name `lab`.
-   Lab identity is Week-scoped and explicitly uses `lab_id`; title is
    display metadata.
-   Lab artifacts are rooted at `week-{week:02d}/lab/{lab_id}/`.
-   Third-party Plugin implementations continue to depend on
    `generator.sdk`; ADR 0015 does not expand the public Plugin SDK.

### Verification

-   Verified the Milestone 7 representative Marketplace E2E composes
    production repository, acquisition, integrity verification,
    installation, and Template Package contracts.

-   Verified repository not-found, missing payload, and integrity
    mismatch failures occur before installation side effects.

-   Verified failed Marketplace flows leave no partial installation
    state and require no public network or generated-project filesystem
    persistence.

-   Recorded the Milestone 7 final local regression evidence: 1315
    passed, 1 deselected.

-   Verified total coverage at 89.89%, above the required 67.0% gate.


-   Verified the Milestone 7 acceptance PR GitHub Actions / CI passed.

-   Completed the Milestone 7 acceptance squash merge.

-   Completed Milestone 7 post-merge consistency verification.

-   Verified local `main` and `origin/main` resolve to the same commit
    after acceptance merge.

-   Marked Milestone 7 --- Marketplace as formally Completed.


-   Verified PR #77 establishes the Milestone 6 AI Integration
    architecture and ADR 0021.

-   Verified PR #78 establishes `AIRequest`, `AIResponse`, `AIProvider`,
    and deterministic `FakeAIProvider`.

-   Verified PR #79 establishes structured AI response validation.

-   Verified PR #80 maps validated AI responses into production Course /
    Week domain objects.

-   Verified PR #81 establishes the provider-independent AI Course
    Generation Service.

-   Verified PR #82 establishes advisory AI Review contracts and
    service.

-   Verified PR #83 establishes AI Documentation contracts and service.

-   Verified PR #84 establishes AI Template Completion contracts and
    service.

-   Verified PR #85 establishes the high-level AI Course Builder and
    requested week-count completeness validation.

-   Verified core Milestone 6 AI tests remain deterministic and require
    no network, API key, paid provider account, or real Provider SDK.

-   Verified current AI services do not directly mutate the production
    filesystem and do not bypass existing Courseware Domain validation.

-   Verified ADR 0022 acceptance after provider adapter
    responsibilities, SDK isolation, credential isolation, finite
    timeout, error conversion, deterministic adapter testing, and
    live-test separation were implemented.

-   Verified the first concrete `OpenAIProviderAdapter` remains behind
    the existing `AIProvider` boundary and is covered by deterministic
    no-network tests.

-   Verified `ai_live` is opt-in and excluded from normal pytest /
    pre-commit / core CI.

-   Verified missing `OPENAI_API_KEY` skips explicit live smoke
    verification rather than making core verification fail.

-   Paid/live OpenAI invocation remains optional operational
    verification.

-   Verified the representative deterministic AI E2E across AI Course
    Builder, Courseware Domain, Composition, production generators, and
    filesystem behavior.

-   Verified E2E reproducibility, dry-run non-persistence, and failure
    before filesystem side effects.

-   Recorded the Step 6.11 full-regression evidence: 1119 passed.

-   Recorded the Step 6.12 final local regression evidence: 1119 passed,
    1 deselected.

-   Verified total coverage at 90.23%, above the required 67.0% gate.

-   Verified acceptance PR GitHub Actions / CI passed.

-   Completed Milestone 6 post-merge consistency verification.

-   Recorded the final Milestone 6 acceptance baseline: 1119 passed, 1
    deselected with 90.23% total coverage against the required 67.0%
    gate.

-   Verified Courseware Composition deterministic request/execution
    ordering and ordered result aggregation.

-   Verified existing registry preflight prevents execution when a
    required generator cannot be resolved.

-   Verified representative composition across Course, Week, Lab, Quiz,
    Assignment, Slides, and Website.

-   Verified fail-fast behavior stops later generators without claiming
    rollback of earlier successful work.

-   Verified composition-wide dry-run, overwrite propagation, manifest
    compatibility, and input immutability.

-   Verified PR #69 through PR #72 complete the Composition
    design/test/implementation/integration sequence.

-   Verified PR #73 accepts the Courseware Composition contract
    documentation.

-   Verified PR #74 adds the Milestone 5 representative E2E acceptance
    boundary.

-   Verified the representative E2E generates Course, Week, Lab, Quiz,
    Assignment, Slides, and Website artifacts through the production
    composition/generator pipeline.

-   Verified representative E2E artifact membership, manifest generator
    provenance, deterministic/reproducible user-facing output, and
    full-course dry-run non-persistence.

-   Recorded the Milestone 5 formal acceptance regression baseline: 867
    passed with 88.76% total coverage.

-   Verified Website request validation for site title, ordered pages,
    safe relative `.html` paths, unique normalized paths, required
    `index.html`, page titles, and content.

-   Verified deterministic multi-page Website planning, navigation
    ordering, and static HTML output.

-   Verified Website dry-run, overwrite, manifest, built-in list, JSON
    input, and CLI integration.

-   Verified Website remains a publishing projection without hosting,
    CMS, asset-pipeline, Markdown-conversion, or public-SDK
    responsibilities.

-   Verified PR #64 through PR #67 complete the Website
    design/test/implementation/integration sequence.

-   Verified Slides request validation for deck title, ordered slides,
    slide titles, ordered content, immutability, and deterministic
    planning.

-   Verified deterministic Slides `slides.md` generation and
    slide/content ordering.

-   Verified Slides dry-run, overwrite, manifest, built-in list, JSON
    input, and CLI integration.

-   Verified PPTX / PDF / HTML rendering remains outside the core Slides
    Generator boundary.

-   Verified PR #59 through PR #62 complete the Slides
    design/test/implementation/integration sequence.

-   Verified the full regression suite at the Milestone 5 formal
    acceptance baseline: 867 passed with 88.76% total coverage.

-   Verified the required 67.0% coverage gate was satisfied.

-   Verified Quiz request validation for Week, `quiz_id`, title,
    Questions, choices, and correct-answer membership.

-   Verified explicit/unique Question IDs and deterministic
    Question/choice ordering.

-   Verified deterministic Quiz `GenerationPlan` destinations.

-   Verified learner-facing Quiz artifacts do not expose correct-answer
    data.

-   Verified Quiz dry-run, overwrite, manifest, built-in list, JSON
    input, and CLI integration.

-   Verified PR #49 through PR #52 complete the Quiz
    design/test/implementation/integration sequence.

-   Verified Lab request validation for Week, `lab_id`, and title.

-   Verified deterministic Lab `GenerationPlan` destinations.

-   Verified validation-before-planning behavior.

-   Verified dry-run creates no persistent Lab artifacts or manifest
    changes.

-   Verified overwrite protection and existing filesystem semantics.

-   Verified Lab manifest records use the existing schema.

-   Verified built-in list and CLI Lab integration.

-   Verified existing Course/Week/domain contracts remain green.

-   Verified no accidental `generator.sdk` expansion.

-   Verified Ruff, pre-commit, pytest, coverage, and GitHub Actions
    through the Lab design/test/implementation/integration PR sequence.

------------------------------------------------------------------------

### Milestone 3 Generator Framework

-   Added ADR 0005 through ADR 0009 to define shared Generator input,
    validation, planning, execution, and legacy lifecycle removal
    contracts.
-   Established `BaseGenerator.run(GenerateRequest)` as the
    framework-controlled canonical execution entry point.
-   Removed legacy `GeneratorContext` lifecycle hooks and
    Generator-specific result compatibility types.
