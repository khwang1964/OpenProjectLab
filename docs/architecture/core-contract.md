# Core Framework Contract

## 1. Purpose

OpenProjectLab Core Framework Contract 定義核心元件之間的正式責任、依賴方向、資料交換格式、生命週期與錯誤邊界。

本文件不是單一模組的實作說明，而是 Configuration、Registry、Generator、Template、Filesystem、Manifest 與 CLI 共同遵守的整合契約。

其目的在於確保：

* 核心元件可以獨立演進。
* 依賴方向保持一致。
* 公開介面不被任意破壞。
* Generator 行為可預測、可測試且可擴充。
* Plugin 未來可以在不繞過核心規則的情況下加入。
* 文件、測試與實作維持同步。

---

## 2. Scope

本文件涵蓋以下核心元件：

```text
CLI
Configuration
Registry
Generator
Template Renderer
Filesystem
Manifest
Core Exceptions
Runtime Models
```

Plugin Framework 只涵蓋與核心契約直接相關的邊界。完整 Plugin 設計應由獨立架構文件定義。

---

## 3. Architectural Principles

OpenProjectLab Core Framework 遵循以下原則。

### 3.1 Design First

任何核心功能變更應先明確定義：

* 問題與目標
* 元件責任
* 公開契約
* 依賴方向
* 錯誤模型
* 相容性影響
* 測試策略

實作不應先於架構決策。

### 3.2 Documentation First

任何新的公開行為，都必須先在架構文件或參考文件中定義。

文件至少應描述：

* 使用方式
* 資料格式
* 預設值
* 錯誤行為
* 邊界條件
* 相容性政策

### 3.3 Automation First

可由工具驗證的規則，不應只依賴人工記憶。

適合自動化的項目包括：

* 格式檢查
* 型別檢查
* 單元測試
* 整合測試
* 文件連結檢查
* CLI contract tests
* Manifest schema validation
* pre-commit
* CI

### 3.4 Explicit Contracts

核心元件必須透過明確介面協作，不依賴隱性約定。

### 3.5 Dependency Inversion

高階流程依賴抽象契約，不直接依賴具體基礎設施實作。

### 3.6 Determinism

相同輸入、設定、模板與版本，應得到相同 Generation Plan 與等價輸出。

### 3.7 Side-effect Isolation

檔案系統寫入、Manifest 更新與其他副作用，必須集中在清楚的執行邊界。

### 3.8 Fail Fast

無效設定、未知 Generator、路徑衝突與模板錯誤應盡早回報。

### 3.9 Backward Compatibility

已公開的 CLI、設定鍵、Generator 名稱與 Manifest 格式，除非經過版本策略，不應任意破壞。

---

## 4. High-level Architecture

```text
User
 │
 ▼
CLI
 │
 ├── Parse Arguments
 ├── Load Configuration
 ├── Build Runtime Options
 ├── Build Dependencies
 ├── Build Registry
 └── Dispatch Request
 │
 ▼
Generator Registry
 │
 ├── Lookup Generator
 └── Create Generator
 │
 ▼
Generator
 │
 ├── Validate Request
 ├── Build Template Context
 ├── Build Generation Plan
 └── Execute Plan
 │
 ├──────────────► Template Renderer
 │
 ├──────────────► Filesystem
 │
 └──────────────► Manifest
 │
 ▼
Generation Result
 │
 ▼
CLI Output / Exit Code
```

---

## 5. Core Dependency Direction

推薦依賴方向：

```text
CLI
 ├──► Configuration
 ├──► Registry
 └──► Runtime Models

Registry
 └──► Generator Contract

Generator
 ├──► Template Contract
 ├──► Filesystem Contract
 ├──► Manifest Contract
 └──► Runtime Models

Template
 └──► Template Models

Filesystem
 └──► Filesystem Models

Manifest
 └──► Manifest Models
```

禁止反向依賴：

```text
Configuration ─X─► CLI
Registry      ─X─► CLI
Generator     ─X─► CLI parser
Template      ─X─► Generator implementations
Filesystem    ─X─► Generator implementations
Manifest      ─X─► CLI
```

---

## 6. Composition Root

所有具體依賴應在 Composition Root 組裝。

目前主要 Composition Root 為：

```text
generator/cli/main.py
```

其責任包括：

1. 建立 CLI parser。
2. 解析命令列參數。
3. 載入 ProjectConfig。
4. 建立 RuntimeOptions。
5. 建立 Template Renderer。
6. 建立 Filesystem。
7. 建立 Manifest Store。
8. 建立 Generator Registry。
9. 註冊核心與 Plugin Generator。
10. 將 Request dispatch 給目標 Generator。
11. 將結果轉換為 CLI 輸出與 exit code。

Composition Root 不應包含：

* Generator 業務邏輯。
* YAML 解析細節。
* 模板渲染細節。
* 檔案寫入演算法。
* Manifest schema 邏輯。

---

## 7. Core Runtime Flow

完整執行流程：

```text
1. Parse CLI arguments
2. Resolve configuration path
3. Load and validate configuration
4. Build runtime options
5. Build shared services
6. Build generator registry
7. Resolve requested generator
8. Build generator request
9. Validate request
10. Build generation plan
11. Validate plan
12. Execute plan
13. Update manifest
14. Return generation result
15. Render CLI output
16. Return exit code
```

每一步應具有獨立錯誤邊界。

---

## 8. Core Data Models

建議核心框架使用以下主要模型：

```text
ProjectConfig
RuntimeOptions
GeneratorMetadata
GeneratorEntry
GenerateRequest
TemplateContext
GenerationPlan
GenerationOperation
WritePolicy
GenerationResult
ManifestRecord
```

這些模型應優先使用：

```python
@dataclass(frozen=True, slots=True)
```

除非物件本質上需要可變狀態。

---

## 9. Configuration Contract

Configuration 負責將外部設定來源轉換為可信的內部設定模型。

### 9.1 Input

主要輸入：

```text
Path to YAML configuration file
```

未來可能包含：

* environment variables
* profile
* explicit overrides

### 9.2 Output

```python
ProjectConfig
```

### 9.3 Guarantees

成功回傳時，Configuration 必須保證：

