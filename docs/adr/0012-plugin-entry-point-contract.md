# ADR 0012: Plugin Entry Point Contract

* **Status:** Proposed
* **Date:** 2026-08-10
* **Decision owners:** OpenProjectLab maintainers
* **Milestone:** 4 — Plugin Ecosystem / Plugin SDK
* **Related ADRs:** 0002, 0005, 0006, 0007, 0008, 0009, 0010, 0011
* **Related architecture:** `docs/architecture/plugin-sdk-contract-inventory.md`, `docs/architecture/sdk.md`

## Context

OpenProjectLab（OPL）Milestone 4 已建立 Public Plugin SDK、Plugin validation boundary、transactional loading semantics，以及明確的 Registry preflight query contract。

目前已完成的主要演進為：

```text
Plugin SDK public contract
        │
        ▼
module-based loading pipeline
        │
        ▼
plugin validation contract
        │
        ▼
validate-all-before-register
        │
        ▼
registry preflight boundary
```

ADR 0010 已決定正式第三方 Plugin distribution mechanism 應採 Python package Entry Points，group 為：

```text
openprojectlab.generators
```

並決定 Entry Point 必須 resolve 成：

```text
type[BaseGenerator]
```

ADR 0011 進一步建立集中 validation boundary：

```python
validate_plugin_generator(candidate)
```

所有第三方 Generator 在進入 Registry 前都必須通過相同 validation contract，包括：

* candidate 必須是 class；
* candidate 必須繼承 `BaseGenerator`；
* 不得是 `BaseGenerator` 本身；
* 不得是 abstract class；
* public Generator name 必須合法；
* 必須符合 zero-argument construction contract；
* contract violation 透過 `PluginError` 回報。

目前新的 runtime path 已存在：

```text
generator/plugins/discovery.py
generator/plugins/validation.py
generator/plugins/loader.py
generator/plugins/registry.py
generator/sdk/
```

目前 module-based transitional flow 為：

```text
module name
    │
    ▼
discover_generators()
    │
    ▼
validate all
    │
    ▼
preflight all
    │
    ▼
register all
```

此流程已建立重要的 transaction semantics：

```text
failure before registry mutation
```

並避免：

```text
partial registration
```

然而，正式第三方 Python distribution 尚未接上新的 Plugin runtime。

Repository 仍存在較早期：

```text
generator/core/plugin.py
```

其中 `PluginManager` 已使用：

```python
importlib.metadata.entry_points()
```

以及：

```text
openprojectlab.generators
```

但其 loading contract 與目前新的 Registry / validation architecture 不一致。

舊 flow 概念上為：

```text
entry_points(group=...)
    │
    ▼
EntryPoint.load()
    │
    ▼
registry.register(ep.name, ep.load())
```

而新的 Registry contract 為：

```python
registry.register(generator_class)
```

registration identity 來自：

```python
generator_class.name
```

此外，舊 `PluginManager.load_into()` 以 broad exception handling 包住每個 Entry Point，並逐一 mutation Registry，因此沒有完整套用：

* ADR 0011 validation；
* Entry Point name / Generator name identity check；
* validate-all-before-register；
* preflight-all-before-register；
* transaction-level no-partial-registration semantics。

因此 Milestone 4 需要建立正式的 Python Entry Point Contract，將 packaging metadata discovery 與新的 Plugin runtime 收斂成單一路徑。

---

## Decision

OPL Plugin SDK v1 正式使用 Python package Entry Points 作為第三方 Generator Plugin 的 distribution discovery contract。

固定 Entry Point group：

```text
openprojectlab.generators
```

每個 Entry Point 必須代表一個 Generator Plugin，並 resolve 成：

```text
type[BaseGenerator]
```

正式 loading pipeline：

```text
Installed Python distributions
            │
            ▼
importlib.metadata.entry_points()
            │
            ▼
group = "openprojectlab.generators"
            │
            ▼
EntryPoint metadata
            │
            ▼
EntryPoint.load()
            │
            ▼
loaded candidate
            │
            ▼
validate_plugin_generator()
            │
            ▼
validated Generator class
            │
            ▼
verify entry_point.name == generator.name
            │
            ▼
preflight ALL registrations
            │
            ▼
register ALL
```

任何 Entry Point contract violation 必須在 Registry mutation 前失敗。

Entry Point loading transaction 不得留下 partial registration。

