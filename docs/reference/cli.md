# OpenProjectLab CLI Reference

> Status: Active
> Audience: Users, contributors, maintainers
> Command: `opl`

本文件記錄 OpenProjectLab（OPL）目前公開的命令列介面。

CLI 是 OPL 的主要操作入口，負責：

* 解析命令與參數
* 載入設定檔
* 查詢 Generator Registry
* 執行指定 Generator
* 將結果轉換為使用者訊息與結束碼

CLI 不應包含 Generator 的主要業務邏輯。

---

## 1. 安裝與驗證

在專案根目錄建立並啟用虛擬環境後，執行：

```powershell
python -m pip install -e .
```

驗證 `opl` 命令是否可用：

```powershell
opl --help
```

若 PowerShell 無法辨識 `opl`，請先確認虛擬環境已啟用：

```powershell
.venv\Scripts\Activate.ps1
```

也可以檢查可執行檔位置：

```powershell
Get-Command opl
```

預期應指向：

```text
F:\OpenProjectLab\.venv\Scripts\opl.exe
```

實際路徑會依專案位置而不同。

---

## 2. 命令格式

一般格式：

```text
opl [global-options] <command> [command-options]
```

目前已確認的子命令：

```text
list
bootstrap
course
week
```

目前 CLI 採用子命令設計，因此列出 Generator 的正確方式是：

```powershell
opl list
```

而不是：

```powershell
opl --list
```

---

## 3. 全域說明

查看完整說明：

```powershell
opl --help
```

預期會顯示可用的子命令與全域選項。

目前已確認支援：

```text
--config FILE
```

此選項可指定非預設設定檔。

例如：

```powershell
opl --config .\config\default.yaml list
```

若未指定 `--config`，CLI 會使用專案定義的預設設定檔。

目前預設位置為：

```text
config/default.yaml
```

實際解析方式應以目前版本的 CLI 實作為準。

---

## 4. `opl list`

列出目前已註冊的 Generator。

### 語法

```powershell
opl list
```

### 預期輸出

目前預期包含：

```text
bootstrap
course
week
```

實際順序可能依 Registry 實作而定。

### 用途

此命令可用於：

* 驗證 CLI 安裝是否成功
* 確認 Registry 是否正確初始化
* 查看目前可使用的 Generator
* 協助自動化流程進行能力探索

### 設定檔範例

```powershell
opl --config .\config\default.yaml list
```

---

## 5. `opl bootstrap`

執行 Bootstrap Generator。

### 語法

```powershell
opl bootstrap
```

### 用途

Bootstrap Generator 用於建立 OPL 專案或基礎結構所需的初始內容。

其具體輸入、輸出與覆寫行為，應以目前 Generator 實作與相關設定為準。

### 建議執行前確認

* 設定檔存在
* 目標路徑正確
* 目標目錄內沒有需要保留但尚未備份的檔案
* 所需 Template 存在

### 設定檔範例

```powershell
opl --config .\config\default.yaml bootstrap
```

### 驗證方式

執行後可檢查：

```powershell
git status --short
```

或檢視目標目錄：

```powershell
Get-ChildItem -Recurse
```

---

## 6. `opl course`

執行 Course Generator。

### 語法

```powershell
opl course
```

### 用途

Course Generator 用於建立課程層級的目錄、設定或教材結構。

目前文件不假設其所有輸入選項。請以以下命令確認實際支援的參數：

```powershell
opl course --help
```

若目前版本尚未為子命令提供個別 `--help`，請參考：

```powershell
opl --help
```

以及對應設定檔。

### 設定檔範例

```powershell
opl --config .\config\default.yaml course
```

### 執行後建議檢查

* 課程目錄是否建立
* 必要文件是否產生
* Template 是否正確渲染
* UTF-8 內容是否正常
* 重複執行時是否有明確行為

---

## 7. `opl week`

執行 Week Generator。

### 語法

```powershell
opl week
```

### 用途

Week Generator 用於建立單週教材或課程週次結構。