* YAML 已安全解析。
* 頂層結構有效。
* 核心區段型別有效。
* 預設值已套用。
* 路徑已依正式規則解析。
* 設定物件可供核心元件安全使用。

### 9.4 Prohibited Behavior

Configuration 不得：

* 寫入檔案。
* 建立輸出目錄。
* 執行 Generator。
* 渲染模板。
* 更新 Manifest。
* 直接建立 Registry。
* 靜默忽略重大錯誤。

### 9.5 Error Boundary

所有設定錯誤應繼承：

```python
ConfigurationError
```

---

## 10. Runtime Options Contract

Runtime Options 表示單次執行選項，不是永久專案設定。

建議模型：

```python
@dataclass(frozen=True, slots=True)
class RuntimeOptions:
    dry_run: bool = False
    overwrite: bool = False
    verbose: bool = False
    force: bool = False
```

Runtime Options 來源通常為：

* CLI arguments
* command-specific request
* Configuration defaults

覆寫順序必須明確。

Runtime Options 不應直接寫回 Configuration。

---

## 11. Registry Contract

Registry 是 Generator catalog 的唯一可信來源。

### 11.1 Responsibilities

* 註冊 Generator。
* 驗證名稱。
* 防止重複註冊。
* 查找 Generator。
* 列舉 Generator。
* 建立 Generator 實例。
* 保存 Generator metadata。

### 11.2 Input

```python
GeneratorEntry
```

### 11.3 Lookup Input

```text
Generator canonical name or supported alias
```

### 11.4 Output

```python
GeneratorEntry
```

或：

```python
Generator
```

若透過 `create()`。

### 11.5 Guarantees

* 名稱唯一。
* 列舉排序穩定。
* 未知名稱明確失敗。
* `get()` 不執行 factory。
* `list()` 不執行 factory。
* `create()` 不自動執行 `generate()`。
* 每次 create 預設建立獨立實例。

### 11.6 Error Boundary

Registry 錯誤應繼承：

```python
RegistryError
```

---

## 12. Generator Contract

Generator 負責將 GenerateRequest 轉換為 GenerationResult。

核心契約可表示為：

```python
class Generator(Protocol):
    def generate(
        self,
        request: GenerateRequest,
    ) -> GenerationResult:
        ...
```

較完整形式：

```python
class Generator(Protocol):
    def validate(
        self,
        request: GenerateRequest,
    ) -> None:
        ...

    def plan(
        self,
        request: GenerateRequest,
    ) -> GenerationPlan:
        ...

    def execute(
        self,
        plan: GenerationPlan,
    ) -> GenerationResult:
        ...
```

### 12.1 Responsibilities

Generator 應負責：

* 驗證 Generator-specific request。
* 建立 Template Context。
* 建立 Generation Plan。
* 呼叫 Template Renderer。
* 呼叫 Filesystem。
* 協調 Manifest 更新。
* 回傳 GenerationResult。

### 12.2 Prohibited Behavior

Generator 不得：

* 解析 CLI arguments。
* 自行讀取 YAML。
* 直接修改 Registry。
* 依賴目前工作目錄。
* 使用未文件化的全域狀態。
* 靜默覆寫使用者檔案。
* 直接呼叫 `print()` 作為主要結果通道。

### 12.3 Error Boundary

所有 Generator 執行錯誤應繼承：

```python
GeneratorError
```

---

## 13. GenerateRequest Contract

GenerateRequest 描述一次產生作業。

建議：

```python
@dataclass(frozen=True, slots=True)
class GenerateRequest:
    generator_name: str
    target: Path
    values: Mapping[str, Any]
    options: RuntimeOptions
```

具體 Generator 可以定義專用 Request：

```python
@dataclass(frozen=True, slots=True)
class CourseGenerateRequest:
    course_id: str
    title: str
    target: Path
    options: RuntimeOptions
```

### 13.1 Requirements

Request 必須：

* 可驗證。
* 不包含可變全域狀態。
* 明確記錄所有影響結果的輸入。
* 與 CLI parser namespace 分離。
* 不直接攜帶 argparse-specific 物件。

### 13.2 Validation Boundary

通用驗證可以在 dispatch 層處理：

* generator name
* target type
* runtime options

Generator-specific 驗證由具體 Generator 處理：

* course ID 格式
* week number 範圍
* 必要 metadata
* 特定模板選項

---

## 14. Template Renderer Contract

Template Renderer 將模板與 context 轉換為文字內容。

建議介面：

```python
class TemplateRenderer(Protocol):
    def render(
        self,
        template_name: str,
        context: Mapping[str, Any],
    ) -> str:
        ...
```

或：

```python
def render(
    self,
    request: TemplateRenderRequest,
) -> RenderedTemplate:
    ...
```

### 14.1 Responsibilities

* 定位模板。
* 驗證模板名稱。
* 渲染 context。
* 處理 undefined variables。
* 回傳文字內容。
* 統一模板錯誤。

### 14.2 Prohibited Behavior

Template Renderer 不得：

* 寫入目標檔案。
* 建立 Manifest。
* 建立 Generator。
* 修改 Configuration。
* 解析 CLI arguments。
* 決定 overwrite policy。

### 14.3 Input

```text
Template identifier
Template context
Optional rendering options
```

### 14.4 Output

```text
Rendered text
```

### 14.5 Error Boundary

模板錯誤應繼承：

```python
TemplateError
```

可能包含：

```python
TemplateNotFoundError
TemplateRenderError
TemplateContextError
```

---

## 15. Template Context Contract

Template Context 是模板可使用的正式資料介面。

範例：

```python
context = {
    "project": {
        "name": "OpenProjectLab",
        "version": "0.1.0",
    },
    "course": {
        "id": "modern-java",
        "title": "Modern Java in Action",
    },
}
```

### 15.1 Requirements

Template Context 必須：

* 使用穩定鍵名。
* 只包含模板需要的資料。
* 不直接暴露完整 ProjectConfig。
* 不包含 service object。
* 不包含 Registry。
* 不包含 FileSystem。
* 可序列化或可容易檢查。
* 有文件與測試。

### 15.2 Compatibility

修改已公開 context key 可能破壞既有模板，因此必須視為相容性變更。

新增 optional key 通常為 backward-compatible。

移除或重新命名 key 需要 migration。

