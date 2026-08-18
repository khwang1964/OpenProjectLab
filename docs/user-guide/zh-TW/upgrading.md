# Upgrading

OpenProjectLab 提供明確的 upgrade-package mechanism，用於 preview 與套用受控的 project changes。此 command 使用 OPL upgrade ZIP 更新 project content；它**不是**用 `pip` 升級 installed `openprojectlab` Python distribution 的替代方式。

## 1. 兩種不同的 Upgrade

請分清楚：

```text
Python package upgrade
→ 改變 installed OPL software

opl upgrade <package.zip>
→ inspect/apply OPL project upgrade package
```

若要更換 installed Python distribution，應依取得 artifact 的 package installation/release procedure 執行。

本章說明第二種 operation。

## 2. 安全預設：先 Inspect

`upgrade` command 需要 ZIP package：

```console
opl upgrade <package.zip>
```

未指定 `--apply` 時，OPL 只 inspect package 與 project state，顯示：

```text
package/version
added paths 數量
modified paths 數量
deleted paths 數量
unchanged paths 數量
conflicts（若有）
```

最後會明確表示尚未變更任何檔案。

preview-first 是正常 workflow。

## 3. Inspection Exit Status

plan 沒有 conflicts 時 inspection 成功。

若 plan 有 conflicts，CLI 會列出它們並回傳 conflict status，不修改 project。

請利用 conflict list 判斷目前 project 是否符合 upgrade package 的 source-state assumptions。

## 4. Apply Upgrade

確認 plan 沒問題後：

```console
opl upgrade <package.zip> --apply
```

upgrade manager 會再次驗證 package、建立 backup，然後套用 declared operations。

成功後會顯示 package/version、changed paths 數量與 backup directory。

## 5. Upgrade Package Structure

ZIP 包含：

```text
upgrade-manifest.yaml
payload/
```

目前 manifest schema 要求：

```text
schema_version: "1.0"
package: <non-empty string>
version: <non-empty string>
description: <string>
entries: <non-empty list>
```

每個 entry 宣告：

```text
path
operation
sha256            # add/modify 必須
source_sha256     # optional current-state guard
```

supported operations：

```text
add
modify
delete
```

重複 manifest paths 會被拒絕。

## 6. Path Safety

manifest paths 必須是安全的 relative POSIX-style paths。

OPL 會拒絕 absolute path、含 `..` 或 `.` components、使用 backslashes、空 path，以及 Windows reserved device names。

ZIP members 在 extraction 前會驗證 path；final target 也會檢查必須位於 project root 內。

這些 checks 用來降低 path traversal 與 unsafe target 風險。

## 7. Payload Integrity

每個 `add` / `modify` entry 都需要 64-character SHA-256 digest。

planning 或 apply 前，OPL 會確認 `payload/` 下對應 file 存在且 digest 相符。

payload 缺少或 digest mismatch 都會讓 upgrade 失敗。

## 8. Conflict Detection

plan 會檢查 current project state。

### `add`

target 已存在即 conflict。

### `modify`

target 不存在即 conflict。

若有 `source_sha256`，current target 必須符合該 digest，否則 conflict。

若 current file 已等於 new payload digest，會分類為 unchanged。

### `delete`

target 不存在視為 unchanged。

若有 `source_sha256`，existing target 必須符合後才能 delete，否則記錄 conflict。

## 9. `--allow-conflicts`

CLI 提供：

```text
--allow-conflicts
```

它只在 apply 時有意義：

```console
opl upgrade <package.zip> --apply --allow-conflicts
```

此 option 允許 plan 存在 add/modify/delete state conflicts 時仍進行 application。

只有在理解每個 conflict 後才應使用。它不會停用 manifest validation、path safety 或 payload integrity checks。

conflicts 代表 project 與 package 預期 source state 不同，因此 override 前強烈建議使用 version control 或 external backup。

## 10. Backups

變更 existing path 前，OPL 會把 previous state 複製到 timestamped backup directory。

預設位置：

```text
.opl/backups/
```

successful result 會顯示 exact backup directory。

其中也會寫入 `upgrade-report.yaml`，記錄 package/version，以及 plan 的 added、modified、deleted、unchanged、conflict lists。

upgraded project 驗證完成前不要刪除 backup。

## 11. Apply Failure 時的 Rollback

upgrade manager 在 apply 過程維護 operation journal。

若 application 中發生 exception，它會嘗試從 backup 恢復先前存在的 paths，並移除 failed operation 中建立的新 paths。

此 rollback 僅屬於 upgrade manager controlled apply operation。不要把它延伸解讀到 Generator execution 或 Courseware composition；那些 subsystem 有不同 failure semantics。

## 12. Project Root

CLI upgrade handler 預設使用 current working directory 作為 project root，除非 calling code 另外提供 project root。

因此應從真正要 inspect/update 的 project 執行：

```console
cd <project-root>
opl upgrade <path-to-package.zip>
```

使用 `--apply` 前務必確認 current directory。

## 13. Recommended Workflow

```text
1. commit 或 backup current project work。
2. 切換到 intended project root。
3. 執行 opl upgrade <package.zip>。
4. 檢查 add/modify/delete/unchanged/conflict counts。
5. 處理 unexpected conflicts。
6. 決定 override conflicts 前先執行 normal project tests/checks。
7. review 完成後才使用 --apply。
8. 驗證 upgraded project。
9. validation 完成前保留 reported .opl/backups directory。
10. 將 resulting project changes 另外 commit。
```

## 14. `opl upgrade` 不會做什麼

command 不會自動：

- 從 network 下載 upgrade package；
- 升級 installed Python package；
- resolve Marketplace dependencies；
- activate plugins；
- execute Generators；
- merge arbitrary user edits；
- 保證使用 `--allow-conflicts` 後的 project 在 semantic 上一定正確。

## 15. Recovery Guidance

若 apply 回報 failure，先保存 error 並檢查 backup directory，再嘗試下一次 apply。

若使用 version control，也檢查：

```console
git status
git diff
```

在理解 project state 前，不要反覆使用 `--allow-conflicts` 套用同一 package。

## Upgrade Checklist

- backup 或 commit current work。
- 確認 intended project root。
- apply 前先 inspect。
- review 每個 conflict。
- integrity error 應查明原因，不要繞過。
- `--allow-conflicts` 只在明確理解後使用。
- apply 後驗證 project。
- validation 成功前保留 `.opl/backups`。
- project upgrade 與 Python package upgrade 分開。

## 下一步

回到 [README](README.md)，或 upgrade 失敗時查看 [Troubleshooting](troubleshooting.md)。
