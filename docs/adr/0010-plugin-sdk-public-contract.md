# ADR 0010: Plugin SDK Public Contract

* **Status:** Proposed
* **Date:** 2026-08-09
* **Decision owners:** OpenProjectLab maintainers
* **Milestone:** 4 — Plugin Ecosystem / Plugin SDK
* **Related ADRs:** 0003, 0005, 0006, 0007, 0008, 0009
* **Related architecture:** `docs/architecture/plugin-sdk-contract-inventory.md`, `docs/architecture/sdk.md`

## Context

OpenProjectLab（OPL）在 Milestone 3 已完成 Generator canonical lifecycle 的建立與 legacy lifecycle 的移除。

目前 Generator lifecycle 為：

```text
GenerateRequest
      │
      ▼
BaseGenerator.run()
      │
      ├── validate_request(request)
      │
      ├── plan(request)
      │       │
      │       ▼
      │  GenerationPlan
      │
      └── execute(request, plan)
              │
              ▼
       GenerationResult
```

`BaseGenerator.run()` 由 framework 控制。

Concrete Generator 的 extension points 為：

```text
validate_request()
plan()
execute()
```

Milestone 4 不重新設計這些 contracts，而是決定第三方 Plugin 應如何透過穩定的 Public SDK 使用它們。

目前 Repository 已存在：

```text
generator.sdk
generator.core.plugin.PluginManager
generator.core.registry.GeneratorRegistry
```

並已使用 Python package metadata Entry Points：

```text
openprojectlab.generators
```

進行 Plugin discovery。

但是目前 Public SDK boundary 不完整。

`generator.sdk` 目前只公開：

```python
from generator.sdk import BaseGenerator, GeneratorState
```

然而 `BaseGenerator` 的 public lifecycle signatures 又直接使用：

```text
GenerateRequest
GenerationPlan
GenerationResult
```

而這些型別目前位於：

```text
generator.core.models
```

第三方 Plugin 因此無法只依賴 `generator.sdk` 完整實作 Generator lifecycle。

另外，目前 Plugin loading path：

```text
EntryPoint
    │
    ▼
load()
    │
    ▼
GeneratorRegistry.register()
```

缺少明確的 Plugin contract validation boundary。

Registry 又隱含假設 registered generator type 可以透過：

```python
generator_type()
```

無參數建立。

這些 behavior 已存在，但尚未形成穩定的 Public Plugin SDK contract。

因此 Milestone 4 需要正式定義：

* Public SDK import boundary；
* Public lifecycle type surface；
* Plugin Entry Point contract；
* Generator construction contract；
* Plugin validation boundary；
* Public exception boundary；
* compatibility policy；
* internal implementation boundary。

---

## Decision

OPL 將建立一個最小、穩定且可版本化的 Plugin SDK。

第三方 Generator Plugin 的唯一正式 dependency boundary 為：

```text
generator.sdk
```

Plugin authors 不應依賴：

```text
generator.core.*
generator.generators.*
```

作為 Public API。

---

## 1. Public SDK Boundary

正式 Plugin architecture 採用：

```text
Third-Party Plugin
        │
        ▼
   generator.sdk
        │
        ▼
 Stable Contracts
        │
        ▼
 Internal Runtime
```

`generator.sdk` 是 OPL 對第三方 Generator Plugin 提供 compatibility guarantees 的 namespace。

`generator.core` 與 `generator.generators` 保持 implementation namespaces。

內部 implementation 可以繼續被 `generator.sdk` re-export，但第三方程式碼不應依賴 implementation location。

因此：

```python
from generator.sdk import BaseGenerator
```

是 supported usage。

以下不屬於 supported Plugin API：

```python
from generator.generators.base import BaseGenerator
```

即使 internal import 在某個版本仍然可以運作，也不構成 compatibility guarantee。

---

## 2. Public Lifecycle Contract

第一版 Plugin SDK 將公開 canonical lifecycle 所需的完整 type graph。

目標 Public SDK surface：

```python
from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationOperation,
    GenerationPlan,
    GenerationResult,
    GeneratorValidationError,
    PluginError,
    RuntimeOptions,
    WritePolicy,
    WriteResult,
    WriteStatus,
)
```

這些 symbols 的 implementation 可以繼續存在於 internal modules。

本 ADR 決定的是：

```text
stable import path
```

而不是要求立即搬動 implementation source files。

Public compatibility boundary 為：

```text
generator.sdk
```

---

## 3. BaseGenerator Remains the v1 Plugin Contract

Plugin SDK v1 採用 inheritance-based Generator contract。

第三方 Generator 必須繼承：