---

## 16. Generation Plan Contract

Generation Plan 是 Generator 與副作用執行層之間的邊界。

建議模型：

```python
@dataclass(frozen=True, slots=True)
class GenerationPlan:
    generator: str
    operations: tuple["GenerationOperation", ...]
```

操作模型：

```python
@dataclass(frozen=True, slots=True)
class GenerationOperation:
    source_template: str
    destination: Path
    context: Mapping[str, Any]
    write_policy: "WritePolicy"
```

### 16.1 Purpose

Generation Plan 提供：

* dry-run 支援。
* 事前衝突檢查。
* deterministic ordering。
* 測試 Generator 邏輯而不寫檔。
* 產生摘要。
* Manifest 預覽。
* 安全檢查。

### 16.2 Plan Guarantees

Plan 建立完成後應保證：

* destination 唯一或衝突已明確處理。
* 所有 destination 位於允許根目錄。
* 所有 template identifier 合法。
* 操作順序穩定。
* write policy 明確。
* 所有必要 context 已建立。

### 16.3 Plan Validation

執行前必須驗證：

* 重複 destination。
* path traversal。
* 目標存在衝突。
* 不允許的 overwrite。
* 模板缺失。
* 來源與目標規則。
* operation ordering。

---

## 17. Write Policy Contract

建議定義：

```python
from enum import Enum


class WritePolicy(str, Enum):
    CREATE_ONLY = "create-only"
    OVERWRITE = "overwrite"
    SKIP_EXISTING = "skip-existing"
    ERROR_IF_EXISTS = "error-if-exists"
```

或較簡化：

```python
@dataclass(frozen=True, slots=True)
class WritePolicy:
    overwrite: bool = False
    skip_existing: bool = False
```

Policy 必須避免矛盾狀態，例如：

```text
overwrite=true
skip_existing=true
```

建議使用 Enum 表達互斥語意。

---

## 18. Filesystem Contract

Filesystem 是所有核心檔案副作用的主要邊界。

建議介面：

```python
class FileSystem(Protocol):
    def exists(self, path: Path) -> bool:
        ...

    def write_text(
        self,
        path: Path,
        content: str,
        *,
        policy: WritePolicy,
    ) -> "WriteResult":
        ...

    def make_directory(
        self,
        path: Path,
    ) -> None:
        ...
```

### 18.1 Responsibilities

* 建立必要目錄。
* 寫入文字檔案。
* 套用 Write Policy。
* 執行 dry-run 或預覽策略。
* 驗證安全根目錄。
* 統一 filesystem error。
* 回報寫入結果。

### 18.2 Prohibited Behavior

Filesystem 不得：

* 渲染模板。
* 解讀 Generator-specific request。
* 修改 Registry。
* 解析 Configuration。
* 自行決定 Manifest schema。
* 猜測 overwrite 意圖。

### 18.3 Encoding

文字檔案預設使用：

```text
UTF-8
```

換行政策應一致並有文件。

建議儲存庫文字檔使用：

```text
LF
```

### 18.4 Error Boundary

Filesystem 錯誤應繼承：

```python
FileSystemError
```

---

## 19. Filesystem Safety Contract

所有寫入必須符合安全政策。

### 19.1 Root Boundary

目標路徑必須位於允許的 output root 之內。

概念驗證：

```python
resolved_target = target.resolve()
resolved_root = output_root.resolve()

if not resolved_target.is_relative_to(resolved_root):
    raise UnsafePathError(...)
```

### 19.2 Path Traversal

必須拒絕逃離 root 的路徑，例如：

```text
../../outside.txt
```

### 19.3 Existing Files

既有檔案處理必須由 Write Policy 決定。

不得默默覆寫。

### 19.4 Symlink

Symlink 政策必須明確。

至少應測試：

* target 是 symlink。
* parent 是 symlink。
* symlink 指向 root 外部。
* overwrite symlink 的行為。

Milestone 3 若尚未完整支援，應採保守拒絕策略。

---

## 20. Dry-run Contract

Dry-run 應產生完整計畫與結果預覽，但不產生持久副作用。

Dry-run 可以：

* 載入設定。
* 查找 Generator。
* 驗證 request。
* 建立 Generation Plan。
* 驗證模板存在。
* 渲染模板，若需要驗證內容。
* 檢查目標衝突。
* 回傳預計操作。

Dry-run 不得：

* 建立目錄。
* 寫入檔案。
* 修改 Manifest。
* 建立永久快取。
* 修改設定。
* 執行外部命令，除非明確標示為安全預覽。

Dry-run 結果應與正式執行計畫一致。

---

## 21. Manifest Contract

Manifest 記錄 OpenProjectLab 產生與管理的檔案。

建議概念：

```json
{
  "schema_version": 1,
  "project": {
    "name": "example"
  },
  "generations": [
    {
      "generator": "course",
      "generator_version": "0.1.0",
      "files": [
        {
          "path": "courses/example/README.md",
          "status": "created"
        }
      ]
    }
  ]
}
```

### 21.1 Responsibilities

Manifest 應記錄：

* schema version。
* Generator identity。
* Generator source 或版本。
* 產生檔案路徑。
* 檔案操作狀態。
* 必要 provenance。
* Upgrade 所需 metadata。

### 21.2 Prohibited Behavior

Manifest 不得：

* 取代 Configuration。
* 儲存 Secret。
* 任意儲存完整 Template Context。
* 決定檔案內容。
* 自行執行 Generator。
* 自動刪除未追蹤檔案。

### 21.3 Error Boundary

Manifest 錯誤應繼承：

```python
ManifestError
```

---

## 22. Manifest Update Timing

建議流程：

```text
Validate Plan
    │
    ▼
Execute File Operations
    │
    ▼
Collect Write Results
    │
    ▼
Build Manifest Update
    │
    ▼
Persist Manifest
    │
    ▼
Return Generation Result
```

若檔案寫入失敗，Manifest 不應宣稱未完成的檔案已成功產生。

Manifest 更新必須基於實際 WriteResult，而不是預期 Plan。

---

## 23. Generation Result Contract

GenerationResult 是 Generator 與 CLI 之間的主要結果格式。

建議：

