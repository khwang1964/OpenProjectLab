# Configuration Architecture

## 1. Purpose

OpenProjectLab 的 Configuration Framework 負責將外部設定檔轉換成核心框架可安全使用、可驗證且一致的設定物件。

Configuration 是 CLI、Generator、Template、Filesystem、Manifest 與 Plugin Framework 之間的重要基礎設施。它不應只是 YAML 檔案的直接映射，而應提供明確的設定契約、路徑語意、錯誤處理與相容性規則。

本文件定義 OpenProjectLab Configuration Framework 的架構、責任、資料流程、擴充方式與測試要求。

---

## 2. Goals

Configuration Framework 的主要目標如下：

1. 提供單一且明確的設定載入入口。
2. 驗證設定檔的結構與資料型別。
3. 將相對路徑解析為穩定且可預期的絕對路徑。
4. 區分使用者設定、系統預設值與執行期參數。
5. 支援 CLI 與 Generator 共用一致的設定模型。
6. 提供可理解且可行動的錯誤訊息。
7. 保持設定載入流程可測試、可預測且無隱性副作用。
8. 為未來的 Plugin Configuration 與設定版本遷移保留擴充空間。

---

## 3. Non-goals

Configuration Framework 不負責：

* 執行專案產生流程。
* 直接建立或修改檔案。
* 渲染模板。
* 註冊 Generator。
* 自動下載遠端設定。
* 儲存機密資訊。
* 將任意 Python 程式碼作為設定執行。
* 在未明確定義規則時，自動修正錯誤設定。
* 將所有業務驗證集中在 Configuration 層。

Configuration Framework 驗證的是「設定是否有效」，而 Generator 驗證的是「該設定是否適用於特定產生作業」。

---

## 4. Architectural Context

Configuration 位於 CLI 與核心服務之間。

```text
User
  │
  ▼
CLI Arguments
  │
  ▼
Configuration Loader
  │
  ├── Read YAML
  ├── Parse Structure
  ├── Validate Sections
  ├── Apply Defaults
  └── Resolve Paths
  │
  ▼
ProjectConfig
  │
  ├── CLI
  ├── Generator Registry
  ├── Generators
  ├── Template Renderer
  ├── Filesystem
  └── Plugin Loader
```

Configuration Framework 應將外部、不可信且可能不完整的輸入，轉換成內部可信的設定模型。

---

## 5. Dependency Direction

Configuration Framework 可以依賴：

* Python 標準函式庫
* YAML parser
* 核心例外類別
* Configuration 專用模型與驗證工具

Configuration Framework 不應依賴：

* CLI parser 實作
* 具體 Generator
* Template Renderer
* Manifest Writer
* Plugin 實作
* 專案產生流程

建議依賴方向如下：

```text
CLI
 │
 ▼
Configuration
 │
 ▼
Core Models

Generator ───────► Configuration Model
Template  ───────► Configuration Model
Filesystem ──────► Resolved Paths
```

Configuration 是被上層元件使用的核心服務，不應反向依賴使用者。

---

## 6. Current Configuration Model

目前核心設定模型可包含以下區段：

```python
@dataclass(slots=True)
class ProjectConfig:
    project: dict[str, Any] = field(default_factory=dict)
    paths: dict[str, Any] = field(default_factory=dict)
    generator: dict[str, Any] = field(default_factory=dict)
    plugins: dict[str, Any] = field(default_factory=dict)
```

目前區段的概念責任如下：

| Section     | Responsibility           |
| ----------- | ------------------------ |
| `project`   | 專案名稱、描述、版本與專案層級資訊        |
| `paths`     | 模板、輸出、課程與其他檔案系統位置        |
| `generator` | Generator 行為與預設產生選項      |
| `plugins`   | Plugin 啟用狀態與 Plugin 專用設定 |

這個模型適合作為 Milestone 3 的基礎，但長期應逐步從通用字典演進為具型別的分區設定模型。

---

## 7. Configuration Sources

OpenProjectLab 的設定值可能來自多個來源：

1. 內建預設值
2. 專案設定檔
3. 使用者指定的設定檔
4. CLI 參數
5. Generator Request
6. 未來可能支援的環境變數

建議覆寫優先順序為：

```text
Generator Request
        ↓
CLI Arguments
        ↓
Explicit Configuration File
        ↓
Project Configuration File
        ↓
Built-in Defaults
```

越靠上的來源優先權越高。

Configuration Framework 必須清楚記錄哪些來源已正式支援。尚未實作的來源不可只存在於文件中而沒有測試。

---

## 8. Default Configuration File

CLI 可以提供預設設定檔，例如：

```text
config/default.yaml
```

預設設定檔的位置必須依據專案根目錄或已安裝套件資源解析，不應依賴目前工作目錄。

錯誤示例：

```python
Path("config/default.yaml")
```

當 CLI 從不同目錄執行時，此寫法可能指向錯誤位置。

建議：

```python
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "default.yaml"
```

若未來採用正式 Python package resource，應改由 `importlib.resources` 載入內建設定。

