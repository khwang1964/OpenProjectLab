# Changelog

## Unreleased
<!-- v1.2.3-dry-run-execution-preview-changelog -->

- Started `v1.2.3 Dry-run Execution Preview` as a Design First slice over the
  accepted and implemented Bootstrap Planning Core.
- Proposed immutable `BootstrapDryRunStep`, `BootstrapDryRunPreview`, and a
  projection-only `BootstrapDryRunExecutor`.
- Required reuse of the authoritative immutable `BootstrapPlan`, deterministic
  preview ordering, and equivalent-preview behavior.
- Kept expected effects descriptive and prohibited generator execution,
  persistent writes, network access, plugin activation, and partial state.
- Kept apply and validation runtime at `Not Started`, checkpoint/resume and
  generalized rollback `Deferred`, Stable CLI syntax `Not Accepted`, and
  production implementation `Not Started`.

<!-- v1.2.2.1-bootstrap-planning-core-terminal-changelog -->

- Completed the first production Bootstrap Planning Core implementation in
  PR #228, squash merged as `528f356a3160af5445a9e4b4193ee5e62029653e`.
- Added immutable `BootstrapStep`, `BootstrapPlan`, and `ExpectedEffect`
  models and deterministic `BootstrapPlanner`.
- Reused the existing `GeneratorRegistry.names()` lookup boundary without
  instantiating or executing generators.
- Verified deterministic ordering and equivalent-plan behavior.
- Preserved mutation-free planning with no filesystem writes, network access,
  or plugin activation.
- Kept dry-run, apply, and validation runtime at `Not Started`.
- Kept Stable Bootstrap CLI syntax at `Not Accepted`.
<!-- v1.2.2-bootstrap-planning-core-acceptance-changelog -->

- Accepted `v1.2.2 Bootstrap Planning Core` after Design PR #226 squash merged
  as `c76c1b931da7d0aaf13792546b451c46f4769fe0`.
- Accepted `BootstrapStep`, `BootstrapPlan`, and `BootstrapPlanner` design
  contracts.
- Accepted deterministic ordering, equivalent-plan behavior,
  GeneratorRegistry reuse, and Generator lifecycle preservation.
- Preserved mutation-free planning with no generator execution, network
  access, or plugin activation.
- Kept expected effects as descriptive data only.
- Kept dry-run, apply, and validation runtime at `Not Started`.
- Kept checkpoint/resume and generalized rollback Deferred.
- Kept Stable Bootstrap CLI syntax at `Not Accepted`.
- Kept `v1.2 Implementation` at `Not Started`.
<!-- v1.2.2-bootstrap-planning-core-changelog -->

- Started `v1.2.2 --- Bootstrap Planning Core` as the first
  implementation-oriented Design First slice under the accepted Bootstrap
  Framework architecture.
- Defined `BootstrapStep`, `BootstrapPlan`, and `BootstrapPlanner` planning
  contracts.
- Required deterministic ordering and equivalent-plan behavior.
- Required reuse of the existing GeneratorRegistry and Generator lifecycle.
- Kept filesystem mutation, generator execution, network access, and plugin
  activation forbidden during planning.
- Kept expected effects as descriptive data only.
- Kept dry-run, apply, and validation runtime at `Not Started`.
- Kept checkpoint/resume and generalized rollback Deferred.
- Kept Stable Bootstrap CLI syntax at `Not Accepted`.
- Kept `v1.2.2 Bootstrap Planning Core` at `Not Accepted`.
- Kept `v1.2 Implementation` at `Not Started`.
<!-- v1.2.1-bootstrap-framework-design-acceptance-changelog -->

- Accepted `v1.2.1 Bootstrap Framework Design Baseline` after Design PR #224
  squash merged as `f9f98b35aef679d2521498d6246c201906a3e721`.
- Recorded synchronized-main post-merge focused verification at `9 passed`.
- Accepted the Bootstrap Framework architecture and core design contracts.
- Kept Checkpoint / Resume Deferred.
- Kept Stable Bootstrap CLI syntax at `Not Accepted`.
- Kept `v1.2 Implementation` at `Not Started`.

<!-- v1.2.1-bootstrap-framework-design-changelog -->

- Started `v1.2.1 --- Bootstrap Framework Design Baseline` as the first
  Design First slice after acceptance of the v1.2 Planning Baseline.
- Added the governing Bootstrap Framework design contract and architecture.
- Proposed `BootstrapPlan`, `BootstrapStep`, and `BootstrapResult` as the
  core orchestration contracts.
- Defined mutation-free `plan` and `dry-run`, with `apply` as the explicit
  committed-mutation phase.
- Required reuse of the existing Generator lifecycle and filesystem
  abstraction; no parallel mutation pipeline or alternative Generator
  lifecycle is accepted.
- Defined fail-closed execution and inspection-only validation semantics;
  validation failure does not imply automatic rollback.
- Kept generalized rollback and Checkpoint / Resume Deferred.
- Kept Stable Bootstrap CLI syntax at `Not Accepted`.
- Kept `v1.2.1 Bootstrap Framework Design Baseline` at `Not Accepted`.
- Kept `v1.2 Implementation` at `Not Started`.
<!-- v1.2-planning-baseline-acceptance-changelog -->

- Accepted the v1.2 Planning Baseline after PR #222 merged as
  `cc710f57141f7766acbb4e1ff3feb1884549ea2e`.
- Recorded post-merge focused verification at `10 passed`.
- Accepted `v1.2.1 --- Bootstrap Framework Design Baseline` as the next
  Design First slice.
- Kept `v1.2 Implementation` at `Not Started`.

<!-- v1.2-planning-baseline-changelog -->

-   Started the v1.2 Planning Baseline from accepted predecessor merge
    `55781b43f7b661a48338601cb22a4d69a120c584`.
-   Prioritized Bootstrap Framework maturity first, followed by
    Developer/Release Automation, AI-assisted generation, and Marketplace
    production workflow.
-   Proposed `v1.2.1 --- Bootstrap Framework Design Baseline` as the first
    implementation slice.
-   Kept `v1.2 Planning Baseline` at `Not Accepted`.
-   Kept `v1.2 Implementation` at `Not Started`.
-   Preserved Design First / Documentation First / Automation First boundaries.


-   Accepted Post-v1.1 Roadmap Planning after PR #220 passed required CI and squash merged as `8459d3f42a08dc4364624215a77ec58c04b7539f`.
-   Completed main synchronization and post-merge planning consistency verification.
-   Recorded focused post-merge verification `10 passed`.
-   Recorded full regression `2322 passed, 56 skipped, 1 deselected` with total coverage `91.17%` against required `67.0%`.
-   Formally selected `v1.2` as the next backward-compatible feature-release boundary.
-   Marked `Next Version Decision` and `v1.2 Planning Baseline` as Accepted.
-   Kept `v1.2 Implementation` at `Not Started` pending the next Design First contract.


<!-- post-v1.1-roadmap-planning-changelog -->

-   Entered Post-v1.1 Roadmap Planning after terminal acceptance of v1.1 at
    `9997e9d85ed3672451c6c538d464d07a93d3d9cb`.
-   Selected `v1.2` as the current next-version planning boundary and
    classified it as a backward-compatible feature release.
-   Established Bootstrap Framework maturity, AI-assisted project/course
    generation, Marketplace production workflow, and developer/release
    automation as candidate workstreams.
-   Kept `Next Version Decision` at `Not Yet Accepted`; this planning slice
    does not accept v1.2.
-   Kept `v1.2 Implementation` at `Not Started` pending planning acceptance,
    Design First architecture contracts, executable tests, and required
    governance/CI closure.
-   Kept v2.0 out of scope unless a future architecture decision proves that
    an intentional Stable-contract break is necessary.


