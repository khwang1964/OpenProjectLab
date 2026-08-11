# ADR 0013: Plugin Distribution Contract

> Status: Proposed
> Date: 2026-08-11
> Milestone: Future Plugin Evolution
> Decision scope: Third-party plugin packaging, distribution identity, metadata, installation assumptions, compatibility preflight, and distribution acceptance

## Context

OpenProjectLab（OPL）Milestone 4 已建立並接受第三方 Plugin 的 runtime contract，包括：

- `generator.sdk` public contract
- supported entry-point discovery
- entry-point loading
- plugin validation
- registry preflight / registration
- runtime plugin loading
- example third-party plugin
- installed example plugin entry-point validation

Milestone 5 不重新設計上述 runtime contracts。

下一個問題是：第三方 Plugin 如何在不破壞既有 runtime boundary 的前提下，被可靠地封裝、建置、安裝、辨識、檢查相容性與驗證 distribution artifact。

`docs/architecture/plugin-ecosystem.md` 已將 Plugin Ecosystem 的外層責任定義為：

```text
Plugin Source
    ↓
Python Packaging Metadata
    ↓
Installation Environment
    ↓
Entry Point Discovery
    ↓
Compatibility Validation
    ↓
Milestone 4 Validation + Registry + Loader
    ↓
Runtime Execution
```

因此需要一份 ADR 固定 distribution contract，避免後續 implementation 將 package installation、metadata、compatibility、registry 與 runtime loading 混成同一責任。

---

## Decision Drivers

本決策受以下需求驅動：

1. 保護 Milestone 4 已接受的 Plugin SDK 與 runtime loading contracts。
2. 優先採用 Python 標準 packaging/distribution mechanism，而不是建立 OPL 私有 package format。
3. 明確區分 Python distribution identity 與 OPL runtime plugin identity。
4. 讓 compatibility failure 在 plugin registration / execution 前被辨識。
5. 讓 diagnostics 可以在不必要 import plugin implementation 的情況下檢查 distribution metadata。
6. 讓 built artifact 可以在乾淨環境被安裝與驗證。
7. 不讓 runtime loader 或 registry 承擔 package installation、remote catalog 或 dependency management。
8. 為未來 package manager、registry/catalog、marketplace 保留清楚的 integration boundary。
9. 讓 contract 可以由自動化測試與 CI 驗證。
10. 對尚未實作的能力保持明確的 Proposed 狀態。

---

## Decision

OPL 採用以下 Plugin Distribution Contract。

### 1. Standard Python Distribution

第三方 OPL Plugin 應以標準 Python distribution 作為主要 distribution unit。

Plugin source repository 應以 `pyproject.toml` 描述 build 與 package metadata，並可產生標準 Python distribution artifact，例如 wheel；sdist 可作為額外 artifact，但不得成為 runtime loader 的特殊輸入格式。

OPL 不建立私有 `.opl-plugin` package format 作為 Milestone 5 的基礎。

概念：

```text
Plugin Source Repository
        ↓
pyproject.toml
        ↓
Python Build Backend
        ↓
wheel / sdist
        ↓
Python Environment Installation
        ↓
OPL Entry Point Discovery
```

### 2. Distribution Identity and Runtime Identity Are Distinct

OPL 明確區分：

**Distribution identity**

由 Python packaging metadata 定義，例如：

```text
example-opl-plugin
```

主要用於：

- build
- install / uninstall
- dependency resolution
- distribution version
- artifact identity
- package index identity

**Plugin runtime identity**

由 OPL Plugin contract 定義，例如：

```text
example
```

主要用於：

- OPL registry
- runtime lookup
- diagnostics
- duplicate detection
- execution selection

兩者可以相關，但不得假設永遠相同，也不得以 import package name 取代其中任何一者。

### 3. Entry Point Remains the Runtime Discovery Boundary

Distribution 必須使用 Milestone 4 已接受的 supported entry-point contract 暴露 OPL Plugin。

Milestone 5 不建立第二套 runtime discovery mechanism。

因此：

```text
Installed Distribution
        ↓
Python Distribution Metadata
        ↓
Supported OPL Entry Point
        ↓
Milestone 4 Discovery
        ↓
Compatibility Preflight
        ↓
Validation / Registry / Loading
```

Distribution tooling 不得繞過 entry-point contract 直接把 arbitrary module 注入 registry。

### 4. Package Metadata Is Separate from Runtime Plugin Object

可由 distribution metadata 判定的資訊，應優先從 installed distribution metadata 取得，而不是先 import plugin implementation。

Distribution metadata 至少應能支援：

- distribution name
- distribution version
- supported Python version
- OPL compatibility requirement
- supported OPL entry point declaration

