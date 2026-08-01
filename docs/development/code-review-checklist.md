# OpenProjectLab Code Review Checklist

> Status: Active
> Audience: Contributors, reviewers, maintainers
> Applies to: Pull Requests, feature branches, documentation changes, refactoring, bug fixes

本文件定義 OpenProjectLab（OPL）統一的 Code Review 檢查標準。

Code Review 的目的不只是確認程式可以執行，也包括：

* 驗證設計是否符合架構原則
* 防止不必要的耦合與技術債
* 確保文件與程式同步
* 確保測試能保護重要行為
* 確保變更可理解、可維護且可安全演進

---

## 1. Review Roles

### Author

變更作者負責：

* 清楚說明問題與解決方案
* 控制變更範圍
* 完成自我檢查
* 更新文件
* 新增或更新測試
* 回應 Review 意見

### Reviewer

Reviewer 負責：

* 驗證設計與行為
* 找出風險與不一致
* 提出具體且可執行的建議
* 區分必要修改與非阻擋性建議
* 避免只檢查格式，而忽略架構與行為

### Maintainer

Maintainer 負責：

* 確認變更符合專案方向
* 處理架構與相容性爭議
* 決定是否需要 ADR
* 確認 Release 與治理要求

---

## 2. Pull Request Context

Review 前，PR 應清楚說明：

* [ ] 要解決的問題
* [ ] 變更範圍
* [ ] 採用的設計方式
* [ ] 可能受影響的模組
* [ ] 測試方式
* [ ] 文件更新
* [ ] 已知限制
* [ ] 是否包含破壞性變更

Reviewer 應能只閱讀 PR 說明與相關文件，就理解這次變更的目的。

---

## 3. Scope and Focus

確認變更範圍合理：

* [ ] PR 聚焦於單一主題
* [ ] 沒有混入無關重構
* [ ] 沒有混入暫存檔、快取或產物
* [ ] 沒有大量不必要的格式變更
* [ ] 沒有修改不相關的設定
* [ ] 變更規模適合 Review
* [ ] 大型變更已拆分為可理解的階段

應避免在同一個 PR 中同時加入：

* 新功能
* 大型重構
* 依賴更新
* 文件重整
* 無關格式化

除非這些變更具有不可分割的依賴關係。

---

## 4. Architecture Review

### 4.1 Responsibility

* [ ] 功能位於正確的模組
* [ ] 每個類別或函式具有清楚責任
* [ ] CLI 沒有包含主要業務邏輯
* [ ] Generator 沒有直接處理 CLI 解析
* [ ] Template 沒有承擔複雜業務規則
* [ ] Core 沒有反向依賴 CLI
* [ ] SDK 沒有暴露不必要的內部實作

### 4.2 Dependency Direction

* [ ] 依賴方向符合 Architecture Overview
* [ ] 沒有形成循環依賴
* [ ] 沒有新增隱藏的全域狀態
* [ ] 設定、路徑與服務以明確方式傳入
* [ ] 高階邏輯沒有過度依賴特定實作
* [ ] 新依賴具有明確理由

### 4.3 Extensibility

* [ ] 新功能能透過既有 Framework 擴充
* [ ] 沒有為單一情境建立過度抽象
* [ ] 公開介面保持最小
* [ ] 擴充點具有清楚契約
* [ ] 未完成的 Plugin 能力沒有被描述為穩定功能

### 4.4 Architecture Decision

以下情況應考慮新增 ADR：

* 新增核心 Framework
* 修改依賴方向
* 修改公開 API
* 修改 Generator 生命週期
* 修改設定格式
* 引入重要第三方依賴
* 修改 Plugin 或 SDK 契約
* 採用具有長期影響的技術方案

檢查：

* [ ] 已判斷是否需要 ADR
* [ ] 必要時已新增或更新 ADR
* [ ] Architecture 文件已同步更新

---

## 5. Correctness Review

確認程式行為符合需求：

* [ ] 正常流程正確
* [ ] 錯誤流程正確
* [ ] 邊界條件已處理
* [ ] 空值或缺少輸入時行為明確
* [ ] 路徑處理同時考慮相對與絕對路徑
* [ ] Windows、Linux 與 macOS 差異已考量
* [ ] Unicode 與 UTF-8 內容可正確處理
* [ ] 重複執行不會產生非預期結果
* [ ] 錯誤不會被靜默忽略
* [ ] 回傳值與 Exit Code 一致

