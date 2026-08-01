# OpenProjectLab Errors Reference

> Status: Active
> Audience: CLI users, maintainers, contributors, Generator developers, SDK developers
> Scope: Framework exceptions, CLI messages, exit codes, recovery guidance, and diagnostics

本文件說明 OpenProjectLab（OPL）目前與規劃中的錯誤處理契約，包括：

* Framework Exception 分類
* 錯誤訊息格式
* CLI Exit Code
* 常見錯誤與修正方式
* Exception Chaining
* `stdout` 與 `stderr`
* Debug 與 Logging
* 測試與驗證方式

本文件聚焦於「發生錯誤時，使用者與開發者應如何理解及處理」。

關於錯誤處理的架構責任、Layer 邊界與演進方向，請參閱：

* [Error Handling Architecture](../architecture/error-handling.md)

---

## 1. 錯誤處理基本原則

OPL 的錯誤處理遵循以下原則：

* 錯誤應在最接近問題來源的 Layer 被識別。
* 底層例外應轉換成具有 OPL 語意的 Framework Exception。
* 原始例外應透過 Exception Chaining 保留。
* 一般使用者訊息應清楚、具體且可操作。
* 技術細節應放入 Debug Log 或 Traceback。
* 錯誤輸出應寫入 `stderr`。
* 成功輸出應寫入 `stdout`。
* 底層模組不應直接呼叫 `sys.exit()`。
* CLI 負責將 Exception 轉換成 Exit Code。
* 預期錯誤與未預期程式錯誤必須區分。

---

## 2. Framework Root Exception

建議所有可預期的 OPL Framework 錯誤都繼承：

```python
class OpenProjectLabError(Exception):
    """Base exception for expected OpenProjectLab failures."""
```

CLI 或 SDK 使用者可以捕捉：

```python
try:
    ...
except OpenProjectLabError as exc:
    ...
```

這不表示所有 Python 例外都應轉成 `OpenProjectLabError`。

以下未預期錯誤可能表示程式缺陷：

```text
TypeError
AttributeError
AssertionError
RuntimeError
```

它們通常應保留原始 Traceback。

---

## 3. 建議的 Exception Hierarchy

```text
OpenProjectLabError
├── ConfigurationError
│   ├── ConfigurationFileNotFoundError
│   ├── ConfigurationSyntaxError
│   ├── ConfigurationStructureError
│   ├── ConfigurationValueError
│   └── ConfigurationVersionError
├── RegistryError
│   ├── InvalidGeneratorNameError
│   ├── DuplicateGeneratorError
│   └── GeneratorNotFoundError
├── GeneratorError
│   ├── GeneratorValidationError
│   ├── GenerationPlanError
│   ├── OutputConflictError
│   ├── GenerationAbortedError
│   └── OutputValidationError
├── TemplateError
│   ├── TemplateRootError
│   ├── TemplateNotFoundError
│   ├── TemplatePathError
│   ├── TemplateContextError
│   ├── TemplateSyntaxError
│   └── TemplateRenderError
└── FilesystemError
    ├── DirectoryCreationError
    ├── FileReadError
    ├── FileWriteError
    ├── PathContainmentError
    └── AtomicWriteError
```

目前 Repository 可能尚未實作所有子類別。

正式可用的 Exception 應以：

```text
generator/core/exceptions.py
```

及相關測試為準。

---

## 4. ConfigurationError

`ConfigurationError` 表示設定檔、設定結構或設定值無效。

常見原因：

* 設定檔不存在
* YAML 格式錯誤
* YAML 根節點不是 Mapping
* Section 不是 Mapping
* 必要欄位缺失
* 路徑欄位型別錯誤
* 設定版本不支援

概念使用：

```python
raise ConfigurationError(
    f"找不到設定檔：{path}"
)
```

目前 `ProjectConfig.load()` 已可能使用此類別處理：

* Missing Configuration File
* Invalid YAML
* Invalid Top-Level Structure
* Invalid Section Type

---

## 5. ConfigurationFileNotFoundError

此錯誤表示指定設定檔不存在。

範例訊息：

```text
找不到設定檔：
F:\OpenProjectLab\config\missing.yaml
```

可能修正方式：

* 確認 `--config` 路徑是否正確。
* 確認檔名與副檔名。
* 確認目前使用的專案目錄。
* 確認檔案沒有被移動或刪除。
* 使用預設設定檔位置。

CLI 範例：

```powershell
opl --config config\default.yaml list
```

---

## 6. ConfigurationSyntaxError

此錯誤表示 YAML 無法解析。

常見原因：

* 縮排錯誤
* 冒號缺失
* 引號未關閉
* List 與 Mapping 混用
* Tab 與 Space 混用
* 無效特殊字元

範例：

```yaml
project:
  name: "OpenProjectLab
```

此處字串缺少結尾引號。

建議驗證：

```powershell
python -c "import yaml, pathlib; print(yaml.safe_load(pathlib.Path('config/default.yaml').read_text(encoding='utf-8')))"
```

