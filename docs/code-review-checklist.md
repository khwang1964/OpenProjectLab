# Code Review Checklist

## Architecture
- [ ] 依賴方向符合 CLI → Registry → Generator → Core。
- [ ] 新功能透過 SDK 或外掛擴充，而非修改核心耦合。
## Tests
- [ ] 正常、錯誤、dry-run、force 路徑均有測試。
- [ ] `pytest`、`ruff check .`、`mypy generator` 通過。
## Documentation
- [ ] 使用手冊、設計文件及 ADR 已同步更新。
## Security
- [ ] 不允許未授權覆寫檔案。
- [ ] 模板與設定錯誤具明確訊息。

## v0.6 Doctor / Manifest

- [ ] Doctor 檢查不得修改檔案或設定。
- [ ] CLI exit code 能正確反映檢查結果。
- [ ] Manifest 缺少必要欄位時提供明確錯誤。
- [ ] 新功能具備單元測試與整合測試。
- [ ] README、架構文件、Release Notes 與版本號同步。
- [ ] 保持 `opl list`、Bootstrap、Course、Week 向後相容。
