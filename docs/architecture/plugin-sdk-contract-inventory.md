# Plugin SDK Contract Inventory

> Status: Historical Baseline — Milestone 4 Step 1 completed
> Milestone: 4 — Plugin Ecosystem / Plugin SDK
> Step: 1 — Plugin SDK Contract Inventory
> Scope: Existing SDK, generator, plugin, registry, model, exception, packaging, and test contracts
> Audience: Maintainers, Plugin SDK designers, Generator developers, contributors
> Baseline: Repository snapshot after Milestone 3 completion
> Current note: Later Milestone 4 work supersedes several "current" observations below; see the status update section.

OpenProjectLab（OPL）Milestone 4 的第一個工作，是在新增或穩定 Plugin API 之前，盤點目前 Repository 中已經存在的 Generator、SDK 與 Plugin 相關契約。

本文件不是新的 Public API 規格，也不直接決定最終 Plugin SDK surface。

本文件的目的，是建立 Milestone 4 的 architecture baseline，回答：

1. 哪些 Generator contracts 已在 Milestone 3 正式建立？
2. 哪些 symbols 目前已透過 `generator.sdk` 公開？
3. 哪些 internal types 實際位於 Plugin extension type graph？
4. 哪些 Plugin behaviors 已存在，但仍只是 implicit contract？
5. 哪些 Core implementation 應保持 internal？
6. 哪些 public-boundary tests 尚未建立？
7. 哪些問題需要由下一份 ADR 正式決定？

本 Inventory 將作為後續 Plugin SDK ADR、contract tests、SDK façade、Plugin validation 與 Plugin author documentation 的設計基礎。

---


## Milestone 4 Status Update — Entry Point Runtime and Legacy PluginManager

本 Inventory 保留 Milestone 4 Step 1 當時的 repository baseline，因此後續章節中的：

```text
Current
Missing
Gap
Candidate
Deferred
```

描述應理解為歷史盤點，而不是 2026-08-11 的最新 runtime 狀態。

後續 Milestone 4 已完成：

```text
ADR 0010 — Plugin SDK Public Contract
ADR 0011 — Plugin Validation Contract
ADR 0012 — Plugin Entry Point Contract
```

以及 production implementation：

```text
generator/sdk/
generator/plugins/discovery.py
generator/plugins/validation.py
generator/plugins/registry.py
generator/plugins/loader.py
generator/plugins/entry_points.py
```

目前 canonical installed-plugin flow 已是：

```text
Python distribution
    ↓
openprojectlab.generators
    ↓
EntryPoint.load()
    ↓
validate_plugin_generator()
    ↓
entry-point / generator identity check
    ↓
transactional preflight
    ↓
GeneratorRegistry
```

Public SDK contract tests 與 Plugin contract/integration tests 也已建立，因此原 Inventory 中「SDK façade incomplete」、「沒有 tests/sdk」、「沒有 explicit validation boundary」等項目均已由後續工作關閉。

### Legacy PluginManager Inventory Result

Step 4D-3 針對：

```text
generator/core/plugin.py
PluginManager
PluginDescriptor
```

進行 caller inventory。

目前在 OPL production code 與 tests 中，未發現 `generator/core/plugin.py` 之外的 caller。

Canonical replacement 已存在於：

```text
generator.plugins.entry_points
```

且 `PluginManager` / `PluginDescriptor` 不屬於 `generator.sdk` Public API。

因此它們目前分類更新為：

```text
LEGACY INTERNAL IMPLEMENTATION
SUPERSEDED BY CANONICAL ENTRY POINT RUNTIME
REMOVAL CANDIDATE
```

正式移除仍必須先有 architecture/removal tests，並於獨立 PR 完成。

---

## 1. Milestone 3 Baseline

Milestone 4 不重新設計 Milestone 3 已完成的 Generator lifecycle。

目前已建立並由測試保護的核心契約包括：

* `GenerateRequest`
* `RuntimeOptions`
* `GeneratorValidationError`
* `GenerationOperation`
* `GenerationPlan`
* `GenerationResult`
* canonical `BaseGenerator.run()` lifecycle
* legacy `GeneratorContext` lifecycle removal
* built-in generator lifecycle conformance

目前 canonical lifecycle 為：

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

Framework 控制 `run()`。

