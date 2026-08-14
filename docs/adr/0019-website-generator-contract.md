# ADR 0019: Website Generator Contract

- **Status:** Proposed
- **Date:** 2026-08-14
- **Decision owners:** OpenProjectLab maintainers
- **Scope:** Open Courseware Platform / Generator Framework
- **Related ADRs:** 0005, 0006, 0007, 0008, 0014, 0015, 0016, 0017, 0018

## Context

OpenProjectLab（OPL）在 Milestone 5 已完成 Course/Week domain foundation，以及
Lab、Quiz、Assignment、Slides Generator vertical slices。下一個 capability
是 Website Generator：將明確、已驗證的 courseware publishing intent 投影成
deterministic static website。

Open Courseware Platform architecture 已將 Website 定義為 publishing
projection，而不是 Course domain owner：

```text
Course / Week / Materials
        ↓
Website Projection
        ↓
Navigation + Pages + Assets
        ↓
Static Website
```

因此 Website Generator 必須延續既有
`GenerateRequest → validate_request → plan → execute → GenerationResult`
canonical lifecycle，不得同時承擔 composition、hosting、deployment、
authentication、analytics、CMS 或 remote publishing。

本 ADR 固定第一版 Website Generator 的 identity、request contract、
validation、page/path semantics、GenerationPlan、artifact layout、template、
manifest、CLI、security、tests、documentation、automation 與 rollback boundary。

## Decision Drivers

1. 保護 Milestone 3 canonical Generator lifecycle。
2. 保護 Milestone 4 Plugin SDK/runtime boundary。
3. 延續 Milestone 5 Domain / Generator / Template / Artifact 分離。
4. Website 是 publishing projection，不是 Course domain owner。
5. 第一版輸出必須 deterministic、可測試、可 Git review。
6. 核心 CI 不依賴 network、browser、hosting provider 或 external build tool。
7. Validation / planning 必須在 filesystem mutation 前完成。
8. 不建立 Website-specific request/result hierarchy。
9. 不把 static-site framework 或 deployment vendor 寫死進 core contract。
10. 保留後續 Composition Integration、assets、themes、deployment 的擴充空間。

## Decision

OPL 新增 `WebsiteGenerator`，canonical identity：

```text
website
```

遵循：

```text
GenerateRequest
    ↓
validate_request()
    ↓
plan()
    ↓
execute()
    ↓
GenerationResult
```

第一版產生 deterministic UTF-8 static HTML site：

```text
<target>/
└── site/
    ├── index.html
    └── ... additional deterministic pages
```

不要求 Node.js、npm、static-site framework、browser runtime 或 network。

## Generator Identity

預期 production implementation：

```text
generator/generators/website_generator.py
```

metadata：

```python
name = "website"
description = "Generate an OpenProjectLab static course website"
```

Website 必須使用共享：

```text
GenerateRequest
RuntimeOptions
GenerationOperation
GenerationPlan
GenerationResult
GeneratorValidationError
```

不得建立：

```text
WebsiteGenerateRequest
WebsiteGenerationPlan
WebsiteGenerationResult
```

## Responsibility Boundary

Website Generator 負責：

- website-specific request validation
- deterministic planning
- template selection/context
- static HTML artifact generation
- dry-run / overwrite / filesystem semantics
- manifest integration
- standard `GenerationResult`

Website Generator不負責：

- Course / Week domain ownership
- repository crawling
- courseware composition
- 修改 Lab / Quiz / Assignment / Slides artifacts
- hosting / deployment / DNS / TLS
- authentication / authorization
- analytics / CMS / database
- LMS integration
- remote publishing
- network requests
- package installation
- JavaScript/CSS build pipeline
- Git operations
- AI content generation
- Plugin discovery/loading

## Projection Boundary

```text
Validated Publishing Intent
        ↓
WebsiteGenerator
        ↓
GenerationPlan
        ↓
Website Templates
        ↓
Static HTML Artifacts
```

Generated HTML 是 derived artifact，不得反向成為 Course domain source of
truth。

## Minimum Request Contract

第一版 `GenerateRequest.values`：

