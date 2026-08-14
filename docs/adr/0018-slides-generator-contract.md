# ADR 0018: Slides Generator Contract

- **Status:** Proposed
- **Date:** 2026-08-14
- **Decision owners:** OpenProjectLab maintainers
- **Scope:** Open Courseware Platform / Generator Framework
- **Related ADRs:** 0005, 0006, 0007, 0008, 0014, 0015, 0016, 0017

## Context

OpenProjectLab（OPL）在 Milestone 5 已建立 Open Courseware Platform，並完成 Lab、Quiz 與 Assignment Generator 的垂直切片。下一個能力是 Slides Generator，用來為課程或週次產生可維護、可測試、可重複生成的投影片來源。

Slides 與 Lab、Quiz、Assignment 的主要差異，在於「投影片內容」與「最終呈現格式」之間存在額外的 rendering 邊界。若第一版直接把 Slides Generator 綁定特定二進位格式，例如 PowerPoint `.pptx`，Generator Contract 就會同時承擔課程內容規劃、投影片結構、版面引擎與檔案格式輸出的責任，造成不必要耦合。

OPL 既有 Generator Framework 已建立共享輸入、驗證、規劃與執行契約，因此 Slides Generator 應延續同一 canonical lifecycle，而不是建立特例。

本 ADR 定義第一版 Slides Generator 的公開契約、輸入資料、驗證規則、Generation Plan、輸出格式、Template 邊界、CLI 整合、錯誤行為、測試策略與未來 renderer 擴充方向。

## Decision

OPL 將新增 `SlidesGenerator`，並使其遵循既有 Generator canonical lifecycle：

```text
GenerateRequest
    ↓
validate()
    ↓
plan()
    ↓
generate()
    ↓
GenerationResult
```

第一版 Slides Generator 的 canonical artifact 為 **Markdown 投影片來源檔**，而不是直接產生 `.pptx`。

Slides Generator 負責：

- 驗證 slides-specific request values。
- 將課程或週次資料轉換成投影片生成計畫。
- 使用既有 Template Framework 渲染 Markdown 投影片來源。
- 產生決定性、可測試、可版本控制的文字 artifact。
- 回傳標準 `GenerationResult`。

Slides Generator **不負責**：

- 直接產生 PowerPoint、PDF 或 HTML。
- 實作 presentation rendering engine。
- 執行外部轉檔工具。
- 決定簡報播放程式。
- 修改既有 Generator lifecycle。
- 建立 Slides 專屬 result type。

最終格式轉換將視為獨立 renderer capability，未來可透過 renderer contract 或 plugin 擴充。

## Canonical Artifact

第一版 canonical output 為：

```text
slides.md
```

Markdown 是 OPL Slides Generator 的來源契約，而非對所有 presentation backend 的永久限制。

選擇 Markdown 的理由：

- 是純文字，可直接進入 Git diff 與 code review。
- 易於 golden-file testing。
- 與既有 Template Framework 相容。
- 不需要第一版就引入二進位文件函式庫。
- Renderer 可在後續轉換成 `.pptx`、PDF 或 HTML。
- 內容生成與視覺 rendering 可以保持分離。
- Plugin 可在不修改核心 Generator contract 的情況下提供其他 renderer。

第一版不承諾特定第三方 Markdown slide dialect。若未來需要 Marp、Reveal.js 或其他 dialect，應以新的明確 contract 或 renderer profile 定義，不應暗中依賴未記錄的語法。

## Generator Identity

`SlidesGenerator` 的 canonical generator name 為：

```text
slides
```

CLI 與 Registry 應使用相同名稱。

Generator 名稱屬於公開契約，變更需視為相容性變更。

## Input Contract

Slides Generator 使用既有 `GenerateRequest`，不得建立 `SlidesGenerateRequest` 等平行 request type。

Slides-specific 資料放在 `GenerateRequest.values`。

第一版要求下列 keys：

```text
title
slides
```

建議輸入概念如下：