Concrete Generator 的 extension points 為：

```text
validate_request()
plan()
execute()
```

因此 Milestone 4 的工作不是重新定義 Generator execution lifecycle，而是建立一個穩定的 Plugin-facing boundary，使第三方 Generator 可以依賴這些既有契約，而不必依賴 Core 私有模組。

---

## 2. Current Repository Boundary

目前與 Plugin SDK 最直接相關的 Repository 結構為：

```text
generator/
├── sdk/
│   ├── __init__.py
│   └── generator.py
│
├── generators/
│   ├── base.py
│   ├── bootstrap_generator.py
│   ├── course_generator.py
│   └── week_generator.py
│
└── core/
    ├── models.py
    ├── exceptions.py
    ├── plugin.py
    ├── registry.py
    ├── template.py
    ├── filesystem.py
    └── ...
```

目前存在兩條不同的 extension-related dependency path。

Public SDK path：

```text
Third-Party Code
      │
      ▼
generator.sdk
      │
      ▼
generator.generators.base
```

Plugin discovery path：

```text
Installed Distribution
      │
      │ Python package metadata
      ▼
Entry Point
      │
      ▼
generator.core.plugin.PluginManager
      │
      ▼
generator.core.registry.GeneratorRegistry
      │
      ▼
Generator Type
```

目前兩條路徑都已存在，但尚未形成一個完整、明確且經 public contract tests 保護的 Plugin SDK boundary。

---

## 3. Current SDK Public Surface

目前 `generator.sdk` 正式 re-export：

```python
from generator.sdk import BaseGenerator, GeneratorState
```

`generator/sdk/__init__.py` 的 public surface 為：

```python
__all__ = [
    "BaseGenerator",
    "GeneratorState",
]
```

因此目前實際 Public SDK surface：

| Symbol           | Implementation source       | Exported by SDK | Classification                          |
| ---------------- | --------------------------- | --------------: | --------------------------------------- |
| `BaseGenerator`  | `generator.generators.base` |             Yes | Existing public extension contract      |
| `GeneratorState` | `generator.generators.base` |             Yes | Existing public symbol; review required |

`BaseGenerator` 已是事實上的 external extension point。

但其 method signatures 所使用的 Request、Plan 與 Result types 尚未由 `generator.sdk` 公開。

因此目前 SDK façade 是不完整的。

---

## 4. Canonical Generator Contract

`BaseGenerator` 目前定義：

```python
run(request: GenerateRequest) -> GenerationResult
```

並提供 extension hooks：

```python
validate_request(request: GenerateRequest) -> None
plan(request: GenerateRequest) -> GenerationPlan
execute(
    request: GenerateRequest,
    plan: GenerationPlan,
) -> GenerationResult
```

這表示 Public Generator Contract 實際上不是單一 `BaseGenerator` class。

完整的 lifecycle type graph 至少包含：

```text
BaseGenerator
├── GenerateRequest
├── GenerationPlan
└── GenerationResult
```

而這三個 model 又 transitively reference 其他 types。

因此只公開 `BaseGenerator` 無法形成 self-contained Plugin SDK。

---

## 5. Request Contract Inventory

### 5.1 GenerateRequest

Implementation：

```text
generator/core/models.py
```

目前欄位：

```text
generator_name
target
values
options
```

特性：

* frozen dataclass
* slots
* generator name normalization
* `Path` normalization
* immutable values mapping
* shared by built-in generators
* canonical lifecycle input

Classification：

```text
REQUIRED SDK CONTRACT CANDIDATE
```

原因：

所有第三方 Generator 若實作 canonical lifecycle，都必須接受此 type。

目前 architectural gap 是：

```text
BaseGenerator
    │
    └── public method signature
            │
            ▼
generator.core.models.GenerateRequest
```

也就是 public extension class 的 method signature 指向 internal namespace。

---

### 5.2 RuntimeOptions

Implementation：

```text
generator/core/models.py
```

目前欄位：

```text
dry_run
overwrite
verbose
force
```

並提供：

```text
write_policy
```

因為：

```text
GenerateRequest.options
```

的型別為 `RuntimeOptions`，所以若 `GenerateRequest` 成為 SDK contract，`RuntimeOptions` 已 transitively 位於 public type graph。

Classification：

```text
TRANSITIVE SDK CONTRACT CANDIDATE
```

