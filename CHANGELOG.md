# Changelog

## Unreleased

### Added

#### Milestone 5 — Open Courseware Platform

- Added the Open Courseware Platform architecture and responsibility boundaries.
- Added ADR 0014 and minimum production `Course` / `Week` domain models.
- Added Course/Week domain contract tests for identity, validation,
  immutability, duplicate rejection, and deterministic ordering.
- Added ADR 0015 — Lab Generator Contract.
- Added `LabGenerator` as the first concrete material Generator.
- Added the canonical `lab` built-in Generator identity.
- Added deterministic Lab output at
  `week-{week:02d}/lab/{lab_id}/README.md`.
- Added the default Lab README template.
- Added Lab contract tests, generator integration tests, and CLI integration tests.
- Added the `lab` CLI command and Lab exposure through built-in generator listing.
- Added Lab manifest integration using the existing manifest schema.
- Added ADR 0016 — Quiz Generator Contract.
- Added `QuizGenerator` as the second concrete material Generator.
- Added canonical `quiz` built-in Generator identity and Week-scoped `quiz_id`.
- Added structured single-answer multiple-choice question validation with explicit
  Question IDs, ordered choices, and correct-answer membership validation.
- Added deterministic Quiz output at
  `week-{week:02d}/quiz/{quiz_id}/README.md`.
- Added the learner-facing Quiz README template without answer-key exposure.
- Added Quiz contract tests, generator integration tests, and CLI integration tests.
- Added the `quiz` CLI command and built-in `list` / legacy `--list` exposure.
- Added structured Quiz CLI input through `--questions-file` JSON.
- Added Quiz manifest integration using the existing manifest schema.
- Added ADR 0017 — Assignment Generator Contract.
- Added `AssignmentGenerator` as the third concrete Week-scoped material Generator.
- Added canonical `assignment` built-in identity and explicit Week-scoped `assignment_id`.
- Added ordered Assignment objectives, deliverables, and resources plus authored
  instructions and submission guidance.
- Added deterministic Assignment output at
  `week-{week:02d}/assignment/{assignment_id}/README.md`.
- Added the Assignment README template.
- Added Assignment contract tests, generator integration tests, and CLI integration tests.
- Added the `assignment` CLI command and built-in `list` / legacy `--list` exposure.
- Added structured Assignment CLI input through `--content-file` JSON.
- Added Assignment manifest integration using the existing manifest schema.
- Added ADR 0018 — Slides Generator Contract.
- Added `SlidesGenerator` as the first presentation-source Generator.
- Added canonical `slides` built-in identity and deterministic `<target>/slides.md` output.
- Added the canonical `templates/slides/slides.md.j2` template and manifest registration.
- Added Slides contract tests, generator integration tests, template tests, and CLI integration tests.
- Added the `slides` CLI command and built-in `list` / legacy `--list` exposure.
- Added structured Slides CLI input through `--slides-file` JSON.
- Added Slides manifest integration using the existing manifest schema.

#### Milestone 4 — Plugin Ecosystem

- Added ADR 0010 through ADR 0012 for the Plugin SDK, validation, and Entry Point contracts.
- Added the stable `generator.sdk` public façade.
- Added canonical `openprojectlab.generators` Entry Point discovery/loading.
- Added Plugin validation, registry preflight, and transactional registration.
- Added the SDK-only example third-party Plugin distribution.
- Added real installed-distribution E2E validation.
- Added `docs/milestones/milestone-4-acceptance.md`.

### Changed

- Marked ADR 0018 — Slides Generator Contract as Accepted after design, contract,
  implementation, integration, regression, documentation, and CI gates completed.
- Updated Open Courseware architecture to mark Slides as Implemented while Website,
  composition orchestration, and PPTX / PDF / HTML rendering remain Proposed.
- Preserved `GenerateRequest`, `GenerationPlan`, `GenerationResult`, dry-run,
  overwrite, manifest, filesystem, and renderer boundaries for Slides.
- Preserved `generator.sdk` without adding Slides-specific public symbols.

- Marked ADR 0016 — Quiz Generator Contract as Accepted after design, contract,
  implementation, integration, regression, and CI gates completed.
- Marked ADR 0017 — Assignment Generator Contract as Accepted after design,
  contract, implementation, integration, regression, documentation, and CI gates completed.
