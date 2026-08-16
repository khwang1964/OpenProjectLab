# Architecture Decision Records

本目錄收錄 OpenProjectLab（OPL）的 Architecture Decision
Records（ADR），
用來記錄重要架構決策的背景、決策內容、替代方案及其影響。

## ADR 狀態

-   **Proposed**：已提出，尚未正式採納。
-   **Accepted**：已接受並成為目前的架構決策。
-   **Deprecated**：仍保留紀錄，但不建議繼續採用。
-   **Superseded**：已由另一份 ADR 取代。

## ADR 索引

  -----------------------------------------------------------------------------------------
  ADR                                                      標題                 狀態
  -------------------------------------------------------- -------------------- -----------
  [0001](0001-project-philosophy.md)                       Project philosophy   Accepted

  [0002](0002-generator-lifecycle.md)                      Generator lifecycle  Accepted

  [0003](0003-configuration-and-plugin-framework.md)       Configuration and    Accepted
                                                           plugin framework

  [0004](0004-remove-generator-specific-result-types.md)   Remove               Accepted
                                                           generator-specific
                                                           result types

  [0005](0005-generator-input-contract.md)                 Generator Input      Accepted
                                                           Contract

  [0006](0006-generator-validation-contract.md)            Generator Validation Accepted
                                                           Contract

  [0007](0007-generation-plan-contract.md)                 Generation Plan      Accepted
                                                           Contract

  [0008](0008-generator-execution-contract.md)             Generator Execution  Accepted
                                                           Contract

  [0009](0009-remove-legacy-generator-lifecycle.md)        Remove Legacy        Accepted
                                                           Generator Lifecycle

  [0010](0010-plugin-sdk-public-contract.md)               Plugin SDK Public    Accepted
                                                           Contract

  [0011](0011-plugin-validation-contract.md)               Plugin Validation    Accepted
                                                           Contract

  [0012](0012-plugin-entry-point-contract.md)              Plugin Entry-Point   Accepted
                                                           Contract

  [0013](0013-plugin-distribution-contract.md)             Plugin Distribution  Proposed
                                                           Contract

  [0014](0014-open-courseware-domain-contract.md)          Open Courseware      Accepted
                                                           Domain Contract

  [0015](0015-lab-generator-contract.md)                   Lab Generator        Accepted
                                                           Contract

  [0016](0016-quiz-generator-contract.md)                  Quiz Generator       Accepted
                                                           Contract

  [0017](0017-assignment-generator-contract.md)            Assignment Generator Accepted
                                                           Contract

  [0018](0018-slides-generator-contract.md)                Slides Generator     Accepted
                                                           Contract

  [0019](0019-website-generator-contract.md)               Website Generator    Accepted
                                                           Contract

  [0020](0020-courseware-composition-contract.md)          Courseware           Accepted
                                                           Composition Contract

  [0021](0021-ai-integration-contract.md)                  AI Integration       Accepted
                                                           Contract

  [0022](0022-ai-provider-adapter-contract.md)             AI Provider Adapter  Accepted
                                                           Contract

  [0023](0023-marketplace-artifact-contract.md)            Marketplace Artifact Accepted
                                                           Contract
  -----------------------------------------------------------------------------------------

## Milestone Acceptance Records

ADR 記錄架構決策；Milestone acceptance record 記錄跨 ADR、實作、測試、
文件與 automation gates 的里程碑收束證據。兩者責任不同，不以 acceptance
record 取代 ADR。

目前正式 acceptance records：

-   `docs/milestones/milestone-4-acceptance.md`
-   `docs/milestones/milestone-5-acceptance.md`
-   `docs/milestones/milestone-6-acceptance.md`
-   `docs/milestones/milestone-7-acceptance.md`

Milestone 6 的核心架構決策由 ADR 0021 與 ADR 0022 保持 `Accepted`；
Milestone 6 formal acceptance 已由 milestone acceptance record、最終
quality-gate evidence、GitHub Actions / CI、squash merge 與 post-merge
consistency verification 完成收束。

Milestone 6 final acceptance baseline：

``` text
1119 passed, 1 deselected
Total coverage: 90.23%
Required coverage: 67.0% --- Passed
GitHub Actions / CI: Passed
Squash merge: Completed
Post-merge consistency verification: Completed
```

Milestone 7 Marketplace artifact contract、repository/index、integrity/acquisition、
installation、Template Package 與 representative E2E 已完成。ADR 0023 ---
Marketplace Artifact Contract 已依 implementation、contract tests、full regression
與 coverage evidence 轉為 `Accepted`。

Milestone 7 final local baseline：

``` text
1315 passed, 1 deselected
Total coverage: 89.89%
Required coverage: 67.0% --- Passed
```

Acceptance PR GitHub Actions / CI 與 post-merge consistency verification 仍作為
Milestone 7 最後 closure gates。

## 新增 ADR

1.  使用下一個可用的四位數編號。
2.  檔名使用 `NNNN-short-decision-title.md` 格式。
3.  初始狀態設為 `Proposed`。
4.  將 ADR 加入本索引。
5.  完成架構審查、契約測試與必要實作後，將狀態改為 `Accepted`。

ADR 應至少包含：

-   Context
-   Decision
-   Alternatives considered
-   Consequences
-   Migration plan
-   Test strategy
-   Documentation changes
-   Rollback plan
-   Code Review Checklist

## 維護原則

-   已接受的 ADR 不應直接改寫其歷史決策。
-   架構方向改變時，應新增 ADR，並將舊 ADR 標示為 `Superseded`。
-   ADR 狀態、實作進度與相關架構文件必須保持一致。
-   影響公開 API、相容性或版本策略的決策必須留下 ADR。
