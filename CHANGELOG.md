# Changelog

## Unreleased

### Added

#### Milestone 8 --- v1.0 Stabilization & Release Readiness

-   Added `docs/releases/v1.0-release-readiness.md` as the governing
    release-readiness plan for the final pre-v1.0 engineering milestone.
-   Defined the Milestone 8 release gates from 8.1 Release Readiness
    Baseline through 8.10 RC Acceptance.
-   Defined the v1.0 contract classification model: Stable, Candidate,
    Experimental, Internal, and Deferred.
-   Defined a feature-freeze mindset for Milestone 8 so non-blocking
    product expansion is deferred to the v1.1+ backlog.
-   Defined English and Traditional Chinese (Taiwan) User Manuals as
    mandatory v1.0 release requirements with functional documentation
    parity.
-   Defined the First 15 Minutes Quick Start as a representative
    onboarding flow that should become an executable documentation smoke
    test where practical.
-   Defined compatibility and deprecation policy work as explicit v1.0
    release-readiness gates.
-   Defined support-matrix and known-limitations documentation as
    explicit v1.0 release-readiness gates.
-   Defined release automation, artifact/version/tag consistency, clean
    installation verification, and release reproducibility as explicit
    release-readiness requirements.
-   Defined Milestone 8 completion as readiness to create `v1.0.0-rc.1`,
    distinct from the later `v1.0.0` GA acceptance.
-   Added `docs/releases/v1.0-public-contract-audit.md` to classify and
    freeze the v1.0 compatibility surface.
-   Added dedicated v1 contract-freeze tests for SDK exports, Generator
    contracts, Plugin contracts, CLI behavior, Courseware Domain,
    built-in artifact contracts, Composition, AI, Marketplace,
    Configuration, Filesystem, public errors, and packaging metadata /
    console entry point.
-   Added `docs/releases/v1.0-public-contract-freeze-acceptance.md` as
    the Step 8.2 acceptance record.
-   Recorded the packaging audit finding that repository-level
    `templates/` require built-artifact and clean-install verification
    in Step 8.4 before they can be claimed as release-ready packaged
    resources.
-   Added `docs/releases/v1.0-reliability-hardening.md` as the governing
    Step 8.3 reliability / regression hardening plan.
-   Added v1 reliability tests for Filesystem, Generator lifecycle,
    Courseware Composition, Plugin loading, Marketplace, AI, CLI input
    boundaries, and representative reliability E2E behavior.
-   Added `docs/releases/v1.0-reliability-hardening-acceptance.md` as
    the Step 8.3 acceptance record.
-   Added `docs/releases/v1.0-packaging-installation.md` as the
    governing Step 8.4 packaging / installation / distribution design.
-   Added Step 8.4 build-artifact, installed-resource, clean-install,
    and template-resource migration contract coverage.
-   Added `generator.resources` as the package-owned runtime resource
    boundary.
-   Migrated runtime templates to canonical
    `generator/resources/templates/`.
-   Added `docs/releases/v1.0-packaging-installation-acceptance.md` as
    the Step 8.4 acceptance record.

-   Added the complete v1.0 English and Traditional Chinese (Taiwan) User Manuals with 13 paired chapters per language.
-   Added automated documentation structure, bilingual parity, functional parity, and First 15 Minutes installed-user verification.
-   Added `docs/releases/v1.0-documentation-user-manuals-acceptance.md` as the Step 8.5 acceptance record.

-   Added `docs/releases/v1.0-compatibility-deprecation-policy.md` as the
    governing Step 8.6 compatibility and deprecation policy.
-   Added `tests/compatibility/test_version_policy_contract.py` for
    release-series governance, classification boundaries, behavioral
    breaking-change rules, major-version removal policy, emergency
    exceptions, and Step 8.2 source-of-truth preservation.
-   Added `tests/compatibility/test_deprecation_policy_contract.py` for
    Deprecated Stable lifecycle, required deprecation records, migration
    guidance, EN/zh-TW parity, documentation / CHANGELOG obligations, and
    emergency compatibility exceptions.

-   Added `docs/reference/support-matrix.md` as the evidence-backed v1.0
    support contract.
