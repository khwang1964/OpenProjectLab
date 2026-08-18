# Generators

Generators 是 OpenProjectLab（OPL）主要的內容生產單元。它們將已驗證 requests 轉換成明確 generation plans，再透過 shared framework lifecycle 執行。

本章說明 user-facing Generator model，以及目前 CLI 提供的 built-in Generator families。

## 1. Canonical Lifecycle

built-in Generators 遵循：

```text
GenerateRequest
    ↓
validate_request
    ↓
plan
    ↓
execute
    ↓
GenerationResult
```

此 lifecycle 由 framework 擁有。Generator 提供 domain-specific validation 與 planning behavior，但不取代共同 execution model。

## 2. Request Model

generation request 主要包含：

```text
generator_name
target
values
options
```

`values` 保存 Generator-specific structured input。

runtime options 包含 CLI flags 所代表的 shared behaviors，例如：

```text
--dry-run
--force
```

對支援 manifest 的 built-in commands，CLI 會透過 generation context 傳遞 manifest recording 設定。

## 3. 先 Planning，再 Execution

有效 request 會轉換成 `GenerationPlan`。

planning 讓預計執行的 filesystem operations 在 execution 前明確化。這有利於 deterministic tests，也避免各 Generator 偷偷建立彼此不相容的 write lifecycle。

plan 將 templates、destinations 與 rendering 所需 context 建立明確關聯。

## 4. Built-in Generator Identities

目前 built-in Generator identities：

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

使用：

```console
opl list
```

查看 installed set。

## 5. Bootstrap Generator

identity：

```text
bootstrap
```

用途：建立較完整的 project/course skeleton。

典型 user input：

```text
project slug
project/course name
language
license
optional copyright metadata
```

CLI 範例：

```console
opl --output-root ./output bootstrap modern-java --name "Modern Java"
```

Bootstrap 與其他 built-in Generators 共用相同 validation、planning、execution、dry-run、overwrite 與 result boundaries。

## 6. Course Generator

identity：

```text
course
```

用途：生成 course-level README artifact。

典型 input：

```text
course name
language
weeks
license
optional textbook
optional instructor
optional description
```

代表性 target：

```text
<output-root>/<project-slug>/README.md
```

CLI 範例：

```console
opl --output-root ./output course demo-course --name "Demo Course" --weeks 4 --language en
```

First 15 Minutes executable documentation smoke test 使用此 Generator，因為它能提供小型但完整的 installed-artifact end-to-end workflow。

## 7. Week Generator

identity：

```text
week
```

用途：生成 weekly courseware README。

典型 input：

```text
week number
title
course name
language
optional textbook chapter
directory pattern
```

CLI default directory pattern：

```text
week-{week:02d}
```

範例：

```console
opl --output-root ./output week demo-course --week 1 --title "Introduction"
```

## 8. Lab Generator

identity：

```text
lab
```

用途：生成 weekly Lab material。

必要 CLI concepts：

```text
week
lab-id
title
```

範例：

```console
opl --output-root ./output lab demo-course --week 1 --lab-id hello-lab --title "Hello Lab"
```

## 9. Assignment Generator

identity：

```text
assignment
```

用途：從 structured content 生成 Assignment material。

CLI 從以下 option 指定的檔案載入 UTF-8 JSON object：

```text
--content-file FILE
```

再將 structured values 傳入 Generator contract。

command shape：

```console
opl --output-root ./output assignment demo-course --week 1 --assignment-id assignment-01 --title "Assignment 01" --content-file ./assignment.json
```

本章不推測完整 Assignment JSON schema；應使用與 installed version 對應的 Assignment contract 與 examples。

## 10. Quiz Generator

identity：

```text
quiz
```

用途：從 structured questions 生成 Quiz material。

CLI 透過：

```text
--questions-file FILE
```

載入 UTF-8 JSON。

command shape：

```console
opl --output-root ./output quiz demo-course --week 1 --quiz-id quiz-01 --title "Quiz 01" --questions-file ./questions.json
```

載入後的 question structure 是否符合 Quiz contract，由 Generator validation 判定。

