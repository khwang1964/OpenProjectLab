# Troubleshooting

本章提供 OpenProjectLab（OPL）v1.0 documented installed-user workflows 的系統化疑難排解方式。遇到問題時，先找出 failure boundary，不要立刻修改檔案或使用 `--force`。

## 1. 先確認執行環境

確認目前使用的是預期 Python environment：

```console
python --version
python -c "import generator; print(generator.__file__)"
opl --help
opl list
```

目前 package metadata 要求 Python 3.12 以上。若是在驗證 installed-user workflow，`generator.__file__` 應位於 installed environment，而不是 OpenProjectLab source checkout。

若 `python -c "import generator"` 成功但找不到 `opl`，請確認 environment 的 scripts directory 位於 `PATH`，且 wheel 確實安裝到同一 environment。

## 2. 找不到 `opl`

檢查 active environment 與 package installation：

```console
python -m pip show openprojectlab
python -m pip --version
```

若 package 不存在，將預期 wheel 安裝到目前 environment。

不要用 editable installation 當成 release artifact 可用的證據。Editable install 可能暴露 repository files，進而掩蓋 packaging defects。

## 3. `opl list` 沒有預期 Built-ins

documented built-in Generator identities：

```text
assignment
bootstrap
course
lab
quiz
slides
website
week
```

若結果不同，先確認實際執行的是哪一份 OPL installation。不要假設 unrelated plugin 或不同 environment 會改變 built-in contract。

## 4. Configuration Errors

CLI 接受 global options：

```text
--config FILE
--template-root DIR
--output-root DIR
```

明確指定的 configuration file 若不存在或內容無效，configuration loading 會失敗。請檢查 path、YAML syntax 與 documented configuration structure。

排查 path 問題時，可優先明確指定 `--output-root` 或 `--template-root`。

## 5. Template Errors

built-in installed-user workflow 正常使用 package-owned runtime templates。

若 generation 發生 template loading、validation 或 rendering 問題：

1. 確認正在測試 installed wheel，而不是依賴 repository `templates/`。
2. 若不是刻意測試 custom templates，先移除 `--template-root` override。
3. 使用 package-owned templates 重跑 representative command。
4. 若必須使用 custom template root，確認 directory structure 與 required template files 符合 Generator contract。

custom template tree 會改變 generated content，因此屬於 advanced override。

## 6. Generator Validation Errors

generation commands 會在寫入前驗證 required arguments 與 structured content。

常見原因：

- 缺少 required command options；
- week/count value 不是正整數；
- assignment、quiz、slides、website 的 JSON input malformed；
- structured content 違反 Generator contract；
- target 已存在但不允許 overwrite。

可使用 `--dry-run` 驗證並查看 planned output，而不修改檔案。

不要把 `--force` 當第一個 troubleshooting step。應先確認 existing target 為何與 requested generation 衝突。

## 7. Output 寫到非預期位置

onboarding 與 reproducible automation 建議明確指定 output root：

```console
opl --output-root ./opl-output course demo-course --name "Demo Course"
```

global options 必須放在 subcommand 前。

若 configuration 也提供 output paths，排查時明確 CLI override 最容易確認實際使用位置。

## 8. Structured JSON Files 無法載入

`assignment`、`quiz`、`slides`、`website` 接受 structured JSON files。

請確認：

- file 存在；
- 使用 UTF-8 JSON；
- top-level shape 符合 command documented contract；
- required fields 存在；
- values 使用預期 types。

JSON syntax 正確仍可能因 Generator validation 而失敗。

## 9. Existing Files 與 `--force`

shared write options：

```text
--dry-run
--force
--no-manifest
```

`--force` 是允許 overwrite 的控制，不是 repair operation。

使用前先檢查 existing output，確認 replacement 是刻意的。若檔案含 user edits，先備份或交由 version control 管理。

## 10. Manifest 問題

generation 預設可能依 Generator lifecycle 更新 `.opl/manifest.yaml`。

`--no-manifest` 會停用該 command 的 manifest recording。應刻意使用，不要只是為了掩蓋 manifest discrepancy。

若 generated files 與 manifest state 看起來不一致，先在 clean output directory 重現，再考慮手動修改 manifest。

## 11. Plugin Loading Problems

第三方 Generator plugin 請確認：

1. plugin distribution 與 OPL 安裝在同一 Python environment。
2. 宣告 `openprojectlab.generators` Entry Point。
3. Entry Point name 等於 Generator public `name`。
4. exported object 符合 Plugin SDK Generator contract。
5. name 不與既有 registry entry collision。

installation 本身不代表 plugin 已完成 discovery、validation 與 registration。

## 12. AI Integration Problems

documented v1.0 CLI 沒有 general `opl ai` command。

programmatic AI integration 應將 failures 分開：

```text
provider invocation
AIResponse production
response structure validation
domain mapping
downstream generation
```

provider 成功輸出不代表已是有效 OPL courseware。除非有明確 OPL contract，credentials 與 vendor-specific settings 屬於 selected adapter/deployment boundary。

## 13. Marketplace Problems

Marketplace stages 應分離：

```text
metadata lookup
→ acquisition
→ integrity verification
→ installation
→ optional later activation/integration
```

SHA-256 mismatch 表示 acquired bytes 與 declared integrity metadata 不符。installation 成功也不代表 plugin 自動 activated 或 Generator 已執行。

baseline in-memory Marketplace components 是 deterministic / no-network；不要用 hosted marketplace service 的假設來診斷它們。

## 14. Upgrade Problems

套用 upgrade package 前一定先 inspect：

```console
opl upgrade <package.zip>
```

inspection 不修改 project files。若 plan 有 conflicts，應先檢查，再決定是否 apply。

常見 upgrade failures：

- ZIP package 不存在或無效；
- `upgrade-manifest.yaml` 無效；
- manifest schema 不支援；
- unsafe paths；
- payload files 缺少；
- SHA-256 mismatch；
- current project state 與 add/modify/delete 發生 conflicts。

使用 `--apply` 或 `--allow-conflicts` 前先閱讀 [Upgrading](upgrading.md)。

## 15. Clean Reproduction

問題不明確時建立 minimal clean reproduction：

```text
fresh virtual environment
→ install intended wheel
→ work outside source repository
→ use package-owned templates
→ use explicit output root
→ run opl list
→ run smallest failing command
```

如此可分離 packaging/runtime defects 與 repository-local state。

## 16. Bug Report 應保留的資訊

請記錄：

```text
OPL package version/artifact
Python version
operating system
installation method
exact command
exit status
complete error message
是否在 source repository 內執行
是否使用 --config / --template-root / --output-root
重現所需 minimal input files
```

不要附上 API keys、credentials、private course material 或其他 secrets。

## Troubleshooting Checklist

- 確認 active Python environment。
- 確認 installed OPL package 與 `opl` executable。
- 驗證 packaging 時在 source checkout 外重現。
- 使用 explicit output root。
- destructive change 前優先 `--dry-run`。
- 使用 `--force` 前先診斷 validation/conflict。
- plugin installation 與 registration 分離。
- Marketplace installation 與 activation 分離。
- apply upgrade 前先 inspect。
- 保存 exact error 與 minimal reproduction。

## 下一步

繼續閱讀 [Upgrading](upgrading.md)。