```python
{
    "title": "Modern Java in Action",
    "pages": (
        {
            "path": "index.html",
            "title": "Home",
            "content": "Welcome to the course.",
        },
    ),
}
```

Required：

```text
title
pages
```

Optional integration values 可包含：

```text
course_name
record_manifest
template_name
output_directory
```

第一版不要求完整 `Course` / `Week` object，避免在 Composition Integration
前過早建立新的 serialization/public API。

## Site Title Contract

`title`：

- 必須是 `str`
- trim 後不可為空
- 不得由 filesystem path 隱式推導
- validation 不得修改 request
- normalized value 可進入 operation context

非法：

```text
None
True
42
""
"   "
```

## Pages Contract

`pages` 必須是 ordered、non-empty sequence。

每個 page 是 mapping：

```python
{
    "path": "index.html",
    "title": "Home",
    "content": "Welcome."
}
```

Required page fields：

```text
path
title
content
```

規則：

- `str` / `bytes` / `bytearray` 不可被誤認為 pages sequence
- mapping 本身不可被誤認為 pages sequence
- page 必須為 mapping
- page ordering 必須保留
- nested caller-owned input 不得被修改
- 第一版不建立 public `WebsitePage` domain class

## Page Path Contract

`page["path"]` 是相對於 canonical website root 的 relative HTML path。

合法：

```text
index.html
about.html
weeks/week-01.html
materials/lab-01.html
```

要求：

- non-empty `str`
- relative path
- `.html` suffix
- 不得 absolute
- 不得 path traversal
- normalization 後不得 escape site root
- normalized paths 必須 unique

非法：

```text
../index.html
../../outside.html
C:\temp\index.html
/temp/index.html
index.md
""
```

Duplicate path 必須在任何 filesystem mutation 前被拒絕；不得 last-write-wins、
first-write-wins、silent rename。

## Required Home Page

第一版 `pages` 必須包含：

```text
index.html
```

理由是提供 deterministic static-site entry point，且避免第一版引入 homepage
selection option。

## Page Title Contract

每個 page `title`：

- required
- 必須是 `str`
- trim 後不可為空
- 是 display metadata，不是 identity
- 不得用 title 推導 destination

Page identity 由 explicit `path` 決定。

## Page Content Contract

`content`：

- key 必須存在
- 必須是 `str`
- 可包含 Unicode / multiline
- 第一版允許空字串
- 不執行 Markdown-to-HTML conversion
- 不執行 remote fetch
- 不 eval
- 不將 content 當 Jinja template source

若未來需要 Markdown rendering 或 sanitization contract，另以 ADR 固定。

## Canonical Output Root

預設：

```text
<target>/site/
```

例如：

```text
index.html
→ <target>/site/index.html

weeks/week-01.html
→ <target>/site/weeks/week-01.html
```

`site/` 將 derived Website artifacts 與 author-owned courseware source 分離。

## Deterministic Ordering

`GenerationPlan.operations` 採 `pages` input order。

不得依賴：

- filesystem enumeration
- hash iteration accident
- timestamp
- random value
- network
- locale-dependent sorting

相同 normalized request 必須得到等價 plan。

## Canonical Template

第一版 canonical template：

```text
templates/website/page.html.j2
```

所有 pages 共享此 template。

Canonical context 至少：

```python
{
    "site_title": "...",
    "page": {
        "path": "...",
        "title": "...",
        "content": "...",
    },
    "navigation": (
        {"path": "index.html", "title": "Home"},
        ...
    ),
}
```

Navigation 保留 pages order。

Template 不負責 validation、duplicate detection、path safety、filesystem、
registry、network、domain identity 或 deployment。

## HTML Contract

第一版 artifact 是 UTF-8 HTML text，至少具有：

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>...</title>
</head>
<body>
  ...