---

## 9. Configuration Loading Flow

建議的設定載入流程如下：

```text
Receive configuration path
          │
          ▼
Validate file existence
          │
          ▼
Read UTF-8 text
          │
          ▼
Parse YAML
          │
          ▼
Validate top-level mapping
          │
          ▼
Validate known sections
          │
          ▼
Apply defaults
          │
          ▼
Resolve paths
          │
          ▼
Construct ProjectConfig
          │
          ▼
Return immutable or controlled configuration object
```

每一個步驟都應具有明確錯誤邊界。

---

## 10. Loading Interface

建議保留單一公開載入入口：

```python
@classmethod
def load(cls, path: Path) -> "ProjectConfig":
    ...
```

使用方式：

```python
config = ProjectConfig.load(Path("config/default.yaml"))
```

此介面應保證：

* 輸入檔案存在。
* YAML 可以解析。
* YAML 頂層為 mapping。
* 已知區段具有正確型別。
* 回傳有效的 `ProjectConfig`。
* 解析錯誤統一轉換為 `ConfigurationError`。

---

## 11. File Reading

設定檔必須明確使用 UTF-8：

```python
text = path.read_text(encoding="utf-8")
```

不應依賴作業系統預設編碼，因為 OpenProjectLab 可能包含中文課程名稱、說明與路徑。

讀取失敗時，應保留原始例外作為 exception chaining：

```python
try:
    text = path.read_text(encoding="utf-8")
except OSError as exc:
    raise ConfigurationError(
        f"無法讀取設定檔：{path}"
    ) from exc
```

---

## 12. YAML Parsing

YAML 必須使用安全載入方式：

```python
data = yaml.safe_load(text)
```

禁止使用：

```python
yaml.load(text)
```

除非明確指定安全 Loader。

空白設定檔可視為空 mapping：

```python
data = yaml.safe_load(text) or {}
```

但空白設定檔是否有效，應由產品規則決定。若所有設定均有預設值，可以允許；若缺少必要區段，則應在驗證階段回報。

---

## 13. Top-level Validation

設定檔頂層必須是 mapping。

有效：

```yaml
project:
  name: example
```

無效：

```yaml
- project
- paths
```

驗證範例：

```python
if not isinstance(data, dict):
    raise ConfigurationError(
        "設定檔最上層必須是 mapping"
    )
```

不應讓 list、string、integer 或 boolean 靜默通過。

---

## 14. Section Validation

每個正式支援的設定區段都必須是 mapping。

例如：

```python
sections = ("project", "paths", "generator", "plugins")

for section in sections:
    value = data.get(section, {})

    if not isinstance(value, dict):
        raise ConfigurationError(
            f"設定區段必須是 mapping：{section}"
        )
```

有效：

```yaml
paths:
  template_root: templates
```

無效：

```yaml
paths: templates
```

錯誤訊息必須包含：

* 問題區段
* 預期型別
* 實際問題
* 設定檔位置，若可取得

---

## 15. Unknown Sections

對於未識別的頂層區段，可採用以下策略之一：

### Strict Mode

發現未知區段立即失敗。

優點：

* 可及早發現拼字錯誤。
* 設定契約更明確。

缺點：

* 降低向前相容性。
* Plugin 擴充較困難。

### Permissive Mode

忽略或保留未知區段。

優點：

* 較容易擴充。
* 可以支援外部 Plugin。

缺點：

* 拼字錯誤可能被忽略。

### Recommended Policy

核心區段採取嚴格驗證，Plugin 專用設定集中放在 `plugins` 之下。

例如：

```yaml
plugins:
  enabled:
    - syllabus
  settings:
    syllabus:
      language: zh-TW
```

不建議讓 Plugin 任意建立頂層設定區段。

---

## 16. Required and Optional Values

每個設定鍵應明確分類為：

* Required
* Optional with default
* Optional without default
* Deprecated
* Reserved

例如：

| Key                   | Requirement | Default                  |
| --------------------- | ----------- | ------------------------ |
| `project.name`        | Optional    | `openprojectlab-project` |
| `paths.template_root` | Required    | None                     |
| `paths.output_root`   | Optional    | `build`                  |
| `generator.overwrite` | Optional    | `false`                  |
| `plugins.enabled`     | Optional    | `[]`                     |

不得只透過程式中的 `dict.get()` 隱性決定契約。正式設定鍵必須在文件與測試中定義。

---

## 17. Default Values

預設值應集中管理，不應散落在 CLI、Generator 與 Template Renderer 中。

不建議：

```python
overwrite = config.generator.get("overwrite", False)
```

同一個預設值若在多處重複，未來容易不一致。

建議：

```python
@dataclass(frozen=True, slots=True)
class GeneratorConfig:
    overwrite: bool = False
    dry_run: bool = False
```

或由 Configuration Builder 統一套用：

```python
generator_data = {
    "overwrite": False,
    "dry_run": False,
    **data.get("generator", {}),
}
```

---

