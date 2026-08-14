# Milestone 5 Acceptance — Open Courseware Platform

> Status: Accepted
> Milestone: 5 — Open Courseware Platform
> Acceptance branch: `docs/accept-milestone-5`
> Scope: Domain contracts, courseware generators, presentation/publishing projections,
> composition, representative E2E, documentation, regression, and CI acceptance

------------------------------------------------------------------------

## 1. Objective

Milestone 5 extends OpenProjectLab from a stable Generator / Plugin engineering
platform into a structured Open Courseware generation platform without replacing
the contracts established by Milestone 3 and Milestone 4.

The milestone is accepted only when Course / Week domain foundations, concrete
courseware generators, presentation/publishing projections, deterministic
composition, representative E2E behavior, documentation, regression, and CI
evidence form one traceable engineering chain.

------------------------------------------------------------------------

## 2. Preserved Foundations

Milestone 5 preserves the Milestone 3 canonical Generator lifecycle:

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

It also preserves the Milestone 4 Plugin boundary:

```text
third-party generator
    ↓
generator.sdk
    ↓
openprojectlab.generators
    ↓
validation / registry / loader
```

Milestone 5 does not introduce a second request/result model, registry, plugin
runtime, manifest format, or filesystem implementation.

------------------------------------------------------------------------

## 3. Accepted Architecture Decisions

| ADR | Decision | Status |
| --- | --- | --- |
| 0014 | Open Courseware Domain Contract | Accepted |
| 0015 | Lab Generator Contract | Accepted |
| 0016 | Quiz Generator Contract | Accepted |
| 0017 | Assignment Generator Contract | Accepted |
| 0018 | Slides Generator Contract | Accepted |
| 0019 | Website Generator Contract | Accepted |
| 0020 | Courseware Composition Contract | Accepted |

ADR 0013 remains a separate Proposed future Plugin Distribution decision and is
not a Milestone 5 acceptance dependency.

------------------------------------------------------------------------

## 4. Accepted Capabilities

### 4.1 Course / Week Domain Foundation

Production:

```text
generator/courseware/models.py
```

Accepted behavior includes immutable Course / Week models, stable identity,
positive Week validation, bool rejection, duplicate Week rejection, and
deterministic Week ordering.

### 4.2 Lab Generator

Canonical identity:

```text
lab
```

Canonical artifact:

```text
week-{week:02d}/lab/{lab_id}/README.md
```

Lab preserves the canonical GenerationPlan / GenerationResult lifecycle,
dry-run, overwrite, filesystem, manifest, CLI, template, and built-in registry
boundaries.

### 4.3 Quiz Generator

Canonical identity:

```text
quiz
```

Quiz accepts structured ordered questions with explicit unique IDs, ordered
choices, and correct-answer membership validation. Learner-facing output does
not expose answer-key data.

Canonical artifact:

```text
week-{week:02d}/quiz/{quiz_id}/README.md
```

### 4.4 Assignment Generator

Canonical identity:

```text
assignment
```

Assignment supports ordered objectives, deliverables, resources, authored
instructions, and submission guidance.

Canonical artifact:

```text
week-{week:02d}/assignment/{assignment_id}/README.md
```

### 4.5 Slides Projection

Canonical identity:

```text
slides
```

Canonical source artifact:

```text
<target>/slides.md
```

Slides is an authored presentation-source projection. PPTX, PDF, and HTML
rendering are not claimed by this milestone.

### 4.6 Website Projection

Canonical identity:

```text
website
```

Website produces deterministic ordered static HTML pages under:

```text
<target>/site/
```

A canonical `index.html` is required. Hosting, deployment, CMS, analytics,
authentication, and remote publishing are outside Milestone 5.

### 4.7 Courseware Composition

Production:

```text
generator/courseware/composition.py
```

Accepted composition flow:

```text
Ordered GenerateRequest(s)
        ↓
CoursewareComposer
        ↓
GeneratorRegistry preflight
        ↓
BaseGenerator.run(request)
        ↓
Ordered GenerationResult collection
```

Accepted semantics:

- deterministic sequential request/execution ordering
- preflight generator resolution before execution
- canonical `BaseGenerator.run(request)` lifecycle
- ordered `GenerationResult` aggregation
- fail-fast behavior
- no cross-generator rollback
- dry-run / overwrite propagation through existing request options
- existing filesystem and manifest ownership
- caller-input immutability
- no public SDK expansion

------------------------------------------------------------------------

