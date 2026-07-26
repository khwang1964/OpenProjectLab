# OpenProjectLab Template Pack v1.1 安裝說明

## 安裝位置

將 ZIP 中的 `templates`、`tests` 與 `docs` 複製到：

```text
F:\OpenProjectLab
```

最重要的是確認以下檔案存在：

```text
F:\OpenProjectLab\templates\bootstrap\project\README.md.j2
```

## 驗證安裝

```powershell
Test-Path .\templates\bootstrap\project\README.md.j2
```

預期：

```text
True
```

執行模板測試：

```powershell
python -m pytest tests/template/test_template_pack.py -v --no-cov
```

執行 Bootstrap：

```powershell
opl bootstrap modern-java `
  --name "Modern Java in Action"
```

若先前已建立部分目錄，可加上：

```powershell
--force
```

完整命令：

```powershell
opl bootstrap modern-java `
  --name "Modern Java in Action" `
  --force
```

## v1.1 修正

本版本明確包含：

```text
tests/template/test_template_pack.py
```

驗證方式：

```powershell
Test-Path .\tests\template\test_template_pack.py
```

預期：

```text
True
```
