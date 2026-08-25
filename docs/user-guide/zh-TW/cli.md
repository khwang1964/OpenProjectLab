# 命令列介面（CLI）

`opl` 是 OpenProjectLab 安裝後的 command-line entry point。

本章說明目前 v1.0 release-readiness CLI surface。實際安裝版本的 executable source of truth 是：

```console
opl --help
opl <command> --help
```

## 1. Command 基本形式

一般形式：

```text
opl [global options] <command> [command options]
```

目前 global options：

```text
--config FILE
--template-root DIR
--output-root DIR
```

例如：

```console
opl --output-root ./output course demo-course --name "Demo Course"
```

global options 應放在 subcommand 前。

## 2. 可用 Commands

目前 CLI 定義：

```text
list
bootstrap
course
week
lab
assignment
quiz
slides
website
upgrade
```

`list` 列出 built-in Generator identities。`upgrade` 是 CLI operation，但不是 Generator identity。

目前也保留 hidden legacy `--list` compatibility path。新的文件與 automation 應使用：

```console
opl list
```

## 3. `list`

列出 built-in Generators：

```console
opl list
```

目前 identities：

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

這也是輕量的 installation verification。

## 4. 共用 Write Options

generation commands 提供：

```text
--dry-run
--force
--no-manifest
```

### `--dry-run`

執行 validation 與 planning，但不進行正常 persisted generation。

### `--force`

在 Generator/filesystem contract 允許時，允許 overwrite behavior。

### `--no-manifest`

此 generation request 不更新 `.opl/manifest.yaml`。

以下 built-in generation commands 都使用這組共用 options。

## 5. `bootstrap`

建立完整 course-project skeleton。

必要輸入：

```text
project_slug
--name NAME
```

選用輸入：

```text
--language LANGUAGE
--license LICENSE
--copyright-year YEAR
--copyright-holder HOLDER
--dry-run
--force
--no-manifest
```

defaults：

```text
--language zh-TW
--license "CC BY 4.0"
```

範例：

```console
opl --output-root ./output bootstrap modern-java --name "Modern Java"
```

## 6. `course`

生成 course README。

必要輸入：

```text
project_slug
--name NAME
```

選用輸入：

```text
--language LANGUAGE
--weeks N
--textbook TEXT
--instructor TEXT
--description TEXT
--license LICENSE
--dry-run
--force
--no-manifest
```

defaults：

```text
--language zh-TW
--weeks 16
--license "CC BY 4.0"
```

`--weeks` 必須是大於 0 的整數。

範例：

```console
opl --output-root ./output course demo-course --name "Demo Course" --weeks 4 --language en
```

## 7. `week`

生成 weekly courseware README。

必要輸入：

```text
project_slug
--week N
--title TITLE
```

選用輸入：

```text
--course-name NAME
--language LANGUAGE
--textbook-chapter TEXT
--directory-pattern PATTERN
--dry-run
--force
--no-manifest
```

defaults：

```text
--language zh-TW
--directory-pattern "week-{week:02d}"
```

`--week` 必須大於 0。

範例：

```console
opl --output-root ./output week demo-course --week 1 --title "Introduction"
```

## 8. `lab`

生成 weekly Lab README。

必要輸入：

```text
project_slug
--week N
--lab-id ID
--title TITLE
```

選用輸入：

```text
--course-name NAME
--dry-run
--force
--no-manifest
```

範例：

```console
opl --output-root ./output lab demo-course --week 1 --lab-id hello-lab --title "Hello Lab"
```

## 9. `assignment`

從 structured JSON content 生成 weekly Assignment README。

必要輸入：

```text
project_slug
--week N
--assignment-id ID
--title TITLE
--content-file FILE
```

選用輸入：

```text
--course-name NAME
--dry-run
--force
--no-manifest
```

content file 會以 UTF-8 JSON 載入，而且 JSON root 必須是 object。

command shape：

```console
opl --output-root ./output assignment demo-course --week 1 --assignment-id assignment-01 --title "Assignment 01" --content-file ./assignment.json
```

完整 structured content domain schema 應依 Assignment Generator contract，而不是由本章自行推測。

## 10. `quiz`

從 structured questions JSON file 生成 weekly Quiz README。

必要輸入：

```text
project_slug
--week N
--quiz-id ID
--title TITLE
--questions-file FILE
```

選用輸入：

```text
--course-name NAME
--dry-run
--force
--no-manifest
```

command shape：