---

## 7. ConfigurationStructureError

此錯誤表示 YAML 可以解析，但資料結構不符合預期。

錯誤範例：

```yaml
paths: templates
```

若 `paths` 必須是 Mapping，正確形式應為：

```yaml
paths:
  template_root: ../templates
```

範例錯誤訊息：

```text
設定區段 `paths` 必須是 Mapping，
但目前型別為 String。
```

---

## 8. ConfigurationValueError

此錯誤表示欄位存在，但值無效。

例如：

```yaml
generator:
  overwrite: "sometimes"
```

若 `overwrite` 必須為 Boolean，應使用：

```yaml
generator:
  overwrite: false
```

其他可能情境：

* 空字串
* 負數週次
* 不支援的模式
* 不存在的必要目錄
* 無效編碼名稱
* 不合法的 Generator 名稱

---

## 9. ConfigurationVersionError

未來設定檔若具有版本：

```yaml
version: 2
```

但目前 OPL 只支援 Version 1，可能產生：

```text
不支援設定版本：2
目前支援版本：1
```

若版本機制尚未實作，此錯誤屬於規劃能力。

---

## 10. RegistryError

`RegistryError` 表示 Generator 註冊或查詢失敗。

常見原因：

* Generator 名稱不存在
* 名稱重複
* 名稱格式錯誤
* 註冊物件不符合 Generator 契約

Registry 不應直接將：

```python
KeyError
```

暴露給 CLI 使用者。

---

## 11. GeneratorNotFoundError

此錯誤表示要求的 Generator 不存在。

範例：

```text
找不到 Generator：lesson

可用 Generator：
- bootstrap
- course
- week
```

目前可使用：

```powershell
opl list
```

確認可用 Generator。

---

## 12. DuplicateGeneratorError

此錯誤表示同一名稱被註冊超過一次。

例如：

```python
registry.register(
    FirstCourseGenerator()
)

registry.register(
    SecondCourseGenerator()
)
```

若兩者名稱皆為：

```text
course
```

第二次註冊應失敗。

範例訊息：

```text
Generator 已註冊：course
```

Registry 不應靜默覆寫原有 Generator。

---

## 13. InvalidGeneratorNameError

Generator 名稱若不符合規則，應產生此錯誤。

建議合法名稱：

```text
bootstrap
course
week
course-pack
```

不合法範例：

```text
Course
week generator
../week
--course
course\week
```

建議格式：

```text
^[a-z][a-z0-9-]*$
```

正式驗證規則應以目前實作為準。

---

## 14. GeneratorError

`GeneratorError` 表示 Generator 無法完成其工作。

常見原因：

* Request 無效
* Generation Plan 無法建立
* 必要輸入缺失
* 輸出路徑衝突
* 渲染結果驗證失敗
* 寫入過程無法完成
* 執行被中止

Generator 應提供足夠資訊指出：

* 哪個 Generator
* 哪個 Request
* 哪個 Target
* 發生在哪個階段
* 是否有部分輸出

---

## 15. GeneratorValidationError

此錯誤表示 Generator Request 無效。

例如：

```python
if request.week_number < 1:
    raise GeneratorValidationError(
        "week_number 必須大於或等於 1"
    )
```

其他可能情境：

* Course ID 為空
* Target 缺失
* 不支援的輸出格式
* 必要 Metadata 缺失
* 不合法的課程名稱
* Template 選擇無效

---

## 16. GenerationPlanError

此錯誤表示無法建立合法的 Generation Plan。

例如：

* 同一個輸出路徑出現兩次
* Template 與輸出 Mapping 不完整
* Destination 超出 Output Root
* 必要 Planned File 缺失
* Plan 內存在互相衝突的操作

範例：

```text
無法建立 Week Generation Plan：
輸出路徑重複：README.md
```

若 Generation Plan 尚未正式實作，此類別屬於規劃能力。

---

## 17. OutputConflictError

此錯誤表示輸出已存在，而且目前 Policy 不允許覆寫。

範例：

```text
目標檔案已存在：
courses\java\week-01\README.md
```

可能修正方式：

* 使用新的輸出目錄。
* 刪除舊輸出。
* 備份舊檔案。
* 使用明確覆寫選項。
* 改用 Skip Existing Policy。

不應在沒有明確授權時自動覆寫使用者內容。

---

## 18. GenerationAbortedError

此錯誤表示執行被中止。

可能原因：

* 使用者取消
* 前置驗證失敗
* Template 驗證失敗
* 寫入前偵測到衝突
* Atomic Commit 失敗

錯誤應指出：

* 是否尚未寫入任何檔案
* 是否存在部分輸出
* 是否已完成清理
* 是否可以安全重試

---

## 19. OutputValidationError

此錯誤表示 Template 已渲染，但產出的內容無效。

例如：