-   Added `docs/releases/v1.0-known-limitations.md` as the canonical v1.0
    known-limitations and Deferred-scope register.
-   Added `tests/support/test_support_matrix_contract.py` and
    `tests/support/test_known_limitations_contract.py`.
-   Added exact Step 8.7 environment evidence for Ubuntu
    (`ubuntu-latest`) with Python 3.14 and the explicitly verified Windows
    maintainer environment with Python 3.14.5.
-   Added `docs/releases/v1.0-support-matrix-known-limitations-acceptance.md`
    as the Step 8.7 acceptance candidate.
-   Added `docs/releases/v1.0-release-automation-reproducibility-acceptance.md`
    as the Step 8.8 formal acceptance record.
-   Added completion-state Step 8.8 release-verification evidence covering
    release identity, artifact/checksum validation, GitHub Release
    consistency, clean-install behavior, semantic reproducibility, and the
    maintainer release process.
-   Added `docs/releases/v1.0-full-release-readiness-verification.md` as the
    governing Step 8.9 design for closure auditing, contract/policy/documentation
    consistency, artifact-backed installed-user verification, full quality
    gates, CI evidence, and formal readiness acceptance.
-   Added Step 8.9.2 Milestone 8 closure-contract automation covering required
    governing documents, accepted records, unresolved placeholders, and Roadmap
    terminal-state alignment.
-   Added Step 8.9.3 cross-document public-contract, compatibility/deprecation,
    support-matrix, and known-limitations consistency automation.
-   Added `tests/release_readiness/test_v1_documentation_first_15_minutes.py`
    as the Step 8.9.4 integration contract for the accepted documentation
    suites, 13-chapter EN/zh-TW parity, and current-wheel First 15 Minutes
    verification.
-   Added `tests/release_readiness/test_v1_artifact_backed_installed_user_e2e.py`
    as the Step 8.9.5 clean-environment contract for installed distribution
    identity, source-checkout isolation, console behavior, representative
    artifact generation, and invalid-command behavior.

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

-   Completed Step 8.7 support-matrix and known-limitations governing
    design through PR #128.
-   Completed Step 8.7 focused support-contract automation through PR
    #129; the focused suite passes with 31 tests.
-   Populated exact environment support evidence through PR #130.
-   Limited v1.0 environment support claims to evidence-backed
    combinations and kept all other Python/OS combinations unclaimed.
-   Formally accepted Step 8.7 Support Matrix / Known Limitations after
    acceptance PR #131 passed GitHub Actions / CI, was squash merged,
    `main` was synchronized with `origin/main`, and post-merge consistency
    verification completed.
-   Moved the active Milestone 8 focus to Step 8.8 --- Release Automation
    & Reproducibility.
-   Formally accepted Step 8.8 Release Automation & Reproducibility after
    acceptance PR #139 passed both required GitHub Actions checks, was squash
    merged as commit `f7d1b5f8a24d0169ee4fb5cf7484c1101a88abf7`, and
    completed main synchronization and post-merge consistency verification.
-   Kept Step 8.9 Full Release-readiness Verification as the next planned gate;
    Step 8.8 closure does not pre-approve or start Step 8.9.
-   Started Step 8.9 Full Release-readiness Verification with its governing
    design and verification inventory boundary.
-   Defined the Step 8.9 fail-closed delivery sequence from Steps 8.1–8.8
    closure auditing through representative installed-user E2E, full
    regression, CI verification, and formal acceptance.
-   Kept Step 8.10 RC Acceptance separate: Step 8.9 neither creates
    `v1.0.0-rc.1` nor pre-approves RC Acceptance.
-   Completed Step 8.9.2 with 28 focused closure-contract tests and corrected
    the Step 8.1 baseline status from `Proposed` to `Accepted`.
-   Moved the active verification slice to Step 8.9.3 Contract / Policy /
    Support Consistency Automation while preserving Steps 8.2, 8.6, and 8.7
    as their respective authorities.
-   Completed Step 8.9.3 with 50 focused release-readiness tests and a passing
    pre-commit run, then moved the active slice to Step 8.9.4 Documentation /
    First 15 Minutes Verification.
