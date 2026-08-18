# OpenProjectLab v1.0 Support Matrix

> **Status:** Design / Contract Definition
> **Milestone:** 8 --- v1.0 Stabilization & Release Readiness
> **Step:** 8.7 --- Support Matrix / Known Limitations
> **Depends on:** Step 8.2 Public Contract Audit & Freeze; Step 8.3 Reliability / Regression Hardening; Step 8.4 Packaging / Installation / Distribution; Step 8.5 Documentation & Bilingual User Manuals; Step 8.6 Compatibility & Deprecation Policy

---

## 1. Purpose

This document defines the v1.0 support matrix for OpenProjectLab (OPL).

The support matrix is intentionally evidence-based. A platform, Python
version, installation path, command surface, or workflow is marked
**Supported** only when OPL has explicit automated test, CI, installed-user,
or release-verification evidence for that claim.

The governing rule is:

```text
Observed locally
        ≠
Supported

Implemented
        ≠
Supported

Documented
        ≠
Supported

Supported
        =
Explicit evidence + maintained commitment
```

Step 8.7 does not widen the Step 8.2 Stable public-contract surface. It
documents the environments and workflows in which those frozen contracts
have actually been verified.

---

## 2. Status Vocabulary

Every support claim must use one of these states:

### Supported

The capability or environment has direct verification evidence and is
part of the v1.0 maintained support commitment.

A Supported claim requires at least one of:

- GitHub Actions / CI coverage;
- deterministic automated tests;
- built-artifact / clean-install verification;
- explicit release-readiness verification;
- another reproducible maintainer-owned verification path.

### Experimental

The capability exists and may be useful, but does not receive the same
support commitment as Supported behavior.

Experimental claims must:

- be labeled explicitly;
- avoid implying Stable compatibility support;
- identify missing evidence or limitations;
- not become release blockers unless explicitly promoted.

### Known Limitation

The capability is within the v1.0 product boundary but has an accepted,
documented limitation.

Known limitations belong in
`docs/releases/v1.0-known-limitations.md`.

### Deferred

The capability is intentionally outside the v1.0 release scope.

Deferred items are not defects in v1.0 unless a later release-readiness
decision explicitly promotes them.

---

## 3. Evidence Rules

A support claim must identify its evidence source.

Preferred evidence hierarchy:

```text
GitHub Actions / CI
        ↓
Automated deterministic tests
        ↓
Built-artifact / clean-install verification
        ↓
Explicit maintainer release verification
        ↓
Documented manual verification
```

A one-off local success on an untracked environment is not sufficient for
a Supported claim.

If evidence is incomplete, classify the item as Experimental or leave it
unclaimed rather than guessing.

---

## 4. Runtime Support

### 4.1 Python

The v1.0 release must list only Python versions that are actually
exercised by CI or release verification.

Current verified repository evidence establishes that the project test
suite and release-readiness work execute successfully on the maintained
development/runtime environment used for Milestone 8. However, this
document must not infer a wider Python-version range merely from package
metadata or syntax compatibility.

Therefore:

```text
Python version support
    → Supported only when explicitly represented in CI or release verification
```

Until Step 8.7 automation verifies the exact version set, the canonical
version list must be populated from repository evidence rather than
assumption.

### 4.2 Operating Systems

The same rule applies to operating systems:

```text
OS support
    → Supported only when directly exercised by CI / release verification
```

A platform must not be listed as Supported solely because OPL is written
in Python.

---

## 5. Installation and Packaging Support

### 5.1 Built Wheel Installation

**Status:** Supported

Evidence established in Step 8.4:

- wheel build passes;
- sdist build passes;
- Twine validation passes;
- required runtime resources are present in the wheel;
- clean-wheel installation succeeds;
- installed `generator` import succeeds;
- installed `opl list` succeeds;
- installed representative generation succeeds;
- runtime templates resolve from package-owned resources;
- repository-level legacy template dependency is removed.