</body>
</html>
```

ADR 不固定完整 visual design。Contract tests 關注 deterministic structure、
title、content、navigation、UTF-8，以及沒有 timestamp/random metadata。

## Navigation Contract

第一版 navigation 由 validated pages deterministic 投影：

```python
(
    {"path": "index.html", "title": "Home"},
    {"path": "weeks/week-01.html", "title": "Week 01"},
)
```

Ordering 與 pages 一致。

第一版不建立完整 routing engine、base URL、pretty URL 或 deployment subpath
contract；這些留待未來 decision。

## Immutability

Validation / planning 可建立新的 normalized context，但不得修改：

```text
request.values
pages sequence
page mappings
nested caller-owned values
```

Contract tests 必須驗證 request immutability。

## Validation and Planning Purity

`validate_request()` 不得：

- 寫 filesystem
- 建 directory
- 寫 manifest
- render template
- 呼叫 network
- deployment

`plan()` 不得：

- 寫 filesystem
- 建 directory
- 寫 manifest
- deployment

Planning 只建立 deterministic `GenerationPlan`。

## Generation Plan

每個 page 對應一個 `GenerationOperation`：

```python
GenerationPlan(
    generator_name="website",
    operations=(
        GenerationOperation(
            template_name="website/page.html.j2",
            destination=target / "site" / "index.html",
            context={...},
            write_policy=...,
        ),
        ...
    ),
)
```

不得建立 Website-specific operation type。

## Execution Contract

```text
GenerationOperation
        ↓
TemplateRenderer
        ↓
rendered HTML
        ↓
FileSystem.write_text()
        ↓
WriteResult
```

Execution 沿用既有 filesystem safety / overwrite / dry-run contract。

## Dry-Run Contract

`RuntimeOptions.dry_run=True`：

- 執行完整 validation/planning
- 不建立 `<target>/site`
- 不寫 HTML
- 不 persistent 更新 manifest
- `GenerationResult.dry_run == True`

Dry-run 與 real execution 共用 planning logic。

## Overwrite Contract

沿用：

```text
RuntimeOptions.overwrite
GenerationOperation.write_policy
FileSystem
```

不得 silent overwrite、自動 rename 或建立 Website-specific backup policy。

## Manifest Contract

沿用既有 `GenerationManifest` schema。

每個 page 可記錄：

```text
generator: website
template: website/page.html.j2
```

metadata 只放穩定必要資料，例如：

```python
{
    "site_title": "...",
    "page_title": "...",
}
```

不得寫入 timestamp、random ID、host absolute path、deployment URL、secret。

`record_manifest=False` 不得建立/修改 manifest；dry-run 不 persistent 更新。

## Template Manifest

新增：

```text
templates/website/page.html.j2
```

時必須同步 repository template manifest 與 template contract tests。

不得透過關閉 `test_no_unregistered_jinja_templates` 規避 registration contract。

## Assets Contract

第一版不建立 asset pipeline：

```text
CSS bundling
JavaScript bundling
image optimization
font packaging
fingerprinting
minification
Sass/Less
npm
webpack/vite
```

若未來加入 assets，必須另行固定 source ownership、destination、overwrite、
manifest、hashing 與 deterministic semantics。

## Security Boundary

Website Generator 處理會進入 HTML 的 authored content，因此 implementation
必須以實際 Template Framework 行為確認 escaping policy。

第一版不得：

- eval authored content
- 將 content 當 template source
- 執行 authored JavaScript
- fetch remote scripts
- 注入 secrets
- 執行 shell/deployment hooks

本 ADR不宣稱第一版具有完整 untrusted-content sanitization guarantee。

## No Repository Crawling

第一版不自行：

```text
scan weeks/
scan lab/
scan quiz/
scan assignment/
scan slides/
parse arbitrary generated artifacts
```

Caller 明確提供 `pages` publishing intent。

這避免 filesystem layout 成為隱性 domain API，也避免 Website Generator
侵入下一階段 Composition Integration。

## Composition Compatibility

未來可由 composition layer：

```text
Course
  ↓
Weeks / Materials
  ↓
Composition
  ↓
Website pages publishing intent
  ↓
GenerateRequest(generator_name="website", ...)
  ↓