-   Required Step 8.9.4 final evidence to identify a current built wheel and
    execute the wheel-backed documentation tests; required skips cannot count
    as completion evidence.
-   Completed Step 8.9.4 through PR #144 and squash merge commit
    `234d683d9bae3a82cd2cda951d0926c1da1c9140`; post-merge current-wheel
    verification passed 116 documentation and release-readiness tests with
    zero required skips and a clean working tree.
-   Moved the active verification slice to Step 8.9.5 Artifact-backed
    Representative Installed-user E2E.
-   Completed Step 8.9.5 through PR #145 after both required GitHub Actions
    jobs passed and squash merged as commit
    `e34ce0d901c2c7a214c0785cdebeee1d3c63359b`.
-   Verified the Step 8.9.5 post-merge artifact-backed suite with 64 passed,
    zero required skips, and a clean working tree.
-   Moved the active verification slice to Step 8.9.6 Integrated Package /
    Release Identity Verification without creating a tag, GitHub Release, or
    RC.

-   Established the v1 compatibility rule: `1.0.x` for
    compatibility-preserving fixes, `1.x` for backward-compatible
    evolution, and `2.0` for intentional breaking Stable-contract changes.
-   Established the Deprecated Stable lifecycle and the normal rule that
    Stable removal is not permitted before the next major version.
-   Established mandatory migration guidance, user-facing EN/zh-TW
    functional parity, documentation / CHANGELOG obligations, and explicit
    emergency compatibility-exception evidence.
-   Kept Step 8.2 public-contract freeze tests authoritative for the exact
    v1.0 Stable surface.
-   Completed Step 8.6 compatibility/deprecation policy automation and
    documentation / CHANGELOG alignment.
-   Re-ran the completed repository against a real built wheel through
    `OPL_TEST_WHEEL`, preserving packaging, clean-install, and First 15
    Minutes installed-user verification in the Step 8.6 acceptance state.
-   Formally accepted Step 8.6 Compatibility & Deprecation Policy after
    acceptance PR #126 passed GitHub Actions / CI, was squash merged, and
    `main` was synchronized with `origin/main`.
-   Completed Step 8.6 post-merge consistency verification.
-   Moved the active Milestone 8 focus to Step 8.7 --- Support Matrix /
    Known Limitations.

-   Formally accepted Step 8.5 Documentation & Bilingual User Manuals after acceptance PR #120 passed GitHub Actions / CI, was squash merged, `main` was synchronized with `origin/main`, and post-merge consistency verification completed.
-   Moved the active Milestone 8 focus to Step 8.6 --- Compatibility & Deprecation Policy.

-   Started Milestone 8 --- v1.0 Stabilization & Release Readiness as
    the final pre-v1.0 engineering milestone.

-   Completed and formally accepted Step 8.2 public-contract freeze
    after final local regression, quality gates, and GitHub Actions / CI
    passed.

-   Classified the verified v1.0 public surface into Stable,
    Experimental, Internal, and Deferred boundaries without promoting
    unimplemented architecture proposals.

-   Kept Step 8.4 packaging / clean-install verification as the owner of
    the discovered template-resource packaging risk.

-   Started Step 8.3 Reliability / Regression Hardening under the Step
    8.2 frozen v1.0 contract boundary.

-   Completed the Step 8.3 reliability test implementation across the
    planned subsystems without expanding the frozen v1.0 public surface.

-   Preserved fail-fast Composition semantics without introducing
    cross-Generator rollback or generalized transaction guarantees.

-   Completed and formally accepted Step 8.3 Reliability / Regression
    Hardening after targeted reliability coverage, full regression,
    coverage, local quality gates, and GitHub Actions / CI passed.

-   Started Step 8.4 Packaging / Installation / Distribution under the
    frozen v1.0 public-contract boundary.

-   Replaced repository-root default template resolution with the
    package-owned `package_template_root()` boundary while preserving
    explicit template-root override behavior.

-   Removed the legacy repository-level runtime template dependency
    after isolation tests proved package-owned templates fully replace
    it.

-   Completed and formally accepted Step 8.4 Packaging / Installation /
    Distribution after local artifact verification and GitHub Actions /
    CI passed.