仍需由 ADR 決定：

* 哪些 runtime flags 屬於 stable Plugin contract；
* Plugin 是否可以依賴 `force`；
* `overwrite` 與 `write_policy` 的責任邊界；
* 未來新增 Runtime Option 是否屬於 backward-compatible change。

---

## 6. Planning Contract Inventory

### 6.1 GenerationPlan

Implementation：

```text
generator/core/models.py
```

目前欄位：

```text
generator_name
operations
```

特性：

* frozen
* immutable operations tuple
* generator name normalization
* duplicate destination rejection
* canonical `plan()` result
* canonical `execute()` input

Classification：

```text
REQUIRED SDK CONTRACT CANDIDATE
```

因為第三方 Generator 的：

```python
plan(...)
```

必須產生 `GenerationPlan`，而：

```python
execute(...)
```

必須接受相同 Plan。

---

### 6.2 GenerationOperation

Implementation：

```text
generator/core/models.py
```

目前欄位：

```text
template_name
destination
context
write_policy
```

它是：

```text
GenerationPlan.operations
```

的 element type。

Classification：

```text
TRANSITIVE SDK CONTRACT CANDIDATE
```

需要後續決定：

* Plugin 是否直接建構 `GenerationOperation`；
* `template_name` 是否形成 Template SDK contract；
* `context: Mapping[str, Any]` 是否適合作為長期 Public API；
* Plugin 是否可以自行指定 `WritePolicy`；
* destination 是否需要更嚴格的 containment contract。

---

### 6.3 WritePolicy

Implementation：

```text
generator/core/models.py
```

目前值：

```text
CREATE_ONLY
OVERWRITE
SKIP_EXISTING
```

使用位置包括：

```text
RuntimeOptions.write_policy
GenerationOperation.write_policy
```

Classification：

```text
TRANSITIVE SDK CONTRACT CANDIDATE
```

一旦公開，enum values 與其 semantics 都應視為 compatibility contract。

---

## 7. Result Contract Inventory

### 7.1 GenerationResult

Implementation：

```text
generator/core/models.py
```

目前欄位：

```text
generator_name
writes
warnings
dry_run
manifest_updated
```

並提供：

```text
created
updated
skipped
unchanged
affected_paths
count()
```

它是 canonical lifecycle 的共同輸出型別。

Classification：

```text
REQUIRED SDK CONTRACT CANDIDATE
```

Milestone 3 已建立 shared `GenerationResult` contract，因此 Milestone 4 不應重新建立 generator-specific result types。

Plugin SDK 應重用此共同契約。

---

### 7.2 WriteResult

Implementation：

```text
generator/core/models.py
```

欄位：

```text
path
status
```

因為：

```text
GenerationResult.writes
```

直接公開 `WriteResult`，它也是 transitive contract。

Classification：

```text
TRANSITIVE SDK CONTRACT CANDIDATE
```

---

### 7.3 WriteStatus

Implementation：

```text
generator/core/models.py
```

目前值：

```text
CREATED
UPDATED
SKIPPED
UNCHANGED
```

使用位置：

```text
WriteResult.status
GenerationResult.count()
GenerationResult.created
GenerationResult.updated
GenerationResult.skipped
GenerationResult.unchanged
```

Classification：

```text
TRANSITIVE SDK CONTRACT CANDIDATE
```

Public SDK 若公開 `WriteResult` 或 `GenerationResult.writes`，就必須處理 `WriteStatus` 的 compatibility semantics。

---

## 8. Current Lifecycle Type Graph

目前完整 lifecycle graph：

```text
BaseGenerator
    │
    ├── run(GenerateRequest)
    │          │
    │          └── RuntimeOptions
    │                  │
    │                  └── WritePolicy
    │
    ├── validate_request(GenerateRequest)
    │
    ├── plan(GenerateRequest)
    │          │
    │          ▼
    │    GenerationPlan
    │          │
    │          └── GenerationOperation
    │                  │
    │                  └── WritePolicy
    │
    └── execute(
            GenerateRequest,
            GenerationPlan,
        )
            │
            ▼
      GenerationResult
            │
            └── WriteResult
                    │
                    └── WriteStatus
```

這是目前最重要的 Inventory 結論之一：

