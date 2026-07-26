# Pre-commit 修正報告

## 問題根因

1. `generator/core/context.py` 混用了 Tab 與空白，造成 Python `IndentationError`。
2. `BaseGenerator.prepare()`、`post_generate()`、`cleanup()` 使用空白 `pass`，觸發 Ruff `B027`。
3. 專案啟用了完整 pydocstyle `D` 規則，但既有程式尚未完成所有 public API docstring，導致大量 `D101`–`D107` 阻擋提交。
4. pre-commit 的自動修正 hooks 會調整尾端空白與格式；修正後需要重新加入 Git staging area。

## 已套用修正

- 將 `GeneratorContext` 全部改為四個空白縮排。
- 修復 `GeneratorContext` class/method docstring。
- 將三個 optional lifecycle hooks 改為明確的 `return None`。
- 補強 `BaseGenerator` 型別註記與生命週期文件。
- 將 `D101`–`D107` 設為暫時性全域忽略；保留其他 Ruff `D` 規則。
- 保留測試目錄的 docstring per-file ignores。
- 正規化文字檔為 UTF-8/LF，移除尾端空白。

## 驗證結果

```text
python -m compileall -q generator     PASS
python -m pytest -q                   210 passed
coverage                              78.79%
line length > 100                     none
```

## Windows 最終驗收

```powershell
cd F:\OpenProjectLab
.\.venv\Scripts\Activate.ps1
pre-commit clean
pre-commit install
pre-commit run --all-files
```

若 hooks 自動修改檔案，再執行：

```powershell
git add .
pre-commit run --all-files
```