-   Terminally accepted OpenProjectLab v1.1 after Formal Acceptance PR #218
    passed required CI and squash merged as `c740613f5ac29d696962545afb2ee0f5b0c8c630`.
-   Completed main synchronization and post-merge formal-acceptance consistency.
-   Recorded full regression `2312 passed, 53 skipped, 1 deselected` and total
    coverage `91.17%` against the required `67.0%` threshold.
-   Preserved repository historical identity `1.0.0` and v1.1 candidate
    identity `1.1.0rc1` / `v1.1.0-rc.1`.
-   Marked Formal v1.1 Acceptance and v1.1 as terminally Accepted.


-   Started v1.1.9 Formal v1.1 Acceptance pre-acceptance closure.
-   Recorded focused formal-acceptance verification `35 passed, 20 skipped in 0.12s`.
-   Recorded full regression `2312 passed, 53 skipped, 1 deselected` with total coverage
    `91.17%`; required coverage threshold `67.0%` passed.
-   Recorded `git diff --check` and pre-commit as Passed.
-   Kept Formal v1.1 Acceptance at `Not Accepted`; PR CI, squash merge,
    main synchronization, post-merge consistency, and terminal acceptance
    alignment remain Pending.


-   Accepted v1.1.8 Reliability / Artifact-backed Verification after PR #216
    passed required CI and squash merged as `19103257e7fe405f8d38ad4e43fd549e78867bde`.
-   Preserved repository canonical identity `1.0.0` while verifying the
    temporary-build candidate identity `1.1.0rc1` / `v1.1.0-rc.1`.
-   Verified candidate build evidence, wheel/sdist identity, checksums,
    clean-installed CLI behavior, Marketplace and AI Stable installed-user
    surfaces, First 15 Minutes onboarding, full regression, required coverage,
    `git diff --check`, pre-commit, and post-merge consistency.
-   Marked v1.1.8 `Accepted` while keeping Formal v1.1 Acceptance
    `Not Accepted`; next gate is v1.1.9 Formal v1.1 Acceptance.


### Added

#### v1.1 Planning Baseline

-   Started the OpenProjectLab v1.1 Planning Baseline with Operational CLI
    Expansion as the proposed release theme.
-   Added `docs/releases/v1.1-planning-baseline.md` as the governing v1.1
    scope, compatibility, non-goal, delivery, and acceptance contract.
-   Preserved the accepted v1.0 Stable public-contract subset and required all
    v1.1 evolution to remain backward compatible.
-   Defined additive deterministic-local Marketplace CLI and
    provider-independent AI CLI as planned contract slices; implementation
    remains Not Started until dedicated contracts are accepted.
-   Kept remote Marketplace, automatic activation, signing/trust, dependency
    resolution, ratings/reviews, monetization, AI Provider Marketplace, AI
    Refactoring Assistant, streaming/tool calling, and generalized transaction
    rollback Deferred.
-   Added fail-closed v1.1 planning-contract automation covering terminal
    document alignment, compatibility preservation, explicit non-goals,
    documentation parity, artifact-backed verification, and prohibition of
    fabricated future evidence.
-   Recorded the current governing state as `v1.1 Planning Baseline --- In
    Progress` and `Formal v1.1 Acceptance --- Not Accepted`.
-   Verified governing baseline PR #164 passed required Quality checks and
    Packaging artifact verification, then squash merged as
    `33c367b989014c34c162f326ee825f3fe8f4c8e6`.
-   Completed governing-baseline main synchronization and lightweight
    post-merge consistency verification.
-   Added `docs/releases/v1.1-planning-baseline-acceptance.md` and focused
    fail-closed acceptance automation.
-   Started `v1.1.1 Acceptance Closure --- In Progress` while preserving
    `Formal v1.1 Planning Baseline Acceptance --- Not Accepted`, `Marketplace
    CLI --- Not Started`, `AI CLI --- Not Started`, and `Formal v1.1 Acceptance
    --- Not Accepted`.
-   Kept acceptance PR CI, squash merge, main synchronization, post-merge
    consistency, and terminal documentation alignment Pending.
-   Verified acceptance PR #165 passed required CI and squash merged as
    `97dac1eca516e7b91e2f5bdfbe6da84b7a32215c`.
-   Completed acceptance main synchronization, the post-merge focused suite
    with `15 passed`, repository consistency gates, and terminal documentation
    alignment.
-   Marked `v1.1.1 Planning Baseline --- Accepted` and `Formal v1.1 Planning
    Baseline Acceptance --- Accepted` while preserving `Marketplace CLI ---
    Not Started`, `AI CLI --- Not Started`, and `Formal v1.1 Acceptance --- Not
    Accepted`.
-   Moved the next active slice to `v1.1.2 CLI Public Contract Design` without
    introducing product implementation.
-   Added `docs/releases/v1.1-cli-public-contract.md` as the governing v1.1.2
    design for additive command families, v1.0 CLI compatibility, exit and
    stream behavior, machine-readable output, and failure-before-side-effect
    boundaries.
-   Added `tests/integration/test_v1_1_cli_public_contract.py` as fail-closed
    design automation preserving the reviewed v1 command inventory while
    preventing premature `marketplace` or `ai` production registration.
-   Defined `opl marketplace ...` and `opl ai ...` only as reserved command
    families for their dedicated later contract slices; both implementations
    remain `Not Started`.
-   Preserved the existing broad Stable exit behavior (`0` for success and `2`
    for reviewed usage or handled operational failure) without claiming a
    finer taxonomy, exact human-readable messages, or a production `--json`
    contract.
-   Verified the focused v1/v1.1 CLI public-contract suite with `40 passed`.
-   Recorded `v1.1.2 CLI Public Contract Design --- In Progress`, `Formal v1.1
    CLI Public Contract Acceptance --- Not Accepted`, and `Formal v1.1
    Acceptance --- Not Accepted`; full regression, coverage, local quality
    gates, PR, CI, merge, and post-merge evidence remain unrecorded until run.
-   Verified governing design PR #167 passed required CI and squash merged as
    `2727bba27a1438b949870f9dee7df4aa16d43244` without registering the
    reserved `marketplace` or `ai` command families.
-   Added `docs/releases/v1.1-cli-public-contract-acceptance.md` and
    `tests/integration/test_v1_1_cli_public_contract_acceptance.py` to start
    fail-closed v1.1.2 acceptance closure.
-   Kept acceptance-state execution, acceptance PR/CI/merge, main
    synchronization, post-merge consistency, terminal alignment, and Formal
    v1.1 CLI Public Contract Acceptance Pending / Not Accepted.
-   Completed acceptance-state focused verification with `48 passed` and full
    regression with `2008 passed, 32 skipped, 1 deselected in 22.37s`; the
    required 67.0% coverage gate, `git diff --check`, and pre-commit passed.
-   Verified acceptance PR #168 passed required CI run `32362619408` and
    squash merged as `044e80ae39b01b5006663e44ea4db0f4a98a8482`.
-   Kept main synchronization, post-merge consistency, terminal alignment,
    and Formal v1.1 CLI Public Contract Acceptance Pending / Not Accepted
    until synchronized-main evidence is supplied.
-   Synchronized local `main` with `origin/main` at
    `044e80ae39b01b5006663e44ea4db0f4a98a8482`, confirmed a clean working tree,
    and preserved the immutable `v1.0.0` tag target at
    `d469b41b898d80811a14a423d08b09d0b51bc189`.
-   Advanced the remaining closure gate to post-merge focused and local
    consistency verification; terminal alignment remains Pending.
-   Verified the synchronized-main post-merge focused CLI acceptance suite
    with `48 passed in 0.22s`; post-merge local quality and clean-tree gates
    remain Pending.
-   Verified final post-merge `git diff --check`, pre-commit, pytest hook, and
    clean-working-tree consistency passed on synchronized `main`.