---

## 1. Canonical Entry Point Group

Plugin SDK v1 固定使用：

```text
openprojectlab.generators
```

Plugin package 應透過 Python packaging metadata 宣告：

```toml
[project.entry-points."openprojectlab.generators"]
example-plugin = "opl_example:ExampleGenerator"
```

此 group name 屬於 Plugin SDK compatibility surface。

改變 group name 視為 potentially breaking change，必須：

1. 建立 ADR；
2. 提供 migration strategy；
3. 更新 contract tests；
4. 更新 Plugin author documentation；
5. 依 compatibility policy 提供適當 transition。

Host runtime 不應同時建立多個 undocumented alias group。

---

## 2. One Entry Point Represents One Generator Class

Plugin SDK v1 採：

```text
one Entry Point
    ↓
one Generator class
```

`EntryPoint.load()` 必須直接 resolve 成：

```text
type[BaseGenerator]
```

合法：

```toml
[project.entry-points."openprojectlab.generators"]
example-plugin = "opl_example:ExampleGenerator"
```

其中：

```python
class ExampleGenerator(BaseGenerator):
    name = "example-plugin"
```

不合法的 Entry Point target 包括：

```text
Generator instance
factory function
module object
arbitrary callable
arbitrary object
```

例如以下 v1 不支援：

```toml
example-plugin = "opl_example:create_generator"
```

即使 `create_generator()` 最終可以建立 Generator，也不符合 v1 Entry Point object contract。

Factory-based construction 若未來有 dependency injection 或 lifecycle 需求，應另行設計。

---

## 3. Entry Point Name Is the Public Plugin Identity

Entry Point metadata name 必須與 Generator class 的 public name 一致：

```text
entry_point.name == generator_class.name
```

例如：

```toml
[project.entry-points."openprojectlab.generators"]
java-course = "opl_java:JavaCourseGenerator"
```

必須對應：

```python
class JavaCourseGenerator(BaseGenerator):
    name = "java-course"
```

以下不合法：

```text
Entry Point name: java
Generator name: java-course
```

Mismatch 必須產生：

```text
PluginError
```

且必須發生在 Registry mutation 前。

此規則確保：

* packaging metadata；
* runtime Registry；
* CLI diagnostics；
* Plugin author documentation；
* future Plugin listing；

共享同一個 public identity。

Host 不應 silent-normalize、rename 或選擇其中一個名稱覆蓋另一個名稱。

---

## 4. Entry Point Name Uses the Generator Naming Contract

ADR 0011 已建立 Generator public naming rule：

```text
^[a-z][a-z0-9-]*$
```

Entry Point name 與 `generator_class.name` 必須一致，因此正式 Plugin Entry Point name 也必須符合相同 naming contract。

合法：

```text
example
example-plugin
course2
java-course
```

不合法：

```text
Example
example_plugin
example.plugin
example plugin
../example
```

Entry Point integration 不得建立第二套 normalization rule。

Name validation 應重用既有 Plugin validation contract，而 Entry Point integration 只額外驗證：

```text
metadata identity == runtime identity
```

---

## 5. Entry Point Discovery Is Metadata Discovery

Entry Point discovery 的責任是：

```text
find installed Plugin declarations
```

不是：

```text
validate Generator behavior
register Generator
execute Generator
```

建議 responsibility split：

```text
Entry Point Discovery
    │
    └── returns EntryPoint metadata

Entry Point Loading
    │
    └── EntryPoint.load()

Plugin Validation
    │
    └── validates loaded candidate

Registration Preflight
    │
    └── verifies transaction can commit

GeneratorRegistry
    │
    └── stores validated Generator classes
```

不得把全部責任重新集中到單一 legacy `PluginManager` method。

---

## 6. Use `importlib.metadata`

正式 implementation 必須使用 Python standard library：

```python
from importlib.metadata import entry_points
```

不新增第三方 Plugin discovery dependency。

概念 discovery：

```python
entry_points(group="openprojectlab.generators")
```

Implementation 可以因支援的 Python version 採等效 API shape，但 observable contract 必須一致。

Entry Point ordering 不應被視為 Public SDK semantic guarantee，除非後續 ADR 明確定義。

Plugin correctness 不得依賴 metadata discovery order。

---

## 7. Loaded Candidates Reuse the Existing Validator

