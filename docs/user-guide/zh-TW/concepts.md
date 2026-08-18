# OpenProjectLab 核心概念

本章介紹 OpenProjectLab（OPL）的核心心智模型。一般使用者不需要了解內部實作細節，但理解主要架構邊界後，會更容易掌握 CLI、Generators、plugins、courseware、AI integration 與 Marketplace 的行為。

## 1. OpenProjectLab 作為 Project Engineering Platform

OPL 最初可被理解為專案與內容 Generator，但它的設計目標不只是在 templates 中替換文字。

平台遵循四個工程原則：

```text
Design First
Documentation First
Automation First
Testing First
```

對使用者而言，實際意義是：重要行為應透過明確 contract 與可驗證 workflow 表達，而不是依賴隱藏慣例。

## 2. Generators

Generator 是將結構化輸入轉換為一個或多個規劃後 artifacts 的元件。

內建 Generator identities 包括：

```text
bootstrap
course
week
lab
quiz
assignment
slides
website
```

每個 Generator 可以有自己的使用者輸入，但所有內建 Generators 都共享 framework 控制的 canonical lifecycle。

## 3. Canonical Generation Lifecycle

核心 lifecycle：

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

### Request

request 用來識別：

- 要執行哪一個 Generator；
- target location；
- 該 Generator 所需要的 values；
- overwrite、dry-run 等 runtime options。

### Validation

validation 會在可避免的 side effects 發生前拒絕不合法輸入。

Generator 不應該先開始寫入檔案，之後才發現必要輸入無效。

### Plan

planning 將有效 request 轉換為明確的 `GenerationPlan`。

plan 描述預計執行的 generation operations，包括各 artifact 所使用的 template 與 destination。

### Execution

execution 透過既有 rendering 與 filesystem boundaries 執行 plan。

### Result

execution 回傳 `GenerationResult`，而不是讓各 Generator 自行建立不同的 result model。

這個共享 lifecycle 是 OPL 的核心架構限制：extension 不應建立第二套 execution framework。

## 4. Targets、Output Roots 與 Generated Artifacts

CLI 先解析 output root，再於其中建立 Generator-specific targets。

例如，`course` command 使用 `demo-course` 作為 project slug 時，target 為：

```text
<output-root>/demo-course/
```

Course Generator 會產生：

```text
<output-root>/demo-course/README.md
```

除非透過較低階的 programmatic use 明確改變 output name。

在相關行為啟用時，generation 也可能維護 OPL-owned metadata，例如 project manifest。

## 5. Package-Owned Runtime Resources

內建 Generators 使用 runtime templates。

為了符合 v1.0 release readiness，這些 templates 由已安裝 Python package 的 package-resource boundary 擁有，而不是依賴 repository-level `templates/` directory。

概念如下：

```text
installed openprojectlab distribution
        ↓
generator.resources
        ↓
package-owned templates
        ↓
built-in Generator
```

這代表使用者即使不在 source repository 中，也應能正常執行 OPL。

若使用者確實要指定不同的 template root，CLI 仍提供明確的 `--template-root` override。

## 6. Dry Run 與 Overwrite 行為

內建 generation commands 共用與寫入相關的 runtime options。

### Dry Run

`--dry-run` 會執行 validation 與 planning，但不持久化正常的 generated output。

當你想先確認 generation request 是否有效，再決定是否寫入檔案時，可以使用它。

### Force / Overwrite

`--force` 在 underlying Generator 與 filesystem contract 允許的範圍內啟用 overwrite behavior。

如果沒有明確要求 overwrite，OPL 會維持既有 write-conflict behavior，而不是默默覆蓋使用者內容。

### Manifest Control

`--no-manifest` 可停用原本會記錄 generation metadata 的 command 之 manifest 更新。

## 7. Courseware Model

OPL 包含 Open Courseware layer。

其基礎包含 Course 與 Week concepts；在其上可以生成：

