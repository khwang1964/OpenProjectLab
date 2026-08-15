# ADR 0022 --- AI Provider Adapter Contract

> **Status:** Accepted **Date:** 2026-08-15 **Milestone:** 6 --- AI
> Integration **Step:** 6.10 --- Real Provider Adapter **Decision
> Scope:** Provider adapter boundary, SDK isolation, credentials,
> timeout, error conversion, deterministic tests, and live-provider test
> separation

## Context

ADR 0021 established the provider-independent AI Integration Contract.
OPL has since implemented `AIRequest`, `AIResponse`, `AIProvider`,
`FakeAIProvider`, structured validation, AI-to-Courseware mapping,
Course Generation, Review, Documentation, Template Completion, and
Course Builder.

Step 6.10 introduces the first boundary that may depend on a real
external provider. A real provider adds network access, credentials,
vendor SDK types, vendor exceptions, timeout behavior, rate limits,
service availability, cost, and non-determinism.

These infrastructure concerns must not leak into Courseware Domain,
Generator, Composition, GenerationPlan, Filesystem, or existing
provider-independent AI application contracts.

## Decision

OPL SHALL integrate real AI providers through Provider Adapters
implementing the existing `AIProvider` protocol.

``` text
OPL Application Service
        ↓
AIProvider
        ↓
Provider Adapter
        ↓
Provider SDK / HTTP Client
        ↓
External AI Provider
```

Return path:

``` text
Provider-specific Response
        ↓
Provider Adapter
        ↓
AIResponse
        ↓
Existing Validation / Mapping
        ↓
OPL Application Service
```

The Provider Adapter is an infrastructure boundary. Step 6.10 SHALL NOT
introduce a second provider abstraction merely because a real provider
is added.

## Responsibilities

A Provider Adapter SHALL:

-   accept an OPL `AIRequest`;
-   translate it into the provider-specific request;
-   invoke an injected provider client or transport;
-   use a finite configured timeout;
-   translate a successful response into the existing `AIResponse`;
-   normalize only provider-independent metadata needed by OPL;
-   convert recognized provider failures into OPL AI exceptions;
-   preserve exception chaining;
-   keep credentials and provider SDK types inside the infrastructure
    boundary.

A Provider Adapter SHALL NOT own:

-   Courseware Domain validation;
-   AI-to-Courseware mapping;
-   Courseware Composition;
-   Generator planning or execution;
-   `GenerationPlan` creation;
-   Filesystem writes;
-   CLI formatting;
-   Git operations;
-   prompt ownership;
-   credential persistence;
-   automatic retry orchestration in the initial contract.

## Provider SDK Isolation

Provider SDK imports SHALL remain inside provider adapter/infrastructure
code.

The following dependencies are prohibited:

``` text
Courseware Domain → Provider SDK
Generator          → Provider SDK
AI Application     → Provider-specific Response
AIRequest/Response → Provider SDK Type
```

Provider SDK upgrades should therefore be containable inside the adapter
boundary unless the provider-independent OPL contract intentionally
changes.

## Module Boundary

The initial provider infrastructure should use:

``` text
generator/ai/providers/
├── __init__.py
└── <provider>.py
```

A speculative `base.py` inheritance hierarchy SHALL NOT be added unless
multiple concrete adapters demonstrate a missing common abstraction not
already represented by `AIProvider`.

## Client Injection and Composition Root

Provider client construction and credential resolution belong outside
provider-independent application services.

``` text
Runtime Environment / Secret Mechanism
        ↓
Configuration / Composition Root
        ↓
Provider Client
        ↓
Provider Adapter
        ↓
AIProvider
        ↓
AI Application Service
```

The adapter SHOULD accept an already configured client or controlled
transport so deterministic tests can replace network behavior without
changing application code.

This ADR does not yet define the final public AI configuration schema.

## Credential Contract

Credentials SHALL NOT be stored in:

-   `AIRequest.task`, `instructions`, or `context`;
-   `AIResponse.content` or `metadata`;
-   Courseware Domain objects;
-   Template Context;
-   `GenerationPlan`;
-   generated courseware;
-   normal logs;
-   normal exception messages.

Credentials SHALL NOT be hard-coded or committed. Runtime environment or
an appropriate secret mechanism SHALL provide them outside Domain and
Generator layers.