具體產出可能包括：

* 單週目錄
* 講義
* 投影片來源
* Lab
* Demo
* 作業
* 小考
* Metadata

上述內容取決於目前 Template 與設定，並非所有版本都一定產生全部項目。

### 設定檔範例

```powershell
opl --config .\config\default.yaml week
```

### 執行後建議檢查

```powershell
git status --short
```

以及：

```powershell
Get-ChildItem courses -Recurse
```

請依實際設定中的輸出路徑調整檢查位置。

---

## 8. 設定檔載入

CLI 透過 `--config` 指定設定檔：

```powershell
opl --config <FILE> <command>
```

例如：

```powershell
opl --config .\config\default.yaml list
```

設定檔必須是有效的 YAML。

目前主要設定區段包括：

```yaml
project: {}
paths: {}
generator: {}
plugins: {}
```

各區段應為 Mapping。

完整欄位與路徑規則請參閱：

* [Configuration Reference](configuration.md)
* [Configuration Framework](../architecture/configuration-framework.md)

---

## 9. 路徑行為

使用設定檔時，應特別注意：

* 設定檔路徑可以是相對路徑或絕對路徑
* Template root 可能是相對路徑或絕對路徑
* 輸出目錄可能依目前工作目錄或設定檔位置解析
* Windows 使用反斜線，但文件與 Python 程式應優先使用 `pathlib.Path`
* 不應在程式碼中硬編碼 `F:\OpenProjectLab`

正式行為應由 Configuration Framework 定義，CLI 只負責接收參數。

---

## 10. 錯誤處理

CLI 應將內部錯誤轉換為清楚的使用者訊息。

常見錯誤類型包括：

### 找不到設定檔

```text
找不到設定檔：<path>
```

### YAML 格式錯誤

```text
YAML 格式錯誤：<path>
```

### 設定區段型別錯誤

例如某個區段不是 Mapping。

### 不存在的命令

Argparse 應顯示錯誤與使用說明。

### 找不到 Generator

Registry 應回報名稱無效或未註冊。

### Template 或輸出錯誤

應指出相關 Template 或目標路徑。

CLI 在正常使用者錯誤情境下，不應輸出不必要的完整 traceback。

---

## 11. Exit Code

CLI 應使用 Exit Code 表示執行結果。

建議語意：

| Exit Code | 意義                    |
| --------: | --------------------- |
|       `0` | 成功                    |
|     非 `0` | 設定、參數、Generator 或執行錯誤 |

目前各類錯誤是否具有固定的獨立 Exit Code，應以實作與測試為準。

在自動化流程中可使用：

```powershell
opl list

if ($LASTEXITCODE -ne 0) {
    Write-Error "OPL command failed."
    exit $LASTEXITCODE
}
```

---

## 12. PowerShell 使用範例

### 啟用虛擬環境

```powershell
cd F:\OpenProjectLab
.venv\Scripts\Activate.ps1
```

### 查看命令

```powershell
opl --help
```

### 列出 Generator

```powershell
opl list
```

### 使用指定設定檔

```powershell
opl --config .\config\default.yaml list
```

### 執行完整測試

```powershell
python -m pytest
```

### 執行 Coverage

```powershell
python -m pytest `
    --cov=generator `
    --cov-report=term-missing `
    --cov-report=xml
