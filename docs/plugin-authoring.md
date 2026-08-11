# OpenProjectLab Plugin Authoring Guide

> Milestone: 4 — Plugin Ecosystem / Plugin SDK
> Audience: Third-party Generator Plugin authors
> Status: Canonical authoring guide for Plugin SDK v1

OpenProjectLab（OPL）Plugin SDK 的目標，是讓第三方 Generator 可以透過穩定的公開契約擴充 OPL，而不需要依賴核心私有模組。

核心規則：

> Third-party Plugin code depends on `generator.sdk`, not `generator.core`, `generator.generators`, or `generator.plugins`.

---

## 1. Plugin Architecture

正式的第三方 Plugin loading flow：

```text
Python Distribution
    ↓
openprojectlab.generators
    ↓
EntryPoint.load()
    ↓
Plugin contract validation
    ↓
entry_point.name == generator.name
    ↓
transactional registration preflight
    ↓
GeneratorRegistry
```

Plugin author 只需要實作 Generator 與 package metadata，不需要直接操作 Registry、loader 或 validation implementation。

---

## 2. Supported Public Imports

Plugin implementation 應從：

```python
generator.sdk
```

取得公開 lifecycle contracts。

典型 imports：

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

實際可用 symbols 以目前版本的 `generator.sdk.__all__` 與 SDK contract tests 為準。

Plugin code 不應 import：

```text
generator.core.*
generator.generators.*
generator.plugins.*
```

這些 namespace 屬於 host runtime implementation details，不是第三方相容性保證。

---

## 3. Minimal Plugin Generator

Plugin SDK v1 使用 `BaseGenerator` inheritance-based contract。

最小結構：

```python
from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
)


class ExampleGenerator(BaseGenerator):
    name = "example-plugin"

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        return GenerationPlan(
            generator_name=request.generator_name,
        )

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        return GenerationResult(
            generator_name=request.generator_name,
            dry_run=request.options.dry_run,
        )
```

`BaseGenerator.run()` 由 Framework 控制。

Plugin 不應覆寫 framework orchestration 來建立另一套 lifecycle。

Canonical lifecycle：

```text
GenerateRequest
    ↓
validate_request()
    ↓
plan()
    ↓
GenerationPlan
    ↓
execute()
    ↓
GenerationResult
```

---

## 4. Validation

若 Plugin 需要驗證 request，可覆寫：

```python
validate_request(request)
```

驗證失敗應使用公開的 structured validation contract：

```python
GeneratorValidationError
```

不要依賴一般 `ValueError` 作為正式 Generator validation API。

Validation 必須在 planning / execution side effects 之前完成。

---

## 5. Planning

`plan()` 應描述 Generator 將執行的工作，而不是直接產生不可逆 side effects。

Plugin 可以透過：

```text
GenerationPlan
GenerationOperation
WritePolicy
```

表達 generation intent。

Planning 應維持 deterministic，並與 dry-run 使用同一份計畫語意。

---

## 6. Execution and Result

`execute()` 接收：

```text
GenerateRequest
GenerationPlan
```

並回傳共同：

```text
GenerationResult
```

不要建立 Plugin-specific result type 作為 Framework lifecycle 的正式輸出。

共同 result graph：

```text
GenerationResult
    ↓
WriteResult
    ↓
WriteStatus
```

---

## 7. Plugin Naming Contract

每個 Plugin Generator 必須提供 stable public name：

```python
name = "example-plugin"
```

Plugin SDK v1 naming rule：

```text
^[a-z][a-z0-9-]*$
```

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

Framework 不會 silent-normalize invalid Plugin names。

---

## 8. Zero-Argument Constructor

Plugin SDK v1 要求 Generator class 支援：

```python
ExampleGenerator()
```

因此不要建立必填 constructor arguments：

```python
class InvalidGenerator(BaseGenerator):
    def __init__(self, config):
        ...
```

若需要執行工作或讀取 request-dependent data，應放在 Framework-controlled lifecycle，而不是 constructor。

Constructor 應保持輕量，避免：

* filesystem writes
* network calls
* subprocess execution
* expensive discovery
* generation execution
* global state mutation

---

## 9. Python Entry Point Declaration

第三方 Plugin distribution 必須在自己的 `pyproject.toml` 宣告：

```toml
[project.entry-points."openprojectlab.generators"]
example-plugin = "opl_example:ExampleGenerator"
```

正式 group：

```text
openprojectlab.generators
```

一個 Entry Point 對應一個 Generator class。

Plugin SDK v1 不接受 Entry Point resolve 成：

```text
factory function
Generator instance
module
arbitrary callable
arbitrary object
```

---

## 10. Entry Point Identity

Entry Point metadata name 必須等於 Generator runtime name：

