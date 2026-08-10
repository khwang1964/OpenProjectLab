# ADR 0011: Plugin Validation Contract

* **Status:** Accepted
* **Date:** 2026-08-10
* **Decision owners:** OpenProjectLab maintainers
* **Milestone:** 4 — Plugin Ecosystem / Plugin SDK
* **Related ADRs:** 0002, 0005, 0006, 0007, 0008, 0009, 0010
* **Related architecture:** `docs/architecture/plugin-sdk-contract-inventory.md`, `docs/architecture/sdk.md`

## Context

OpenProjectLab（OPL）Milestone 4 已建立第一版 Public Plugin SDK surface 與基本 Plugin loading pipeline。

目前 canonical Generator lifecycle 為：

```text
GenerateRequest
      │
      ▼
BaseGenerator.run()
      │
      ├── validate_request(request)
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

ADR 0010 已決定 Plugin SDK v1 的主要 public contract：

```text
Third-Party Plugin
        │
        ▼
   generator.sdk
        │
        ▼
 BaseGenerator subclass
```

並進一步決定 Python package Entry Point：

```text
openprojectlab.generators
```

必須 resolve 成：

```text
type[BaseGenerator]
```

且 Plugin Generator 必須支援：

```text
zero-argument construction
```

目前 Repository 已存在：

```text
generator/plugins/discovery.py
generator/plugins/loader.py
generator/plugins/registry.py
generator/sdk/
```

目前 module-based loading flow 為：

```text
module name
    │
    ▼
discover_generators()
    │
    ▼
BaseGenerator subclasses
    │
    ▼
load_plugin()
    │
    ▼
GeneratorRegistry.register()
```

目前 discovery 已能：

* import Plugin module；
* 找出 `BaseGenerator` subclass；
* 排除 `BaseGenerator` 本身；
* 排除 abstract Generator；
* 在沒有可用 Generator 時拋出 `PluginError`。

目前 Registry 已能：

* 依 `generator_class.name` 註冊；
* 拒絕 duplicate name；
* 對不存在的 registration name 拋出 `PluginError`。

然而，這些行為仍不足以構成完整 Plugin validation contract。

目前尚缺少獨立且明確的 validation boundary，用來驗證：

* loaded object 是否真的是 class；
* loaded class 是否為 `BaseGenerator` subclass；
* loaded class 是否就是禁止註冊的 `BaseGenerator` 本身；
* loaded class 是否為 abstract class；
* public Generator name 是否有效；
* class 是否能以 zero-argument construction 建立；
* contract violation 是否一致轉換為 `PluginError`；
* validation 是否在 Registry mutation 前完成。

如果沒有集中 validation boundary，contract rules 會分散在 discovery、loader、registry 與未來 Entry Point integration 中。

這會造成：

* 相同 Plugin 在不同 loading path 得到不同結果；
* invalid Plugin 可能直到 execution 或 instance creation 才失敗；
* internal `TypeError`、`AttributeError` 或 `KeyError` 洩漏成 Plugin-facing behavior；
* Registry 可能收到尚未驗證的 class；
* Entry Point integration 需要重新實作相同規則；
* SDK compatibility contract 難以透過單一 test suite 保護。

因此 Milestone 4 下一步需要建立正式的 Plugin Validation Contract。

---

## Decision

OPL 將建立單一、集中且可測試的 Plugin Generator validation boundary。

所有第三方 Generator 在進入 runtime Registry 前，必須先通過相同 validation contract。

目標 flow：

```text
Plugin Source
    │
    ├── transitional module discovery
    │
    └── Python Entry Point
            │
            ▼
       loaded object
            │
            ▼
  Plugin Generator Validation
            │
            ├── class
            ├── BaseGenerator subclass
            ├── not BaseGenerator itself
            ├── concrete
            ├── valid public name
            └── zero-argument construction
            │
            ▼
     Validated Generator Class
            │
            ▼
     GeneratorRegistry.register()
```

Validation failure 必須：

```text
fail before registry mutation
```

並透過：

```text
PluginError
```

形成穩定的 Plugin-facing error boundary。

---

## 1. Validation Boundary

Plugin validation 必須是一個獨立責任，不應只存在於 discovery filtering 或 Registry side effects 中。

建議 internal API：

```python
def validate_plugin_generator(
    candidate: object,
) -> type[BaseGenerator]:
    ...