-   Completed terminal documentation alignment and marked `v1.1.2 CLI Public
    Contract Design --- Accepted` and `Formal v1.1 CLI Public Contract
    Acceptance --- Accepted` while preserving `Formal v1.1 Acceptance --- Not
    Accepted`.
-   Moved the next active slice to `v1.1.3 Marketplace CLI Contract`; no
    Marketplace CLI or AI CLI implementation was introduced by acceptance.
-   Added `docs/releases/v1.1-marketplace-cli-contract.md` as the governing
    v1.1.3 design for deterministic local catalog discovery, exact artifact
    inspection, payload verification, and non-activating installation.
-   Added `tests/integration/test_v1_1_marketplace_cli_contract.py` as
    fail-closed contract automation that prevents premature production parser
    registration or implementation claims.
-   Defined the proposed `opl marketplace versions`, `inspect`, `verify`, and
    `install` command surface while explicitly excluding a fabricated global
    `list` operation from the existing repository contract.
-   Preserved local-only catalog and payload resolution, exact coordinates,
    SHA-256 integrity verification, failure-before-side-effect behavior,
    non-persistent installation, and explicit `--dry-run` and `--json`
    boundaries.
-   Kept remote Marketplace access, activation, dependency resolution,
    publisher trust/signing, ratings/reviews, and monetization Deferred.
-   Verified the focused Marketplace contract suite with `35 passed`, all
    pre-commit hooks, and the full regression suite with `2018 passed, 32
    skipped, 1 deselected in 23.05s`.
-   Recorded `v1.1.3 Marketplace CLI Contract --- In Progress`, `Marketplace
    CLI Contract --- Not Accepted`, `Marketplace CLI Implementation --- Not
    Started`, and `Formal v1.1 Acceptance --- Not Accepted`; governing PR, CI,
    merge, synchronization, and post-merge evidence remain Pending.
-   Recorded governing contract PR #170 as squash merged at
    `5f63bd3dc438ba1ea5e10b8225c761964c1819bc` and synchronized local `main`
    with `origin/main` at that commit with a clean working tree.
-   Added `docs/releases/v1.1-marketplace-cli-contract-acceptance.md` and
    `tests/integration/test_v1_1_marketplace_cli_contract_acceptance.py` to
    begin a separate fail-closed v1.1.3 Acceptance Closure.
-   Kept fresh acceptance-state focused/full-regression/coverage/local-quality
    execution, governing required CI evidence confirmation, acceptance
    PR/CI/merge, post-merge consistency, and terminal documentation alignment
    Pending.
-   Verified the fresh v1.1.3 acceptance-state focused suite with `84 passed`
    and zero failures/errors.
-   Verified the fresh acceptance-state full regression with `1533 passed, 11
    skipped, 1 deselected in 11.00s` and zero failures/errors.
-   Verified all pre-commit hooks, including Ruff, Ruff Format, and pytest,
    passed for the acceptance candidate.
-   Kept governing required CI, required coverage, and `git diff --check`
    evidence Pending confirmation; acceptance PR/CI/merge and all post-merge
    gates also remain Pending.
-   Preserved `Marketplace CLI Contract --- Not Accepted`, `Marketplace CLI
    Implementation --- Not Started`, and `Formal v1.1 Acceptance --- Not
    Accepted`; the governing merge alone does not satisfy acceptance.
-   Confirmed the remaining v1.1.3 governing CI, required coverage,
    `git diff --check`, acceptance-state, and post-merge quality gates passed.
-   Recorded `Acceptance PR #171 --- Merged` and `Acceptance merge ---
    02ed8569bbd5a6c12632783186220954b2b99f12`, synchronized `main`, and
    completed post-merge consistency verification.
-   Completed terminal documentation alignment and marked
    `v1.1.3 Marketplace CLI Contract --- Accepted` and
    `Marketplace CLI Contract Acceptance --- Accepted` while preserving
    `Marketplace CLI Implementation --- Not Started` and
    `Formal v1.1 Acceptance --- Not Accepted`.
-   Recorded `Next --- v1.1.4 Marketplace CLI Implementation` as the active
    follow-up slice.
-   Started `v1.1.4 Marketplace CLI Implementation --- In Progress` with a
    Design First implementation baseline; production parser registration and
    command handlers remain Not Started.
-   Clarified that internal `MarketplaceRepository.list_artifacts()` exists
    but remains intentionally outside the accepted Marketplace CLI surface;
    v1.1.4 does not add `opl marketplace list`.
-   Defined the implementation sequence for internal parsing/catalog adapters,
    `versions`/`inspect`, safe `verify`, non-activating `install`, deterministic
    JSON/diagnostics, production registration, bilingual manuals, and formal
    implementation acceptance.
-   Added fail-closed design automation requiring architecture, tests,
    EN/zh-TW functional parity, executable documentation, and the canonical
    in-repository use-case demo boundary before implementation can be accepted.
-   Completed the v1.1.4.1 implementation baseline and implemented the
    v1.1.4.2 internal identity, coordinate, and strict UTF-8 JSON catalog
    adapters without registering the production `marketplace` parser.
-   Verified implementation PR #174 passed required CI and squash merged as
    `0ac32017b1420464c7c52a2b63993fc4e27a63b4`; synchronized `main` and
    completed focused post-merge adapter verification.
-   Completed v1.1.4.2 terminal documentation alignment while preserving
    `Production Parser Registration --- Not Started`, `Marketplace CLI Command
    Handlers --- Not Started`, and `Formal v1.1 Acceptance --- Not Accepted`.
-   Moved the next active implementation slice to `v1.1.4.3 versions / inspect`.
-   Started `v1.1.4.3 versions / inspect --- In Progress` with internal,
    side-effect-free query services over the accepted repository boundary;
    production parser registration remains Not Started.
-   Verified implementation PR #176 passed required CI and squash merged as
    `d1fbfbbd60c9d7ae14efdff443ff550032f279c2`; synchronized `main` and
    completed post-merge versions/inspect verification.
-   Completed `v1.1.4.3 versions / inspect` terminal documentation alignment
    while preserving production parser registration and all later Marketplace
    CLI implementation slices as Not Started.
-   Moved the next active slice to
    `v1.1.4.4 verify / Safe Payload Acquisition` while preserving
    `Formal v1.1 Acceptance --- Not Accepted`.
-   Started `v1.1.4.4 verify / Safe Payload Acquisition --- In Progress` with
    file-only local containment, SHA-256 verification, and explicit
    failure-before-installation boundaries; production parser registration
    remains Not Started.
-   Verified implementation PR #178 passed required CI and squash merged as
    `ec0a77cd19d8783e2877228ece0a9e006579436e`; synchronized `main` and
    completed post-merge safe-verification checks.
-   Completed `v1.1.4.4 verify / Safe Payload Acquisition` terminal alignment
    while preserving installation and production parser registration as Not
    Started and `Formal v1.1 Acceptance --- Not Accepted`.
-   Moved the next active slice to
    `v1.1.4.5 install / dry-run / No-partial-state`.
-   Started `v1.1.4.5 install / dry-run / No-partial-state --- In Progress`
    with verification-before-installation orchestration, immutable outcomes,
    dry-run no-install behavior, and duplicate-installation preservation;
    production parser registration remains Not Started.
-   Verified implementation PR #180 passed required CI and squash merged as
    `4de1347edc09d959cd8b00d6acc6f459defd938e`; synchronized `main` and
    completed focused post-merge install/dry-run verification.
-   Completed `v1.1.4.5 install / dry-run / No-partial-state` terminal
    alignment while preserving production parser registration as Not Started
    and `Formal v1.1 Acceptance --- Not Accepted`.