- Updated Open Courseware architecture to mark Assignment as Implemented while
  PPT/Slides, Website, shared LearningMaterial abstractions, composition orchestration,
  grading/scoring/rubric runtime, submission backend, starter-code packaging, and
  courseware-specific SDK expansion remain Proposed.
- Updated Open Courseware architecture to mark Quiz as Implemented while Assignment,
  PPT/Slides, Website, shared LearningMaterial abstractions, composition orchestration,
  answer-key generation, assessment runtime, and courseware-specific SDK exposure
  remain Proposed.
- Preserved `GenerateRequest`, `GenerationPlan`, `GenerationResult`, dry-run,
  overwrite, manifest, filesystem, and renderer boundaries for Quiz.
- Preserved `generator.sdk` without adding Quiz-specific public symbols.

- Marked ADR 0015 — Lab Generator Contract as Accepted after contract,
  implementation, integration, and CI gates completed.
- Updated Open Courseware architecture to mark Lab as Implemented while
  Quiz, Assignment, PPT/Slides, Website, shared LearningMaterial abstractions,
  composition orchestration, and courseware-specific SDK exposure remain Proposed.
- Updated the Milestone 5 roadmap from planning to active implementation.
- Preserved `GenerateRequest`, `GenerationPlan`, `GenerationResult`,
  dry-run, overwrite, manifest, filesystem, and renderer boundaries for Lab.
- Preserved `generator.sdk` without adding Course/Week/Lab-specific public symbols.
- Marked Milestone 4 — Plugin Ecosystem as Completed and moved active development
  focus to Milestone 5.

### Removed

- Removed the legacy `generator.core.plugin.PluginManager`.
- Removed the legacy internal `PluginDescriptor` runtime path.

### Migration

- Existing Course/Week Generator contracts remain unchanged.
- Lab callers should use canonical generator name `lab`.
- Lab identity is Week-scoped and explicitly uses `lab_id`; title is display metadata.
- Lab artifacts are rooted at `week-{week:02d}/lab/{lab_id}/`.
- Third-party Plugin implementations continue to depend on `generator.sdk`;
  ADR 0015 does not expand the public Plugin SDK.

### Verification

- Verified Slides request validation for deck title, ordered slides, slide titles,
  ordered content, immutability, and deterministic planning.
- Verified deterministic Slides `slides.md` generation and slide/content ordering.
- Verified Slides dry-run, overwrite, manifest, built-in list, JSON input, and CLI integration.
- Verified PPTX / PDF / HTML rendering remains outside the core Slides Generator boundary.
- Verified PR #59 through PR #62 complete the Slides design/test/implementation/integration sequence.
- Verified the full regression suite at the integration baseline: 738 passed.

- Verified Quiz request validation for Week, `quiz_id`, title, Questions, choices,
  and correct-answer membership.
- Verified explicit/unique Question IDs and deterministic Question/choice ordering.
- Verified deterministic Quiz `GenerationPlan` destinations.
- Verified learner-facing Quiz artifacts do not expose correct-answer data.
- Verified Quiz dry-run, overwrite, manifest, built-in list, JSON input, and CLI integration.
- Verified PR #49 through PR #52 complete the Quiz design/test/implementation/integration sequence.

- Verified Lab request validation for Week, `lab_id`, and title.
- Verified deterministic Lab `GenerationPlan` destinations.
- Verified validation-before-planning behavior.
- Verified dry-run creates no persistent Lab artifacts or manifest changes.
- Verified overwrite protection and existing filesystem semantics.
- Verified Lab manifest records use the existing schema.
- Verified built-in list and CLI Lab integration.
- Verified existing Course/Week/domain contracts remain green.
- Verified no accidental `generator.sdk` expansion.
- Verified Ruff, pre-commit, pytest, coverage, and GitHub Actions through the
  Lab design/test/implementation/integration PR sequence.

------------------------------------------------------------------------

### Milestone 3 Generator Framework

- Added ADR 0005 through ADR 0009 to define shared Generator input,
  validation, planning, execution, and legacy lifecycle removal contracts.
- Established `BaseGenerator.run(GenerateRequest)` as the framework-controlled
  canonical execution entry point.
- Removed legacy `GeneratorContext` lifecycle hooks and Generator-specific
  result compatibility types.
