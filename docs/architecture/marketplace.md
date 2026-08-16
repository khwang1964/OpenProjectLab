# OpenProjectLab Marketplace Architecture

> **Status:** Proposed
> **Milestone:** 7 — Marketplace
> **Scope:** Marketplace artifacts, package metadata, identity, versioning, compatibility, integrity, discovery, distribution, installation, upgrade, removal, trust, and ecosystem boundaries
> **Audience:** Maintainers, contributors, Plugin authors, Generator authors, Template authors, package publishers, and future Marketplace tooling developers

OpenProjectLab（OPL）Marketplace 的目的，是在既有 OPL 架構之上建立一個**可發佈、可發現、可驗證、可安裝與可版本化的擴充生態系統**。

Marketplace 不建立新的 Generator lifecycle，也不取代 Plugin SDK、Generator contracts、Template infrastructure、Courseware Domain、AI integration 或 Filesystem boundaries。

核心原則：

> **Marketplace distributes capabilities; existing OPL contracts execute them.**

---

## 1. Context

Milestone 3 至 Milestone 6 已建立：

* canonical Generator lifecycle；
* stable Generator contracts；
* `generator.sdk` public façade；
* Plugin validation；
* canonical `openprojectlab.generators` Entry Point discovery/loading；
* transactional Plugin registration；
* third-party Plugin distribution model；
* Open Courseware Domain；
* deterministic Courseware Composition；
* AI Provider / Adapter boundaries；
* deterministic testing and CI boundaries。

因此 Milestone 7 的主要問題已不是：

> OPL 如何執行一個 Generator？

而是：

> OPL 如何安全地描述、發佈、發現、驗證與取得第三方能力？

Marketplace 必須建立在既有 contracts 上，而不是建立第二套 execution framework。

---

## 2. Goals

Marketplace Architecture 的主要目標：

* 定義 Marketplace Artifact。
* 建立穩定 artifact identity。
* 建立明確 artifact version。
* 定義 artifact type。
* 表達 OPL compatibility requirement。
* 定義 distribution metadata。
* 支援 artifact integrity verification。
* 建立 deterministic metadata validation。
* 支援 package discovery。
* 建立 installation boundary。
* 建立 upgrade compatibility boundary。
* 建立 removal/uninstallation boundary。
* 保留既有 Plugin SDK 與 Generator lifecycle。
* 支援未來 Community Repository。
* 支援未來 versioned Template distribution。
* 讓 contract tests 不依賴 public Marketplace service 或 network。

---

## 3. Non-Goals

Milestone 7 初始 Marketplace Architecture 不直接定義：

* Web Marketplace UI。
* 商業付款系統。
* Rating / Review system。
* Recommendation engine。
* Social network。
* Package monetization。
* License purchasing。
* Remote code execution。
* Container sandbox。
* General-purpose package manager。
* Python dependency resolver replacement。
* PyPI replacement。
* GitHub replacement。
* Template rendering engine replacement。
* Generator execution replacement。
* Plugin loading replacement。
* AI Provider marketplace。
* Automatic trust of third-party code。

以上能力若未來需要，應以獨立 ADR 決定。

---

## 4. Architectural Principle

Marketplace 的責任鏈：

```text
Publisher
    ↓
Marketplace Artifact Metadata
    ↓
Validation
    ↓
Repository / Distribution Source
    ↓
Discovery
    ↓
Artifact Selection
    ↓
Compatibility Validation
    ↓
Integrity Validation
    ↓
Installation
    ↓
Existing OPL Integration Boundary
```

安裝後的 execution 仍遵循既有 OPL contracts。

例如 Plugin：

```text
Marketplace
    ↓
Plugin Distribution
    ↓
Installation
    ↓
Python Distribution
    ↓
openprojectlab.generators Entry Point
    ↓
Existing Plugin Validation
    ↓
Registry Preflight
    ↓
Transactional Registration
    ↓
Canonical Generator Lifecycle
```