> Public SDK surface 必須依照完整 type graph 設計，而不能只看目前 `generator.sdk.__all__`。

---

## 9. GeneratorState Inventory

`GeneratorState` 目前由：

```python
from generator.sdk import GeneratorState
```

公開。

目前 values：

```text
CREATED
VALIDATED
PREPARED
GENERATED
COMPLETED
FAILED
```

但是 canonical `BaseGenerator.run()` 目前只執行：

```text
validate_request
plan
execute
```

並沒有透過這些 enum values 驅動 lifecycle transition。

因此 `GeneratorState` 存在一個特殊情況：

```text
PUBLIC TODAY
BUT LONG-TERM SDK VALUE NOT YET JUSTIFIED
```

Milestone 4 不應直接移除此 symbol，因為它已經透過 SDK export。

下一份 ADR 應決定：

* 保留為 stable SDK contract；
* deprecate；
* 或重新定義其 lifecycle role。

在 ADR 決策前，Inventory 只記錄現況，不改變 compatibility。

---

## 10. Exception Contract Inventory

目前 exception hierarchy：

```text
OPLGeneratorError
├── ValidationError
│   └── GeneratorValidationError
├── GeneratorNotFoundError
├── ConfigurationError
├── TemplateError
└── PluginError
```

### GeneratorValidationError

目前提供 structured fields：

```text
generator
field
message
```

Milestone 3 已建立 structured generator validation contract。

Classification：

```text
STRONG SDK CONTRACT CANDIDATE
```

第三方 Generator 應能以 framework-defined validation semantics 回報 invalid request，而不是任意拋出不穩定 internal exception。

### PluginError

目前由 `PluginManager` 將 Plugin loading failure 包裝為：

```text
PluginError
```

Classification：

```text
PLUGIN SDK ERROR CANDIDATE
```

但目前 exception message 與 error structure 仍相對簡單。

### Other Exceptions

以下 types 是否需要成為 Plugin SDK public surface，尚未確定：

```text
OPLGeneratorError
ValidationError
GeneratorNotFoundError
ConfigurationError
TemplateError
```

不應因為它們存在於 `generator.core.exceptions` 就自動全部 re-export。

下一份 ADR 應定義最小且穩定的 public exception hierarchy。

---

## 11. Existing Plugin Discovery Contract

目前 Plugin discovery implementation：

```text
generator/core/plugin.py
```

使用：

```python
importlib.metadata.entry_points(...)
```

Entry Point group：

```text
openprojectlab.generators
```

目前 discovery：

```text
entry_points(
    group="openprojectlab.generators"
)
```

並將 metadata 轉成：

```text
PluginDescriptor
├── name
└── object_path
```

目前 loading path：

```text
Entry Point
    │
    ▼
ep.load()
    │
    ▼
registry.register(
    ep.name,
    loaded_object,
)
```

因此 Repository 已經存在一個 implicit Plugin discovery contract。

---

## 12. Packaging Contract Inventory

目前 OPL `pyproject.toml` 宣告：

```toml
[project.scripts]
opl = "generator.cli.main:main"
```

但 OPL host package 本身沒有：

```toml
[project.entry-points."openprojectlab.generators"]
```

這不是 Plugin discovery 缺陷。

Plugin entry points 應由第三方 Plugin distribution 在自己的 package metadata 中宣告。

依目前 runtime implementation，概念上第三方 package 將需要類似：

```toml
[project.entry-points."openprojectlab.generators"]
my-generator = "my_plugin:MyGenerator"
```

這個範例目前只是由現有 loader behavior 推導出的 packaging shape。

正式 syntax、object contract、naming rules 與 compatibility guarantees 必須由後續 ADR 與 Plugin author documentation 定義。

---

## 13. Current Implicit Plugin Contract

根據目前 implementation，一個 Plugin Generator 實際上隱含需要符合：

1. 安裝為 Python distribution；
2. 宣告 `openprojectlab.generators` entry point；
3. entry point 必須具有 name；
4. entry point value 必須可以被 `EntryPoint.load()` 載入；
5. loaded object 必須能交給 `GeneratorRegistry.register()`；
6. registry 後續必須可以建立該 generator。

目前這些要求存在於 runtime behavior 中。

但它們尚未形成：

* Public SDK contract
* typed protocol
* dedicated compatibility tests
* Plugin author reference
* version compatibility policy