```python
BaseGenerator
```

並實作 canonical extension points：

```python
validate_request(...)
plan(...)
execute(...)
```

Plugin 不應 override `run()` 來建立另一套 lifecycle。

Canonical lifecycle 繼續由 framework 控制：

```text
run()
 │
 ├── validate_request()
 ├── plan()
 └── execute()
```

Milestone 4 不引入另一套 Generator Protocol 取代 `BaseGenerator`。

未來若有充分 use case 需要 structural typing，可透過新的 ADR 引入 Protocol，而不是在 v1 同時維護兩套 extension models。

---

## 4. Plugin Discovery Uses Python Entry Points

OPL Plugin discovery 繼續使用 Python distribution metadata Entry Points。

正式 Entry Point group：

```text
openprojectlab.generators
```

第三方 Plugin distribution 應在自己的 package metadata 中宣告 Generator。

例如：

```toml
[project.entry-points."openprojectlab.generators"]
example = "opl_example_plugin:ExampleGenerator"
```

其中：

```text
example
```

是 OPL Generator registration name。

而：

```text
opl_example_plugin:ExampleGenerator
```

是 Python Entry Point object reference。

OPL host 使用：

```python
importlib.metadata.entry_points(
    group="openprojectlab.generators"
)
```

進行 discovery。

Plugin loading 使用 Entry Point 的：

```python
entry_point.load()
```

resolve object。

OPL 不建立自訂 filesystem scanning 或 Plugin directory protocol 取代 Python packaging metadata。

---

## 5. Entry Point Object Contract

Plugin SDK v1 規定：

> `openprojectlab.generators` Entry Point 必須 resolve 成 `BaseGenerator` subclass。

例如：

```python
from generator.sdk import BaseGenerator


class ExampleGenerator(BaseGenerator):
    ...
```

第三方 package：

```toml
[project.entry-points."openprojectlab.generators"]
example = "opl_example_plugin:ExampleGenerator"
```

不支援將以下 object 當成 Generator Plugin v1 contract：

```text
module
arbitrary object
pre-created generator instance
unrelated callable
```

Factory-based Plugin contract 不納入 v1。

---

## 6. Construction Contract

Plugin SDK v1 明確採用：

```text
zero-argument construction
```

也就是 loaded Generator class 必須可以：

```python
generator_type()
```

成功建立。

例如：

```python
class ExampleGenerator(BaseGenerator):
    def __init__(self) -> None:
        ...
```

不得要求：

```python
ExampleGenerator(config)
```

或：

```python
ExampleGenerator(service, registry, template_engine)
```

才能建立。

這個決策將目前 `GeneratorRegistry.create()` 的 implicit assumption 升格為 Plugin SDK v1 contract。

這不是永久禁止 dependency injection。

如果未來 Plugin 需要 framework-provided services，應另外設計：

```text
Generator Factory
Plugin Context
Dependency Injection
```

並透過新 ADR 改變 construction contract。

---

## 7. Plugin Contract Validation

Plugin loading 必須在進入 internal Registry 前驗證 Plugin contract。

目標 flow：

```text
Entry Point
    │
    ▼
load()
    │
    ▼
Plugin Contract Validation
    │
    ├── valid entry-point name
    ├── loaded object is a class
    ├── subclass of BaseGenerator
    └── supports zero-argument construction
    │
    ▼
GeneratorRegistry
```

Invalid Plugin 應：

```text
fail early
```

而不是在 execution 階段因 implementation accident 才失敗。

第三方使用者不應需要解讀：

```text
AttributeError
TypeError
KeyError
```

來判斷 Plugin contract violation。

Framework 應轉換成穩定的 Plugin-facing error。

---

## 8. Public Exception Boundary

Plugin SDK v1 正式公開：

```text
GeneratorValidationError
```

作為 Generator request validation contract。

第三方 Generator 可以使用：

```python
from generator.sdk import GeneratorValidationError
```

回報 structured validation failure。

Plugin loading / contract violation 應使用：

```text
PluginError
```

作為 Plugin-facing error boundary。

因此 `PluginError` 屬於 Plugin SDK v1 Public API，
implementation 階段必須將：

```python
PluginError
```

加入 `generator.sdk` public exports。

但是其他 Core exceptions：

```text
ValidationError
GeneratorNotFoundError
ConfigurationError
TemplateError
```

不因本 ADR 自動成為 Plugin SDK Public API。

Public exception surface 維持最小化。

---

## 9. GeneratorState Compatibility

`GeneratorState` 目前已由：

```text
generator.sdk
```

公開。

但是 canonical lifecycle 已不依賴 `GeneratorState` 進行 execution orchestration。

