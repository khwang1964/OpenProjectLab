# Course Generator

## 1. 目的

`CourseGenerator` 負責建立課程層級的基本教材入口，目前會使用 Jinja2 模板產生課程 `README.md`。

本功能遵循 OpenProjectLab 的三項原則：

1. **Design First**：Generator 只協調資料、模板與輸出路徑。
2. **Documentation First**：公開介面、錯誤、dry-run 與測試方式均有文件。
3. **Automation First**：相同 Generator 可由 CLI、測試或其他自動化流程重複使用。

---

## 2. 架構

```text
CLI / Registry
      │
      ▼
CourseGenerator
  ├─ 合併 context
  ├─ 決定模板
  └─ 決定輸出路徑
      │
      ▼
TemplateRenderer
  ├─ 路徑安全
  ├─ StrictUndefined
  └─ Jinja2 渲染
      │
      ▼
FileSystem
  ├─ UTF-8
  ├─ overwrite
  ├─ 原子寫入
  └─ dry-run
```

`CourseGenerator` 不直接呼叫 `Path.write_text()`，也不自行建立 Jinja2 `Environment`。

---

## 3. 檔案位置

```text
generator/generators/course_generator.py
templates/course/README.md.j2
tests/generators/test_course_generator.py
docs/course-generator.md
```

預設輸出：

```text
courses/<course-slug>/README.md
```

---

## 4. 基本使用

```python
from pathlib import Path

from generator.generators.course_generator import CourseGenerator


generator = CourseGenerator(template_root=Path("templates"))

result = generator.generate(
    output_root=Path("courses/modern-java"),
    context={
        "course_name": "Modern Java in Action",
        "language": "zh-TW",
        "weeks": 16,
        "textbook": "Modern Java in Action, 2/e",
    },
)

print(result)
```

---

## 5. 建構式路徑

可在建構式同時提供模板與輸出根目錄：

```python
generator = CourseGenerator(
    template_root=Path("templates"),
    output_root=Path("courses/modern-java"),
)

generator.generate(context=context)
```

也可在 `generate()` 覆寫：

```python
generator.generate(
    output_root=Path("courses/another-course"),
    template_root=Path("custom-templates"),
    context=context,
)
```

呼叫時提供的路徑優先於建構式設定。

---

## 6. Context

必要欄位：

```python
{
    "course_name": "Modern Java in Action",
    "language": "zh-TW",
    "weeks": 16,
}
```

選用欄位：

```python
{
    "textbook": "Modern Java in Action, 2/e",
    "instructor": "Instructor Name",
    "description": "課程說明",
    "learning_objectives": [
        "理解現代 Java 語言特性",
        "熟悉函數式程式設計",
    ],
    "license_name": "CC BY 4.0",
}
```

也支援關鍵字形式：

```python
generator.generate(
    Path("courses/demo"),
    course_name="Demo Course",
    language="zh-TW",
    weeks=8,
)
```

若 mapping 與關鍵字包含相同欄位，關鍵字值優先。

---

## 7. Dry-run

```python
generator.generate(
    Path("courses/modern-java"),
    context,
    dry_run=True,
)
```

dry-run 會：

- 驗證模板根目錄。
- 驗證模板是否存在。
- 執行 Jinja2 渲染。
- 檢查必要變數。
- 回傳預計輸出的路徑。
- 不建立目錄。
- 不寫入檔案。

---

## 8. Overwrite

預設允許覆寫：

```python
generator.generate(output_root, context, overwrite=True)
```

禁止覆寫：

```python
generator.generate(output_root, context, overwrite=False)
```

若 `README.md` 已存在，`FileSystemError` 會被拋出，既有檔案不會被修改。

---

## 9. 自訂模板與輸出名稱

```python
generator.generate(
    output_root,
    context,
    template_name="course/custom.md.j2",
    output_name="docs/course.md",
)
```

`template_name` 相對於 `template_root`。

`output_name` 相對於 `output_root`，可包含子目錄。

---

## 10. 相容介面

`run()` 是 `generate()` 的相容別名：

```python
generator.run(output_root, context, dry_run=True)
```

類別同時提供 Registry 可使用的中繼資料：

```python
CourseGenerator.name
CourseGenerator.description
```

---

## 11. 測試

只執行 CourseGenerator 測試：

```powershell
python -m pytest tests/generators/test_course_generator.py -v --no-cov
```

單獨測量模組 coverage：

```powershell
python -m pytest tests/generators/test_course_generator.py -v `
  -o addopts="" `
  --cov=generator.generators.course_generator `
  --cov-branch `
  --cov-report=term-missing `
  --cov-fail-under=90
```

完整專案測試：

```powershell
python -m pytest -v
```

---

## 12. Code Review Checklist

### 架構

- [ ] Generator 不直接寫入檔案。
- [ ] Generator 不直接建立 Jinja2 Environment。
- [ ] 模板渲染統一經過 `TemplateRenderer`。
- [ ] 輸出操作統一經過 `FileSystem`。

### 行為

- [ ] 正確產生 `README.md`。
- [ ] 支援 UTF-8 與繁體中文。
- [ ] 支援建構式與方法層級路徑。
- [ ] 支援 mapping 與關鍵字 context。
- [ ] 關鍵字 context 覆寫 mapping。
- [ ] 支援自訂模板與輸出名稱。
- [ ] `run()` 與 `generate()` 行為一致。

### dry-run 與安全性

- [ ] dry-run 不建立目錄或檔案。
- [ ] dry-run 仍檢查模板及必要變數。
- [ ] `overwrite=False` 保留既有檔案。
- [ ] 模板路徑安全由 `TemplateRenderer` 統一處理。

### 測試與文件

- [ ] 單元測試使用 `tmp_path`。
- [ ] Generator 測試全部通過。
- [ ] 完整專案測試全部通過。
- [ ] coverage 不低於專案門檻。
- [ ] 文件與實際公開介面一致。