```python
@dataclass(frozen=True, slots=True)
class GenerationResult:
    generator: str
    created: tuple[Path, ...] = ()
    updated: tuple[Path, ...] = ()
    skipped: tuple[Path, ...] = ()
    unchanged: tuple[Path, ...] = ()
    warnings: tuple[str, ...] = ()
    dry_run: bool = False
```

可擴充：

```python
failed: tuple[OperationFailure, ...]
manifest_updated: bool
```

### 23.1 Requirements

Result 必須：

* 明確區分 created、updated、skipped。
* 不依賴 `print()` 取得資訊。
* 支援 dry-run。
* 排序穩定。
* 可供 CLI、測試與未來 API 使用。
* 與 Manifest 實際狀態一致。

### 23.2 Success Semantics

成功不一定代表所有檔案都被建立。

例如 `SKIP_EXISTING` 下，全部 skipped 仍可能是成功。

成功條件必須由正式規則定義。

---

## 24. WriteResult Contract

Filesystem 的每次寫入可回傳：

```python
@dataclass(frozen=True, slots=True)
class WriteResult:
    path: Path
    status: "WriteStatus"
```

```python
class WriteStatus(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    SKIPPED = "skipped"
    UNCHANGED = "unchanged"
```

WriteResult 是 GenerationResult 與 Manifest 的事實來源。

---

## 25. Error Hierarchy

建議核心例外結構：

```python
class OpenProjectLabError(Exception):
    pass


class ConfigurationError(OpenProjectLabError):
    pass


class RegistryError(OpenProjectLabError):
    pass


class GeneratorError(OpenProjectLabError):
    pass


class TemplateError(OpenProjectLabError):
    pass


class FileSystemError(OpenProjectLabError):
    pass


class ManifestError(OpenProjectLabError):
    pass
```

進一步細分：

```text
OpenProjectLabError
├── ConfigurationError
│   ├── ConfigurationFileNotFoundError
│   ├── ConfigurationParseError
│   └── ConfigurationValidationError
│
├── RegistryError
│   ├── DuplicateGeneratorError
│   ├── UnknownGeneratorError
│   └── GeneratorConstructionError
│
├── GeneratorError
│   ├── InvalidRequestError
│   ├── GenerationPlanError
│   └── GenerationExecutionError
│
├── TemplateError
│   ├── TemplateNotFoundError
│   ├── TemplateContextError
│   └── TemplateRenderError
│
├── FileSystemError
│   ├── UnsafePathError
│   ├── FileConflictError
│   └── FileWriteError
│
└── ManifestError
    ├── ManifestParseError
    ├── ManifestValidationError
    └── ManifestWriteError
```

---

## 26. Error Ownership

錯誤應由最接近問題的元件建立。

| Problem          | Owner             |
| ---------------- | ----------------- |
| YAML 無法解析        | Configuration     |
| Generator 名稱未知   | Registry          |
| course ID 無效     | Generator         |
| 模板不存在            | Template Renderer |
| 路徑逃離 root        | Filesystem        |
| Manifest JSON 無效 | Manifest          |
| CLI argument 缺失  | CLI parser        |

上層可以包裝錯誤，但不得錯誤分類。

例如模板不存在，不應轉換為 UnknownGeneratorError。

---

## 27. Exception Chaining

包裝底層錯誤時必須保留原始例外：

```python
try:
    ...
except OSError as exc:
    raise FileWriteError(
        f"無法寫入檔案：{path}"
    ) from exc
```

這有利於：

* Debug。
* 日誌。
* 測試。
* 問題診斷。
* 保留底層錯誤脈絡。

---

## 28. CLI Error Mapping

CLI 應將錯誤映射為穩定 exit code。

建議：

| Exit Code | Meaning                            |
| --------: | ---------------------------------- |
|       `0` | Success                            |
|       `1` | General execution failure          |
|       `2` | CLI or configuration error         |
|       `3` | Unknown generator or command       |
|       `4` | Template error                     |
|       `5` | Filesystem conflict or unsafe path |
|       `6` | Manifest error                     |

早期版本可以較簡化，但必須保持一致並有測試。

CLI 一般模式應顯示簡潔錯誤：

```text
錯誤：找不到 Generator：courses
```

Verbose 或 debug 模式才顯示詳細 traceback。

---

## 29. Logging Contract

核心元件應使用 logging，而非直接輸出。

### 29.1 CLI

負責：

* 設定 logging level。
* 選擇 human-readable formatter。
* 將結果轉成使用者輸出。

### 29.2 Core Services

可記錄：

* 載入的設定檔。
* Generator lookup。
* Plan operation count。
* 檔案寫入結果。
* Manifest 更新。
* Plugin registration。
* 警告與錯誤。

### 29.3 Restrictions

不得記錄：

* Secret。
* Token。
* Password。
* 完整敏感設定。
* 不必要的個人資料。
* 巨大的 Template Context。
* 完整 rendered output，除非 debug 且安全。

---

## 30. Determinism Contract

在以下條件相同時：

* OpenProjectLab version
* Configuration
* Runtime Options
* Generator Request
* Templates
* Plugin set
* Input filesystem state

應產生：

* 相同 Generation Plan。
* 相同 operation order。
* 相同 rendered content。
* 等價 Generation Result。
* 相同 Manifest logical content。

不得隱性使用：

* 當前時間。
* 隨機值。
* 不穩定排序。
* 目前工作目錄。
* 未宣告環境變數。
* 網路資料。

若需要 timestamp，應明確注入 Clock。

若需要 random ID，應明確注入 ID provider。

---

## 31. Idempotency Contract

對相同 Request 重複執行時，行為必須由 Write Policy 明確決定。

可能結果：

### CREATE_ONLY

第二次執行失敗，因為檔案已存在。

### SKIP_EXISTING

第二次執行成功，但檔案標記為 skipped。

### OVERWRITE

第二次執行更新內容。

### CONTENT_AWARE

若內容相同，標記 unchanged；不同則 updated。

Generator 不應為了達到 idempotency 而靜默改變 policy。

---

## 32. Atomicity Contract

理想情況下，一個 Generation Plan 應 all-or-nothing。

但在一般檔案系統中，完全 transaction 可能成本較高。

Milestone 3 最低要求：