## 5. Representative E2E Acceptance

Representative E2E:

```text
tests/integration/test_courseware_composition_e2e.py
```

The acceptance fixture composes a representative courseware repository through
the production `CoursewareComposer`, existing `GeneratorRegistry`, and
production Course / Week / Lab / Quiz / Assignment / Slides / Website
generators.

The E2E boundary verifies:

- deterministic generator execution order
- complete representative artifact membership
- Course / Week / Lab / Quiz / Assignment / Slides / Website output
- manifest generator provenance
- reproducible user-facing artifact content for equivalent input
- composition-wide dry-run leaves no persistent project repository

The E2E test intentionally does not duplicate generator-specific validation,
overwrite, filesystem safety, or plugin-runtime tests already owned by lower
contract/integration layers.

------------------------------------------------------------------------

## 6. Engineering Evidence

Milestone 5 was developed through small Design → Test → Implementation →
Integration → Acceptance slices.

Representative PR sequence:

```text
#40–#43  Open Courseware architecture/domain foundation
#44–#48  Lab
#49–#53  Quiz
#54–#58  Assignment
#59–#63  Slides
#64–#68  Website
#69       Composition design
#70       Composition contract tests
#71       Composition implementation
#72       Composition representative integration
#73       Composition documentation acceptance
#74       Milestone 5 representative E2E
```

The exact repository history remains the authoritative record for individual PR
titles and merge commits.

------------------------------------------------------------------------

## 7. Test Strategy and Coverage

Milestone 5 acceptance is layered:

```text
Domain contract tests
        ↓
Generator contract tests
        ↓
Template tests
        ↓
Generator / CLI integration tests
        ↓
Composition contract tests
        ↓
Composition integration tests
        ↓
Representative E2E
        ↓
Full regression / coverage / CI
```

Core tests remain isolated from network, hosted LMS, cloud storage, AI APIs,
and deployment providers.

### Final acceptance baseline

Run on the acceptance branch:

```powershell
python -m pytest
```

Formal Milestone 5 acceptance baseline:

```text
867 passed
Total coverage: 88.76%
Required coverage: 67.0%
```

This baseline was produced on the Milestone 5 acceptance branch with
`python -m pytest`. Earlier Website or Composition integration baselines are
historical checkpoints and are not used as the formal milestone acceptance
baseline.

------------------------------------------------------------------------

## 8. Documentation Evidence

Milestone 5 acceptance requires alignment of:

```text
docs/architecture/open-courseware-platform.md
docs/adr/README.md
docs/adr/0014-open-courseware-domain-contract.md
docs/adr/0015-lab-generator-contract.md
docs/adr/0016-quiz-generator-contract.md
docs/adr/0017-assignment-generator-contract.md
docs/adr/0018-slides-generator-contract.md
docs/adr/0019-website-generator-contract.md
docs/adr/0020-courseware-composition-contract.md
docs/roadmap.md
docs/HISTORY.md
CHANGELOG.md
docs/milestones/milestone-5-acceptance.md
```

Accepted ADR history is not rewritten during milestone closure; later
architecture changes require a new superseding ADR where appropriate.

------------------------------------------------------------------------

## 9. Public SDK Boundary

Milestone 5 does not require courseware-specific additions to `generator.sdk`.

This preserves the Milestone 4 extension contract and prevents courseware
implementation details from becoming accidental third-party public API.

Any future courseware-specific SDK expansion requires:

1. an ADR,
2. public export tests,
3. third-party-style contract tests,
4. Plugin authoring documentation,
5. backward-compatibility review.

------------------------------------------------------------------------

## 10. Explicit Non-Goals / Deferred Capabilities

Milestone 5 does not claim:

- a concrete public `LearningMaterial` hierarchy
- a public `CompositionResult` hierarchy
- composition CLI commands
- parallel composition
- cross-generator transactions or rollback
- capability metadata as a public contract
- PPTX / PDF / HTML slide rendering
- Website hosting or deployment
- CMS, analytics, or authentication
- LMS / student / grading / submission runtime
- AI content generation
- a second Plugin registry/runtime
- a second manifest format
- courseware-specific public SDK symbols

These remain future capabilities and require their own design/contract work.

------------------------------------------------------------------------

## 11. Acceptance Automation

Before the acceptance PR is merged:

```powershell
git diff --check
pre-commit run --all-files
python -m pytest
```

CI must reproduce the repository quality gates.