因此本 ADR 決定：

```text
GeneratorState remains temporarily importable
but is not part of the new core Plugin SDK contract.
```

Milestone 4 不立即移除它。

Implementation 階段應：

1. 保留既有 import compatibility；
2. 將其視為 legacy public symbol；
3. 文件中不再推薦新 Plugin 使用；
4. 在正式移除前提供 deprecation period。

若要移除 `GeneratorState`，應遵循 Public API compatibility policy，不得直接破壞既有 import。

---

## 10. Internal Components Remain Internal

以下 components 不納入 Plugin SDK：

```text
PluginManager
GeneratorRegistry
filesystem implementation
template implementation
manifest implementation
configuration loader
CLI implementation
upgrade implementation
internal helpers
```

因此不應建立：

```python
from generator.sdk import PluginManager
from generator.sdk import GeneratorRegistry
```

這些是 host runtime implementation details。

Plugin SDK 的目的不是 re-export 整個 Core。

---

## 11. Write Policy Contract

因為：

```text
RuntimeOptions
    │
    └── WritePolicy

GenerationOperation
    │
    └── WritePolicy
```

`WritePolicy` transitively 位於 canonical lifecycle type graph。

因此 `WritePolicy` 成為 Plugin SDK v1 contract。

目前 values：

```text
CREATE_ONLY
OVERWRITE
SKIP_EXISTING
```

視為 Public API semantics。

Plugin 可以透過 `GenerationOperation` 表達 write intent。

Framework 仍負責實際 filesystem enforcement。

Plugin 不應繞過 framework filesystem behavior 自行實作不同 overwrite semantics。

---

## 12. Result Contract

所有 Plugin Generator 必須回傳共同：

```text
GenerationResult
```

而不是建立 Plugin-specific result type 作為 framework lifecycle output。

Result graph：

```text
GenerationResult
      │
      └── WriteResult
              │
              └── WriteStatus
```

因此：

```text
GenerationResult
WriteResult
WriteStatus
```

均屬於 Public SDK compatibility surface。

目前 `WriteStatus` values：

```text
CREATED
UPDATED
SKIPPED
UNCHANGED
```

視為 Public API semantics。

---

## 13. Compatibility Policy

`generator.sdk` 是 versioned compatibility boundary。

以下變更視為 potentially breaking：

* 移除 public symbol；
* rename public symbol；
* 改變 required lifecycle method signature；
* 改變 Entry Point group；
* 改變 Entry Point object contract；
* 改變 required constructor contract；
* 移除 public dataclass field；
* 改變 public enum value 或既有 semantics；
* 改變 public exception contract；
* 要求 Plugin import internal namespace。

以下通常可以視為 backward-compatible，但仍需測試：

* 新增 optional helper；
* 新增不影響既有 callers 的 optional capability；
* 新增 exception subclass；
* internal implementation refactor；
* 將 existing implementation symbol re-export through `generator.sdk`；
* 新增具有安全 default 的 optional contract extension。

任何 Public SDK breaking change 都必須：

1. 建立 ADR；
2. 提供 migration strategy；
3. 更新 contract tests；
4. 更新 Plugin author documentation；
5. 更新 changelog；
6. 依版本政策處理 deprecation 或 major-version boundary。

---

## 14. Plugin Naming Contract

Entry Point name 是 Plugin Generator 的 registration name。

Host 應套用既有 Generator name normalization semantics。

Plugin authors SHOULD 使用僅包含 ASCII letters、digits、underscores、
dots 與 dashes 的 Entry Point names，以符合 Python packaging
對新 Entry Point names 的建議形式。

空白名稱不得註冊。

重複名稱不得 silently overwrite 已註冊 Generator。

Name collision 必須產生 deterministic failure。

本 ADR 不引入 namespace-qualified Plugin names。

若 Plugin ecosystem 成長後需要：

```text
vendor.generator
distribution:generator
```

等 namespace model，應另行設計。

---

## 15. No Plugin API Version Negotiation in v1

Plugin SDK v1 不新增：

```text
PLUGIN_API_VERSION
SDK_VERSION
capability negotiation
runtime protocol negotiation
```

第一階段 compatibility 由：

```text
OpenProjectLab package version
+
documented generator.sdk contract
```

管理。

這保持 Plugin SDK v1 最小化。

如果未來需要同時支援多個 incompatible Plugin protocols，再透過新的 ADR 引入 explicit API-version negotiation。

---

## Alternatives Considered

### Alternative 1 — Allow Plugins to Import `generator.core`

Rejected.