Canonical package-owned runtime resource boundary:

```text
generator/resources/templates/
```

### 5.2 Source Checkout

**Status:** Supported for development and test workflows

Source checkout remains the normal repository-development environment.

This does not replace built-wheel verification for installed-user claims.

### 5.3 Editable Installation

**Status:** Not a release-readiness dependency

OPL v1.0 release claims must not depend on editable-only import behavior.
Installed-user verification is based on real built artifacts.

### 5.4 Repository `PYTHONPATH` Dependence

**Status:** Not supported as an installed-user requirement

Installed workflows must not require repository `PYTHONPATH`.

---

## 6. CLI Support

### Supported

The Step 8.2 frozen CLI surface and existing automated integration coverage
define the v1.0 supported command behavior.

Supported CLI behavior includes the reviewed built-in command surface,
including where frozen by Step 8.2 and covered by tests:

```text
list
bootstrap
course
week
lab
quiz
assignment
slides
website
```

The exact Stable option/argument semantics remain governed by the Step 8.2
public-contract freeze and corresponding tests.

### Not implied

The following are not automatically supported merely because they would be
useful:

- Marketplace CLI;
- AI-specific CLI expansion;
- remote service management commands;
- release-management CLI.

Those remain Deferred unless explicitly promoted.

---

## 7. Generator Support

### Supported Built-in Generators

The following built-in Generator identities have implementation,
integration, and regression evidence:

```text
bootstrap
course
week
lab
quiz
assignment
slides
website
```

Support includes the Stable behavior frozen by Step 8.2, including
canonical identities, validated inputs, generation planning, deterministic
artifact behavior, dry-run/overwrite semantics where applicable, and
manifest integration.

### Generator Extension

Third-party Generator extensions should use the Stable Plugin SDK boundary
rather than Internal implementation paths.

---

## 8. Plugin Support

### Supported

The supported plugin integration boundary is the Stable Plugin SDK and
canonical Entry Point runtime established in Milestone 4 and frozen by
Step 8.2.

Canonical Entry Point group:

```text
openprojectlab.generators
```

Supported behavior includes:

- `generator.sdk` public façade;
- Entry Point discovery/loading;
- validation;
- registry preflight;
- transactional registration behavior;
- installed third-party example verification.

### Deferred

The following are not part of the v1.0 supported plugin-distribution
promise unless separately promoted:

- remote plugin marketplace distribution;
- general dependency solving;
- publisher identity/signing;
- sandbox/trust enforcement;
- monetization.

---

## 9. Courseware Support

### Supported

The following Courseware capabilities have deterministic production and
test evidence:

- Course / Week domain model;
- Lab generation;
- Quiz generation;
- Assignment generation;
- Slides Markdown-source generation;
- Website static HTML generation;
- Courseware Composition;
- representative end-to-end generation;
- dry-run and overwrite behavior where defined;
- deterministic artifact membership/order where frozen.

### Not Supported as v1.0 Commitments

The following are not part of the current supported v1.0 Courseware
contract unless explicitly promoted:

- grading/scoring runtime;
- submission backend;
- QuestionBank/randomization;
- PPTX/PDF rendering;
- hosting/deployment;
- CMS behavior;
- generalized cross-Generator rollback.

---

## 10. AI Support

### Supported Core Boundary

Provider-independent AI contracts with deterministic tests are supported
to the extent classified Stable by Step 8.2.

This includes the tested provider-independent request/response,
validation, mapping, application-service, and representative deterministic
AI-to-Courseware paths.

### Experimental / Optional Operational Boundary

Real-provider operation is not required for normal core CI.

The concrete OpenAI adapter has deterministic no-network tests and live
testing is explicitly separated.

Live provider verification remains opt-in operational verification and may
depend on external credentials, provider availability, network access, and
third-party service behavior.

### Deferred

The following remain outside the v1.0 supported core commitment unless
promoted:

- AI Refactoring Assistant;
- AI CLI;
- provider marketplace;
- evaluation/provenance/usage accounting;
- caching;
- streaming;
- tool calling.

---

## 11. Marketplace Support

### Supported Core Contracts

The deterministic in-memory Marketplace contract surface frozen by Step
8.2 is supported where covered by implementation and tests:

- artifact identity/version/type;
- compatibility metadata;
- distribution/integrity metadata;
- deterministic repository/index lookup;
- acquisition;
- SHA-256 integrity verification;
- deterministic in-memory installation;
- Template Package contracts;
- representative Marketplace E2E.

### Deferred

The following are outside the v1.0 supported scope:

- remote Marketplace service;
- Community Repository hosting;
- Marketplace CLI;
- real package-manager integration;
- automatic Plugin/Generator activation;
- artifact signing / publisher identity;
- sandbox/trust policy;
- general dependency resolver;
- lock-file/cache policy;
- ratings/reviews;
- monetization/payment;
- AI Provider Marketplace.

---

## 12. Documentation Support

### Supported

v1.0 maintains two formal User Manuals:

```text
docs/user-guide/en/
docs/user-guide/zh-TW/
```

Each contains 13 paired chapters.

Automated documentation verification protects:

- structure;
- bilingual parity;
- functional parity;
- First 15 Minutes installed-user workflow.

User-facing migration guidance introduced by future compatibility changes
must preserve EN/zh-TW functional parity.

---

## 13. Filesystem and Configuration Support

Only the Step 8.2 verified Stable subset is supported.

The support matrix does not promote every implementation detail of
configuration loading, path handling, filesystem internals, backup,
rollback, or error text.

Stable failure/write boundaries and public exception categories remain
governed by the frozen v1 contract.

---

## 14. Network and External-Service Requirements

Normal core verification is intended to remain deterministic and
network-independent.

Supported core workflows must not require:

- external Marketplace service availability;
- paid AI account;
- live AI Provider access;
- remote package registry behavior beyond the explicit release/install
  process being tested;
- hidden network dependencies.

Where a workflow requires external services, classify it separately and do
not represent it as equivalent to deterministic core support.

---

## 15. Support Matrix Table

The final Step 8.7 implementation should maintain an evidence-backed table
using this schema:

| Area | Capability / Environment | Status | Evidence | Notes |
|---|---|---|---|---|
| Packaging | Built wheel install | Supported | Step 8.4 clean-install tests | Package-owned resources |
| CLI | Frozen v1 command surface | Supported | Step 8.2 contract tests + integration tests | Stable subset only |
| Generators | Built-in generators | Supported | Contract/integration/E2E tests | Stable behavior only |
| Plugins | `generator.sdk` + Entry Point loading | Supported | Milestone 4 + Step 8.2 tests | Third-party SDK boundary |
| Courseware | Domain + composition + built-ins | Supported | Milestone 5 + Step 8.2/8.3 tests | No grading backend |
| AI | Provider-independent core | Supported | Milestone 6 + Step 8.2/8.3 tests | Deterministic core |
| AI | Live provider invocation | Experimental | Opt-in live tests | External dependency |
| Marketplace | Deterministic local core | Supported | Milestone 7 + Step 8.2/8.3 tests | No remote service |
| Docs | EN + zh-TW manuals | Supported | Step 8.5 automation | 13 paired chapters |
| Release | Remote Marketplace | Deferred | No v1 implementation commitment | v1.1+ candidate |

Environment-specific rows for operating systems and Python versions must
be added only after the exact CI/release evidence is confirmed.

---

## 16. Automation Requirements

Step 8.7 should add focused support-matrix contract tests.

Recommended structure:

```text
tests/support/
    __init__.py
    test_support_matrix_contract.py
    test_known_limitations_contract.py
```

Automation should verify that:

- every status uses the canonical vocabulary;
- every Supported row has an evidence reference;
- Experimental rows are not described as Stable;
- Deferred rows are not represented as v1 blockers;
- support claims do not exceed known CI/release evidence;
- the support matrix and known-limitations document cross-reference each
  other;
- Step 8.7 does not redefine Step 8.2 contract classifications;
- environment rows are not added without explicit evidence.

A generalized environment-detection engine is not required for v1.0.

---

## 17. Acceptance Criteria

### Support Governance

- [ ] Canonical status vocabulary is defined.
- [ ] Supported claims require evidence.
- [ ] Experimental claims are clearly labeled.
- [ ] Deferred claims remain outside v1.0 scope.
- [ ] Known limitations are separately documented.
- [ ] Step 8.2 remains authoritative for Stable contract classification.

### Environment Claims

- [ ] Python support lists only actually verified versions.
- [ ] OS support lists only actually verified platforms.
- [ ] Installed-user support is based on real built artifacts.
- [ ] Unsupported environment assumptions are not promoted.

### Capability Claims

- [ ] CLI support matches frozen/tested behavior.
- [ ] Generator support matches implemented/tested built-ins.
- [ ] Plugin support matches Stable SDK/Entry Point evidence.
- [ ] Courseware support does not claim deferred grading/rendering/hosting.
- [ ] AI support separates deterministic core from live-provider operation.
- [ ] Marketplace support separates deterministic core from remote service.
- [ ] Documentation support reflects EN/zh-TW automated parity.

### Automation / Quality

- [ ] `tests/support/test_support_matrix_contract.py` exists.
- [ ] `tests/support/test_known_limitations_contract.py` exists.
- [ ] `git diff --check` passes.
- [ ] Ruff / Ruff Format pass.
- [ ] pre-commit passes.
- [ ] full pytest passes.
- [ ] coverage remains >= 67.0%.
- [ ] GitHub Actions / CI passes.

---

## 18. Code Review Checklist

### Evidence

- [ ] Every Supported claim has direct evidence.
- [ ] No claim is based only on developer expectation.
- [ ] Local-only success is not presented as general support.
- [ ] CI and release evidence are cited accurately.

### Classification

- [ ] Supported / Experimental / Known Limitation / Deferred are not mixed.
- [ ] Experimental behavior is not presented as Stable.
- [ ] Deferred behavior is not presented as a missing v1 feature.
- [ ] Step 8.2 classifications are not silently changed.

### Scope

- [ ] No new v1.0 feature is introduced merely to fill the matrix.
- [ ] Step 8.7 does not pre-empt Step 8.8 release automation.
- [ ] Step 8.7 does not broaden the Stable public surface.
- [ ] Unknown environment support remains unclaimed.

### Documentation

- [ ] Support matrix and known limitations agree.
- [ ] EN/zh-TW user-facing support statements remain compatible.
- [ ] CHANGELOG / HISTORY / roadmap are updated at acceptance.
- [ ] Known limitations include mitigation or workaround when available.

---

## 19. Delivery Slices

```text
8.7.1 Support-matrix governing design
      ↓
8.7.2 Known-limitations governing design
      ↓
8.7.3 Support-matrix contract tests
      ↓
8.7.4 Known-limitations contract tests
      ↓
8.7.5 Populate exact environment evidence
      ↓
8.7.6 Full regression + quality gates
      ↓
8.7.7 Formal Step 8.7 acceptance
      ↓
Step 8.8 Release Automation & Reproducibility
```

---

## 20. Current State

```text
Step 8.6 Compatibility & Deprecation Policy        Accepted
Step 8.7 Support Matrix / Known Limitations        In Progress
Support governance                                  Defined by this document
Exact Python-version matrix                         Pending evidence review
Exact operating-system matrix                       Pending evidence review
Known-limitations register                          Defined separately
Formal Step 8.7 acceptance                          Pending
```

---

# Final Principle

> Claim support only where OPL has evidence and is willing to maintain the
> commitment.

The v1.0 support matrix is a release contract, not a marketing list.