## 18. Path Configuration

路徑是 Configuration Framework 最重要的責任之一。

典型路徑設定可能包括：

```yaml
paths:
  template_root: templates
  output_root: build
  course_root: courses
  manifest_path: .opl/manifest.json
```

所有路徑應具有明確的解析基準。

---

## 19. Relative Path Semantics

相對路徑不可依賴執行 CLI 時的目前工作目錄，除非文件明確定義如此。

建議將相對路徑解析基準定義為：

1. 設定檔所在目錄；或
2. OpenProjectLab 專案根目錄。

較建議使用「設定檔所在目錄」，因為設定檔與它引用的資源可以一起移動。

例如：

```text
F:\OpenProjectLab\config\default.yaml
```

內容：

```yaml
paths:
  template_root: ../templates
```

解析結果：

```text
F:\OpenProjectLab\templates
```

解析程式：

```python
base_dir = config_path.parent.resolve()
template_root = (base_dir / raw_path).resolve()
```

---

## 20. Absolute Path Semantics

若設定值已是絕對路徑，應保留其絕對語意。

```python
candidate = Path(raw_path)

if candidate.is_absolute():
    resolved = candidate.resolve()
else:
    resolved = (base_dir / candidate).resolve()
```

Windows 路徑範例：

```yaml
paths:
  template_root: F:/OpenProjectLab/templates
```

YAML 中建議使用正斜線，避免反斜線跳脫問題。

---

## 21. Path Normalization

路徑解析後應進行合理正規化：

* 展開 `.` 與 `..`
* 轉換為絕對路徑
* 保留原始大小寫語意
* 不應在載入設定時自動建立目錄
* 不應在載入設定時刪除任何檔案
* 不應在沒有需求時強制解析 symlink

Configuration loading 應保持無副作用。

---

## 22. Path Existence Validation

不同路徑需要不同驗證策略。

### Input Paths

例如模板根目錄。

通常應驗證存在：

```python
if not template_root.exists():
    raise ConfigurationError(
        f"找不到模板根目錄：{template_root}"
    )
```

### Output Paths

例如建置輸出目錄。

載入設定時可允許不存在，由 Generator 或 Filesystem 在執行時建立。

### File Targets

例如 Manifest 檔案。

應驗證父目錄是否合理，但不應要求檔案預先存在。

路徑驗證必須依照用途，而不是所有路徑一律使用同一規則。

---

## 23. Typed Configuration Evolution

目前使用 `dict[str, Any]` 可以快速支援早期開發，但長期會產生以下問題：

* 拼字錯誤只能在執行期發現。
* IDE 無法提供完整提示。
* 預設值散落。
* 型別驗證重複。
* 文件與程式容易不一致。

Milestone 3 建議逐步演進為分區型別模型：

```python
@dataclass(frozen=True, slots=True)
class ProjectMetadataConfig:
    name: str
    description: str = ""
    version: str = "0.1.0"


@dataclass(frozen=True, slots=True)
class PathsConfig:
    template_root: Path
    output_root: Path
    course_root: Path
    manifest_path: Path


@dataclass(frozen=True, slots=True)
class GeneratorSettings:
    overwrite: bool = False
    dry_run: bool = False


@dataclass(frozen=True, slots=True)
class PluginSettings:
    enabled: tuple[str, ...] = ()
    settings: Mapping[str, Mapping[str, Any]] = field(
        default_factory=dict
    )


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    project: ProjectMetadataConfig
    paths: PathsConfig
    generator: GeneratorSettings
    plugins: PluginSettings
```

此變更應採漸進方式，不應一次破壞所有現有 Generator。

---

## 24. Immutability

設定載入完成後，原則上不應被任意修改。

推薦使用：

```python
@dataclass(frozen=True, slots=True)
```

不可變設定具有以下優點：

* 避免 Generator 意外修改全域設定。
* 更容易推理。
* 更容易測試。
* 提高併行執行安全性。
* 有利於 deterministic generation。

若需要建立覆寫版本，應建立新物件：

```python
effective_config = replace(
    config.generator,
    dry_run=True,
)
```

而不是直接修改原物件。

---

## 25. Configuration Overrides

CLI 參數可能覆寫設定檔值。

例如：

```powershell
opl bootstrap sample --dry-run
```

即使設定檔中：

```yaml
generator:
  dry_run: false
```

本次執行仍應使用：

```text
dry_run = true
```

覆寫流程應明確：

```text
Loaded ProjectConfig
        │
        ▼
CLI Override Mapping
        │
        ▼
Effective Runtime Configuration
```

不建議直接修改原始 `ProjectConfig`。

可以建立：

```python
@dataclass(frozen=True, slots=True)
class RuntimeOptions:
    dry_run: bool
    overwrite: bool
    verbose: bool
```

將長期設定與單次執行選項分離。

---

## 26. Configuration and Generator Request

Configuration 與 Generator Request 不應混為同一物件。

Configuration 描述：

* 系統與專案如何設定
* 模板在哪裡
* 輸出預設位置
* Plugin 是否啟用