For Python changes there would additionally be explicit Ruff checks, but the
formal Milestone 5 acceptance PR is documentation-only.

------------------------------------------------------------------------

## 12. Code Review Checklist

### Architecture

- [x] Milestone 3 canonical Generator lifecycle is preserved.
- [x] Milestone 4 Plugin runtime / SDK boundary is preserved.
- [x] Domain, Generator, Template, Artifact, Filesystem, and Composition ownership are separated.
- [x] Composition uses the existing registry and canonical `run(request)` lifecycle.
- [x] No second orchestration, manifest, filesystem, or plugin infrastructure is introduced.
- [x] Deferred capabilities are not described as implemented.

### Contracts and Implementation

- [x] ADR 0014 through ADR 0020 are Accepted.
- [x] Course / Week domain production models exist.
- [x] Lab / Quiz / Assignment generators are implemented and integrated.
- [x] Slides / Website projections are implemented and integrated.
- [x] Courseware composition is implemented and integrated.
- [x] No courseware-specific public SDK expansion is required.

### Tests

- [x] Domain contracts are covered.
- [x] Generator contracts are covered.
- [x] Template behavior is covered.
- [x] Generator / CLI integrations are covered.
- [x] Composition contract and integration behavior are covered.
- [x] Representative E2E is covered.
- [x] Representative E2E validates artifact membership and manifest provenance.
- [x] Representative E2E validates reproducibility and dry-run non-persistence.
- [x] Final full-regression suite passes on the acceptance branch.
- [x] Final coverage remains above the required 67.0% gate.
- [ ] CI passes for the acceptance PR.

### Documentation

- [x] Architecture reflects implemented Milestone 5 boundaries.
- [x] ADR index reflects accepted Milestone 5 decisions.
- [x] Roadmap reflects Representative E2E completion and formal acceptance.
- [x] HISTORY records the Milestone 5 engineering evolution.
- [x] CHANGELOG records Milestone 5 capabilities and verification evidence.
- [x] Formal Milestone 5 acceptance document exists.

### Automation

- [x] `git diff --check` passes.
- [ ] `pre-commit run --all-files` passes.
- [x] `python -m pytest` passes.
- [x] Final regression / coverage numbers are recorded in this document.
- [ ] GitHub Actions CI passes.

------------------------------------------------------------------------

## 13. Exit Criteria

Milestone 5 is formally Accepted when all of the following are true:

1. ADR 0014 through ADR 0020 are Accepted.
2. Course / Week domain contracts are implemented and tested.
3. Lab, Quiz, Assignment, Slides, and Website generators/projections are implemented and integrated.
4. Courseware Composition is implemented, integrated, and documentation-accepted.
5. Representative E2E passes through the production composition/generator pipeline.
6. Architecture, ADR index, Roadmap, HISTORY, CHANGELOG, and this acceptance document are aligned.
7. Full regression suite passes.
8. Coverage satisfies the 67.0% repository gate.
9. `pre-commit run --all-files` passes.
10. Acceptance PR CI passes.
11. No deferred capability is incorrectly claimed as implemented.

------------------------------------------------------------------------

## 14. Acceptance Result

Current state:

```text
Architecture / ADRs                 READY
Domain contracts                    READY
Material generators                 READY
Slides / Website projections        READY
Courseware Composition              READY
Representative E2E                  READY
Documentation alignment             READY
Final regression / coverage         PASSED — 867 passed / 88.76%
pre-commit                          PENDING
Acceptance PR CI                    PENDING
```

The final regression and coverage gates have passed. Before the acceptance PR
is merged, the remaining closure gates are:

```text
pre-commit
Acceptance PR CI
```

`CHANGELOG.md` must record the same 867 passed / 88.76% formal acceptance
baseline before merge.

------------------------------------------------------------------------

## 15. Conclusion

Milestone 5 establishes OpenProjectLab as a composable Open Courseware
generation platform built on the existing Generator and Plugin contracts.

The milestone demonstrates that Course / Week domain intent, concrete learning
materials, presentation/publishing projections, deterministic composition,
manifest provenance, and representative end-to-end generation can coexist
without introducing a parallel framework or expanding the public SDK without
evidence.

The next milestone may build AI-assisted capabilities on top of this structured
boundary, but AI remains a consumer/producer of validated courseware intent—not
a replacement for the canonical Generator lifecycle or filesystem safety
contracts.

> **Build courseware through explicit contracts, deterministic composition,
> and reproducible engineering evidence.**
