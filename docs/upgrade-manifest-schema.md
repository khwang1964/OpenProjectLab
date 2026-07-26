# Upgrade Manifest Schema 1.0

## Root

| 欄位 | 必填 | 型別 | 說明 |
|---|---:|---|---|
| `schema_version` | 是 | string | 固定為 `1.0` |
| `package` | 是 | string | 更新包名稱 |
| `version` | 是 | string | 更新包版本 |
| `description` | 否 | string | 更新說明 |
| `entries` | 是 | list | 至少一筆更新項目 |

## Entry

| 欄位 | 必填 | 說明 |
|---|---:|---|
| `path` | 是 | 相對於專案根目錄的 POSIX 路徑 |
| `operation` | 是 | `add`、`modify`、`delete` |
| `sha256` | add/modify | payload 的 SHA256 |
| `source_sha256` | 否 | 目前專案檔案的預期 SHA256 |

## Path 規則

合法：

```text
generator/core/example.py
docs/example.md
```

不合法：

```text
../outside.txt
C:/Windows/file.txt
folder\file.txt
CON.txt
```
