# Registry Architecture

## 1. Purpose

OpenProjectLab 的 Registry Framework 負責管理所有可用的 Generator，提供一致的註冊、查找、列舉與建立機制。

Registry 是 CLI、Generator Framework 與 Plugin Framework 之間的中介層。CLI 不應直接匯入或判斷每一個具體 Generator；Generator 也不應自行修改全域註冊狀態。

Registry 的核心目標，是將「使用者輸入的 Generator 名稱」安全且可預測地轉換為「可執行的 Generator 實例」。

本文件定義 Registry Framework 的責任、介面、生命週期、錯誤處理、Plugin 整合與測試契約。

---

## 2. Goals

Registry Framework 的主要目標如下：

1. 提供單一 Generator 註冊入口。
2. 以穩定名稱查找 Generator。
3. 防止名稱衝突與重複註冊。
4. 支援列舉目前可用的 Generator。
5. 將 Generator discovery 與 CLI dispatch 解耦。
6. 支援核心 Generator 與 Plugin Generator。
7. 提供可測試、可預測且無隱性全域狀態的行為。
8. 為未來 Generator metadata、alias 與版本相容機制保留擴充空間。

---

## 3. Non-goals

Registry Framework 不負責：

* 解析 CLI 參數。
* 載入 YAML 設定。
* 執行 Generator 的產生流程。
* 渲染模板。
* 寫入檔案系統。
* 更新 Manifest。
* 下載或安裝 Plugin。
* 自動猜測未知 Generator 名稱。
* 管理 Generator 內部生命週期狀態。
* 將 Generator 執行錯誤轉換成成功結果。

Registry 負責「有哪些 Generator」與「如何取得 Generator」，不負責「Generator 如何產生內容」。

---

## 4. Architectural Context

Registry 位於 CLI 與 Generator 實作之間。

```text
User Command
    │
    ▼
CLI Parser
    │
    ▼
Generator Name
    │
    ▼
Generator Registry
    │
    ├── Register
    ├── Lookup
    ├── List
    ├── Validate
    └── Construct
    │
    ▼
Generator Instance
    │
    ▼
Generation Workflow
```

對 Plugin Generator 而言：

```text
Plugin Discovery
      │
      ▼
Plugin Metadata
      │
      ▼
Registry Registration
      │
      ▼
CLI-visible Generator
```

Registry 應是 Generator catalog 的唯一可信來源。

---

## 5. Dependency Direction

建議依賴方向如下：

```text
CLI
 │
 ▼
Registry
 │
 ▼
Generator Contract

Plugin Loader
 │
 ▼
Registry
```

Registry 可以依賴：

* Generator Protocol 或抽象基底類別
* Generator metadata model
* Registry 專用例外
* Callable、Mapping 與其他標準型別

Registry 不應依賴：

* argparse parser
* 具體 CLI command handler
* Template Renderer
* Filesystem implementation
* Manifest implementation
* 特定 Plugin 實作
* 專案產生流程

具體 Generator 可以在 Composition Root 被註冊，但 Registry 核心模組不應直接匯入所有 Generator。

---

## 6. Registry Responsibilities

Registry 應負責：

1. 驗證 Generator 名稱。
2. 註冊 Generator factory。
3. 防止重複名稱。
4. 依名稱查找 Generator。
5. 列出可用 Generator。
6. 提供穩定排序。
7. 回報未知 Generator。
8. 儲存必要 metadata。
9. 支援核心與 Plugin 來源識別。
10. 保持註冊與查找行為 deterministic。

Registry 不應執行 Generator。

---

## 7. Current Generator Set

目前 OpenProjectLab 的核心 Generator 包含：

```text
bootstrap
course
week
```

其概念責任如下：

| Generator   | Responsibility           |
| ----------- | ------------------------ |
| `bootstrap` | 建立新的 OpenProjectLab 專案骨架 |
| `course`    | 建立課程層級內容與結構              |
| `week`      | 建立單週教材與相關檔案              |

這些名稱是 CLI 與使用者文件的一部分，因此應視為公開契約。

重新命名 Generator 必須考慮 backward compatibility、alias 與 migration。

---

## 8. Registry Terminology

### Generator Name

使用者在 CLI 中輸入的穩定識別名稱，例如：

```text
bootstrap
course
week
```

### Generator Factory

建立 Generator 實例的 callable。

例如：

```python
Callable[[], Generator]
```

或：

```python
Callable[[GeneratorDependencies], Generator]
```

### Generator Metadata

描述 Generator 的名稱、說明、來源、版本與能力。

### Core Generator

由 OpenProjectLab 核心套件提供的 Generator。

### Plugin Generator

由外部 Plugin 提供並註冊的 Generator。

### Alias

指向正式 Generator 名稱的替代名稱。

---

## 9. Generator Contract

Registry 不應依賴具體 Generator 類別，而應依賴穩定契約。

可定義：

```python
from typing import Protocol


class Generator(Protocol):
    @property
    def name(self) -> str:
        ...

    def generate(self, request: object) -> object:
        ...
```

若 Generator 的名稱只存在於 Registry metadata，則 Generator 本身可以不提供 `name` property。

較推薦的方向，是將 identity 與 implementation 分離：

```python
registry.register(
    metadata=GeneratorMetadata(
        name="course",
        description="Generate course-level content",
    ),
    factory=build_course_generator,
)
```

這可避免 Registry 必須先建立實例才能知道名稱。

---

## 10. Registry Entry

每一個註冊項目應封裝為獨立模型。

```python
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True, slots=True)
class GeneratorEntry:
    metadata: "GeneratorMetadata"
    factory: Callable[[], "Generator"]
```

若建構需要依賴：

```python
@dataclass(frozen=True, slots=True)
class GeneratorEntry:
    metadata: "GeneratorMetadata"
    factory: Callable[
        ["GeneratorDependencies"],
        "Generator",
    ]
```