Generator Request 描述：

* 本次要產生什麼
* 使用者輸入的 course ID
* week number
* output destination
* dry-run 或 overwrite 選項

例如：

```python
@dataclass(frozen=True, slots=True)
class GenerateRequest:
    generator_name: str
    target: Path
    values: Mapping[str, Any]
    dry_run: bool = False
    overwrite: bool = False
```

Generator 接收 Configuration 與 Request，組成實際執行內容：

```python
result = generator.generate(
    config=config,
    request=request,
)
```

---

## 27. Environment Variables

若未來支援環境變數，必須定義固定命名規則，例如：

```text
OPL_TEMPLATE_ROOT
OPL_OUTPUT_ROOT
OPL_DRY_RUN
OPL_PLUGIN_PATH
```

環境變數不應自動覆寫所有任意設定鍵。

建議只支援少量、明確且適合部署環境的值。

敏感資訊若未來需要支援，應使用專門 Secrets 機制，不應寫入一般設定檔或 Manifest。

---

## 28. Configuration Versioning

未來設定格式可能變更，因此應預留版本欄位：

```yaml
config_version: 1
```

載入時：

```python
version = data.get("config_version", 1)
```

Configuration Framework 應：

* 明確支援已知版本。
* 拒絕未知的未來版本。
* 對已淘汰版本提供清楚訊息。
* 不應靜默猜測重大格式變更。

例如：

```text
不支援設定版本 3；目前支援版本為 1。
```

---

## 29. Configuration Migration

當設定格式變更時，可提供明確遷移層：

```text
Raw Configuration v1
        │
        ▼
Migration v1 → v2
        │
        ▼
Validated Configuration v2
```

遷移必須：

* 可測試。
* 可重複執行。
* 不直接修改原始檔案，除非使用者明確執行 upgrade。
* 產生清楚變更紀錄。
* 保留備份策略。

自動載入與永久修改設定檔應是兩個不同操作。

---

## 30. Plugin Configuration

所有 Plugin 設定應封裝在 `plugins` 區段。

建議格式：

```yaml
plugins:
  enabled:
    - syllabus
    - assessment

  settings:
    syllabus:
      locale: zh-TW
      include_learning_outcomes: true

    assessment:
      quiz_count: 10
```

核心 Configuration Framework 應驗證：

* `enabled` 是字串清單。
* `settings` 是 mapping。
* Plugin 名稱格式有效。
* 每個 Plugin 設定值是 mapping。

Plugin 專用欄位的進一步驗證，應由 Plugin 自己提供 validator。

---

## 31. Plugin Validation Contract

未來可以定義：

```python
class PluginConfigValidator(Protocol):
    def validate(
        self,
        config: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        ...
```

核心流程：

```text
Load plugin settings
        │
        ▼
Locate enabled plugin
        │
        ▼
Run plugin validator
        │
        ▼
Return normalized plugin settings
```

Plugin 驗證失敗應轉換為可辨識的 ConfigurationError 或 PluginConfigurationError。

---

## 32. Error Model

所有設定相關錯誤應繼承：

```python
class ConfigurationError(Exception):
    """Raised when configuration cannot be loaded or validated."""
```

未來可細分：

```python
class ConfigurationFileNotFoundError(ConfigurationError):
    pass


class ConfigurationParseError(ConfigurationError):
    pass


class ConfigurationValidationError(ConfigurationError):
    pass


class ConfigurationVersionError(ConfigurationError):
    pass
```

上層 CLI 可以統一捕捉：

```python
except ConfigurationError as exc:
    print(f"設定錯誤：{exc}", file=sys.stderr)
    return 2
```

---

## 33. Error Message Guidelines

設定錯誤訊息應回答：

1. 哪個設定有問題？
2. 預期值是什麼？
3. 實際值是什麼？
4. 設定檔位於哪裡？
5. 使用者下一步可以怎麼修正？

良好示例：

```text
設定錯誤：paths.template_root 必須是字串路徑，
但收到 list。設定檔：F:\OpenProjectLab\config\default.yaml
```

不良示例：

```text
Invalid config.
```

不應在一般 CLI 輸出中直接顯示完整 traceback；除非啟用 debug 或 verbose 模式。

---

## 34. Validation Layers

建議將驗證分成三層。

### Layer 1: Syntax Validation

* 檔案是否可讀。
* YAML 是否可解析。
* 頂層是否為 mapping。

### Layer 2: Schema Validation

* 區段型別。
* 必要鍵。
* 欄位型別。
* 已知值範圍。
* 設定版本。

### Layer 3: Semantic Validation

* 路徑是否合法。
* 必要輸入目錄是否存在。
* Plugin 是否已註冊。
* 互斥選項是否同時啟用。
* 設定組合是否合理。

Generator-specific semantic validation 不應放在 Configuration Loader。

---

## 35. Validation Example

