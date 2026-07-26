# OpenProjectLab Template System

## 1. 目的

Template System 將教材結構與 Python 產生器邏輯分離，使課程內容可以安全覆寫、驗證、版本化與重複使用。

## 2. 架構

```text
CLI
  ↓
Generator
  ↓
TemplateRenderer
  ├─ templates/manifest.yaml
  ├─ bootstrap/
  ├─ course/
  ├─ week/
  ├─ lab/
  ├─ assignment/
  ├─ quiz/
  ├─ slides/
  ├─ website/
  └─ shared/
```

Generator 只負責：

- 建立 context
- 選擇模板
- 計算輸出路徑
- 呼叫 TemplateRenderer
- 寫入檔案及 Manifest

模板只負責輸出內容與格式。

## 3. Template Root

預設 Template Root：

```text
F:\OpenProjectLab\templates
```

可由 CLI 覆寫：

```powershell
opl --template-root .\custom-templates bootstrap demo `
  --name "Demo"
```

## 4. 命名規範

```text
<generator>/<artifact>.j2
```

Bootstrap 多檔案模板使用：

```text
bootstrap/project/<filename>.j2
```

規則：

- 全部使用 UTF-8
- 路徑使用 `/`
- 不可包含 `..`
- 不可使用絕對路徑
- 檔名應清楚對應產出物

## 5. Context

模板採用 StrictUndefined。必要欄位不存在時，渲染必須失敗，不可靜默產生不完整教材。

常用 context：

| 變數 | 用途 |
|---|---|
| `project_slug` | 專案目錄名稱 |
| `project_name` | 專案顯示名稱 |
| `course_name` | 課程名稱 |
| `week` | 週次整數 |
| `week_padded` | 兩位數週次 |
| `title` | 教材標題 |
| `language` | 語言 |
| `license` | 授權方式 |
| `weeks` | 總週數 |
| `textbook` | 教科書 |

## 6. Manifest

`templates/manifest.yaml` 記錄：

- Template Pack schema
- 套件版本
- 模板路徑
- 對應 Generator
- 必要 context 變數

每次新增、重新命名或移除模板，都必須同步更新 Manifest。

## 7. Override

客製模板應保留相同相對路徑。例如要覆寫 Bootstrap README：

```text
custom-templates/
└─ bootstrap/
   └─ project/
      └─ README.md.j2
```

呼叫：

```powershell
opl --template-root .\custom-templates bootstrap demo `
  --name "Demo"
```

若只覆寫少數模板，未來可由多層 Search Path 功能提供 fallback；目前版本要求指定的 Template Root 內包含 Generator 所需全部模板。

## 8. 測試

```powershell
python -m pytest tests/template/test_template_pack.py -v --no-cov
```

測試涵蓋：

- Manifest schema
- 路徑安全
- 模板存在
- Jinja 語法編譯
- 參考 context 渲染
- BootstrapGenerator 契約

## 9. Code Review Checklist

- [ ] 新模板已加入 `manifest.yaml`
- [ ] 必要 context 已明確記錄
- [ ] StrictUndefined 渲染通過
- [ ] UTF-8 繁體中文正常
- [ ] 路徑為安全相對路徑
- [ ] Generator 契約未被破壞
- [ ] 測試已新增或更新
- [ ] 文件已同步更新

## 10. Template Test Architecture

```text
tests/template/
├─ conftest.py
├─ test_template_manifest.py
├─ test_template_compile.py
├─ test_template_render.py
├─ test_template_paths.py
├─ test_template_contract.py
└─ test_template_pack.py
```

各測試責任分離，避免單一測試檔同時承擔 schema、編譯、渲染與契約檢查。

## 11. CI

`.github/workflows/template-tests.yml` 在模板、測試或文件變更時，自動執行：

```bash
python -m pytest tests/template -v --no-cov
```