Reviewer 不應只確認測試通過，也應閱讀實作並驗證需求是否真的被滿足。

---

## 6. Error Handling

* [ ] 錯誤在接近來源的位置產生
* [ ] 使用適當的自訂例外
* [ ] 例外訊息清楚且可操作
* [ ] CLI 將內部錯誤轉換為使用者可理解的訊息
* [ ] 正常錯誤不會輸出不必要的 traceback
* [ ] 原始例外在需要時透過 `raise ... from ...` 保留
* [ ] 沒有使用過度寬泛的 `except Exception`
* [ ] 檔案系統錯誤具有足夠上下文
* [ ] 錯誤訊息不洩漏敏感資料

---

## 7. Configuration Review

若變更涉及設定：

* [ ] 設定欄位名稱清楚
* [ ] 預設值合理
* [ ] 必要欄位會被驗證
* [ ] Mapping、List、String 等型別已驗證
* [ ] 相對路徑的解析基準明確
* [ ] 絕對路徑行為明確
* [ ] 缺少設定檔時有清楚錯誤
* [ ] YAML 格式錯誤能被正確處理
* [ ] 向後相容性已考量
* [ ] Configuration Reference 已更新
* [ ] 設定範例已更新

---

## 8. Generator Review

若變更涉及 Generator：

* [ ] Generator 名稱唯一
* [ ] Registry 註冊方式一致
* [ ] Generator 可獨立於 CLI 測試
* [ ] 輸入與輸出明確
* [ ] 目標目錄行為明確
* [ ] 已存在檔案的處理方式明確
* [ ] 重複執行行為明確
* [ ] 錯誤不會留下不完整輸出
* [ ] Template 缺失時有清楚錯誤
* [ ] CLI Reference 已更新
* [ ] Generator 文件已更新
* [ ] 已新增單元或整合測試

---

## 9. Template Review

若變更涉及 Template：

* [ ] Template 放置於正確目錄
* [ ] `generator/templates/` 與根目錄 `templates/` 的用途沒有混淆
* [ ] Template 變數名稱清楚
* [ ] 必要變數會被驗證
* [ ] 缺少變數時錯誤明確
* [ ] 渲染結果使用 UTF-8
* [ ] 輸出換行格式一致
* [ ] Template 不包含複雜業務邏輯
* [ ] 路徑遍歷風險已考量
* [ ] 渲染測試已新增或更新
* [ ] Template Reference 已更新

---

## 10. API and SDK Review

若變更涉及公開介面：

* [ ] 公開 API 的必要性明確
* [ ] 命名清楚且一致
* [ ] 型別標註完整
* [ ] 回傳值與錯誤行為有文件
* [ ] 沒有暴露不穩定的內部類別
* [ ] 沒有不必要地擴大公開表面
* [ ] 向後相容性已評估
* [ ] API Reference 已更新
* [ ] 使用範例已提供
* [ ] 契約測試已建立

公開 API 一旦被第三方依賴，後續修改成本會顯著增加，因此必須保守設計。

---

## 11. Code Quality

* [ ] 命名能表達意圖
* [ ] 函式長度合理
* [ ] 類別責任集中
* [ ] 沒有重複邏輯
* [ ] 沒有無用程式碼
* [ ] 沒有被註解掉的大段舊程式
* [ ] 沒有不必要的全域變數
* [ ] 沒有魔術數字或隱藏常數
* [ ] 型別標註符合專案標準
* [ ] Docstring 用於公開或複雜介面
* [ ] 註解解釋原因，而不是重述程式碼
* [ ] Ruff 檢查通過
* [ ] Ruff Format 檢查通過

---

## 12. Testing Review

### 12.1 Test Coverage

* [ ] 新功能有測試
* [ ] Bug 修正有回歸測試
* [ ] 正常流程有測試
* [ ] 錯誤流程有測試
* [ ] 邊界條件有測試
* [ ] 公開 API 有契約測試
* [ ] CLI 變更有 CLI 測試
* [ ] Template 變更有渲染測試
* [ ] Generator 變更有整合測試

### 12.2 Test Quality