* YAML 無法解析
* TOML 無法解析
* JSON 無法解析
* Python 語法錯誤
* 必要 Markdown 標題缺失
* Metadata 欄位錯誤

範例：

```text
產出驗證失敗：
Template：course/metadata.yaml.j2
原因：渲染後內容不是合法 YAML。
```

---

## 20. TemplateError

`TemplateError` 表示 Template 尋找、驗證或渲染失敗。

常見原因：

* Template Root 不存在
* Template 不存在
* Template 路徑逃逸
* Context 缺少必要變數
* Template 語法錯誤
* Include 找不到
* Filter 不存在
* Template Engine 渲染失敗

---

## 21. TemplateRootError

此錯誤表示 Template Root 無效。

例如：

```text
Template Root 不存在：
F:\OpenProjectLab\templates
```

可能修正方式：

* 檢查 `paths.template_root`。
* 確認相對路徑基準。
* 確認目錄名稱大小寫。
* 確認 Template 是否包含在安裝套件中。
* 確認目前使用的設定檔。

---

## 22. TemplateNotFoundError

此錯誤表示指定 Template 不存在。

範例：

```text
找不到 Template：
week/README.md.j2

Template Root：
F:\OpenProjectLab\templates
```

檢查命令：

```powershell
Get-ChildItem templates -Recurse
```

或：

```powershell
Get-ChildItem generator\templates -Recurse
```

還應確認實際 Template Root 使用哪個位置。

---

## 23. TemplatePathError

此錯誤表示 Template 路徑不安全或不合法。

應拒絕：

```text
../../private.txt
```

```text
C:\Users\User\.ssh\id_ed25519
```

```text
\\server\share\secret.txt
```

Template Resolver 應確認解析後路徑仍位於 Template Root 內。

---

## 24. TemplateContextError

此錯誤表示 Template 缺少必要 Context，或 Context 型別不正確。

Template：

```jinja2
# Week {{ week_number }}: {{ week_title }}
```

Context：

```python
{
    "week_number": 1,
}
```

此時缺少：

```text
week_title
```

範例訊息：

```text
無法渲染 Template `week/README.md.j2`：
缺少必要 Context 變數 `week_title`。
```

不應靜默產生：

```markdown
# Week 1:
```

---

## 25. TemplateSyntaxError

此錯誤表示 Template 語法不正確。

錯誤範例：

```jinja2
{% if include_lab %}
## Lab
```

缺少：

```jinja2
{% endif %}
```

錯誤訊息應盡可能包含：

* Template 名稱
* 行號
* 原始 Template Engine 訊息
* Exception Chain

---

## 26. TemplateRenderError

此錯誤表示 Template 已被找到且語法可能有效，但渲染過程失敗。

可能原因：

* Filter 不存在
* Include 失敗
* 型別操作錯誤
* Undefined Variable
* Template Engine 內部錯誤

範例：

```text
無法渲染 Template：
week/README.md.j2
```

原始 Template Engine 例外應透過 Chaining 保留。

---

## 27. FilesystemError

`FilesystemError` 表示檔案或目錄操作失敗。

常見原因：

* 權限不足
* 路徑不存在
* 無法建立目錄
* 無法讀取
* 無法寫入
* 檔案被其他程式鎖定
* 路徑超出 Output Root
* Atomic Rename 失敗
* 磁碟空間不足

---

## 28. DirectoryCreationError

此錯誤表示無法建立目錄。

範例：

```text
無法建立輸出目錄：
F:\OpenProjectLab\courses\java\week-01
```

可能原因：

* 權限不足
* 上層路徑不存在
* 同名檔案已存在
* 路徑名稱不合法
* 防毒軟體或同步程式鎖定
* 磁碟錯誤

---

## 29. FileReadError

此錯誤表示無法讀取檔案。

可能原因：

* 檔案不存在
* 權限不足
* 編碼錯誤
* 檔案被鎖定
* 路徑是目錄而非檔案

範例：

```text
無法讀取 Template：
templates\week\README.md.j2
```

---

## 30. FileWriteError

此錯誤表示無法寫入檔案。

範例：

```text
無法寫入檔案：
courses\java\week-01\README.md
```

可能修正方式：

* 確認檔案未被其他程式鎖定。
* 確認目錄權限。
* 確認磁碟空間。
* 確認路徑合法。
* 關閉正在使用該檔案的編輯器或同步程式。

---

## 31. PathContainmentError

此錯誤表示輸出路徑超出允許的 Output Root。

例如 Output Root：

```text
F:\OpenProjectLab\courses
```

但 Destination 解析為：

```text
F:\private.txt
```

此操作應被拒絕。

範例訊息：

```text
輸出路徑超出允許範圍：
F:\private.txt

允許的 Output Root：
F:\OpenProjectLab\courses
```

---

## 32. AtomicWriteError

此錯誤表示 Atomic Write 過程失敗。

典型流程：

```text
Write Temporary File
  ↓
Validate
  ↓
Replace Destination
```