1. 執行前完成所有可預先驗證的檢查。
2. 操作順序穩定。
3. 寫入失敗立即停止。
4. Manifest 只記錄實際成功操作。
5. GenerationResult 清楚回報部分完成。
6. 不宣稱整體成功。
7. 保留可診斷資訊。

未來可加入：

* staging directory
* atomic rename
* rollback
* transactional manifest update

---

## 33. Partial Failure Contract

若 plan 中部分檔案已寫入後發生失敗：

* 必須回傳或拋出可辨識失敗。
* 必須記錄已完成操作。
* Manifest 不得虛構未完成項目。
* CLI 應顯示專案可能處於部分更新狀態。
* 不應自動刪除使用者既有檔案。
* rollback 必須是明確且經測試的功能。

可定義：

```python
@dataclass(frozen=True, slots=True)
class PartialGenerationState:
    completed: tuple[WriteResult, ...]
    failed_operation: GenerationOperation
```

---

## 34. Validation Boundaries

驗證應分層進行。

### CLI Validation

* 必要 argument。
* argument 基本型別。
* command choice。
* mutually exclusive options。

### Configuration Validation

* YAML 結構。
* 設定鍵型別。
* 路徑解析。
* config version。

### Registry Validation

* Generator name。
* duplicate registration。
* alias conflict。
* factory callable。

### Generator Validation

* Generator-specific request。
* course ID。
* week number。
* metadata completeness。

### Template Validation

* template exists。
* context completeness。
* render syntax。

### Filesystem Validation

* safe target。
* destination conflicts。
* write policy。
* filesystem access。

### Manifest Validation

* schema version。
* JSON structure。
* record integrity。

同一規則不應在多層重複實作。

---

## 35. Public API Policy

核心模組應只公開穩定介面。

建議：

```python
from generator.core.config import ProjectConfig
from generator.core.registry import GeneratorRegistry
from generator.core.models import GenerateRequest
from generator.core.models import GenerationResult
from generator.core.exceptions import OpenProjectLabError
```

內部 helper 應保持 private：

```python
_validate_name
_resolve_path
_normalize_context
_build_internal_plan
_commit_manifest
```

外部程式不得依賴：

* private attributes。
* 內部 dict 格式。
* module import side effects。
* 未文件化 exception message。
* 具體 collection 實作。

---

## 36. Protocol-first Design

對可替換服務應優先定義 Protocol。

例如：

```python
class TemplateRenderer(Protocol):
    def render(
        self,
        template_name: str,
        context: Mapping[str, Any],
    ) -> str:
        ...
```

```python
class FileSystem(Protocol):
    def write_text(
        self,
        path: Path,
        content: str,
        *,
        policy: WritePolicy,
    ) -> WriteResult:
        ...
```

```python
class ManifestStore(Protocol):
    def record(
        self,
        result: GenerationResult,
    ) -> None:
        ...
```

優點：

* Generator 容易測試。
* 可使用 fake service。
* 降低具體實作耦合。
* 支援未來 Plugin 與不同後端。

---

## 37. Dependency Injection Contract

依賴應由外部注入。

推薦：

```python
generator = CourseGenerator(
    renderer=renderer,
    filesystem=filesystem,
    manifest=manifest,
)
```

不推薦：

```python
class CourseGenerator:
    def __init__(self) -> None:
        self.renderer = TemplateRenderer(...)
        self.filesystem = FileSystem(...)
```

Generator 不應自行定位全域設定或建立共享服務。

---

## 38. Service Lifetime

建議生命週期：

| Service          | Lifetime                         |
| ---------------- | -------------------------------- |
| ProjectConfig    | One CLI execution                |
| RuntimeOptions   | One command                      |
| Registry         | One CLI execution                |
| TemplateRenderer | One CLI execution                |
| Filesystem       | One CLI execution                |
| ManifestStore    | One CLI execution or one project |
| Generator        | One generation request           |
| GenerationPlan   | One generation request           |
| GenerationResult | One generation request           |

具體生命週期可調整，但必須明確且可測試。

---

## 39. Immutability Contract

應優先不可變的模型：

* ProjectConfig
* RuntimeOptions
* GeneratorMetadata
* GeneratorEntry
* GenerateRequest
* GenerationOperation
* GenerationPlan
* WriteResult
* GenerationResult

不可變性有助於：

* 減少跨元件副作用。
* 保持 deterministic behavior。
* 提高平行安全性。
* 簡化測試。
* 降低意外修改。

---

## 40. Collection Contract

對外回傳 collection 時，建議使用：

```python
tuple
Mapping
Sequence
```

避免直接暴露內部 list 或 dict。

例如：

```python
def names(self) -> tuple[str, ...]:
    ...
```

```python
def operations(self) -> tuple[GenerationOperation, ...]:
    ...
```

內部可使用 mutable collection 建構，對外應回傳穩定只讀形式。

---

## 41. Path Contract

所有核心路徑應使用：

```python
pathlib.Path
```

而不是任意混用字串。

在外部序列化邊界才轉為：

```text
POSIX-style relative string
```

Manifest 中建議儲存相對於 project root 的正斜線路徑：

```text
courses/example/README.md
```

不建議儲存機器特定絕對路徑：

```text
F:\OpenProjectLab\courses\example\README.md
```

---

## 42. Encoding and Newline Contract

所有專案文字輸出預設：

```text
Encoding: UTF-8
Newline: LF
```

使用：

```python
path.write_text(
    content,
    encoding="utf-8",
    newline="\n",
)
```

若 Python 版本或 API 支援情況不同，應由 Filesystem 統一處理。

模板本身也應採 UTF-8 與 LF。

---

## 43. CLI Output Contract

CLI 輸出應由 GenerationResult 產生，而不是由 Generator 隨意列印。

成功範例：

```text
Generator: course
Created: 4
Updated: 0
Skipped: 1
```

Dry-run：

```text
Dry run: no files were written
Would create:
  courses/example/README.md
  courses/example/course.yaml
```

錯誤：

```text
錯誤：目標檔案已存在：courses/example/README.md
```

Machine-readable output 未來可透過：

```powershell
opl course ... --output-format json
```

但應使用相同 GenerationResult，而不是另一套執行流程。

---

## 44. Versioning Contract

核心框架需區分：