Marketplace 不繞過 Plugin validation。

---

## 5. Marketplace Artifact

Marketplace 的基本單位稱為：

```text
MarketplaceArtifact
```

初始 artifact categories：

```text
MarketplaceArtifact
├── Plugin Package
├── Generator Package
└── Template Package
```

這三種類型共享 identity、version、compatibility、distribution 與 integrity contracts，但實際 activation / execution semantics 不一定相同。

---

## 6. Artifact Type

概念模型：

```python
class ArtifactType(StrEnum):
    PLUGIN = "plugin"
    GENERATOR = "generator"
    TEMPLATE = "template"
```

正式名稱與 module placement 由後續 contract implementation 決定。

Artifact type 必須：

* 明確；
* deterministic；
* 可驗證；
* 不依賴自由文字推論；
* 未知 type 必須拒絕。

---

## 7. Plugin Package

Plugin Package 表示符合既有 Plugin SDK / Entry Point contracts 的第三方 distribution。

Marketplace 不重新定義 Plugin runtime。

責任鏈：

```text
Plugin Package
    ↓
Distribution Installation
    ↓
Entry Point Discovery
    ↓
Existing Plugin Validation
    ↓
Registry Preflight
    ↓
Transactional Registration
```

Marketplace metadata 不得被視為 Plugin validation 的替代品。

---

## 8. Generator Package

Generator Package 表示提供 OPL Generator capability 的可發佈 artifact。

如果 Generator 透過 Plugin distribution 提供，應優先沿用既有 Plugin SDK 與 Entry Point contract。

Marketplace 不建立：

```text
MarketplaceGenerator.run()
```

或其他平行 execution API。

正式 Generator execution 仍使用既有 canonical lifecycle。

---

## 9. Template Package

Template Package 表示可版本化與分發的 Template 集合。

Template Package 可以包含：

* Jinja templates；
* static resources；
* package metadata；
* template manifest；
* documentation。

Template Package 不應：

* 直接執行任意 Generator；
* 自行修改 Registry；
* 自行繞過 Filesystem policy；
* 在 discovery 階段執行 arbitrary code。

Template activation、resolution 與 ownership semantics 應由後續 Template Package contract 定義。

---

## 10. Artifact Identity

每個 Marketplace Artifact 必須具有穩定 identity。

概念：

```text
ArtifactIdentity
```

最低需求：

```text
namespace
name
```

例如：

```text
openprojectlab/example-generator
community/modern-java-templates
```

Identity 應：

* 與 display name 分離；
* deterministic；
* case policy 明確；
* 不包含 filesystem traversal semantics；
* 不依賴本機路徑；
* 不依賴 distribution URL；
* 在 repository scope 中唯一。

---

## 11. Display Name Is Not Identity

以下欄位：

```text
display_name
description
author_display_name
```

屬於 human-readable metadata。

它們不能作為 artifact identity。

例如：

```text
Display Name:
Modern Java Templates
```

可以修改成：

```text
Modern Java Course Templates
```

但 artifact identity 可以保持：

```text
community/modern-java-templates
```

避免 presentation change 造成 dependency break。

---

## 12. Artifact Version

每個可發佈 Artifact 必須具有明確 version。

初始 architecture 建議採用 Semantic Versioning compatible representation：

```text
MAJOR.MINOR.PATCH
```

例如：

```text
1.0.0
1.2.3
2.0.0
```

正式 parser、pre-release、build metadata 與 comparison semantics 應由 contract tests 與 implementation 決定。

不得以：

```text
latest
current
new
stable
```

作為 artifact version contract。

這些可以是 channel 或 alias，但不是 canonical version。

---

## 13. Artifact Coordinate

Artifact identity 與 version 組成 immutable coordinate：

```text
ArtifactCoordinate
    ├── identity
    └── version
```

概念：