其他 authoring metadata，例如 homepage、source repository、description 或 license，可依標準 Python project metadata提供。

Runtime plugin object 仍由 Milestone 4 Plugin SDK contract 定義。

### 5. Compatibility Is a Preflight Contract

Compatibility validation 位於 entry-point discovery 與 Milestone 4 runtime validation / registration 之間。

```text
Discover installed distribution
        ↓
Read distribution metadata
        ↓
Evaluate compatibility
        ↓
Compatible?
   ├── no  → stop with compatibility result/error
   └── yes → continue to Milestone 4 validation
```

不相容 Plugin 不得進入正常 registry registration 或 execution。

Compatibility preflight 不取代 Milestone 4 plugin validation；兩者驗證不同責任：

- compatibility：環境與版本是否允許繼續
- plugin validation：runtime plugin object 是否符合 OPL contract

### 6. Compatibility Dimensions

Milestone 5 的 compatibility contract 至少考慮：

- Python runtime compatibility
- OPL distribution/runtime compatibility
- Plugin distribution version identity

OPL compatibility requirement 應使用標準、可機器判定的 version/specifier semantics，而不是解析自然語言字串。

本 ADR 不建立獨立的第二套「SDK version」系統。只有在 `generator.sdk` 未來確實需要與 OPL distribution version 分離演進時，才應透過新的 ADR 決定。

### 7. Unknown Compatibility Must Not Be Silently Treated as Compatible

若必要 compatibility metadata 缺失、無法解析或無法判定，系統不得靜默宣告 compatible。

正式 implementation 必須以明確結果表示至少：

```text
compatible
incompatible
unknown
```

`unknown` 的最終 runtime policy 應由實作 contract tests 固定；在該 policy 正式接受前，不應文件化成既有穩定行為。

### 8. Installation Is Outside the Runtime Loader

Runtime loader 不負責：

- 執行 `pip install`
- 建立 virtual environment
- 下載 remote package
- dependency resolution
- package upgrade
- package uninstall
- remote registry/catalog lookup

Runtime loader 的前提是 Plugin distribution 已存在於目前 Python environment，且可由 supported entry-point discovery 找到。

未來若 OPL 建立 package manager，它必須位於 runtime plugin system 外層。

### 9. Registry Remains a Runtime Registry

Milestone 4 Plugin Registry 繼續負責 runtime identity 與 registration semantics。

Registry 不負責：

- Python package installation
- remote package search
- version solving
- package artifact storage
- marketplace metadata
- dependency download

Distribution identity conflict 與 runtime plugin identity conflict 必須能被分別診斷。

### 10. Diagnostics Must Be Stage-Aware

Milestone 5 diagnostics 應能區分至少下列階段：

```text
distribution metadata
installation presence
entry-point discovery
compatibility
plugin validation
registry preflight
loading
```

不得將所有失敗都壓縮為單一「plugin load failed」。

Metadata-only diagnostics 應盡量避免 import plugin implementation。

需要真正載入 entry point 的 diagnostics 必須明確屬於 runtime/deep validation，並承認第三方程式碼可能產生 side effects。

### 11. Built Artifact Is the Distribution Acceptance Unit

Source-tree tests 不足以證明 distribution contract。

正式 distribution acceptance 應至少驗證：

```text
Build artifact
    ↓
Create / use clean test environment
    ↓
Install artifact
    ↓
Inspect distribution metadata
    ↓
Discover supported entry point
    ↓
Evaluate compatibility
    ↓
Load and validate plugin
    ↓
Register / execute representative path
```

Acceptance 不應只依賴 editable install。

核心 CI 測試不得依賴公開網路 package index 才能成功；應可使用本地 build artifact 完成。

### 12. Distribution Validation Is Not a Security Sandbox

成功通過 metadata、compatibility 與 plugin validation，不代表第三方 Plugin 是可信或 sandboxed。

OPL 必須清楚維持以下 trust boundary：

- installed third-party plugin 是可執行 Python code
- entry-point load 可能執行第三方程式碼
- compatibility metadata 可以錯誤或惡意宣告
- package metadata validation 不等於 supply-chain verification
- Plugin validation 不等於 security validation

簽章、provenance、publisher verification、allowlist、remote trust policy 等能力屬於 future work，除非另有 ADR 與實作。

---

## Contract Model

概念上的 distribution descriptor 可以表示為：

```python
@dataclass(frozen=True, slots=True)
class PluginDistribution:
    distribution_name: str
    distribution_version: str
    entry_point_name: str
    entry_point_value: str
    opl_requirement: str | None
    python_requirement: str | None
```