```python
GenerateRequest(
    target=...,
    values={
        "title": "Week 01: Reactive Programming",
        "slides": (
            {
                "title": "Learning Objectives",
                "content": (
                    "Understand reactive systems.",
                    "Explain asynchronous data flows.",
                ),
            },
            {
                "title": "Core Concepts",
                "content": (
                    "Streams",
                    "Backpressure",
                    "Non-blocking execution",
                ),
            },
        ),
    },
    options=...,
)
```

### `title`

`title`：

- 必須存在。
- 必須為 `str`。
- `strip()` 後不可為空字串。

### `slides`

`slides`：

- 必須存在。
- 必須是有順序的非字串 sequence。
- 至少包含一張 slide。
- 每個元素必須是 mapping。
- 保留輸入順序。

每一張 slide 第一版要求：

```text
title
content
```

### Slide `title`

每張 slide 的 `title`：

- 必須存在。
- 必須為 `str`。
- `strip()` 後不可為空字串。

### Slide `content`

每張 slide 的 `content`：

- 必須存在。
- 必須是有順序的非字串 sequence。
- 可以是空 sequence。
- 每一項必須為非空 `str`。

空的 `content` 可支援 section divider 或 title-only slide。

第一版不在 core contract 中定義：

- 圖片
- Speaker notes
- Animation
- Theme
- Transition
- Layout identifiers
- Embedded media
- Arbitrary HTML
- Binary attachments

這些能力應在有明確需求時透過後續 ADR 擴充。

## Immutability

Slides Generator 不得修改：

- `GenerateRequest`
- `request.values`
- `slides` sequence
- individual slide mappings
- `RuntimeOptions`

Validation 與 Planning 應視輸入為唯讀資料。

測試必須驗證 Generator 不會就地正規化或寫回 request mapping。

## Validation Contract

`validate()` 必須在任何 filesystem mutation 之前完成。

驗證至少涵蓋：

- `title` 是否存在。
- `title` 是否為非空字串。
- `slides` 是否存在。
- `slides` 是否為合法 sequence。
- `slides` 不得是單一字串或 bytes。
- 至少有一張 slide。
- 每一張 slide 必須是 mapping。
- 每張 slide 必須有合法 `title`。
- 每張 slide 必須有 `content`。
- `content` 必須是合法 sequence。
- `content` 不得是單一字串或 bytes。
- `content` 每一項必須為非空字串。
- output target 必須符合既有 Generator / filesystem contract。

驗證失敗必須使用既有 Generator validation error contract，不建立 Slides 專屬例外階層，除非後續架構需求證明有必要。

Validation 不應：

- 建立目錄。
- 寫入檔案。
- 渲染 Template。
- 自動修正錯誤輸入。
- 靜默移除非法 slide。

## Planning Contract

`plan()` 必須建立標準 `GenerationPlan`，不得直接寫入檔案。

第一版計畫包含單一主要輸出：

```text
slides.md
```

概念：

```text
SlidesGenerator.plan(request)
    ↓
validate request
    ↓
build template context
    ↓
plan slides.md
    ↓
GenerationPlan
```

Generation Plan 必須：

- 使用既有 plan model。
- 保持 deterministic ordering。
- 不執行 filesystem mutation。
- 不建立 Slides-specific plan type。
- 可由 dry-run 與正式執行共享。

若既有 plan contract 需要 template path、destination 與 context，Slides Generator 應依既有結構提供，而不是新增特例。

## Template Contract

第一版新增 canonical template：

```text
templates/slides/slides.md.j2
```

Template Context 至少提供：

```text
title
slides
```

Template 只負責 presentation source 的文字渲染，不負責：

- filesystem policy
- output root resolution
- CLI behavior
- PowerPoint rendering
- PDF conversion
- Plugin discovery

模板輸出應：

- 使用 UTF-8。
- 保持 deterministic。
- 不插入目前時間。
- 不插入隨機 ID。
- 不依賴執行機器的絕對路徑。
- 在相同輸入下產生相同內容。

## Markdown Structure

第一版 canonical source 建議使用簡單、backend-neutral 的 Markdown：

```markdown
# Week 01: Reactive Programming

---

## Learning Objectives

- Understand reactive systems.
- Explain asynchronous data flows.

---

## Core Concepts

- Streams
- Backpressure
- Non-blocking execution
```