```text
community/modern-java-templates@1.2.0
```

相同 coordinate 不應指向不同 artifact content。

這是 reproducibility 與 integrity 的基本要求。

---

## 14. Metadata Model

Marketplace metadata 最低應表達：

```text
schema_version
identity
version
artifact_type
description
opl_compatibility
distribution
integrity
```

未來可加入：

```text
authors
license
homepage
repository
documentation
keywords
dependencies
capabilities
deprecation
```

Optional metadata 不應改變 core identity semantics。

---

## 15. Metadata Example

概念格式：

```yaml
schema_version: 1

artifact:
  namespace: community
  name: modern-java-templates
  version: 1.2.0
  type: template

description: Templates for Modern Java courseware.

compatibility:
  openprojectlab: ">=0.7,<1.0"

distribution:
  kind: package
  reference: example-distribution-reference

integrity:
  algorithm: sha256
  digest: example-digest
```

這只是 architecture example，不代表目前 production schema 已存在。

---

## 16. Schema Version

Marketplace metadata 本身必須 versioned。

例如：

```text
schema_version: 1
```

Artifact version 與 metadata schema version 是不同概念。

```text
Artifact Version
```

描述 artifact release。

```text
Schema Version
```

描述 metadata contract。

兩者不得混用。

---

## 17. OPL Compatibility

Marketplace 必須在 installation / activation 前判斷 artifact 是否與目前 OPL runtime 相容。

概念：

```text
CompatibilityRequirement
```

例如：

```text
>=0.7,<1.0
```

Compatibility validation 應：

* deterministic；
* 不依賴 network；
* 在 side effect 前完成；
* 不以 warning 取代明確 incompatibility failure。

---

## 18. Compatibility Is Not Dependency Resolution

OPL compatibility contract 只回答：

> 這個 artifact 宣告支援哪些 OPL versions？

它不等同於完整 dependency solver。

第三方 Python dependencies 初期仍可由既有 Python packaging ecosystem 處理。

Marketplace 不應在第一階段重新實作 pip / packaging dependency resolution。

---

## 19. Distribution Metadata

Marketplace metadata 必須將 artifact identity 與 artifact location 分離。

概念：

```text
DistributionMetadata
```

可能描述：

* Python package distribution；
* archive；
* repository release；
* future OPL package source。

但 architecture 不應把 GitHub、PyPI 或其他 provider-specific URL 寫入 core identity contract。

Distribution source 可以改變，而 artifact identity 應保持穩定。

---

## 20. Discovery Is Not Installation

Marketplace discovery：

```text
Search
    ↓
Metadata
    ↓
Candidate Artifact
```

不應自動導致：

```text
Download
Install
Activate
Execute
```

Discovery 必須是 side-effect-free。

這是 Marketplace 的重要安全 boundary。

---

## 21. Installation Is Not Activation

即使 artifact 已下載或安裝，也不代表它應立即被執行。

應區分：

```text
Discover
    ↓
Select
    ↓
Validate
    ↓
Acquire
    ↓
Install
    ↓
Activate / Load
    ↓
Execute
```

對 Plugin Package：

```text
Install
```

與：

```text
Entry Point discovery / registration
```

是不同階段。

這讓安全政策與 rollback 更容易定義。

---

## 22. Integrity

Marketplace 必須能驗證取得的 artifact 是否符合 metadata 所宣告的內容。

初始 contract 建議至少支援：

```text
SHA-256
```

概念：

```text
IntegrityMetadata
    ├── algorithm
    └── digest
```

Integrity 驗證必須發生在 artifact 被信任或 activation 前。

---

## 23. Integrity Is Not Trust

Checksum 可以證明：

> 下載內容與預期內容一致。

Checksum 不能證明：

> 內容是安全的。

因此必須區分：

```text
Integrity
Trust
Authenticity
Authorization
```

Milestone 7 初始 architecture 不應宣稱 checksum 等同 security approval。

