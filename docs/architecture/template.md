# Template Framework Architecture

Version: 1.0

Status: Draft

Audience:

- Framework Developers
- Generator Developers
- Maintainers

---

# 1. Purpose

Template Framework 提供 OpenProjectLab (OPL) 所有文字與結構化檔案的生成能力。

Framework 的目標並非綁定特定 Template Engine，而是提供一個穩定、可測試、可擴充的抽象層（Abstraction Layer），讓 Generator 專注於內容生成，而非 Template 實作細節。

本文件描述：

- Architecture
- Design Principles
- Core Components
- Dependency Rules
- Rendering Pipeline
- Security Boundary
- Extension Points
- Future Evolution

---

# 2. Goals

Template Framework 應滿足：

- Generator 不直接操作 Template Engine
- Template Engine 可替換
- Template 可重用
- Render 結果可重現（Deterministic）
- Template 可測試
- Context 契約清楚
- Template 與 Business Logic 分離

---

# 3. Non-Goals

Template Framework 不負責：

- CLI Argument Parsing
- Course Business Rules
- Week Business Rules
- Output Path Planning
- File Writing
- Configuration Parsing

上述工作分別由：

- CLI Framework
- Generator Framework
- Filesystem Framework
- Configuration Framework

負責。

---

# 4. High-Level Architecture

```
                  Generator
                      │
                      ▼
              Context Builder
                      │
                      ▼
              Template Framework
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
 Template Resolver          Template Renderer
        │                           │
        └─────────────┬─────────────┘
                      ▼
              Output Validator
                      │
                      ▼
                 Filesystem
```

---

# 5. Design Principles

Template Framework 遵循：

## Single Responsibility

Template 僅負責內容呈現。

Generator 負責：

- 商業邏輯
- Context 建立

Filesystem 負責：

- 寫入
- 建立目錄
- Atomic Write

---

## Dependency Inversion

Generator

↓

Template Framework Interface

↓

Concrete Template Engine

Generator 永遠不依賴：

- Jinja2
- Mustache
- Handlebars

---

## Open / Closed Principle

新增：

- Filter
- Function
- Template Engine

不應修改 Generator。

---

## Deterministic Rendering

相同：

- Template
- Context
- Version

必須得到完全一致輸出。

不得依賴：

- 現在時間
- Random
- Working Directory
- Environment Variables

---

# 6. Core Components

Template Framework 包含：

## Template Resolver

職責：

- Resolve Template Name
- 驗證路徑
- 防止 Path Traversal
- 搜尋 Template

---

## Template Loader

負責：

- UTF-8 Read
- Cache（Future）
- Syntax Loading

---

## Template Renderer

負責：

- Build Environment
- Render
- Exception Translation

---

## Output Validator

負責：

- UTF-8
- LF
- Structured File Validation
- Empty File Detection

---

# 7. Rendering Pipeline

```
Generator

↓

Build Context

↓

Resolve Template

↓

Load Template

↓

Validate Template

↓

Render

↓

Validate Output

↓

Filesystem Write
```

所有 Render Flow 必須遵循此順序。

---

# 8. Context Contract

Context 是 Template 與 Generator 間唯一公開契約。

Template Framework：

不知道：

- Course
- Week
- Bootstrap

它只知道：

```
Mapping<String, Any>
```

Generator 必須保證：

- 型別
- 必要欄位
- Business Rule

---

# 9. Template Search Strategy

Template Name：

```
week/README.md.j2
```

搜尋流程：

```
Template Root

↓

Normalize

↓

Resolve

↓

Validate

↓

Load
```

Resolver 必須拒絕：

- Absolute Path
- `..`
- Template Root 外部檔案

---

# 10. Security Boundary

Template Framework 信任：

- Template Root
- Context Data

Template Framework 不信任：

- User Input Path
- Arbitrary File Access
- External Process
- Network

Template 不可：

- 執行 Shell
- 修改檔案
- 開啟 Socket
- 存取 Secret

---

# 11. Exception Model

所有 Engine Exception 必須轉換成 Framework Exception。

例如：

```
TemplateSyntaxError

↓

TemplateFrameworkSyntaxError
```

Framework 外不得暴露 Engine 專屬例外。

---

# 12. Structured Output

Template Framework 可產生：

- Markdown
- YAML
- JSON
- TOML
- Python

Framework 應提供 Validation Hook。

例如：

```
Markdown

↓

No Validation
```

```
YAML

↓

yaml.safe_load()
```

```
JSON

↓

json.loads()
```

```
Python

↓

ast.parse()
```

---

# 13. Extension Points

未來可擴充：

- Custom Filter
- Custom Function
- Custom Loader
- Plugin Template
- Multiple Template Sources

不應修改：

Generator Interface。

---

# 14. Future Architecture

未來規劃：

- Template Cache
- Incremental Render
- Parallel Rendering
- Template Versioning
- Remote Template Repository
- Sandboxed Rendering
- AI-assisted Template Generation

---

# 15. Quality Attributes

Template Framework 應滿足：

## Maintainability

高內聚

低耦合

---

## Testability

所有 Component 可獨立測試。

---

## Security

所有 Template Path 經過驗證。

---

## Performance

Template Engine 可加入 Cache，而不影響 Public API。

---

## Portability

支援：

- Windows
- Linux
- macOS

不得依賴平台特殊路徑。

---

# 16. Testing Strategy

應包含：

- Unit Test
- Integration Test
- Golden File Test
- Regression Test

所有測試：

- Deterministic
- Isolated
- UTF-8
- LF

---

# 17. Related Documents

Reference：

- docs/reference/template.md

Architecture：

- docs/architecture/generator.md
- docs/architecture/filesystem.md
- docs/architecture/configuration.md

Development：

- docs/development/template-development.md
- docs/development/template-testing.md
