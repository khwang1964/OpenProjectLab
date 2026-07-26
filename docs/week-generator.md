# Week Generator

## 1. 目的

`WeekGenerator` 負責建立單一週次的教材入口與目錄。預設會在課程目錄下產生：

```text
week-01/README.md
week-02/README.md
...
```

本功能延續 OpenProjectLab 的 Design First、Documentation First 與 Automation First 原則。

---

## 2. 架構

```text
CLI / Registry
      │
      ▼
WeekGenerator
  ├─ 驗證 week
  ├─ 格式化週次目錄
  ├─ 合併 context
  └─ 決定輸出位置
      │
      ▼
TemplateRenderer
      │
      ▼
FileSystem
```

責任分工：

- `WeekGenerator`：週次規則、context 與輸出路徑。
- `TemplateRenderer`：模板安全與 Jinja2 渲染。
- `FileSystem`：原子寫入、overwrite 與 dry-run。

---

## 3. 檔案位置

```text
generator/generators/week_generator.py
tests/generators/test_week_generator.py
templates/week/README.md.j2
docs/week-generator.md
```

---

## 4. 基本使用

```python
from pathlib import Path

from generator.generators.week_generator import WeekGenerator


generator = WeekGenerator(template_root=Path("templates"))

result = generator.generate(
    output_root=Path("courses/modern-java"),
    context={
        "week": 1,
        "title": "課程介紹與現代 Java 概覽",
        "course_name": "Modern Java in Action",
        "language": "zh-TW",
    },
)
```

預期輸出：

```text
courses/modern-java/week-01/README.md
```

---

## 5. 必要 Context

```python
{
    "week": 1,
    "title": "課程介紹與現代 Java 概覽",
    "course_name": "Modern Java in Action",
    "language": "zh-TW",
}
```

其中 `week`：

- 必須是 `int`。
- 不可為 `bool`。
- 必須大於 0。

Generator 會自動加入：

```python
{
    "week_padded": "01",
}
```

---

## 6. 選用 Context

```python
{
    "textbook_chapter": "Chapter 1",
    "learning_objectives": [
        "說明 Java 生態系的演進",
        "建立本課程開發環境",
    ],
    "readings": [
        "Modern Java in Action, Chapter 1",
    ],
    "agenda": [
        "課程介紹",
        "環境檢查",
        "第一個 Demo",
    ],
    "completion_criteria": [
        "完成環境設定",
        "成功執行 Demo",
    ],
}
```

---

## 7. Dry-run

```python
generator.generate(
    Path("courses/modern-java"),
    context,
    dry_run=True,
)
```

dry-run：

- 驗證週次。
- 驗證目錄格式。
- 驗證模板與必要變數。
- 回傳預計輸出路徑。
- 不建立目錄。
- 不寫入檔案。

---

## 8. 自訂週次目錄

預設格式：

```python
directory_pattern = "week-{week:02d}"
```

例如：

```python
generator.generate(
    output_root,
    context,
    directory_pattern="lesson-{week:03d}",
)
```

第 1 週將輸出：

```text
lesson-001/README.md
```

安全限制：

- 不可為空。
- 不可為絕對路徑。
- 不可包含 `..`。
- 必須是有效的 Python format string。

---

## 9. 自訂輸出名稱

```python
generator.generate(
    output_root,
    context,
    output_name="docs/week.md",
)
```

輸出：

```text
week-01/docs/week.md
```

---

## 10. Context 優先順序

可用 mapping：

```python
generator.generate(output_root, context)
```

也可直接使用關鍵字：

```python
generator.generate(
    output_root,
    week=2,
    title="Lambda",
    course_name="Modern Java",
    language="zh-TW",
)
```

若兩者包含相同欄位，關鍵字值優先。

---

## 11. 相容介面

`run()` 是 `generate()` 的相容別名：

```python
generator.run(output_root, context, dry_run=True)
```

Registry 中繼資料：

```python
WeekGenerator.name
WeekGenerator.description
```

---

## 12. 測試

只執行 WeekGenerator：

```powershell
python -m pytest tests/generators/test_week_generator.py -v --no-cov
```

單獨測量 coverage：

```powershell
python -m pytest tests/generators/test_week_generator.py -v `
  -o addopts="" `
  --cov=generator.generators.week_generator `
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

- 正常產生每週 README。
- 兩位數週次格式。
- UTF-8 與繁體中文。
- 自動建立輸出目錄。
- dry-run 零副作用。
- dry-run 仍驗證 context。
- 拒絕零與負數週次。
- 拒絕非整數與布林週次。
- 拒絕缺少週次。
- 拒絕缺少模板變數。
- 拒絕不存在模板。
- 禁止覆寫。
- 建構式與方法路徑。
- mapping 與關鍵字 context。
- 自訂週次目錄。
- 自訂輸出名稱。
- 無效目錄格式。
- `run()` 相容介面。

---

## 14. Code Review Checklist

### 架構

- [ ] Generator 不直接寫入檔案。
- [ ] Generator 不直接建立 Jinja2 Environment。
- [ ] 模板渲染經過 `TemplateRenderer`。
- [ ] 寫入行為經過 `FileSystem`。

### 週次規則

- [ ] `week` 必須是整數。
- [ ] `week` 不接受布林值。
- [ ] `week` 必須大於 0。
- [ ] 預設目錄為兩位數格式。
- [ ] `week_padded` 正確加入 context。

### 路徑安全

- [ ] 週次目錄不是絕對路徑。
- [ ] 週次目錄不包含 `..`。
- [ ] 空目錄名稱會被拒絕。
- [ ] 無效 format string 會明確失敗。

### dry-run 與覆寫

- [ ] dry-run 不建立目錄。
- [ ] dry-run 不寫入檔案。
- [ ] dry-run 仍執行模板驗證。
- [ ] `overwrite=False` 保留既有內容。

### 測試與文件

- [ ] 單元測試使用 `tmp_path`。
- [ ] WeekGenerator 測試全部通過。
- [ ] 完整測試全部通過。
- [ ] coverage 達到專案要求。
- [ ] 文件與公開 API 一致。