Compatibility result 可以表示為：

```python
class CompatibilityStatus(StrEnum):
    COMPATIBLE = "compatible"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"
```

```python
@dataclass(frozen=True, slots=True)
class CompatibilityResult:
    status: CompatibilityStatus
    reason: str | None = None
```

以上僅描述 contract shape，不代表本 ADR 要求使用完全相同的 class 名稱或 module placement。

正式 public/private API 由後續 tests 與 implementation 決定。

---

## Metadata Ownership

| Metadata | Owner | Primary purpose |
|---|---|---|
| Distribution name | Python packaging | install / artifact identity |
| Distribution version | Python packaging | version / compatibility |
| Python requirement | Python packaging | interpreter compatibility |
| OPL compatibility requirement | Plugin distribution contract | host compatibility |
| Entry point group | OPL contract | discovery namespace |
| Entry point name | Distribution + OPL contract | discovery/runtime mapping |
| Entry point target | Python packaging | load target |
| Runtime plugin identity | Milestone 4 plugin contract | registry/runtime identity |

同一資訊不應在多個位置建立互相獨立、容易 drift 的 source of truth。

---

## Required Invariants

1. 未安裝的 distribution 不會被 runtime registry 當作已安裝 Plugin。
2. 沒有 supported entry point 的 distribution 不會被當作可載入 OPL Plugin。
3. incompatible Plugin 不會進入正常 registration/execution。
4. compatibility validation 不取代 runtime plugin validation。
5. distribution name 不被當作 runtime plugin identity 的唯一來源。
6. runtime loader 不執行 installation。
7. registry 不執行 remote discovery 或 package resolution。
8. metadata-only inspection 不需要載入 plugin implementation。
9. built artifact acceptance 可以在無外部網路的 CI 環境重現。
10. Milestone 4 public SDK 與 loading contracts 不因 distribution implementation 被隱式修改。

---

## Failure Model

Milestone 5 應能區分：

- Distribution not installed
- Missing OPL entry point
- Invalid distribution metadata
- Unknown compatibility
- Incompatible Python
- Incompatible OPL
- Broken entry point
- Invalid plugin object
- Duplicate runtime identity

上述失敗不應全部轉成相同文字或相同內部 exception，而失去 stage information。

正式 exception hierarchy 與 CLI exit-code mapping若需要公開穩定契約，應另行設計並同步 Errors Reference。

---

## Installation Environment Contract

Milestone 5 對 runtime 的基本假設：

- OPL 與 Plugin 位於可被目前 Python interpreter 觀察到的 environment。
- Python packaging system 已完成安裝。
- supported entry-point metadata 可由 Python distribution metadata API 讀取。
- runtime loader 不負責修復缺失 dependency。
- runtime loader 不自行切換 environment。
- editable install 可以用於 development，但不是唯一 acceptance path。

若未來 OPL 管理獨立 Plugin environment，必須另行決定 environment ownership、isolation、dependency conflicts、interpreter selection、upgrade/uninstall semantics 與 security boundary。

本 ADR 不預先決定上述機制。

---

## Distribution Acceptance Tests

### Unit tests

- distribution metadata extraction
- version/specifier parsing
- compatibility evaluation
- malformed metadata
- missing metadata
- deterministic result ordering

### Contract tests

- compatible distribution 可以進入下一階段
- incompatible distribution 在 load/register 前停止
- unknown compatibility 有明確結果
- distribution identity 與 runtime identity 分離
- Milestone 4 entry-point contract 被保留
- metadata-only inspection 不 load plugin implementation

### Integration tests

使用可安裝的 example Plugin 驗證：

- installed distribution 可被發現
- entry point 可被取得
- compatibility 可被判定
- Milestone 4 validation 仍通過
- registry behavior 不被 distribution layer 改變

### Artifact acceptance test

CI 至少包含：

```text
build
  ↓
install built wheel
  ↓
inspect metadata
  ↓
discover
  ↓
compatibility check
  ↓
load
  ↓
validate
  ↓
register / representative execution
```

不得只測 source checkout 或 editable install。

---

## Documentation Contract

任何新增或修改 Plugin distribution 能力的 PR，應依影響同步更新：

- `docs/architecture/plugin-ecosystem.md`
- `docs/adr/0013-plugin-distribution-contract.md`
- Plugin authoring documentation
- SDK documentation（若 public SDK 受影響）
- Errors Reference（若新增 error contract）
- CLI Reference（若新增 diagnostics/install commands）
- `docs/roadmap.md`
- `docs/HISTORY.md`
- `CHANGELOG.md`
- Milestone acceptance documentation

