# Contributing to OpenProjectLab

感謝參與 OpenProjectLab。

所有 Python 程式碼必須遵循：

- Design First
- Documentation First
- Automation First
- Testing First
- Clear Comments

完整規範請參閱：

- [Python Coding Standard](docs/development/python-coding-standard.md)
- [Testing Guide](docs/development/testing.md)
- [Code Review Checklist](docs/development/code-review-checklist.md)

提交程式碼前請執行：

```powershell
python -m pre_commit run --all-files
python -m pytest
