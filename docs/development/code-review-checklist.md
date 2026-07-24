# OpenProjectLab Code Review Checklist

## Design

- [ ] 功能責任清楚
- [ ] 沒有不必要的模組耦合
- [ ] 公開 API 已明確定義
- [ ] 錯誤處理方式一致

## Documentation

- [ ] Module docstring 清楚
- [ ] 公開 Class 與 Function 有 docstring
- [ ] 複雜邏輯說明 Why
- [ ] 文件與實作同步
- [ ] TODO/FIXME 可追蹤

## Testing

- [ ] Happy path 已測試
- [ ] Error path 已測試
- [ ] Boundary cases 已測試
- [ ] 不使用真實專案目錄
- [ ] Coverage 沒有下降

## Automation

- [ ] Ruff 通過
- [ ] Formatter 通過
- [ ] pytest 通過
- [ ] pre-commit 通過
- [ ] CI 通過

## Maintainability

- [ ] 命名清楚
- [ ] 沒有 magic number
- [ ] 沒有重複程式碼
- [ ] 沒有過時註解
- [ ] 沒有被註解掉的舊程式碼