可能失敗於：

* 暫存檔建立
* Flush
* Rename
* Replace
* Cleanup

錯誤應說明：

* 正式檔案是否保持不變
* 暫存檔是否已刪除
* 是否可安全重試

若 Atomic Write 尚未實作，此錯誤屬於規劃能力。

---

## 33. 預期錯誤與未預期錯誤

### 預期錯誤

系統已知且使用者可以理解或修正。

例如：

```text
ConfigurationError
GeneratorNotFoundError
TemplateNotFoundError
OutputConflictError
```

一般 CLI 行為：

* 顯示簡潔錯誤訊息
* 不顯示完整 Traceback
* 回傳穩定的非零 Exit Code

### 未預期錯誤

通常表示程式缺陷或未考慮情境。

例如：

```text
TypeError
AttributeError
AssertionError
RuntimeError
```

一般 CLI 行為：

* 顯示「內部錯誤」
* 回傳 Exit Code `1`
* Debug 模式顯示 Traceback
* 建立 Regression Test

---

## 34. Exception Chaining

底層例外應保留：

```python
try:
    ...
except OSError as exc:
    raise FileWriteError(
        f"無法寫入檔案：{target}"
    ) from exc
```

使用：

```python
raise NewError(...) from exc
```

可以同時提供：

* 使用者友善訊息
* 原始錯誤類型
* Traceback
* 開發者診斷資訊
* 可測試的 `__cause__`

---

## 35. 不應使用的錯誤處理方式

不建議：

```python
try:
    ...
except Exception:
    pass
```

不建議：

```python
try:
    ...
except Exception:
    return None
```

不建議：

```python
try:
    ...
except Exception:
    raise GeneratorError("失敗")
```

除非確實能合理分類所有被捕捉錯誤。

問題包括：

* 隱藏真正 Bug
* 失去原始語意
* 讓失敗被誤認為成功
* 測試難以發現問題
* 使用者不知道如何修正

---

## 36. CLI Exit Codes

建議 Exit Code：

| Exit Code | 說明                      |
| --------: | ----------------------- |
|       `0` | 成功                      |
|       `1` | 未分類或內部錯誤                |
|       `2` | CLI 使用方式錯誤              |
|       `3` | 設定錯誤                    |
|       `4` | Registry 或 Generator 錯誤 |
|       `5` | Template 錯誤             |
|       `6` | Filesystem 或輸出錯誤        |
|     `130` | 使用者以 `Ctrl+C` 中斷        |

這是建議契約。

正式行為應以目前 CLI 實作與測試為準。

---

## 37. Exit Code Mapping

概念：

```python
def exit_code_for(
    exc: OpenProjectLabError,
) -> int:
    if isinstance(exc, ConfigurationError):
        return 3

    if isinstance(exc, RegistryError):
        return 4

    if isinstance(exc, GeneratorError):
        return 4

    if isinstance(exc, TemplateError):
        return 5

    if isinstance(exc, FilesystemError):
        return 6

    return 1
```

Exit Code Mapping 應集中管理。

不應由：

* Configuration Loader
* Registry
* Generator
* Template Renderer
* File Writer

各自決定 Process Exit Code。

---

## 38. argparse Exit Code

Python `argparse` 對 CLI 使用方式錯誤通常使用：

```text
2
```

例如：

* 缺少必要參數
* 無效 Option
* 無效子命令
* 錯誤值格式

CLI 應確認是否保留 `argparse` 標準行為，或使用自訂 Parser Error Strategy。

---

## 39. KeyboardInterrupt

使用者按下：

```text
Ctrl+C
```

通常會產生：

```python
KeyboardInterrupt
```

建議 CLI 行為：

```python
except KeyboardInterrupt:
    print(
        "操作已取消。",
        file=sys.stderr,
    )
    return 130
```

若執行中已建立部分輸出，應同時說明：

* 已建立哪些檔案
* 是否完成清理
* 是否可以重新執行

---

## 40. stdout 與 stderr

正常輸出應寫入：

```python
sys.stdout
```

例如：

```text
bootstrap
course
week
```

錯誤輸出應寫入：

```python
sys.stderr
```

例如：

```text
錯誤：找不到設定檔。
```

這讓 Script 可以分別處理輸出：

```powershell
opl list 1>output.txt 2>error.txt
```

---

## 41. CLI 錯誤格式

簡單錯誤：

```text
錯誤：找不到 Generator：lesson
```

較複雜錯誤：

```text
錯誤：無法載入設定檔。

設定檔：
F:\OpenProjectLab\config\default.yaml

原因：
`paths` 必須是 Mapping。

建議：
請檢查 YAML 縮排與欄位結構。
```

格式應保持：

* 簡潔
* 一致
* 易於閱讀
* 不暴露不必要內部資訊

---

## 42. 錯誤訊息設計

好的錯誤訊息應包含以下資訊中的必要部分：