```

成功時回傳同一個 validated Generator class：

```python
validated = validate_plugin_generator(candidate)
assert validated is candidate
```

失敗時拋出：

```python
PluginError
```

這個 function 屬於 host runtime implementation detail。

它不因本 ADR 自動成為：

```text
generator.sdk
```

public API。

第三方 Plugin author 應依賴公開 contract，而不是呼叫 framework internal validator。

---

## 2. Candidate Must Be a Class

Plugin Generator candidate 必須是 Python class。

合法：

```python
class ExampleGenerator(BaseGenerator):
    ...
```

不合法：

```python
ExampleGenerator()
```

不合法：

```python
def create_generator():
    ...
```

不合法：

```python
plugin = object()
```

因此 validator 必須先確認：

```python
inspect.isclass(candidate)
```

或等效行為。

若 candidate 不是 class，必須拋出 `PluginError`，而不是讓後續 `issubclass()` 產生未分類 `TypeError`。

---

## 3. Candidate Must Subclass BaseGenerator

Plugin SDK v1 採 inheritance-based contract。

因此 candidate 必須滿足：

```python
issubclass(candidate, BaseGenerator)
```

不採用純 duck typing：

```python
class LooksLikeGenerator:
    def plan(self, request): ...
    def execute(self, request, plan): ...
```

即使 method shape 相同，若未繼承 `BaseGenerator`，仍不符合 Plugin SDK v1 contract。

這與 ADR 0010 保持一致。

---

## 4. BaseGenerator Itself Is Not a Plugin

以下不合法：

```python
candidate is BaseGenerator
```

`BaseGenerator` 是 framework extension contract，不是可註冊的 concrete Plugin Generator。

Validator 必須明確拒絕它。

這項規則不得只依賴 abstract-class detection 的偶然結果。

原因是 framework 未來可能改變 `BaseGenerator` abstract method shape，但 `BaseGenerator` 本身仍不應成為 Plugin registration target。

---

## 5. Plugin Generator Must Be Concrete

Abstract Generator 不得註冊。

例如：

```python
class AbstractPluginGenerator(BaseGenerator):
    pass
```

由於尚未實作：

```text
plan()
execute()
```

它仍是 abstract class。

Validator 必須使用：

```python
inspect.isabstract(candidate)
```

或等效 mechanism 拒絕 abstract Generator。

這讓 failure 發生在 Plugin loading 階段，而不是 instance construction 階段。

---

## 6. Public Generator Name Contract

每個 Plugin Generator 必須提供穩定的 public registration name：

```python
class ExampleGenerator(BaseGenerator):
    name = "example-plugin"
```

Plugin validation 必須確認 `name`：

* 是 `str`；
* 去除前後空白後仍非空；
* 等於其 normalized form；
* 符合 OPL public Generator naming rule。

Plugin SDK v1 採用以下 naming rule：

```text
^[a-z][a-z0-9-]*$
```

合法範例：

```text
example
example-plugin
course2
java-course
```

不合法範例：

```text
Example
 example
example
example_plugin
example.plugin
week generator
../week
--example
```

Validator 不應自動將 invalid name 改寫成另一個 name。

也就是：

```text
validation, not silent normalization
```

如果未來需要更寬鬆的 Python Entry Point naming compatibility，應透過新的 ADR 修改此 rule，而不是在不同 loading path 進行不同 normalization。

---

## 7. Entry Point Name and Generator Name

ADR 0010 定義 Python Entry Point name 是 Generator registration name。

因此正式 Entry Point integration 必須檢查：

```text
entry_point.name == generator_class.name
```

例如：

```toml
[project.entry-points."openprojectlab.generators"]
example-plugin = "opl_example:ExampleGenerator"
```

對應：

```python
class ExampleGenerator(BaseGenerator):
    name = "example-plugin"