- Lab material；
- Quiz material；
- Assignment material；
- Slides source；
- static Website output。

Courseware Composition 是協調既有 Generators，而不是建立第二套 generation lifecycle。

目前 established composition behavior 是 deterministic 與 fail-fast；它不保證 generalized cross-Generator rollback。

## 8. Plugin Extension Model

第三方 Generator extensions 使用 stable Plugin SDK/public boundary，以及 canonical Entry Point group：

```text
openprojectlab.generators
```

概念如下：

```text
third-party installed distribution
        ↓
openprojectlab.generators Entry Point
        ↓
discovery / loading
        ↓
validation
        ↓
registry
        ↓
canonical Generator lifecycle
```

installation 與 discovery 並不代表可以略過 validation 或 shared Generator lifecycle。

Plugin authors 在 public SDK 已提供所需 contract 時，應依賴 SDK boundary，而不是 internal modules。

## 9. AI Integration Boundary

OPL 的 AI architecture 將 provider-specific behavior 與核心 application contracts 分離。

provider-independent model：

```text
application request
        ↓
AIProvider
        ↓
AIResponse
        ↓
structural validation
        ↓
domain mapping / application service
```

AI output 被視為 external input，必須先驗證，才能用於建立 domain objects 或參與 generation。

一般 deterministic tests 不需要 real provider、public network access 或 paid invocation。

具體 provider adapter 可以存在於 provider-independent boundary 後方，但 provider-specific SDK details 並不是核心 AI contract。

## 10. Marketplace Boundary

Marketplace layer 將 distributable artifacts 與不同責任分離：

```text
artifact lookup
    ↓
acquisition
    ↓
integrity verification
    ↓
installation
```

installation 與 activation 是刻意分離的責任。

已驗證的 Marketplace core 並不代表 v1.0 包含 public remote Marketplace service、ratings、reviews、monetization、generalized dependency solving 或其他 deferred platform capabilities。

## 11. Stable、Experimental、Internal 與 Deferred

Milestone 8 會稽核 v1.0 surface，避免文件意外承諾超出專案可維護範圍的能力。

實用的閱讀方式：

- **Stable** — 屬於經過審查的 compatibility surface。
- **Experimental** — 已實作，但尚未提升到相同 compatibility commitment。
- **Internal** — implementation detail，不是 user contract。
- **Deferred** — 刻意排除於 v1.0 scope。

正式 compatibility/deprecation policy 由後續 Milestone 8 policy step 負責，本章不提前定義該政策。

## 12. Determinism

Deterministic behavior 是 OPL 的重要特性。

在等價的有效輸入與相同相關 configuration 下，OPL 的目標是產生可預測的 plans 與 artifacts。這使系統更容易測試、review、自動化並整合進 CI。

core generation 不應在缺乏明確 contract 的情況下引入 hidden nondeterminism。

## 13. Failure Boundaries

OPL 一般遵循：

```text
在可避免的 side effects 前完成 validation
以可預測方式失敗
在 contract 要求時保留既有狀態
不宣稱不存在的 rollback
```

例如：

- invalid Generator input 應在 generation 前失敗；
- Marketplace installation 前應先完成 integrity verification；
- invalid AI structured output 應在 downstream filesystem effects 前失敗；
- composition 發生 failure 時會停止，但不宣稱撤銷先前已成功的 Generators。

## 14. 使用者心智模型

可以用以下方式理解 OPL：

```text
CLI / application input
        ↓
verified public contracts
        ↓
Generator / Plugin / AI / Marketplace boundaries
        ↓
deterministic planning and validation
        ↓
filesystem or installation result
```

你不需要使用所有 subsystem。這些 shared contracts 的目的，是讓簡單 workflow 與較大型 composed workflow 都具有一致且可預測的行為。

## 下一步

請繼續閱讀[安裝](installation.md)，然後完成[快速開始](quick-start.md)。