因此 Classification：

```text
EXISTING IMPLICIT PLUGIN CONTRACT
```

---

## 14. Registry Contract Inventory

目前：

```text
generator/core/registry.py
```

提供：

```text
register(name, generator_type)
create(name)
names()
```

Registry 會：

```text
strip
↓
lower
↓
validate non-empty
↓
reject duplicate
```

並在 create 時：

```python
return self._items[key]()
```

因此目前存在一個重要 implicit requirement：

```text
REGISTERED GENERATOR TYPE MUST SUPPORT
ZERO-ARGUMENT CONSTRUCTION
```

這個 requirement 目前：

* 沒有型別宣告；
* 沒有 Protocol；
* 沒有 Plugin SDK documentation；
* 沒有 Plugin-specific validation layer。

因此 `GeneratorRegistry` 本身應保持：

```text
INTERNAL IMPLEMENTATION
```

但 zero-argument construction requirement 不應被忽略。

下一份 ADR 必須決定 Plugin entry point 最終代表：

```text
Generator Class
```

或：

```text
Generator Factory
```

或其他明確 descriptor。

不應讓目前 Registry 的 implementation accident 自動成為永久 SDK contract。

---

## 15. PluginDescriptor Inventory

目前：

```text
PluginDescriptor
├── name
└── object_path
```

並使用：

```python
@dataclass(frozen=True, slots=True)
```

目前它只由 internal PluginManager discovery 使用。

Classification：

```text
INTERNAL TODAY
PUBLIC VALUE REQUIRES REVIEW
```

若未來 Plugin author 或 external application 需要 inspection/discovery API，可以考慮建立 public descriptor。

但不應因為現有 class 名稱為 `PluginDescriptor` 就自動公開。

---

## 16. Core Components That Should Remain Internal

Milestone 4 不應把整個 `generator.core` 轉成 SDK。

目前以下 implementation 應預設保持 internal；其中 `PluginManager` 已在後續 Step 4D-3 確認為 legacy removal candidate：

```text
PluginManager  # legacy removal candidate
GeneratorRegistry
filesystem implementation
template implementation
manifest implementation
configuration loader
CLI parser
upgrade implementation
internal helpers
```

目標 dependency direction：

```text
Plugin
  │
  ▼
generator.sdk
  │
  ▼
Stable Contracts
  │
  ▼
Internal Adapters
  │
  ▼
generator.core
```

不應變成：

```text
Plugin
  │
  ▼
generator.core.*
```

---

## 17. Existing Contract Test Coverage

目前 Repository 已有成熟的 Generator contract tests。

重要測試包括：

```text
tests/generators/test_generation_input_contract.py
tests/generators/test_generation_result_contract.py
tests/generators/test_generator_validation_contract.py
tests/generators/test_generator_execution_contract.py
tests/generators/test_legacy_generator_lifecycle_removal.py
tests/generators/test_builtin_generator_lifecycle_contract.py
tests/generators/test_base_generator_lifecycle.py
```

另外：

```text
tests/core/test_models.py
tests/core/test_generation_result.py
tests/core/test_registry.py
```

保護 shared models、result semantics 與 registry behavior。

這些測試是 Milestone 4 的重要 foundation。

但是它們主要驗證：

```text
Internal Contract Correctness
```

而不是：

```text
Public SDK Compatibility Boundary
```

---

## 18. Missing SDK Contract Test Layer

目前 Repository 沒有：

```text
tests/sdk/
```

這是 Milestone 4 最明確的 testing gap 之一。

未來應建立：

```text
tests/
└── sdk/
    ├── test_public_imports.py
    ├── test_generator_contract.py
    ├── test_plugin_generator_contract.py
    └── ...
```

實際檔案名稱由後續 contract-test design 決定。

Public SDK tests 應從 external developer perspective 驗證：

```python
from generator.sdk import ...
```

而不是：

```python
from generator.core import ...
```

---

## 19. Required Future SDK Tests

### 19.1 Public Import Contract

驗證正式 public symbols 可以由：

```python
from generator.sdk import ...
```

取得。

Public compatibility 不應要求第三方知道 internal module layout。

---

### 19.2 SDK-Only Generator Contract

建立 test-only third-party-style Generator。

其 implementation 應只依賴：

