# Architecture Decision Records

本目錄收錄 OpenProjectLab（OPL）的 Architecture Decision Records（ADR），
用來記錄重要架構決策、背景、替代方案及其影響。

## ADR 狀態

- **Proposed**：已提出，尚未正式採納。
- **Accepted**：已接受並作為目前架構決策。
- **Deprecated**：仍保留紀錄，但不建議繼續採用。
- **Superseded**：已由另一份 ADR 取代。

## ADR 索引

| ADR | 標題 | 狀態 |
| --- | --- | --- |
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-generator-framework.md) | Generator framework | Accepted |
| [0003](0003-filesystem-write-result.md) | Filesystem `WriteResult` contract | Accepted |
| [0004](0004-remove-generator-specific-result-types.md) | Remove generator-specific result types | Proposed |

## 新增 ADR

1. 複製既有 ADR 的結構。
2. 使用下一個四位數編號。
3. 檔名採用：

   ```text
   NNNN-short-decision-title.md