WebsiteGenerator
```

Composition 不得呼叫 WebsiteGenerator private methods。本 ADR 不提前建立
Courseware Orchestrator。

## CLI Contract

Integration 階段新增：

```text
opl website <project_slug> --title <SITE_TITLE> --pages-file <FILE>
```

`--pages-file` 使用 UTF-8 JSON：

```json
[
  {
    "path": "index.html",
    "title": "Home",
    "content": "Welcome."
  },
  {
    "path": "weeks/week-01.html",
    "title": "Week 01",
    "content": "Introduction."
  }
]
```

CLI 只負責 parsing、JSON loading、建立 `GenerateRequest` /
`RuntimeOptions`、呼叫 generator、呈現 shared result/error。

CLI 不重做 page validation、不 render HTML、不直接寫 files/manifest。

## CLI Shared Options

沿用：

```text
--template-root
--output-root
--dry-run
--force
--no-manifest
```

不得建立 Website-specific overwrite/dry-run semantics。

## Built-in Listing

Integration 完成後：

```text
opl list
opl --list
```

均包含：

```text
website
```

Design/Contract 階段不得把 runtime capability 描述成已存在。

## Error Contract

Website validation 使用：

```text
GeneratorValidationError
```

CLI 使用既有 error translation。

第一版不建立 `WebsiteValidationError`、`WebsiteCLIError`、
`WebsitePathError`。

## Failure Atomicity

Website 是 multi-operation Generator。本 ADR不宣稱跨多個 HTML writes
具 transaction atomicity，除非既有 shared execution/filesystem contract
已提供此保證。

因此：

- validation/planning 必須先完整完成
- duplicate/path errors 必須在 write 前拒絕
- execution I/O failure 依 shared semantics 傳播
- 不在 WebsiteGenerator 私自實作 transaction rollback

若需要 multi-artifact atomic generation，應建立 shared execution/filesystem
ADR，而不是 Website 特例。

## Determinism Contract

相同 request、template、runtime options 應產生相同：

- operation count/order
- destinations
- template names
- normalized contexts
- rendered HTML semantic output
- manifest semantic records

禁止 canonical output 自動加入：

```text
current date/time
random UUID
hostname
absolute local path
environment-specific deployment URL
```

## Encoding and Newlines

Artifacts 使用 UTF-8；newline behavior 沿用 repository /
TemplateRenderer / FileSystem policy，不建立 platform-specific 特例。

## Public SDK Boundary

ADR 0019 不擴張 `generator.sdk`。

若未來 Website publishing intent 成為 third-party public contract，必須另行：

1. 定義穩定 public model。
2. 增加 SDK export tests。
3. 更新 Plugin authoring docs。
4. 接受 compatibility commitment。

## Alternatives Considered

### A. 直接綁定 static-site framework

拒絕第一版採用：會引入額外 runtime/dependency、framework conventions 與
跨平台 CI complexity。

### B. 只產生 Markdown

拒絕：Website architecture 已定義 static Website projection；HTML 是最小而
完整的 publishing artifact，且不需要 hosting。

### C. 自動掃描 course repository

拒絕：會讓 filesystem layout 變成隱性 domain contract，並混入 composition
responsibility。

### D. 第一版直接 deployment

拒絕：hosting、credentials、provider API 不屬於 Milestone 5 core。

### E. 建立 Website/Page public domain hierarchy

拒絕：第一版不需要新的 public class hierarchy 即可固定 Generator contract，
避免 premature abstraction。

## Consequences

### Positive

- 遵循既有 Generator lifecycle。
- Static output deterministic、可測試、可 Git review。
- 不依賴 network/hosting provider。
- Multi-page output 由 canonical `GenerationPlan` 表達。
- Composition 與 publishing projection 分離。
- 保留 themes/assets/deployment 的未來擴充空間。
- CLI 與其他 built-in generators 一致。

### Trade-offs

- 第一版 pages 由 caller 明確提供。
- 不自動把 Course/Week/Materials 組成網站。
- 不提供完整 static-site framework。
- 不提供 asset pipeline / Markdown renderer / deployment。
- 不新增 Website-specific transaction rollback。

## Testing Strategy

Website vertical slice：

```text
Design
  ↓
Contract Tests
  ↓
Minimum Implementation
  ↓
Integration
  ↓
