# ADR 0023 — Marketplace Artifact Contract

> **Status:** Accepted
> **Date:** 2026-08-16
> **Milestone:** 7 — Marketplace
> **Decision Type:** Architecture / Distribution Contract

## Context

OpenProjectLab 已完成 Generator Framework、Plugin Ecosystem、Open Courseware Platform 與 AI Integration 的主要 architecture milestones。

既有架構已提供：

- canonical Generator lifecycle；
- stable Generator contracts；
- `generator.sdk` public façade；
- Plugin validation；
- canonical `openprojectlab.generators` Entry Point loading；
- Registry preflight；
- transactional Plugin registration；
- third-party Plugin distribution model；
- deterministic Courseware composition；
- controlled Filesystem side effects；
- provider-independent AI boundaries。

Milestone 7 的目標是建立 Marketplace capability，使 OPL ecosystem 可以逐步支援：

- Plugin Packages；
- Generator Packages；
- Template Packages；
- versioned artifacts；
- artifact discovery；
- compatibility validation；
- integrity verification；
- Community Repository；
- installation / upgrade workflows。

目前缺少一個共同 contract，回答：

> 什麼是 OPL Marketplace Artifact？

如果沒有共同 artifact contract，Plugin、Generator 與 Template distribution 可能各自建立不同的：

- identity；
- version；
- metadata；
- compatibility；
- integrity；
- discovery；
- installation semantics。

這會形成平行 package models，並增加 Marketplace 與既有 Plugin / Generator architecture 的耦合。

因此在實作 Marketplace repository、installer 或 CLI 之前，必須先定義最小 Marketplace Artifact Contract。

---

## Decision

OPL 將建立一個 provider-independent、repository-independent、installation-independent 的 Marketplace Artifact Contract。

核心概念為：

```text
MarketplaceArtifact
```

它代表 Marketplace 中可識別、可版本化、可驗證與可分發的 artifact metadata。

初始 artifact types：

```text
Plugin Package
Generator Package
Template Package
```

Marketplace Artifact Contract 只描述 artifact。

它不定義新的 execution lifecycle。

---

## Artifact Model

概念模型：

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

正式 Python API 由後續 contract tests 與 implementation 決定。

本 ADR 不要求 Step 7.1 立即建立 production classes。

---

## Artifact Identity

Artifact 必須具有 stable identity。

概念：

```text
ArtifactIdentity
├── namespace
└── name
```

例如：

```text
community/modern-java-templates
```

Identity 必須：

- deterministic；
- stable；
- independent of display name；
- independent of local filesystem path；
- independent of distribution URL；
- safe for comparison；
- uniquely identify artifact within repository scope。

Display metadata 不構成 identity。

---

## Artifact Version

每個 artifact release 必須具有 explicit version。

初始 contract 採用 Semantic Versioning compatible representation：

```text
MAJOR.MINOR.PATCH
```

Canonical artifact version 不使用：

```text
latest
stable
current
```

這些若未來需要，只能作為 alias / channel。

Version comparison semantics 必須 deterministic。

---

## Artifact Coordinate

Identity 與 version 組成：

```text
ArtifactCoordinate
```

概念：

```text
community/modern-java-templates@1.2.0
```

Artifact coordinate 是 immutable release identifier。

相同 coordinate 不得合法對應不同內容。

---

## Artifact Type

初始 artifact types：

```text
plugin
generator
template
```

Unknown artifact type 必須 validation failure。

Artifact type 不由檔名、package content 或 display description 推論。

---

## Metadata Schema Version

Marketplace metadata 必須具有獨立 schema version：

```text
schema_version
```

例如：

```text
schema_version: 1
```

Metadata schema version 與 artifact version 不同。

Schema version 控制 metadata contract evolution。

Artifact version控制 artifact release evolution。

---

## Compatibility Contract

Artifact 必須能宣告其 OPL runtime compatibility。

概念：

```text
CompatibilityRequirement
```

例如：

```text
>=0.7,<1.0
```

Compatibility validation 必須：

- deterministic；
- side-effect-free；
- network-independent；
- 在 installation / activation side effects 前執行。

不相容 artifact 必須明確拒絕。

Compatibility Contract 不等同於 general dependency resolution。

---

## Distribution Contract

Artifact identity 與 distribution location 必須分離。

概念：

```text
DistributionMetadata
```

Distribution metadata 描述 artifact 如何取得。

它不能成為 artifact identity。

