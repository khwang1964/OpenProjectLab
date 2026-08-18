# Plugins

OpenProjectLab 透過 Plugin SDK 與 Python Entry Points 支援第三方 Generator extensions。Plugins 與 built-in Generators 使用相同 Generator lifecycle。

## Architecture

```text
installed Python distribution
→ Entry Point discovery
→ load candidate
→ validate Generator contract
→ validate identity
→ preflight collisions
→ GeneratorRegistry
```

canonical Entry Point group：

```text
openprojectlab.generators
```

plugin authors 應依賴 public Plugin SDK，而不是 private implementation modules。

## Packaging 與 discovery

distribution 可透過 packaging metadata 宣告 Generator：

```toml
[project.entry-points."openprojectlab.generators"]
hello = "example_plugin:HelloGenerator"
```

discovery 使用 installed Python distribution metadata；任意 source directory 不等於 installed plugin。

## Loading 與 validation

OPL 載入 Entry Point object，並依 shared Plugin SDK Generator contract 驗證。Python import 成功本身不足以證明 object 是有效 plugin。

Entry Point metadata name 必須等於 Generator public runtime `name`：

```text
EntryPoint.name == Generator.name
```

不一致會被拒絕。

## Atomic batch registration

對一批 Entry Points，OPL 會先載入與驗證全部 candidates，並完成 registration preflight 後才修改 registry。batch 內重複 names，以及 target registry 已存在的 names 都會被拒絕。因此後面的 failure 不會留下前面 batch members 部分註冊的狀態。

`GeneratorRegistry` 仍是 plugin loading 與 courseware orchestration 共用的 lookup boundary。

## Lifecycle

```text
package plugin
→ install distribution
→ discover Entry Point
→ load
→ validate
→ register
→ resolve through shared Generator framework
```

installation 與 activation/registration 是不同概念。

## Marketplace relationship

Marketplace installation **不會**自動 discover 或 register plugin Entry Points：

```text
Marketplace artifact installed ≠ plugin activated
```

詳見 [Marketplace](marketplace.md)。

## Troubleshooting

plugin 無法載入時，確認它與 OPL 安裝在相同 Python environment、宣告 `openprojectlab.generators`、export 有效 Plugin SDK Generator、Entry Point name 等於 `Generator.name`，且沒有與既有 registry name collision。

### Plugin author checklist

- 依賴 public Plugin SDK。
- 實作 canonical Generator contract。
- package 成 installable Python distribution。
- 宣告 `openprojectlab.generators`。
- Entry Point name 與 `Generator.name` 相同。
- 避免 private OPL dependencies。
- 在 clean environment 測試 installation/discovery。
- 測試 validation 與 collision failures。
- 不假設 Marketplace installation 等於 activation。

## 下一步

繼續閱讀 [AI Integration](ai-integration.md)。