---

## 24. Trust Boundary

Marketplace artifacts 可能來自第三方。

所有第三方 metadata 與 package content 都應視為：

```text
untrusted external input
```

因此必須驗證：

* metadata structure；
* artifact type；
* identity；
* version；
* compatibility；
* integrity；
* package-specific contract。

Plugin code 仍可能執行 arbitrary Python code。

Marketplace metadata validation 不提供 sandbox 保證。

---

## 25. Repository

Marketplace Repository 是可發現 artifact metadata 的來源。

概念：

```text
MarketplaceRepository
```

初始 architecture 應允許：

```text
Local Repository
Static Repository
Remote Repository
Community Repository
```

但 contract tests 應優先使用 deterministic local fixtures。

Core tests 不應依賴 public Marketplace availability。

---

## 26. Community Repository

Milestone 7 roadmap 中的 Community Repository 應建立在相同 artifact metadata contract 上。

Community Repository 不應擁有另一套 artifact model。

理想：

```text
MarketplaceArtifact Contract
        ↓
Repository Index
        ↓
Community Repository
```

未來若增加官方 repository，也應沿用相同 contract。

---

## 27. Repository Index

Repository 可以提供 artifact index：

```text
ArtifactIdentity
    ↓
Available Versions
    ↓
Artifact Metadata
```

Index 必須 deterministic。

同一 artifact coordinate 不得同時對應兩個互相衝突的 metadata records。

---

## 28. Duplicate Artifacts

Repository 必須拒絕或明確處理：

```text
same identity
+
same version
+
different metadata/content
```

不可採用「最後一個覆蓋前一個」的 silent behavior。

Duplicate coordinate 是 integrity / reproducibility violation。

---

## 29. Version Selection

Marketplace 未來可以支援：

```text
exact version
compatible version range
latest compatible version
```

但 selection policy 必須 deterministic。

Contract implementation 初期可以先只支援 exact version，以降低 dependency resolution complexity。

---

## 30. Installation Boundary

Marketplace installation service 的責任：

```text
Validated Artifact
    ↓
Acquire Distribution
    ↓
Verify Integrity
    ↓
Install
    ↓
Return Installation Result
```

它不應：

* 執行 Generator；
* 建立 Courseware；
* 呼叫 AI；
* 修改 unrelated repository files；
* bypass Plugin validation；
* 自動 commit Git changes。

---

## 31. Installation Result

未來可定義 immutable result：

```text
ArtifactInstallationResult
```

最低資訊：

```text
artifact coordinate
installation status
installed location/distribution
warnings
```

不要只回傳 Boolean。

結構化結果較適合：

* CLI；
* automation；
* tests；
* future API；
* diagnostics。

---

## 32. Upgrade

Upgrade 應視為：

```text
Installed Artifact A@1.0.0
        ↓
Candidate A@1.1.0
        ↓
Compatibility Validation
        ↓
Integrity Validation
        ↓
Upgrade Policy
        ↓
Installation Transition
```

Upgrade 不應默認：

* major version 一定相容；
* user files 可以覆寫；
* Plugin state 可以自動 migration。

重大 upgrade semantics 應由後續 ADR 定義。

---

## 33. Removal

Removal 必須區分：

* distribution removal；
* registry state；
* generated artifacts；
* user-owned files。

移除 Marketplace package 不應自動刪除該 Generator 曾產生的使用者內容。

例如：

```text
courses/
```

不應因 uninstall Generator Plugin 而被刪除。

---

## 34. Existing Plugin Distribution Contract

Marketplace 應重用既有 Plugin distribution architecture。

ADR 0013 已為 Plugin distribution future direction 提供基礎。

Marketplace Artifact Contract 應在其上建立通用 metadata / discovery layer，而不是推翻既有 Entry Point integration。

若 ADR 0013 與 Marketplace implementation 出現衝突，應另行 review ADR 0013 status，而不是靜默改寫歷史決策。