-   Moved the next active slice to
    `v1.1.4.6 Deterministic JSON and Diagnostics`.
-   Started `v1.1.4.6 Deterministic JSON and Diagnostics --- In Progress` with
    command-specific schema-version-1 JSON documents, deterministic compact
    encoding, human stdout rendering, handled diagnostics on stderr, and the
    existing broad `0`/`2` exit boundary; production parser registration
    remains Not Started.
-   Verified implementation PR #182 passed required CI and squash merged as
    `b415f7f02f9c81d92341a010c449ff619d97b8cd`; synchronized `main` and
    completed post-merge JSON/diagnostics verification.
-   Completed `v1.1.4.6 Deterministic JSON and Diagnostics` terminal alignment
    while preserving `Production Parser Registration --- Not Started` and
    `Formal v1.1 Acceptance --- Not Accepted`.
-   Moved the next active implementation slice to
    `v1.1.4.7 Production Parser Registration`.
-   Started `v1.1.4.7 Production Parser Registration --- In Progress` by
    registering exactly `versions`, `inspect`, `verify`, and `install`, wiring
    the accepted local catalog/payload services and deterministic renderers,
    and preserving the prohibition on `opl marketplace list`.
-   Replaced historical parser-absence assertions with exact additive
    inventory, v1 preservation, stdout/stderr, exit `0`/`2`, and production
    handler integration assertions; AI CLI and Formal v1.1 Acceptance remain
    Not Started / Not Accepted.
-   Verified implementation PR #184 passed required CI and squash merged as
    `85f8ec822270fd3c993fc0b23fa70367681bcb0c`; synchronized `main` and
    completed the post-merge production parser and documentation-parity smoke.
-   Completed `v1.1.4.7 Production Parser Registration` terminal alignment,
    including the exact four-command inventory and completed production
    Marketplace handlers, while preserving Formal v1.1 Acceptance as Not
    Accepted.
-   Moved the next active slice to
    `v1.1.4.8 EN / zh-TW User Manual Updates`.
-   Started `v1.1.4.8 EN / zh-TW User Manual Updates --- In Progress` with
    functionally equivalent Marketplace CLI chapters documenting the exact
    four-command inventory, local catalog/payload workflow, dry-run, JSON,
    stream/exit behavior, non-activation, and Deferred capabilities.
-   Added bilingual CLI chapter links and executable documentation automation
    that runs a documented Marketplace command against a local fixture while
    preserving the frozen v1.0 manual contract and Formal v1.1 Acceptance as
    Not Accepted.
-   Verified documentation PR #186 passed required CI and squash merged as
    `6a3a98d22ed2e2a995bb8d497ae5f7ff5607a0b4`; synchronized `main` and
    completed the post-merge bilingual documentation and parser smoke.
-   Completed `v1.1.4.8 EN / zh-TW User Manual Updates` terminal alignment
    with `EN / zh-TW Marketplace CLI Manuals --- Complete`, while preserving
    `Formal v1.1 Acceptance --- Not Accepted`.
-   Moved the next active slice to
    `v1.1.4.9 Full Regression / CI / Formal Acceptance`.
-   Started `v1.1.4.9 Full Regression / CI / Formal Acceptance --- In
    Progress` from synchronized `main` at
    `f7910d51c49c74614381491458414739c47d5d74`.
-   Recorded the acceptance-candidate full regression as `2150 passed, 33
    skipped, 1 deselected` in 23.77s with 90.74% total coverage, and the
    Marketplace-focused regression as `160 passed, 1 skipped` in 1.07s.
-   Added the Formal v1.1 acceptance candidate record and fail-closed
    automation. Formal v1.1 Acceptance remains Not Accepted until the
    acceptance PR, required CI, squash merge, synchronized `main`, post-merge
    verification, and terminal documentation alignment are complete.
-   Verified acceptance PR #188 passed required CI and squash merged as
    `a89d0d4e7b8fd068c1c4e2b841489bf211efbf28`; synchronized `main` and
    completed post-merge verification with `56 passed` focused, `2158 passed,
    33 skipped, 1 deselected` full regression, and 90.74% total coverage.
-   Completed v1.1.4.9 terminal documentation alignment and accepted the
    deterministic-local Marketplace CLI implementation as
    `Marketplace CLI Implementation Acceptance --- Accepted` without
    overclaiming Formal v1.1 Acceptance. The next governed slice is
    `v1.1.5 AI CLI Contract`.
-   Started `v1.1.5 AI CLI Contract --- In Progress` as a design-only slice
    over the existing provider-independent AI services. Proposed commands are
    exactly `course`, `review`, `document`, and `template`; production parser
    registration and AI CLI implementation remain Not Started.
-   Defined deterministic local response-file execution as the Stable core
    path and explicit live-provider invocation as Experimental and opt-in.
    Normal tests and required CI remain credential-free and network-independent.

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
-   Added `docs/releases/v1.0-full-release-readiness-verification-acceptance.md`
    as the Step 8.9 formal acceptance record, initially retaining post-merge
    closure gates as Pending until synchronized-main evidence is recorded.
-   Added `docs/releases/v1.0-rc-acceptance.md` as the governing
    Step 8.10 RC Acceptance contract.
-   Defined `v1.0.0-rc.1` as the first canonical RC identity while keeping
    RC Acceptance separate from `v1.0.0` GA Acceptance.
-   Added fail-closed RC identity requirements covering approved source
    commit, package version, wheel / sdist metadata, artifact checksums,
    RC tag, installed-user evidence, and GitHub Release identity.
-   Added `tests/release_readiness/test_v1_rc_acceptance_contract.py`
    to automate the Step 8.10 governing-contract boundary.
-   Added `docs/releases/v1.0-rc-build-artifact-identity.md` as the
    Step 8.10.4 RC Build / Artifact Identity governing design.
-   Added `tests/release_readiness/test_v1_rc_build_artifact_identity.py`
    for focused RC package-version, tag-mapping, artifact-metadata,
    stale-artifact, and checksum identity verification.
-   Added `docs/releases/v1.0-rc-artifact-backed-verification.md` as the
    Step 8.10.5 governing design for checksum-bound installed-user
    verification of the current RC wheel.
-   Added `tests/release_readiness/test_v1_rc_artifact_backed_verification.py`
    as the RC-specific coordination contract over the existing packaging,
    First 15 Minutes, installed-user E2E, and integrated release-identity
    verification layers.
-   Added `docs/releases/v1.0-rc-creation-publication-identity.md` as the
    Step 8.10.8 publication-identity contract for approved source SHA,
    immutable RC tag, draft-first GitHub prerelease, exact published assets,
    and post-publication re-verification.
-   Added `docs/releases/v1.0-rc-acceptance-record.md` as the Step 8.10.9
    formal RC acceptance candidate record.
-   Added `tests/release_readiness/test_v1_rc_formal_acceptance.py` as the
    fail-closed Step 8.10.9 automation preventing premature RC acceptance
    while PR/CI/merge/main-sync/post-merge closure gates remain Pending.
-   Added `docs/releases/v1.0-ga-acceptance.md` as the governing
    `v1.0.0` GA Acceptance contract.
-   Added `docs/releases/v1.0-ga-baseline.md` and
    `docs/releases/v1.0-ga-rc-evidence-review.md` for GA.1 baseline and
    reviewed blocker disposition.
-   Added `docs/releases/v1.0-ga-build-artifact-identity.md` and
    `tests/release_readiness/test_v1_ga_build_artifact_identity.py` for
    stable `1.0.0 / v1.0.0` version and artifact identity.
-   Added `docs/releases/v1.0-ga-artifact-backed-verification.md` and
    `tests/release_readiness/test_v1_ga_artifact_backed_verification.py`
    as the GA.4 fail-closed artifact-backed coordination gate.