```text
entry_point.name == generator_class.name
```

例如：

```toml
[project.entry-points."openprojectlab.generators"]
example-plugin = "opl_example:ExampleGenerator"
```

必須搭配：

```python
class ExampleGenerator(BaseGenerator):
    name = "example-plugin"
```

如果 metadata 寫：

```text
example
```

而 runtime name 是：

```text
example-plugin
```

Plugin loading 會以 `PluginError` 拒絕。

---

## 11. Package Layout Example

一個最小第三方 package 可以是：

```text
opl-example-plugin/
├── pyproject.toml
├── README.md
├── src/
│   └── opl_example/
│       ├── __init__.py
│       └── generator.py
└── tests/
    └── test_plugin.py
```

`pyproject.toml`：

```toml
[project]
name = "opl-example-plugin"
version = "0.1.0"

[project.entry-points."openprojectlab.generators"]
example-plugin = "opl_example.generator:ExampleGenerator"
```

---

## 12. Loading and Transaction Safety

OPL host runtime 會先：

```text
discover all
load all
validate all
identity-check all
preflight all
register all
```

才開始 Registry mutation。

因此任一 Plugin 發生：

```text
load failure
validation failure
identity mismatch
duplicate name
existing registry collision
```

都不得留下 partial registration。

這是 host guarantee，不是 Plugin author 必須自行實作的 transaction logic。

---

## 13. PluginError Boundary

Plugin loading / contract violation 使用：

```text
PluginError
```

作為 Plugin-facing error boundary。

Plugin author 不應依賴完整錯誤訊息文字作為永久 API。

相容性重點是：

```text
exception type
contract semantics
relevant identity
```

---

## 14. Testing a Plugin

Plugin 自己至少應測試：

```text
Generator can be imported
Generator subclasses BaseGenerator
Generator name follows naming rule
Generator supports zero-argument construction
plan() returns GenerationPlan
execute() returns GenerationResult
Plugin imports only generator.sdk
```

在 OPL repository 中，Plugin SDK / runtime 由下列層次保護：

```text
tests/sdk/
tests/plugins/
```

包含：

```text
public exports
third-party-style Generator contract
Plugin validation
Registry preflight
Entry Point contract
transactional Entry Point integration
legacy runtime removal boundary
```

---

## 15. Compatibility Expectations

`generator.sdk` 是第三方 Plugin 的 versioned compatibility boundary。

下列變更可能是 breaking：

* 移除或 rename public SDK symbol
* 改變 required lifecycle signature
* 改變 Entry Point group
* 改變 Entry Point target contract
* 改變 Plugin naming rule
* 改變 zero-argument constructor requirement
* 移除 public dataclass field
* 改變 public enum semantics
* 改變 public exception boundary

Plugin 不應把 internal module layout 當成相容性承諾。

---

## 16. Security and Trust

Python Entry Point 會 import third-party Python package。

因此安裝並啟用 Plugin 等同信任該 package 在目前 Python process 執行程式碼。

Plugin validation 提供：

```text
structural compatibility
identity validation
transactional Registry safety
```

但不提供：

```text
sandboxing
malware isolation
process isolation
permission isolation
```

---

## 17. Author Checklist

### SDK Boundary

- [ ] Plugin 只 import `generator.sdk`。
- [ ] 不 import `generator.core.*`。
- [ ] 不 import `generator.generators.*`。
- [ ] 不 import `generator.plugins.*`。

### Generator Contract

- [ ] Generator 繼承 `BaseGenerator`。
- [ ] class 是 concrete。
- [ ] `name` 符合 `^[a-z][a-z0-9-]*$`。
- [ ] 支援 zero-argument construction。
- [ ] `plan()` 回傳 `GenerationPlan`。
- [ ] `execute()` 回傳 `GenerationResult`。
- [ ] request validation 使用 framework contract。

### Packaging

- [ ] 使用 `openprojectlab.generators` Entry Point group。
- [ ] one Entry Point → one Generator class。
- [ ] Entry Point name 等於 `generator.name`。
- [ ] package metadata 指向正確 class object。

### Quality

- [ ] Plugin 有自動化測試。
- [ ] 不依賴 OPL internal implementation layout。
- [ ] constructor 無昂貴或不可逆 side effects。
- [ ] 不假設 Entry Point discovery order。

---

## 18. Related Architecture Decisions

Plugin authoring contract 由以下 ADR 共同定義：

```text
ADR 0010 — Plugin SDK Public Contract
ADR 0011 — Plugin Validation Contract
ADR 0012 — Plugin Entry Point Contract
```

若這些 ADR 與本指南發生差異，以 accepted ADR 與目前 SDK contract tests 為準。