## 11. Slides Generator

identity：

```text
slides
```

用途：從 structured slide content 生成 Markdown slide material。

input 由：

```text
--slides-file FILE
```

載入。

command shape：

```console
opl --output-root ./output slides demo-course --title "Week 01 Slides" --slides-file ./slides.json
```

## 12. Website Generator

identity：

```text
website
```

用途：從 structured page content 生成 static course website output。

input 由：

```text
--pages-file FILE
```

載入。

command shape：

```console
opl --output-root ./output website demo-course --title "Demo Course" --pages-file ./pages.json
```

## 13. Package-Owned Templates

built-in Generators 正常從 installed `generator.resources` package boundary 解析 templates。

這是 v1.0 installed-user contract 的重要部分：

```text
installed wheel
    ↓
package-owned template
    ↓
Generator plan
    ↓
generated artifact
```

一般使用不得要求 repository-level template tree。

如果確實需要 custom template，可以明確使用 `--template-root` override。

## 14. Dry Run

使用：

```text
--dry-run
```

在不進行正常 persisted generation 的情況下完成 validation 與 planning。

例如：

```console
opl --output-root ./output course demo-course --name "Demo Course" --dry-run
```

First 15 Minutes smoke test 會驗證這個代表性 Course dry-run 不會持久化 `README.md`。

## 15. Overwrite Behavior

只有在確實要 overwrite 時才使用：

```text
--force
```

沒有 overwrite permission 時，existing destinations 會依既有 filesystem/Generator contract 受到保護。

不要設計必須固定依賴 `--force` 才能隱藏 stale 或 unexpected output 的 automation。

## 16. Manifest Recording

built-in CLI generation requests 正常會啟用 manifest recording。

使用：

```text
--no-manifest
```

可以停用單次 request 的 manifest update。

manifest 是 OPL-owned metadata，不應與 Generator 的主要 authored artifact 混為一談。

## 17. Validation 與 Failure

Generators 會在可避免的 write effects 前驗證 domain input。

invalid input 可能包括：

- 非正數的 week counts 或 week numbers；
- 缺少 required identifiers；
- JSON 載入後的 structured content 無效；
- Generator-specific schema violations；
- unsafe 或 conflicting filesystem operations。

CLI 會將已處理的 validation/configuration/value/file failures 轉換成 non-zero exit status。

## 18. Determinism

對等價 inputs 與相關 configuration，Generators 應產生可預測 plans。

determinism 支援：

```text
contract tests
integration tests
documentation smoke tests
CI
reviewable generated artifacts
```

沒有明確 contract 時，Generator 不應把 hidden network calls 或其他 uncontrolled external behavior 帶入 canonical lifecycle。

## 19. Generators 與 Courseware Composition

Courseware Composition 協調既有 Generators。

概念：

```text
courseware intent
    ↓
ordered Generator requests
    ↓
canonical lifecycle for each Generator
    ↓
composed courseware artifacts
```

Composition 不會建立第二套 Generator framework，也不代表對已成功執行的 Generators 提供 generalized rollback。

詳見 [Courseware](courseware.md)。

## 20. Third-Party Generators

第三方 Generators 透過 Plugin SDK 與 canonical Entry Point group 整合：

```text
openprojectlab.generators
```

它們應參與相同 public Generator contracts，而不是略過 validation、planning 或 registration。

詳見 [Plugins](plugins.md)。

## 21. Generator Checklist

執行 Generator 前確認：

```text
[ ] 使用 opl list 確認 Generator identity。
[ ] 查看 opl <command> --help。
[ ] 提供所有 required domain input。
[ ] location 重要時使用 explicit output root。
[ ] 除非刻意 override，否則使用 package-owned templates。
[ ] 寫入前考慮使用 --dry-run。
[ ] 只有刻意 overwrite 時才使用 --force。
[ ] 決定是否維持 manifest recording。
[ ] 將 structured JSON files 視為需要驗證的 Generator inputs。
```

## 下一步

繼續閱讀 [Courseware](courseware.md)，了解 Generator outputs 如何參與更大的 courseware model。