因此 distribution source 可以改變，而 artifact coordinate 保持不變。

本 ADR 不要求 Marketplace 自行取代 Python packaging ecosystem。

---

## Integrity Contract

Artifact metadata 必須能描述 artifact integrity。

初始最低要求：

```text
SHA-256
```

概念：

```text
IntegrityMetadata
├── algorithm
└── digest
```

取得 artifact 後，必須在 activation 前驗證 integrity。

Integrity mismatch 必須失敗。

---

## Integrity Does Not Establish Trust

本 ADR 明確區分：

```text
Integrity
Authenticity
Trust
Authorization
```

Checksum 只能證明取得的內容是否與預期 digest 一致。

Checksum 不能證明：

- publisher identity；
- code safety；
- absence of malicious behavior；
- artifact quality。

Signing、publisher verification 與 trust policy 不屬於本 ADR 的初始 scope。

---

## Plugin Package Decision

Plugin Package 不建立 Marketplace-specific Plugin runtime。

安裝後仍必須經過：

```text
Existing Entry Point Discovery
    ↓
Existing Plugin Validation
    ↓
Registry Preflight
    ↓
Transactional Registration
```

Marketplace metadata validation 不能取代 Plugin validation。

---

## Generator Package Decision

Generator Package 不建立新的 Generator lifecycle。

正式 execution 仍遵循既有：

```text
GenerateRequest
    ↓
validate_request()
    ↓
plan()
    ↓
GenerationPlan
    ↓
execute / simulate
    ↓
GenerationResult
```

如果 Generator 透過 Plugin distribution 提供，應重用既有 Plugin SDK / Entry Point contracts。

---

## Template Package Decision

Template Package 使用相同 Marketplace identity/version/compatibility/integrity contracts。

Template-specific：

- manifest；
- template resolution；
- resource ownership；
- rendering integration；
- upgrade semantics；

由後續 contract / ADR 定義。

Template Package discovery 不得執行 arbitrary code。

---

## Discovery Decision

Artifact discovery 必須與 installation 分離。

```text
Discover
    ↓
Inspect Metadata
    ↓
Select
```

Discovery 必須 side-effect-free。

搜尋 artifact 不應：

- download executable package；
- install distribution；
- register Plugin；
- execute Generator；
- modify generated files。

---

## Installation Decision

Installation 與 activation 必須分離。

```text
Validate
    ↓
Acquire
    ↓
Verify Integrity
    ↓
Install
    ↓
Activate / Load
```

這使 compatibility、integrity 與 security checks 可以在 execution 前完成。

---

## Repository Decision

Marketplace repository 必須使用相同 Artifact Contract。

Repository 可以是：

- local；
- static；
- remote；
- community-hosted。

Core contract 不依賴特定 hosting provider。

Contract tests 必須使用 deterministic local fixtures。

Public remote Marketplace availability 不得成為 normal CI requirement。

---

## Duplicate Coordinate Decision

相同：

```text
identity + version
```

不得合法對應不同 artifact content。

如果 repository 發現 duplicate coordinate with conflicting metadata/content：

```text
fail explicitly
```

不得 silent overwrite。

---

## Public API Decision

Marketplace models 不會因本 ADR 自動加入：

```text
generator.sdk
```

任何 public SDK exposure 都必須經過獨立 compatibility review。

Step 7.1 的 Marketplace Artifact Contract 是 architecture contract，不是立即的 stable public SDK promise。

---

## Security Decision

Marketplace metadata 與第三方 distribution 一律視為：

```text
untrusted external input
```

因此必須：

- validate metadata；
- validate compatibility；
- verify integrity；
- preserve existing Plugin validation；
- preserve existing Generator validation；
- avoid execution during discovery。

本 ADR 不提供 sandbox guarantee。

---

## Filesystem Decision

Marketplace metadata 不得任意控制 Generator output filesystem。

Artifact installation storage 與 generated project output 是不同責任。

正式 generated artifacts 仍透過既有：

```text
GenerationPlan
    ↓
Filesystem
```

Marketplace installation 不得繞過這個 boundary。

---

## Alternatives Considered

### Alternative A — Separate Metadata Contract Per Artifact Type

為 Plugin、Generator、Template 各建立獨立 metadata format。

Rejected as primary architecture。

原因：

- identity 重複設計；
- version 重複設計；
- compatibility 重複設計；
- integrity 重複設計；
- Marketplace repository 需要理解多套不一致模型。

Artifact-specific metadata 仍可以擴充 common contract。