```text
generator.sdk
```

並完成：

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

如果 sample Plugin 必須 import：

```text
generator.core.*
```

就代表 SDK boundary 仍不完整。

---

### 19.3 Entry Point Contract

驗證 Plugin discovery 對正式 entry point contract 的支援。

應覆蓋：

* discovery；
* loading；
* registration；
* generator creation；
* canonical execution。

---

### 19.4 Invalid Plugin Rejection

至少應涵蓋：

```text
invalid loaded object
duplicate name
invalid generator name
unsupported construction contract
load failure
contract mismatch
```

外部應收到 framework-defined error，而不是依賴：

```text
AttributeError
TypeError
KeyError
```

等 implementation accident。

---

### 19.5 Internal Boundary Protection

Public Plugin test fixture 不應 import：

```text
generator.core.*
generator.generators.*
```

這可以成為 architecture-level contract test。

---

## 20. Architecture Gaps

### Gap 1 — SDK Façade Is Incomplete

目前：

```text
generator.sdk
```

只公開：

```text
BaseGenerator
GeneratorState
```

但 `BaseGenerator` public signatures 依賴：

```text
GenerateRequest
GenerationPlan
GenerationResult
```

因此 public surface 目前不是 self-contained。

---

### Gap 2 — Public API References Internal Namespace Types

目前：

```text
BaseGenerator
    │
    ▼
generator.core.models
```

這使 Plugin developer 在理解或實作 lifecycle 時需要知道 internal model location。

Milestone 4 應建立 stable SDK import path。

---

### Gap 3 — Plugin Loader Bypasses Explicit SDK Validation

目前：

```text
EntryPoint.load()
      │
      ▼
GeneratorRegistry.register()
```

中間沒有明確 Plugin SDK contract validator。

因此 invalid object 可能直到 registration 或 construction 才失敗。

---

### Gap 4 — Constructor Contract Is Implicit

Registry 目前直接：

```python
generator_type()
```

因此 zero-argument construction 是 implementation-derived requirement。

Milestone 4 必須決定它是否應：

* 正式成為 Plugin contract；
* 改為 factory contract；
* 或由 adapter 隔離。

---

### Gap 5 — GeneratorState Stability Is Unclear

`GeneratorState` 已公開，但 canonical lifecycle 不依賴其 state transition。

因此它增加了 compatibility burden，而目前 Plugin value 不明確。

---

### Gap 6 — Exception Boundary Is Not Defined

目前 Core 有多種 exceptions，但 Plugin developer 應依賴哪些尚未正式定義。

---

### Gap 7 — No Dedicated Public SDK Contract Tests

Internal contract tests 已成熟，但：

```text
tests/sdk/
```

尚不存在。

因此目前沒有獨立 quality gate 防止 SDK public surface 被意外破壞。

---

### Gap 8 — Plugin Packaging Contract Is Undocumented

Runtime 已使用：

```text
openprojectlab.generators
```

但第三方 package：

* 如何宣告 entry point；
* entry point value 指向什麼；
* naming rules；
* constructor/factory rules；
* compatibility requirements；

尚未形成正式 Plugin author contract。

---

## 21. Initial Contract Classification

### Tier A — Strong SDK Candidates

直接或 transitively 位於 canonical Generator lifecycle：

```text
BaseGenerator
GenerateRequest
RuntimeOptions
GenerationPlan
GenerationOperation
GenerationResult
WriteResult
WritePolicy
WriteStatus
GeneratorValidationError
```

這些 types 是下一份 ADR 最重要的 public-surface candidates。

---

### Tier B — Plugin-Specific Candidates

與 Plugin boundary 直接相關，但公開方式仍需設計：

```text
PluginError
PluginDescriptor
Plugin compatibility metadata
Plugin factory / class contract
```

---

### Tier C — Existing Public Symbol Requiring Review

```text
GeneratorState
```

不可在沒有 compatibility decision 的情況下直接移除。

---

### Tier D — Keep Internal by Default

```text
PluginManager
GeneratorRegistry
filesystem implementation
template implementation
configuration implementation
manifest implementation
CLI implementation
upgrade implementation
```

---

## 22. Proposed Target Boundary

Milestone 4 應朝以下 architecture 演進：

