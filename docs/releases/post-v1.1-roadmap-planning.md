# OpenProjectLab Post-v1.1 Roadmap Planning

> **Status:** Accepted --- Terminally Closed
> **Predecessor:** OpenProjectLab v1.1 --- Terminally Accepted
> **Predecessor Merge:** 9997e9d85ed3672451c6c538d464d07a93d3d9cb
> **Next Version Decision:** Accepted
> **Implementation:** Not Started

------------------------------------------------------------------------

## 1. Purpose

This document governs the transition from the terminally accepted v1.1 release
into the next OpenProjectLab development cycle.

The purpose of this planning slice is to decide the next version boundary
before implementation begins.

The planning process follows:

``` text
v1.1 --- Terminally Accepted
        ↓
Post-v1.1 Roadmap Planning --- In Progress
        ↓
candidate workstreams evaluated
        ↓
next-version boundary selected
        ↓
planning acceptance
        ↓
implementation may begin
```

No post-v1.1 product implementation is authorized by this document.

## 2. Design Principles

The next development cycle continues to follow:

- Design First;
- Documentation First;
- Automation First;
- fail-closed public-contract evolution;
- backward-compatible 1.x evolution unless a breaking boundary is explicitly
  approved;
- artifact-backed release verification;
- executable acceptance evidence;
- historical acceptance records remain immutable.

## 3. Current Accepted Baseline

The planning baseline begins from the following accepted capabilities:

- Stable core generator lifecycle and SDK contracts;
- Plugin discovery, validation, loading, and entry-point contracts;
- Open Courseware composition and generator workflows;
- AI integration core contracts;
- Marketplace artifact, repository, integrity, acquisition, installation, and
  CLI workflows;
- v1.1 CLI public-contract evolution;
- Marketplace CLI versions / inspect / verify / install;
- AI CLI Stable local-response workflows;
- Experimental AI provider opt-in boundary;
- English / zh-TW documentation parity;
- wheel / sdist artifact-backed verification;
- clean-installed CLI verification;
- First 15 Minutes installed-wheel verification;
- terminal v1.1 formal acceptance.

## 4. Next-version Decision Framework

The next version must be selected from one of these categories:

### 4.1 Maintenance continuation

Use a v1.1.x maintenance release when work is limited to:

- defect correction;
- documentation correction;
- reliability hardening;
- packaging or CI corrections;
- non-behavioral internal cleanup;
- compatibility fixes that do not expand Stable product scope.

### 4.2 Backward-compatible feature release

Use v1.2 when the next cycle adds meaningful Stable capabilities while
preserving existing v1.x Stable contracts.

The default planning hypothesis is that the next feature cycle is likely to be
v1.2, but this is not accepted until the planning baseline passes review.

### 4.3 Breaking release

Use v2.0 only when an intentional Stable-contract break is required and a
formal compatibility / migration design proves that a backward-compatible
v1.x evolution is insufficient.

v2.0 must not be selected merely because a feature is large.

## 5. Candidate Workstreams

The post-v1.1 planning process evaluates the following workstreams.

### 5.1 Bootstrap Framework maturity

Candidate goals:

- stronger project bootstrap orchestration;
- deterministic multi-step bootstrap plans;
- explicit dry-run / apply boundaries;
- generated-project validation;
- resumable or inspectable bootstrap state where justified;
- stronger composition between generators without weakening existing
  lifecycle contracts.

### 5.2 AI-assisted project and course generation

Candidate goals:

- higher-level AI-assisted generation workflows built on existing Stable AI
  request / response contracts;
- deterministic local-response workflows remain first-class;
- live provider use remains explicit and opt-in unless separately promoted;
- generated changes remain inspectable before mutation;
- no implicit credential lookup or network fallback in Stable local workflows.

### 5.3 Marketplace production workflow

Candidate goals:

- richer local package discovery / inspection workflows;
- stronger installation planning and provenance visibility;
- improved no-partial-state guarantees;
- explicit trust and policy boundaries before any remote service is added;
- no implicit activation.

### 5.4 Developer and release automation

Candidate goals:

- reduce manual release / acceptance bookkeeping;
- make candidate-build identity and verification more reproducible;
- automate governance consistency checks;
- make branch / PR / CI / post-merge acceptance evidence easier to reproduce;
- preserve human merge approval boundaries.

## 6. Explicit Non-goals

The planning baseline does not approve:

- a remote Marketplace service;
- ratings, reviews, monetization, or commercial marketplace behavior;
- automatic plugin or generator activation;
- generalized dependency resolution;
- artifact signing / trust infrastructure without a dedicated architecture
  proposal;
- silent network access;
- implicit AI provider selection;
- automatic credential discovery in Stable local workflows;
- arbitrary repository mutation by AI;
- generalized streaming or tool-calling guarantees;
- generalized transaction rollback across all generators;
- v2.0 without an explicit breaking-change justification;
- implementation before planning acceptance.

## 7. Required Architecture Decisions Before Implementation

Any workstream selected for the next accepted release must define, before
implementation:

- public contract boundary;
- compatibility impact;
- failure and rollback behavior;
- state / mutation model;
- deterministic / offline expectations;
- CLI surface if applicable;
- configuration boundary if applicable;
- security / trust boundary if applicable;
- documentation impact;
- test strategy;
- acceptance gates;
- migration impact, if any.

## 8. Acceptance Gates for This Planning Slice

The Post-v1.1 Roadmap Planning baseline remains unaccepted until:

``` text
Governing design --- Defined
Fail-closed planning tests --- Added
Next-version decision --- Accepted
In-scope workstreams --- Accepted for v1.2 planning
Explicit non-goals --- Defined
Architecture decision requirements --- Defined
Roadmap alignment --- Completed
HISTORY alignment --- Completed
CHANGELOG alignment --- Completed
Focused planning tests --- Passed
Full regression --- 2322 passed, 56 skipped, 1 deselected
Total coverage --- 91.17%
Required coverage --- 67.0% --- Passed
git diff --check --- Passed
pre-commit --- Passed
Planning PR #220 required CI --- Passed
Planning PR #220 squash merge --- Completed
main synchronization --- Completed
Post-merge consistency verification --- Passed
Terminal planning acceptance --- Completed
Next Version Decision --- Accepted
Implementation --- Not Started
```

## 9. Code Review Checklist

### Historical integrity

- [ ] v1.1 remains Terminally Accepted.
- [ ] PR #219 merge identity remains unchanged.
- [ ] historical v1.0 / v1.1 acceptance records are not rewritten.

### Version selection

- [ ] maintenance vs v1.2 vs v2.0 criteria are explicit.
- [ ] v1.2 is not preaccepted.
- [ ] v2.0 is not selected without a breaking-contract justification.

### Scope

- [ ] candidate workstreams are explicit.
- [ ] selected workstreams are still planning-only.
- [ ] non-goals prevent scope creep.
- [ ] implementation remains Not Started.

### Architecture / automation

- [ ] each selected workstream must define architecture before implementation.
- [ ] acceptance evidence must be executable.
- [ ] Documentation First remains mandatory.
- [ ] Automation First remains mandatory.
- [ ] merge approval remains a human gate.

## 10. Current State

``` text
v1.1 --- Terminally Accepted
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