---

### Alternative B — Use Python Package Metadata as Entire Marketplace Contract

直接將 Python distribution metadata 當作 Marketplace model。

Rejected。

原因：

- Template Package 不一定等同 Python package；
- OPL-specific compatibility 無法完全表達；
- artifact type 與 integrity semantics 不夠明確；
- Marketplace identity 會與 packaging provider 過度耦合。

Python packaging 可以作為 distribution mechanism，但不是完整 Marketplace domain contract。

---

### Alternative C — Use Git Repository URL as Artifact Identity

例如：

```text
https://example/repository.git
```

作為 artifact identity。

Rejected。

原因：

- repository 可以搬遷；
- hosting provider 不應成為 domain identity；
- 同 repository 可能包含多個 artifacts；
- URL 不等於 version；
- reproducibility 不足。

---

### Alternative D — Marketplace-specific Generator Runtime

建立：

```text
MarketplaceGenerator
MarketplaceExecutionPlan
MarketplaceResult
```

Rejected。

原因：

- 與既有 Generator lifecycle 重複；
- 破壞 Milestone 3 architecture；
- Plugin / built-in / Marketplace Generator 會形成多套 runtime。

Marketplace 必須重用 existing execution contracts。

---

### Alternative E — Remote Marketplace First

先建立 remote API / web service，再決定 artifact model。

Rejected。

原因：

- service contract 會過早綁定尚未穩定的 domain model；
- core tests 可能依賴 network；
- artifact identity/version/integrity 尚未先穩定；
- 增加 operational complexity。

OPL 採用 contract-first strategy。

---

## Consequences

### Positive

- Plugin、Generator、Template 可以共享一致 identity/version semantics。
- Marketplace repository 可以建立在共同 artifact model 上。
- Distribution mechanism 與 artifact identity 解耦。
- Compatibility 可以在 installation 前驗證。
- Integrity 可以成為正式 contract。
- Existing Plugin / Generator architecture 被保留。
- Core tests 可以完全 deterministic。
- Remote Marketplace service 可以延後實作。
- 未來 Community Repository 可以共享相同 schema。

### Costs

- 需要新增 Marketplace models 與 validation。
- 需要 version requirement parser / comparison strategy。
- 需要 metadata schema evolution policy。
- 需要 integrity verification。
- Template Package 仍需要後續專屬 contract。
- Installation / rollback 仍需要後續 architecture。
- Artifact signing / publisher trust 尚未解決。

---

## Migration Plan

目前沒有 production Marketplace API，因此不需要 runtime migration。

導入順序：

```text
Architecture / ADR
    ↓
Artifact Contract Tests
    ↓
Minimal Immutable Models
    ↓
Metadata Validation
    ↓
Compatibility Validation
    ↓
Integrity Contract
    ↓
Repository Contract
    ↓
Installation Integration
    ↓
Template Package Contract
    ↓
Representative Marketplace E2E
    ↓
Milestone Acceptance
```

既有 Plugin distributions 不應被立即破壞。

後續 Marketplace integration 應以 adapter / metadata mapping 的方式逐步納入既有 Plugin distribution。

---

## Test Strategy

### Contract Tests

驗證：

- valid artifact；
- identity；
- version；
- artifact type；
- coordinate；
- schema version；
- compatibility；
- distribution metadata；
- integrity metadata；
- immutability；
- deterministic comparison / serialization。

### Failure Tests

驗證：

- empty identity；
- malformed identity；
- invalid version；
- unknown artifact type；
- unsupported schema version；
- invalid compatibility requirement；
- malformed integrity digest；
- unsupported integrity algorithm；
- duplicate coordinate。

### Compatibility Tests

驗證：

- compatible runtime；
- incompatible runtime；
- lower boundary；
- upper boundary；
- exact version；
- version range。

### Integrity Tests

驗證：

- valid SHA-256；
- digest mismatch；
- malformed digest；
- changed content；
- deterministic hashing。

### Repository Tests

使用 deterministic local fixtures 驗證：

- artifact lookup；
- exact version lookup；
- available version ordering；
- artifact not found；
- duplicate coordinate；
- deterministic results。

### Integration Tests

後續 installation integration 驗證：

- incompatible artifact causes no activation；
- integrity failure causes no activation；
- Plugin validation cannot be bypassed；
- installation does not execute Generator；
- installation does not modify generated courseware。

### Representative E2E

Milestone 7 acceptance 前建立：