-   Added `docs/releases/v1.0-ga-creation-publication-identity.md` and
    `tests/release_readiness/test_v1_ga_creation_publication_identity.py`
    for GA.7 stable tag / GitHub Release publication identity.
-   Added `docs/releases/v1.0-ga-acceptance-record.md` and
    `tests/release_readiness/test_v1_ga_formal_acceptance.py` for GA.8
    fail-closed Formal GA Acceptance / Post-merge closure.

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

-   Accepted v1.1.7 Documentation / EN-zh-TW Parity after PR #214 passed
    required CI and squash merged as `eafc65cd849ffbe546e2228e1027cca4863452a7`.
-   Re-ran synchronized-main post-merge focused documentation verification
    (`60 passed in 0.21s`) and the complete documentation suite
    (`97 passed, 3 skipped in 0.60s`), with `git diff --check` and pre-commit Passed.
-   Advanced the release sequence to v1.1.8 Reliability / Artifact-backed
    Verification while keeping Formal v1.1 Acceptance at `Not Accepted`.


-   Started v1.1.7 Documentation / EN-zh-TW Parity release-level coordination.
-   Added a fail-closed release documentation parity contract covering the
    bilingual chapter structure, Marketplace CLI, AI CLI, and First 15 Minutes
    / onboarding authorities.
-   Verified the documentation suite with `97 passed, 3 skipped in 0.43s`, plus
    `git diff --check` and pre-commit Passed.
-   Kept v1.1.7 at `In Progress` and Formal v1.1 Acceptance at
    `Not Accepted` pending PR / CI / merge / post-merge closure.


-   Accepted v1.1.6.11 AI CLI Implementation after PR #212 passed required CI
    and squash merged as `a6f2161d0affba59cae19cbe4deb5f7b6cd91b84`.
-   Re-ran synchronized-main post-merge focused verification
    (`============================= 47 passed in 1.06s ==============================`), full regression (`=============== 2277 passed, 33 skipped, 1 deselected in 27.57s ===============`), and total
    coverage (`91.17%`); `git diff --check` and pre-commit passed.
-   Marked AI CLI Implementation Acceptance as `Accepted` while keeping Formal
    v1.1 Acceptance at `Not Accepted`.


-   Started v1.1.6.11 Full Regression / AI CLI Implementation Acceptance from
    the accepted v1.1.6.10 terminal baseline.
-   Added a fail-closed AI CLI implementation acceptance record and automation
    covering the exact four-command inventory, Stable local-response behavior,
    Experimental provider boundaries, failure semantics, non-mutating behavior,
    and EN / zh-TW parity.
-   Kept AI CLI Implementation Acceptance and Formal v1.1 Acceptance at
    `Not Accepted` until PR/CI/merge/post-merge/terminal closure completes.


-   Accepted v1.1.6.10 AI CLI EN / zh-TW User Manual Parity after
    Documentation PR #210 passed required CI and squash merged as
    `e982c0cad94511a649e0701ec0682855cd3db8ea`.
-   Re-verified the bilingual documentation contract from synchronized `main`
    with `80 passed` and pre-commit Passed.
-   Recorded post-merge consistency verification as Passed and advanced the
    next gate to v1.1.6.11 Full Regression / AI CLI Implementation Acceptance.
-   Kept AI CLI Implementation Acceptance and Formal v1.1 Acceptance at
    `Not Accepted`.


-   Added v1.1.6.10 AI CLI EN / zh-TW User Manual Parity documentation and
    fail-closed parity automation.
-   Documented the exact `course`, `review`, `document`, and `template` AI CLI
    command inventory in both formal User Manuals.
-   Aligned Stable deterministic local-response behavior, Experimental
    explicit/injection-only/fail-closed provider behavior, exit-code 2 /
    stderr / no-success-output failure semantics, and non-mutating boundaries.
-   Explicitly rejected automatic SDK import, automatic credential lookup,
    implicit provider selection, and network fallback in both manuals.
-   Recorded local documentation verification at `80 passed` with pre-commit
    Passed while keeping AI CLI Implementation Acceptance and Formal v1.1
    Acceptance at `Not Accepted`.


-   Completed v1.1.6.9 AI CLI Production Parser Registration through
    PR #208, squash merged as
    `2befa064c8172fe2dab05c06d3737935d38642be`.
-   Registered the exact `course`, `review`, `document`, and `template`
    AI subcommand inventory in the production parser.
-   Preserved deterministic stable local-response execution and the existing
    exit-2 / stderr diagnostic boundary.
-   Preserved Experimental provider execution as explicit, injection-only,
    and fail-closed; parser registration does not own SDK import, credential
    lookup, implicit provider selection, or network fallback.
-   Marked v1.1.6.9 Production Parser Registration as Accepted while keeping
    AI CLI Implementation Acceptance and Formal v1.1 Acceptance Not Accepted.
-   Advanced the next AI CLI slice to v1.1.6.10 EN / zh-TW User Manual
    Parity.

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
-   Completed Step 8.9.6 integrated package / release identity verification
    through PR #146.
-   Completed Step 8.9.7 full regression and local quality gates with
    `1822 passed, 22 skipped, 1 deselected`, 90.89% coverage, passing
    pre-commit and `git diff --check`, and a clean working tree.
-   Reviewed all 22 Step 8.9.7 skips as expected artifact-backed tests requiring
    `OPL_TEST_WHEEL`, `OPL_TEST_DIST_DIR`, or `OPL_RELEASE_COMMIT_SHA`.
-   Completed Step 8.9.8 GitHub Actions / CI verification for acceptance PR
    #147; workflow run `32229975851` passed both `Quality checks` and
    `Packaging artifact verification`.
-   Squash merged Step 8.9 acceptance PR #147 as commit
    `9b0566b3fc4d2b0b94ae5e775fdd3c86c0e79e03`.
-   Advanced the active Milestone 8 slice to Step 8.9.9 Formal Acceptance /
    Post-merge Consistency. Main synchronization, post-merge verification, and
    final Step 8.9 `Accepted` status remain pending actual closure evidence.
-   Fixed the Step 8.9.9 closure-contract document scope so the active Step 8.9
    governing and acceptance records are excluded from the prior Steps 8.1–8.8
    debt scan without weakening forbidden closure markers.
-   Added regression coverage for the corrected Step 8.9 document-selection
    boundary; the targeted closure-contract suite passed 29 tests.
-   Recorded fresh pre-merge full-regression evidence for the closure-scope
    correction: `1823 passed, 22 skipped, 1 deselected`, with zero failures.
-   Verified PR #148 CI workflow `32232518973` passed both required
    jobs and squash merged as commit `0d1fdc5a22c0de38d3b3f806a7e85197a65e2e3d`.
-   Completed the final Step 8.9.9 synchronized-main post-merge verification
    at `0d1fdc5a22c0de38d3b3f806a7e85197a65e2e3d` with `HEAD == main == origin/main`.
-   Recorded the final post-merge full regression as
    `1823 passed, 22 skipped, 1 deselected` with zero failures/errors and 90.89% coverage against
    the required 67.0% gate.
-   Verified `git diff --check`, Ruff, Ruff Format, pre-commit, pytest hook,
    and clean-working-tree consistency after PR #148.
-   Aligned Roadmap, HISTORY, CHANGELOG, the governing Step 8.9 record, and
    the formal acceptance record to the same terminal state.
-   Formally accepted Step 8.9 --- Full Release-readiness Verification.
-   Made Step 8.10 --- RC Acceptance the next independent release gate without
    creating or pre-accepting `v1.0.0-rc.1`.
-   Started Step 8.10 --- RC Acceptance after the accepted Step 8.9
    repository baseline.
-   Completed Step 8.10.1 RC Acceptance Baseline, Step 8.10.2 RC
    Acceptance Contract, and Step 8.10.3 RC Contract Automation.