Entry Point integration 不得重新實作：

```text
is class
BaseGenerator subclass
not BaseGenerator
concrete
valid generator name
zero-argument construction
```

所有 loaded candidates 必須經：

```python
validate_plugin_generator(candidate)
```

因此正式 dependency：

```text
EntryPoint.load()
        │
        ▼
validate_plugin_generator()
        │
        ▼
Entry Point identity validation
        │
        ▼
registration preflight
```

這確保 transitional module loading 與正式 Entry Point loading 共用相同 Generator contract。

---

## 8. Entry Point Identity Validation Is a Separate Check

Standalone Generator validator 不應知道 Python packaging metadata。

因此：

```python
validate_plugin_generator(candidate)
```

不應增加 `EntryPoint` parameter。

Entry Point-specific identity check 應位於 Entry Point integration boundary，例如概念 API：

```python
def validate_entry_point_identity(
    entry_point_name: str,
    generator_class: type[BaseGenerator],
) -> None:
    ...
```

或由 Entry Point loader 內部等效邏輯完成。

其唯一責任是確認：

```text
entry_point_name == generator_class.name
```

不要把 packaging concerns 放入 generic Plugin Generator validator。

---

## 9. Loading Is Transactional at the Discovery Batch Boundary

正式 Entry Point loading 必須延續 ADR 0011 與目前 loader 已建立的：

```text
validate all
preflight all
register all
```

如果一次 discovery batch 找到：

```text
plugin-a
plugin-b
plugin-c
```

則不得：

```text
load A → register A
load B → register B
load C → fail
```

留下：

```text
A registered
B registered
C failed
```

正式 transaction flow：

```text
discover all matching Entry Points
        │
        ▼
load all candidates
        │
        ▼
validate all candidates
        │
        ▼
validate all metadata identities
        │
        ▼
preflight all names
        │
        ▼
register all
```

任何 pre-commit phase failure：

```text
Registry remains unchanged
```

---

## 10. Entry Point Load Failure Must Not Partially Register

`EntryPoint.load()` 可能因：

* module import failure；
* missing attribute；
* broken package installation；
* import-time exception；
* incompatible dependency；

而失敗。

若任何 Entry Point load 失敗，整個 loading transaction 必須在 Registry mutation 前停止。

已成功 load 的其他 candidates 不得因此先被註冊。

這項規則讓：

```text
load failure
validation failure
identity failure
preflight failure
```

共享同一 transaction guarantee：

```text
no partial registration
```

---

## 11. Duplicate Names Must Fail Before Registration

可能發生兩種 collision。

### 11.1 Duplicate Names Within the Discovered Batch

例如兩個 distributions 都宣告：

```text
example-plugin
```

必須在 Registry mutation 前 deterministic failure。

### 11.2 Collision With Existing Registry State

若 Registry 已有：

```text
example-plugin
```

新的 Entry Point 不得覆寫。

正式 preflight 必須在任何 batch registration 前完成。

Registry 仍是 runtime name ownership 的 authoritative store。

Entry Point loader 不得 silent overwrite。

---

## 12. Existing Registry State Must Be Preserved

Entry Point loading failure 不得：

* 移除既有 registration；
* 替換既有 registration；
* 留下部分新 registration；
* 改變既有 class identity。

例如：

```text
Registry before:
    built-in-a
    plugin-existing
```

若新 discovery batch 失敗：

```text
Registry after:
    built-in-a
    plugin-existing
```

必須保持等價。

---

## 13. `PluginError` Is the Plugin-Facing Error Boundary

預期的 Entry Point contract violation 應透過：

```text
PluginError
```

回報，包括：

* Entry Point target 不是合法 Generator class；
* Generator validation failure；
* Entry Point name 與 Generator name mismatch；
* duplicate Plugin name；
* collision with existing Registry；
* 可分類的 Entry Point loading failure。

底層例外應保留 chaining：

```python
raise PluginError(...) from exc
```

但 implementation 不應 broad-catch 整個 transaction：

```python
except Exception:
    raise PluginError(...)
```

並把 framework programming errors 全部偽裝成 Plugin contract violation。

Exception translation 必須靠近可理解其語意的 boundary。

---

## 14. Error Diagnostics Should Identify the Entry Point

Entry Point-related `PluginError` 應盡可能包含足以診斷的 identity，例如：