-   Added dedicated GitHub Actions artifact-path verification that builds
    wheel and sdist artifacts, validates them with Twine, resolves the
    exact built wheel through `OPL_TEST_WHEEL`, and runs the packaging
    suite against the real artifact.

-   Recorded Step 8.4 packaging artifact evidence: 29 packaging tests
    passed with 0 skipped using
    `openprojectlab-0.6.0-py3-none-any.whl`; the corresponding sdist is
    `openprojectlab-0.6.0.tar.gz`.

-   Moved the active Milestone 8 focus to Step 8.5 --- Documentation &
    Bilingual User Manuals.

-   Moved the active development focus from Marketplace feature
    completion to contract audit, stabilization, packaging,
    documentation, compatibility, release automation, and RC readiness.

-   Established that deferred Marketplace, AI, filesystem, and error
    capabilities remain non-blocking unless explicitly promoted through
    a later release-readiness decision.

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

-   Verified Step 8.7 support-contract automation passes with 31 tests.
-   Verified pre-commit passes for the Step 8.7 support/evidence state.
-   Verified PR #128 merged the v1.0 support-matrix / known-limitations
    governing design.
-   Verified PR #129 merged the v1 support-matrix contract automation.
-   Verified PR #130 merged the exact environment-support evidence.
-   Recorded Ubuntu (`ubuntu-latest`) + Python 3.14 as CI-backed Supported
    environment evidence.
-   Recorded Windows + Python 3.14.5 as maintainer-owned wheel-backed
    Supported environment evidence without generalizing the claim to all
    Windows configurations.
-   Recorded Step 8.7 completion-state full regression evidence:
    1679 passed, 1 deselected.
-   Verified Step 8.7 total coverage at 90.55%, above the required 67.0%
    gate.
-   Verified `git diff --check`, Ruff, Ruff Format, and pre-commit passed
    for the Step 8.7 local acceptance state.
-   Verified GitHub Actions / CI passed for Step 8.7 acceptance PR #131.
-   Verified Step 8.7 acceptance PR #131 was squash merged.
-   Verified local `main` is synchronized with `origin/main` after the
    acceptance merge.
-   Completed Step 8.7 post-merge consistency verification.
-   Marked Step 8.7 --- Support Matrix / Known Limitations as formally
    Accepted.

-   Recorded Step 8.8 completion-state full regression evidence:
    1777 passed, 1 deselected.
-   Verified Step 8.8 total coverage at 90.89%, above the required 67.0%
    gate.
-   Recorded the Step 8.8 completion-state evidence as fresh verification
    rather than reusing the Step 8.7 `1679 / 90.55%` baseline.
-   Verified Step 8.8 acceptance PR #139 passed GitHub Actions / CI with two
    successful checks and no failures, skips, cancellations, or pending checks.
-   Verified the Step 8.8 acceptance PR was squash merged as commit
    `f7d1b5f8a24d0169ee4fb5cf7484c1101a88abf7`.
-   Completed Step 8.8 main synchronization and post-merge consistency
    verification.
-   Re-ran the wheel-backed post-merge full regression with
    `1777 passed, 1 deselected in 37.40s` and 90.89% coverage.
-   Verified pre-commit and `git diff --check` passed with a clean working tree.
-   Marked Step 8.8 --- Release Automation & Reproducibility as formally
    Accepted.

-   Verified PR #122 merged the v1.0 compatibility and deprecation
    governing policy.
-   Verified PR #123 merged the v1 compatibility policy contract tests.
-   Verified PR #124 merged the v1 deprecation policy contract tests.
-   Recorded Step 8.6 policy automation as complete.
-   Recorded the Step 8.6 wheel-backed final local regression evidence:
    1648 passed, 1 deselected.
-   Verified Step 8.6 total coverage at 90.55%, above the required 67.0%
    gate.
-   Verified the wheel-backed run eliminates the 11 expected
    `OPL_TEST_WHEEL`-missing skips from the preceding source-only run.
-   Added
    `docs/releases/v1.0-compatibility-deprecation-policy-acceptance.md`
    as the Step 8.6 formal acceptance record.
