# Pre-commit Fix Code Review Checklist

## Architecture

- [x] Generator lifecycle hooks 保持 optional，不錯誤改成 abstract method。
- [x] `BaseGenerator.run()` 保留失敗狀態與 finally cleanup 語意。
- [x] Ruff policy 調整集中於 `pyproject.toml`。

## Correctness

- [x] 所有 `generator/**/*.py` 可編譯。
- [x] `GeneratorContext` 不含混合 Tab/space。
- [x] Optional hooks 不再觸發 `B027`。
- [x] 沒有超過 100 字元的 Python 程式行。

## Tests

- [x] 完整 pytest：210 passed。
- [x] Coverage：78.79%，高於 67% threshold。
- [x] Upgrade/Patch System tests 通過。
- [x] Template Pack tests 通過。

## Documentation

- [x] 根因與修正方式已記錄。
- [x] Windows pre-commit 驗收步驟已提供。
- [x] 後續 docstring debt 已明確標示為漸進式改善項目。
