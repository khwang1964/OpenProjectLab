# Marketplace CLI

OpenProjectLab 提供 deterministic、local-only 的 Marketplace CLI，用於檢視
versioned artifacts、驗證 exact payload bytes，以及執行 process-local、
non-activating installation。

## 命令清單

production command family 僅包含：

```text
opl marketplace versions IDENTITY --catalog FILE [--json]
opl marketplace inspect COORDINATE --catalog FILE [--json]
opl marketplace verify COORDINATE --catalog FILE --payload-root DIR [--json]
opl marketplace install COORDINATE --catalog FILE --payload-root DIR [--dry-run] [--json]
```

`IDENTITY` 格式為 `namespace/name`；`COORDINATE` 格式為
`namespace/name@MAJOR.MINOR.PATCH`。

沒有 `opl marketplace list` 命令。若要查詢版本，請針對一個 exact
identity 使用 `versions`。

## 本機 catalog

每個命令都必須明確指定一份 UTF-8 JSON catalog。最小範例如下：

```json
{
  "schema_version": 1,
  "artifacts": [
    {
      "schema_version": 1,
      "identity": {
        "namespace": "community",
        "name": "demo"
      },
      "version": "1.2.3",
      "artifact_type": "template",
      "description": "Local demo artifact",
      "compatibility": ">=1.0,<2.0",
      "distribution": {
        "kind": "file",
        "reference": "packages/demo.opl"
      },
      "integrity": {
        "algorithm": "sha256",
        "digest": "<64 lowercase hexadecimal characters>"
      }
    }
  ]
}
```

若 UTF-8 JSON malformed、schema version 不支援、field type 錯誤、出現
unknown field、identity／coordinate 無效，或 exact coordinate 重複，catalog
parsing 會 fail closed。

## Payload root 與安全性

`verify` 與 `install` 必須指定 `--payload-root DIR`。artifact 的
`distribution.reference` 只能在此 root 下解析。

CLI 會拒絕 absolute path、drive-prefixed path、parent traversal、missing
file、directory、escaping symlink、unsupported distribution kind，以及任何
network fallback。Lookup、containment、acquisition 與 SHA-256 verification
必須在 installation 之前完成。

## 操作範例

列出 deterministic semantic versions：

```powershell
python -m generator.cli.main marketplace versions community/demo `
  --catalog .\examples\marketplace\catalog.json
```

以 JSON 檢視一個 exact artifact：

```powershell
python -m generator.cli.main marketplace inspect community/demo@1.2.3 `
  --catalog .\examples\marketplace\catalog.json `
  --json
```

驗證本機 payload bytes，但不安裝：

```powershell
python -m generator.cli.main marketplace verify community/demo@1.2.3 `
  --catalog .\examples\marketplace\catalog.json `
  --payload-root .\examples\marketplace\payloads `
  --json
```

不呼叫 installer，先預覽 installation：

```powershell
python -m generator.cli.main marketplace install community/demo@1.2.3 `
  --catalog .\examples\marketplace\catalog.json `
  --payload-root .\examples\marketplace\payloads `
  --dry-run `
  --json
```

執行 process-local installation：

```powershell
python -m generator.cli.main marketplace install community/demo@1.2.3 `
  --catalog .\examples\marketplace\catalog.json `
  --payload-root .\examples\marketplace\payloads
```

## 輸出與失敗

human-readable success output 寫入 stdout。使用 `--json` 時，成功只輸出一個
compact UTF-8 JSON object，且包含 `schema_version: 1`。diagnostic 寫入
stderr。

broad exit contract：

- `0`：Marketplace operation 成功；
- `2`：usage error，或 handled catalog、lookup、payload、integrity、
  installation、filesystem failure。

handled failure 不會輸出 success JSON document；若 failure 發生於
installation 之前，installer state 必須保持不變。

## Installation 不等於 activation

Marketplace installation 是 process-local、non-persistent、
non-activating：

```text
artifact installed != artifact activated
```

它不會 register plugin、execute Generator、write Courseware output，或修改
package manager environment。

## Deferred 功能

目前 CLI 不提供 remote Marketplace access、implicit network fallback、
global browsing/search、dependency resolution、lockfile、cache、publisher
signing/trust、ratings/reviews、payment、automatic activation、plugin
execution 或 AI CLI behavior。

## 檢查清單

- 使用 exact identity 或 coordinate。
- 明確指定 local catalog。
- `verify` 與 `install` 明確指定 payload root。
- 使用 `--dry-run` 驗證 installation inputs，且不產生 installer effects。
- 使用 `--json` 取得 deterministic machine-readable success output。
- SHA-256 integrity 只代表 bytes 相符，不代表 publisher authenticity。
- 不假設 installation 會 activate 或 persist artifact。

## 下一步

繼續閱讀 [疑難排解](troubleshooting.md)。
