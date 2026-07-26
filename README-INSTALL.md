# Step 12 Upgrade/Patch System 安裝

## 1. 安裝前備份

```powershell
cd F:\OpenProjectLab

git status
git add .
git commit -m "chore: backup before step 12"
```

## 2. 解壓縮

將本更新包直接解壓到：

```text
F:\OpenProjectLab
```

本套件新增：

```text
generator/core/upgrade.py
generator/cli/upgrade.py
tests/core/test_upgrade.py
tests/integration/test_upgrade_cli.py
docs/upgrade-system.md
docs/upgrade-manifest-schema.md
examples/example-upgrade-patch.zip
```

## 3. 整合 `main.py`

依照：

```text
generator/cli/UPGRADE-INTEGRATION.md
```

加入 `upgrade` 子命令。

## 4. 執行測試

```powershell
python -m pytest `
  tests/core/test_upgrade.py `
  tests/integration/test_upgrade_cli.py `
  -v --no-cov
```

## 5. CLI 驗收

```powershell
opl upgrade .\examples\example-upgrade-patch.zip
```

預期只顯示計畫，不修改檔案。

套用：

```powershell
opl upgrade `
  .\examples\example-upgrade-patch.zip `
  --apply
```

確認：

```powershell
Test-Path .\docs\upgrade-example.md
```

預期：

```text
True
```