分隔符號與標題層級構成第一版 template behavior，但核心 contract 重點是可決定性產生 Markdown artifact，而不是承諾某個第三方 renderer 的完整語法。

若未來 renderer 需要額外 front matter 或 metadata，應透過明確 profile 或 renderer-specific layer 加入。

## Output Contract

Slides Generator 第一版輸出：

```text
<target>/slides.md
```

不得：

- 寫出 `.pptx`。
- 額外建立未出現在 plan 的檔案。
- 在使用者未授權時覆寫既有 artifact。
- 直接寫入 target 之外的位置。

既有 overwrite、dry-run、path safety 與 result semantics 均應沿用 Generator Framework 的共享 contract。

## Dry-Run Semantics

當 `RuntimeOptions` 表示 dry-run 時，Slides Generator 必須：

- 完成 validation。
- 完成 plan。
- 回報預計產生的 `slides.md`。
- 不建立目錄。
- 不寫入檔案。
- 不修改既有檔案。

Dry-run 與正式執行必須共享相同的 planning logic，以避免兩套行為漂移。

## Execution Contract

`generate()` 必須遵循既有 Generator Execution Contract。

Slides Generator 不應自行重新實作 canonical lifecycle。

概念：

```text
validate
  ↓
plan
  ↓
execute shared generation path
  ↓
GenerationResult
```

所有成功結果使用共享 `GenerationResult`。

不得新增：

```text
SlidesGenerationResult
```

或任何等價的 generator-specific result type。

## Determinism and Idempotency

相同的 request、template 與 runtime options 必須產生相同 plan 與相同 Markdown content。

第一版不得在 artifact 中自動加入：

- Current timestamp
- Random UUID
- Machine hostname
- Absolute local path
- Environment-specific value

若既有 overwrite policy 不允許重複執行覆寫，第二次執行可依共享 contract 產生 conflict；這不違反 deterministic generation。

Idempotent overwrite/update 行為應由共享 filesystem policy 決定，而非 Slides Generator 自行定義。

## Renderer Boundary

Presentation rendering 是 Slides Generator 之外的能力。

架構邊界：

```text
Courseware / Request
        ↓
SlidesGenerator
        ↓
Canonical Markdown Artifact
        ↓
Renderer Contract (future)
   ┌────┼────┐
   ↓    ↓    ↓
 PPTX  PDF  HTML
```

未來 renderer 應：

- 接受 canonical slide source 或明確 slide model。
- 不改變 Generator lifecycle。
- 可由 plugin 提供。
- 與 core Slides Generator 解耦。
- 擁有自己的 dependency、error 與 testing contract。

若未來證明 structured slide model 比 Markdown 更適合作為 renderer boundary，可新增 ADR 調整，但不得在本 ADR 未經記錄的情況下直接讓 core Generator 依賴 PowerPoint library。

## CLI Integration Boundary

本 ADR 定義 generator contract，但不在 design PR 直接修改 CLI。

後續 integration PR 應：

- 將 `slides` 註冊到既有 generator registry / CLI composition。
- 讓 `opl list` 可觀察到 `slides`。
- 使用現有 CLI request construction path。
- 不在 CLI 重新實作 Slides validation。
- 不在 CLI 直接渲染 Markdown。
- 不在 CLI 直接寫入檔案。

具體 CLI argument surface 應優先與既有 Lab、Quiz、Assignment integration pattern 一致。

## Plugin Compatibility

Slides Generator 必須是正常的 Generator Framework participant。

因此：

- 使用公開 Generator contract。
- 不依賴 private plugin loader internals。
- 不需要 Slides-specific registry。
- 第三方 plugin 未來可以提供其他 generator 或 renderer。
- Renderer extension 不應要求修改 core registry semantics。

若 renderer 未來成為正式 Plugin SDK 能力，應另立 ADR 定義 public renderer contract。

## Error Behavior

Slides Generator 使用既有 exception hierarchy 與 validation contract。

錯誤必須：