* OPL application version
* Configuration schema version
* Manifest schema version
* Generator contract version
* Plugin API version
* Template pack version

這些版本不可混為單一數字。

範例：

```text
OPL version: 0.3.0
Config schema: 1
Manifest schema: 1
Generator API: 1
Plugin API: 1
Template pack: 2026.1
```

---

## 45. Backward Compatibility Contract

以下項目視為公開契約：

* CLI command 名稱。
* CLI option 名稱。
* Generator canonical name。
* Generator alias。
* Configuration key。
* Configuration default。
* Template context key。
* Manifest schema。
* 核心 exception 類型。
* GenerationResult 欄位。
* Plugin registration contract。

不相容變更必須：

1. 有 ADR。
2. 更新 Roadmap。
3. 更新 CHANGELOG。
4. 提供 migration guide。
5. 加入 compatibility tests。
6. 適當提高版本。

---

## 46. Deprecation Contract

Deprecated 功能至少應經歷：

```text
Available
    ↓
Deprecated with warning
    ↓
Migration period
    ↓
Removal in documented version
```

不得在沒有警告與 migration 的情況下直接移除已公開功能。

警告應包含：

* 淘汰項目。
* 替代方案。
* 預計移除版本，若已知。
* migration 文件位置。

---

## 47. Plugin Boundary Contract

Plugin 不得繞過核心服務直接修改內部狀態。

Plugin 可透過正式介面：

* 提供 GeneratorEntry。
* 提供 Template pack。
* 提供 Plugin configuration validator。
* 提供 metadata。
* 使用正式 Filesystem contract。
* 回傳 GenerationResult。

Plugin 不得：

* 修改 Registry private mapping。
* 取代核心 Generator，除非正式 override policy。
* 修改 ProjectConfig 物件。
* 直接寫入核心 Manifest 內部結構。
* 依賴 private module。
* 於 import 時執行不可預期副作用。

---

## 48. Testing Architecture

核心契約需要多層測試。

```text
Unit Tests
    │
    ▼
Contract Tests
    │
    ▼
Integration Tests
    │
    ▼
End-to-End Tests
```

### Unit Tests

測試單一元件。

### Contract Tests

確認公開契約不被破壞。

### Integration Tests

確認元件間協作。

### End-to-End Tests

確認 CLI 到實際檔案輸出的完整流程。

---

## 49. Required Unit Test Areas

### Configuration

* YAML parsing。
* section validation。
* path resolution。
* defaults。
* errors。

### Registry

* registration。
* duplicate handling。
* lookup。
* ordering。
* factory construction。

### Generator

* request validation。
* plan creation。
* deterministic operations。
* result mapping。

### Template

* template lookup。
* rendering。
* missing context。
* syntax error。

### Filesystem

* write policy。
* safe root。
* overwrite。
* dry-run。
* encoding。

### Manifest

* load。
* validate。
* update。
* schema version。
* write failure。

---

## 50. Core Contract Tests

建議建立：

```text
tests/contracts/
├── test_configuration_contract.py
├── test_registry_contract.py
├── test_generator_contract.py
├── test_template_contract.py
├── test_filesystem_contract.py
├── test_manifest_contract.py
└── test_generation_result_contract.py
```

契約測試應確認：

* 公開介面。
* 預設值。
* exception 類型。
* collection order。
* path semantics。
* dry-run semantics。
* write status。
* schema version。

---

## 51. Generator Contract Test Suite

所有核心與 Plugin Generator 應可共用一組 contract tests。

概念：

```python
class GeneratorContractTests:
    def make_generator(self) -> Generator:
        raise NotImplementedError

    def make_valid_request(self) -> GenerateRequest:
        raise NotImplementedError

    def test_plan_is_deterministic(self) -> None:
        ...

    def test_dry_run_has_no_side_effects(self) -> None:
        ...

    def test_result_matches_operations(self) -> None:
        ...

    def test_invalid_request_fails(self) -> None:
        ...
```

具體 Generator 測試繼承或套用相同測試函式。

---

## 52. Integration Test Matrix

至少應涵蓋：

| Configuration | Generator | Runtime Mode     | Expected             |
| ------------- | --------- | ---------------- | -------------------- |
| Valid         | bootstrap | normal           | project created      |
| Valid         | bootstrap | dry-run          | no files             |
| Valid         | course    | normal           | course files created |
| Valid         | week      | normal           | week files created   |
| Invalid       | any       | normal           | configuration error  |
| Valid         | unknown   | normal           | registry error       |
| Valid         | course    | conflict         | file conflict        |
| Valid         | course    | overwrite        | files updated        |
| Valid         | course    | skip             | files skipped        |
| Valid         | any       | manifest failure | failure reported     |

---

## 53. End-to-End Test Contract

End-to-end tests 應：

1. 使用 temporary directory。
2. 建立真實 configuration。
3. 執行 CLI entry point。
4. 驗證 exit code。
5. 驗證 stdout 與 stderr。
6. 驗證產生檔案。
7. 驗證檔案內容。
8. 驗證 Manifest。
9. 驗證重複執行。
10. 驗證 dry-run 無副作用。

避免依賴使用者機器既有目錄。

---

## 54. Golden File Testing

對穩定模板輸出可使用 golden tests。

流程：

```text
Generator Request
      │
      ▼
Render Output
      │
      ▼
Compare with tests/golden/
```

Golden tests 必須：

* 明確審查差異。
* 不以自動更新掩蓋問題。
* 使用 UTF-8 與 LF。
* 避免 timestamp 或隨機內容。
* 適當正規化平台差異。

---

## 55. Fake Services

Generator 單元測試應使用 fake service。

例如：

```python
class FakeRenderer:
    def render(
        self,
        template_name: str,
        context: Mapping[str, Any],
    ) -> str:
        return f"rendered:{template_name}"
```

```python
class MemoryFileSystem:
    def __init__(self) -> None:
        self.files: dict[Path, str] = {}
```

```python
class FakeManifestStore:
    def __init__(self) -> None:
        self.results: list[GenerationResult] = []
```

這可以避免每個 Generator 單元測試都操作真實檔案系統。

---

## 56. CI Contract

每個 Pull Request 至少應執行：

```powershell
pre-commit run --all-files
python -m pytest
```