Registry 應保存 entry，而不是隨意保存 class、instance 與 callable 的混合形式。

---

## 11. Generator Metadata

建議定義：

```python
@dataclass(frozen=True, slots=True)
class GeneratorMetadata:
    name: str
    description: str
    source: str = "core"
    version: str | None = None
    aliases: tuple[str, ...] = ()
    deprecated: bool = False
```

欄位語意如下：

| Field         | Meaning               |
| ------------- | --------------------- |
| `name`        | 正式且唯一的 Generator 名稱   |
| `description` | CLI list 與文件使用的簡短說明   |
| `source`      | `core` 或 Plugin 識別名稱  |
| `version`     | Generator 或 Plugin 版本 |
| `aliases`     | 可接受的替代名稱              |
| `deprecated`  | 是否已淘汰                 |

Metadata 應保持不可變。

---

## 12. Name Rules

Generator 名稱應符合穩定規則。

建議：

* 使用小寫 ASCII。
* 使用連字號分隔多個單字。
* 不允許前後空白。
* 不允許路徑分隔字元。
* 不允許空字串。
* 不允許控制字元。
* 不允許以 `-` 開頭。
* 不允許與 CLI 保留命令衝突。

建議格式：

```text
^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$
```

有效：

```text
bootstrap
course
week
course-pack
assessment-kit
```

無效：

```text
Course
course_generator
../course
 course
course/
```

---

## 13. Name Normalization

Registry 可以接受有限度正規化，例如：

```python
normalized = name.strip().lower()
```

但不建議進行過度猜測。

例如，不應自動將：

```text
course_generator
```

轉換成：

```text
course
```

因為這可能掩蓋拼字或 API 使用錯誤。

正式註冊時應要求名稱已符合規則；查找時可選擇是否允許大小寫正規化。

建議 CLI 與 Registry 使用完全一致的小寫正式名稱。

---

## 14. Core Registry Interface

建議公開介面：

```python
class GeneratorRegistry:
    def register(
        self,
        entry: GeneratorEntry,
    ) -> None:
        ...

    def get(
        self,
        name: str,
    ) -> GeneratorEntry:
        ...

    def contains(
        self,
        name: str,
    ) -> bool:
        ...

    def list(
        self,
    ) -> tuple[GeneratorEntry, ...]:
        ...

    def create(
        self,
        name: str,
        dependencies: GeneratorDependencies,
    ) -> Generator:
        ...
```

不一定需要同時提供 `get()` 與 `create()`，但兩者責任必須明確。

* `get()`：取得註冊資料。
* `create()`：建立 Generator 實例。

---

## 15. Registration Flow

建議註冊流程如下：

```text
Receive Generator Entry
        │
        ▼
Validate Metadata
        │
        ▼
Validate Factory
        │
        ▼
Normalize Name
        │
        ▼
Check Duplicate Name
        │
        ▼
Check Alias Conflicts
        │
        ▼
Store Entry
        │
        ▼
Update Alias Index
```

任何驗證失敗都不應留下部分註冊狀態。

註冊操作應具備原子性。

---

## 16. Registration Example

```python
registry = GeneratorRegistry()

registry.register(
    GeneratorEntry(
        metadata=GeneratorMetadata(
            name="bootstrap",
            description="Create a new OpenProjectLab project",
        ),
        factory=build_bootstrap_generator,
    )
)
```

對簡化版 API：

```python
registry.register(
    name="bootstrap",
    factory=build_bootstrap_generator,
    description="Create a new OpenProjectLab project",
)
```

內部仍應轉換成一致的 `GeneratorEntry`。

---

## 17. Duplicate Registration

同一正式名稱不得被重複註冊。

```python
registry.register(entry_a)
registry.register(entry_b)
```

若兩者名稱皆為：

```text
course
```

第二次必須失敗。

建議例外：

```python
class DuplicateGeneratorError(RegistryError):
    pass
```

錯誤訊息：

```text
Generator 已註冊：course
既有來源：core
新來源：plugin:course-tools
```

不得默默覆寫既有 Generator。

---

## 18. Override Policy

預設政策應是：

```text
No implicit override
```

即使 Plugin 與核心 Generator 同名，也不可自動取代核心實作。

若未來需要 override，必須是明確功能，例如：

```python
registry.replace(
    name="course",
    entry=custom_entry,
    allow_core_override=True,
)
```

此功能應：

* 預設停用。
* 產生明確警告。
* 記錄來源。
* 有安全政策。
* 有相容性測試。
* 不透過一般 `register()` 隱性完成。

Milestone 3 不建議實作 Generator override。

---

## 19. Alias Registration

Alias 可以支援舊命令或較短名稱。

例如：

```python
GeneratorMetadata(
    name="bootstrap",
    aliases=("init",),
)
```

查找：

```text
init → bootstrap
```

Alias 必須遵守：

* 不可與正式名稱衝突。
* 不可與其他 Alias 衝突。
* 不可指向多個 Generator。
* 必須被列入 metadata。
* 必須有測試。
* Deprecated alias 應顯示警告。

Registry 應維護獨立 alias index：

```python
_aliases: dict[str, str]
```

---

## 20. Lookup Flow

建議查找流程：

```text
Receive Name
    │
    ▼
Normalize Input
    │
    ▼
Check Formal Name
    │
    ├── Found ──► Return Entry
    │
    ▼
Check Alias
    │
    ├── Found ──► Resolve Formal Name
    │
    ▼
Raise UnknownGeneratorError
```

查找不應建立 Generator 實例，除非呼叫的是明確 `create()` API。

---

## 21. Unknown Generator

未知名稱應回報專用例外：

```python
class UnknownGeneratorError(RegistryError):
    pass
```