---

## 35. Existing Plugin SDK Boundary

Marketplace 不擴張 `generator.sdk`，除非有獨立 public API review。

Plugin Package 安裝後仍必須遵守：

* stable SDK imports；
* Plugin validation；
* Entry Point contract；
* Registry preflight；
* transactional registration。

Marketplace metadata 不構成 SDK API。

---

## 36. Generator Boundary

Marketplace 不建立新的 Generator contract。

正式 Generator lifecycle 保持：

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

Marketplace 只負責取得與安裝提供該 capability 的 artifact。

---

## 37. Courseware Boundary

Marketplace 不直接修改 Courseware Domain invariants。

Template / Generator package 可以提供新的 courseware capability，但正式 Domain objects 仍必須符合既有 Domain validation。

Marketplace metadata 不可取代 Courseware validation。

---

## 38. AI Boundary

Marketplace 初始 scope 不包含 AI Provider Marketplace。

若未來 distribution AI Provider adapters，仍必須遵守：

* existing `AIProvider` boundary；
* provider-specific isolation；
* credential isolation；
* deterministic no-network core tests；
* no direct filesystem side effect。

此能力需要獨立 ADR。

---

## 39. Filesystem Boundary

Marketplace 不應讓 artifact metadata 任意指定 unrestricted filesystem destination。

任何 artifact acquisition、cache 或 installation path 都必須有明確 root / containment policy。

Generated user content 仍由既有 GenerationPlan / Filesystem pipeline 管理。

Marketplace installation 不得繞過既有 output policies。

---

## 40. Security Model

Marketplace 初始 security model：

```text
Metadata is untrusted.
Distribution is untrusted until verified.
Installed code is not automatically trusted.
Discovery has no execution side effect.
Compatibility is validated before activation.
Integrity is validated before activation.
Existing Plugin/Generator contracts remain authoritative.
```

---

## 41. Metadata Validation

Validation 至少包含：

```text
schema version
identity
artifact version
artifact type
OPL compatibility
distribution metadata
integrity metadata
```

Invalid metadata 必須 fail explicitly。

不可：

```text
ignore unknown invalid required fields
```

後繼 schema 是否允許 unknown optional fields，應由 schema evolution policy 定義。

---

## 42. Determinism

Marketplace core contracts 必須 deterministic。

相同：

```text
metadata
runtime version
repository state
selection policy
```

應得到相同：

```text
validation result
compatibility result
artifact selection
```

核心 contract 不應依賴：

* current time；
* random selection；
* remote ranking；
* recommendation engine；
* mutable global state。

---

## 43. Network Boundary

Marketplace architecture 可以支援 remote repository，但：

* contract tests 不依賴 network；
* metadata validation 不依賴 network；
* compatibility validation 不依賴 network；
* version comparison 不依賴 network；
* CI 不依賴 public Marketplace availability。

Remote integration tests 應與 core deterministic tests 分離。

---

## 44. Proposed Domain Models

後續 contract implementation 可以評估：

```text
ArtifactType
ArtifactIdentity
ArtifactVersion
ArtifactCoordinate
CompatibilityRequirement
DistributionMetadata
IntegrityMetadata
MarketplaceArtifact
```

初始 implementation 應保持 models：

* immutable；
* side-effect-free；
* provider-independent；
* filesystem-independent；
* network-independent。

---

## 45. Proposed Module Boundary

可能的 production structure：

```text
generator/
└── marketplace/
    ├── __init__.py
    ├── models.py
    ├── validation.py
    ├── compatibility.py
    ├── repository.py
    └── installation.py
```

**此目錄目前只是 architecture proposal。**

Step 7.1 不應因本文件而直接建立 production modules。

---

## 46. Public API

Marketplace models 不應自動加入：

```text
generator.sdk
```

Public exposure 必須另外回答：

