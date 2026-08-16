# Milestone 7 — Marketplace Acceptance

> **Status:** Accepted
> **Milestone:** 7 — Marketplace
> **Date:** 2026-08-16
> **Primary ADR:** ADR 0023 — Marketplace Artifact Contract

## Purpose

本文件記錄 OpenProjectLab（OPL）Milestone 7 — Marketplace 的正式
acceptance boundary、implementation evidence、test evidence、documentation
alignment 與 automation gates。

Milestone 7 的核心原則：

```text
Marketplace distributes.
Contracts validate.
Existing OPL pipelines execute.
```

Marketplace 的責任是 artifact distribution、discovery、acquisition、
integrity verification 與 installation boundary；它不建立第二套 Generator
execution framework，也不取代既有 Plugin SDK、Entry Point、Generator
lifecycle、Courseware Domain 或 Filesystem contracts。

---

## Acceptance Scope

Milestone 7 acceptance 涵蓋：

```text
Marketplace Architecture / ADR
        ↓
Artifact Contract
        ↓
Immutable Artifact Models
        ↓
Repository / Index Contract
        ↓
Integrity Verification
        ↓
Artifact Acquisition
        ↓
Installation Contract
        ↓
Template Package Contract
        ↓
Representative Marketplace E2E
```

不屬於本 Milestone acceptance requirement：

- public remote Marketplace service；
- Marketplace web UI；
- ratings / reviews；
- recommendation engine；
- monetization / payment；
- publisher signing / identity verification；
- sandboxed third-party code execution；
- general-purpose dependency resolver；
- Marketplace CLI；
- AI Provider Marketplace；
- lock-file / cache policy；
- public `generator.sdk` Marketplace expansion。

---

## Architecture Acceptance

### Step 7.1 — Marketplace Architecture and Artifact Contract

Architecture：

```text
docs/architecture/marketplace.md
```

Primary ADR：

```text
docs/adr/0023-marketplace-artifact-contract.md
```

ADR 0023 establishes the common Marketplace artifact boundary:

```text
MarketplaceArtifact
├── schema_version
├── identity
├── version
├── artifact_type
├── description
├── compatibility
├── distribution
└── integrity
```

The accepted architecture preserves:

- stable artifact identity independent of distribution location；
- explicit artifact version；
- immutable artifact coordinate；
- explicit Plugin / Generator / Template artifact types；
- independent metadata schema version；
- deterministic OPL compatibility validation；
- distribution metadata separated from identity；
- SHA-256 integrity metadata；
- discovery separated from installation；
- installation separated from activation；
- existing Plugin SDK and Entry Point boundaries；
- existing canonical Generator lifecycle；
- existing Courseware / Filesystem boundaries；
- deterministic no-network core tests。

---

## Implementation Acceptance

### Step 7.2 — Artifact Contract Tests

Marketplace artifact contract tests establish the expected behavior before
production implementation, including valid and invalid metadata, identity,
version, artifact type, coordinate, compatibility, integrity and immutability.

### Step 7.3 — Minimum Artifact Models

Production Marketplace models implement the common artifact contract under:

```text
generator/marketplace/
```

The implementation provides immutable Marketplace metadata without introducing
a Marketplace-specific execution lifecycle.

### Step 7.4 — Repository / Index Contract

The Marketplace repository contract provides deterministic artifact lookup,
exact-version resolution, version ordering, explicit not-found behavior and
duplicate-coordinate protection.

Repository behavior remains independent of public network availability.

### Step 7.5 — Integrity and Acquisition

Marketplace integrity and acquisition boundaries establish:

```text
Artifact Metadata
    ↓
Acquire Payload
    ↓
Verify SHA-256
```

Integrity mismatch fails explicitly before installation or activation.

Acquisition remains independently testable with deterministic in-memory data.

### Step 7.6 — Installation Integration

The installation contract establishes:

```text
Validated Artifact + Acquired Payload
        ↓
Installation
        ↓
Installation Result
```

Installation remains separate from activation.

The initial contract does not perform Plugin registration, Generator execution,
Courseware generation, remote package management, or generated-project
filesystem mutation.

### Step 7.7 — Template Packages

Template Packages reuse the common Marketplace artifact identity/version
contract and add immutable template-specific manifest metadata.

The contract establishes:

- safe relative paths；
- path traversal rejection；
- duplicate name/path rejection；
- deterministic ordering；
- template/resource separation；
- immutable package metadata。

Template Package metadata does not itself render Jinja templates or execute
Generators.

### Step 7.8 — Representative Marketplace E2E

Representative integration composes the production Marketplace boundaries:

```text
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

The representative E2E verifies:

- successful repository → acquisition → integrity → installation flow；
- deterministic behavior for equivalent inputs；
- exact artifact coordinate semantics；
- repository not-found failure before side effects；
- missing payload failure before installation；
- integrity mismatch failure before installation；
- failed flows leave no partial installation state；
- Template Package contract remains preserved；
- no public network dependency；
- no generated-project filesystem persistence；
- no Plugin activation；
- no Generator execution。

---

## ADR 0023 Acceptance

ADR 0023 may transition from `Proposed` to `Accepted` when the final branch
contains the implementation and test evidence described above and all final
quality gates pass.

Before the acceptance commit, verify and update ADR 0023:

```text
Status: Proposed → Accepted
Implementation Status: actual implemented state
Acceptance Criteria: checked only where evidence exists
```

Capabilities intentionally deferred from Milestone 7 must remain described as
deferred / not implemented.

---

## Regression and Quality Gates

Final acceptance evidence must be recorded from the acceptance branch after all
Milestone 7 implementation and documentation changes are present.

```text
Full regression:        1315 passed, 1 deselected
Total coverage:         89.89%
Required coverage:      67.0% --- Passed
git diff --check:       Passed
Ruff:                   Passed
Ruff Format:            Passed
pre-commit:             Passed
GitHub Actions / CI:    Passed
Squash merge:           Completed
Post-merge consistency: Completed
```

The previous Milestone 6 baseline (`1119 passed, 1 deselected`, 90.23%
coverage) is historical evidence only and must not be reused as the Milestone 7
final acceptance baseline.

---

## Documentation Alignment

Milestone 7 formal acceptance requires synchronized updates to:

```text
docs/architecture/marketplace.md
docs/adr/0023-marketplace-artifact-contract.md
docs/adr/README.md
docs/roadmap.md
docs/HISTORY.md
CHANGELOG.md
docs/milestones/milestone-7-acceptance.md
```

README or other top-level documentation should be updated only where it
currently exposes ADR / milestone status that would otherwise become stale.

Documentation must not claim remote Marketplace, Marketplace CLI, signing,
trust, sandboxing, dependency resolution, or other deferred capabilities are
implemented.

---

## Acceptance Checklist

### Architecture

- [x] Marketplace architecture defined.
- [x] Common Marketplace Artifact Contract defined.
- [x] Marketplace does not introduce a second Generator lifecycle.
- [x] Existing Plugin SDK / Entry Point boundaries remain canonical.
- [x] Courseware Domain and Filesystem boundaries remain preserved.
- [x] Discovery, acquisition, integrity, installation and activation
      responsibilities remain separated.

### Implementation

- [x] Minimum Marketplace artifact models implemented.
- [x] Repository / index contract implemented.
- [x] Integrity verification implemented.
- [x] Deterministic acquisition boundary implemented.
- [x] Installation contract implemented.
- [x] Template Package contract implemented.
- [x] Representative Marketplace E2E implemented.

### Testing

- [x] Artifact contract tests implemented.
- [x] Repository contract tests implemented.
- [x] Integrity contract tests implemented.
- [x] Acquisition contract tests implemented.
- [x] Installation contract tests implemented.
- [x] Template Package contract tests implemented.
- [x] Representative Marketplace E2E implemented.
- [x] Core Marketplace tests require no public network.
- [x] Final full regression passed.
- [x] Final coverage recorded and above 67.0%.

### Documentation

- [x] ADR 0023 updated to final Accepted state.
- [x] Marketplace architecture synchronized with implemented state.
- [x] ADR index synchronized.
- [x] Roadmap synchronized.
- [x] HISTORY synchronized.
- [x] CHANGELOG synchronized.
- [x] Milestone 7 acceptance record created.
- [x] Deferred capabilities remain accurately identified.

### Automation

- [x] `git diff --check` passed.
- [x] Ruff passed.
- [x] Ruff Format passed.
- [x] `pre-commit run --all-files` passed.
- [x] `python -m pytest` passed.
- [x] Coverage policy passed.
- [x] GitHub Actions / CI passed.
- [x] Acceptance PR squash merged.
- [x] Post-merge consistency verification completed.

---

## Code Review Checklist

- [ ] No Marketplace-specific Generator lifecycle introduced.
- [ ] No parallel Plugin loading / registration architecture introduced.
- [ ] Artifact identity is independent of display metadata and distribution
      location.
- [ ] Artifact version and metadata schema version remain distinct.
- [ ] Duplicate artifact coordinates cannot silently overwrite.
- [ ] Compatibility validation remains deterministic and network-independent.
- [ ] SHA-256 integrity mismatch fails before installation/activation.
- [ ] Integrity is not documented as authenticity or trust.
- [ ] Discovery does not execute third-party code.
- [ ] Installation remains separate from activation.
- [ ] Template paths reject absolute paths and traversal.
- [ ] Template Package does not become a second rendering runtime.
- [ ] Representative E2E composes production Marketplace contracts rather than
      duplicating them.
- [ ] Failure paths leave no partial installation state.
- [ ] Marketplace does not control generated Courseware filesystem output.
- [ ] No accidental `generator.sdk` expansion.
- [ ] Deferred capabilities are not overclaimed.
- [ ] Architecture, ADR, roadmap, HISTORY and CHANGELOG agree.
- [x] Final regression / coverage / pre-commit / CI evidence is recorded.

---

## Final Acceptance Decision

**Current status: Accepted and post-merge verified.**

Milestone 7 has completed the full acceptance sequence:

```text
Documentation Alignment
        ↓
Final Full Regression
        ↓
Coverage Verification
        ↓
pre-commit / Quality Gates
        ↓
Acceptance PR / CI
        ↓
Squash Merge
        ↓
Post-merge Consistency Verification
```

The final local regression baseline is `1315 passed, 1 deselected` with
89.89% total coverage against the required 67.0% gate. ADR 0023 is `Accepted`.
GitHub Actions / CI passed, the acceptance PR was squash merged, local `main`
was synchronized with `origin/main`, and post-merge consistency verification
completed. Milestone 7 is therefore formally closed.

> **Marketplace distributes. Contracts validate. Existing OPL pipelines execute.**