Acceptance
```

### Contract Tests

新增：

```text
tests/generators/test_website_generator_contract.py
```

至少驗證：

- `name == "website"` 與 wrong identity
- title required/type/empty/normalization
- pages required、non-empty ordered sequence
- string/bytes/mapping 不被誤當 pages sequence
- page 必須 mapping
- path required/type/relative/`.html`
- traversal/absolute path rejection
- duplicate normalized path rejection
- `index.html` required
- page title required/type/non-empty
- content key required/type/Unicode/multiline/empty-string behavior
- validation/planning 無 filesystem mutation
- one operation per page
- canonical `site/` destinations
- canonical template
- deterministic operation ordering/navigation
- request immutability
- standard `GenerationPlan` / `GenerationResult`
- dry-run / overwrite / manifest-disable semantics

### Template Tests

更新 template tests，至少驗證：

```text
templates/website/page.html.j2
```

可被發現、compile、render，並驗證 `<!doctype html>`、title、content、
navigation。Template manifest 必須同步。

### Generator Integration Tests

新增：

```text
tests/generators/test_website_generator_integration.py
```

驗證：

- `site/index.html`
- multi-page generation
- nested page destination
- UTF-8
- deterministic order/navigation
- manifest
- dry-run
- manifest disabled
- overwrite protection / force
- standard `GenerationResult`

### CLI Integration Tests

新增：

```text
tests/integration/test_website_cli.py
```

驗證：

- `website` command
- `list` / `--list`
- `--pages-file`
- missing/invalid/non-sequence JSON
- shared validation error path
- dry-run
- no-manifest
- overwrite / force

### Regression

不得破壞：

```text
bootstrap
course
week
lab
quiz
assignment
slides
plugin SDK
public exports
template/manifest contracts
CLI integration
```

## Documentation Changes

Design PR：

- 新增 `docs/adr/0019-website-generator-contract.md`
- 更新 `docs/adr/README.md`
- ADR 0019 status 為 `Proposed`

Contract / implementation / integration 視需要同步：

- `docs/architecture/open-courseware-platform.md`
- Generator / CLI reference
- Template reference
- Courseware authoring docs

Acceptance PR 必須同步：

- ADR 0019：`Proposed` → `Accepted`
- `docs/adr/README.md`
- `docs/architecture/open-courseware-platform.md`
- `docs/roadmap.md`
- `docs/HISTORY.md`
- `CHANGELOG.md`
- Milestone 5 acceptance/progress docs（若存在）

在 production capability 尚未存在前不得把 Website 標為 Implemented。

## Automation

每個 Website vertical-slice PR 至少：

```powershell
git diff --check
pre-commit run --all-files
python -m pytest
```

Contract PR 可先：

```powershell
python -m pytest tests\generators\test_website_generator_contract.py -v --no-cov
```

Implementation 階段：

```powershell
python -m pytest `
  tests\generators\test_website_generator_contract.py `
  tests\template `
  -v --no-cov
```

Integration 階段：

```powershell
python -m pytest `
  tests\generators\test_website_generator_integration.py `
  tests\integration\test_website_cli.py `
  -v --no-cov