* third-party authors 是否需要直接 import？
* compatibility commitment 是什麼？
* versioning policy 是什麼？
* 是否能保持 stable？

在完成 public API review 前，Marketplace contracts 應視為 internal application contracts。

---

## 47. Error Boundary

未來 Marketplace 可能需要：

```text
MarketplaceError
MetadataValidationError
ArtifactNotFoundError
ArtifactVersionError
ArtifactCompatibilityError
ArtifactIntegrityError
ArtifactInstallationError
```

正式 hierarchy 應與既有 OPL error architecture 對齊。

不應將：

```text
ValueError
KeyError
HTTPError
PackageManager-specific exception
```

直接暴露成 Marketplace public contract。

---

## 48. Failure Semantics

Marketplace failure 應遵守：

```text
Validate before side effect.
Acquire before activate.
Verify before trust.
Fail explicitly.
Preserve original cause.
Avoid partial installation when practical.
```

對不可避免的 partial failure，必須提供結構化結果或清楚 cleanup semantics。

---

## 49. Caching

Artifact cache 屬於未來 optimization。

初始 Marketplace contract 不應依賴 cache 才能正確運作。

若加入 cache，必須：

* key by immutable coordinate/integrity；
* verify cached content；
* define invalidation；
* avoid treating stale metadata as authoritative。

---

## 50. Lock File

Marketplace lock file 可以支援 reproducibility，但不是 Step 7.1 必要 implementation。

未來可能記錄：

```text
artifact coordinate
resolved version
integrity digest
distribution reference
```

Lock semantics 應以獨立 ADR 定義。

---

## 51. CLI

Marketplace CLI 尚未定義。

未來可能包括：

```text
opl marketplace search
opl marketplace show
opl marketplace install
opl marketplace update
opl marketplace remove
```

但 Step 7.1 不建立 CLI contract。

CLI 只能在 Marketplace application contracts 穩定後設計。

---

## 52. Testing Strategy

Marketplace 測試分層：

```text
Model Tests
    ↓
Metadata Contract Tests
    ↓
Compatibility Tests
    ↓
Integrity Tests
    ↓
Repository Tests
    ↓
Installation Integration Tests
    ↓
Representative Marketplace E2E
```

---

## 53. Contract Tests

第一個 implementation step 應優先建立：

```text
tests/marketplace/test_artifact_contract.py
```

最低 coverage：

* valid artifact metadata；
* invalid identity；
* invalid version；
* unknown artifact type；
* invalid compatibility requirement；
* malformed distribution metadata；
* malformed integrity metadata；
* immutable models；
* deterministic equality / serialization behavior；
* duplicate coordinate rejection。

---

## 54. Compatibility Tests

至少測：

```text
supported runtime
unsupported runtime
boundary version
invalid requirement
exact version
range requirement
```

Compatibility tests 不得依賴 installed OPL package version 的偶然狀態。

應明確傳入 runtime version。

---

## 55. Integrity Tests

至少測：

```text
valid SHA-256
invalid digest format
digest mismatch
unsupported algorithm
same content → same digest
changed content → mismatch
```

不需要 network。

---

## 56. Repository Tests

Repository contract tests 使用 local deterministic fixtures。

驗證：

* lookup by identity；
* lookup exact version；
* available versions；
* artifact not found；
* duplicate coordinate；
* deterministic ordering。

---

## 57. Installation Tests

Installation integration tests 必須驗證：

* validation occurs before install；
* incompatible artifact causes no activation；
* integrity mismatch causes no activation；
* Plugin installation still passes existing Plugin validation；
* installation does not execute Generator；
* installation does not modify generated courseware；
* failure cleanup behavior。

---

## 58. Representative E2E

Milestone 7 最終應具有 deterministic representative E2E：

