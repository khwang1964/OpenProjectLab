# `generator/cli/main.py` 整合方式

## 1. Import

加入：

```python
from generator.cli.upgrade import add_upgrade_parser
```

## 2. 建立子命令

在 `subparsers = parser.add_subparsers(...)` 之後加入：

```python
add_upgrade_parser(subparsers)
```

## 3. Handler 分派

在：

```python
args = parser.parse_args(argv)
```

之後加入：

```python
handler = getattr(args, "command_handler", None)
if handler is not None:
    return handler(args)
```

若目前 `main.py` 已採用 `command_handler` 架構，只需要加入
`add_upgrade_parser(subparsers)`。

## 4. Project root

若目前 CLI parser 尚未提供 `project_root`，可在 `parse_args()` 後加入：

```python
args.project_root = PROJECT_ROOT
```