-   Verified GitHub Actions / CI passed for Step 8.6 acceptance PR #126.
-   Verified acceptance PR #126 squash merged as
    `f3ae0584e8b47b5ccf0d94fe1a7882868d899580`.
-   Verified `HEAD`, local `main`, and `origin/main` resolve to the same
    acceptance merge commit.
-   Completed Step 8.6 post-merge consistency verification.
-   Marked Step 8.6 --- Compatibility & Deprecation Policy as formally
    Accepted.

-   Recorded the Step 8.5 final local regression evidence: 1616 passed, 1 deselected.
-   Verified Step 8.5 total coverage at 90.55%, above the required 67.0% gate.
-   Verified the executable First 15 Minutes documentation workflow passes with 3 passed and 0 skipped against the built-wheel path.
-   Verified documentation structure, EN/zh-TW parity, functional parity, `git diff --check`, Ruff, Ruff Format, and pre-commit for the Step 8.5 local acceptance state.
-   Verified GitHub Actions / CI passed for Step 8.5 acceptance PR #120.
-   Completed the Step 8.5 acceptance squash merge.
-   Verified local `main` is synchronized with `origin/main` after the acceptance merge.
-   Completed Step 8.5 post-merge consistency verification.
-   Marked Step 8.5 --- Documentation & Bilingual User Manuals as formally Accepted.

-   Verified the Step 8.2 dedicated v1 contract-freeze slices are green
    during incremental development.

-   Verified the corrected Marketplace v1 public-contract suite passes
    with 16 tests.

-   Recorded the Step 8.2 final local regression evidence: 1469 passed,
    1 deselected.

-   Verified total coverage at 90.33%, above the required 67.0% gate.

-   Verified `git diff --check`, Ruff, Ruff Format, and pre-commit
    passed for the completed Step 8.2 repository state.

-   Verified GitHub Actions / CI passed for the Step 8.2 acceptance PR.

-   Marked Step 8.2 --- Public Contract Audit & Freeze as formally
    Accepted.

-   Verified the consolidated Step 8.3 reliability suite passes with 66
    tests.

-   Verified Step 8.3 hardening covers failure-before-side-effect,
    deterministic repetition, atomic-write failure preservation,
    temporary-file cleanup, Plugin batch atomicity, Marketplace
    integrity-before-installation, AI structured-output rejection, CLI
    input failures, and representative Composition fail-fast behavior.

-   Recorded the Step 8.3 final local regression evidence: 1535 passed,
    1 deselected.

-   Verified total coverage at 90.54%, above the required 67.0% gate.

-   Verified `git diff --check`, Ruff, Ruff Format, and pre-commit
    passed for the completed Step 8.3 repository state.

-   Verified GitHub Actions / CI passed for the Step 8.3 acceptance PR.

-   Marked Step 8.3 --- Reliability / Regression Hardening as formally
    Accepted.

-   Verified Step 8.4 wheel and sdist builds pass.

-   Verified `python -m twine check dist/*` passes.

-   Verified required runtime templates are present in the built wheel.

-   Verified clean-wheel installation imports the installed `generator`
    package without repository `PYTHONPATH` or editable installation.

-   Verified installed `opl list` and representative installed
    generation pass using package-owned runtime resources.

-   Verified the legacy repository-level runtime template dependency is
    removed.

-   Recorded the Step 8.4 final local regression evidence: 1558 passed,
    1 deselected.

-   Verified total coverage at 90.55%, above the required 67.0% gate.

-   Verified `git diff --check`, Ruff, Ruff Format, and pre-commit
    passed for the completed Step 8.4 local repository state.

-   Verified GitHub Actions / CI passed for the Step 8.4 acceptance PR.

-   Verified the dedicated GitHub `Packaging artifact verification` job
    passed together with the existing `Quality checks` job.

-   Verified the Step 8.4 packaging suite passes with 29 tests and 0
    skipped against `openprojectlab-0.6.0-py3-none-any.whl`.

-   Marked Step 8.4 --- Packaging / Installation / Distribution as
    formally Accepted.

-   Milestone 7 historical evidence was not reused.

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