* 發生什麼事
* 發生在哪裡
* 問題原因
* 使用者如何修正
* 是否存在部分輸出
* 是否可以重試

較差：

```text
Generation failed.
```

較佳：

```text
Week Generator 無法完成輸出：
目標檔案已存在：
courses\java\week-01\README.md

請使用新的輸出目錄，或啟用明確的覆寫選項。
```

---

## 43. 錯誤訊息不是程式契約

不應：

```python
if str(exc) == "Template not found":
    ...
```

應使用：

```python
except TemplateNotFoundError:
    ...
```

錯誤文字可以改善或翻譯。

真正適合作為程式契約的是：

* Exception Type
* Error Code
* Structured Metadata
* Exit Code

---

## 44. Error Codes

未來 OPL 可以為錯誤提供穩定 Code：

```text
OPL-CONFIG-001
OPL-REGISTRY-001
OPL-GENERATOR-001
OPL-TEMPLATE-001
OPL-FS-001
```

概念：

```python
class OpenProjectLabError(Exception):
    code = "OPL-UNKNOWN"
```

```python
class TemplateNotFoundError(TemplateError):
    code = "OPL-TEMPLATE-001"
```

用途：

* Automation
* SDK
* JSON Output
* 文件搜尋
* 多語系支援
* Issue 分類

若 Error Code 尚未實作，不應依賴此能力。

---

## 45. Structured Error Metadata

未來 Exception 可保存結構化資訊：

```python
class TemplateNotFoundError(TemplateError):
    def __init__(
        self,
        template_name: str,
        template_root: Path,
    ) -> None:
        self.template_name = template_name
        self.template_root = template_root

        super().__init__(
            f"找不到 Template：{template_name}"
        )
```

呼叫者可以直接使用：

```python
exc.template_name
```

而不是解析：

```python
str(exc)
```

---

## 46. Debug Mode

一般模式應顯示：

```text
錯誤：找不到 Template：week/README.md.j2
```

Debug 模式可以額外顯示：

* Exception Type
* Exception Chain
* Traceback
* Template Root
* Output Root
* Generator Name
* 解析後路徑
* 相關設定值

Debug 模式仍不應顯示：

* Password
* Token
* SSH Private Key
* Cookie
* Secret Environment Variable

若 `--debug` 尚未實作，此能力屬於規劃。

---

## 47. Logging

Library Code 應使用：

```python
import logging

logger = logging.getLogger(__name__)
```

Library 不應在 Import 時執行：

```python
logging.basicConfig(...)
```

Logging 設定應由 CLI 或 Host Application 負責。

---

## 48. Logging Levels

### DEBUG

適合：

* 解析後路徑
* Template 名稱
* Generator 選擇
* Generation Plan
* Skip 原因
* Exception Chain

### INFO

適合：

* 開始產生
* 完成產生
* 載入設定
* 建立檔案數量

### WARNING

適合：

* 跳過既有檔案
* 使用棄用功能
* 非致命格式問題
* 相容性警告

### ERROR

適合：

* 可預期但無法完成的 Framework 操作

### CRITICAL

適合：

* Application 無法維持基本狀態
* 嚴重內部錯誤

---

## 49. 避免重複 Logging

不應在每一層都記錄相同錯誤。

例如：

```text
Filesystem Layer logs
Generator Layer logs
Application Layer logs
CLI Layer logs
```

結果會出現四次相同訊息。

建議：

* 底層建立具體 Exception。
* 中間層只在增加重要 Context 時包裝。
* 最外層負責最終 Log 與使用者輸出。
* Debug 模式顯示 Exception Chain。

---

## 50. 敏感資訊

錯誤訊息與 Log 不應包含：

* API Token
* Password
* SSH Private Key
* Authentication Header
* Cookie
* Secret Environment Variable
* 不必要的個人資訊
* Template Context 中的敏感資料

錯誤範例：

```text
Authentication failed with token ghp_example_secret
```

較佳：

```text
GitHub authentication failed.
```

---

## 51. 本機路徑

本機 CLI 錯誤通常可以顯示相關路徑，例如：

```text
F:\OpenProjectLab\config\default.yaml
```

但寫入以下位置時應評估遮蔽：

* CI Log
* Issue Report
* Telemetry
* Remote API
* Shared Artifact

例如：

```text
C:\Users\KHWang\
```

可視情況改為：

```text
<user-home>\
```

---

## 52. Partial Failure

Generator 可能建立部分檔案後才失敗。

錯誤應說明：

* 是否已建立檔案
* 是否已更新檔案
* 是否已完成清理
* 是否留下暫存檔
* 是否可以安全重試

範例：

```text
Week Generator 未能完成。

已建立：
- week-01\README.md
- week-01\lab.md

尚未建立：
- week-01\quiz.md

請檢查輸出目錄後再重新執行。
```

理想情況應使用 Transactional Generation 避免部分輸出。

---

## 53. Recovery Guidance

### 找不到設定檔

