# ADR 0004：移除 Generator 專屬 Result 相容層

- 狀態：Accepted
- 日期：2026-08-01
- 決策者：OpenProjectLab 維護者
- 相關文件：`docs/architecture/generator.md`、`docs/architecture/generator-framework.md`
- 前置變更：PR #2（統一 Generator Result 契約）

## Context

Bootstrap、Course 與 Week Generator 已統一由 `generate()` 與 `run()` 回傳
`GenerationResult` 相容值，並以不可變的 `tuple[WriteResult, ...]` 記錄寫入結果。
目前仍保留下列 Generator 專屬子類別：

- `BootstrapResult`
- `CourseResult`
- `WeekResult`

這些類別是遷移期間的相容層。它們讓舊呼叫端繼續使用專屬欄位，但也使公開 API、
CLI、測試與文件同時依賴共同契約及具體結果型別，增加兩套契約長期並存的風險。

## Current dependencies

| 相容層 | 額外欄位 | 可否由共同契約推導 | 現有依賴 |
| --- | --- | --- | --- |
| `CourseResult` | `output_path` | 可以；目前只有一筆寫入，可使用 `affected_paths[0]` | Generator 功能測試 |
| `WeekResult` | `output_path` | 可以；目前只有一筆寫入，可使用 `affected_paths[0]` | Generator 功能測試 |
| `BootstrapResult` | `project_root` | 不能可靠地由共同契約完整表達 | CLI、Generator 功能測試 |
| `BootstrapResult` | `generated_files` | 可以；等同目前的 `affected_paths` | CLI、Generator 功能測試 |
| `BootstrapResult` | `created_directories` | 不能；目錄建立未記錄於 `writes` | CLI、Generator 功能測試 |

此外，CLI 的 `_print_file_result()` 宣告接收 `Path`，Course 與 Week 的呼叫端卻傳入
`GenerationResult`。這是既存的型別與執行期契約落差，應在移除相容層前修正。

## Decision

採用分階段棄用與移除策略，最終只保留 `GenerationResult` 作為 Generator 的正式結果
契約。

1. 不將 `output_path` 加入 `GenerationResult`。單一輸出只是部分 Generator 的目前行為，
   無法代表 Bootstrap 的多檔輸出，也會讓共同模型偏向單檔 Generator。
2. 所有檔案輸出統一透過 `writes`、`affected_paths` 與各狀態屬性存取。
3. CLI 改為接受 `GenerationResult`，並以共同契約列印檔案結果。
4. Bootstrap 的專案根目錄由命令已知的輸入值計算；目錄預覽由 Generator 的計畫或既有
   `DIRECTORY_MANIFEST` 顯示，不放入執行結果模型。
5. 三個專屬 Result 類別先標示棄用並解除內部依賴；在下一個明確的 breaking-change
   版本界線移除。
6. 移除後，三個 Generator 直接建立並回傳 `GenerationResult`，不再建立專屬子類別。

## Rationale

`GenerationResult` 描述「執行後發生了哪些寫入」，而專案根目錄與預先規劃的目錄屬於
請求或生成計畫。將兩者混入共同結果會模糊模型責任。以 `affected_paths` 表達零個、
一個或多個輸出，可維持共同契約的一致性，也能支援未來新增的 Generator。

## Alternatives considered

### 將 `output_path` 提升為共同欄位

不採用。Bootstrap 產生多個檔案，單一 `output_path` 的語意不清，且與 `writes` 重複。

### 永久保留三個 Result 子類別

不採用。這會使呼叫端繼續依賴具體型別，削弱共同契約與參數化契約測試的價值。

### 立即刪除相容層

不採用。CLI、測試與文件仍有直接依賴；立即移除會形成未公告的公開 API breaking
change，也會同時擴大實作與文件修改範圍。

### 在 `GenerationResult` 增加任意 metadata

目前不採用。未定型的 metadata 會降低型別安全，並可能成為新的隱性專屬契約。若未來
確有跨 Generator 的結構化結果需求，應另立 ADR。

## Migration plan

### Phase 1：解除內部依賴並公告棄用

1. 讓 CLI 的結果輸出函式接收 `GenerationResult`。
2. Course 與 Week CLI 使用 `affected_paths`，不再把 Result 當成 `Path` 傳遞。
3. Bootstrap CLI 從命令輸入取得專案根目錄，並以 `affected_paths` 列出生成檔案。
4. 將具體型別的 `isinstance()` 測試改為 `GenerationResult` 契約驗證。
5. 保留 Generator 的功能測試，包括輸出內容、路徑、dry-run、覆寫與 Manifest 行為。
6. 對三個相容類別加入一致的棄用文件與 release note；此階段仍可建立相容子類別。