```

若兩者不同：

```text
Entry Point name: example
Generator.name: example-plugin
```

應視為 Plugin contract violation。

原因：

* 避免同一 Generator 出現兩個 public identity；
* Registry lookup name 保持決定性；
* packaging metadata 與 runtime behavior 一致；
* CLI、文件與 diagnostics 使用同一名稱。

目前 module-based loader 尚沒有 Entry Point object，因此此項檢查在 Entry Point integration phase 才會套用。

---

## 8. Zero-Argument Construction Contract

ADR 0010 已決定 Plugin SDK v1 使用：

```text
zero-argument construction
```

因此 validated Generator class 必須能成功執行：

```python
generator_class()
```

以下不符合 v1 contract：

```python
class InvalidGenerator(BaseGenerator):
    def __init__(self, config):
        ...
```

Validation 必須在 registration 前確認 construction contract。

建議 behavior：

```python
try:
    generator_class()
except TypeError as exc:
    raise PluginError(...) from exc
```

但 validator 不應 broad-catch：

```python
except Exception:
```

並把所有 constructor bug 都錯誤分類成 signature violation。

Implementation 應區分：

1. 無法以 zero arguments 呼叫的 constructor contract violation；
2. constructor 本身執行後產生的未預期 bug。

優先策略應是先檢查 callable signature，在不執行 Plugin side effects 的情況下驗證 zero-argument compatibility。

如果 Python signature 無法可靠判斷，implementation 可以在明確測試保護下使用 construction probe。

此細節屬於 implementation choice，但 observable contract 必須一致。

---

## 9. Constructor Side Effects Are Discouraged

因為 Plugin SDK v1 要求 framework 能建立 Generator instance，Plugin constructor 應保持輕量。

Plugin `__init__()` 不應：

* 寫入 filesystem；
* 存取 network；
* 啟動 subprocess；
* 修改 global state；
* 自動執行 generation；
* 讀取 secret；
* 進行昂貴 discovery。

真正工作應發生在 framework-controlled lifecycle：

```text
validate_request()
plan()
execute()
```

本 ADR 不將「constructor 完全無 side effect」設計為可自動驗證 contract，因為 runtime 無法可靠證明。

但它是 Plugin authoring requirement，後續文件必須明確說明。

---

## 10. Validation Must Precede Registry Mutation

Loader 不得：

```text
register first
validate later
```

正式順序必須是：

```text
load/discover
    ↓
validate
    ↓
register
```

若 validation 失敗：

```text
Registry state remains unchanged
```

對單一 Plugin loading transaction，至少必須保證 invalid candidate 不會被加入 Registry。

如果一次 Plugin source 暴露多個 Generator，implementation 必須避免：

```text
first generator registered
second generator invalid
registry left partially mutated
```

因此 multi-generator module loading 應採：

```text
discover all
    ↓
validate all
    ↓
register all
```

而不是逐個：

```text
discover → validate → register
```

後者可能造成 partial registration。

---

## 11. Duplicate Registration Remains a Registry Responsibility

Validation 與 Registry uniqueness 是兩個不同 contract。

Validator 負責單一 Generator class 的合法性。

Registry 負責 runtime state 中：

```text
name uniqueness
```

因此 duplicate name 仍由：

```text
GeneratorRegistry.register()
```

拒絕。

不應要求 standalone validator 知道整個 Registry state。

目標 responsibility split：

```text
Plugin Validator
    └── Is this generator class valid?

Generator Registry
    └── Can this valid generator be registered here?
```

---

## 12. PluginError Is the Validation Error Boundary

所有預期的 Plugin contract violation 必須透過：

```text
PluginError
```

回報。

例如：

* candidate 不是 class；
* candidate 不是 `BaseGenerator` subclass；
* candidate 是 `BaseGenerator`；
* candidate 是 abstract；
* `name` 無效；
* zero-argument construction contract 不成立；
* Entry Point name 與 Generator name 不一致。

底層預期例外應保留 chaining：

```python
raise PluginError(...) from exc
```

但未預期 framework/programming bugs 不應全部被轉換成 `PluginError`。

例如：

```text
AssertionError
unexpected AttributeError
internal RuntimeError
```

若不是已定義 contract violation，應保留原始錯誤讓測試與 traceback 暴露問題。

---

## 13. Error Messages Are Diagnostic, Not the Stable Contract

測試與 caller 不應依賴完整 `PluginError` 文字。

不建議：

```python
assert str(exc) == "Invalid plugin generator"
```

建議：

```python
with pytest.raises(PluginError):
    ...
