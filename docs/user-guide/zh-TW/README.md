# OpenProjectLab v1.0 使用者手冊

> **語言：** 繁體中文（台灣）
> **適用對象：** OpenProjectLab 使用者、教育工作者、課程教材作者與擴充功能使用者
> **狀態：** v1.0 文件基線

OpenProjectLab（OPL）是一個專案工程與內容生成平台，其核心建立在明確契約、確定性生成、套件自有執行期資源、清楚的擴充邊界，以及自動化驗證之上。

本手冊說明 v1.0 的使用者可見功能範圍，並刻意聚焦於目前已實作、已測試且屬於 v1.0 發布就緒工作的行為。本手冊不會把提案中或延後實作的能力描述成 Stable v1.0 保證。

## 從這裡開始

如果你第一次使用 OPL，建議依序閱讀：

1. [核心概念](concepts.md) — 建立 OPL 的整體心智模型。
2. [安裝](installation.md) — 安裝並驗證 OPL artifact。
3. [快速開始](quick-start.md) — 完成一個具代表性的首次工作流程。
4. [CLI](cli.md) — 深入了解命令列介面。

## 手冊目錄

- [核心概念](concepts.md)
- [安裝](installation.md)
- [快速開始](quick-start.md)
- [組態設定](configuration.md)
- [CLI](cli.md)
- [Generators](generators.md)
- [Courseware](courseware.md)
- [Plugins](plugins.md)
- [AI 整合](ai-integration.md)
- [Marketplace](marketplace.md)
- [疑難排解](troubleshooting.md)
- [升級](upgrading.md)

英文版手冊同步維護於 `docs/user-guide/en/`。

## 本手冊涵蓋範圍

v1.0 手冊涵蓋 OPL 已驗證的使用者可見邊界：

- `opl` 命令列介面；
- 內建 Generators；
- 確定性生成行為；
- 套件自有的執行期 templates；
- Course 與 Week courseware 概念；
- courseware composition；
- Plugin SDK 與標準 Generator Entry Point 邊界；
- provider-independent AI integration 概念；
- Marketplace artifact 與安裝概念；
- 疑難排解與升級指引。

部分能力會等到各自的 release-readiness gate 被接受後，才成為正式文件範圍。特別是，本手冊不會提前定義 Milestone 8 Step 8.6–8.8 所負責的 compatibility/deprecation policy、environment support claims 或 release-publication semantics。

## 核心使用流程

OPL 的高階模型如下：

```text
使用者意圖 / CLI 輸入
        ↓
Generator request
        ↓
validation
        ↓
generation plan
        ↓
execution
        ↓
generated artifacts
        ↓
GenerationResult
```

這個 lifecycle 由 framework 統一管理，使內建與擴充 Generators 都能共享可預測的行為。

## 內建 Generator 類型

目前 CLI 提供以下內建 Generator identities：

```text
assignment
bootstrap
course
lab
quiz
slides
website
week
```

可以執行：

```console
opl list
```

查看目前安裝版本提供的 Generator surface。

## Installed-User 原則

v1.0 文件以「從正式安裝的 distribution 使用 OPL」作為正常使用情境。

主要使用流程不得依賴：

- editable installation；
- `PYTHONPATH`；
- 僅存在於 repository 的 templates；
- 未追蹤的本機檔案；
- 必須從 OpenProjectLab source checkout 中執行。

開發 OPL 本身時可以使用 source checkout，但那屬於開發者流程，不是本手冊所定義的一般使用者路徑。

## 文件慣例

命令會以 fenced block 顯示，例如：

```console
opl list
```

不是 literal input 的 placeholder 會使用角括號：

```text
<output-directory>
<wheel-path>
```

command names、option names、Python modules、Entry Point names、configuration keys 與 artifact paths 等 canonical identifiers，會保留產品實際使用的形式，不進行翻譯。

## 文件正確性

本手冊受 v1.0 documentation contract 管理。

若本手冊內容與已接受的 v1.0 contract 或已驗證的 production behavior 衝突，應修正手冊，而不是重新解釋產品行為。

文件本身也是 release readiness 的一部分：使用者預期會實際執行的指令，應在可行範圍內透過自動化測試驗證。

## 下一步

請繼續閱讀[核心概念](concepts.md)，再依序完成[安裝](installation.md)與[快速開始](quick-start.md)。