建議完整 CI：

```text
Lint
Formatting
Type Check
Unit Tests
Contract Tests
Integration Tests
Documentation Checks
Package Build
CLI Smoke Test
```

若支援多 Python 版本，CI 應建立 matrix。

---

## 57. Documentation Contract

每個核心元件應有：

### Architecture Document

描述責任、邊界、資料流與設計決策。

### Reference Document

描述正式 API、欄位、選項與精確行為。

### User Guide

描述使用者如何操作。

### Development Guide

描述開發者如何擴充與測試。

建議對應：

```text
docs/architecture/configuration.md
docs/architecture/registry.md
docs/architecture/generator.md
docs/architecture/template.md
docs/architecture/core-contract.md

docs/reference/filesystem.md
docs/reference/template.md
docs/reference/generators.md

docs/configuration.md
docs/cli.md
```

---

## 58. Required Change Set

每次新增核心功能，Pull Request 應同步包含：

1. Architecture update。
2. Implementation。
3. Unit tests。
4. Contract tests。
5. Integration tests。
6. User or reference documentation。
7. Code Review Checklist。
8. CHANGELOG entry，若為使用者可見變更。
9. ADR，若為重要架構決策。

只有程式碼而沒有測試與文件，不視為完整功能。

---

## 59. Recommended Core Package Layout

```text
generator/
├── cli/
│   ├── main.py
│   ├── parser.py
│   └── commands/
│
├── core/
│   ├── config.py
│   ├── registry.py
│   ├── models.py
│   ├── protocols.py
│   ├── exceptions.py
│   ├── filesystem.py
│   ├── manifest.py
│   └── runtime.py
│
├── generators/
│   ├── bootstrap_generator.py
│   ├── course_generator.py
│   └── week_generator.py
│
└── template/
    ├── renderer.py
    └── context.py
```

此結構是方向，不要求一次性重構。

拆分應基於實際責任與維護需求。

---

## 60. Milestone 3 Completion Criteria

Milestone 3 Core Framework 至少需完成：

### Configuration

* 穩定載入。
* 安全 YAML。
* 路徑解析。
* 明確錯誤。
* 單元與整合測試。

### Registry

* 單一 Generator catalog。
* duplicate handling。
* stable listing。
* factory construction。
* 無全域 mutable singleton。

### Generator

* 明確 Request。
* 可測試 Plan。
* 統一 Result。
* dry-run。
* deterministic behavior。

### Template

* 穩定 render contract。
* context schema。
* template errors。
* 無檔案副作用。

### Filesystem

* 安全 root。
* write policy。
* UTF-8。
* dry-run。
* result reporting。

### Manifest

* schema version。
* 實際操作記錄。
* 安全更新。
* error handling。

### Integration

* CLI 使用上述所有契約。
* 完整 pytest 通過。
* pre-commit 通過。
* 文件同步。
* Code Review Checklist 完成。

---

## 61. Milestone 3 Recommended Sequence

```text
1. Architecture Documents
   ├── generator.md
   ├── configuration.md
   ├── registry.md
   └── core-contract.md

2. Core Models
   ├── RuntimeOptions
   ├── GenerateRequest
   ├── GenerationPlan
   ├── WriteResult
   └── GenerationResult

3. Registry Stabilization

4. Configuration Stabilization

5. Generator Plan Separation

6. Filesystem Write Policy

7. Manifest Result Integration

8. Contract Tests

9. CLI Integration Cleanup

10. Documentation and Review
```

---

## 62. Architecture Decision Requirements

以下變更應建立 ADR：

* 導入 typed Configuration。
* 採用 Generation Plan。
* 採用 Registry factory。
* Manifest schema version 變更。
* Generator API version。
* Plugin API。
* Write Policy。
* Transaction 或 rollback。
* Package layout 大幅重構。
* 移除或重新命名公開 Generator。
* 改變相對路徑解析基準。

---

## 63. Code Review Checklist

### Design First

* [ ] 問題是否已明確描述？
* [ ] 是否先更新架構文件？
* [ ] 元件責任是否清楚？
* [ ] 是否定義輸入、輸出與錯誤？
* [ ] 是否評估替代方案？
* [ ] 是否評估 backward compatibility？
* [ ] 是否需要 ADR？
* [ ] 是否避免為未存在需求過度設計？

### Dependency Direction

* [ ] CLI 是否只作為 Composition Root 與 presentation layer？
* [ ] Configuration 是否不依賴 CLI？
* [ ] Registry 是否不依賴具體 Generator？
* [ ] Generator 是否不解析 CLI arguments？
* [ ] Template 是否不寫入檔案？
* [ ] Filesystem 是否不渲染模板？
* [ ] Manifest 是否不執行 Generator？
* [ ] 是否沒有循環依賴？
* [ ] 是否避免 service locator 與全域 singleton？

### Configuration

* [ ] 是否安全載入 YAML？
* [ ] 是否驗證所有核心區段？
* [ ] 是否集中管理預設值？
* [ ] 是否明確解析相對路徑？
* [ ] 是否不依賴目前工作目錄？
* [ ] 是否區分 ProjectConfig 與 RuntimeOptions？
* [ ] 是否保持載入無副作用？
* [ ] 是否使用 ConfigurationError？
* [ ] 是否有路徑與錯誤測試？

### Registry

* [ ] 是否為 Generator catalog 唯一來源？
* [ ] 是否拒絕重複名稱？
* [ ] 是否穩定排序？
* [ ] 是否使用 factory？
* [ ] 每次 create 是否建立獨立實例？
* [ ] lookup 是否不執行 factory？
* [ ] 是否避免 process-wide mutable state？
* [ ] Plugin 衝突政策是否明確？
* [ ] 是否有 contract tests？

### Generator

* [ ] 是否接收正式 Request model？
* [ ] 是否不接收 argparse Namespace？
* [ ] 是否有 request validation？
* [ ] 是否可以建立 Generation Plan？
* [ ] Plan 是否 deterministic？
* [ ] 是否透過注入取得 services？
* [ ] 是否不直接建立具體 Filesystem 或 Renderer？
* [ ] 是否不直接 print？
* [ ] 是否回傳 GenerationResult？
* [ ] 是否有 dry-run 測試？

