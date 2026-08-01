# Bootstrap Generator

## 1. 目的

`BootstrapGenerator` 用來建立完整的 OpenProjectLab 課程專案骨架。

它不只產生單一檔案，而是依照 manifest 一次建立：

```text
README.md
LICENSE
CONTRIBUTING.md
.gitignore
course.yaml
docs/
assets/
templates/
weeks/
```

---

## 2. 設計原則

### Design First

Generator 僅負責：

- 驗證 `project_slug`
- 組合 context
- 根據 manifest 決定輸出
- 協調 TemplateRenderer 與 FileSystem
- 回傳結構化結果

### Documentation First

公開 API、context、dry-run、overwrite、錯誤與測試方式均記錄於本文件。

### Automation First

相同 Generator 可由：

- CLI
- Registry
- 單元測試
- CI/CD
- 其他 Python 模組

重複使用。

---

## 3. 架構

```text
CLI / Registry
      │
      ▼
BootstrapGenerator
  ├─ project_slug validator
  ├─ TEMPLATE_MANIFEST
  ├─ DIRECTORY_MANIFEST
  └─ GenerationResult
      │
      ├──────────────┐
      ▼              ▼
TemplateRenderer   FileSystem
      │              │
      └──────┬───────┘
             ▼
完整課程專案骨架
```

---

## 4. Manifest

### TEMPLATE_MANIFEST

```python
{
    "README.md": "bootstrap/project/README.md.j2",
    "LICENSE": "bootstrap/project/LICENSE.j2",
    "CONTRIBUTING.md": "bootstrap/project/CONTRIBUTING.md.j2",
    ".gitignore": "bootstrap/project/gitignore.j2",
    "course.yaml": "bootstrap/project/course.yaml.j2",
}
```

### DIRECTORY_MANIFEST

```python
(
    "docs",
    "assets",
    "templates",
    "weeks",
)
```

新增模板或目錄時，應優先修改 manifest，而不是在流程中加入散落的硬編碼。

---

## 5. 基本使用

```python
from pathlib import Path

from generator.generators.bootstrap_generator import BootstrapGenerator


generator = BootstrapGenerator(
    template_root=Path("templates"),
)

output_root = Path("courses")
project_slug = "modern-java"
project_root = output_root / project_slug

result = generator.generate(
    output_root=output_root,
    context={
        "project_name": "Modern Java in Action",
        "project_slug": project_slug,
        "language": "zh-TW",
        "license_name": "CC BY 4.0",
    },
)

print(project_root)
for path in result.affected_paths:
    print(path)
```

預期輸出：

```text
courses/modern-java/
```

---

## 6. GenerationResult 與相容層

```python
@dataclass(frozen=True, slots=True)
class GenerationResult:
    writes: tuple[WriteResult, ...]
    dry_run: bool

    @property
    def affected_paths(self) -> tuple[Path, ...]: ...
```

`GenerationResult` 是所有核心 Generator 的正式共用回傳契約。
`affected_paths` 依 manifest／寫入順序提供所有受影響檔案的有序檢視，供 CLI、測試、自動化、日誌與稽核使用。

Bootstrap 特有資訊不加入共用結果模型：

- `project_root` 應由 request、`output_root` 與 `project_slug` 保存或推導。
- 舊 `generated_files` 的使用端應改讀 `affected_paths`。
- `created_directories` 是 Bootstrap 實作細節，不應新增為 `GenerationResult` 的共用欄位。

### 暫時相容層

`BootstrapResult`、`CourseResult` 與 `WeekResult` 目前僅作為分階段遷移的暫時相容層，預計在所有使用端完成遷移後移除。新程式碼不得再匯入或依賴這些型別。

遷移對照：

| 舊用法 | 新用法 |
|---|---|
| `result.generated_files` | `result.affected_paths` |
| `result.output_path` | 依需求選取 `affected_paths`，不可假設共用單一路徑 |
| `result.project_root` | 從 request 或 `output_root / project_slug` 推導 |
| `result.created_directories` | 不屬於共用結果契約 |

---

## 7. Context

必要欄位：

```python
{
    "project_name": "Modern Java in Action",
    "project_slug": "modern-java",
    "language": "zh-TW",
    "license_name": "CC BY 4.0",
}
```

選用欄位：

```python
{
    "copyright_year": "2026",
    "copyright_holder": "OpenProjectLab Contributors",
}
```

也可使用關鍵字：

```python
generator.generate(
    Path("courses"),
    project_name="Demo Course",
    project_slug="demo-course",
    language="zh-TW",
    license_name="CC BY 4.0",
)
```

