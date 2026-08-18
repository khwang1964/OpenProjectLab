# 組態設定

OpenProjectLab（OPL）提供一個精簡的 YAML configuration model，以及三個全域 CLI path overrides。本章只說明目前 v1.0 release-readiness baseline 已實作的 configuration behavior。

configuration file 並不是第二套 command language。Generator-specific inputs 仍應由各 CLI command 或 programmatic request 提供。

## 1. Configuration Model

`ProjectConfig` 識別四個 top-level YAML sections：

```yaml
project: {}
paths: {}
generator: {}
plugins: {}
```

每個 section 若存在，都必須是 YAML mapping。缺少的 section，或明確設定為 `null` 的 section，會視為空 mapping。

loader 會拒絕：

- 明確指定但不存在的 configuration file；
- 格式錯誤的 YAML；
- YAML document root 不是 mapping；
- 已識別 section 的 value 不是 mapping。

其他未知 top-level keys 不屬於本手冊所定義的 configuration contract。

## 2. Configuration 範例

repository 中目前的 development default 具有以下結構：

```yaml
project:
  name: OpenProjectLab
  version: 0.6.0
  locale: zh-TW

paths:
  templates: templates
  courses: courses
  docs: docs

generator:
  overwrite: false
  dry_run: false

plugins:
  enabled: true
```

這個範例展示可接受的 section structure。不要假設其中每個 value 都會被每一個 CLI command 使用。

對目前 CLI root resolution 而言，`paths` section 是直接相關的 configuration surface。

## 3. 指定 Configuration File

全域 option：

```text
--config FILE
```

例如：

```console
opl --config ./opl.yaml list
```

明確指定的 configuration file 必須存在，且內容必須是有效 YAML。

CLI 同時具有一個 built-in development default path。在 installed distribution 中，這個 repository-oriented default file 可能不存在；如果缺少的正是 built-in default，CLI 會在不載入它的情況下繼續。如此一般 installed use 就能依賴 package-owned templates 與明確 output root，而不需要 source checkout。

## 4. Template Root Resolution

CLI 依下列優先順序解析 template root：

```text
--template-root
    ↓
paths.template_root
    ↓
paths.templates
    ↓
package-owned default template root
```

全域 override：

```text
--template-root DIR
```

例如：

```console
opl --template-root ./custom-templates course demo-course --name "Demo Course"
```

一般 installed-user workflow 應省略此 option，使用 package-owned runtime templates。

custom template root 屬於 advanced override。OPL 不保證任意 external template tree 都與所有 built-in Generator 相容。

## 5. Output Root Resolution

CLI 依下列優先順序解析 output root：

```text
--output-root
    ↓
paths.course_root
    ↓
paths.courses
    ↓
paths.output_root
    ↓
built-in default output root
```

全域 override：

```text
--output-root DIR
```

例如：

```console
opl --output-root ./output course demo-course --name "Demo Course"
```

為了讓 user documentation 與 automation 更可重現，建議明確指定 `--output-root`。

## 6. Relative Path 行為

CLI 會展開並解析 path values。

目前 CLI 將 relative configured path 或 command-line root 相對於其 internal project-root resolution boundary 解析，而不一定相對於 shell 的 current working directory。

因此，需要精確 filesystem location 的 automation 應優先使用 absolute path。First 15 Minutes smoke test 在執行 installed artifact 時，就是以程式方式提供明確路徑。

不要讓 scripts 依賴未文件化的 repository checkout location 假設。

## 7. `project` Section

loader 接受 `project` mapping。

例如：

```yaml
project:
  name: Example Courseware Project
  locale: en
```

generic configuration loader 會保留此 mapping，但目前 CLI 不會自動將任意 `project` values 轉換成每一個 Generator 的 command arguments。

如果 Generator command 要求 `--name`、`--week`、`--title` 或其他明確 argument，除非 command documentation 另有說明，仍必須提供。

## 8. `generator` Section

loader 接受 `generator` mapping。

例如：

```yaml
generator:
  overwrite: false
  dry_run: false
```

目前 CLI 的 write behavior 由 command options 控制：

```text
--dry-run
--force
--no-manifest
```

除非有明確文件與測試，不要假設 generic `generator` mapping 中的任意 values 會覆寫這些 CLI options。

## 9. `plugins` Section

loader 接受 `plugins` mapping。

例如：

```yaml
plugins:
  enabled: true
```

Plugin discovery、validation、loading 與 registration 有各自的 public contracts。configuration key 的存在本身並不構成完整 plugin-management interface。

使用者可見的 plugin model 請參閱 [Plugins](plugins.md)。

## 10. Configuration Errors

當 OPL 無法安全解析明確指定的 configuration file 時，會回報 configuration failure。

常見原因：

```text
file does not exist
invalid YAML
document root is not a mapping
project is not a mapping
paths is not a mapping
generator is not a mapping
plugins is not a mapping
```

疑難排解時，可先將檔案縮減為最小有效 mapping：

```yaml
paths: {}
```

再逐項加入 workflow 真正需要的設定。

## 11. 建議的 Installed-User Configuration

簡單 installed-user workflow 可以只使用最少設定。

例如：

```yaml
paths:
  courses: C:/Users/example/opl-output
```

也可以完全不建立 persistent configuration file，而直接指定 output root：

```console
opl --output-root <output-directory> course demo-course --name "Demo Course"
```

後者特別適合 CI 與教學，因為 path 直接出現在 command 中。

## 12. Configuration Checklist

使用 configuration file 前確認：

```text
[ ] 檔案為 UTF-8 YAML。
[ ] YAML root 是 mapping。
[ ] project、paths、generator、plugins 在存在時皆為 mapping。
[ ] Path overrides 指向預期位置。
[ ] location 重要時，automation 使用明確或 absolute paths。
[ ] Generator-specific required CLI arguments 仍有提供。
[ ] Custom template root 是刻意選擇。
```

## 下一步

繼續閱讀 [CLI](cli.md)，了解完整 command-line surface。