Tests SHALL verify representative credential values do not leak through
OPL request/response models, exception messages, or relevant
representations.

## Timeout Contract

Every real provider invocation SHALL have a finite timeout.

Provider-specific timeout failures SHALL become:

``` text
AITimeoutError
```

with the original provider exception preserved as the chained cause.

Timeout configuration is an infrastructure/application concern and SHALL
NOT enter Courseware Domain models.

## Retry Contract

Automatic retry is explicitly out of scope for the initial Provider
Adapter contract.

One `AIProvider.generate()` call represents one logical provider
invocation. Any provider SDK retry default must be explicitly reviewed,
configured, and documented.

A future OPL retry policy requires separate design for eligible
failures, maximum attempts, backoff, cancellation, idempotency, logging,
rate limits, and cost.

## Provider-Independent Error Contract

Step 6.10 SHALL establish or complete only the minimum
provider-independent error types required by implemented adapters.

Intended hierarchy:

``` text
OpenProjectLabError
└── AIError
    ├── AIConfigurationError
    ├── AIProviderError
    ├── AIAuthenticationError
    ├── AIRateLimitError
    ├── AITimeoutError
    ├── AIResponseError
    ├── AIResponseValidationError
    └── AIUnavailableError
```

Existing compatible errors SHALL be preserved.

Recognized provider failures map conceptually as follows:

``` text
authentication failure → AIAuthenticationError
rate limit             → AIRateLimitError
timeout                → AITimeoutError
service unavailable    → AIUnavailableError
other known invocation → AIProviderError
```

Exception chaining SHALL be preserved with `raise ... from exc`.

## Unexpected Programming Errors

Adapters SHALL NOT indiscriminately hide programming errors such as
`TypeError`, `AttributeError`, `AssertionError`, or unexpected
`RuntimeError` behind `AIProviderError`.

A broad `except Exception` conversion is prohibited unless a narrowly
documented provider SDK contract requires it and tests prove programming
errors remain distinguishable.

## Response Normalization

Successful invocation SHALL return the existing OPL `AIResponse`.
Provider-specific response objects SHALL NOT escape the adapter.

Provider-independent metadata may include provider identifier, model
identifier, finish status, usage information, and request/correlation
identifier. Such metadata remains outside Courseware Domain state.

Transport success does not imply valid Courseware. Existing structural
validation and Domain mapping remain authoritative after adapter
normalization.

## Side Effects

A Provider Adapter may perform its external provider invocation. It
SHALL NOT directly write/delete production files, create
`GenerationPlan`, execute Generators, mutate Courseware Domain objects,
perform Git operations, or install plugins.

Provider failure must not create partial production filesystem state.

## Deterministic Adapter Tests

Normal Provider Adapter tests SHALL NOT call a real network service.

Use an injected fake/stub client or controlled transport to verify:

-   `AIRequest` → provider request translation;
-   provider response → `AIResponse`;
-   model and timeout configuration;
-   authentication/rate-limit/timeout/unavailable error conversion;
-   exception chaining;
-   credential non-leakage;
-   unexpected programming-error transparency;
-   no filesystem side effect.

Proposed structure:

``` text
tests/ai/providers/
├── __init__.py
├── test_provider_adapter_contract.py
├── test_provider_adapter_errors.py
└── test_provider_adapter_credentials.py
```

These tests belong in normal pytest, pre-commit, and CI.

## Live Provider Tests

Live-provider tests SHALL be separated from deterministic core tests.

They must be explicitly marked, opt-in, excluded from normal pre-commit
and credential-free core CI, bounded by timeout, cost-aware, and must
not assert exact natural-language output.

The intended marker is:

``` text
ai_live
```

Normal:

``` powershell
python -m pytest
```

must require no provider credential or live external AI availability.

An explicit live run may use:

``` powershell
python -m pytest -m ai_live
```

with separately configured credentials.

## Core CI Contract

Core CI SHALL remain valid with:

``` text
No provider API key
No paid AI account
No live provider availability
No provider network dependency
```

A separate live-provider workflow may be introduced later.

## First Provider Selection

This ADR intentionally does not select a vendor. The
provider-independent adapter contract is decided before vendor selection
drives implementation.

Selection should consider SDK maturity, structured-output support,
timeout/error semantics, client injection, credential handling, Python
compatibility, dependency footprint, and maintenance burden.

