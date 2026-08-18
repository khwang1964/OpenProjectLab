# Courseware

OpenProjectLab（OPL）將 courseware domain 與檔案 rendering 分離。目前 layer 提供 immutable `Course`、`Week` domain models，以及透過 shared `GeneratorRegistry` 協調 ordered Generator requests 的 `CoursewareComposer`。

## Domain model

`Week(number, title)` 表示一個 teaching unit。`number` 必須是大於 0 的整數。

`Course(course_id, title, language, weeks=())` 是 root aggregate。它會 trim `course_id`、拒絕空 ID 與重複 week numbers、將 weeks 正規化為 tuple，並依 week number 排序。

```python
from generator.courseware import Course, Week

course = Course(
    course_id="modern-java",
    title="Modern Java",
    language="en",
    weeks=(Week(2, "Streams"), Week(1, "Introduction")),
)
```

結果 weeks 順序為 1、2。

## Composition architecture

Courseware composition 重用 Generator framework：

```text
ordered GenerateRequest values
→ validate sequence
→ resolve every required Generator
→ execute sequentially
→ tuple[GenerationResult, ...]
```

`CoursewareComposer.plan()` 保留 authored order 並回傳 immutable tuple。輸入必須是只包含 `GenerateRequest` 的 ordered `Sequence`；strings、bytes、mappings、non-sequences 與混合型別 sequence 都會被拒絕。

## Fail-fast preflight

`run()` 在任何 Generator 執行前先解析**全部** required Generators。如果後面的 request 指定不存在的 Generator，composition 會在前面的 request 產生 filesystem effects 前失敗。

preflight 成功後依序執行。如果某 Generator runtime failure，後續 requests 不再執行；先前成功 writes **不會**自動反轉。因此這是 fail-fast orchestration，不是 ACID transaction 或 generalized rollback。

## CLI boundary

v1.0 documented CLI 維持 Generator-oriented commands（`course`、`week`、`lab`、`assignment`、`quiz`、`slides`、`website`），沒有 documented general-purpose `courseware compose` command。programmatic composition 應視為 framework/domain capability，直到未來 release 建立 CLI contract。

## AI relationship

AI-assisted course generation 將 provider-independent AI output 映射到相同 `Course` / `Week` domain model：

```text
AIResponse → validated mapping → Course / Week
```

AI 不建立平行 courseware representation。

## Design boundaries

```text
Course / Week        domain model
Generators           artifact planning/execution
CoursewareComposer   ordered orchestration
Plugin SDK           Generator discovery/registration
AI                   provider-independent assistance
Marketplace          artifact distribution contracts
```

### Checklist

- Week number 使用正整數且不可重複。
- `course_id` 不可為空。
- Course / Week 視為 immutable values。
- 提供 ordered `GenerateRequest` values。
- composition 前註冊全部 required Generators。
- unresolved Generator 應在 preflight fail。
- 不假設已完成 Generator writes 會 rollback。

## 下一步

繼續閱讀 [Plugins](plugins.md)。