```text
請確認 `--config` 指定的路徑，
或使用預設設定檔 `config/default.yaml`。
```

### YAML 無效

```text
請檢查錯誤行附近的縮排、冒號與引號。
```

### Generator 不存在

```text
請執行 `opl list` 查看可用 Generator。
```

### Template 不存在

```text
請檢查 `paths.template_root`，
並確認指定 Template 已存在。
```

### 檔案已存在

```text
請使用新目錄，或使用明確覆寫選項。
```

### 寫入權限不足

```text
請確認輸出目錄權限，
並確認檔案未被其他程式鎖定。
```

---

## 54. Retry

以下錯誤通常不應自動重試：

* 無效設定
* Template 不存在
* Generator 不存在
* 無效 Request
* 路徑逃逸
* 輸出衝突

未來若加入網路或遠端儲存，以下錯誤可能可以重試：

* 暫時性網路中斷
* Rate Limit
* 暫時檔案鎖定
* 遠端服務短暫不可用

Retry 必須定義：

* 最大次數
* Backoff
* 可重試錯誤
* Idempotency
* Cancellation
* Logging

---

## 55. Assertions

`assert` 適合檢查內部不變量。

例如：

```python
assert plan.files
```

不應用於使用者輸入：

```python
assert request.week_number > 0
```

應使用：

```python
if request.week_number < 1:
    raise GeneratorValidationError(
        "week_number 必須大於或等於 1"
    )
```

原因：

* `assert` 可被最佳化模式移除。
* `AssertionError` 不適合作為使用者錯誤。
* 錯誤訊息與分類不夠明確。

---

## 56. 常見問題排除

### 問題：執行 `opl list` 顯示設定錯誤

檢查：

```powershell
Test-Path config\default.yaml
```

查看內容：

```powershell
Get-Content config\default.yaml
```

執行設定測試：

```powershell
python -m pytest tests\core\test_config.py -v
```

---

### 問題：找不到 Generator

執行：

```powershell
opl list
```

目前預期：

```text
bootstrap
course
week
```

檢查 Registry：

```powershell
Get-Content generator\core\registry.py
```

---

### 問題：找不到 Template

列出 Template：

```powershell
Get-ChildItem templates -Recurse -ErrorAction SilentlyContinue
```

```powershell
Get-ChildItem generator\templates -Recurse -ErrorAction SilentlyContinue
```

搜尋 Template Root：

```powershell
Get-ChildItem generator -Recurse -Filter *.py |
    Select-String -Pattern "template_root"
```

---

### 問題：檔案無法寫入

確認路徑：

```powershell
Test-Path <output-directory>
```

確認檔案屬性：

```powershell
Get-Item <output-file> |
    Format-List *
```

檢查是否為唯讀：

```powershell
Get-Item <output-file> |
    Select-Object FullName, IsReadOnly
```

---

### 問題：pre-commit 修改檔案後失敗

這通常表示 Hook 已自動修正檔案。

重新檢查：

```powershell
git status --short
git diff
```

再重新加入：

```powershell
git add .
```

然後再次執行：

```powershell
pre-commit run --all-files
```

---

## 57. 測試 Exception Hierarchy

概念：

```python
def test_configuration_error_is_framework_error():
    assert issubclass(
        ConfigurationError,
        OpenProjectLabError,
    )
```

```python
def test_template_error_is_framework_error():
    assert issubclass(
        TemplateError,
        OpenProjectLabError,
    )
```

---

## 58. 測試 Exception Chaining

```python
def test_invalid_yaml_preserves_cause(
    tmp_path,
):
    path = tmp_path / "config.yaml"
    path.write_text(
        "project: [",
        encoding="utf-8",
    )

    with pytest.raises(
        ConfigurationError
    ) as exc_info:
        ProjectConfig.load(path)

    assert exc_info.value.__cause__ is not None
```

實際 Exception 類型應依目前實作調整。

---

## 59. 測試錯誤訊息

不要過度依賴完整錯誤文字。

建議：

```python
assert "config.yaml" in str(exc_info.value)
assert "YAML" in str(exc_info.value)
```

若 Error Code 已實作：

```python
assert exc_info.value.code == "OPL-CONFIG-002"
```

---

## 60. 測試 stderr

```python
def test_cli_writes_error_to_stderr(
    capsys,
):
    exit_code = main([
        "--config",
        "missing.yaml",
        "list",
    ])

    captured = capsys.readouterr()

    assert exit_code != 0
    assert captured.out == ""
    assert captured.err
```

---

## 61. 測試 Exit Code

```python
@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (ConfigurationError("x"), 3),
        (RegistryError("x"), 4),
        (TemplateError("x"), 5),
        (FilesystemError("x"), 6),
    ],
)
def test_exit_code_mapping(
    error,
    expected,
):
    assert exit_code_for(error) == expected
```

若目前尚未採用分類 Exit Code，應先測試現有行為。

---

## 62. 測試未預期錯誤