- 在最接近來源的位置辨識。
- 保留既有 exception chaining 規則。
- 不捕捉所有 `Exception` 並改寫成模糊 Slides error。
- 不依賴錯誤訊息字串作控制流程。
- 不自行呼叫 `sys.exit()`。

主要 validation error 應指出具體欄位或 slide index，使測試與使用者能辨識失敗位置。

例如概念訊息：

```text
slides[1].title must be a non-empty string
```

完整文字不視為穩定 public API；Exception type 與 shared contract 才是主要程式契約。

## Public API

本 ADR 不新增新的頂層 SDK public symbols，除非後續 implementation review 判定 `SlidesGenerator` 應依既有 built-in generator export policy 公開。

若需要修改：

```text
generator/sdk/
generator/generators/__init__.py
```

必須同步更新 public export tests。

任何新 public symbol 都必須：

- 有明確用途。
- 有測試。
- 有文件。
- 評估相容性。

## Alternatives Considered

### Alternative A: Direct `.pptx` generation

拒絕作為第一版。

優點：

- 使用者直接取得 PowerPoint。
- 不需要額外 renderer。

缺點：

- Generator 直接依賴特定 binary document library。
- 二進位檔難以 Git review。
- Contract tests 更容易耦合實作細節。
- Theme、layout、media 等能力會快速膨脹 core scope。
- 未來 PDF / HTML 需要另一套平行生成邏輯。
- Plugin extensibility 較差。

### Alternative B: Structured slide domain model only

考慮但暫不採用為第一版 canonical artifact。

優點：

- Renderer-neutral。
- 型別契約更強。
- 有利多 backend rendering。

缺點：

- 需要先設計新的 Slide、Deck、Block domain hierarchy。
- 在目前需求下增加額外 public model surface。
- 會延長 Step 5.6 並讓 vertical slice 超出既有 Generator pattern。

若未來 renderer 數量與複雜度提升，可另立 ADR 引入正式 slide domain model。

### Alternative C: Renderer-specific Markdown such as Marp

暫不作為 core contract。

優點：

- 可快速取得 HTML / PDF / PPTX toolchain。
- 生態成熟。

缺點：

- 核心 artifact 會被特定第三方語法綁定。
- Renderer dependency 進入 core contract。
- 未來替換 backend 可能造成 migration burden。

可在未來以 renderer plugin 或 profile 支援。

### Alternative D: Reuse Assignment/Quiz generator as generic document generator

拒絕。

Slides 有不同的內容結構與未來 renderer boundary。將其塞入其他 generator 會模糊 domain semantics，也讓 validation contract 變得不清楚。

## Consequences

### Positive

- 延續既有 canonical Generator lifecycle。
- 不新增 generator-specific request/result types。
- 投影片 source 可 Git review。
- 容易做 template golden tests。
- Renderer 與 content generation 解耦。
- 未來可擴充 PPTX / PDF / HTML。
- 第三方 renderer 可透過 Plugin Ecosystem 發展。
- 第一版 implementation scope 小且明確。

### Negative

- 第一版不會直接產生 `.pptx`。
- 使用者若需要最終 presentation format，需要後續 renderer。
- Markdown 與真正 presentation layout 間存在抽象落差。
- 若未來引入 structured slide model，可能需要 migration。

### Risks

- Template 若逐步加入 backend-specific syntax，可能使「backend-neutral」名存實亡。
- `slides` mapping 若無節制擴張，可能形成未正式建模的 ad-hoc schema。
- Renderer API 若過早加入 core，可能破壞目前的低耦合設計。

這些風險應透過 contract tests、ADR review 與後續 renderer ADR 控制。

## Migration Plan

本功能為新增能力，不需要既有資料 migration。

導入順序：

1. **Design PR**
   - 建立本 ADR。
   - 更新 ADR index。
2. **Contract Test PR**
   - 新增 Slides Generator contract tests。
   - 以尚未實作的 production API 驅動 contract。
3. **Implementation PR**
   - 新增 `SlidesGenerator`。
   - 新增 `templates/slides/slides.md.j2`。
   - 通過 contract 與 template tests。
