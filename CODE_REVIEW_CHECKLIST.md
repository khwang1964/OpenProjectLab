# Step 12 Code Review Checklist

## Architecture

- [ ] CLI 僅負責輸入輸出與 exit code
- [ ] UpgradeManager 負責完整升級流程
- [ ] Manifest parsing 與 apply 邏輯分離
- [ ] Plan 與 Apply 採兩階段設計

## Security

- [ ] 禁止絕對路徑
- [ ] 禁止 `..`
- [ ] 禁止 Windows 保留名稱
- [ ] ZIP member 在 extract 前驗證
- [ ] Payload SHA256 必須驗證
- [ ] source SHA256 衝突預設拒絕
- [ ] 不允許目標逃逸 project root

## Reliability

- [ ] 修改前建立備份
- [ ] Apply 發生例外時 rollback
- [ ] Delete 操作可備份舊檔
- [ ] Upgrade report 可追蹤
- [ ] Preview 模式不修改檔案

## Tests

- [ ] Path traversal 測試
- [ ] Duplicate path 測試
- [ ] Preview 無副作用測試
- [ ] Add/modify/delete 測試
- [ ] Backup 測試
- [ ] Conflict 測試
- [ ] Integrity 測試
- [ ] CLI preview 測試
- [ ] CLI apply 測試

## Documentation

- [ ] 架構文件已更新
- [ ] Manifest schema 已文件化
- [ ] 安裝說明已完成
- [ ] CLI 範例已完成
- [ ] CHANGELOG 已更新