```python
def test_unexpected_error_returns_one(
    monkeypatch,
    capsys,
):
    def fail(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        target_module,
        "run_application",
        fail,
    )

    exit_code = main(["list"])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "內部錯誤" in captured.err
```

---

## 63. 測試敏感資料

```python
def test_error_does_not_expose_secret():
    secret = "super-secret-token"

    error = build_authentication_error(
        secret
    )

    assert secret not in str(error)
```

未來也應測試：

* Log
* JSON Error
* Debug Formatter
* Exception Metadata

---

## 64. Error Integration Matrix

| 情境            | 建議 Exception                     | 建議 Exit Code |
| ------------- | -------------------------------- | -----------: |
| 設定檔不存在        | `ConfigurationFileNotFoundError` |          `3` |
| YAML 無效       | `ConfigurationSyntaxError`       |          `3` |
| 設定結構錯誤        | `ConfigurationStructureError`    |          `3` |
| Generator 不存在 | `GeneratorNotFoundError`         |          `4` |
| 名稱重複          | `DuplicateGeneratorError`        |          `4` |
| Request 無效    | `GeneratorValidationError`       |          `4` |
| Template 不存在  | `TemplateNotFoundError`          |          `5` |
| Context 缺失    | `TemplateContextError`           |          `5` |
| 輸出衝突          | `OutputConflictError`            |    `4` 或 `6` |
| 寫入權限不足        | `FileWriteError`                 |          `6` |
| 路徑逃逸          | `PathContainmentError`           |          `6` |
| 使用者中斷         | `KeyboardInterrupt`              |        `130` |
| 未預期 Bug       | 原始 Exception                     |          `1` |

`OutputConflictError` 應屬於 Generator 或 Filesystem，需由正式架構決定。

---

## 65. 檢查目前 Exception 實作

查看檔案：

```powershell
Get-Content generator\core\exceptions.py
```

搜尋 Exception 定義：

```powershell
Get-ChildItem generator -Recurse -Filter *.py |
    Select-String -Pattern `
        "class .*Error|raise |except " |
    Select-Object Path, LineNumber, Line
```

---

## 66. 搜尋 Broad Exception

搜尋：

```powershell
Get-ChildItem generator -Recurse -Filter *.py |
    Select-String -Pattern `
        "except Exception|except BaseException|except:"
```

每個結果都應確認：

* 是否必要
* 是否位於 Top-Level
* 是否保留 Traceback
* 是否回傳正確 Exit Code
* 是否可能隱藏 Bug
* 是否有測試

---

## 67. 搜尋 Silent Failure

搜尋：

```powershell
Get-ChildItem generator -Recurse -Filter *.py |
    Select-String -Pattern `
        "except .*:\s*$|pass$|return None"
```

此搜尋可能產生誤判，需人工 Review。

重點是找出：

```python
except OSError:
    pass
```

或捕捉後未回報失敗的程式碼。

---

## 68. 搜尋 sys.exit

底層 Framework 不應呼叫 `sys.exit()`。

搜尋：

```powershell
Get-ChildItem generator -Recurse -Filter *.py |
    Select-String -Pattern `
        "sys\.exit|raise SystemExit"
```

合理位置通常只應位於：

* CLI Entry Point
* Console Script Wrapper

---

## 69. 搜尋錯誤輸出

```powershell
Get-ChildItem generator -Recurse -Filter *.py |
    Select-String -Pattern `
        "stderr|print\(|logging|logger|traceback" |
    Select-Object Path, LineNumber, Line