### Template

* [ ] Template Context 是否最小化？
* [ ] 是否不直接暴露完整 ProjectConfig？
* [ ] context key 是否文件化？
* [ ] undefined variable policy 是否明確？
* [ ] Template Renderer 是否無檔案副作用？
* [ ] template lookup 是否安全？
* [ ] 是否使用 TemplateError？
* [ ] 是否有 render 與 missing-template 測試？
* [ ] context compatibility 是否評估？

### Generation Plan

* [ ] operation 是否有穩定排序？
* [ ] destination 是否唯一？
* [ ] template identifier 是否有效？
* [ ] write policy 是否明確？
* [ ] 是否檢查 path traversal？
* [ ] 是否在副作用前完成驗證？
* [ ] dry-run 是否使用同一份 plan？
* [ ] plan 是否可獨立測試？
* [ ] 是否避免在 plan 階段寫檔？

### Filesystem

* [ ] 所有寫入是否集中於 Filesystem？
* [ ] 是否使用 Path？
* [ ] 是否限制 output root？
* [ ] 是否拒絕 unsafe path？
* [ ] overwrite policy 是否明確？
* [ ] 是否使用 UTF-8？
* [ ] newline 是否一致？
* [ ] dry-run 是否沒有副作用？
* [ ] 是否回傳 WriteResult？
* [ ] 是否有 symlink 政策與測試？

### Manifest

* [ ] 是否有 schema version？
* [ ] 是否只記錄實際成功操作？
* [ ] path 是否儲存為 portable relative path？
* [ ] 是否不儲存 Secret？
* [ ] 是否不儲存不必要 context？
* [ ] 寫入失敗是否清楚回報？
* [ ] 是否避免宣稱未完成操作成功？
* [ ] 是否有 parse、validation 與 update 測試？
* [ ] 是否評估 atomic write？

### Error Handling

* [ ] 是否使用正確 error owner？
* [ ] 是否保留 exception chaining？
* [ ] 是否沒有錯誤分類混淆？
* [ ] 訊息是否包含可行動資訊？
* [ ] CLI 是否映射穩定 exit code？
* [ ] 一般模式是否不輸出 traceback？
* [ ] debug 模式是否保留完整資訊？
* [ ] 是否避免顯示 Secret？
* [ ] partial failure 是否清楚表達？

### Determinism and Idempotency

* [ ] 相同輸入是否產生相同 plan？
* [ ] collection 是否穩定排序？
* [ ] 是否避免隱性 timestamp？
* [ ] 是否避免隱性 random？
* [ ] 是否避免依賴 CWD？
* [ ] write policy 是否定義重複執行行為？
* [ ] unchanged、skipped、updated 是否區分？
* [ ] Manifest 是否與實際結果一致？
* [ ] 是否有重複執行測試？

### Security

* [ ] 設定檔是否視為不可信輸入？
* [ ] 是否使用 safe YAML loader？
* [ ] 是否拒絕 path traversal？
* [ ] 是否處理 symlink escape？
* [ ] Plugin 是否不能隱性覆寫核心 Generator？
* [ ] Template path 是否受限制？
* [ ] 是否不執行設定內容？
* [ ] 日誌與 Manifest 是否不含 Secret？
* [ ] 寫入範圍是否最小化？

### Testing

* [ ] 是否新增單元測試？
* [ ] 是否新增 contract tests？
* [ ] 是否新增 integration tests？
* [ ] 是否新增 end-to-end 測試？
* [ ] dry-run 是否有測試？
* [ ] error path 是否有測試？
* [ ] partial failure 是否有測試？
* [ ] path safety 是否有測試？
* [ ] Windows path 是否有測試？
* [ ] 中文與空白路徑是否有測試？
* [ ] 完整 pytest 是否通過？
* [ ] pre-commit 是否通過？

### Documentation

* [ ] 架構文件是否更新？
* [ ] Reference 文件是否更新？
* [ ] User guide 是否更新？
* [ ] Development guide 是否更新？
* [ ] CLI help 是否同步？
* [ ] Configuration example 是否同步？
* [ ] Template context 是否同步？
* [ ] Manifest schema 是否同步？
* [ ] CHANGELOG 是否更新？
* [ ] ADR 是否新增或更新？
* [ ] Roadmap 是否更新？

### Automation

* [ ] 新規則是否可由測試自動驗證？
* [ ] 是否加入 pre-commit 檢查？
* [ ] CI 是否執行新增測試？
* [ ] 是否加入 schema validation？
* [ ] 是否避免依賴人工手動步驟？
* [ ] 是否有 CLI smoke test？
* [ ] 是否能從乾淨環境重現？
* [ ] 文件範例是否可自動測試？

---

## 64. Acceptance Criteria

本 Core Framework Contract 可視為正式建立，至少需符合：

* 核心元件責任與依賴方向已清楚定義。
* Configuration、Registry、Generator、Template、Filesystem 與 Manifest 各有明確邊界。
* GenerateRequest、GenerationPlan、WriteResult 與 GenerationResult 的角色已定義。
* 所有核心副作用集中且可測試。
* dry-run 行為有一致契約。
* error hierarchy 與 owner 已定義。
* deterministic 與 idempotent 行為已有政策。
* backward compatibility 與 versioning 已定義。
* Plugin 不得繞過核心契約。
* 單元、契約、整合與端對端測試策略已建立。
* 文件、測試、自動化與 Code Review Checklist 同步。
* Milestone 3 的後續實作可以依本文件逐步執行。

---

## 65. Related Documents

* `docs/architecture/generator.md`
* `docs/architecture/configuration.md`
* `docs/architecture/registry.md`
* `docs/architecture/template.md`
* `docs/reference/filesystem.md`
* `docs/reference/template.md`
* `docs/reference/generators.md`
* `docs/configuration.md`
* `docs/cli.md`
* `docs/ROADMAP.md`
* `docs/adr/`
* `generator/cli/main.py`
* `generator/core/config.py`
* `generator/core/registry.py`
* `generator/core/filesystem.py`
* `generator/core/manifest.py`
* `generator/core/exceptions.py`
* `generator/template/`
* `generator/generators/`
* `tests/core/`
* `tests/contracts/`
* `tests/integration/`