這會把 internal implementation layout 變成永久 compatibility burden，並阻礙 Core refactoring。

---

### Alternative 2 — Re-export All Core Types

Rejected.

Plugin SDK 應是最小 public boundary，而不是 `generator.core` 的 alias。

---

### Alternative 3 — Introduce a New Generator Protocol Immediately

Rejected for v1.

Milestone 3 已建立成熟的 `BaseGenerator` canonical lifecycle。

現在同時加入 Protocol 會增加兩套 extension models 與 compatibility burden，而沒有已證明的必要性。

---

### Alternative 4 — Entry Point Resolves to Factory Function

Deferred.

Factory contract 對 dependency injection 有長期價值，但目前 runtime 與 Registry 已採 class construction。

Milestone 4 v1 優先穩定現有 semantics。

---

### Alternative 5 — Entry Point Resolves to Generator Instance

Rejected.

Instance-based loading會模糊 lifecycle ownership、state isolation 與 repeated creation semantics。

---

### Alternative 6 — Filesystem Plugin Directory

Rejected.

OPL 已採用 Python package metadata Entry Points。

另建 Plugin directory discovery protocol 會重複 packaging ecosystem 已提供的能力。

---

### Alternative 7 — Immediately Remove GeneratorState

Rejected.

`GeneratorState` 已存在於 Public SDK。

即使它不再是 canonical lifecycle 的必要部分，也不應無 deprecation path 直接移除。

---

## Consequences

### Positive

* 第三方 Plugin 有單一穩定 import boundary。
* Core implementation 可以持續重構。
* Canonical lifecycle contracts 可以被第三方安全使用。
* Plugin discovery 使用 Python packaging standard mechanism。
* Invalid Plugin 可以在 registration 前 fail early。
* Public SDK 可以建立獨立 contract tests。
* Plugin documentation 可以只使用 `generator.sdk`。
* Public API compatibility 可以被 CI 保護。

### Negative

* `generator.sdk` 的 compatibility burden 明顯增加。
* Public dataclass fields 與 enum semantics 未來修改成本提高。
* zero-argument constructor 成為 v1 compatibility constraint。
* `BaseGenerator` inheritance model 在 v1 成為正式 extension contract。
* `GeneratorState` 需要一段 compatibility/deprecation period。

### Neutral

* Core implementation types 不需要立即搬動。
* `generator.sdk` 可以透過 re-export 建立 stable path。
* Entry Point discovery mechanism 本身不需要重寫。

---

## Migration Plan

### Phase 1 — Contract Tests

新增：

```text
tests/sdk/
```

先建立 failing/contract-defining tests，至少涵蓋：

* public imports；
* SDK-only Generator implementation；
* lifecycle type graph；
* Plugin class validation；
* zero-argument construction；
* invalid Plugin rejection；
* internal import independence。

### Phase 2 — SDK Façade

擴充：

```text
generator/sdk/__init__.py
```

以及必要的 façade modules，使正式 Public SDK symbols 都可以從：

```python
generator.sdk
```

取得。

### Phase 3 — Plugin Validation

在：

```text
EntryPoint.load()
```

與：

```text
GeneratorRegistry.register()
```

之間加入 explicit Plugin contract validation。

### Phase 4 — Integration

驗證：

```text
third-party-style distribution
        ↓
entry point
        ↓
discovery
        ↓
validation
        ↓
registration
        ↓
construction
        ↓
canonical generator execution
```

### Phase 5 — Documentation

建立或更新：

```text
docs/architecture/sdk.md
docs/reference/
Plugin author guide
example Plugin
CHANGELOG.md
docs/roadmap.md
```

---

## Test Strategy

### Public Import Tests

驗證：

```python
from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationOperation,
    GenerationPlan,
    GenerationResult,
    GeneratorValidationError,
    RuntimeOptions,
    WritePolicy,
    WriteResult,
    WriteStatus,
)
```

全部成功。

---

### SDK-Only Generator Test

Test Plugin implementation 只能 import：

```text
generator.sdk
```

不得依賴：

```text
generator.core.*
generator.generators.*
```

---

### Lifecycle Contract Test

驗證：

```text
GenerateRequest
      ↓
validate_request
      ↓
GenerationPlan
      ↓
execute
      ↓
GenerationResult
```

對第三方-style Generator 完整成立。

---

### Plugin Validation Tests

至少涵蓋：

* valid `BaseGenerator` subclass；
* non-class object；
* unrelated class；
* invalid constructor；
* duplicate name；
* empty name；
* Entry Point load failure。

---

### Compatibility Tests

`GeneratorState` 在 deprecation period 仍必須可以從既有 SDK path import。