```

確認：

* 錯誤是否寫入 `stderr`
* Library 是否直接 `print()`
* 是否重複 Logging
* 是否呼叫 `basicConfig()`
* 是否顯示敏感資料

---

## 70. 執行錯誤相關測試

核心測試：

```powershell
python -m pytest tests\core -v
```

CLI 測試：

```powershell
python -m pytest tests\test_cli.py -v
```

整合測試：

```powershell
python -m pytest tests\integration -v
```

完整測試：

```powershell
python -m pytest
```

---

## 71. 新增 Exception 流程

### Step 1：確認錯誤語意

回答：

* 哪個 Layer 擁有？
* 呼叫者需要區分嗎？
* 是否已有合適父類別？
* 是否屬於預期錯誤？

### Step 2：定義 Exception

加入適當模組：

```text
generator/core/exceptions.py
```

或未來專屬子模組。

### Step 3：加入 Metadata

例如：

* Path
* Field
* Generator Name
* Template Name
* Error Code

### Step 4：保留原始例外

使用：

```python
raise NewError(...) from exc
```

### Step 5：更新 CLI Mapping

必要時新增：

* Exit Code
* Formatter
* Recovery Guidance

### Step 6：新增測試

至少測試：

* Parent Class
* 觸發條件
* Message 關鍵內容
* Exception Chaining
* CLI Exit Code
* `stderr`

### Step 7：更新文件

至少更新：

* Errors Reference
* Error Handling Architecture
* CLI Reference
* SDK Architecture（若公開）
* Changelog

---

## 72. 修改既有 Exception

修改前確認：

* 是否更改父類別？
* 是否影響既有 `except`？
* 是否更改 Error Code？
* 是否更改 Exit Code？
* 是否移除 Metadata？
* 是否為 Public SDK Contract？
* 是否需要 Deprecation？
* 是否需要 Migration Guide？

將 Exception 移到其他階層可能是破壞性變更。

---

## 73. Error Review Checklist

### Exception Design

* [ ] Exception 代表明確語意。
* [ ] 父類別正確。
* [ ] 所屬 Layer 清楚。
* [ ] 沒有為單一錯誤文字建立不必要 Class。
* [ ] 預期錯誤與未預期錯誤已區分。
* [ ] Public Exception 相容性已評估。
* [ ] Metadata 使用結構化欄位。
* [ ] 原始例外透過 Chaining 保留。

### Messages

* [ ] 訊息指出問題。
* [ ] 訊息指出相關位置。
* [ ] 訊息指出具體原因。
* [ ] 適當時提供修正方式。
* [ ] 沒有模糊的「Operation failed」。
* [ ] 沒有暴露 Secret。
* [ ] 一般模式沒有不必要 Traceback。
* [ ] 錯誤文字沒有被當作控制流程。

### CLI

* [ ] 錯誤寫入 `stderr`。
* [ ] 正常輸出保留在 `stdout`。
* [ ] Exit Code 合理且穩定。
* [ ] `KeyboardInterrupt` 已處理。
* [ ] 未預期錯誤回傳 `1`。
* [ ] CLI 沒有重新實作底層驗證。
* [ ] 底層元件沒有呼叫 `sys.exit()`。

### Logging

* [ ] 使用標準 `logging`。
* [ ] Library 沒有呼叫 `basicConfig()`。
* [ ] 沒有重複記錄相同錯誤。
* [ ] Log Level 正確。
* [ ] Traceback 只在適當位置記錄。
* [ ] Log 沒有敏感資料。
* [ ] 本機路徑揭露已評估。

### Recovery

* [ ] 部分失敗行為已定義。
* [ ] 已建立檔案有回報。
* [ ] 暫存檔會被清理。
* [ ] 是否可重試已說明。
* [ ] 覆寫行為明確。
* [ ] 錯誤不會留下無法判斷的狀態。

### Tests

* [ ] Exception Hierarchy 有測試。
* [ ] 觸發條件有測試。
* [ ] Exception Chaining 有測試。
* [ ] Message 關鍵內容有測試。
* [ ] Exit Code 有測試。
* [ ] `stderr` 有測試。
* [ ] 未預期錯誤有測試。
* [ ] Cleanup 有測試。
* [ ] Sensitive Data 有測試。
* [ ] Integration Matrix 有測試。

### Documentation and Automation

* [ ] Errors Reference 已更新。
* [ ] Error Handling Architecture 已更新。
* [ ] CLI Reference 已同步。
* [ ] SDK Architecture 已同步（如適用）。
* [ ] Changelog 已更新。
* [ ] 必要時已新增 ADR。
* [ ] `git diff --check` 通過。
* [ ] `pre-commit run --all-files` 通過。
* [ ] `python -m pytest` 通過。

---

## 74. 目前限制

目前 OPL 錯誤處理可能仍有以下限制：

* Exception Hierarchy 尚未完整
* 部分錯誤可能只使用 `ConfigurationError`
* Registry 專屬錯誤可能尚未建立
* Generator 專屬錯誤可能尚未建立
* Template 專屬錯誤可能尚未建立
* Filesystem 專屬錯誤可能尚未建立
* CLI Exit Code 尚未分類
* 錯誤 Formatter 尚未集中
* Debug 模式尚未實作
* Error Code 尚未實作
* Structured Metadata 尚未普遍加入
* Partial Failure 尚未完整定義
* Transactional Generation 尚未完成
* SDK Error Contract 尚未穩定

以上項目若未出現在程式碼與測試中，應視為規劃，而不是現有功能。

---

## 75. Related Documents

* [Documentation Hub](../README.md)
* [Architecture Overview](../architecture/overview.md)
* [Error Handling Architecture](../architecture/error-handling.md)
* [Configuration Framework](../architecture/configuration-framework.md)
* [Generator Framework](../architecture/generator-framework.md)
* [Template Framework](../architecture/template-framework.md)
* [Generator Registry](../architecture/registry.md)
* [SDK Architecture](../architecture/sdk.md)
* [CLI Reference](cli.md)
* [Configuration Reference](configuration.md)
* [Template Reference](template.md)
* [Development Workflow](../development/development-workflow.md)
* [Code Review Checklist](../development/code-review-checklist.md)

---

> **錯誤訊息應讓使用者知道發生什麼事與如何修正；Exception 則應讓程式知道問題屬於哪一類。**
