# Generator Reference

> Status: Implemented
> Milestone: 3 — Core Framework
> Last updated: 2026-08-04
> Audience: Generator users, SDK consumers, maintainers, and plugin authors
> Related: ADR 0002, ADR 0005, ADR 0006, `docs/architecture/generator.md`

本文件定義 OpenProjectLab（OPL）Generator 的現行公開使用契約，包括共用輸入、
執行選項、回傳結果、結構化驗證錯誤，以及 Bootstrap、Course、Week 三個內建
Generator 的輸入規則。

架構動機、依賴方向與未來設計請參閱 `docs/architecture/generator.md`；本文件只描述
呼叫端目前可以依賴的行為。

## 1. Built-in Generators

| Name | Class | Purpose |
| --- | --- | --- |
| `bootstrap` | `BootstrapGenerator` | 建立 OPL 專案或課程專案骨架 |
| `course` | `CourseGenerator` | 建立課程層級內容 |
| `week` | `WeekGenerator` | 建立單一週次或教學單元內容 |

`name` 是 Registry、CLI、`GenerateRequest.generator_name` 與錯誤資訊使用的穩定
識別碼。呼叫端不應由 Python class name 推導 generator name。

## 2. Shared Input Contract

所有內建 Generator 共用 `GenerateRequest`：

```python
from pathlib import Path

from generator.core.models import GenerateRequest, RuntimeOptions

request = GenerateRequest(
    generator_name="course",
    output_root=Path("courses"),
    values={
        "course_slug": "modern-java",
        "course_name": "Modern Java in Action",
    },
    options=RuntimeOptions(dry_run=True),
)
```

### `GenerateRequest`

| Field | Meaning |
| --- | --- |
| `generator_name` | 要執行的 canonical generator name |
| `output_root` | 本次產出的根目錄 |
| `values` | Generator-specific 業務輸入 |
| `options` | 共用 runtime flags |

`GenerateRequest` 負責共用資料結構與 value-object invariants；特定 Generator 的欄位
存在性、型別、範圍及格式則由該 Generator 驗證。

### `RuntimeOptions`

`RuntimeOptions` 保存不屬於業務內容的執行選項。`dry_run=True` 只抑制實體寫入，
不會跳過輸入、template、rendering、路徑安全或衝突檢查。

Dry run 必須：

- 執行與正常模式相同的 pre-write validation；
- 回傳完整的預計寫入結果；
- 不建立、更新或刪除檔案；
- 不更新 generation manifest。

## 3. Execution

`run(request)` 是建議的標準生命週期入口：

```python
generator = CourseGenerator(template_root)
result = generator.run(request)
```

遷移期間支援的 `generate(request)` 必須提供與 `run(request)` 相同的驗證行為、例外
語意及成功結果。呼叫端不應依賴兩者之間的內部實作差異。

執行順序如下：

1. 驗證 `generator_name`；
2. 驗證並正規化 generator-specific values；
3. 建立並驗證產出計畫；
4. render templates 並完成 domain checks；
5. 執行或模擬 writes；
6. 回傳 `GenerationResult`。

驗證失敗時不會回傳 `GenerationResult`，也不得產生任何 filesystem 或 manifest
side effect。

## 4. Generation Result

所有內建 Generator 均直接回傳共用 `GenerationResult`。舊的
`BootstrapResult`、`CourseResult` 與 `WeekResult` 已移除。

```python
from generator.core.models import GenerationResult

result: GenerationResult = generator.run(request)

for path in result.affected_paths:
    print(path)
```

主要欄位與衍生資料：

| Member | Contract |
| --- | --- |
| `generator_name` | 完成執行的 canonical generator name |
| `writes` | 不可變的 `tuple[WriteResult, ...]`，保留操作順序 |
| `dry_run` | 是否為模擬執行 |
| `manifest_updated` | 本次是否實際更新 manifest |
| `warnings` | 不可變的警告集合 |
| `affected_paths` | 由 `writes` 衍生，並保留 write order |
| `created` / `updated` / `skipped` / `unchanged` | 依 write status 衍生的結果集合 |

Dry run 仍會回報預計的 writes，但必須滿足：

```python
result.dry_run is True
result.manifest_updated is False
```

`GenerationResult` 描述結構化事實，不包含預先格式化的 console output。

## 5. Generator Validation Error

Generator-specific 業務驗證失敗時會拋出 `GeneratorValidationError`：

```python
from generator.core.exceptions import GeneratorValidationError

try:
    result = generator.run(request)
except GeneratorValidationError as exc:
    print(exc.generator)
    print(exc.field)
    print(exc.message)
```

### Stable attributes

| Attribute | Contract |
| --- | --- |
| `generator` | 發生錯誤的 canonical generator name |
| `field` | 無效的公開欄位名稱；request-level 錯誤可為 `None` |
| `message` | 簡潔、可供使用者理解的錯誤說明 |

這三個 attributes 是相容性契約。完整字串的標點或句型不是穩定 API，除非個別測試
明確宣告；程式應優先判斷 exception type 與結構化 attributes。

### Error ownership