例如：

```text
找不到 Generator：courses
可用的 Generator：bootstrap, course, week
```

可以提供相近名稱建議，但必須清楚標示為建議，而不是自動執行。

例如：

```text
找不到 Generator：courses
是否要使用：course
```

CLI 不應在未經使用者確認時自動替換成近似名稱。

---

## 22. Suggested Name Matching

若需要提供拼字建議，可以使用：

```python
difflib.get_close_matches()
```

例如：

```python
suggestions = get_close_matches(
    requested,
    registry.names(),
    n=3,
    cutoff=0.7,
)
```

建議功能必須：

* 只用於錯誤訊息。
* 不改變 lookup 結果。
* 不造成不確定命令被執行。
* 有穩定排序。
* 不依賴網路。

---

## 23. Listing Generators

Registry 應提供穩定列舉。

```python
entries = registry.list()
```

建議預設依正式名稱排序：

```text
bootstrap
course
week
```

不應依賴 dict insertion order 作為公開契約，除非文件明確要求註冊順序。

CLI list 輸出可使用：

```text
bootstrap  Create a new OpenProjectLab project
course     Generate course-level content
week       Generate week-level content
```

---

## 24. Stable Ordering

為了 deterministic output，以下行為應固定排序：

* `registry.list()`
* `registry.names()`
* unknown-name 錯誤中的可用名稱
* CLI help 中的 Generator 列表
* Plugin registration report
* 文件自動產生的 Generator catalog

建議一律依 canonical name 排序。

---

## 25. Registry Construction

Registry 應在 Composition Root 建立，而不是在模組 import 時建立全域 singleton。

推薦：

```python
def build_registry(
    config: ProjectConfig,
) -> GeneratorRegistry:
    registry = GeneratorRegistry()

    register_core_generators(
        registry,
        config=config,
    )

    register_plugin_generators(
        registry,
        config=config,
    )

    return registry
```

不推薦：

```python
GLOBAL_REGISTRY = GeneratorRegistry()

GLOBAL_REGISTRY.register(...)
```

全域 Registry 容易造成：

* 測試互相污染。
* import order 影響行為。
* Plugin 重複註冊。
* 難以建立隔離環境。
* 平行測試不穩定。

---

## 26. Composition Root

CLI main 應負責組裝 Registry。

```python
def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    config = ProjectConfig.load(args.config)
    dependencies = build_dependencies(config)
    registry = build_registry(config, dependencies)

    return dispatch(
        args=args,
        registry=registry,
        config=config,
    )
```

Composition Root 負責：

* 載入設定。
* 建立共享服務。
* 註冊核心 Generator。
* 載入 Plugin。
* 建立 Registry。
* 將 Registry 傳入 CLI dispatch。

Registry 本身不應知道如何解析整份 Configuration。

---

## 27. Core Generator Registration

建議建立獨立函式：

```python
def register_core_generators(
    registry: GeneratorRegistry,
    dependencies: GeneratorDependencies,
) -> None:
    registry.register(
        GeneratorEntry(
            metadata=GeneratorMetadata(
                name="bootstrap",
                description="Create a project skeleton",
                source="core",
            ),
            factory=lambda: BootstrapGenerator(
                renderer=dependencies.renderer,
                filesystem=dependencies.filesystem,
                manifest=dependencies.manifest,
            ),
        )
    )
```

若避免 lambda，可使用 factory object 或 `functools.partial`。

核心註冊應集中，而不是散落在 CLI command handler。

---

## 28. Factory Design

Registry 建議儲存 factory，而不是共享 Generator instance。

原因：

* Generator 可能持有執行狀態。
* 每次執行應取得乾淨實例。
* 有利於平行或重複執行。
* 測試更容易隔離。
* 避免前一次執行資料洩漏到下一次。

簡單 factory：

```python
Callable[[], Generator]
```

依賴注入 factory：

```python
Callable[[GeneratorDependencies], Generator]
```

預先綁定 factory：

```python
factory = partial(
    CourseGenerator,
    renderer=renderer,
    filesystem=filesystem,
    manifest=manifest,
)
```

---

## 29. Generator Dependencies

建議使用明確依賴容器：

```python
@dataclass(frozen=True, slots=True)
class GeneratorDependencies:
    config: ProjectConfig
    renderer: TemplateRenderer
    filesystem: FileSystem
    manifest: ManifestStore
```

但應避免將過大的 service container 傳給所有 Generator。

更好的長期方向是：

* Factory 接收 dependencies。
* Factory 只將必要依賴傳入 Generator。
* Generator 不直接使用 Registry。
* Registry 不直接使用 Template 或 Filesystem。

---

## 30. Create Operation

Registry 可提供：

```python
def create(
    self,
    name: str,
    dependencies: GeneratorDependencies,
) -> Generator:
    entry = self.get(name)
    return entry.factory(dependencies)
```

或 factory 已預先綁定：

```python
def create(self, name: str) -> Generator:
    return self.get(name).factory()
```

`create()` 必須：

* 先完成正式 lookup。
* 正確處理 alias。
* 不快取有狀態 Generator，除非明確設計。
* 將 factory 建構錯誤保留或轉換為專用錯誤。
* 不自動執行 `generate()`。

---

## 31. Factory Errors

若 factory 建構失敗，可定義：

```python
class GeneratorConstructionError(RegistryError):
    pass
```

錯誤訊息應包含：

* Generator 名稱。
* Generator 來源。
* 建構失敗原因。
* 原始例外鏈。

例如：

```text
無法建立 Generator：course
來源：core
原因：找不到模板根目錄
```

不要將 construction error 誤報為 unknown Generator。

---

## 32. Registry Error Hierarchy

建議：