關鍵字 context 會覆寫 mapping 中的同名值。

---

## 8. project_slug 規則

驗證規則：

```regex
^[a-z0-9]+(?:-[a-z0-9]+)*$
```

允許：

```text
modern-java
data-structures
opl-demo-2026
course1
```

拒絕：

```text
Modern Java
../modern-java
/course
modern_java
modern/java
modern--java
```

這項規則同時防止：

- 絕對路徑
- 路徑跳脫
- 空白
- 大寫字母
- 底線
- 重複連字號

---

## 9. Dry-run

```python
result = generator.generate(
    Path("courses"),
    context,
    dry_run=True,
)
```

dry-run 會：

- 驗證 template_root。
- 驗證 output_root。
- 驗證 project_slug。
- 載入所有模板。
- 渲染所有模板。
- 驗證所有必要變數。
- 建立完整結果清單。
- 不建立任何目錄。
- 不寫入任何檔案。

BootstrapGenerator 會先完成所有模板渲染，再開始檔案系統操作，避免模板錯誤造成半完成專案。

---

## 10. Overwrite

預設：

```python
overwrite = True
```

禁止覆寫：

```python
generator.generate(
    Path("courses"),
    context,
    overwrite=False,
)
```

若目標檔案已存在，`FileSystemError` 會被拋出。

注意：目前檔案是依 manifest 順序寫入。未來若需要完整交易式 rollback，可新增 `GenerationPlan` 與 staging directory。

---

## 11. 錯誤類型

可能拋出：

```text
ValueError
TemplatePathError
TemplateRenderError
FileSystemError
```

典型情況：

- 未提供 template_root
- 未提供 output_root
- project_slug 不合法
- 模板不存在
- 必要變數缺失
- 禁止覆寫既有檔案
- 檔案系統操作失敗

---

## 12. 測試

只執行 BootstrapGenerator：

```powershell
python -m pytest tests/generators/test_bootstrap_generator.py -v --no-cov
```

單獨 coverage：

```powershell
python -m pytest tests/generators/test_bootstrap_generator.py -v `
  -o addopts="" `
  --cov=generator.generators.bootstrap_generator `
  --cov-branch `
  --cov-report=term-missing `
  --cov-fail-under=90
```

完整專案：

```powershell
python -m pytest -v
```

---

## 13. 測試範圍

- 建立完整專案結構。
- 產生全部 manifest 檔案。
- 建立全部 manifest 目錄。
- 支援 UTF-8 與繁體中文。
- dry-run 完全零副作用。
- dry-run 仍驗證所有模板。
- 缺少 context 時失敗。
- 拒絕不合法 slug。
- 接受合法 slug。
- 明確 project_slug 覆寫 context。
- 模板不存在時失敗。
- overwrite=False 保留既有內容。
- 回傳 `GenerationResult`。
- `affected_paths` 保持 manifest 定義的輸出順序。
- 使用端不依賴 `BootstrapResult`、`generated_files`、`created_directories` 或 `output_path`。
- 支援建構式 output_root。
- 支援 template_root 覆寫。
- 支援關鍵字 context。
- `run()` 相容介面。

---

## 14. Code Review Checklist

### 架構

- [ ] Generator 不直接建立 Jinja2 Environment。
- [ ] 所有模板經過 `TemplateRenderer`。
- [ ] 所有寫入經過 `FileSystem`。
- [ ] 多檔案輸出由 manifest 管理。
- [ ] 回傳 `GenerationResult`。
- [ ] 生成檔案由 `affected_paths` 提供有序檢視。
- [ ] `project_root` 從 request 或命令輸入保存／推導。
- [ ] 不把 Bootstrap 特有欄位加入共用結果模型。
- [ ] 新程式碼不依賴 Generator-specific Result 相容型別。

### 驗證與安全

- [ ] project_slug 使用固定 regex。
- [ ] 防止絕對路徑。
- [ ] 防止 `..` 跳脫。
- [ ] 防止空白與非法字元。
- [ ] 所有模板在寫入前先完成渲染驗證。

### dry-run 與覆寫

- [ ] dry-run 不建立目錄。
- [ ] dry-run 不建立檔案。
- [ ] dry-run 仍驗證所有模板。
- [ ] overwrite=False 不破壞既有檔案。

### 測試與文件

- [ ] 測試使用 `tmp_path`。
- [ ] 單元測試全部通過。
- [ ] 完整測試全部通過。
- [ ] coverage 達到專案門檻。
- [ ] 文件與公開 API 一致。
- [ ] CLI 輸出契約測試涵蓋實際路徑且不洩漏結果物件表示法。
