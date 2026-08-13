# Architecture Decision Records

本目錄收錄 OpenProjectLab（OPL）的 Architecture Decision Records（ADR），
用來記錄重要架構決策的背景、決策內容、替代方案及其影響。

## ADR 狀態

- **Proposed**：已提出，尚未正式採納。
- **Accepted**：已接受並成為目前的架構決策。
- **Deprecated**：仍保留紀錄，但不建議繼續採用。
- **Superseded**：已由另一份 ADR 取代。

## ADR 索引

| ADR | 標題 | 狀態 |
| --- | --- | --- |
| [0001](0001-project-philosophy.md) | Project philosophy | Accepted |
| [0002](0002-generator-lifecycle.md) | Generator lifecycle | Accepted |
| [0003](0003-configuration-and-plugin-framework.md) | Configuration and plugin framework | Accepted |
| [0004](0004-remove-generator-specific-result-types.md) | Remove generator-specific result types | Accepted |
| [0005](0005-generator-input-contract.md) | Generator Input Contract | Accepted |
| [0006](0006-generator-validation-contract.md) | Generator Validation Contract | Accepted |
| [0007](0007-generation-plan-contract.md) | Generation Plan Contract | Accepted |
| [0008](0008-generator-execution-contract.md) | Generator Execution Contract | Accepted |
| [0009](0009-remove-legacy-generator-lifecycle.md) | Remove Legacy Generator Lifecycle | Accepted |
| [0010](0010-plugin-sdk-public-contract.md) | Plugin SDK Public Contract | Accepted |
| [0011](0011-plugin-validation-contract.md) | Plugin Validation Contract | Accepted |
| [0012](0012-plugin-entry-point-contract.md) | Plugin Entry-Point Contract | Accepted |
| [0013](0013-plugin-distribution-contract.md) | Plugin Distribution Contract | Proposed |
| [0014](0014-open-courseware-domain-contract.md) | Open Courseware Domain Contract | Accepted |
| [0015](0015-lab-generator-contract.md) | Lab Generator Contract | Accepted |
| [0016](0016-quiz-generator-contract.md) | Quiz Generator Contract | Accepted |
| [0017](0017-assignment-generator-contract.md) | Assignment Generator Contract | Proposed |

## 新增 ADR

1. 使用下一個可用的四位數編號。
2. 檔名使用 `NNNN-short-decision-title.md` 格式。
3. 初始狀態設為 `Proposed`。
4. 將 ADR 加入本索引。
5. 完成架構審查、契約測試與必要實作後，將狀態改為 `Accepted`。

ADR 應至少包含：

- Context
- Decision
- Alternatives considered
- Consequences
- Migration plan
- Test strategy
- Documentation changes
- Rollback plan
- Code Review Checklist

## 維護原則

- 已接受的 ADR 不應直接改寫其歷史決策。
- 架構方向改變時，應新增 ADR，並將舊 ADR 標示為 `Superseded`。
- ADR 狀態、實作進度與相關架構文件必須保持一致。
- 影響公開 API、相容性或版本策略的決策必須留下 ADR。