```python
class RegistryError(Exception):
    """Base error for generator registry operations."""


class InvalidGeneratorNameError(RegistryError):
    pass


class DuplicateGeneratorError(RegistryError):
    pass


class UnknownGeneratorError(RegistryError):
    pass


class AliasConflictError(RegistryError):
    pass


class GeneratorConstructionError(RegistryError):
    pass


class PluginRegistrationError(RegistryError):
    pass
```

CLI 可以捕捉 `RegistryError`，同時保留具體錯誤類型供測試與內部處理。

---

## 33. CLI Integration

CLI 不應維護獨立 Generator 名單。

不推薦：

```python
if args.command == "bootstrap":
    generator = BootstrapGenerator(...)
elif args.command == "course":
    generator = CourseGenerator(...)
elif args.command == "week":
    generator = WeekGenerator(...)
```

推薦：

```python
generator = registry.create(args.command)
result = generator.generate(request)
```

`list` command：

```python
for entry in registry.list():
    print(entry.metadata.name)
```

CLI help、list 與 dispatch 應共用同一 Registry 資料來源，避免清單不一致。

---

## 34. CLI Parser Timing

有兩種 CLI parser 架構。

### Static Parser

在 parser 建立時，明確建立每個 subcommand。

```python
subparsers.add_parser("bootstrap")
subparsers.add_parser("course")
subparsers.add_parser("week")
```

優點：

* 每個命令可以有專屬參數。
* argparse help 完整。

缺點：

* Plugin command 較難動態加入。

### Dynamic Parser

先建立 Registry，再依 metadata 建立 subcommand。

```python
for entry in registry.list():
    add_generator_subcommand(
        subparsers,
        entry,
    )
```

優點：

* Plugin 可自動進入 CLI。

缺點：

* 需要 metadata 描述參數 schema。
* parser 建構更複雜。

Milestone 3 可保留 Static Parser，但 Generator lookup 與執行仍應使用 Registry。

---

## 35. Command and Generator Separation

不是所有 CLI command 都是 Generator。

例如：

```text
list
doctor
config
version
upgrade
```

這些可能是系統命令，而不是 Generator。

建議架構：

```text
CLI Commands
├── System Commands
│   ├── list
│   ├── doctor
│   ├── config
│   └── version
│
└── Generator Commands
    ├── bootstrap
    ├── course
    └── week
```

Registry 只管理 Generator，不管理所有 CLI command。

`list` 命令可以讀取 Registry，但不應被註冊為 Generator。

---

## 36. Plugin Integration

Plugin Loader 可以發現 Plugin Generator，再註冊進相同 Registry。

```text
Load Enabled Plugins
        │
        ▼
Read Plugin Metadata
        │
        ▼
Validate Compatibility
        │
        ▼
Obtain Generator Entries
        │
        ▼
Register in Registry
```

Plugin 不應直接存取 Registry 內部 dict。

應提供正式 API：

```python
registry.register(plugin_entry)
```

---

## 37. Plugin Registration Contract

Plugin 可以提供：

```python
def register_generators(
    registry: GeneratorRegistry,
    context: PluginContext,
) -> None:
    ...
```

或回傳 entries：

```python
def get_generators(
    context: PluginContext,
) -> tuple[GeneratorEntry, ...]:
    ...
```

較推薦 Plugin 回傳 entries，由核心統一註冊：

```python
entries = plugin.get_generators(context)

for entry in entries:
    registry.register(entry)
```

優點：

* 核心可以先驗證完整批次。
* 避免 Plugin 任意修改 Registry。
* 容易實作 transactional registration。
* 容易產生註冊報告。

---

## 38. Transactional Plugin Registration

若 Plugin 提供多個 Generator：

```text
plugin-a:
  - syllabus
  - assessment
  - export
```

其中一個名稱衝突時，不應留下其他部分已註冊項目。

建議流程：

```text
Collect Plugin Entries
        │
        ▼
Validate All Entries
        │
        ▼
Check All Conflicts
        │
        ▼
Commit All Registrations
```

即 all-or-nothing。

Milestone 3 若尚未支援批次註冊，至少應在文件中標示 Plugin registration 可能不是 transactional。

---

## 39. Plugin Source Identity

Plugin Generator metadata 應包含來源：

```python
GeneratorMetadata(
    name="assessment-kit",
    description="Generate assessments",
    source="plugin:opl-assessment",
    version="1.2.0",
)
```

這有助於：

* 重複註冊錯誤。
* Debug。
* CLI list 詳細模式。
* 相容性檢查。
* 問題回報。
* Manifest provenance。

---

## 40. Plugin Compatibility

Plugin Generator 註冊前應驗證：

* Plugin API version。
* OPL core version compatibility。
* Generator contract version。
* 必要 capability。
* 名稱是否合法。
* factory 是否 callable。
* metadata 是否完整。

Registry 可以驗證 entry 結構，但版本相容性通常由 Plugin Loader 負責。

責任邊界：

```text
Plugin Loader
  └── 驗證 Plugin 與 OPL 相容性

Registry
  └── 驗證 Generator Entry 與名稱衝突
```

---

## 41. Core Name Protection

核心 Generator 名稱應受到保護。

例如：

```text
bootstrap
course
week
```

Plugin 不得註冊同名項目。

可以維護：

```python
CORE_GENERATOR_NAMES = frozenset(
    {
        "bootstrap",
        "course",
        "week",
    }
)
```

但更好的做法是先註冊核心 Generator，再由一般 duplicate policy 自然阻止衝突。

錯誤訊息應指出核心名稱不可被取代。

---

## 42. Registry Mutability

Registry 在建構階段需要可修改，執行階段則應盡量凍結。

建議生命週期：

```text
Create Mutable Registry
        │
        ▼
Register Core Generators
        │
        ▼
Register Plugin Generators
        │
        ▼
Freeze Registry
        │
        ▼
Use for CLI Execution
```