| Failure | Exception ownership |
| --- | --- |
| Shared request model invariant | `GenerateRequest` 的既有 value-object error |
| Generator identity or business value | `GeneratorValidationError` |
| Template resolution or rendering | Template subsystem exception |
| Destination or filesystem operation | Filesystem subsystem exception |
| Manifest schema or persistence | Manifest subsystem exception |
| Configuration or upgrade | 各自的 domain exception |

Generator 不會把 template、filesystem、manifest、configuration 或 upgrade failures
重新分類為 `GeneratorValidationError`。

## 6. Validation Fields

所有內建 Generator 都會驗證下列共用欄位：

| Field | Rule |
| --- | --- |
| `generator_name` | 必須與所選 Generator 的 canonical name 相符 |
| `template_root` | 必須符合該 Generator 的 template root 契約 |

目前的 generator-specific validation fields：

| Generator | Field | Contract |
| --- | --- | --- |
| Bootstrap | `project_slug` | 必須是非空且符合專案 slug 規則的字串 |
| Course | — | 除共用欄位外，依現行 request/context contract 驗證 |
| Week | `week` | 必須是有效範圍內的整數；`bool` 不視為整數 |
| Week | `directory_pattern` | 必須可格式化，且結果必須是安全的相對輸出目錄 |

錯誤的 `field` 必須使用公開 `GenerateRequest` 欄位名稱，或 `values` 中的 key。例如：

```python
assert exc.generator == "week"
assert exc.field == "directory_pattern"
```

驗證順序具有決定性；相同 request 的第一個錯誤應保持穩定。

## 7. CLI Error Boundary

CLI 在 application boundary 捕捉 `GeneratorValidationError`，將訊息寫入 stderr，並
回傳 exit code `2`。正常的使用者輸入錯誤不應顯示 traceback。

```text
valid request       -> exit code 0
validation failure  -> exit code 2, message on stderr
```

Argument parser errors 仍由 parser 處理。未預期的程式錯誤不應偽裝成 validation
failure，以便測試與診斷工具看見真正的 traceback。

## 8. Plugin Generator Requirements

Plugin Generator 若要與內建 Generator 及 CLI 保持一致，必須：

- 使用 canonical、穩定且已註冊的 generator name；
- 接受共用 `GenerateRequest` 與 `RuntimeOptions`；
- 對 generator-specific 業務輸入拋出 `GeneratorValidationError`；
- 正確填入 `generator`、`field` 與 `message`；
- 在 planning 或任何 side effect 前完成驗證；
- 讓 normal run 與 dry run 提供相同的 pre-write validation；
- 回傳共用 `GenerationResult`；
- 保留下游 domain exception 類別及 exception chaining。

在正式 SDK re-export boundary 完成前，plugin 不應假設未記錄的內部模組是穩定 API。

## 9. Testing Contract

Generator 的最低測試範圍包括：

- `GeneratorValidationError` attributes 與 rendering；
- generator-name mismatch；
- 缺少值、錯誤型別、越界值、錯誤 pattern 與不安全路徑；
- normal run 與 dry run 的相同驗證結果；
- 驗證失敗前後 filesystem 與 manifest 均無 side effect；
- template、filesystem 與 manifest exception boundaries 不變；
- `run()` 與受支援的 `generate()` 行為相等且不重複驗證；
- CLI stderr、exit code `2` 與無 traceback 行為；
- 所有內建 Generator 的 parameterized contract tests。

目前 validation migration 的驗證基線：

```text
32 generator validation contract tests passed
332 full-suite tests passed
Coverage: 80.79% (required: 67%)
```

這些數字是 2026-08-04 的實作 checkpoint，不是永久固定的測試總數。

## 10. Code Review Checklist

- [ ] Generator 使用 canonical name，且 Registry、request 與 error metadata 一致。
- [ ] 共用資料結構由 `GenerateRequest` 驗證，業務規則由 Generator 驗證。
- [ ] 業務輸入錯誤使用 `GeneratorValidationError`。
- [ ] `generator`、`field` 與 `message` attributes 正確且具決定性。
- [ ] Template、filesystem、manifest、configuration 與 upgrade errors 未被錯誤包裝。
- [ ] 所有驗證在任何 physical write 或 manifest mutation 前完成。
- [ ] Dry run 執行完整 pre-write validation，且無 side effect。
- [ ] `run()` 與受支援的 `generate()` 具有相等契約。
- [ ] 成功結果使用共用 `GenerationResult`，writes 順序保持穩定。
- [ ] CLI validation failure 回傳 exit code `2` 且不輸出 traceback。
- [ ] 新規則具備 unit、contract 與 integration tests。
- [ ] Architecture、reference、ADR、changelog 與 plugin guidance 已同步更新。
- [ ] Ruff、pytest、coverage、pre-commit 與 documentation checks 全部通過。

## 11. Related Documents

- `docs/architecture/generator.md`
- `docs/adr/0002-generator-lifecycle.md`
- `docs/adr/0005-generator-input-contract.md`
- `docs/adr/0006-generator-validation-contract.md`
- `docs/reference/filesystem.md`
- `docs/reference/template.md`