```

---

## 13. CLI 開發規範

新增或修改 CLI 行為時，應遵循以下規則。

### 13.1 CLI 僅負責協調

CLI 可以：

* 解析參數
* 載入設定
* 查詢 Registry
* 呼叫服務
* 顯示結果
* 設定 Exit Code

CLI 不應：

* 直接實作複雜 Generator 邏輯
* 直接渲染 Template
* 直接處理大量檔案操作
* 儲存隱藏全域狀態
* 將所有錯誤都捕捉為模糊訊息

### 13.2 命令命名

命令名稱應：

* 使用小寫
* 使用清楚的動詞或名詞
* 避免縮寫
* 與 Registry 名稱一致
* 避免和全域選項衝突

### 13.3 參數設計

參數應：

* 具有清楚名稱
* 提供有意義的 Help
* 不依賴模糊的隱藏預設值
* 使用一致的路徑與布林選項風格
* 在必要時提供驗證

### 13.4 輸出設計

CLI 輸出應：

* 適合人類閱讀
* 保持穩定與可預期
* 在錯誤時提供可操作資訊
* 避免不必要的除錯內容
* 未來若支援機器可讀格式，應使用明確選項，例如 `--json`

---

## 14. 新增 CLI 命令流程

新增命令時應同步完成：

1. 定義需求與責任
2. 更新 Architecture
3. 設計命令名稱與參數
4. 更新 CLI Reference
5. 實作 CLI Parser
6. 實作或整合對應服務
7. 新增 CLI 測試
8. 新增錯誤流程測試
9. 更新 README
10. 更新 Changelog

若命令引入長期公開契約，應評估是否需要 ADR。

---

## 15. CLI 測試

CLI 變更至少應測試：

* `--help`
* 有效子命令
* 無效子命令
* 預設設定檔
* 指定設定檔
* 找不到設定檔
* 無效 YAML
* Generator 執行成功
* Generator 執行失敗
* Exit Code
* 輸出內容

執行相關測試：

```powershell
python -m pytest tests\test_cli.py -v
```

如果 CLI 測試位於整合測試目錄：

```powershell
python -m pytest tests\integration\test_cli_integration.py -v
```

完整測試：

```powershell
python -m pytest
```

---

## 16. 目前支援狀態

| 命令 | 狀態 | 說明 |
| --------------- | ------ | ---------------------- |
| `opl list` | Active | 列出已註冊 Generator |
| `opl bootstrap` | Active | 執行 Bootstrap Generator |
| `opl course` | Active | 執行 Course Generator |
| `opl week` | Active | 執行 Week Generator |

以下命令屬於未來規劃，不應視為目前可用功能：

```text
opl doctor
opl plugin
opl template
opl upgrade
```

如果某項命令已在實際程式中完成，應先以 `opl --help`、測試與程式碼確認，再更新本文件。

---

## 17. 驗證目前 CLI

可使用以下命令建立 CLI 行為快照：

```powershell
opl --help
opl list
opl bootstrap --help
opl course --help
opl week --help
```

若某個子命令不支援個別 Help，請記錄實際輸出，不要在文件中假設其行為。

也可以直接呼叫 Python Entry Point：

```powershell
python -m generator.cli.main --help
```

此命令是否可用取決於 `generator.cli.main` 是否包含模組執行入口。

正式使用方式仍以：

```powershell
opl
```

為主。

---

## 18. CLI Review Checklist

修改 CLI 時請確認：

* [ ] 命令名稱清楚且一致
* [ ] CLI 不包含主要業務邏輯
* [ ] 使用 `--help` 可理解命令用途
* [ ] 設定檔參數行為明確
* [ ] 預設設定檔解析正確
* [ ] 錯誤訊息可操作
* [ ] Exit Code 正確
* [ ] CLI 測試已新增或更新
* [ ] README 已更新
* [ ] CLI Reference 已更新
* [ ] Changelog 已更新（如適用）
* [ ] 未完成命令清楚標示為規劃中
* [ ] `pre-commit run --all-files` 通過
* [ ] `python -m pytest` 通過

---

## 19. Related Documents

* [Documentation Hub](../README.md)
* [Architecture Overview](../architecture/overview.md)
* [Generator Framework](../architecture/generator-framework.md)
* [Configuration Framework](../architecture/configuration-framework.md)
* [Generator Registry](../architecture/registry.md)
* [Configuration Reference](configuration.md)
* [Development Workflow](../development/development-workflow.md)
* [Code Review Checklist](../development/code-review-checklist.md)

---

> **好的 CLI 應讓正確的操作容易完成，並讓錯誤原因容易理解。**