A vendor-specific constraint that materially changes architecture
requires documentation and, when appropriate, another ADR.

## Alternatives Considered

### Direct Provider SDK calls from AI Application Services

Rejected because every use case would become coupled to vendor
request/response/configuration/error types.

### Provider SDK calls from Generators

Rejected because external AI availability would contaminate the
canonical Generator lifecycle.

### Provider selection logic in every feature

Rejected because scattered vendor branching would make replacement and
testing inconsistent.

### New abstract base provider class immediately

Rejected because `AIProvider` already defines the application boundary;
another hierarchy would be speculative.

### Live Provider Tests in normal CI

Rejected because credentials, cost, network availability, rate limits,
and non-determinism would become core merge dependencies.

### Automatic retry in the first adapter

Rejected because retry has cost, idempotency, rate-limit, timeout, and
observability implications requiring an explicit policy.

## Consequences

Positive consequences:

-   preserves provider independence;
-   protects Courseware Domain and Generator contracts;
-   contains provider SDK churn;
-   enables deterministic adapter tests;
-   keeps core CI credential-free;
-   creates a stable error boundary;
-   makes credential ownership explicit;
-   enables future provider replacement.

Costs:

-   translation code is required;
-   provider exceptions need explicit mapping;
-   live-test infrastructure is separate;
-   provider timeout/error semantics must be normalized carefully.

## Implementation Status

Step 6.10 --- Real Provider Adapter 已完成。

目前 implementation evidence 包括：

-   existing `AIProvider` 持續作為 provider-independent application
    boundary；
-   minimum provider-independent AI provider error hierarchy；
-   first concrete `OpenAIProviderAdapter`；
-   injected client / transport boundary for deterministic tests；
-   finite timeout behavior；
-   explicit authentication, rate-limit, timeout, unavailable, and
    provider error conversion；
-   exception chaining；
-   credential isolation and non-leakage coverage；
-   deterministic generic provider-adapter tests；
-   deterministic no-network OpenAI adapter tests；
-   opt-in `ai_live` marker and live-provider smoke-test separation；
-   missing `OPENAI_API_KEY` causes live verification to skip rather
    than fail core verification；
-   normal pytest, pre-commit, and core CI remain credential-free and
    cost-free.

Paid/live OpenAI invocation remains optional operational verification
and is not required for ADR 0022 acceptance or Milestone 6 core
acceptance.

Latest Milestone 6 local acceptance regression:

``` text
1119 passed, 1 deselected
Total coverage: 90.23%
Required coverage: 67.0%
```

The coverage gate is satisfied. Acceptance PR GitHub Actions / CI remains a
separate final Milestone 6 closure gate.

Step 6.11 has subsequently established the representative deterministic
AI-to-Courseware E2E. ADR 0022 therefore has no remaining implementation
dependency on that E2E; Milestone 6 formal acceptance is tracked
separately in `docs/milestones/milestone-6-acceptance.md`.

## Implementation Plan

The Step 6.10 implementation sequence has completed:

``` text
ADR 0022 Provider Adapter Contract ✅
        ↓
Architecture / ADR Index / Roadmap Alignment ✅
        ↓
Provider Adapter Contract Tests ✅
        ↓
Minimum Provider-independent Error Additions ✅
        ↓
First Concrete Provider Adapter ✅
        ↓
No-network Provider-specific Tests ✅
        ↓
Live-test Marker / Separation ✅
        ↓
Documentation Alignment ✅
        ↓
Full Regression / Core CI ✅
```

Optional paid/live Provider smoke verification remains operational and
is not a core acceptance gate.

## Test Strategy

Contract tests verify protocol compatibility, deterministic request
translation, response normalization, and SDK isolation.

Failure tests verify authentication, rate-limit, timeout,
unavailable/provider error conversion, chaining, and unexpected-error
transparency.

Security tests verify credential isolation from `AIRequest`,
`AIResponse`, Domain, exceptions, and normal test requirements.

Side-effect tests verify the adapter does not write production files or
invoke Generator/Git operations.

Required deterministic gates:

``` powershell
ruff check generator\ai tests\ai
ruff format --check generator\ai tests\ai
python -m pytest tests\ai -v --no-cov
pre-commit run --all-files
python -m pytest
```

Live-provider tests are not part of these core gates.

## Documentation Changes