```text
entry point name
entry point value/object path
distribution identity when available
```

但完整 error message wording 不屬於 stable compatibility contract。

Tests 應優先驗證：

```text
exception type
transaction semantics
relevant identity fragment
```

而不是固定整句英文。

---

## 15. Distribution Identity Is Diagnostic in v1

Plugin SDK v1 不使用 Python distribution name 作為 Registry key。

Registry identity 仍是：

```text
generator_class.name
```

Entry Point name 必須與之相同。

Distribution metadata 可以用於：

* diagnostics；
* future Plugin listing；
* debugging；
* compatibility reporting。

但 v1 不引入：

```text
distribution:generator
vendor.generator
package/generator
```

等 namespace registration model。

若未來 ecosystem 出現大規模 name collision，應另行 ADR 設計 namespacing。

---

## 16. Multiple Entry Points Per Distribution Are Allowed

單一 Python distribution 可以宣告多個 Generator Entry Points：

```toml
[project.entry-points."openprojectlab.generators"]
course-a = "opl_bundle:CourseAGenerator"
course-b = "opl_bundle:CourseBGenerator"
```

每個 Entry Point 都必須獨立滿足：

```text
one Entry Point
    ↓
one Generator class
```

並各自滿足：

```text
entry_point.name == generator_class.name
```

Host 不要求一個 distribution 只能提供一個 Generator。

---

## 17. No Implicit Module Scanning for Installed Plugins

正式 distribution discovery 不採：

```text
scan installed modules
scan package names
inspect arbitrary namespaces
import every package
```

只處理明確宣告在：

```text
openprojectlab.generators
```

group 的 Entry Points。

這避免：

* 不必要 imports；
* unpredictable side effects；
* naming heuristics；
* expensive environment scanning；
* accidental Plugin activation。

---

## 18. Module-Based Loading Becomes Transitional/Internal

目前：

```python
load_plugin(module_name, registry)
```

仍可保留用於：

* internal integration tests；
* development helpers；
* transitional compatibility。

但它不是正式第三方 distribution discovery contract。

Plugin author documentation 應以：

```toml
[project.entry-points."openprojectlab.generators"]
...
```

作為 canonical installation model。

若未來移除 module-based loading，應先確認沒有 public compatibility promise 依賴它。

---

## 19. Legacy `generator.core.plugin.PluginManager`

Repository 目前仍存在：

```text
generator/core/plugin.py
```

其 `PluginManager` 已使用正確的 Entry Point group，但其 Registry interaction 與新的 Plugin architecture 不一致。

本 ADR 決定：

```text
legacy PluginManager must not become the canonical Milestone 4 path
```

新的 Entry Point implementation 應建立在：

```text
generator.plugins
```

runtime boundary 上，並重用：

```text
validate_plugin_generator()
GeneratorRegistry
registry preflight semantics
```

不得修改舊 `PluginManager` 使兩套 architecture 繼續平行演進。

Migration strategy：

1. 新增 canonical Entry Point discovery/loading path 至 `generator.plugins`；
2. 將 runtime callers 遷移到 canonical path；
3. 以 tests 證明新 path 完整涵蓋必要 behavior；
4. 搜尋 legacy `PluginManager` callers；
5. 若無 public compatibility requirement，後續獨立 PR deprecate/remove legacy path；
6. 若存在 compatibility requirement，建立明確 adapter，而不是維護兩套 independent semantics。

Legacy removal 不包含在本 ADR 的第一個 implementation commit。

---

## 20. No Plugin Execution During Discovery or Loading

Entry Point discovery/loading 階段不得呼叫：

```text
BaseGenerator.run()
validate_request()
plan()
execute()
```

Entry Point integration 只負責建立可用 Generator class registrations。

真正 generation lifecycle 仍由 framework 在明確 request 下控制。

因此：

```text
Plugin discovery
≠
Plugin execution
```

---

## 21. Constructor Contract Remains ADR 0011 Responsibility

Entry Point integration 不新增新的 constructor model。

Validated Generator class 仍必須符合 ADR 0011：

```text
zero-argument construction
```

Entry Point loader 不提供：

```text
dependency injection
constructor arguments
factory context
service locator
```

若未來需要 dependency injection，應另行設計 Plugin construction contract。

---

## 22. Public SDK Import Boundary Remains Unchanged

第三方 Plugin implementation 仍應只依賴：