```

最後仍執行完整 pre-commit、pytest 與 GitHub CI。

## Migration Plan

### Phase 1 — Design

```text
docs/adr/0019-website-generator-contract.md
docs/adr/README.md
```

### Phase 2 — Contract Tests

```text
tests/generators/test_website_generator_contract.py
```

固定 identity、validation、page/path、homepage、planning、immutability 與
shared lifecycle。

### Phase 3 — Minimum Implementation

```text
generator/generators/website_generator.py
templates/website/page.html.j2
templates/manifest.yaml
tests/template/...
```

### Phase 4 — Integration

```text
generator/cli/main.py
tests/generators/test_website_generator_integration.py
tests/integration/test_website_cli.py
```

加入 `website`、`--pages-file`、list、dry-run、force、manifest integration。

### Phase 5 — Acceptance

同步 ADR index、architecture、roadmap、HISTORY、CHANGELOG，執行完整
regression / CI，完成 Website vertical slice。

## Rollback Plan

Design PR 可直接 revert。

ADR 尚為 Proposed 時可由後續 design PR 修訂；一旦 Accepted，架構變更應以
新 ADR supersede，不直接改寫歷史決策。

若 implementation 需要回滾：

- 移除 CLI integration
- 移除 built-in Website implementation/template
- 回復 template manifest
- 保留 ADR/HISTORY/CHANGELOG 歷史
- 確保其他 generators 與 Plugin SDK 不受影響

## Code Review Checklist

### Architecture

- [ ] Website 是 publishing projection，不是 Course domain owner。
- [ ] 遵循 canonical Generator lifecycle。
- [ ] 使用共享 request/plan/result contracts。
- [ ] 沒有 Website-specific request/result hierarchy。
- [ ] 沒有重設 Plugin SDK/runtime。
- [ ] 沒有 hosting/deployment responsibility。
- [ ] 沒有 external static-site framework dependency。
- [ ] 沒有 repository crawling/composition responsibility。
- [ ] 沒有不必要 public API expansion。

### Validation

- [ ] title/pages contracts 完整。
- [ ] pages 是 non-empty ordered sequence。
- [ ] string/bytes/mapping 不被誤當 pages sequence。
- [ ] path/title/content validation 完整。
- [ ] duplicate paths 被拒絕。
- [ ] `index.html` requirement 有測試。
- [ ] traversal/absolute path 被拒絕。
- [ ] validation 無 filesystem mutation。
- [ ] request/nested input immutable。
- [ ] 使用 shared validation error。

### Planning / Execution

- [ ] `plan()` 不寫 filesystem。
- [ ] canonical root 為 `<target>/site/`。
- [ ] one operation per page。
- [ ] operation/navigation ordering deterministic。
- [ ] canonical template 固定。
- [ ] dry-run 不建立 site/manifest。
- [ ] overwrite 使用 shared semantics。
- [ ] manifest 使用既有 schema。
- [ ] 回傳 standard `GenerationResult`。
- [ ] 不私自建立 transaction semantics。

### Template / Security

- [ ] `templates/website/page.html.j2` 已註冊。
- [ ] template compile/render tests 通過。
- [ ] context 明確且最小。
- [ ] template 不做 validation/filesystem/network。
- [ ] 不插入 timestamp/random data。
- [ ] authored content 不被 eval/當 template source。
- [ ] HTML escaping policy 由實際 framework 行為確認。
- [ ] 未宣稱不存在的 sanitization guarantee。

### CLI / Tests

- [ ] `website` command 有 integration test。
- [ ] `--pages-file` success/failure tests 完整。
- [ ] `list` / `--list` 包含 website。
- [ ] dry-run/force/no-manifest semantics 一致。
- [ ] Contract/template/generator/CLI tests 完整。
- [ ] Existing generators regression tests 通過。
- [ ] Plugin SDK/public export tests 通過。

### Documentation / Automation

- [ ] ADR 0019 已加入 index，Design status 為 Proposed。
- [ ] Architecture 未提前標示 Website Implemented。
- [ ] Acceptance PR 同步 ADR/architecture/roadmap/HISTORY/CHANGELOG。
- [ ] `git diff --check` 通過。
- [ ] `pre-commit run --all-files` 通過。
- [ ] `python -m pytest` 通過。
- [ ] GitHub CI 通過。
- [ ] PR scope 僅包含當前 vertical-slice 階段。

## Decision Summary

Step 5.7 以 `WebsiteGenerator` 建立 deterministic static Website publishing
projection：

```text
GenerateRequest
      ↓
WebsiteGenerator
      ↓
validate_request()
      ↓
GenerationPlan
      ↓
templates/website/page.html.j2
      ↓
<target>/site/
      ├── index.html
      └── ... deterministic pages
      ↓
GenerationResult
```

核心 contract：

```text
identity             website
required values      title, pages
page identity        explicit relative .html path
home page            index.html
canonical root       <target>/site/
canonical template   website/page.html.j2
output               deterministic UTF-8 static HTML
CLI input            --pages-file JSON
```

第一版明確不包含 hosting、deployment、authentication、analytics、CMS、
database、LMS、remote publishing、repository crawling、Markdown conversion、
asset build pipeline、Node.js/static-site framework 或 AI generation。

此決策延續 OPL 的 Design First、Documentation First、Automation First、
Testing First，以及既有 Generator Framework / Plugin SDK boundaries，並為
後續 Course → Week → Materials → Projections Composition Integration 保留清楚
且可演進的 publishing boundary。