-   Preserved the RC / GA acceptance boundary and prohibited source-only,
    stale-artifact, skipped-required-gate, tag-retargeting, and unpublished
    placeholder evidence from satisfying formal RC acceptance.
-   Moved the active Milestone 8 slice to Step 8.10.4 --- RC Build /
    Artifact Identity without creating a tag or GitHub Release.
-   Updated the canonical package version from `0.6.0` to `1.0.0rc1` for
    the first v1.0 Release Candidate.
-   Updated RC tag derivation so PEP 440 package version `1.0.0rc1`
    deterministically maps to the human-facing release identity
    `v1.0.0-rc.1`, while stable `vX.Y.Z` tag mapping remains unchanged.
-   Completed Step 8.10.4 RC Build / Artifact Identity against source
    commit `11a997c2b9787cdae34b15818c6170948e89b7fc` with fresh wheel / sdist artifacts and exact
    checksum verification.
-   Moved the active Milestone 8 slice to Step 8.10.5 --- RC
    Artifact-backed Verification without creating a tag, GitHub Release,
    or formal RC acceptance.
-   Completed Step 8.10.5 RC Artifact-backed Verification against source
    commit `784a139b4afc91779d6b3c76fe35162a0e348261` with the fresh `1.0.0rc1` wheel / sdist,
    checksum-bound artifact identity, source-checkout isolation,
    installed `opl`, packaged runtime resources, First 15 Minutes, and
    representative installed-user E2E all verified.
-   Preserved fail-closed source/artifact binding: an initial run using
    stale `OPL_RELEASE_COMMIT_SHA=11a997c2b9787cdae34b15818c6170948e89b7fc`
    failed against current `HEAD=784a139b4afc91779d6b3c76fe35162a0e348261`; fresh artifacts and all
    four RC artifact inputs were then regenerated/rebound before
    completion.
-   Moved the active Milestone 8 slice to Step 8.10.6 --- RC Full
    Regression / Local Quality Gates, without creating a tag, GitHub
    Release, or formal RC acceptance.
-   Completed Step 8.10.6 RC Full Regression / Local Quality Gates with
    `1881 passed, 1 deselected`, zero failures/errors, zero required
    artifact-backed skips, and 90.90% coverage against the required
    67.0% gate.
-   Verified `git diff --check`, Ruff, Ruff Format, and pre-commit for the
    Step 8.10.6 completion-state repository.
-   Moved the active Milestone 8 slice to Step 8.10.7 --- RC GitHub
    Actions / CI without creating a tag, GitHub Release, or formal RC
    acceptance.
-   Completed Step 8.10.7 RC GitHub Actions / CI after PR #152 passed
    both required GitHub Actions jobs and completed squash merge / main
    synchronization.
-   Completed Step 8.10.8 RC Creation / Publication Identity using approved
    publication commit `b5958edbbf0e3279ed74fa0e3aee13e893c5dfc8` and immutable RC tag `v1.0.0-rc.1`.
-   Published the exact verified RC asset set as a GitHub prerelease:
    `openprojectlab-1.0.0rc1-py3-none-any.whl`, `openprojectlab-1.0.0rc1.tar.gz`, and `SHA256SUMS.txt`.
-   Verified the published wheel SHA-256 as `0dbea1bdbf972a91c25aeb84e5441cb308df866b269ab8f7feea8d099d93d337` and the published
    sdist SHA-256 as `37e2593a4693b7f038da1b9f0b3ae83643fff2d989992a185a3cdc9022098ea2`.
-   Verified the checksum-manifest asset SHA-256 as `0b56ca72ab9aec34afabcf3fb00d170522a923d4e0120df3bca6234061bb3c4f`.
-   Verified the GitHub Release was draft-first, then published with
    `draft=false`, `prerelease=true`, and target commit `b5958edbbf0e3279ed74fa0e3aee13e893c5dfc8`.
-   Started Step 8.10.9 Formal RC Acceptance / Post-merge with an
    Acceptance Candidate record; formal RC acceptance remains Pending until
    acceptance PR/CI/merge/main-sync/post-merge closure completes.
-   Completed Step 8.10.9 Formal RC Acceptance / Post-merge through
    acceptance PR #154.
-   Verified PR #154 required CI passed and squash merged as
    `d37a3d84161e66e98ebbff2aafaf1a14e27f865c`.
-   Completed synchronized-main post-merge consistency and cross-document
    terminal-state alignment.
-   Formally accepted Step 8.10 --- RC Acceptance for `v1.0.0-rc.1`.
-   Preserved the immutable published RC source/tag identity at
    `b5958edbbf0e3279ed74fa0e3aee13e893c5dfc8`; the acceptance merge does not retarget the RC.
-   Closed Milestone 8 RC Acceptance while keeping `v1.0.0` GA Acceptance
    explicitly Not Accepted.
-   Started the independent `v1.0.0` GA Acceptance lifecycle after formal
    RC acceptance.
-   Completed GA.1 RC evidence review with no recorded unresolved GA blocker
    found in the reviewed evidence and no GA correction required by that
    evidence.
-   Transitioned the canonical package version from `1.0.0rc1` to stable
    `1.0.0` while preserving historical RC identity.
-   Completed GA.4 Artifact-backed Verification with `30 passed` and zero
    required GA artifact-backed skips.
-   Recorded GA.5 fresh full-regression evidence with
    `1980 passed, 4 skipped, 1 deselected` and 90.90% coverage.
-   Classified the four GA.5 skips as historical RC artifact-backed checks
    correctly refusing to consume GA artifacts as RC evidence.
-   Completed GA.5 Full Regression / Local Quality Gates after the fresh
    `1980 passed, 4 skipped, 1 deselected` regression completed with zero
    failures/errors, 90.90% coverage, zero required GA artifact-backed skips,
    and passing `git diff --check`, Ruff, Ruff Format, and pre-commit gates.
-   Advanced the active GA gate to GA.6 GitHub Actions / CI while keeping
    `v1.0.0` tag creation, GA publication, and Formal GA Acceptance pending.
-   Completed GA.6 GitHub Actions / CI with both required jobs passing.
-   Completed GA.7 GA Creation / Publication Identity using stable
    `v1.0.0`, with annotated tag target bound to the approved publication
    commit, draft-first non-prerelease GitHub Release validation, stable
    publication, and post-publication identity re-read.
-   Started GA.8 Formal GA Acceptance / Post-merge with an acceptance record
    and fail-closed contract automation; Formal `v1.0.0` GA Acceptance
    remains Not Accepted until PR/CI/merge/main-sync/post-merge closure.
-   Completed GA.8 Formal GA Acceptance / Post-merge after required CI,
    squash merge, synchronized `main`, clean-working-tree verification,
    post-merge regression, local quality gates, and terminal documentation
    alignment all passed.
-   Recorded the GA.8 acceptance merge / terminal-main SHA as
    `d13382c359873c2a9eb8fb9cf6d39e32636d5fc1`.
-   Formally accepted OpenProjectLab `v1.0.0` GA while preserving the
    immutable published `v1.0.0` tag and artifact source identity.

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

-   Verified the Step 8.9.9 closure-scope correction targeted suite passes with
    29 tests.
-   Recorded the closure-scope correction full regression:
    1823 passed, 22 skipped, 1 deselected, with zero failures.
-   Verified pre-commit and `git diff --check` passed before PR #148.
-   Verified PR #148 GitHub Actions workflow `32232518973` passed both
    `Quality checks` and `Packaging artifact verification`.
-   Verified PR #148 squash merged as
    `0d1fdc5a22c0de38d3b3f806a7e85197a65e2e3d`.
-   Verified final synchronized-main identity after PR #148:
    `HEAD == main == origin/main == 0d1fdc5a22c0de38d3b3f806a7e85197a65e2e3d`.