```python
from generator.sdk import ...
```

Entry Point metadata 只指定 Plugin object path，不代表 Plugin 可以依賴：

```text
generator.plugins
generator.core
generator.generators
```

等 internal namespace。

例如 Plugin package：

```python
from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
)
```

仍是 canonical authoring model。

Entry Point integration 不擴大 `generator.sdk` export surface。

---

## 23. Proposed Internal Architecture

本 ADR 不要求 exact module names，但建議 canonical responsibility layout：

```text
generator/plugins/
    discovery.py
    entry_points.py
    loader.py
    registry.py
    validation.py
```

概念 responsibilities：

```text
entry_points.py
    ├── discover installed Entry Points
    ├── load Entry Point candidates
    └── validate Entry Point metadata identity

validation.py
    └── validate Generator class contract

registry.py
    └── store/query Generator registrations

loader.py
    └── orchestrate transactional loading
```

Implementation 可以選擇不同 internal factoring，只要：

* responsibilities 不混亂；
* contract tests 保護 observable behavior；
* 不建立第二套 Registry；
* 不建立第二套 Generator validator；
* 不恢復 legacy `PluginManager` architecture。

---

## 24. Proposed Internal APIs

可能的 internal API：

```python
PLUGIN_ENTRY_POINT_GROUP = "openprojectlab.generators"
```

```python
def discover_plugin_entry_points() -> tuple[EntryPoint, ...]:
    ...
```

```python
def load_entry_point_generators(
    registry: GeneratorRegistry,
) -> tuple[type[BaseGenerator], ...]:
    ...
```

或等效設計。

這些 API 預設為：

```text
internal runtime API
```

不因本 ADR 自動成為：

```text
generator.sdk
```

Public API。

---

## 25. Contract Test Requirements

Implementation 前必須先建立 Entry Point contract tests。

至少涵蓋：

### Discovery

```text
correct group
→ discovered

unrelated group
→ ignored

no matching Entry Points
→ empty result or documented no-op
```

### Loading

```text
valid Entry Point
→ Generator class loaded

Entry Point target is not a class
→ PluginError

Entry Point target is unrelated class
→ PluginError

Entry Point target is abstract Generator
→ PluginError
```

### Identity

```text
entry_point.name == generator.name
→ accepted

entry_point.name != generator.name
→ PluginError
```

### Transaction

```text
all valid
→ all registered

first valid + later invalid
→ PluginError
→ registry unchanged

load failure after earlier successful load
→ PluginError
→ registry unchanged

duplicate names in batch
→ PluginError
→ registry unchanged

collision with existing registry
→ PluginError
→ existing registry unchanged
```

### Lifecycle Isolation

```text
discovery/loading
→ does not call run()
→ does not call plan()
→ does not call execute()
```

---

## 26. Testing Strategy

Tests 應優先 mock/fake：

```text
importlib.metadata EntryPoint behavior
```

而不是要求測試環境真的安裝第三方 wheel。

Unit/contract tests 應能 deterministic 建立：

```text
fake EntryPoint
fake load result
fake load failure
```

至少應有一個較高階 integration test 驗證 Python packaging metadata contract shape，但不應讓大多數 tests 依賴 global environment 中實際安裝的 distributions。

Test isolation 必須避免讀取 developer machine 上任意已安裝 Plugin。

---

## 27. Determinism

Plugin loading correctness 不得依賴：

```text
filesystem ordering
distribution installation ordering
Entry Point enumeration ordering
```

若 diagnostics 或 tests 需要穩定順序，implementation 可以採 deterministic ordering，例如依：

```text
entry_point.name
```

排序。

但排序本身不應改變 collision semantics。

若未來 ordering 會影響 execution precedence，必須另行定義 contract。

---

## 28. Empty Discovery

若環境中沒有：

```text
openprojectlab.generators
```

Entry Points，正式 discovery 應視為正常狀態，而不是 framework failure。

也就是：

```text
no installed third-party plugins
```

應允許 OPL 正常運作。

Entry Point loading API 應回傳空集合或執行 no-op，而不是因為「沒有 Plugin」拋出 `PluginError`。

這與 transitional module loader 的「指定 module 卻找不到 Generator」語意不同。

---

## 29. Security and Trust Boundary

Python Entry Points 指向可執行 Python code。

因此：

```text
EntryPoint.load()
```