```

若需要檢查 diagnostics，可驗證必要關鍵資訊：

```python
assert "example-plugin" in str(exc_info.value)
```

Public compatibility contract 是：

```text
exception type + validation semantics
```

而不是永久固定的英文句子。

未來若需要 machine-readable Plugin error code，應另外設計 structured error metadata。

---

## 14. Discovery and Validation Are Separate Responsibilities

`discover_generators()` 的責任是：

```text
find candidates
```

`validate_plugin_generator()` 的責任是：

```text
prove candidate satisfies Plugin SDK v1 contract
```

現有 discovery 已使用 `BaseGenerator`、abstract-class filtering，因此目前部分 validation behavior 與 discovery 重疊。

Implementation migration 可以逐步調整，但最終應避免同一 rule 在多處獨立實作。

目標 dependency：

```text
Discovery
    ↓
Candidate(s)
    ↓
Validator
    ↓
Validated Generator Class(es)
```

Entry Point loading 也必須重用同一 validator：

```text
EntryPoint.load()
    ↓
Candidate
    ↓
Validator
```

這確保 module-based transitional loading 與正式 Entry Point loading 使用相同 contract。

---

## 15. Module Discovery Is Transitional

目前：

```python
load_plugin(module_name, registry)
```

使用 importable module name 進行 integration testing 與基礎 loading。

ADR 0010 已決定正式 Plugin discovery mechanism 為 Python package metadata Entry Points。

因此本 ADR 不將：

```text
module name scanning
```

升格為 Plugin SDK public distribution contract。

Module-based discovery 可以：

* 保留作為 internal helper；
* 保留作為測試工具；
* 在 Entry Point integration 完成後重新評估是否保留。

正式 external Plugin distribution contract 仍是：

```text
openprojectlab.generators
```

Entry Point group。

---

## 16. Registry Must Receive Only Validated Generator Classes

`GeneratorRegistry` 是 host runtime component，不是 Public SDK。

Registry 可以維持 defensive checks，例如 duplicate name。

但正常 loader path 必須保證：

```text
only validated classes reach register()
```

這讓 Registry 不需要逐步成長為另一個 Plugin validator。

若未來有人直接呼叫 internal Registry API，該行為不構成第三方 Plugin SDK guarantee。

---

## 17. Public SDK Imports Remain the Plugin Author Boundary

第三方 Plugin tests 與 examples 應使用：

```python
from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
    GeneratorValidationError,
)
```

不得要求 Plugin author import：

```python
from generator.plugins.validation import validate_plugin_generator
```

也不得要求：

```python
from generator.core.exceptions import PluginError
```

來實作正常 Generator lifecycle。

`PluginError` 是 host/plugin loading public error boundary；是否要求第三方 Plugin author 主動 raise `PluginError`，不由本 ADR 擴大。

Plugin request validation 仍應使用：

```text
GeneratorValidationError
```

---

## 18. Validation Does Not Execute the Generator Lifecycle

Plugin validation 不應呼叫：

```text
run()
validate_request()
plan()
execute()
```

來判斷 Plugin 是否有效。

原因：

* validation 沒有合法 `GenerateRequest`；
* lifecycle 可能觸發 filesystem behavior；
* Plugin validity 不應依賴某一組 runtime request；
* contract validation 與 functional testing 是不同責任。

Validation 只檢查 Plugin class-level / construction-level contract。

Generator functional correctness 由 Generator tests 與 integration tests 負責。

---

## 19. Validation Result Is the Original Class

第一版不建立：

```text
ValidatedPlugin
ValidatedGeneratorDescriptor
PluginMetadata wrapper
```

作為新的 public data model。

Validator 成功時直接回傳：

```text
type[BaseGenerator]
```

原因：

* 保持 Milestone 4 scope 小；
* 不新增尚未需要的 metadata abstraction；
* Registry 目前已以 class 為儲存單位；
* Entry Point contract 也已定義 resolve 成 class。

若未來需要：

* Plugin version；
* capability flags；
* dependency metadata；
* compatibility ranges；
* distribution identity；

再透過新的 ADR 引入 Plugin descriptor model。

---

## Alternatives Considered

### Alternative 1 — Keep Validation Inside Discovery

做法：

```text
discover_generators()
```

同時負責 import、candidate filtering、contract validation。

拒絕原因：

* Entry Point loading 無法自然重用；
* discovery 與 validation responsibility 混合；
* Registry path 仍可能繞過 validation；
* unit tests 難以直接測試單一 candidate contract。

---

### Alternative 2 — Put All Validation in GeneratorRegistry.register()

做法：Registry 同時驗證 class、name、abstract、constructor 與 uniqueness。

拒絕原因：

* Registry responsibility 過大；
* Entry Point diagnostics 與 source metadata 不容易加入；
* validation 與 state mutation 耦合；
* 容易留下 partial mutation；
* standalone contract tests 不清楚。

Registry 可以保留 defensive checks，但不作為主要 validation boundary。

---

### Alternative 3 — Validate Only at Instance Creation

做法：先註冊 class，直到：

```python
generator_class()
```

才發現錯誤。

拒絕原因：

* fail too late；
* invalid Plugin 已污染 Registry；
* startup/discovery 可能看似成功；
* error source 距離真正 contract violation 太遠。

---

### Alternative 4 — Duck-Typed Plugin Contract

只要 object 提供 `plan()` / `execute()` 就接受。

拒絕原因：

* 與 ADR 0010 inheritance-based v1 contract 衝突；
* framework-controlled `run()` lifecycle 無法保證；
* type surface 與 public compatibility boundary變得模糊。

---

### Alternative 5 — Factory-Based Construction

Entry Point resolve 成 factory：

```python
def create_generator(context): ...
```

拒絕原因：

* ADR 0010 已決定 v1 為 class + zero-argument construction；
* 需要新的 dependency injection / Plugin context contract；
* 超出目前 Milestone 4 scope。

未來若 Plugin 需要 host services，可以用新 ADR 引入。

---

## Consequences

### Positive

* Plugin validation rules 有單一 canonical implementation boundary。
* Module-based 與 Entry Point loading 可以共用相同 validator。
* Invalid Plugin 在 Registry mutation 前 fail early。
* Plugin-facing failures 使用穩定 `PluginError`。
* Public SDK contract 更容易用 tests 保護。
* Entry Point integration 不需要重新設計 validation semantics。
* Registry responsibility 保持集中在 registration state 與 uniqueness。
* Zero-argument construction 從隱含 assumption 變成可測試 contract。
* Generator public name 成為明確 contract。

### Negative

* Loader path 增加一個 validation step。
* Existing tests 需要重新分層成 discovery、validation、registration、integration。
* 現有 discovery filtering 與新的 validator 在 migration 期間可能短暫重疊。
* Name rule 會拒絕部分原本 Python 技術上可表示的 names。
* Zero-argument constructor 限制 Plugin dependency injection 能力。

### Risks

* 若 constructor validation 直接 instantiate Plugin，可能觸發 Plugin side effects。
* 若 signature inspection 實作過度嚴格，可能錯誤拒絕合法 class。
* 若 multi-generator loading 逐一 register，validation failure 可能造成 partial Registry state。
* 若 Entry Point name 與 `Generator.name` identity rule 未同步測試，可能出現 packaging/runtime drift。

這些風險必須由 implementation tests 保護。

---

## Migration Plan

### Phase 1 — ADR and Contract Definition

建立本 ADR，正式定義：

* validation boundary；
* candidate type contract；
* concrete subclass requirement；
* naming rule；
* zero-argument construction；
* `PluginError` boundary；
* validate-before-register ordering。

此 phase 不修改 runtime behavior。

---

### Phase 2 — Validation Contract Tests

先建立 failing tests，例如：

```text
tests/plugins/test_plugin_validation_contract.py
```

至少涵蓋：

* valid concrete Generator；
* non-class candidate；
* unrelated class；
* `BaseGenerator` itself；
* abstract Generator；
* empty name；
* whitespace name；
* uppercase name；
* underscore/dot/path-like invalid name；
* valid dashed name；
* zero-argument construction compatible；
* required constructor argument rejected；
* `PluginError` type；
* exception chaining where applicable。

Tests 應先定義 observable contract，再進入 implementation。

---

### Phase 3 — Validator Implementation

建立 internal validator，例如：

```text
generator/plugins/validation.py
```

提供：

```python
validate_plugin_generator(...)
```

實作應保持：

* pure contract checking where possible；
* no Registry mutation；
* no Generator lifecycle execution；
* narrow exception handling；
* deterministic behavior。

---

### Phase 4 — Loader Integration

更新：

```text
generator/plugins/loader.py
```

使 flow 成為：

```text
discover all
    ↓