```text
Local Marketplace Fixture
    ↓
Discovery
    ↓
Artifact Validation
    ↓
Compatibility Validation
    ↓
Integrity Verification
    ↓
Installation
    ↓
Existing Plugin Discovery
    ↓
Existing Plugin Validation
    ↓
Canonical Generator Execution
    ↓
Deterministic Output
```

核心 E2E 不依賴 public network。

---

## Automation Strategy

每個 Marketplace implementation PR 至少執行：

```powershell
git diff --check
ruff check generator tests
ruff format --check generator tests
pre-commit run --all-files
python -m pytest
```

Marketplace-specific tests 建立後應另外執行：

```powershell
python -m pytest tests\marketplace -v --no-cov
```

Repository coverage 必須保持高於既有 coverage policy。

Normal CI 不依賴：

- public Marketplace；
- public GitHub repository；
- external package index availability；
- credentials；
- paid service。

---

## Documentation Changes

本 ADR 建立時同步：

```text
docs/architecture/marketplace.md
docs/adr/0023-marketplace-artifact-contract.md
docs/adr/README.md
docs/roadmap.md
```

後續 implementation 視需要同步：

```text
docs/reference/marketplace.md
docs/HISTORY.md
CHANGELOG.md
README.md
docs/development/*
```

任何尚未由 production code 與 tests 支援的 Marketplace capability 必須保持 `Proposed`。

---

## Rollback Plan

Step 7.1 為 architecture/documentation-only change，因此 rollback 不涉及 production runtime。

若 ADR 0023 在 implementation 前被否決：

1. 將 ADR 標示為 `Superseded` 或以新 ADR 取代。
2. 更新 `docs/architecture/marketplace.md`。
3. 更新 ADR index。
4. 更新 roadmap。
5. 不需要 production data migration。

一旦 Marketplace artifact metadata 已公開發佈，則不得直接改寫 accepted identity/version semantics。

重大 contract change 必須建立新 ADR 與 migration strategy。

---

## Implementation Status

目前：

```text
Marketplace Architecture        Implemented
Artifact Contract               Implemented
Artifact Contract Tests         Implemented
Marketplace Models              Implemented
Marketplace Repository          Implemented
Compatibility Requirement       Implemented
Integrity Verifier              Implemented
Artifact Acquisition            Implemented
Marketplace Installer           Implemented
Template Packages               Implemented
Representative Marketplace E2E Implemented
Community Repository            Deferred
Marketplace CLI                 Deferred
Remote Marketplace Service      Deferred
```

Milestone 7 已完成 common Marketplace artifact contract 與 deterministic
local/in-memory integration boundary。Remote Marketplace、Community Repository
hosting、CLI、signing、sandbox、general dependency resolution 與 activation
runtime 仍屬後續 capability。

---

## Acceptance Criteria

ADR 0023 可在以下條件完成後由 `Proposed` 轉為 `Accepted`：

### Contract

- [x] Artifact identity contract 有 production implementation。
- [x] Artifact version contract 有 production implementation。
- [x] Artifact type contract 有 production implementation。
- [x] Artifact coordinate contract 有 production implementation。
- [x] Schema version contract 有 production implementation。
- [x] OPL compatibility contract 有 production implementation。
- [x] Distribution metadata contract 有 production implementation。
- [x] Integrity metadata contract 有 production implementation。

### Tests

- [x] Marketplace artifact contract tests 通過。
- [x] Invalid metadata tests 通過。
- [x] Compatibility tests 通過。
- [x] Integrity tests 通過。
- [x] Duplicate coordinate semantics 有測試。
- [x] Tests deterministic。
- [x] Core tests 不依賴 network。

### Architecture

- [x] Marketplace 沒有建立第二套 Generator lifecycle。
- [x] Existing Plugin SDK remains canonical。
- [x] Existing Entry Point / Plugin validation boundaries preserved。
- [x] Marketplace metadata 不繞過 Generator validation。
- [x] Marketplace metadata 不控制 generated filesystem side effects。

### Documentation

- [x] Marketplace architecture 同步。
- [x] ADR index 同步。
- [x] Roadmap 同步。
- [x] Implementation status 沒有 overclaim。

### Automation

- [x] `git diff --check` 通過。
- [x] Ruff 通過。
- [x] Ruff Format 通過。
- [x] `pre-commit run --all-files` 通過。
- [x] `python -m pytest` 通過。
- [x] Coverage 不低於 repository policy。
- [ ] CI 通過（acceptance PR pending）。