會 import third-party package，可能執行 module-level code。

Plugin validation 無法把任意 Python Plugin 變成 sandboxed code。

本 ADR 的 validation contract 提供：

```text
structural compatibility
transactional Registry safety
deterministic identity
```

但不提供：

```text
sandboxing
malware isolation
permission isolation
process isolation
```

Plugin author documentation 應明確指出：

> 安裝並啟用 Python Plugin 等同信任該 Python package 在目前 Python process 中執行程式碼。

若未來需要 untrusted Plugin model，必須採 process/container isolation 等不同 architecture，不能只靠 Entry Point validation。

---

## 30. Compatibility Policy

以下 Entry Point contract 變更視為 potentially breaking：

* 改變 `openprojectlab.generators` group；
* 允許或要求不同 Entry Point target type；
* 改變 Entry Point name / Generator name identity semantics；
* 改變 Plugin naming rule；
* 改變 zero-argument construction requirement；
* 改變 Plugin-facing error boundary；
* 要求 Plugin import internal namespaces。

以下通常可視為 backward-compatible，但仍需測試：

* 改善 diagnostics；
* internal module refactor；
* discovery implementation refactor；
* deterministic ordering refinement；
* 新增 internal helper；
* legacy `PluginManager` migration/removal，前提是沒有 Public SDK compatibility promise。

---

## Alternatives Considered

### Alternative 1 — Continue Using Module-Name Discovery as the Public Contract

Rejected.

Module-name loading 適合 internal tests 與 transitional development，但不是成熟的 installed Python Plugin discovery mechanism。

Entry Points 提供標準 packaging metadata、明確 opt-in 與 distribution integration。

---

### Alternative 2 — Keep the Legacy `PluginManager` as the Canonical Runtime

Rejected.

Legacy `PluginManager` 的 Registry call shape、validation behavior 與 transaction semantics 已不符合目前 Milestone 4 architecture。

讓它繼續成為 canonical path 會重新建立雙軌 Plugin system。

---

### Alternative 3 — Entry Point Resolves to a Factory

Rejected for Plugin SDK v1.

Factory model 可能支援 dependency injection，但會引入新的 construction contract。

目前 `BaseGenerator` + zero-argument construction 已是既定 v1 contract。

---

### Alternative 4 — Entry Point Resolves to a Module and Scans It

Rejected.

這會把正式 Entry Point path 再導回 module scanning，造成：

```text
one Entry Point
→ unknown number of Generators
```

並模糊 packaging metadata identity。

v1 採：

```text
one Entry Point
→ one Generator class
```

---

### Alternative 5 — Allow Entry Point Name to Differ From Generator Name

Rejected.

這會造成 packaging identity 與 runtime identity 分裂，並使 CLI、Registry、diagnostics 與文件需要決定使用哪一個名稱。

---

### Alternative 6 — Register Each Entry Point Immediately After Loading

Rejected.

這會在後續 Entry Point failure 時留下 partial registration，破壞 ADR 0011 已建立的 transaction semantics。

---

### Alternative 7 — Catch Every Exception and Convert to `PluginError`

Rejected.

Broad exception translation 會隱藏 framework bugs，降低 debugging quality。

只應在明確 Plugin boundary 將可分類 failure 轉換為 `PluginError`。

---

## Consequences

### Positive

* 第三方 Plugin 有正式、標準化的 Python packaging discovery mechanism。
* `generator.sdk`、Entry Point metadata 與 Registry identity 使用一致 contract。
* module-based transitional loading 與 Entry Point loading 共用同一 validator。
* Entry Point loading 延續 no-partial-registration transaction semantics。
* legacy `PluginManager` 不再主導新 architecture。
* 未來 Plugin author documentation 可以提供穩定的 `pyproject.toml` 範例。
* Plugin discovery 不需要掃描 arbitrary installed modules。
* Plugin contract tests 可以明確保護 packaging/runtime boundary。

### Negative

* Entry Point integration 會增加 metadata-specific tests。
* loading transaction 需要先 load/validate/preflight 全部 candidates，不能邊 discover 邊 register。
* Entry Point name 與 Generator name 必須同步維護。
* Python Plugin 仍是 trusted in-process code，不提供 sandbox。
* legacy PluginManager 仍需後續 migration/removal 工作。

### Neutral