validate all
    ↓
register all
```

並加入 regression tests，確認 invalid multi-generator Plugin 不造成 partial registration。

---

### Phase 5 — Entry Point Integration

建立或整合正式：

```text
importlib.metadata.entry_points(
    group="openprojectlab.generators"
)
```

loading path。

每個 Entry Point：

```text
entry_point.load()
    ↓
validate_plugin_generator()
    ↓
entry_point.name identity check
    ↓
register()
```

並移除或封裝與此 contract 重複的 legacy loading behavior。

---

### Phase 6 — Documentation Alignment

同步更新：

```text
docs/architecture/sdk.md
docs/architecture/plugin-sdk-contract-inventory.md
docs/reference/errors.md
docs/roadmap.md
CHANGELOG.md
```

若建立正式 Plugin author guide，應新增：

* naming examples；
* constructor rules；
* Entry Point declaration；
* validation failure examples；
* supported imports。

---

## Test Strategy

Plugin validation 必須使用 layered tests。

### Unit Contract Tests

直接測試：

```python
validate_plugin_generator(candidate)
```

不需要 import module 或建立 Entry Point distribution。

這些 tests 保護單一 candidate semantics。

---

### Loader Integration Tests

驗證：

```text
Discovery
    ↓
Validation
    ↓
Registry
```

至少測試：

* valid Plugin 被註冊；
* invalid Plugin 不被註冊；
* duplicate name 保持 Registry error；
* multi-generator validation failure 不留下 partial registration；
* discovery/import failure 保留 `PluginError` contract。

---

### Entry Point Integration Tests

正式 Entry Point phase 應測試：

* group `openprojectlab.generators`；
* Entry Point load valid class；
* Entry Point load non-class；
* Entry Point load unrelated class；
* Entry Point name 與 `Generator.name` mismatch；
* duplicate Entry Point registration；
* load failure chaining；
* valid third-party package style import 只依賴 `generator.sdk`。

測試可優先使用 monkeypatch / fake EntryPoint object，並至少保留一個 package metadata integration test。

---

### Public SDK Regression Tests

既有：

```text
tests/sdk/test_public_exports.py
tests/sdk/test_plugin_generator_contract.py
```

必須繼續保護：

* Plugin author 所需 symbols 可由 `generator.sdk` import；
* Generator implementation 不需要 import internal lifecycle models；
* Public SDK 不意外暴露 Registry/PluginManager internal components。

---

### Quality Gates

Targeted tests：

```powershell
python -m pytest tests\plugins tests\sdk -v --no-cov
```

Lint / format：

```powershell
ruff check generator\plugins generator\sdk tests\plugins tests\sdk
ruff format --check generator\plugins generator\sdk tests\plugins tests\sdk
```

完整品質檢查：

```powershell
git diff --check
pre-commit run --all-files
python -m pytest
```

---

## Documentation Changes

本 ADR 被接受並實作後，至少同步：

* `docs/adr/README.md`
* `docs/architecture/sdk.md`
* `docs/architecture/plugin-sdk-contract-inventory.md`
* `docs/reference/errors.md`
* `docs/roadmap.md`
* `CHANGELOG.md`

如果 Entry Point integration 同時完成，再加入 Plugin author packaging example。

---

## Rollback Plan

如果 validator implementation 造成 incompatibility，可以回退 implementation commit，但保留本 ADR 為：

```text
Proposed
```

重新調整 contract tests 後再實作。

若 ADR 已被正式接受，而實作發現 contract 需要改變：

* 不直接改寫已接受 ADR 的歷史決策；
* 建立新的 superseding ADR；
* 明確記錄 compatibility impact；
* 同步 SDK tests 與 migration guidance。

在 Entry Point integration 完成前，module-based transitional loader 可以暫時保留，避免一次同時改變 discovery、validation 與 packaging 三個維度。

---

## Code Review Checklist

### Architecture

* [ ] Plugin validation 有單一明確 boundary。
* [ ] Discovery、validation、registration responsibility 分離。
* [ ] Validator 不依賴 CLI。
* [ ] Validator 不執行 Generator lifecycle。
* [ ] Registry 不成為第二套完整 validator。
* [ ] 沒有新增第三套 Generator Registry。
* [ ] Public SDK boundary 仍是 `generator.sdk`。
* [ ] Module-based discovery 未被誤寫成正式 external distribution contract。

### Candidate Contract

* [ ] Candidate 必須是 class。
* [ ] Candidate 必須繼承 `BaseGenerator`。
* [ ] `BaseGenerator` 本身被拒絕。
* [ ] Abstract Generator 被拒絕。
* [ ] Valid concrete Generator 被接受。
* [ ] Validator 成功時回傳原始 class。

### Naming

* [ ] `name` 必須為 `str`。
* [ ] `name` 不得為空。
* [ ] `name` 不得包含前後空白。
* [ ] `name` 符合 `^[a-z][a-z0-9-]*$`。
* [ ] Invalid name 不被 silent normalize。
* [ ] Entry Point integration 檢查 `entry_point.name == generator_class.name`。
* [ ] Duplicate name 仍由 Registry 拒絕。

### Construction

* [ ] Plugin 支援 zero-argument construction。
* [ ] Required constructor argument 被拒絕。
* [ ] Constructor validation 不 broad-catch 所有 Exception。
* [ ] Validation 不觸發 Generator `run()`。
* [ ] Constructor side-effect risk 已評估並有文件。

### Error Handling

* [ ] 預期 contract violation 使用 `PluginError`。
* [ ] 必要底層例外透過 chaining 保留。
* [ ] 未預期程式錯誤不被偽裝成 `PluginError`。
* [ ] Tests 不依賴完整錯誤文字。
* [ ] Error message 包含足夠 Plugin identity/context。

### Registry Safety

* [ ] Validation 在 Registry mutation 前完成。
* [ ] Invalid Plugin 不會註冊。
* [ ] Multi-generator validation failure 不造成 partial registration。
* [ ] Duplicate registration 不 silent overwrite。
* [ ] Missing registration lookup 保持既有 error contract。

### Tests

* [ ] 建立 `test_plugin_validation_contract.py`。
* [ ] Non-class candidate 有測試。
* [ ] Unrelated class 有測試。
* [ ] Base class itself 有測試。
* [ ] Abstract class 有測試。
* [ ] Invalid name matrix 有測試。
* [ ] Zero-argument construction 有測試。
* [ ] Loader integration 有 regression test。
* [ ] Partial registration 有測試。
* [ ] SDK public import tests 保持通過。
* [ ] Entry Point integration phase 有 package metadata tests。

### Documentation and Automation

* [ ] ADR index 已更新。
* [ ] SDK Architecture 已同步。
* [ ] Plugin SDK contract inventory 已同步。
* [ ] Errors Reference 已同步。
* [ ] Roadmap 已同步。
* [ ] CHANGELOG 已同步。
* [ ] `git diff --check` 通過。
* [ ] Targeted `pytest --no-cov` 通過。
* [ ] Ruff check 通過。
* [ ] Ruff format check 通過。
* [ ] `pre-commit run --all-files` 通過。
* [ ] `python -m pytest` 通過。

---

## Decision Summary

Plugin SDK v1 validation contract 為：

```text
Candidate
   │
   ▼
Must be a class
   │
   ▼
Must subclass BaseGenerator
   │
   ▼
Must not be BaseGenerator itself
   │
   ▼
Must be concrete
   │
   ▼
Must expose a valid public name
   │
   ▼
Must support zero-argument construction
   │
   ▼
Validated Generator Class
   │
   ▼
Registry
```

正式 Entry Point loading 再增加：

```text
entry_point.name == generator_class.name
```

所有預期 Plugin contract violation 使用：

```text
PluginError
```

而第三方 Plugin 的正式 dependency boundary 繼續是：

```text
generator.sdk
```

本 ADR 不改變 Generator canonical lifecycle，也不引入 factory、Protocol、dependency injection 或 Plugin metadata model。

這些能力若未來需要，應以新的架構決策獨立演進。
