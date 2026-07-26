# OpenProjectLab Python Coding Standard

## 1. 適用範圍

本規範適用於 OpenProjectLab 專案中的所有 Python 原始碼與測試程式。

適用檔案包括：

- `generator/**/*.py`
- `plugins/**/*.py`
- `tests/**/*.py`
- 工具與自動化腳本

## 2. 基本原則

OpenProjectLab 採用以下工程原則：

- Design First
- Documentation First
- Automation First
- Testing First
- Clear Comments
- Maintainability First

## 3. Module Docstring

每個 `.py` 檔案都必須具有 module docstring，用來說明：

- 模組用途
- 主要責任
- 重要設計決策
- 主要資料流程
- 不負責的範圍

範例：

```python
"""
提供 OpenProjectLab 的檔案系統操作介面。

本模組集中處理目錄建立、文字檔案寫入及覆寫控制，
避免 Generator 直接依賴底層 pathlib 操作。
"""
"""
OpenProjectLab (OPL)

File:
    generator/core/filesystem.py

Purpose:
    提供統一的檔案系統操作介面，包含建立目錄、讀寫檔案、
    複製模板、建立專案結構等功能。

Author:
    OpenProjectLab

Copyright:
    MIT License
"""

class FileSystem:
    """
    封裝所有檔案系統相關操作。

    設計目的：

    - 避免直接使用 pathlib
    - 集中處理例外
    - 支援 dry-run
    - 提高可測試性
    """

 def write_text(path: Path, content: str) -> None:
    """
    將文字寫入指定檔案。

    Parameters
    ----------
    path:
        輸出檔案

    content:
        UTF-8 文字內容

    Raises
    ------
    FileSystemError
        寫入失敗時拋出。
    """

# --------------------------------------------------
# 載入 YAML 設定檔
# 若不存在會拋出 ConfigurationError
# --------------------------------------------------

config = load_config()

# 使用 BFS 掃描 Plugin 相依性。
#
# 不使用 DFS 的原因：
# 1. 可以較容易偵測循環相依
# 2. Plugin 載入順序較容易控制

# 等待 Plugin 初始化完成
# 超過 30 秒視為失敗

PLUGIN_TIMEOUT = 30


# TODO(OPLv0.8):
# 支援非同步 Plugin Loader

# FIXME:
# Windows UNC Path 尚未支援，
# Issue #28

# 每個 Plugin 只允許註冊一次，
# 避免重複覆寫 Generator。
registry.add(plugin)