4. **Integration PR**
   - 整合 Registry / CLI。
   - 新增 integration tests。
5. **Acceptance PR**
   - 將 ADR 狀態改為 `Accepted`。
   - 同步 architecture、roadmap、history、changelog 與 milestone 文件。

## Test Strategy

測試必須依 OPL 的 Testing First 原則分層。

### Contract Tests

建議新增：

```text
tests/generators/test_slides_generator_contract.py
```

至少驗證：

- Generator name 為 `slides`。
- 使用共享 `GenerateRequest`。
- 不新增 Slides-specific request type。
- 不新增 Slides-specific result type。
- 合法 request 通過 validation。
- 缺少 `title` 被拒絕。
- 空白 `title` 被拒絕。
- 缺少 `slides` 被拒絕。
- `slides=None` 被拒絕。
- `slides` 為 string / bytes 被拒絕。
- 空 slides sequence 被拒絕。
- slide 非 mapping 被拒絕。
- slide 缺少 `title` 被拒絕。
- slide title 非字串或空白被拒絕。
- slide 缺少 `content` 被拒絕。
- content 非 sequence 被拒絕。
- content 為 string / bytes 被拒絕。
- content item 非字串被拒絕。
- content item 空白被拒絕。
- title-only slide 可使用空 content。
- slide order 被保留。
- request 不被修改。
- plan 為 deterministic。
- plan 不做 filesystem mutation。

### Template Tests

更新既有 template rendering tests，至少驗證：

```text
templates/slides/slides.md.j2
```

可被發現並成功渲染。

Golden expectation 至少包含：

```markdown
# Week 01: Reactive Programming
```

以及 slide separator 與 slide heading。

### Generator Integration Tests

建議新增：

```text
tests/generators/test_slides_generator_integration.py
```

驗證：

- 實際產生 `slides.md`。
- UTF-8 內容正確。
- Slide order 正確。
- Dry-run 不寫入。
- Existing target behavior 符合 shared contract。
- 回傳標準 `GenerationResult`。

### CLI Integration Tests

建議新增：

```text
tests/integration/test_slides_cli.py
```

驗證：

- `slides` 可透過 CLI 路徑執行。
- `opl list` 包含 `slides`。
- 成功輸出符合既有 CLI semantics。
- Validation error 走既有錯誤路徑。
- Dry-run semantics 一致。

### Regression Tests

不得破壞：

- bootstrap
- course
- week
- lab
- quiz
- assignment
- plugin SDK
- public exports
- template tests

每個 implementation / integration PR 都應執行完整測試套件。

## Documentation Changes

Design PR：

- 新增 `docs/adr/0018-slides-generator-contract.md`。
- 更新 `docs/adr/README.md`，加入 ADR 0018，狀態為 `Proposed`。

Contract / implementation / integration 階段視需要同步：

- `docs/architecture/open-courseware-platform.md`
- Generator architecture / reference documents
- CLI reference
- Template reference

Acceptance PR 必須同步：

- 本 ADR：`Proposed` → `Accepted`
- `docs/adr/README.md`
- `docs/roadmap.md`
- `docs/HISTORY.md`
- `CHANGELOG.md`
- Milestone 5 acceptance / progress documentation（若存在）

文件不可在 production capability 尚未存在時把 Proposed 行為描述成 Implemented。

## Automation

每個 Step 5.6 PR 至少執行：

```powershell
git diff --check
pre-commit run --all-files
python -m pytest
```

針對 contract test PR 可先執行：

```powershell
python -m pytest tests\generators	est_slides_generator_contract.py -v --no-cov
```

Implementation 階段應增加 template 與 generator-specific test commands。

Integration 階段應增加：

```powershell
python -m pytest tests\integration -v --no-cov
```

GitHub CI 必須通過後才可 merge。

## Rollback Plan

Design PR 只新增文件，因此 rollback 可直接 revert 該 PR。

若後續 contract 或 implementation 證明此設計不可行：