```python
def _require_mapping(
    data: Mapping[str, Any],
    key: str,
) -> Mapping[str, Any]:
    value = data.get(key, {})

    if not isinstance(value, dict):
        raise ConfigurationValidationError(
            f"{key} 必須是 mapping"
        )

    return value
```

路徑解析：

```python
def _resolve_path(
    value: str,
    *,
    base_dir: Path,
) -> Path:
    path = Path(value).expanduser()

    if not path.is_absolute():
        path = base_dir / path

    return path.resolve()
```

這些 helper 應保持小型、純粹且容易單元測試。

---

## 36. Configuration Builder

隨著設定模型變複雜，可將流程拆分為 Builder：

```python
class ProjectConfigBuilder:
    def __init__(self, source_path: Path) -> None:
        self._source_path = source_path

    def build(self) -> ProjectConfig:
        raw = self._load_yaml()
        normalized = self._normalize(raw)
        validated = self._validate(normalized)
        return self._construct(validated)
```

責任拆分：

```text
Loader
  └── 負責讀取與 YAML parse

Normalizer
  └── 負責預設值與格式統一

Validator
  └── 負責結構與語意驗證

Builder
  └── 負責組裝 ProjectConfig
```

早期版本可以保持單一類別，但當 `load()` 過長時應開始拆分。

---

## 37. Serialization

Configuration Framework 未必需要將 `ProjectConfig` 寫回 YAML。

若未來需要支援：

```powershell
opl config show
opl config validate
opl config migrate
opl config init
```

則應定義獨立 Serializer。

序列化時必須：

* 保持穩定欄位順序。
* 不輸出 Python 專用型別。
* 正確處理 Path。
* 不洩漏 Secrets。
* 明確標示 config version。
* 盡可能保留使用者可讀性。

Loader 與 Serializer 不應互相耦合到無法單獨測試。

---

## 38. CLI Integration

CLI 是 Configuration Framework 的主要 Composition Root。

建議流程：

```python
def main(argv: Sequence[str] | None = None) -> int:
    args = parser.parse_args(argv)

    try:
        config = ProjectConfig.load(args.config)
    except ConfigurationError as exc:
        print(f"設定錯誤：{exc}", file=sys.stderr)
        return 2

    registry = build_registry(config)

    return dispatch(
        args=args,
        config=config,
        registry=registry,
    )
```

CLI 負責：

* 接收設定檔路徑。
* 呼叫 Configuration Loader。
* 顯示使用者可理解的錯誤。
* 將有效設定注入 Registry 與 Generator。

CLI 不應自行解析 YAML 或重新實作路徑規則。

---

## 39. Generator Integration

Generator 應透過建構式注入或方法參數取得必要設定。

建構式注入：

```python
generator = CourseGenerator(
    template_root=config.paths.template_root,
    filesystem=filesystem,
    manifest=manifest,
)
```

或設定物件注入：

```python
generator = CourseGenerator(
    config=config,
    filesystem=filesystem,
)
```

建議只注入 Generator 真正需要的設定，而不是讓所有 Generator 依賴完整設定物件。

這可以降低耦合，並讓測試更簡單。

---

## 40. Template Integration

Template Renderer 通常只需要：

* `template_root`
* encoding
* undefined-variable policy
* optional extension settings

建議：

```python
renderer = TemplateRenderer(
    template_root=config.paths.template_root,
)
```

Template Context 不應直接包含完整 `ProjectConfig`，除非已明確定義其公開契約。

較安全做法：

```python
context = {
    "project": {
        "name": config.project.name,
        "version": config.project.version,
    },
    "course": request.course,
}
```

這可以避免模板依賴內部設定結構。

---

## 41. Filesystem Integration

Filesystem 可能需要：

* output root
* overwrite policy
* dry-run policy
* path safety rules

但 overwrite 與 dry-run 通常是 Runtime Options，而非永久專案設定。

建議：

```python
filesystem = FileSystem(
    root=config.paths.output_root,
    overwrite=runtime.overwrite,
    dry_run=runtime.dry_run,
)
```

Configuration Loader 不應建立 Filesystem，也不應執行寫入。

---

## 42. Manifest Integration

Manifest 設定可以包含：

```yaml
paths:
  manifest_path: .opl/manifest.json
```

Manifest Writer 應接收解析後的路徑：

```python
manifest = ManifestStore(
    path=config.paths.manifest_path,
)
```

Configuration Framework 只負責路徑解析與基本驗證，不負責 Manifest 格式或寫入行為。

---

## 43. Determinism

相同設定檔與相同覆寫參數，應產生相同有效設定。

不得將以下內容隱性加入設定：

* 當前時間
* 隨機值
* 未明確宣告的環境變數
* 目前工作目錄
* 未排序的外部資料
* 網路回應

若環境相關值會影響設定，必須明確記錄其來源。

---

## 44. Side-effect Policy

Configuration loading 必須盡量保持無副作用。

允許：

* 讀取設定檔。
* 檢查必要輸入路徑。
* 正規化路徑。
* 建立記憶體內設定模型。

不允許：