With this ADR:

-   add ADR 0022 to `docs/adr/README.md`;
-   update `docs/architecture/ai-integration.md`;
-   update `docs/roadmap.md`.

When the first adapter is implemented, also review AI
error/configuration references, `CHANGELOG.md`, `docs/HISTORY.md`, and
live-test/CI documentation.

Documentation must distinguish the Provider Adapter Contract from a
configured and operational live provider.

## Rollback Plan

If the first concrete adapter proves unsuitable:

1.  remove or replace the concrete adapter;
2.  remove provider-specific dependencies/configuration;
3.  preserve `AIProvider`, `AIRequest`, `AIResponse`, and application
    services;
4.  preserve deterministic Fake-provider tests;
5.  preserve Courseware Domain and Generator contracts;
6.  supersede this ADR only if the provider-independent adapter boundary
    itself is rejected.

No Courseware migration should be required because provider-specific
state is not stored in Courseware Domain objects.

## Acceptance Criteria

ADR 0022 moved from `Proposed` to `Accepted` after the following
criteria were satisfied:

-   adapter responsibility and SDK isolation are reviewed;
-   credential ownership/isolation is agreed;
-   timeout behavior is agreed;
-   initial retry policy is explicit;
-   provider-independent error conversion is agreed;
-   deterministic adapter testing is agreed;
-   live-provider test separation is agreed;
-   architecture, ADR index, and roadmap are aligned;
-   documentation quality gates pass.

ADR acceptance does not require a live provider call.

Step 6.10 implementation completion additionally required provider
contract tests, the first concrete adapter, required OPL error types,
no-network provider-specific tests, live-test separation, full
regression/core CI, and documentation alignment. These Step 6.10
requirements are now complete.

## Code Review Checklist

### Architecture

-   [ ] Adapter implements existing `AIProvider`.
-   [ ] No speculative second provider abstraction.
-   [ ] Provider SDK imports remain adapter-private.
-   [ ] Courseware Domain and Generator do not depend on provider SDK.
-   [ ] Application services do not consume provider-specific response
    types.
-   [ ] Existing validation/mapping is not bypassed.

### Credentials and Security

-   [ ] Credentials are not hard-coded or committed.
-   [ ] Credentials do not enter `AIRequest`, `AIResponse`, Domain,
    Template Context, or `GenerationPlan`.
-   [ ] Logs and exceptions do not expose credentials.
-   [ ] Credential leakage paths are tested.

### Errors

-   [ ] Recognized provider failures map to OPL AI errors.
-   [ ] Timeout maps to `AITimeoutError`.
-   [ ] Exception chaining is preserved.
-   [ ] Unexpected programming errors are not hidden.

### Timeout and Retry

-   [ ] Real invocation has a finite timeout.
-   [ ] Timeout ownership remains outside Domain.
-   [ ] Automatic retry is not silently introduced.
-   [ ] Provider SDK retry defaults are reviewed/configured/documented.

### Response and Side Effects

-   [ ] Successful invocation returns `AIResponse`.
-   [ ] Provider-specific response objects do not escape.
-   [ ] Provider metadata stays outside Courseware Domain.
-   [ ] Malformed responses fail explicitly.
-   [ ] Adapter does not write files, create plans, run Generators, or
    perform Git operations.

### Testing and Automation

-   [ ] Adapter tests use fake/stub client or controlled transport.
-   [ ] Core tests require no network or API key.
-   [ ] Error conversion and credential isolation tests exist.
-   [ ] Unexpected-error transparency is tested.
-   [ ] Live tests are opt-in and do not assert exact prose.
-   [ ] ADR 0022, architecture, and roadmap are aligned.
-   [ ] `git diff --check`, Ruff, Ruff Format, AI tests, pre-commit,
    full pytest, and CI pass.

## Decision Summary

OPL will connect real AI providers through explicit Provider Adapters
implementing the existing `AIProvider` protocol.

``` text
Application
    ↓
AIProvider
    ↓
Provider Adapter
    ↓
Provider SDK / Network
```

Provider SDKs, credentials, transport behavior, vendor exceptions, and
response normalization remain infrastructure concerns. Normal tests stay
deterministic and credential-free; live-provider tests are opt-in.

> **AI proposes. Domain validates. Generator plans. Filesystem commits.
> Tests verify.**