```text
Local Marketplace Repository
        ↓
Discover Artifact
        ↓
Select Exact Version
        ↓
Validate Metadata
        ↓
Validate Compatibility
        ↓
Acquire Fixture Distribution
        ↓
Verify Integrity
        ↓
Install
        ↓
Existing Plugin Discovery
        ↓
Existing Plugin Validation
        ↓
Existing Generator Lifecycle
        ↓
Deterministic Output
```

核心 acceptance E2E 不應依賴 public Internet。

---

## 59. Documentation Strategy

Marketplace implementation 應同步：

```text
docs/architecture/marketplace.md
docs/adr/0023-marketplace-artifact-contract.md
docs/adr/README.md
docs/roadmap.md
```

後續 implementation 視需要更新：

```text
docs/reference/marketplace.md
docs/HISTORY.md
CHANGELOG.md
README.md
docs/development/*
```

---

## 60. Implementation Phases

### Phase 1 — Architecture and Artifact Contract

* Marketplace architecture；
* ADR 0023；
* ADR index；
* roadmap alignment。

### Phase 2 — Artifact Contract Tests

* identity；
* version；
* type；
* compatibility；
* distribution metadata；
* integrity metadata。

### Phase 3 — Artifact Models

實作最小 immutable Marketplace domain models。

### Phase 4 — Repository Contract

建立 deterministic local repository / index abstraction。

### Phase 5 — Integrity and Acquisition

建立 package acquisition 與 checksum validation boundary。

### Phase 6 — Installation Integration

與既有 Plugin / Generator distribution architecture 整合。

### Phase 7 — Template Packages

建立 versioned Template Package semantics。

### Phase 8 — Representative E2E

驗證完整 Marketplace → existing OPL execution path。

### Phase 9 — Documentation and Acceptance

完成 Milestone 7 acceptance evidence。

---

## 61. Architectural Invariants

Milestone 7 必須保護：

### Distribution Boundary

* Marketplace distributes capabilities。
* Marketplace 不建立第二套 execution lifecycle。
* Discovery 不執行 artifact。
* Installation 不等於 activation。

### Generator Boundary

* canonical Generator lifecycle 不變。
* Marketplace 不建立 Marketplace-specific Generator API。
* Existing Generator validation remains authoritative。

### Plugin Boundary

* Plugin SDK remains canonical。
* Entry Point discovery remains canonical。
* Plugin validation cannot be bypassed。
* Registry preflight / transactional registration remain canonical。

### Security Boundary

* Metadata is untrusted input。
* Integrity verification does not imply trust。
* Third-party code is not automatically safe。
* Validation occurs before activation。

### Testing Boundary

* Core tests require no network。
* Core tests require no public Marketplace。
* Fixtures are deterministic。
* Remote Marketplace availability cannot become CI dependency。

---

## 62. Current Limitations

截至 Milestone 7 Step 7.1 design：

以下屬於 architecture proposal，而非 implemented capability：

* `MarketplaceArtifact` production model；
* artifact metadata schema；
* Marketplace repository；
* artifact discovery；
* compatibility resolver；
* integrity verifier；
* Marketplace installer；
* Template Package distribution；
* Marketplace CLI；
* Community Repository；
* Marketplace lock file；
* package cache；
* remote Marketplace service；
* ratings / reviews；
* signing / publisher identity；
* sandbox；
* automatic dependency resolution。

現有 production capability 仍以既有 Generator、Plugin、Courseware、AI 與 Filesystem contracts 為準。

---

## 63. Marketplace Architecture Code Review Checklist

### Architecture

* [ ] Marketplace 只負責 distribution / discovery / installation concerns。
* [ ] 沒有建立第二套 Generator lifecycle。
* [ ] Existing Plugin SDK remains canonical。
* [ ] Existing Entry Point discovery remains canonical。
* [ ] Courseware Domain boundary 未被 Marketplace 繞過。
* [ ] AI boundary 未被 Marketplace 擴張。
* [ ] Filesystem ownership 清楚。
* [ ] Dependency direction 清楚。