若變更會修改 Milestone 4 已接受的 public/runtime contract，不能只修改本 ADR；必須明確重新評估既有 ADR 與 backward compatibility。

---

## Automation Contract

Distribution contract 的實作 PR 至少應執行：

```powershell
git diff --check
ruff check generator tests
ruff format --check generator tests
pre-commit run --all-files
python -m pytest
```

若 PR 涉及 distribution artifact，CI 還應驗證：

```text
build artifact
install artifact in clean environment
run distribution acceptance tests
```

核心 acceptance 不應依賴外部網路。

---

## Alternatives Considered

### Alternative A: OPL-specific plugin archive format

例如建立 `*.opl-plugin`。

**Rejected for Milestone 5 foundation.**

原因：

- 重複 Python packaging 已解決的 build/install/version metadata 問題。
- 增加 installer、security、dependency 與 tooling 負擔。
- 讓 OPL runtime 與 package management 過度耦合。
- 不利第三方作者使用既有 Python ecosystem。

### Alternative B: Let runtime loader call pip automatically

**Rejected.**

原因：

- discovery 會產生 installation side effect。
- loader 必須處理 network、dependency solver、credentials、environment mutation。
- 失敗邊界難以測試。
- 破壞可重現性。
- 擴大 security surface。

### Alternative C: Use distribution name as runtime plugin name

**Rejected.**

原因：

- packaging identity 與 runtime identity 用途不同。
- distribution rename 會不必要地改變 runtime contract。
- 一個 distribution 未來可能暴露多個 entry points。
- registry conflict 與 package conflict 無法清楚區分。

### Alternative D: Import plugin first, then ask it for compatibility

**Rejected as the primary compatibility mechanism.**

原因：

- incompatibility 已經發生時仍需執行第三方 import。
- import 可能有 side effects。
- broken dependency 會讓 compatibility diagnostics 失去精度。
- metadata-only diagnostics 無法成立。

### Alternative E: Build a remote marketplace now

**Deferred.**

Milestone 5 先建立 local installed-distribution contract。Remote catalog、publisher identity、search、download、trust、rating、signing 等功能應建立在穩定 distribution contract 之上。

---

## Consequences

### Positive

- 保護 Milestone 4 runtime contracts。
- 使用標準 Python ecosystem，降低自訂基礎設施。
- package/distribution 與 runtime plugin responsibility 清楚。
- compatibility failure 可以更早、更精確地被診斷。
- built artifact 成為可自動化驗證的正式交付單位。
- 為未來 package manager / catalog / marketplace 建立乾淨 boundary。

### Negative

- Plugin author 必須維護正確 packaging metadata。
- compatibility metadata 成為新的 contract surface。
- acceptance test 增加 build/install 階段。
- diagnostics 需要區分 metadata-only 與 runtime/deep validation。

### Risks

- metadata 與實際 runtime behavior drift。
- 過早穩定 compatibility metadata key 可能造成 migration 成本。
- Python packaging backend 差異可能影響 artifact。
- 第三方 Plugin 仍是可執行程式碼的 trust boundary。
- package manager 若侵入 runtime layer，可能破壞本 ADR。

---

## Compatibility and Migration

本 ADR 的目標是 additive。

Milestone 4 已存在的第三方 example Plugin 應作為 migration/acceptance fixture，確認：

- 既有 supported entry point 繼續有效。
- 既有 Plugin SDK object contract 不需為 distribution layer 改寫。
- registry semantics 不變。
- loader semantics 不變。

若既有 example Plugin 缺少 Milestone 5 所需 distribution metadata，應以明確、可 review 的 metadata migration 補足，而不是修改 runtime Plugin object 來隱藏缺失。

---

## Implementation Sequence

### Step 5.2 — Metadata Contract

建立 metadata model、metadata extraction、compatibility requirement representation、tests 與 authoring documentation。

### Step 5.3 — Compatibility Contract

建立 compatibility status/result、version/specifier evaluation、incompatible / unknown behavior，以及 Milestone 4 validation 前的 integration boundary。

### Step 5.4 — Installation and Discovery Integration

驗證 installed distribution metadata、supported entry point、clean-environment installation 與 discovery integration。

### Step 5.5 — Diagnostics

建立可區分 stage 的 installed-plugin inspection。

### Step 5.6 — Distribution Acceptance

建立：

```text
build → install → discover → compatibility → load → validate → register/execute
```

的 CI acceptance workflow。

---

## Code Review Checklist

### Architecture