* `generator.sdk` public symbol surface 不因本 ADR 擴大。
* `BaseGenerator` canonical lifecycle 不變。
* `GenerationPlan` / `GenerationResult` contract 不變。
* Registry storage model不需因 Entry Point integration 改變。
* module-based loader 可以暫時保留作為 internal helper。

---

## Implementation Plan

### Phase 1 — Contract Tests

新增 Entry Point contract tests，先建立 Red baseline。

建議：

```text
tests/plugins/test_plugin_entry_point_contract.py
```

測試：

* group filtering；
* empty discovery；
* valid Entry Point loading；
* invalid loaded object；
* name mismatch；
* load failure；
* lifecycle isolation。

---

### Phase 2 — Entry Point Discovery Boundary

在：

```text
generator/plugins/
```

建立 canonical metadata discovery helper。

建議：

```text
generator/plugins/entry_points.py
```

責任僅限：

```text
discover EntryPoint metadata
load candidate
validate metadata identity
```

不得建立第二套 Registry。

---

### Phase 3 — Transactional Entry Point Integration

建立或擴充 orchestration，使：

```text
discover all
load all
validate all
identity-check all
preflight all
register all
```

成為正式 Entry Point loading pipeline。

新增：

```text
tests/plugins/test_plugin_entry_point_integration.py
```

保護 no-partial-registration semantics。

---

### Phase 4 — Legacy Migration

搜尋：

```text
PluginManager
generator.core.plugin
```

所有 runtime callers。

將正式 runtime 遷移至：

```text
generator.plugins
```

canonical path。

Legacy removal/deprecation 使用獨立 PR。

---

### Phase 5 — Documentation

更新：

```text
docs/architecture/sdk.md
docs/architecture/plugin-sdk-contract-inventory.md
docs/adr/README.md
docs/roadmap.md
CHANGELOG.md
```

新增 Plugin author packaging example：

```toml
[project.entry-points."openprojectlab.generators"]
example-plugin = "opl_example:ExampleGenerator"
```

並明確要求 Plugin implementation 從：

```text
generator.sdk
```

import public contract。

---

## Rollback Plan

如果 Plugin Entry Point integration 在實作或整合期間造成不可接受的 regression，rollback 應以保持既有 Plugin runtime 穩定為優先。

### Before Entry Point Integration Is Released

若 Entry Point implementation 尚未成為正式 release 的 Public SDK behavior：

1. revert Entry Point integration implementation；
2. 保留 ADR 0012 作為 architecture decision history；
3. 將 ADR 0012 狀態維持或恢復為 `Proposed`；
4. 保留目前已穩定的 module-based loading pipeline；
5. 保留 ADR 0011 validation contract；
6. 保留 transactional registry preflight semantics；
7. 不恢復 legacy `PluginManager` 為 canonical runtime。

Rollback 後 canonical internal flow 仍為：

```text
module name
    │
    ▼
discover_generators()
    │
    ▼
validate all
    │
    ▼
preflight all
    │
    ▼
register all
```

### After Entry Point Integration Becomes an Accepted Public Contract

若 Entry Point integration 已正式 release 並成為 Plugin SDK compatibility surface，不得直接移除：

```text
openprojectlab.generators
```

Entry Point support。

此時 rollback 必須視為 compatibility migration，而不是單純 code revert。

至少必須：

1. 建立新的 ADR 說明 replacement architecture；
2. 將 ADR 0012 標示為 `Superseded`，而不是刪除；
3. 提供 Plugin author migration path；
4. 保留必要 compatibility adapter 或 deprecation period；
5. 更新 contract tests；
6. 更新 Plugin author documentation；
7. 依版本策略處理 breaking change。

### Components That Must Survive Rollback

Entry Point integration rollback 不應撤銷已獨立成立的 Milestone 4 contracts：

```text
generator.sdk public contract
Plugin validation contract
validate-all-before-register semantics
GeneratorRegistry preflight semantics
BaseGenerator canonical lifecycle
```

特別是不得因 Entry Point implementation rollback 而重新導入：

```text
unvalidated registration
partial registration
legacy generator lifecycle
third-party imports from internal namespaces
```

### Rollback Verification

Rollback 後至少必須重新執行：

```text
Plugin SDK contract tests
Plugin validation contract tests
Plugin loading integration tests
Plugin registry contract tests
full pytest suite
Ruff
pre-commit
```