- 在 ADR 尚為 `Proposed` 時，可透過後續 design PR 修訂。
- 一旦 ADR 轉為 `Accepted`，架構方向若需改變，應建立新的 ADR 並將本 ADR標示為 `Superseded`。
- 不應直接改寫已接受 ADR 的歷史決策。

若 Slides Generator implementation 需要回滾：

- 移除 CLI / registry integration。
- 移除 built-in implementation 與 template。
- 保留 ADR 與歷史紀錄。
- 確保其他 generators 與 Plugin SDK 不受影響。

## Code Review Checklist

### Architecture

- [ ] Slides Generator 遵循既有 canonical Generator lifecycle。
- [ ] 使用共享 `GenerateRequest`。
- [ ] 使用共享 `GenerationPlan`。
- [ ] 使用共享 `GenerationResult`。
- [ ] 沒有 Slides-specific result type。
- [ ] Generator 與 renderer responsibility 已分離。
- [ ] 第一版沒有直接依賴 PowerPoint / PDF library。
- [ ] Renderer 擴充方向不破壞 Plugin SDK 邊界。
- [ ] 沒有新增不必要的 public API。

### Validation

- [ ] `title` contract 有測試。
- [ ] `slides` contract 有測試。
- [ ] 每張 slide 的 `title` 有測試。
- [ ] 每張 slide 的 `content` 有測試。
- [ ] string / bytes 不被誤當 sequence。
- [ ] 空 slides 被拒絕。
- [ ] title-only slide 行為明確。
- [ ] Validation 不執行 filesystem mutation。
- [ ] Request 不會被修改。
- [ ] 錯誤使用共享 validation contract。

### Planning and Generation

- [ ] `plan()` 不直接寫入檔案。
- [ ] `slides.md` destination 明確。
- [ ] Plan ordering deterministic。
- [ ] 相同輸入產生相同 artifact。
- [ ] Dry-run 與正式 execution 共用 planning logic。
- [ ] Output 遵循既有 overwrite/path safety contract。
- [ ] 沒有建立 plan 之外的副作用。

### Template

- [ ] `templates/slides/slides.md.j2` 可被 Template Framework 發現。
- [ ] Template context 只包含必要資料。
- [ ] Template 不依賴 local absolute path。
- [ ] Template 不插入 timestamp / random data。
- [ ] UTF-8 與 newline behavior 符合 repository policy。
- [ ] Template test 已更新。
- [ ] Markdown artifact 可進行 golden review。

### Tests

- [ ] Contract tests 已新增。
- [ ] Validation edge cases 完整。
- [ ] Immutability 有測試。
- [ ] Determinism 有測試。
- [ ] Generator integration tests 已新增。
- [ ] CLI integration tests 已新增。
- [ ] Dry-run 有測試。
- [ ] Existing-output behavior 有測試。
- [ ] 既有 generators regression tests 通過。
- [ ] Plugin SDK tests 通過。

### Documentation

- [ ] ADR 0018 已加入索引。
- [ ] Design 階段狀態為 `Proposed`。
- [ ] Architecture 文件沒有把尚未實作能力標為 Implemented。
- [ ] Acceptance PR 將 ADR 改為 `Accepted`。
- [ ] Roadmap / HISTORY / CHANGELOG 於適當階段同步。
- [ ] Renderer future work 與現有 core capability 清楚區分。

### Automation

- [ ] `git diff --check` 通過。
- [ ] `pre-commit run --all-files` 通過。
- [ ] `python -m pytest` 通過。
- [ ] GitHub CI 通過。
- [ ] PR scope 僅包含當前 vertical-slice 階段需要的變更。

## Decision Summary

Step 5.6 將以 `SlidesGenerator` 建立 OPL 的第一個 presentation-source generator。

第一版：

```text
GenerateRequest
      ↓
SlidesGenerator
      ↓
GenerationPlan
      ↓
templates/slides/slides.md.j2
      ↓
slides.md
```

`.pptx`、PDF 與 HTML 不屬於第一版 Slides Generator 的核心責任，而是未來獨立 renderer capability。

此決策保持 OPL 的 Design First、Documentation First、Automation First 與既有 Generator Contract，並為後續 presentation ecosystem 保留可擴充邊界。