- [ ] Milestone 4 SDK、validation、registry、loader contract 未被重新定義。
- [ ] Distribution layer 位於 runtime plugin system 外層。
- [ ] Runtime loader 不負責 installation。
- [ ] Registry 不負責 package manager 或 remote catalog。
- [ ] Compatibility preflight 與 plugin validation 責任分離。
- [ ] 新 abstraction 對應實際 contract，不是預先建立 marketplace framework。

### Packaging

- [ ] 優先使用標準 `pyproject.toml` / Python distribution metadata。
- [ ] Distribution identity 與 runtime plugin identity 分離。
- [ ] supported entry point 與 Milestone 4 contract 一致。
- [ ] Editable install 不被當作唯一 acceptance path。
- [ ] Built artifact 有 acceptance strategy。
- [ ] 核心測試不依賴公開 package index。

### Compatibility

- [ ] Python compatibility 有明確來源。
- [ ] OPL compatibility requirement 可機器判定。
- [ ] 使用標準 version/specifier semantics。
- [ ] `compatible` / `incompatible` / `unknown` 可區分。
- [ ] incompatible Plugin 在 registration/execution 前停止。
- [ ] 沒有為 SDK 過早建立第二套 version system。
- [ ] compatibility result 不依賴 human-readable message parsing。

### Diagnostics and Security

- [ ] Distribution missing、entry point missing、incompatible、broken entry point、invalid plugin 可區分。
- [ ] Metadata-only diagnostics 不 import plugin implementation。
- [ ] Deep/runtime diagnostics 的 side effects 有文件。
- [ ] 沒有宣稱 Plugin sandboxing。
- [ ] Discovery 不會自動安裝 package。
- [ ] Metadata validation 不被描述為 security validation。
- [ ] Third-party executable-code trust boundary 有文件。

### Tests

- [ ] Metadata extraction 有 unit tests。
- [ ] Compatibility evaluation 有 contract tests。
- [ ] Missing/malformed metadata 有測試。
- [ ] Unknown compatibility 有測試。
- [ ] Incompatible Plugin 不會進入 runtime registration。
- [ ] Installed distribution discovery 有 integration test。
- [ ] Milestone 4 example Plugin 仍通過。
- [ ] Built artifact 有 clean-environment acceptance test。
- [ ] Acceptance 不依賴外部網路。
- [ ] Test output/order deterministic。

### Documentation

- [ ] `docs/architecture/plugin-ecosystem.md` 已同步。
- [ ] 本 ADR 已同步。
- [ ] Plugin authoring 文件已同步。
- [ ] SDK 文件已同步（如適用）。
- [ ] Errors / CLI Reference 已同步（如適用）。
- [ ] `docs/roadmap.md` 已同步。
- [ ] `docs/HISTORY.md` 已同步。
- [ ] `CHANGELOG.md` 已同步。
- [ ] Milestone acceptance 文件已同步。

### Automation

- [ ] `git diff --check` 通過。
- [ ] Ruff checks 通過（若有 Python 變更）。
- [ ] Ruff format check 通過（若有 Python 變更）。
- [ ] Targeted contract tests 通過。
- [ ] Integration tests 通過。
- [ ] Distribution acceptance 可在 CI 重現。
- [ ] `pre-commit run --all-files` 通過。
- [ ] `python -m pytest` 通過。

---

## Acceptance Criteria

ADR 0013 可以從 Proposed 轉為 Accepted，至少需要：

- Plugin distribution responsibility boundary 已獲確認。
- 標準 Python distribution 被接受為主要 packaging unit。
- Distribution identity 與 runtime identity 分離。
- Entry point 繼續作為 Milestone 4 runtime discovery boundary。
- Compatibility preflight placement 已確認。
- Unknown compatibility policy 已由 tests / implementation 固定。
- Runtime loader 不承擔 installation。
- Registry 不承擔 remote package management。
- Built artifact acceptance workflow 已定義並可自動化。
- Plugin authoring documentation 已同步。
- Code Review Checklist 已可用。
- 不需要破壞 Milestone 4 已接受的 public/runtime contracts。

---

## Related Documents

- `docs/architecture/plugin-ecosystem.md`
- `docs/architecture/plugin-sdk-contract-inventory.md`
- `docs/adr/0010-plugin-sdk-public-contract.md`
- `docs/adr/0011-plugin-validation-contract.md`
- `docs/adr/0012-plugin-entry-point-contract.md`
- Plugin authoring documentation
- `docs/roadmap.md`
- `docs/HISTORY.md`
- `CHANGELOG.md`
- Milestone 4 acceptance documentation

---

> **OPL Plugin distribution 的責任是讓標準 Python distribution 能被可靠地建置、安裝、辨識與判定相容性；它不取代 Milestone 4 的 Plugin SDK、validation、registry 或 runtime loading contract。**