並確認：

```text
existing module-based Plugin loading remains operational
Registry transaction semantics remain intact
no Public SDK exports are accidentally removed
legacy PluginManager does not become the canonical runtime
```

---

## Code Review Checklist

### Architecture

- [ ] `openprojectlab.generators` 是唯一 canonical Entry Point group。
- [ ] one Entry Point resolves to one `type[BaseGenerator]`。
- [ ] Entry Point loading 重用 `validate_plugin_generator()`。
- [ ] Entry Point-specific metadata validation 不污染 generic Generator validator。
- [ ] 不建立第二套 Registry。
- [ ] 不讓 legacy `PluginManager` 成為新 canonical path。
- [ ] module-based loading 明確保持 transitional/internal。

### Identity

- [ ] `entry_point.name == generator_class.name`。
- [ ] 不 silent-normalize Entry Point identity。
- [ ] duplicate Entry Point names 在 mutation 前失敗。
- [ ] existing Registry collision 在 mutation 前失敗。

### Transaction Safety

- [ ] discover/load/validate/preflight 完成後才開始 registration。
- [ ] load failure 不留下 partial registration。
- [ ] validation failure 不留下 partial registration。
- [ ] identity mismatch 不留下 partial registration。
- [ ] duplicate failure 不留下 partial registration。
- [ ] existing Registry state 在 failure 後保持不變。

### Error Boundary

- [ ] 預期 Plugin contract violation 使用 `PluginError`。
- [ ] 可分類底層錯誤保留 exception chaining。
- [ ] 不 broad-catch 整個 transaction。
- [ ] diagnostics 能識別出問題 Entry Point。

### Lifecycle

- [ ] discovery 不呼叫 Generator lifecycle。
- [ ] loading 不呼叫 `run()`。
- [ ] loading 不呼叫 `plan()`。
- [ ] loading 不呼叫 `execute()`。
- [ ] zero-argument construction contract 仍由 ADR 0011 validator 管理。

### Testing

- [ ] contract tests 先於 implementation。
- [ ] tests 不依賴 developer machine 任意已安裝 Plugin。
- [ ] empty discovery 有測試。
- [ ] valid Entry Point 有測試。
- [ ] invalid object 有測試。
- [ ] identity mismatch 有測試。
- [ ] load failure transaction 有測試。
- [ ] duplicate transaction 有測試。
- [ ] existing Registry preservation 有測試。
- [ ] existing module loader regression tests 保持 Green。
- [ ] full pytest suite 通過。
- [ ] Ruff / formatting / pre-commit 通過。

### Documentation

- [ ] ADR index 更新。
- [ ] SDK architecture 更新。
- [ ] Plugin contract inventory 更新。
- [ ] roadmap 更新。
- [ ] changelog 更新。
- [ ] Plugin author Entry Point example 更新。

---

## Acceptance Criteria

本 ADR implementation 完成時，必須能證明：

```text
Installed Python Plugin distribution
        │
        ▼
openprojectlab.generators Entry Point
        │
        ▼
EntryPoint.load()
        │
        ▼
type[BaseGenerator]
        │
        ▼
shared Plugin validation
        │
        ▼
metadata/runtime identity validation
        │
        ▼
transactional registry preflight
        │
        ▼
registration
```

並滿足：

1. 沒有第三方 Plugin 時 OPL 正常運作；
2. 合法 Plugin 可以透過 Entry Point 被發現與註冊；
3. invalid target 在 Registry mutation 前失敗；
4. Entry Point name mismatch 在 Registry mutation 前失敗；
5. 任一 batch failure 不留下 partial registration；
6. existing Registry state 在 failure 後保持不變；
7. Plugin loading 不執行 Generator lifecycle；
8. Plugin author 只需依賴 `generator.sdk`；
9. legacy `PluginManager` 不再是 canonical Milestone 4 runtime path；
10. contract、tests、implementation 與 documentation 保持同步。

---

## Follow-up

本 ADR 接受後，下一個工程步驟為：

```text
tests/plugins/test_plugin_entry_point_contract.py
```

先建立 Entry Point contract 的 Red tests，再實作：

```text
generator/plugins/entry_points.py
```

之後才進入 transactional Entry Point integration。

不應在 contract tests 建立前直接修改 legacy `PluginManager` 或新增 production Entry Point loading code。