可以提供：

```python
registry.freeze()
```

freeze 後：

```python
registry.register(...)
```

應失敗。

優點：

* 避免執行期間註冊狀態改變。
* 提高 deterministic behavior。
* 降低 Plugin 動態修改風險。
* 有利於平行執行。

---

## 43. Frozen Registry

可定義：

```python
class RegistryFrozenError(RegistryError):
    pass
```

freeze 後仍允許：

* `get()`
* `contains()`
* `list()`
* `names()`
* `create()`

不允許：

* `register()`
* `replace()`
* `remove()`
* alias 修改

Milestone 3 可先不實作 freeze，但應避免執行期間任意註冊。

---

## 44. Removal Policy

一般執行流程不需要移除 Generator。

若提供：

```python
registry.unregister("course")
```

可能造成：

* CLI help 與 Registry 狀態不同步。
* 核心 Generator 被移除。
* Plugin unload 複雜化。
* 測試狀態不穩定。

Milestone 3 建議不提供公開 `unregister()`。

測試應建立新 Registry，而不是移除既有項目清理狀態。

---

## 45. Singleton Policy

Registry 不應是 process-wide singleton。

不推薦：

```python
_registry = GeneratorRegistry()


def get_registry() -> GeneratorRegistry:
    return _registry
```

推薦：

```python
registry = build_registry(config)
```

每次 CLI 執行與每個測試案例使用獨立 Registry。

若未來服務模式需要共享 registry，可由應用程式生命週期容器持有，而非 Registry 模組自行建立 singleton。

---

## 46. Thread Safety

若 Registry 在 freeze 後只讀，通常可安全供多執行緒查找。

建構階段若可能平行註冊，則需要鎖定或禁止平行註冊。

Milestone 3 建議：

```text
Single-threaded construction
Read-only execution
```

不要為尚未存在的平行註冊需求過度設計。

---

## 47. Determinism

相同核心版本、設定與 Plugin 集合，Registry 應產生相同結果。

Registry 不應依賴：

* 檔案系統未排序列舉。
* Python module import 順序。
* 雜湊順序。
* 網路回應順序。
* Plugin discovery 的偶然順序。

Plugin 發現結果應在註冊前排序，例如依 Plugin ID。

Generator list 應依 canonical name 排序。

---

## 48. Idempotent Construction

重複執行：

```python
build_registry(config)
```

應得到等價但獨立的 Registry。

不應因前一次呼叫而發生 duplicate error。

這表示建構流程不可依賴跨呼叫的全域 Registry。

---

## 49. Registry Inspection

可提供只讀診斷資訊：

```python
registry.names()
registry.entries()
registry.describe("course")
```

未來 CLI：

```powershell
opl list
opl list --verbose
opl generator describe course
```

Verbose output 可包含：

```text
Name: course
Source: core
Version: 0.1.0
Aliases: none
Deprecated: no
Description: Generate course-level content
```

Inspection 不應建立 Generator 實例。

---

## 50. Registry Snapshot

為了 debug 或測試，可以建立 snapshot：

```python
@dataclass(frozen=True, slots=True)
class RegistrySnapshot:
    generators: tuple[GeneratorMetadata, ...]
```

Snapshot 可用於：

* Diagnostic output。
* Contract tests。
* Manifest 或 build report。
* 比較 Plugin 載入前後差異。
* 自動文件產生。

Snapshot 不應包含 factory 或可執行物件。

---

## 51. Registry and Manifest

Registry 本身不應寫入 Manifest。

但 Generation Result 或 Manifest 可以記錄：

```json
{
  "generator": {
    "name": "course",
    "source": "core",
    "version": "0.1.0"
  }
}
```

Generator provenance 應來自 Registry metadata，而不是由具體 Generator 隨意填寫。

流程：

```text
Registry Entry Metadata
        │
        ▼
Generator Execution Context
        │
        ▼
Generation Result
        │
        ▼
Manifest
```

---

## 52. Registry and Documentation

Registry metadata 可以成為文件產生來源。

例如自動建立：

```text
docs/reference/generators.md
```

內容可由：

```python
registry.list()
```

產生。

但自動文件工具應使用穩定 metadata，不應執行 Generator 或讀取其私人屬性。

---

## 53. Deprecation

Generator 若準備淘汰，可以標記：

```python
GeneratorMetadata(
    name="old-course",
    deprecated=True,
)
```

查找仍可成功，但 CLI 應顯示警告：

```text
警告：Generator `old-course` 已淘汰，請改用 `course`。
```

建議 metadata 擴充：

```python
replacement: str | None = None
deprecation_message: str | None = None
```

Deprecated Generator：

* 仍需有測試。
* 必須記錄於 CHANGELOG。
* 必須提供 migration 路徑。
* 不應突然移除。

---

## 54. Backward Compatibility

Registry 的公開契約包括：

* Generator 正式名稱。
* Alias。
* Metadata 欄位。
* Lookup 錯誤行為。
* `list()` 排序。
* Duplicate policy。
* Plugin registration contract。

以下變更可能是不相容變更：

* 重新命名 Generator。
* 移除 Alias。
* 改變 factory signature。
* 允許原本禁止的 override。
* 改變名稱大小寫規則。
* 改變 `list()` 回傳型別。
* 改變 duplicate handling。
* 改變 Plugin source identity 格式。

不相容變更必須有 ADR、migration 與版本策略。

---

## 55. Logging

Registry 可以記錄：

* 核心 Generator 註冊成功。
* Plugin Generator 註冊成功。
* Generator 名稱與來源。
* Alias 解析。
* Deprecated Generator 使用。
* Registration conflict。
* Registry freeze。
* 最終 Generator 數量。

一般模式不應輸出大量註冊細節。

Debug 模式可輸出：