* [ ] 測試名稱清楚描述行為
* [ ] 測試只驗證一個主要行為
* [ ] 測試不依賴執行順序
* [ ] 測試不依賴本機固定路徑
* [ ] 使用 `tmp_path` 等隔離資源
* [ ] 測試不依賴網路
* [ ] 測試結果具有決定性
* [ ] 失敗訊息容易理解
* [ ] Mock 僅用於隔離外部依賴
* [ ] 沒有為通過測試而測試實作細節

### 12.3 Required Commands

```powershell
python -m pytest
```

覆蓋率檢查：

```powershell
python -m pytest `
    --cov=generator `
    --cov-report=term-missing `
    --cov-report=xml
```

檢查：

* [ ] 完整測試通過
* [ ] 沒有新的 Warning
* [ ] 覆蓋率沒有無理由下降
* [ ] Coverage 設定使用正確套件名稱 `generator`

---

## 13. Documentation Review

* [ ] README 只保留高階摘要
* [ ] 深入內容放在 `docs/`
* [ ] Architecture 文件已更新
* [ ] Reference 文件已更新
* [ ] CLI 範例符合實際行為
* [ ] 設定範例符合實際 Schema
* [ ] 所有連結使用相對路徑
* [ ] 所有連結指向存在檔案
* [ ] 檔案名稱大小寫完全一致
* [ ] 規劃中功能有明確標示
* [ ] 沒有將未完成能力描述為已完成
* [ ] Changelog 已更新（如適用）
* [ ] ADR 已更新（如適用）

---

## 14. Repository Hygiene

* [ ] 未提交 `.venv/`
* [ ] 未提交 `__pycache__/`
* [ ] 未提交 `.pytest_cache/`
* [ ] 未提交 `.ruff_cache/`
* [ ] 未提交 `htmlcov/`
* [ ] 未提交 `.coverage`
* [ ] 未提交 `coverage.xml`，除非 CI 明確需要追蹤
* [ ] 未提交 IDE 個人設定
* [ ] 未提交暫存檔
* [ ] 未提交產生的示範專案，除非它是正式 Fixture 或 Example
* [ ] `.gitignore` 已涵蓋新的產物
* [ ] 沒有大型二進位檔案
* [ ] 沒有敏感資訊或憑證

可使用以下命令檢查：

```powershell
git status --short
git diff --check
git ls-files .venv
git ls-files .pytest_cache
git ls-files .ruff_cache
git ls-files htmlcov
```

---

## 15. Security Review

* [ ] 沒有硬編碼 Token、密碼或憑證
* [ ] 沒有輸出敏感設定
* [ ] 使用者輸入已驗證
* [ ] 檔案路徑已正規化
* [ ] 已防止路徑遍歷
* [ ] 沒有不安全地執行 Shell Command
* [ ] 沒有使用不受信任資料進行動態 Import
* [ ] YAML 載入使用安全方法
* [ ] 外部檔案的信任邊界明確
* [ ] 第三方依賴具有合理來源與用途
* [ ] 安全性行為已有測試

---

## 16. Performance and Resource Review

只有在變更可能影響效能時，才需要深入檢查。

* [ ] 沒有無界限的遞迴或迴圈
* [ ] 沒有重複讀取相同檔案
* [ ] 大型目錄掃描具有合理範圍
* [ ] 檔案與資源會正確關閉
* [ ] 沒有不必要地載入所有 Template
* [ ] 大量輸出不會一次全部保存在記憶體
* [ ] 效能最佳化不會犧牲可讀性
* [ ] 若效能是主要目的，已有量測或 Benchmark

---

## 17. Compatibility Review

* [ ] 支援的 Python 版本已確認
* [ ] Windows 路徑行為已測試
* [ ] POSIX 路徑行為已考量
* [ ] 換行格式一致
* [ ] 檔案名稱大小寫在 Linux 上有效
* [ ] CLI 行為與既有版本相容
* [ ] 設定格式相容性已評估
* [ ] 破壞性變更有清楚說明
* [ ] Migration 或 Upgrade 指引已提供
* [ ] Changelog 已標記相容性影響

---

## 18. Automation Review

提交前應執行：

```powershell
git diff --check
pre-commit run --all-files
python -m pytest
```

若需要 Coverage：

```powershell
python -m pytest `
    --cov=generator `
    --cov-report=term-missing `
    --cov-report=xml
```

確認：

* [ ] `git diff --check` 通過
* [ ] pre-commit 所有 Hook 通過
* [ ] Ruff 通過
* [ ] Ruff Format 通過
* [ ] pytest 通過
* [ ] Coverage 執行成功
* [ ] GitHub Actions 通過
* [ ] Hook 自動修改的檔案已重新檢查
* [ ] Automation 結果與本機環境一致

