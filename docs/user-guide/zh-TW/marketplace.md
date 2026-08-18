# Marketplace

OpenProjectLab 的 Marketplace layer 定義 versioned artifact metadata、acquisition、integrity verification 與 installation 的 deterministic contracts。它刻意比 hosted public marketplace service 更窄。

## Domain scope

Marketplace domain 包含 `ArtifactIdentity`、`ArtifactVersion`、`ArtifactCoordinate`、`ArtifactType`、`CompatibilityRequirement`、`DistributionMetadata`、`IntegrityMetadata`、`MarketplaceArtifact`。

exact coordinate 識別 exact versioned artifact，有利於 deterministic lookup 與 tests。

## Pipeline boundaries

以下 stages 必須分離：

```text
metadata lookup
→ acquire exact payload bytes
→ verify integrity
→ install validated payload
```

metadata lookup 不等於 acquisition；acquisition 不等於 verification；verification 不等於 installation 或 activation。

## Acquisition

`ArtifactAcquirer.acquire(MarketplaceArtifact) -> bytes` 回傳 payload bytes。baseline in-memory acquirer 不執行 integrity verification、installation、activation、plugin registration、Generator execution、filesystem mutation 或 network access。

## Integrity

目前 verifier 支援依 `IntegrityMetadata` 做 deterministic SHA-256 digest checking。digest mismatch 產生 integrity error；unsupported algorithm 產生獨立 error。

digest integrity 只證明 bytes 與 declared digest 相符，**不**建立 publisher identity、provenance、trust 或 authenticity。

## Installation

`ArtifactInstaller` 安裝 artifact payload 並回傳 `ArtifactInstallationResult`。目前 in-memory implementation 記錄 bytes/metadata、回報 `installed`，並拒絕同一 exact coordinate 重複安裝。

installation 刻意與 activation 分離：

```text
artifact installed ≠ artifact activated
```

installer 不會 access package manager/network、discover Entry Points、register plugins、execute Generators 或 write Courseware output。

## Plugins

Marketplace 與 Plugin SDK 負責不同 stages：

```text
Marketplace → metadata / bytes / integrity / installation
Plugin SDK  → Entry Point discovery / validation / registry
```

因此 plugin artifact installed 不代表其 Generator 已 registered。

## Public API boundary

Marketplace models 不會因 modules 已存在就自動成為 `generator.sdk`。長期 public compatibility 是獨立 release decision。

## v1.0 不承諾的功能

目前 Marketplace domain 不建立 public remote marketplace、browsing/search UI、publisher accounts、ratings/reviews、payments、automatic dependency resolution、package-manager installation、plugin activation、Generator execution、publisher-signature trust infrastructure 或 baseline network acquisition。

### Checklist

- resolve exact versioned artifact。
- metadata lookup 與 payload acquisition 分離。
- acquired bytes 在 integrity checking 成功前視為 unverified。
- 不把 SHA-256 integrity 當成 publisher authenticity。
- 只安裝原本要驗證的 payload。
- 不假設 installation 會 activate plugins 或 execute Generators。
- 不假設 baseline Marketplace components 使用 network。
- hosted marketplace features 除非明確文件化，否則不屬於 v1.0。

## 下一步

繼續閱讀 [Troubleshooting](troubleshooting.md)。