```text
registered generator name=course source=core
registered generator name=assessment source=plugin:opl-assessment
```

不得將 factory repr 或含敏感資訊的 dependency 物件完整寫入日誌。

---

## 56. Testing Strategy

Registry Framework 必須包含：

1. Unit Tests
2. Contract Tests
3. CLI Integration Tests
4. Plugin Registration Tests
5. Error Tests
6. Determinism Tests
7. Isolation Tests

---

## 57. Unit Tests

建議檔案：

```text
tests/core/test_registry.py
```

最低測試案例：

* 建立空 Registry。
* 註冊有效 Generator。
* 依名稱取得 entry。
* `contains()` 正確。
* 列出已註冊 Generator。
* 穩定排序。
* 重複名稱失敗。
* 無效名稱失敗。
* 未知名稱失敗。
* factory 建立實例。
* 每次 create 回傳新實例。
* Registry 之間互不污染。

---

## 58. Name Validation Tests

必須涵蓋：

```text
bootstrap
course
week
course-pack
assessment2
```

以及無效名稱：

```text
""
" "
"Course"
"-course"
"course_kit"
"course kit"
"../course"
"course/"
"course\\"
```

每一種失敗應回傳 `InvalidGeneratorNameError`。

---

## 59. Duplicate Tests

應測試：

* 核心與核心同名。
* Plugin 與核心同名。
* Plugin 與 Plugin 同名。
* Alias 與正式名稱衝突。
* Alias 與 Alias 衝突。
* 同一 entry 註冊兩次。
* 衝突後 Registry 狀態未改變。

範例：

```python
def test_duplicate_registration_fails() -> None:
    registry = GeneratorRegistry()
    registry.register(make_entry("course"))

    with pytest.raises(
        DuplicateGeneratorError,
        match="course",
    ):
        registry.register(
            make_entry("course")
        )

    assert registry.names() == ("course",)
```

---

## 60. Lookup Tests

應測試：

* 正式名稱查找。
* Alias 查找。
* 未知名稱。
* 名稱前後空白政策。
* 大小寫政策。
* Deprecated alias。
* 相近名稱建議。
* 查找不建立實例。

---

## 61. Factory Tests

應測試：

* factory 被正確呼叫。
* factory 接收正確 dependencies。
* factory 建構錯誤轉換。
* 原始例外鏈保留。
* `get()` 不呼叫 factory。
* `list()` 不呼叫 factory。
* 每次 `create()` 是否建立獨立實例。
* 有狀態 Generator 不會被共享。

範例：

```python
def test_create_returns_new_instance() -> None:
    registry = GeneratorRegistry()
    registry.register(
        make_entry(
            "course",
            factory=FakeGenerator,
        )
    )

    first = registry.create("course")
    second = registry.create("course")

    assert first is not second
```

---

## 62. Ordering Tests

註冊順序：

```text
week
bootstrap
course
```

列舉結果應為：

```text
bootstrap
course
week
```

除非公開政策明確定義 insertion order。

必須測試：

* `list()`
* `names()`
* unknown error 的可用名稱
* CLI list output
* Registry snapshot

---

## 63. Isolation Tests

必須確認：

```python
registry_a = build_registry(config)
registry_b = build_registry(config)
```

兩者互不影響。

例如：

```python
registry_a.register(
    make_entry("custom")
)

assert registry_a.contains("custom")
assert not registry_b.contains("custom")
```

這能防止全域 singleton 或 module-level state。

---

## 64. Plugin Tests

應涵蓋：

* Plugin Generator 成功註冊。
* 未啟用 Plugin 不註冊。
* Plugin 與核心名稱衝突。
* Plugin metadata 不完整。
* Plugin factory 非 callable。
* Plugin API 不相容。
* 多個 Plugin 穩定註冊順序。
* Plugin 批次註冊部分失敗。
* Plugin source metadata 正確。
* Plugin 關閉後不出現在 list。

---

## 65. CLI Integration Tests

建議測試：

```text
tests/integration/test_cli_integration.py
```

案例：

* `opl list` 顯示所有核心 Generator。
* list 輸出順序穩定。
* CLI 使用 Registry 查找 Generator。
* 未知 Generator 回傳非零 exit code。
* 未知 Generator 顯示可用名稱。
* Plugin Generator 出現在 list。
* Generator alias 可執行。
* Deprecated alias 顯示警告。
* CLI 不維護與 Registry 不同的硬編碼清單。

---

## 66. Contract Tests

核心 Generator catalog 應有契約測試：

```python
def test_core_generator_names() -> None:
    registry = build_core_registry()

    assert registry.names() == (
        "bootstrap",
        "course",
        "week",
    )
```

此測試可防止：

* 核心命令無意間消失。
* 名稱拼字變更。
* 註冊遺漏。
* 輸出順序漂移。

若正式新增 Generator，應同步更新契約測試與文件。

---

## 67. Test Factories

建議建立測試 helper：

```python
def make_entry(
    name: str,
    *,
    source: str = "test",
    aliases: tuple[str, ...] = (),
    factory: Callable[[], Generator] = FakeGenerator,
) -> GeneratorEntry:
    return GeneratorEntry(
        metadata=GeneratorMetadata(
            name=name,
            description=f"Test generator: {name}",
            source=source,
            aliases=aliases,
        ),
        factory=factory,
    )
```

Helper 應降低重複，但不可隱藏測試的重要欄位。

---

## 68. Recommended Module Structure

Milestone 3 建議逐步形成：

```text
generator/
└── core/
    ├── registry.py
    ├── registry_models.py
    ├── registry_validation.py
    ├── exceptions.py
    └── protocols.py
```

較小專案可先使用：

```text
generator/core/registry.py
```

當出現以下情況再拆分：