-   Recorded final Step 8.9 post-merge regression evidence:
    1823 passed, 22 skipped, 1 deselected, zero failures/errors, 90.89% coverage.
-   Verified final post-merge `git diff --check`, Ruff, Ruff Format,
    pre-commit, pytest hook, and clean working tree.
-   Completed Step 8.9 post-merge consistency and cross-document alignment.
-   Marked Step 8.9 --- Full Release-readiness Verification as formally
    Accepted.
-   Verified Step 8.10.4 canonical package version `1.0.0rc1` and
    human-facing RC tag mapping `v1.0.0-rc.1`.
-   Built fresh Step 8.10.4 artifacts:
    `openprojectlab-1.0.0rc1-py3-none-any.whl` and `openprojectlab-1.0.0rc1.tar.gz`.
-   Verified the Step 8.10.4 focused release / packaging / integrated
    identity suite passes with `70 passed, 0 skipped`.
-   Verified SHA-256 identity for the RC wheel:
    `5c6a968b5d4225d758ecedc8fa15441c64812cc413ee62d302cf2521eb0b1629`.
-   Verified SHA-256 identity for the RC sdist:
    `34c2bcc33f0265a8f25d1770ea209472fbcdf12f803217e87574de3f08acef12`.
-   Verified the checksum manifest matches the exact current artifact
    bytes.
-   Verified Step 8.10.5 artifact-backed completion against source commit
    `784a139b4afc91779d6b3c76fe35162a0e348261` with `59 passed` and zero required artifact-backed
    skips.
-   Verified the installed RC distribution reports `1.0.0rc1`, imports
    outside the source checkout, exposes the installed `opl` entry point,
    consumes package-owned runtime resources, passes First 15 Minutes,
    and passes the representative installed-user E2E.
-   Verified the Step 8.10.5 checksum manifest and integrated
    package/release identity against the fresh current RC artifact set.
-   Recorded Step 8.10.6 completion-state full regression evidence:
    `1881 passed, 1 deselected`, with zero failures/errors and zero
    required artifact-backed skips.
-   Verified Step 8.10.6 total coverage at 90.90%, above the required
    67.0% gate.
-   Verified Step 8.10.6 `git diff --check`, Ruff, Ruff Format, and
    pre-commit all passed.
-   Verified Step 8.10.7 required GitHub Actions / CI jobs passed.
-   Verified remote annotated `v1.0.0-rc.1` peels to approved publication commit
    `b5958edbbf0e3279ed74fa0e3aee13e893c5dfc8`.
-   Verified Step 8.10.8 published GitHub prerelease identity, exact asset
    membership, final artifact digests, and post-publication identity re-read.
-   Verified the Step 8.10.9 formal-acceptance candidate focused suite passes
    with `41 passed`.
-   Verified Step 8.10.9 acceptance PR #154 was squash merged as
    `d37a3d84161e66e98ebbff2aafaf1a14e27f865c`.
-   Verified Step 8.10 post-merge consistency and terminal document alignment
    completed with no remaining RC acceptance closure gate Pending.
-   Verified formal RC Acceptance is `Accepted` while `v1.0.0` GA Acceptance
    remains `Not Accepted`.
-   Verified GA.4 artifact-backed coordination passes with `30 passed`,
    zero failures, and zero required GA artifact-backed skips.
-   Verified the installed GA distribution reports `1.0.0`, executes outside
    the source checkout, exposes the installed `opl` entry point, consumes
    packaged runtime resources, passes First 15 Minutes, and passes the
    representative installed-user E2E.
-   Recorded GA.5 fresh full-regression evidence:
    `1980 passed, 4 skipped, 1 deselected`, zero failures/errors, 90.90%
    coverage, and the required 67.0% coverage gate passed.
-   Verified the four skips are historical RC artifact-backed tests and do
    not count as GA required artifact-backed skips.
-   Verified GA.5 `git diff --check`, Ruff, Ruff Format, and pre-commit all
    passed.
-   Marked GA.5 Full Regression / Local Quality Gates as Completed and GA.6
    GitHub Actions / CI as In Progress.
-   Verified GA.6 required GitHub Actions / CI jobs passed.
-   Verified GA.7 stable publication identity for `v1.0.0`, including
    draft-first validation, non-prerelease classification, exact stable asset
    membership, and post-publication identity re-read.
-   Verified GA.8 pre-acceptance contract suite passes with `43 passed`.
-   Kept Formal `v1.0.0` GA Acceptance at `Not Accepted` pending GA.8
    acceptance PR, required CI, squash merge, synchronized main, post-merge
    consistency, and terminal documentation alignment.
-   Verified GA.8 post-merge `HEAD == origin/main ==
    d13382c359873c2a9eb8fb9cf6d39e32636d5fc1`.
-   Recorded final GA.8 post-merge full-regression evidence:
    `2004 passed, 4 skipped, 1 deselected`, zero failures, and 90.90%
    coverage against the required 67.0% gate.
-   Verified the four skips remain historical RC artifact-backed checks
    rejecting the configured GA wheel and are not GA-required skips.
-   Verified final pre-commit and repository consistency gates passed.
-   Marked GA.8 as Completed and Formal `v1.0.0` GA Acceptance as
    `Accepted`.

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


<!-- v1.2.3-dry-run-execution-preview-acceptance-changelog -->

- Accepted the v1.2.3 Dry-run Execution Preview design after PR #230 passed
  required CI and squash merged as
  `5f26cf2526ff39de381129d76791d0c28d06c91a`.
- Recorded synchronized-main post-merge focused verification at `11 passed`.
- Kept production dry-run implementation at `Not Started`; the next slice is
  the minimum Dry-run Execution Preview implementation.


<!-- v1.2.3-dry-run-execution-preview-terminal-changelog -->

- Completed the v1.2.3 minimum Dry-run Execution Preview implementation in
  PR #232, squash merged as `ac4cd405098d1179eb5dc5cb7e32f3e9590bb98f`.
- Added immutable `BootstrapDryRunStep`, `BootstrapDryRunPreview`, and the
  projection-only `BootstrapDryRunExecutor.preview(plan)` boundary.
- Recorded post-merge focused verification at `19 passed` while preserving
  mutation-free behavior and keeping apply, validation runtime, and Stable CLI
  syntax outside the slice.

<!-- v1.2.4-bootstrap-apply-execution-changelog -->

- Started v1.2.4 Bootstrap Apply Execution as a Design First slice.
- Proposed immutable apply-step/result evidence and a sequential
  `BootstrapApplyExecutor` coordination boundary.
- Required reuse of the existing BootstrapPlan, Generator lifecycle, and
  filesystem abstraction; direct ExpectedEffect execution is forbidden.
- Defined fail-fast partial-state evidence without generalized rollback or
  transaction-wide atomicity.
- Kept validation, parallel apply, checkpoint/resume, Stable CLI syntax, and
  production implementation outside this design slice.


<!-- v1.2.4-bootstrap-apply-execution-acceptance-changelog -->

- Accepted the v1.2.4 Bootstrap Apply Execution design after PR #234 passed
  required CI and squash merged as `1e0f7ebba9b98dd1c6bfa5edad52efa1bae7f0b6`.
- Recorded synchronized-main post-merge focused verification at `9 passed`.
- Kept production apply implementation at `Not Started`; the next slice is
  the minimum Bootstrap Apply Execution implementation.


<!-- v1.2.4-bootstrap-apply-execution-terminal-changelog -->

- Completed the v1.2.4 minimum Bootstrap Apply Execution implementation in
  PR #236, squash merged as `1fbf799bd6bc687592a46788fc98f2dda1b79907`.
- Added immutable apply-step/result evidence, sequential Generator lifecycle
  reuse, and fail-fast partial-state reporting.