* 建立輸出目錄。
* 修改設定檔。
* 寫入 Manifest。
* 下載 Plugin。
* 渲染模板。
* 執行 Generator。
* 自動遷移並覆寫原始 YAML。
* 刪除或重新命名檔案。

---

## 45. Security Considerations

Configuration Framework 應遵守：

1. 使用 `yaml.safe_load`。
2. 不執行設定中的 Python 表達式。
3. 不允許模板路徑任意逃離安全根目錄，除非明確支援。
4. 不將 Secrets 寫入日誌。
5. 不在錯誤中顯示密碼或 Token。
6. 對 Plugin path 與外部 module loading 採取明確限制。
7. 對輸出路徑進行 traversal 檢查。
8. 對 symlink 行為建立測試與政策。

設定檔本身應視為不可信輸入。

---

## 46. Logging

Configuration Framework 可以記錄：

* 使用的設定檔路徑。
* 設定版本。
* 啟用的 Plugin 名稱。
* 已套用的非敏感覆寫。
* 路徑解析結果，僅在 verbose/debug 模式。
* Deprecated 設定警告。

不應記錄：

* Secret
* Token
* Password
* API key
* 完整私人環境資訊
* 不必要的使用者資料

---

## 47. Testing Strategy

Configuration Framework 必須包含：

1. Unit Tests
2. Path Resolution Tests
3. Validation Tests
4. Error Tests
5. Integration Tests
6. Compatibility Tests
7. Migration Tests，當版本機制加入後

---

## 48. Unit Tests

最低限度應測試：

```text
tests/core/test_config.py
```

建議案例：

* 載入有效 YAML。
* 找不到設定檔。
* YAML 格式錯誤。
* 空白設定檔。
* 頂層不是 mapping。
* `project` 不是 mapping。
* `paths` 不是 mapping。
* `generator` 不是 mapping。
* `plugins` 不是 mapping。
* 未知區段策略。
* 預設值套用。
* 必要鍵缺失。
* 錯誤型別。
* 設定物件不可變性。

---

## 49. Path Resolution Tests

必須涵蓋：

* 相對路徑。
* 絕對路徑。
* `.` 路徑。
* `..` 路徑。
* Windows drive path。
* 路徑包含空白。
* 路徑包含中文。
* 設定檔位於不同目錄。
* 從不同目前工作目錄執行。
* Input path 不存在。
* Output path 不存在但允許。
* Symlink 行為，若支援。

範例：

```python
def test_template_root_relative_path(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    template_dir = tmp_path / "templates"

    config_dir.mkdir()
    template_dir.mkdir()

    config_path = config_dir / "default.yaml"
    config_path.write_text(
        "paths:\n"
        "  template_root: ../templates\n",
        encoding="utf-8",
    )

    config = ProjectConfig.load(config_path)

    assert config.paths.template_root == template_dir.resolve()
```

絕對路徑：

```python
def test_template_root_absolute_path(
    tmp_path: Path,
) -> None:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    config_path = tmp_path / "default.yaml"
    config_path.write_text(
        "paths:\n"
        f"  template_root: {template_dir.as_posix()}\n",
        encoding="utf-8",
    )

    config = ProjectConfig.load(config_path)

    assert config.paths.template_root == template_dir.resolve()
```

---

## 50. Error Tests

每種失敗情況都應驗證：

* 例外型別。
* 訊息包含必要資訊。
* 原始例外是否保留。
* 不會產生副作用。
* CLI 是否回傳正確 exit code。

例如：

```python
with pytest.raises(
    ConfigurationError,
    match="找不到設定檔",
):
    ProjectConfig.load(
        tmp_path / "missing.yaml"
    )
```

---

## 51. Integration Tests

整合測試應確認：

```text
Configuration File
        ↓
CLI
        ↓
ProjectConfig
        ↓
Registry
        ↓
Generator
```

建議案例：

* CLI 使用預設設定檔執行 `list`。
* CLI 使用 `--config` 指定不同設定檔。
* 不同工作目錄執行 CLI。
* 設定模板根目錄後成功產生專案。
* 設定錯誤時 CLI 回傳非零狀態。
* CLI override 正確覆寫設定值。
* dry-run 不產生檔案。
* Plugin 啟用設定正確傳入 Registry。

---

## 52. Contract Tests

所有正式設定鍵應有契約測試。

例如：

```python
def test_default_generator_settings() -> None:
    config = load_minimal_config()

    assert config.generator.overwrite is False
    assert config.generator.dry_run is False
```

契約測試的目的是避免：

* 預設值無意間變更。
* 欄位重新命名但未遷移。
* 文件與程式行為不一致。
* Generator 對設定的假設被破壞。

---

## 53. Test Fixtures

建議建立可重用 fixture：

```python
@pytest.fixture
def config_factory(tmp_path: Path):
    def create(content: str) -> Path:
        path = tmp_path / "config.yaml"
        path.write_text(content, encoding="utf-8")
        return path

    return create
```

也可建立：

