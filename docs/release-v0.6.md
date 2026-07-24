# OpenProjectLab v0.6 Release Notes

## 新增

- `opl doctor`：檢查設定檔、模板、文件與測試目錄。
- `GeneratorManifest`：載入、驗證與輸出 Generator YAML manifest。
- Doctor 與 Manifest 單元測試及 CLI 整合測試。

## 升級

```powershell
python -m pip install -e ".[dev,docs]"
python -m pytest -v
opl doctor
```

## Exit Code

- `0`：所有檢查通過。
- `1`：至少一項檢查失敗。
