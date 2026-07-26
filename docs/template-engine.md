# Template Engine

## 1. 目的

OpenProjectLab Template Engine 負責將課程、週次、README、Lab、作業與網站模板轉換成實際教材檔案。

設計原則：

1. **Design First**：先定義安全、明確、可測試的渲染介面。
2. **Documentation First**：公開介面、例外與 dry-run 行為均有文件。
3. **Automation First**：Generator 統一透過 Template Engine 批次產生教材。

## 2. 架構

```text
BootstrapGenerator / CourseGenerator / WeekGenerator
                         │
                         ▼
                 TemplateRenderer
                 ├─ 路徑驗證
                 ├─ Jinja2 載入
                 ├─ StrictUndefined
                 ├─ context 複製
                 └─ 模板渲染
                         │
                         ▼
                    FileSystem
                 ├─ UTF-8
                 ├─ 原子寫入
                 ├─ overwrite
                 └─ dry-run
```

責任分離：

- `TemplateRenderer`：模板路徑、載入、變數與渲染。
- `FileSystem`：目錄、檔案寫入、覆寫策略與 dry-run。
- Generator：組合 context、選擇模板與決定輸出位置。

## 3. 相依套件

```powershell
python -m pip install Jinja2
```

建議加入 `pyproject.toml`：

```toml
dependencies = [
    "PyYAML>=6.0",
    "Jinja2>=3.1",
]
```

## 4. 基本使用

模板：`templates/course/README.md.j2`

```jinja2
# {{ course_name }}

語言：{{ language }}
週數：{{ weeks }}
```

渲染成字串：

```python
from pathlib import Path
from generator.core.template import TemplateRenderer

renderer = TemplateRenderer(Path("templates"))
content = renderer.render(
    "course/README.md.j2",
    {
        "course_name": "Modern Java in Action",
        "language": "zh-TW",
        "weeks": 16,
    },
)
```

渲染至檔案：

```python
renderer.render_to_file(
    "course/README.md.j2",
    Path("courses/modern-java/README.md"),
    context,
)
```

## 5. Dry-run

```python
renderer.render_to_file(
    "course/README.md.j2",
    Path("courses/modern-java/README.md"),
    context,
    dry_run=True,
)
```

`dry_run=True` 時仍會驗證模板、語法與必要變數，但不建立目錄、不寫入檔案。

## 6. 嚴格變數

Template Engine 使用 Jinja2 `StrictUndefined`。缺少必要變數時拋出 `TemplateRenderError`，避免產生不完整教材。

## 7. 路徑安全

以下路徑會被拒絕：

```python
renderer.render("../secret.txt", {})
renderer.render("course/../../secret.txt", {})
renderer.render(Path("C:/secret.txt"), {})
```

規則：

- 模板名稱必須是相對路徑。
- 不得包含 `..`。
- 正規化後不得離開 `template_root`。
- Jinja2 loader 不追蹤符號連結。

## 8. 例外

- `TemplateEngineError`：Template Engine 例外基底。
- `TemplatePathError`：根目錄或模板路徑不合法。
- `TemplateRenderError`：模板不存在、缺少變數或語法錯誤。
- `FileSystemError`：輸出寫入失敗。

## 9. 相容介面

```python
from generator.core.template import TemplateEngine, render_template
```

`TemplateEngine` 是 `TemplateRenderer` 的相容別名；`render_template()` 提供單次渲染函式介面。

## 10. 測試

```powershell
python -m pytest tests/core/test_template.py -v --no-cov
```

只計算 Template Engine 覆蓋率：

```powershell
python -m pytest tests/core/test_template.py `
  --cov=generator.core.template `
  --cov-report=term-missing `
  --cov-fail-under=90
```

完整測試：

```powershell
python -m pytest -v
```

## 11. Code Review Checklist

### 架構

- [ ] Generator 僅透過 `TemplateRenderer` 使用模板。
- [ ] Template Engine 僅透過 `FileSystem` 寫入輸出。
- [ ] 模板渲染與檔案操作責任分離。

### 安全性

- [ ] 拒絕絕對模板路徑。
- [ ] 拒絕含 `..` 的模板路徑。
- [ ] 使用 `StrictUndefined`。
- [ ] 不追蹤模板目錄符號連結。

### dry-run

- [ ] 不建立目錄。
- [ ] 不寫入檔案。
- [ ] 仍驗證模板、語法與必要變數。

### 品質

- [ ] 公開 API 有型別標註與 docstring。
- [ ] 預設 UTF-8。
- [ ] 測試使用 pytest `tmp_path`。
- [ ] 完整測試全部通過。
- [ ] 專案 coverage 不低於門檻。