* Metadata model 增加。
* Alias 規則變複雜。
* Plugin 批次註冊加入。
* Registry snapshot 加入。
* Registry 檔案過長。
* 驗證 helper 可獨立測試。

避免為了符合目錄形式過早拆成大量小檔案。

---

## 69. Recommended Public API

建議只公開：

```python
from generator.core.registry import GeneratorRegistry
from generator.core.registry import GeneratorEntry
from generator.core.registry import GeneratorMetadata
from generator.core.exceptions import RegistryError
```

內部資料結構應保持 private：

```python
_entries
_aliases
_validate_name
_normalize_name
_commit_registration
```

外部程式不得直接修改 Registry 內部 mapping。

---

## 70. Minimal Implementation Example

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol


class Generator(Protocol):
    def generate(self, request: object) -> object:
        ...


class RegistryError(Exception):
    pass


class DuplicateGeneratorError(RegistryError):
    pass


class UnknownGeneratorError(RegistryError):
    pass


@dataclass(frozen=True, slots=True)
class GeneratorMetadata:
    name: str
    description: str
    source: str = "core"


@dataclass(frozen=True, slots=True)
class GeneratorEntry:
    metadata: GeneratorMetadata
    factory: Callable[[], Generator]


class GeneratorRegistry:
    def __init__(self) -> None:
        self._entries: dict[str, GeneratorEntry] = {}

    def register(
        self,
        entry: GeneratorEntry,
    ) -> None:
        name = entry.metadata.name

        if name in self._entries:
            raise DuplicateGeneratorError(
                f"Generator 已註冊：{name}"
            )

        self._entries[name] = entry

    def get(
        self,
        name: str,
    ) -> GeneratorEntry:
        try:
            return self._entries[name]
        except KeyError as exc:
            raise UnknownGeneratorError(
                f"找不到 Generator：{name}"
            ) from exc

    def create(
        self,
        name: str,
    ) -> Generator:
        return self.get(name).factory()

    def contains(
        self,
        name: str,
    ) -> bool:
        return name in self._entries

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._entries))

    def list(
        self,
    ) -> tuple[GeneratorEntry, ...]:
        return tuple(
            self._entries[name]
            for name in sorted(self._entries)
        )
