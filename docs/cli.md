# OpenProjectLab CLI

## 1. 目的

OPL CLI 將 `BootstrapGenerator`、`CourseGenerator` 與 `WeekGenerator` 統一整合為可測試、可自動化的命令列介面。

```text
opl
├─ list
├─ bootstrap
├─ course
└─ week
```

## 2. 架構

```text
argparse
   │
   ├─ 全域設定與路徑解析
   ├─ 輸入型別驗證
   └─ 一致的錯誤與結果輸出
   │
   ▼
CLI Handler
   │
   ├─ BootstrapGenerator
   ├─ CourseGenerator
   └─ WeekGenerator
   │
   ▼
TemplateRenderer → FileSystem
```

CLI 不實作模板渲染或低階檔案操作，只負責參數解析、context 組裝與 Generator 協調。

## 3. 全域選項

全域選項必須放在子命令之前：

```powershell
opl --config config/default.yaml --template-root templates --output-root courses list
```

| 選項 | 說明 |
|---|---|
| `--config FILE` | YAML 設定檔 |
| `--template-root DIR` | 覆寫模板根目錄 |
| `--output-root DIR` | 覆寫課程輸出根目錄 |

路徑優先順序：

1. CLI 選項
2. `config.paths`
3. 專案預設值

支援的 `config.paths` 名稱：

```yaml
paths:
  template_root: templates
  course_root: courses
```

相容名稱：`templates`、`courses`、`output_root`。

## 4. 列出 Generator

```powershell
opl list
```

預期輸出包含：

```text
bootstrap
course
week
```

## 5. Bootstrap

```powershell
opl bootstrap modern-java `
  --name "Modern Java in Action" `
  --language zh-TW `
  --license "CC BY 4.0"
```

預設不覆寫既有檔案。明確允許覆寫：

```powershell
opl bootstrap modern-java --name "Modern Java" --force
```

預覽：

```powershell
opl bootstrap modern-java --name "Modern Java" --dry-run
```

## 6. Course

```powershell
opl course modern-java `
  --name "Modern Java in Action" `
  --weeks 16 `
  --textbook "Modern Java in Action, 2/e" `
  --language zh-TW `
  --force
```

輸出：

```text
courses/modern-java/README.md
```

## 7. Week

```powershell
opl week modern-java `
  --week 1 `
  --title "課程介紹與現代 Java 概覽" `
  --course-name "Modern Java in Action" `
  --textbook-chapter "Chapter 1" `
  --force
```

輸出：

```text
courses/modern-java/week-01/README.md
```

自訂週次目錄：

```powershell
opl week modern-java `
  --week 1 `
  --title "Introduction" `
  --directory-pattern "lesson-{week:03d}" `
  --force
```

## 8. dry-run

三個寫入型子命令都支援：

```text
--dry-run
```

它會完整執行：

- CLI 參數驗證
- 設定與路徑解析
- Generator 驗證
- 模板載入與渲染
- 輸出路徑計算

但不建立或修改檔案。

## 9. 覆寫策略

基於安全預設，CLI 只有在提供 `--force` 時才傳入：

```python
overwrite = True
```

未提供 `--force` 時，既有檔案會被保留，CLI 回傳狀態碼 `2`。

## 10. 結束狀態碼

| 狀態碼 | 意義 |
|---:|---|
| `0` | 成功 |
| `2` | 參數、設定、模板、Generator 或檔案系統錯誤 |

錯誤統一寫入 stderr：

```text
錯誤：<詳細訊息>
```

## 11. 測試

CLI 整合測試：

```powershell
python -m pytest tests/integration/test_cli_integration.py -v --no-cov
```

CLI coverage：

```powershell
python -m pytest tests/integration/test_cli_integration.py -v `
  -o addopts="" `
  --cov=generator.cli.main `
  --cov-branch `
  --cov-report=term-missing `
  --cov-fail-under=90
```

完整專案：

```powershell
python -m pytest -v
```

## 12. Code Review Checklist

### 架構

- [ ] CLI 僅負責解析、協調與輸出。
- [ ] CLI 不直接使用 Jinja2。
- [ ] CLI 不直接寫入教材檔案。
- [ ] 每個子命令呼叫對應 Generator。
- [ ] `list` 與 Registry 公開名稱一致。

### 參數與路徑

- [ ] 全域選項位於子命令之前。
- [ ] CLI 路徑優先於設定檔。
- [ ] 相對路徑以 `PROJECT_ROOT` 為基準。
- [ ] `week` 與 `weeks` 必須大於 0。
- [ ] 必要參數由 argparse 驗證。

### 安全與錯誤

- [ ] 預設不覆寫既有檔案。
- [ ] 只有 `--force` 允許覆寫。
- [ ] `--dry-run` 零副作用。
- [ ] 錯誤輸出到 stderr。
- [ ] 失敗回傳非零狀態碼。

### 測試與文件

- [ ] 測試 `list`。
- [ ] 測試三個 Generator 子命令。
- [ ] 測試 dry-run。
- [ ] 測試禁止覆寫。
- [ ] 測試無效參數與 slug。
- [ ] 文件範例可直接於 PowerShell 執行。
- [ ] 完整測試與 coverage 通過。


## 舊版相容介面

正式介面為：

```powershell
opl list
```

為避免既有腳本與測試中斷，CLI 仍接受：

```powershell
opl --list
```

`--list` 是隱藏的相容別名，不會顯示在一般 help 中，也不可與子命令同時使用。新程式碼應使用 `opl list`。