- Recorded post-merge focused verification at `30 passed`, full regression at
  `2409 passed, 56 skipped, 1 deselected`, and coverage at `91.05%`.
- Kept validation, generalized rollback, checkpoint/resume, and Stable CLI
  syntax outside the implementation slice.

<!-- v1.2.5-bootstrap-validation-runtime-changelog -->

- Started v1.2.5 Bootstrap Validation Runtime as a Design First slice.
- Proposed immutable validation request, finding, and result contracts plus an
  injected check boundary and deterministic validator.
- Required inspection-only behavior and deterministic check/finding ordering.
- Distinguished invalid-state findings from fail-closed check failures.
- Kept repair, re-apply, rollback, parallel validation, Stable CLI syntax,
  public SDK expansion, and production implementation outside this slice.


<!-- v1.2.5-bootstrap-validation-runtime-acceptance-changelog -->

- Accepted the v1.2.5 Bootstrap Validation Runtime design after PR #238
  passed required CI and squash merged as `eadc9b96a0a7f4231331da162ee9c586cd9613e6`.
- Recorded post-merge focused verification at `9 passed` and kept production
  implementation at `Not Started` pending the separate minimum slice.


<!-- v1.2.5-bootstrap-validation-runtime-terminal-changelog -->

- Completed the v1.2.5 minimum Bootstrap Validation Runtime implementation in
  PR #240, squash merged as `902256c2dbb7ec384abe31decdeeb555240a85ce`.
- Added immutable validation requests, findings, results, ordered injected
  checks, severity-derived validity, and fail-closed completed evidence.
- Recorded post-merge focused verification at `20 passed`, full regression at
  `2430 passed, 56 skipped, 1 deselected`, and coverage at `91.04%`.
- Kept repair, rollback, checkpoint/resume, parallel validation, and Stable CLI
  syntax outside the implementation slice.


<!-- v1.2.6-bootstrap-runtime-integration-design-changelog -->

- Defined the v1.2.6 Bootstrap Runtime Integration design-first boundary.
- Proposed immutable mode/request/result contracts and an internal coordinator.
- Required exactly-once planning, explicit mutation modes, deterministic phase
  ordering, and fail-closed typed failure propagation.


<!-- v1.2.6-bootstrap-runtime-integration-acceptance-changelog -->

- Terminally accepted the v1.2.6 Bootstrap Runtime Integration design after
  PR #242, required CI, merge `4045a21514e912548456569a272a983f32ba5c4b`, and synchronized-main verification.
- Preserved production implementation, CLI, SDK, repair, rollback, checkpoint,
  and parallel-execution boundaries for separate slices.


<!-- v1.2.6-bootstrap-runtime-integration-terminal-changelog -->

- Completed the v1.2.6 minimum Bootstrap Runtime Integration implementation in
  PR #244, squash merged as `f126238de83fc4fe12f4cb6de1d281fccd4281d0`.
- Added explicit preview, apply, and apply-and-validate coordination with one
  authoritative plan, deterministic ordering, and fail-closed propagation.
- Recorded post-merge focused verification at `18 passed`, full regression at
  `2449 passed, 56 skipped, 1 deselected`, and coverage at `91.04%`.
- Kept CLI and SDK expansion, repair, rollback, checkpoint/resume, and parallel
  execution outside this implementation slice.


<!-- v1.2.6-bootstrap-runtime-integration-implementation-closure-changelog -->

- Accepted and completed the v1.2.6 minimum Bootstrap Runtime Integration
  implementation after terminal evidence PR #245, merge `c4971d97dc193a75eddad76faf1ea1c36c222fd5`.
- Verified synchronized-main consistency with `19 passed` focused tests.
- Preserved the accepted deterministic lifecycle and all deferred CLI, SDK,
  repair, rollback, checkpoint/resume, and parallel-execution boundaries.


<!-- v1.2.7-bootstrap-cli-runtime-wiring-design-changelog -->

- Defined the v1.2.7 Bootstrap CLI/runtime wiring design, compatibility,
  fail-closed adapter, deferred boundaries, tests, and review checklist.
- Kept production CLI wiring and stable runtime option spelling out of scope
  pending terminal design acceptance.


<!-- v1.2.7-bootstrap-cli-runtime-wiring-acceptance-changelog -->

- Accepted the v1.2.7 Bootstrap CLI/runtime wiring design after PR #247,
  merge `a254574d7fc9570402f445518f00714ce5e644e0`, required CI, and synchronized-main `9 passed` verification.
- Preserved existing Bootstrap behavior without opt-in and kept production CLI
  wiring for a separate implementation slice.


<!-- v1.2.7-bootstrap-cli-runtime-wiring-terminal-changelog -->

- Completed the v1.2.7 minimum experimental Bootstrap CLI/runtime wiring in
  PR #249, squash merged as `ea8dcb3df06679ad2cea84eab228db0c97373b4f`.
- Added explicit runtime and validation opt-ins with fail-closed mode mapping
  while preserving legacy behavior without opt-in.
- Recorded post-merge focused verification at `16 passed`, full regression at
  `2467 passed, 56 skipped, 1 deselected`, and coverage at `91.08%`.
- Kept stable option spelling and advanced/public surfaces deferred.


<!-- v1.2.7-bootstrap-cli-runtime-wiring-implementation-closure-changelog -->

- Accepted and completed the v1.2.7 minimum experimental Bootstrap CLI/runtime
  wiring after terminal evidence PR #250, merge `fe66ca9c5fd751937f5feeaa7c1bae8b7285b719`.
- Verified synchronized-main consistency with `27 passed` focused tests.
- Preserved legacy no-opt-in behavior and all deferred public or advanced
  lifecycle boundaries.

<!-- v1.2.8-bootstrap-cli-public-contract-design-changelog -->

- Started the v1.2.8 Design First contract for Bootstrap CLI public-contract
  stabilization.
- Defined proposed parsing, exit-status, output-channel, failure-preservation,
  legacy-compatibility, and deferred SDK/advanced-lifecycle boundaries.
- Production stabilization remains Not Started.

<!-- v1.2.8-bootstrap-cli-public-contract-acceptance-changelog -->

- Terminally accepted the v1.2.8 Bootstrap CLI public-contract design after PR
  #252, merge `262cdf6b76f811a158579c58ec9fcbeb25dec6fd`, required CI, and synchronized-main verification.
- Preserved the experimental opt-in, legacy behavior, and deferred SDK, JSON,
  repair, rollback, and advanced lifecycle boundaries.
- Production stabilization remains Not Started.

<!-- v1.2.8-bootstrap-cli-public-contract-terminal-alignment-changelog -->

- Integrated terminal evidence for v1.2.8 Bootstrap CLI public-contract
  implementation PR #254, merge `1d36d568ca0b09cde2f8e12418bfdb63e72f14e2`.
- Verified the synchronized implementation with `38 passed` focused tests and
  preserved legacy exit behavior plus all deferred boundaries.
- Formal minimum implementation acceptance remains Pending.

<!-- v1.2.8-bootstrap-cli-public-contract-implementation-closure-changelog -->

- Accepted and completed the v1.2.8 Bootstrap CLI public-contract minimum
  implementation after terminal-alignment PR #255, merge
  `6d9b96cb651a0423ffdeb75094a645b99f4786b5`, required CI, and `39 passed` post-merge verification.
- Preserved legacy compatibility and deferred SDK, JSON, repair, rollback, and
  advanced lifecycle scope.
- Left the next roadmap slice pending explicit Design First definition.

## v1.2.9 Bootstrap SDK Runtime Public Contract (Design First)

- Added the design and architecture contract for a typed, deterministic, silent SDK bootstrap adapter.
- Added executable release-readiness checks while leaving production implementation Not Started.