```

此範例只涵蓋基本能力。Alias、Plugin metadata、freeze 與 transactional registration 應依 Milestone 計畫逐步加入。

---

## 71. Milestone 3 Evolution Plan

### Phase 1: Stabilize Core Registry

* 明確定義 `GeneratorRegistry`。
* 提供 register、get、list、contains。
* 拒絕重複名稱。
* 統一 `RegistryError`。
* 加入核心單元測試。
* 移除不必要的全域 Registry。

### Phase 2: Factory-based Construction

* Registry 儲存 factory。
* `create()` 每次建立新 Generator。
* 建立 dependency injection 流程。
* 加入 construction error。
* 增加 factory isolation tests。

### Phase 3: Metadata

* 加入 `GeneratorMetadata`。
* list command 顯示 description。
* 記錄 source 與 version。
* 建立 Registry snapshot。
* 使用 metadata 產生 reference 文件。

### Phase 4: Alias and Deprecation

* 加入 alias index。
* 檢查 alias conflict。
* 支援 deprecated alias。
* 顯示 replacement 建議。
* 加入 backward compatibility tests。

### Phase 5: Plugin Registration

* 定義 Plugin Generator entry contract。
* 加入 source identity。
* 驗證 Plugin compatibility。
* 實作批次驗證。
* 視需求加入 transactional registration。
* Registry 建構完成後 freeze。

---

## 72. Documentation Requirements

每次新增、重新命名或移除 Generator，必須同步更新：

* `docs/architecture/registry.md`
* `docs/architecture/generator.md`
* `docs/reference/generators.md`
* CLI help
* README command examples
* Roadmap
* Generator contract tests
* CLI integration tests
* Plugin documentation，若適用
* CHANGELOG
* Migration guide，若屬不相容變更

Generator catalog 不可只存在於程式碼中。

---

## 73. Code Review Checklist

### Architecture

* [ ] Registry 是否只負責註冊、查找與建立？
* [ ] 是否避免執行 Generator？
* [ ] 是否避免解析 CLI 參數？
* [ ] 是否避免直接載入 YAML？
* [ ] 是否避免依賴具體 Template 或 Filesystem？
* [ ] 是否維持 CLI → Registry → Generator 的依賴方向？
* [ ] 是否沒有新增不必要的全域狀態？
* [ ] Registry 是否由 Composition Root 建立？

### Registration

* [ ] Generator 名稱是否已驗證？
* [ ] factory 是否為 callable？
* [ ] metadata 是否完整？
* [ ] 重複正式名稱是否失敗？
* [ ] Alias 衝突是否失敗？
* [ ] Plugin 與核心名稱衝突是否失敗？
* [ ] 註冊失敗後是否不留下部分狀態？
* [ ] 是否避免隱性 override？
* [ ] 是否記錄 Generator 來源？

### Lookup

* [ ] 正式名稱是否可正確查找？
* [ ] Alias 是否正確解析？
* [ ] 未知名稱是否回傳專用錯誤？
* [ ] 錯誤是否包含可用 Generator？
* [ ] 拼字建議是否只用於訊息？
* [ ] 是否避免自動執行近似名稱？
* [ ] lookup 是否不建立 Generator？
* [ ] 名稱正規化政策是否一致？

### Listing

* [ ] `list()` 是否穩定排序？
* [ ] `names()` 是否穩定排序？
* [ ] CLI list 是否使用 Registry？
* [ ] CLI help 是否與 Registry 一致？
* [ ] Plugin Generator 是否正確顯示？
* [ ] Deprecated Generator 是否可辨識？
* [ ] list 是否不呼叫 factory？

### Factory

* [ ] Registry 是否儲存 factory，而非共享有狀態實例？
* [ ] 每次 create 是否建立獨立實例？
* [ ] factory signature 是否明確？
* [ ] dependency injection 是否集中？
* [ ] factory 建構錯誤是否正確處理？
* [ ] 原始例外是否保留？
* [ ] factory 是否不會在 list 或 lookup 時執行？
* [ ] Generator 是否沒有反向依賴 Registry？

### Composition Root

* [ ] 核心 Generator 是否集中註冊？
* [ ] Plugin Generator 是否在核心之後註冊？
* [ ] Registry 是否每次執行重新建立？
* [ ] 測試是否使用獨立 Registry？
* [ ] 是否避免 module import side effects？
* [ ] 是否避免 import order 決定註冊結果？
* [ ] Registry 建構是否 deterministic？

### Plugin

* [ ] Plugin 是否透過正式 API 註冊？
* [ ] Plugin 是否不能直接修改 Registry 內部 mapping？
* [ ] Plugin source 是否記錄？
* [ ] Plugin compatibility 是否在註冊前驗證？
* [ ] Plugin 名稱衝突是否清楚回報？
* [ ] Plugin 批次註冊失敗政策是否明確？
* [ ] 未啟用 Plugin 是否不註冊？
* [ ] Plugin 排序是否穩定？
* [ ] Plugin 錯誤是否不破壞核心 Registry？

### Error Handling

* [ ] 是否使用 `RegistryError` hierarchy？
* [ ] Duplicate error 是否包含名稱？
* [ ] Unknown error 是否包含查找名稱？
* [ ] Alias conflict 是否指出兩個來源？
* [ ] Construction error 是否與 lookup error 區分？
* [ ] Plugin registration error 是否包含 Plugin ID？
* [ ] CLI 是否回傳非零 exit code？
* [ ] 一般模式是否避免輸出 traceback？

### Determinism

* [ ] 註冊結果是否不依賴 import order？
* [ ] Plugin discovery 是否先排序？
* [ ] list output 是否穩定？
* [ ] unknown error 的可用名稱是否穩定？
* [ ] Registry snapshot 是否穩定？
* [ ] 相同輸入是否建立等價 Registry？
* [ ] 是否沒有依賴 process-wide mutable state？

### Mutability

* [ ] 執行期間是否避免修改 Registry？
* [ ] 是否需要 freeze 機制？
* [ ] 是否避免公開 unregister？
* [ ] Metadata 是否不可變？
* [ ] Registry entries 是否只透過正式 API 修改？
* [ ] 測試清理是否建立新 Registry，而非修改全域 Registry？

### Security

* [ ] Plugin 是否無法隱性覆寫核心 Generator？
* [ ] Generator 名稱是否禁止路徑字元？
* [ ] Metadata 是否不包含敏感資料？
* [ ] 日誌是否不輸出完整 dependency repr？
* [ ] 未信任 Plugin entry 是否在註冊前驗證？
* [ ] Registry 是否不執行 Plugin 提供的任意 discovery code 之外功能？
* [ ] factory 是否只在 create 時執行？

### Testing

* [ ] 空 Registry 是否有測試？
* [ ] 有效註冊是否有測試？
* [ ] 無效名稱是否有測試？
* [ ] 重複註冊是否有測試？
* [ ] 未知名稱是否有測試？
* [ ] Alias 是否有測試？
* [ ] Alias conflict 是否有測試？
* [ ] 穩定排序是否有測試？
* [ ] factory 建構是否有測試？
* [ ] factory failure 是否有測試？
* [ ] 每次 create 回傳新實例是否有測試？
* [ ] Registry isolation 是否有測試？
* [ ] Plugin registration 是否有測試？
* [ ] CLI list 是否有整合測試？
* [ ] 核心 Generator catalog 是否有 contract test？
* [ ] 完整 test suite 是否通過？

### Documentation

* [ ] `docs/architecture/registry.md` 是否更新？
* [ ] `docs/architecture/generator.md` 是否同步？
* [ ] Generator reference 是否更新？
* [ ] CLI help 是否更新？
* [ ] README 範例是否更新？
* [ ] Plugin 文件是否更新？
* [ ] 新增 Alias 是否記錄？
* [ ] Deprecated Generator 是否記錄？
* [ ] 不相容變更是否加入 migration guide？
* [ ] CHANGELOG 是否更新？

---

## 74. Acceptance Criteria

Registry Framework 可視為 Milestone 3 基礎完成，至少需符合：

* 核心 Generator 可透過單一 Registry 註冊。
* `bootstrap`、`course`、`week` 可穩定列舉與查找。
* 重複名稱會明確失敗。
* 未知名稱會回傳專用錯誤。
* list 輸出排序穩定。
* CLI 不再維護獨立 Generator catalog。
* Registry 不使用 process-wide mutable singleton。
* 每次 `create()` 建立獨立 Generator 實例。
* Registry 與 Generator 執行責任明確分離。
* Plugin 名稱衝突政策已有定義。
* 單元測試與 CLI 整合測試完整。
* 文件、測試與實作保持同步。
* `pre-commit` 與完整 pytest suite 通過。

---

## 75. Related Documents

* `docs/architecture/generator.md`
* `docs/architecture/configuration.md`
* `docs/architecture/template.md`
* `docs/reference/generators.md`
* `docs/reference/filesystem.md`
* `docs/configuration.md`
* `docs/cli.md`
* `docs/ROADMAP.md`
* `generator/core/registry.py`
* `generator/core/config.py`
* `generator/core/exceptions.py`
* `generator/cli/main.py`
* `generator/generators/bootstrap_generator.py`
* `generator/generators/course_generator.py`
* `generator/generators/week_generator.py`
* `tests/core/test_registry.py`
* `tests/integration/test_cli_integration.py`