### Phase 2：移除相容類別

1. 三個 Generator 直接回傳 `GenerationResult`。
2. 刪除 `BootstrapResult`、`CourseResult`、`WeekResult` 及其匯入。
3. 移除只驗證專屬欄位或具體型別的測試。
4. 更新架構文件、Bootstrap 文件、API/reference 文件與 `CHANGELOG.md`。
5. 在 breaking-change 版本的遷移指南中列出舊欄位替代方式。

## Compatibility and versioning

專屬 Result 類別及其額外欄位可能已被外部 Python 呼叫端使用，因此實際刪除屬於
breaking change。Phase 1 可在相容版本中完成；Phase 2 應安排於下一個允許 breaking
changes 的版本，並在前一個發布版本提供棄用公告。

舊 API 與替代方式如下：

| 舊 API | 替代方式 |
| --- | --- |
| `CourseResult.output_path` | `result.affected_paths[0]`，先驗證結果非空 |
| `WeekResult.output_path` | `result.affected_paths[0]`，先驗證結果非空 |
| `BootstrapResult.generated_files` | `result.affected_paths` |
| `BootstrapResult.project_root` | 呼叫端保留或由原始 request／CLI 參數計算 |
| `BootstrapResult.created_directories` | 由生成計畫或 Bootstrap 目錄規格取得 |

## Test strategy

- 保留 `test_generation_result_contract.py`，驗證三個 Generator 的共同不變條件。
- CLI 測試驗證 Bootstrap、Course、Week 的正常與 dry-run 顯示，不依賴 dataclass repr。
- Generator 功能測試繼續驗證實際輸出內容、覆寫政策、輸入驗證與 Manifest。
- 移除對 `BootstrapResult`、`CourseResult`、`WeekResult` 的 `isinstance()` 斷言。
- 新增相容期測試，確保 Phase 1 仍可匯入舊類別；Phase 2 再刪除該測試。
- 每一階段均執行完整 `pytest`、Ruff 與 `pre-commit run --all-files`。

## Documentation changes

- 新增本 ADR，並更新 `docs/adr/README.md` 索引。
- 修訂 `docs/bootstrap-generator.md`，移除把 `BootstrapResult` 當作最終契約的敘述。
- 更新 `docs/architecture/generator.md` 與
  `docs/architecture/generator-framework.md` 的遷移狀態。
- 在 `CHANGELOG.md` 記錄棄用、替代 API 與最終移除版本。
- 若專案有 API reference 或 migration guide，同步加入欄位對照表。

## Automation

CI 應持續執行：

```text
python -m pytest
python -m ruff check .
python -m ruff format --check .
pre-commit run --all-files
```

可另外加入禁止內部程式重新匯入專屬 Result 類別的靜態搜尋檢查；相容類別定義與相容期
測試可列為暫時例外。

## Rollback plan

Phase 1 主要解除內部耦合，若 CLI 顯示或相容性出現回歸，可恢復舊的列印轉接器，而不必
撤回 `GenerationResult`。Phase 2 若在發布前發現外部依賴尚未完成遷移，可延後刪除並
延長棄用期；不得重新建立第二套正式結果契約。

## Consequences

### Positive

- 所有 Generator 只有一個正式結果契約。
- CLI、測試與未來 plugin 可依賴相同的不可變模型。
- 避免把單檔輸出假設寫入核心模型。
- 專屬計畫資訊與執行結果維持清楚的責任邊界。

### Negative

- 外部呼叫端需要遷移專屬欄位。
- Bootstrap 的目錄資訊需要由 request、plan 或規格取得，不能再從結果子類別直接讀取。
- 必須維護至少一個發布週期的棄用文件與相容測試。

## Code Review Checklist

- [ ] `generate()` 與 `run()` 的公開型別仍為 `GenerationResult`
- [ ] 未將單一 `output_path` 加入共同模型
- [ ] CLI 不再把 `GenerationResult` 傳給要求 `Path` 的函式
- [ ] CLI 未依賴三個專屬 Result 型別
- [ ] `affected_paths` 保持 `writes` 順序
- [ ] dry-run 不建立實體輸出且結果仍可預覽
- [ ] `manifest_updated` 語意未改變
- [ ] 功能測試未被契約測試取代或重複
- [ ] 相容期與 breaking-change 版本已記錄
- [ ] Bootstrap 文件與架構文件同步更新
- [ ] `CHANGELOG.md` 與遷移指南列出替代 API
- [ ] Ruff、pytest、pre-commit 與 CI 全部通過