```text
Third-Party Plugin Distribution
              │
              │ package metadata
              ▼
       Entry Point Discovery
              │
              ▼
      Plugin Contract Adapter
              │
              ▼
         generator.sdk
              │
      ┌───────┼─────────┐
      ▼       ▼         ▼
   Request   Plan      Result
   Contract Contract   Contract
      │       │         │
      └───────┼─────────┘
              ▼
       BaseGenerator
              │
              ▼
       Internal Runtime
              │
              ▼
      GeneratorRegistry
```

External dependency rule：

```text
Third-Party Plugin → generator.sdk
```

Internal dependency rule：

```text
generator.sdk → stable internal implementation
```

禁止把：

```text
Third-Party Plugin → generator.core.*
```

當成正式 Plugin architecture。

---

## 23. Candidate Minimal SDK Surface

Inventory 階段的 strong candidate surface：

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

Plugin-specific error contract 可能再加入：

```python
from generator.sdk import PluginError
```

但這只是 Inventory candidate。

本文件不正式承諾這些 imports。

正式 Public API 必須由 ADR 決定後，再透過：

```text
Documentation
Contract Tests
__all__
Implementation
Changelog
```

同步建立。

---

## 24. Decisions Already Closed

以下問題已由 Milestone 3 解決，不應在 Milestone 4 重新開放：

### Canonical Lifecycle

```text
validate_request
      ↓
plan
      ↓
execute
```

由 `BaseGenerator.run()` 控制。

### Shared Request Contract

使用：

```text
GenerateRequest
RuntimeOptions
```

### Shared Planning Contract

使用：

```text
GenerationOperation
GenerationPlan
```

### Shared Result Contract

使用：

```text
GenerationResult
```

而不是 generator-specific result types。

### Legacy GeneratorContext Lifecycle

已移除，不應重新引入為 Plugin lifecycle。

Milestone 4 應建立在這些 accepted contracts 之上。

---

## 25. Decisions Deferred to ADR

下一階段仍需正式決定：

1. 哪些 lifecycle model types 正式由 `generator.sdk` re-export？
2. `GeneratorState` 保留、deprecate 或重新定義？
3. Plugin entry point value 指向 Generator class、factory 或其他 object？
4. zero-argument constructor 是否成為 public requirement？
5. 是否需要 Generator Protocol？
6. `BaseGenerator` 是否為唯一 supported Plugin implementation model？
7. `PluginError` 與 public exception hierarchy 如何設計？
8. `PluginDescriptor` 是否需要 public version？
9. Plugin naming rules 為何？
10. Core generator names 與 third-party names 發生衝突時如何處理？
11. Plugin compatibility/version metadata 如何表達？
12. `RuntimeOptions` 哪些 semantics 保證穩定？
13. Plugin 是否可以直接控制 `WritePolicy`？
14. Plugin contract validation 發生在 discovery、load、registration 或 execution 哪一階段？
15. Public API compatibility policy 與 deprecation policy 為何？

這些問題應由：

```text
ADR 0010 — Plugin SDK Public Contract
```

正式處理。

---

## 26. ADR Sequence

目前 ADR index 已使用：

```text
0001
...
0008 — Generator Execution Contract
0009 — Remove Legacy Generator Lifecycle
```

因此下一個 architecture decision 應使用：

```text
0010
```

建議：

```text
docs/adr/0010-plugin-sdk-public-contract.md
```

Inventory 本身不是 ADR。

它提供 ADR 0010 所需的 repository evidence 與 problem statement。

---

## 27. Recommended Milestone 4 Work Sequence

```text
Step 1
Plugin SDK Contract Inventory
        │
        ▼
Step 2
ADR 0010 — Plugin SDK Public Contract
        │
        ▼
Step 3
Public SDK Contract Tests
        │
        ▼
Step 4
SDK Public Façade
        │
        ▼
Step 5
Plugin Contract Validation / Adapter
        │
        ▼
Step 6
Discovery and Registration Integration
        │
        ▼
Step 7
Plugin Author Documentation
        │
        ▼
Step 8
Example Third-Party Plugin
```

這個順序保持：

```text
Design First
Documentation First
Testing First
Automation First
```

---

## 28. Step 1 Exit Criteria

Plugin SDK Contract Inventory 完成條件：

