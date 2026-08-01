# Filesystem Reference

Version: 1.0

---

# Overview

OpenProjectLab (OPL) 採用一致且可預測（Predictable）的檔案系統架構。

所有 Generator、CLI、Template 與 Plugin
皆透過統一的 Filesystem API 存取檔案。

本文件說明：

- 目錄結構
- Path Resolution
- 檔案建立規則
- Encoding
- Newline Policy
- Atomic Write
- Dry Run
- 安全限制

---

# Directory Layout

典型專案：

```
project/

├── config/
│   └── default.yaml
│
├── generator/
│
├── plugins/
│
├── templates/
│
├── courses/
│
├── output/
│
├── docs/
│
└── tests/
```

---

# Project Root

Project Root 為：

```
git repository root
```

例如：

```
F:\OpenProjectLab
```

所有 Relative Path
皆以 Project Root 為基準。

---

# Template Root

Template Root 預設：

```
templates/
```

例如：

```
templates/course
templates/week
templates/bootstrap
```

可於：

```
config/default.yaml
```

修改：

```yaml
paths:
  template_root: templates
```

---

# Output Root

預設：

```
output/
```

可修改：

```yaml
paths:
  output_root: output
```

例如：

```
output/course/
output/week01/
```

---

# Configuration Root

所有設定檔：

```
config/
```

例如：

```
config/default.yaml
```

CLI：

```
opl --config config/dev.yaml
```

可指定其他設定。

---

# Relative Path Resolution

Relative Path：

```
templates/course
```

解析為：

```
<ProjectRoot>/templates/course
```

Absolute Path：

```
D:\Templates
```

保持原樣。

---

# Supported Path Types

支援：

- Relative Path
- Absolute Path
- Windows Path
- POSIX Path（於 Linux）

不支援：

- URL
- UNC Network Path（目前）

---

# File Creation

Generator 可建立：

- directory
- markdown
- yaml
- json
- txt

Binary File：

目前不支援。

---

# Existing File Policy

預設：

```
不覆蓋
```

若已存在：

```
FileAlreadyExistsError
```

CLI：

```
--force
```

允許覆寫。

---

# Directory Creation

建立檔案前：

```
mkdir(parents=True, exist_ok=True)
```

自動建立父目錄。

---

# Encoding

所有文字檔：

```
UTF-8
```

禁止：

- Big5
- UTF16
- ANSI

---

# BOM

所有 UTF-8：

```
No BOM
```

---

# Newline Policy

統一：

```
LF
```

即：

```
\n
```

Git 自動轉換 CRLF。

---

# Trailing Newline

所有文字檔：

```
最後一行必須有 newline
```

符合：

```
pre-commit
```

要求。

---

# Trailing Spaces

禁止：

```
line····
```

所有尾端空白必須移除。

---

# Atomic Write

所有寫入流程：

```
tmp file

↓

flush

↓

replace()
```

避免：

- 半寫入
- 中途中斷

---

# Safe Write

禁止：

```
../../
```

跳離 Project Root。

例如：

```
../../../Windows/System32
```

將直接拒絕。

---

# Dry Run

CLI：

```
opl bootstrap --dry-run
```

行為：

- 不建立檔案
- 不修改資料
- 顯示預計動作

例如：

```
CREATE README.md
CREATE config/default.yaml
CREATE docs/
```

---

# File Operation Result

成功：

```
Created:

README.md

docs/

templates/
```

失敗：

```
Error:

Permission denied

Output directory not writable
```

---

# File Permissions

建立檔案：

採用 OS Default。

目前不修改：

- ACL
- chmod

---

# Temporary Files

Atomic Write 使用：

```
.tmp
```

完成後立即移除。

---

# Logging

Filesystem Operation 可輸出：

```
INFO

DEBUG
```

例如：

```
Create:

README.md
```

```
Skip:

docs/
```

```
Overwrite:

README.md
```

---

# Exceptions

Filesystem 常見例外：

```
ConfigurationError
```

```
FileAlreadyExistsError
```

```
PermissionDeniedError
```

```
TemplateNotFoundError
```

```
OutputError
```

詳細請參考：

```
docs/reference/errors.md
```

---

# CLI Examples

建立專案：

```
opl bootstrap Demo
```

Dry Run：

```
opl bootstrap Demo --dry-run
```

Force：

```
opl bootstrap Demo --force
```

指定 Config：

```
opl bootstrap Demo --config config/dev.yaml
```

---

# Python API

```python
from pathlib import Path

from generator.core.filesystem import FileSystem

fs = FileSystem()

fs.write_text(
    Path("README.md"),
    "# Hello"
)
```

---

# Testing

Filesystem 測試涵蓋：

- Relative Path
- Absolute Path
- Invalid Path
- Permission Error
- Existing File
- Dry Run
- Atomic Write
- UTF-8
- LF
- Directory Creation

測試位置：

```
tests/core/
```

---

# Best Practices

建議：

- 永遠使用 Pathlib
- 永遠使用 UTF-8
- 永遠使用 Atomic Write
- 永遠不要直接 open() 寫入核心 Generator
- 永遠使用 Filesystem API

---

# Related Documents

Architecture：

```
docs/architecture/filesystem.md
```

Errors：

```
docs/reference/errors.md
```

Configuration：

```
docs/configuration.md
```

Manifest：

```
docs/reference/manifest.md
```
