# Plugin SDK Architecture

> Status: Active
> Milestone: 4 — Plugin Ecosystem / Plugin SDK
> Related ADRs: 0010, 0011, 0012

## Purpose

`generator.sdk` 是 OpenProjectLab 第三方 Generator Plugin 的穩定 dependency boundary。

第三方 Plugin：

```text
MUST depend on generator.sdk
MUST NOT depend on generator.core.*
MUST NOT depend on generator.generators.*
MUST NOT depend on generator.plugins.*
```

---

## Canonical Architecture

```text
Third-Party Plugin Distribution
          │
          │ openprojectlab.generators
          ▼
      Python Entry Point
          │
          ▼
      EntryPoint.load()
          │
          ▼
 validate_plugin_generator()
          │
          ▼
metadata/runtime identity check
          │
          ▼
 transactional preflight
          │
          ▼
   GeneratorRegistry
          │
          ▼
 BaseGenerator canonical lifecycle
```

Host-side Plugin runtime 位於 `generator.plugins`，但它不是 Plugin author public API。

---

## Public Generator Lifecycle

Framework 控制：

```text
BaseGenerator.run()
```

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

Plugin extension points：

```text
validate_request()
plan()
execute()
```

---

## Public Type Graph

Plugin author 會透過 `generator.sdk` 使用 canonical lifecycle types。

核心 graph：

```text
BaseGenerator
├── GenerateRequest
│   └── RuntimeOptions
│       └── WritePolicy
├── GenerationPlan
│   └── GenerationOperation
│       └── WritePolicy
└── GenerationResult
    └── WriteResult
        └── WriteStatus
```

Validation / loading-facing public exceptions 包括：

```text
GeneratorValidationError
PluginError
```

實際 public symbols 以 `generator.sdk.__all__` 與 `tests/sdk/test_public_exports.py` 為 executable contract。

---

## Plugin Validation Boundary

Host runtime 使用單一 validator：

```text
loaded candidate
    ↓
class
    ↓
BaseGenerator subclass
    ↓
not BaseGenerator itself
    ↓
concrete
    ↓
valid public name
    ↓
zero-argument construction
    ↓
validated Generator class
```

Validator 不應：

```text
register Generator
execute Generator lifecycle
mutate Registry
```

---

## Naming

Plugin Generator public name：

```text
^[a-z][a-z0-9-]*$
```

Entry Point metadata name 必須等於：

```text
generator_class.name
```

Framework 不 silent-normalize invalid Plugin identities。

---

## Python Entry Point Contract

Canonical group：

```text
openprojectlab.generators
```

Contract：

```text
one Entry Point
    ↓
one type[BaseGenerator]
```

不支援：

```text
factory
instance
module
arbitrary callable
```

---

## Transactional Registration

Batch loading 必須：

```text
discover/load all
    ↓
validate all
    ↓
identity-check all
    ↓
preflight all
    ↓
register all
```

任何 failure 在 Registry mutation 前停止。

因此：

```text
no partial registration
```

是正式 runtime invariant。

---

## Internal Boundaries

以下為 host implementation details：

```text
generator.plugins.entry_points
generator.plugins.validation
generator.plugins.registry
generator.plugins.loader
```

第三方 Plugin 不應直接 import。

Legacy：

```text
generator.core.plugin.PluginManager
PluginDescriptor
```

已由 canonical Entry Point runtime 取代並移除。

---

## Testing Layers

```text
tests/sdk/
    public import compatibility
    SDK-only Generator contract

tests/plugins/
    validation contract
    registry contract
    loading integration
    Entry Point contract
    transactional Entry Point integration
    legacy runtime removal boundary
```

Tests 應從 external Plugin developer 與 host-runtime contract 兩種視角保護 architecture。

---

## Compatibility

Potentially breaking：

* 移除 / rename public SDK symbol
* 改變 lifecycle method signature
* 改變 Entry Point group
* 改變 Entry Point target contract
* 改變 naming rule
* 改變 zero-argument construction requirement
* 改變 public exception semantics
* 要求 Plugin import internal namespace

重大 Public SDK 變更必須透過 ADR、tests、documentation 與 migration guidance 管理。

---

## Authoring Reference

第三方 Plugin 的完整開發與 packaging 指南：

```text
docs/plugin-authoring.md
```

---

## Code Review Checklist

- [ ] Plugin author 只需依賴 `generator.sdk`。
- [ ] Public lifecycle type graph 自洽。
- [ ] Host Plugin runtime 保持 internal。
- [ ] validation 與 registration responsibility 分離。
- [ ] Entry Point identity contract 明確。
- [ ] transaction failure 不留下 partial registration。
- [ ] legacy PluginManager 不重新導入。
- [ ] SDK contract tests 與 Plugin runtime tests 同步。
- [ ] 重大 compatibility change 有 ADR。
