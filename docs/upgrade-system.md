# Upgrade/Patch System

## 1. 目的

Step 12 提供安全、可預覽、可驗證、可備份的專案更新機制：

```powershell
opl upgrade patch.zip
opl upgrade patch.zip --apply
```

預設只產生 Upgrade Plan，不修改任何檔案。

## 2. 架構

```text
CLI
└─ generator.cli.upgrade
   └─ UpgradeManager
      ├─ UpgradeManifest
      ├─ PatchEntry
      ├─ Path Safety
      ├─ SHA256 Integrity
      ├─ Conflict Detection
      ├─ Backup
      ├─ Apply
      ├─ Rollback
      └─ Upgrade Report
```

## 3. 更新包格式

```text
patch.zip
├─ upgrade-manifest.yaml
└─ payload/
   └─ relative/project/path
```

範例：

```yaml
schema_version: "1.0"
package: "template-pack"
version: "2.1.0"
description: "更新模板系統"
entries:
  - path: "templates/course/README.md.j2"
    operation: "modify"
    source_sha256: "<舊檔 SHA256>"
    sha256: "<新檔 SHA256>"

  - path: "docs/new-document.md"
    operation: "add"
    sha256: "<新檔 SHA256>"

  - path: "templates/legacy.md.j2"
    operation: "delete"
    source_sha256: "<舊檔 SHA256>"
```

## 4. Operation

- `add`：目標應不存在。
- `modify`：目標應存在。
- `delete`：刪除既有檔案。
- `source_sha256`：選用；用於保護使用者本地修改。
- `sha256`：`add`、`modify` 必填，驗證 payload。

## 5. 安全策略

- 禁止絕對路徑。
- 禁止 `..`。
- 禁止反斜線路徑。
- 禁止 Windows 保留檔名。
- ZIP 解壓前逐項驗證路徑。
- Payload SHA256 必須符合 Manifest。
- 預設拒絕衝突。
- 實際修改前先備份。
- 套用中發生例外時自動 rollback。

## 6. 備份

預設備份到：

```text
.opl/backups/<package>-<version>-<timestamp>/
```

備份內同時包含：

```text
upgrade-report.yaml
```

## 7. CLI

預覽：

```powershell
opl upgrade .\patch.zip
```

套用：

```powershell
opl upgrade .\patch.zip --apply
```

強制接受衝突：

```powershell
opl upgrade .\patch.zip --apply --allow-conflicts
```

`--allow-conflicts` 只應在已人工檢查差異後使用。

## 8. 測試

```powershell
python -m pytest `
  tests/core/test_upgrade.py `
  tests/integration/test_upgrade_cli.py `
  -v --no-cov
```

## 9. 後續演進

Step 13 可加入：

- `opl patch create`
- 差異自動產生
- Ed25519 簽章
- Upgrade history
- Explicit rollback command