* `minimal_config`
* `valid_config`
* `config_with_plugins`
* `config_with_absolute_paths`
* `config_with_relative_paths`

Fixture 不應隱藏測試真正需要驗證的重要值。

---

## 54. Recommended Module Structure

Milestone 3 可逐步演進為：

```text
generator/
└── core/
    ├── config.py
    ├── config_loader.py
    ├── config_models.py
    ├── config_validation.py
    ├── config_paths.py
    ├── exceptions.py
    └── constants.py
```

初期不需要立即拆成所有檔案。

建議拆分時機：

* `config.py` 超過合理可維護大小。
* 驗證 helper 增加。
* 路徑規則開始獨立複雜化。
* Plugin validation 加入。
* 設定版本遷移加入。
* 多種來源合併機制加入。

---

## 55. Recommended Public API

Configuration package 應只公開穩定介面：

```python
from generator.core.config import ProjectConfig
from generator.core.exceptions import ConfigurationError
```

內部 helper 不應被 CLI 或 Generator 直接引用。

例如以下應保持 private：

```python
_resolve_path()
_validate_section()
_normalize_config()
```

這可以保留未來重構空間。

---

## 56. Milestone 3 Evolution Plan

### Phase 1: Stabilize Current Loader

* 確認 YAML 安全載入。
* 驗證頂層與所有區段。
* 修正相對與絕對路徑解析。
* 統一 `ConfigurationError`。
* 補齊現有單元測試。

### Phase 2: Define Configuration Contract

* 文件化所有正式設定鍵。
* 明確定義預設值。
* 定義覆寫優先順序。
* 定義未知區段政策。
* 區分 Configuration 與 Runtime Options。

### Phase 3: Introduce Typed Sections

* 建立 `PathsConfig`。
* 建立 `GeneratorSettings`。
* 建立 `PluginSettings`。
* 保留舊字典介面的過渡相容性。
* 加入 contract tests。

### Phase 4: Versioning and Migration

* 加入 `config_version`。
* 建立 migration interface。
* 新增 `opl config validate`。
* 新增 `opl config migrate`。
* 加入 backward compatibility tests。

### Phase 5: Plugin Configuration

* 定義 Plugin validator contract。
* 驗證 Plugin 設定。
* 加入 Plugin-specific error。
* 建立 Plugin configuration documentation。

---

## 57. Documentation Requirements

每次新增或修改正式設定鍵時，必須同步更新：

* `docs/architecture/configuration.md`
* `docs/configuration.md`
* `config/default.yaml`
* 設定範例
* CLI help，若可由 CLI 覆寫
* 單元測試
* 整合測試
* CHANGELOG，若屬使用者可見變更
* Migration guide，若存在不相容變更

設定行為不可只存在於程式碼中。

---

## 58. Code Review Checklist

### Architecture

* [ ] Configuration 是否保持單一責任？
* [ ] 是否避免依賴具體 Generator？
* [ ] 是否避免依賴 CLI parser 實作？
* [ ] 是否區分 Configuration 與 Runtime Options？
* [ ] 是否避免讓 Template 直接依賴完整設定物件？
* [ ] 是否維持清楚的依賴方向？
* [ ] 是否沒有新增不必要的全域狀態？

### Loading

* [ ] 是否使用 UTF-8 讀取設定檔？
* [ ] 是否使用 `yaml.safe_load`？
* [ ] 是否處理空白 YAML？
* [ ] 是否驗證檔案存在？
* [ ] 是否正確處理檔案讀取錯誤？
* [ ] 是否保留原始例外鏈？
* [ ] 是否避免直接暴露 YAML parser 例外？

### Validation

* [ ] 是否驗證 YAML 頂層為 mapping？
* [ ] 是否驗證所有已知區段為 mapping？
* [ ] 是否驗證必要欄位？
* [ ] 是否驗證欄位型別？
* [ ] 是否驗證可接受值範圍？
* [ ] 是否明確處理未知區段？
* [ ] 是否避免靜默忽略拼字錯誤？
* [ ] 是否將 Generator-specific 驗證留在 Generator？

### Defaults

* [ ] 預設值是否集中管理？
* [ ] 是否避免在 CLI 與 Generator 重複定義預設值？
* [ ] 預設值是否有測試？
* [ ] 預設值是否已文件化？
* [ ] 修改預設值是否評估 backward compatibility？

### Paths

* [ ] 相對路徑解析基準是否明確？
* [ ] 是否不依賴目前工作目錄？
* [ ] 絕對路徑是否正確保留？
* [ ] 是否支援 Windows 路徑？
* [ ] 是否支援路徑中的空白與中文？
* [ ] 是否區分 input 與 output path 驗證？
* [ ] 是否避免載入設定時建立目錄？
* [ ] 是否考慮 path traversal？
* [ ] 是否定義 symlink 行為？
* [ ] 路徑解析是否有獨立測試？

### Overrides

* [ ] 是否定義設定來源優先順序？
* [ ] CLI override 是否不修改原始設定物件？
* [ ] 是否只覆寫明確指定的值？
* [ ] boolean override 是否能區分未指定與 false？
* [ ] Runtime Options 是否與長期設定分離？
* [ ] 覆寫行為是否有整合測試？