---

## 19. Commit Review

* [ ] Commit 聚焦單一目的
* [ ] Commit Message 清楚
* [ ] 使用適當的 Conventional Commit 類型
* [ ] 沒有使用無意義訊息
* [ ] Commit 不包含敏感資訊
* [ ] Commit 歷史容易理解
* [ ] 修正 Hook 後的檔案已重新加入暫存區

建議格式：

```text
<type>(<scope>): <description>
```

例如：

```text
feat(generator): add template validation
fix(config): resolve relative template root
docs(architecture): document generator lifecycle
test(cli): cover invalid configuration exit code
refactor(registry): simplify generator lookup
chore(ci): update pre-commit workflow
```

---

## 20. Review Comment Classification

Reviewer 應清楚標示意見的重要程度。

### Blocking

必須修正後才能合併。

適用於：

* 錯誤行為
* 安全性問題
* 架構違規
* 缺少必要測試
* 文件與行為不一致
* 破壞相容性但未說明

範例：

```text
Blocking: 目前 Generator 直接解析 CLI 參數，違反既有依賴方向。
請將參數解析留在 CLI Layer，再將結構化輸入傳入 Generator。
```

### Suggestion

建議修改，但不一定阻擋合併。

適用於：

* 可讀性改善
* 命名改善
* 小型重構
* 非必要效能改善

範例：

```text
Suggestion: 可以將這段路徑驗證抽成具名函式，
讓主要流程更容易閱讀。
```

### Question

需要作者補充背景或設計理由。

範例：

```text
Question: 這裡選擇在 Registry 建立實例，而不是儲存類別，
是否是為了保留 Generator 狀態？
```

### Nit

非常小且不影響功能的意見。

Nit 不應阻擋 Merge。

---

## 21. Author Self-Review

在請求 Review 前，作者應完成：

* [ ] 已重新閱讀全部差異
* [ ] 已移除除錯輸出
* [ ] 已移除暫時註解
* [ ] 已確認沒有意外檔案
* [ ] 已確認 Commit 範圍
* [ ] 已執行測試
* [ ] 已執行 pre-commit
* [ ] 已檢查文件連結
* [ ] 已確認 PR 說明完整
* [ ] 已說明未完成或後續工作

建議命令：

```powershell
git status
git diff
git diff --check
git log --oneline --decorate -5
```

---

## 22. Final Merge Gate

合併前必須確認：

### Design

* [ ] 設計符合 Architecture
* [ ] 必要的 ADR 已完成
* [ ] 責任邊界清楚

### Documentation

* [ ] 使用文件已更新
* [ ] Architecture 或 Reference 已更新
* [ ] Changelog 已更新（如適用）

### Implementation

* [ ] 程式正確
* [ ] 錯誤行為明確
* [ ] 沒有無關變更

### Testing

* [ ] 新增或更新測試
* [ ] 完整測試通過
* [ ] Coverage 沒有無理由下降

### Automation

* [ ] pre-commit 通過
* [ ] CI 通過
* [ ] Repository Hygiene 通過

### Review

* [ ] 所有 Blocking 意見已解決
* [ ] 未解決的 Suggestion 已記錄或接受
* [ ] Maintainer 已核准必要的架構變更

---

## 23. Review Summary Template

Reviewer 可以在 Review 結尾使用以下格式：

```markdown
## Review Summary

### Architecture

- 結果：
- 主要風險：

### Correctness

- 結果：
- 未涵蓋情境：

### Tests

- 結果：
- 建議補充：

### Documentation

- 結果：
- 需更新文件：

### Automation

- pre-commit：
- pytest：
- CI：

### Decision

- [ ] Approve
- [ ] Request changes
- [ ] Comment only
```

---

## 24. Related Documents

* [Architecture Overview](../architecture/overview.md)
* [Development Workflow](development-workflow.md)
* [Coding Style](coding-style.md)
* [Testing Guide](testing.md)
* [Branching Strategy](branching-strategy.md)
* [Release Process](release-process.md)
* [Contributing Guide](../../CONTRIBUTING.md)
* [Security Policy](../../SECURITY.md)

---

> **好的 Code Review 不只是找出錯誤，而是共同維護系統設計、知識與工程品質。**