* [x] 確認 Milestone 3 canonical contracts。
* [x] 盤點目前 `generator.sdk` public exports。
* [x] 盤點 BaseGenerator public method type graph。
* [x] 盤點 Request contracts。
* [x] 盤點 Planning contracts。
* [x] 盤點 Result contracts。
* [x] 盤點 Exception contracts。
* [x] 盤點 Plugin discovery behavior。
* [x] 盤點 Entry Point group。
* [x] 盤點 Registry implicit requirements。
* [x] 盤點 packaging boundary。
* [x] 分類 Public candidates 與 Internal implementation。
* [x] 確認既有 Generator contract tests。
* [x] 確認目前沒有 dedicated `tests/sdk/` layer。
* [x] 找出 Plugin SDK architecture gaps。
* [x] 區分 Milestone 3 closed decisions 與 Milestone 4 open decisions。
* [x] 確認下一個 ADR 編號為 0010。

---

## 29. Code Review Checklist

### Architecture

* [ ] Inventory 以目前 Repository behavior 為依據。
* [ ] 沒有把 Proposed API 誤寫成 Existing API。
* [ ] Milestone 3 accepted contracts 沒有被重新設計。
* [ ] Public 與 Internal boundary 有明確區分。
* [ ] Transitive type graph 已納入分析。
* [ ] Plugin discovery 與 Generator lifecycle 被視為不同但相關的 boundaries。
* [ ] Registry implementation 沒有被直接宣告為 Public SDK。

### Compatibility

* [ ] 已記錄目前 `generator.sdk.__all__`。
* [ ] 已識別 `GeneratorState` 為 existing public symbol。
* [ ] 沒有在 ADR 前承諾新的 public import。
* [ ] Public dataclass fields 被視為 potential compatibility surface。
* [ ] Public enum values 被視為 potential compatibility surface。
* [ ] Public exception hierarchy 被視為 potential compatibility surface。
* [ ] Implicit constructor requirement 已記錄。

### Plugin Architecture

* [ ] `openprojectlab.generators` Entry Point group 已記錄。
* [ ] Entry Point discovery behavior 已記錄。
* [ ] Entry Point loading behavior 已記錄。
* [ ] Registry registration behavior 已記錄。
* [ ] Zero-argument construction assumption 已記錄。
* [ ] Plugin packaging contract 沒有被誤認為已正式穩定。

### Testing

* [ ] 既有 Generator contract tests 已盤點。
* [ ] Core model tests 已盤點。
* [ ] Registry tests 已盤點。
* [ ] `tests/sdk/` 缺口已記錄。
* [ ] 後續 SDK-only Plugin contract test 已列入工作。
* [ ] 後續 invalid Plugin rejection tests 已列入工作。

### Documentation

* [ ] 本文件與 `docs/architecture/sdk.md` 的方向一致。
* [ ] 本文件與 `docs/roadmap.md` 的 Milestone 4 方向一致。
* [ ] ADR sequence 與 `docs/adr/README.md` 一致。
* [ ] 下一個重大 Public API decision 將使用 ADR 0010。
* [ ] Plugin author documentation 延後到 contract 決策完成後。

### Automation and Quality

* [ ] `git diff --check` 通過。
* [ ] `pre-commit run --all-files` 通過。
* [ ] `python -m pytest` 通過。
* [ ] Documentation-only change 不意外修改 runtime behavior。

---

## 30. Conclusion

目前 OPL 已具備 Plugin Ecosystem 所需的大部分底層 Generator contracts。

Milestone 4 的主要問題不是缺少 Generator lifecycle，而是：

```text
Stable Core Contracts
        │
        ▼
Incomplete SDK Façade
        │
        ▼
Implicit Plugin Contract
```

因此下一階段的目標不是擴大 Core API，而是建立清楚且最小的 Plugin-facing boundary。

核心原則為：

> Third-party Plugin 應依賴 `generator.sdk`，而不是 `generator.core.*`。

以及：

> 已經存在的 Core implementation behavior，不應在沒有 ADR、contract tests 與 compatibility policy 的情況下，自動升格為永久 Public SDK contract。

本 Inventory 完成後，Milestone 4 下一個工作為：

```text
ADR 0010 — Plugin SDK Public Contract
```

該 ADR 將正式決定 Public SDK surface、Plugin entry contract、construction model、exception boundary、compatibility policy 與 contract validation strategy。