```console
opl --output-root ./output quiz demo-course --week 1 --quiz-id quiz-01 --title "Quiz 01" --questions-file ./questions.json
```

檔案會以 UTF-8 JSON 解析。載入後的 question structure 是否符合 Quiz contract，由 Generator validation 判定。

## 11. `slides`

從 structured JSON content 生成 Markdown slides。

必要輸入：

```text
project_slug
--title TITLE
--slides-file FILE
```

選用輸入：

```text
--course-name NAME
--dry-run
--force
--no-manifest
```

command shape：

```console
opl --output-root ./output slides demo-course --title "Week 01 Slides" --slides-file ./slides.json
```

## 12. `website`

從 structured pages JSON 生成 static course website。

必要輸入：

```text
project_slug
--title TITLE
--pages-file FILE
```

選用輸入：

```text
--course-name NAME
--dry-run
--force
--no-manifest
```

command shape：

```console
opl --output-root ./output website demo-course --title "Demo Course" --pages-file ./pages.json
```

## 13. `upgrade`

CLI 也註冊 `upgrade` command。

upgrade behavior 有自己的 contract，應依 installed command help 與[升級](upgrading.md)章節使用。

查看實際 surface：

```console
opl upgrade --help
```

本章不會自行發明尚未由 upgrade command 建立的 options。

## 14. Exit Codes

成功執行 command 時，CLI 回傳：

```text
0
```

已處理的 OPL/configuration/value/JSON/file errors 會寫到 standard error，並回傳：

```text
2
```

script 應檢查 process exit status，而不是解析可能本地化的人類可讀錯誤訊息。

## 15. JSON Input Files

`assignment`、`quiz`、`slides`、`website` 接受 structured UTF-8 JSON files。

CLI 負責載入 JSON；對應 Generator contract 負責驗證載入後的 structure。

malformed JSON、missing file 或 invalid values 都會導致 non-zero CLI outcome。

## 16. Installed-User 範例

驗證安裝：

```console
opl --help
opl list
```

預覽 generation：

```console
opl --output-root ./output course demo-course --name "Demo Course" --dry-run
```

正式生成：

```console
opl --output-root ./output course demo-course --name "Demo Course"
```

這些範例刻意使用 explicit output root 與 package-owned templates。

## 17. CLI Automation 建議

scripts 與 CI 應：

- 使用 explicit global path options；
- 以 exit codes 作為主要 success/failure signal；
- 適當時先使用 `--dry-run`；
- 不依賴 hidden `--list`；
- 不依賴 localized human-readable output；
- installed-user workflow 不依賴 repository checkout；
- 將 JSON input files 視為對應 Generator contract 的 versioned inputs。

## 18. Marketplace 命令

additive `marketplace` family 僅提供 `versions`、`inspect`、`verify` 與
`install`。它使用 explicit local `--catalog` 與 `--payload-root` inputs、
支援 deterministic `--json` success output，並可透過 `--dry-run` 預覽
installation。

它不新增 `opl marketplace list`、remote access、automatic activation 或
persistent package installation。完整 command shapes、catalog 範例、安全規則與
failure boundaries 請閱讀 [Marketplace CLI](marketplace.md)。

## 下一步

繼續閱讀 [Generators](generators.md)，了解這些 commands 背後的 generation model。

## 19. AI CLI

Production `ai` command family 精確提供四個受治理的 subcommands：

```text
opl ai course
opl ai review
opl ai document
opl ai template
```

**Stable** execution path 是 deterministic `local-response` execution。此路徑
不需要 network connection、credential、paid account、provider SDK 或
provider client。

**Experimental** provider path 必須 explicit、injection-only 且 fail-closed。
Provider execution 需要 explicit provider selection 與 injected client factory。
AI CLI 不會執行 automatic SDK import、不會執行 automatic credential lookup、
不會執行 implicit provider selection，也不會執行 network fallback。

Validation 與 failure handling 保留既有 CLI boundary。已處理的 AI CLI failure
使用 exit code 2，diagnostic 寫到 stderr，且不輸出成功內容到 stdout。

AI CLI 對 filesystem 與 repository 維持 non-mutating behavior。`course`、
`review`、`document`、`template` handlers 只回傳 projected content/results，
不會把 AI output 寫入 project、repository、manifest、registry 或 Marketplace
state。

本節不會提前接受較大的 implementation 或 release：

```text
AI CLI Implementation Acceptance --- Not Accepted
Formal v1.1 Acceptance --- Not Accepted
```