### Models

* [ ] 新模型是否具有清楚型別？
* [ ] 是否考慮不可變性？
* [ ] 是否避免大量 `dict[str, Any]` 擴散？
* [ ] 是否保留必要的 backward compatibility？
* [ ] 是否提供從 raw mapping 到 typed model 的單一入口？
* [ ] 是否沒有讓外部元件依賴內部 helper？

### Error Handling

* [ ] 是否使用 `ConfigurationError` 或其子類別？
* [ ] 錯誤訊息是否包含問題欄位？
* [ ] 是否包含設定檔位置？
* [ ] 是否指出預期型別或格式？
* [ ] 是否提供可行動的修正資訊？
* [ ] CLI 是否回傳適當非零 exit code？
* [ ] 一般模式是否避免輸出 traceback？
* [ ] 是否避免在錯誤中顯示 Secret？

### Plugin Configuration

* [ ] Plugin 設定是否位於 `plugins` 區段？
* [ ] 是否驗證 enabled list？
* [ ] 是否驗證 plugin settings mapping？
* [ ] Plugin-specific 驗證是否由 Plugin 負責？
* [ ] Plugin 驗證錯誤是否可辨識？
* [ ] 未安裝 Plugin 的行為是否明確？
* [ ] Plugin 設定是否有隔離測試？

### Versioning

* [ ] 是否需要提高 `config_version`？
* [ ] 是否支援舊版本？
* [ ] 是否提供 migration？
* [ ] 是否拒絕未知未來版本？
* [ ] migration 是否不會自動覆寫原始檔案？
* [ ] migration 是否具備測試？
* [ ] 不相容變更是否記錄於 CHANGELOG？

### Security

* [ ] 是否只使用安全 YAML loader？
* [ ] 是否不執行設定內容？
* [ ] 是否避免記錄 Token、Password 或 Secret？
* [ ] 是否限制外部 Plugin path？
* [ ] 是否檢查危險輸出路徑？
* [ ] 是否避免模板目錄逃離允許範圍？
* [ ] 是否評估 symlink 攻擊？
* [ ] 是否將設定檔視為不可信輸入？

### Side Effects

* [ ] 載入設定時是否不寫入檔案？
* [ ] 是否不建立目錄？
* [ ] 是否不下載資源？
* [ ] 是否不執行 Generator？
* [ ] 是否不修改原始 YAML？
* [ ] 是否不寫入 Manifest？
* [ ] 所有副作用是否延後到適當服務？

### Testing

* [ ] 有效設定是否有測試？
* [ ] 缺少設定檔是否有測試？
* [ ] YAML syntax error 是否有測試？
* [ ] 空白設定檔是否有測試？
* [ ] 頂層型別錯誤是否有測試？
* [ ] 每個區段型別錯誤是否有測試？
* [ ] 相對路徑是否有測試？
* [ ] 絕對路徑是否有測試？
* [ ] 不同工作目錄執行是否有測試？
* [ ] 預設值是否有 contract tests？
* [ ] CLI override 是否有整合測試？
* [ ] 錯誤訊息是否有測試？
* [ ] 設定載入是否確認無副作用？
* [ ] 完整 test suite 是否通過？

### Documentation

* [ ] `docs/architecture/configuration.md` 是否更新？
* [ ] 使用者設定指南是否更新？
* [ ] `config/default.yaml` 是否更新？
* [ ] 所有新增欄位是否有範例？
* [ ] 預設值是否明確記錄？
* [ ] 路徑解析規則是否記錄？
* [ ] Deprecated 欄位是否記錄？
* [ ] Migration 說明是否更新？
* [ ] CHANGELOG 是否更新？

---

## 59. Acceptance Criteria

Configuration Framework 可視為 Milestone 3 基礎完成，至少需符合：

* 設定檔可從任意工作目錄穩定載入。
* YAML 解析使用安全 Loader。
* 頂層與所有核心區段都有型別驗證。
* 相對與絕對路徑行為明確且通過測試。
* Configuration 錯誤統一為 `ConfigurationError`。
* CLI 能顯示清楚錯誤並回傳非零狀態。
* 載入設定不產生檔案系統副作用。
* 預設值與覆寫優先順序已有文件。
* Configuration 與 Generator Request 已概念分離。
* 單元測試、整合測試與 pre-commit 全部通過。
* 架構文件與使用者文件保持同步。

---

## 60. Related Documents

* `docs/architecture/generator.md`
* `docs/architecture/template.md`
* `docs/reference/template.md`
* `docs/reference/filesystem.md`
* `docs/configuration.md`
* `docs/cli.md`
* `docs/ROADMAP.md`
* `config/default.yaml`
* `generator/core/config.py`
* `generator/core/exceptions.py`
* `generator/cli/main.py`
* `tests/core/test_config.py`
* `tests/integration/test_cli_integration.py`