---

### Full Regression

執行：

```text
ruff check
ruff format --check
pytest
pre-commit
```

所有既有 built-in Generator tests 必須維持通過。

---

## Documentation Changes

本 ADR 接受後，後續 implementation 應同步更新：

```text
docs/architecture/sdk.md
docs/architecture/plugin-sdk-contract-inventory.md
docs/reference/
docs/roadmap.md
CHANGELOG.md
```

並建立 Plugin author documentation，至少說明：

* package layout；
* SDK imports；
* `BaseGenerator` implementation；
* Entry Point declaration；
* naming；
* constructor contract；
* validation；
* plan/result semantics；
* compatibility expectations；
* testing recommendations。

---

## Rollback Plan

本 ADR 在 implementation 前可以透過 architecture review 直接修訂或拒絕。

Implementation 開始後，如果 Public SDK façade 發現重大設計問題：

1. 停止新增 Public exports；
2. 保留既有 `BaseGenerator` / `GeneratorState` compatibility；
3. rollback 尚未發布的 façade changes；
4. 保留 Milestone 3 canonical lifecycle；
5. 重新提出 superseding ADR。

不得透過 rollback：

* 恢復 legacy Generator lifecycle；
* 恢復 generator-specific result contracts；
* 破壞已接受的 Milestone 3 contracts。

---

## Code Review Checklist

### Architecture

* [ ] Plugin 只需要依賴 `generator.sdk`。
* [ ] `generator.core` 沒有被宣告為 Public Plugin API。
* [ ] `generator.generators` 沒有被宣告為 Public Plugin API。
* [ ] Milestone 3 canonical lifecycle 維持不變。
* [ ] Public SDK surface 維持最小。
* [ ] Plugin discovery 與 Generator execution responsibilities 分離。

### Public API

* [ ] 所有正式 Public symbols 有 stable `generator.sdk` import path。
* [ ] Public dataclass fields 被視為 compatibility contract。
* [ ] Public enum values 被視為 compatibility contract。
* [ ] Public exceptions 有明確 boundary。
* [ ] 沒有意外 re-export internal implementation types。
* [ ] `GeneratorState` compatibility 有保留。

### Plugin Contract

* [ ] Entry Point group 為 `openprojectlab.generators`。
* [ ] Entry Point resolve 成 `BaseGenerator` subclass。
* [ ] Generator 支援 zero-argument construction。
* [ ] Invalid Plugin 在 Registry 前被拒絕。
* [ ] Duplicate Plugin name deterministic failure。
* [ ] Plugin loading errors 轉成 framework-defined Plugin error。

### Testing

* [ ] 建立 `tests/sdk/`。
* [ ] Public imports 有 contract tests。
* [ ] SDK-only Generator 有 contract test。
* [ ] Entry Point discovery 有 integration test。
* [ ] Invalid Plugin 有 rejection tests。
* [ ] Constructor contract 有測試。
* [ ] GeneratorState compatibility 有測試。
* [ ] Full regression suite 通過。

### Documentation

* [ ] `docs/architecture/sdk.md` 更新。
* [ ] Plugin author guide 建立。
* [ ] Entry Point packaging example 建立。
* [ ] Public API reference 更新。
* [ ] Roadmap 更新。
* [ ] Changelog 更新。

### Quality Gates

* [ ] `git diff --check` 通過。
* [ ] `ruff check` 通過。
* [ ] `ruff format --check` 通過。
* [ ] `pytest` 通過。
* [ ] `pre-commit run --all-files` 通過。

---

## Decision Summary

OPL Plugin SDK v1 採用以下 architecture：

```text
Third-Party Distribution
          │
          │
          │ openprojectlab.generators
          ▼
    Python Entry Point
          │
          ▼
       load()
          │
          ▼
   Contract Validation
          │
          ▼
   BaseGenerator subclass
          │
          │ imports only
          ▼
      generator.sdk
          │
    ┌─────┼─────────┐
    ▼     ▼         ▼
 Request Plan      Result
    │     │         │
    └─────┼─────────┘
          ▼
    Internal Runtime
          │
          ▼
 GeneratorRegistry
```

核心規則：

> Third-party Plugin code depends on `generator.sdk`, not `generator.core` or `generator.generators`.

Plugin discovery 使用：

```text
openprojectlab.generators
```

Python Entry Point group。

Plugin SDK v1 的 Entry Point resolve 成：

```text
BaseGenerator subclass
```

並要求：

```text
zero-argument construction
```

Milestone 4 後續工作必須先建立 Public SDK contract tests，再實作 SDK façade 與 Plugin validation。