---

## Acceptance Evidence

Final local Milestone 7 regression：

```text
1315 passed, 1 deselected
Total coverage: 89.89%
Required coverage: 67.0% --- Passed
```

ADR 0023 因 artifact contract、repository/index、integrity/acquisition、
installation、Template Package 與 representative Marketplace E2E 已完成，
正式轉為 `Accepted`。

GitHub Actions / CI 仍由 Milestone 7 acceptance PR 作為最後 automation gate。

---

## Code Review Checklist

### Architecture

- [ ] Marketplace responsibility limited to ecosystem distribution concerns。
- [ ] No parallel Generator lifecycle。
- [ ] No parallel Plugin loading architecture。
- [ ] Existing Plugin SDK preserved。
- [ ] Existing Generator contracts preserved。
- [ ] Courseware Domain boundary preserved。
- [ ] Filesystem boundary preserved。
- [ ] AI Provider boundary unaffected。

### Artifact Contract

- [ ] Identity 與 display metadata 分離。
- [ ] Identity deterministic。
- [ ] Version explicit。
- [ ] Artifact type explicit。
- [ ] Coordinate immutable。
- [ ] Schema version 與 artifact version 分離。
- [ ] Unknown required values fail explicitly。
- [ ] Duplicate coordinate cannot silently overwrite。

### Compatibility

- [ ] Compatibility requirement explicit。
- [ ] Validation happens before activation。
- [ ] Validation deterministic。
- [ ] Validation requires no network。
- [ ] No general-purpose dependency solver introduced accidentally。

### Distribution

- [ ] Distribution reference is not identity。
- [ ] Hosting provider does not leak into core model。
- [ ] Discovery has no execution side effect。
- [ ] Installation and activation remain separate。

### Integrity and Security

- [ ] Integrity metadata explicit。
- [ ] SHA-256 behavior deterministic。
- [ ] Integrity failure prevents activation。
- [ ] Integrity is not described as trust。
- [ ] Third-party metadata treated as untrusted。
- [ ] Third-party Plugin validation remains required。
- [ ] No sandbox claims without implementation。

### Testing

- [ ] Contract tests precede implementation。
- [ ] Invalid identity tested。
- [ ] Invalid version tested。
- [ ] Unknown type tested。
- [ ] Compatibility boundaries tested。
- [ ] Integrity mismatch tested。
- [ ] Duplicate coordinate tested。
- [ ] Repository ordering deterministic。
- [ ] Core tests require no network。
- [ ] Failure occurs before side effects where required。

### Documentation and Automation

- [ ] `docs/architecture/marketplace.md` synchronized。
- [ ] ADR index synchronized。
- [ ] Roadmap synchronized。
- [ ] Proposed capabilities are not described as implemented。
- [ ] Public SDK exposure reviewed separately。
- [ ] `git diff --check` passes。
- [ ] `pre-commit run --all-files` passes。
- [ ] `python -m pytest` passes。
- [ ] Coverage remains above repository policy。
- [ ] CI passes。

---

## Related Documents

- `docs/architecture/marketplace.md`
- `docs/architecture/generator.md`
- `docs/architecture/plugin-ecosystem.md`
- `docs/architecture/open-courseware-platform.md`
- `docs/architecture/ai-integration.md`
- `docs/adr/0010-plugin-sdk-public-contract.md`
- `docs/adr/0011-plugin-validation-contract.md`
- `docs/adr/0012-plugin-entry-point-contract.md`
- `docs/adr/0013-plugin-distribution-contract.md`
- `docs/adr/0020-courseware-composition-contract.md`
- `docs/adr/0021-ai-integration-contract.md`
- `docs/adr/0022-ai-provider-adapter-contract.md`
- `docs/adr/README.md`
- `docs/roadmap.md`

---

## Decision Summary

OPL Marketplace 將採用共同的 Marketplace Artifact Contract：

```text
MarketplaceArtifact
    ↓
Identity + Version + Type
    ↓
Compatibility
    ↓
Distribution Metadata
    ↓
Integrity Metadata
    ↓
Validation
    ↓
Existing OPL Integration Boundary
```

Marketplace 不建立新的 execution framework。

Plugin、Generator 與 Template 可以成為 Marketplace artifacts，但正式 execution、validation 與 filesystem behavior 仍由既有 OPL contracts 管理。

> **Marketplace distributes. Contracts validate. Existing OPL pipelines execute.**