### Artifact Contract

* [ ] Artifact identity 與 display metadata 分離。
* [ ] Identity policy deterministic。
* [ ] Version contract 明確。
* [ ] Artifact type 明確。
* [ ] Artifact coordinate immutable。
* [ ] Schema version 與 artifact version 分離。
* [ ] Duplicate coordinate semantics 明確。

### Compatibility

* [ ] OPL compatibility 可在 side effect 前驗證。
* [ ] Compatibility 不依賴 network。
* [ ] Incompatible artifact 明確失敗。
* [ ] Marketplace 沒有重新實作 general dependency solver。

### Distribution and Integrity

* [ ] Distribution location 與 identity 分離。
* [ ] Integrity metadata 明確。
* [ ] Integrity verification 發生於 activation 前。
* [ ] Checksum 不被描述成 trust guarantee。
* [ ] Discovery 不產生 installation side effect。
* [ ] Installation 不自動 execution。

### Security

* [ ] Third-party metadata 視為 untrusted。
* [ ] Third-party package content 視為 untrusted。
* [ ] Plugin validation 不被 Marketplace metadata 取代。
* [ ] Path / filesystem boundary 已評估。
* [ ] Remote data 不成為 implicit authority。
* [ ] 不宣稱提供 sandbox。

### Tests

* [ ] Artifact identity validation 有測試策略。
* [ ] Version validation 有測試策略。
* [ ] Type validation 有測試策略。
* [ ] Compatibility 有測試策略。
* [ ] Integrity 有測試策略。
* [ ] Duplicate coordinate 有測試策略。
* [ ] Repository determinism 有測試策略。
* [ ] Installation failure / cleanup 有測試策略。
* [ ] Core tests 不需要 network。
* [ ] Representative E2E strategy 已定義。

### Documentation and Automation

* [ ] Marketplace architecture 已更新。
* [ ] ADR 0023 已同步。
* [ ] ADR index 已同步。
* [ ] Roadmap 已同步。
* [ ] 尚未實作能力明確標為 Proposed。
* [ ] Production API 未因 design PR 被提前擴張。
* [ ] `git diff --check` 通過。
* [ ] `pre-commit run --all-files` 通過。
* [ ] `python -m pytest` 通過。
* [ ] Coverage 不低於 repository policy。

---

## 64. Related Documents

* [Architecture Overview](overview.md)
* [Generator Architecture](generator.md)
* [Plugin Ecosystem](plugin-ecosystem.md)
* [Open Courseware Platform](open-courseware-platform.md)
* [AI Integration](ai-integration.md)
* [Roadmap](../roadmap.md)
* [ADR Index](../adr/README.md)
* [ADR 0010 — Plugin SDK Public Contract](../adr/0010-plugin-sdk-public-contract.md)
* [ADR 0011 — Plugin Validation Contract](../adr/0011-plugin-validation-contract.md)
* [ADR 0012 — Plugin Entry-Point Contract](../adr/0012-plugin-entry-point-contract.md)
* [ADR 0013 — Plugin Distribution Contract](../adr/0013-plugin-distribution-contract.md)
* [ADR 0023 — Marketplace Artifact Contract](../adr/0023-marketplace-artifact-contract.md)

---

## 65. Summary

Marketplace 的核心不是建立另一個執行框架，而是把既有 OPL capability 轉化為可以安全分發與組合的 ecosystem artifacts。

完整責任鏈：

```text
Publisher
    ↓
Marketplace Artifact
    ↓
Metadata Validation
    ↓
Repository Discovery
    ↓
Compatibility Validation
    ↓
Artifact Acquisition
    ↓
Integrity Verification
    ↓
Installation
    ↓
Existing OPL Contract
    ↓
Existing Execution Pipeline
```

Milestone 7 的核心 invariant：

> **Marketplace distributes. Contracts validate. Existing OPL pipelines execute.**
