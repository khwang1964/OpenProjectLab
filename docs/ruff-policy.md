# Ruff Policy

## Purpose

OpenProjectLab uses Ruff for Python linting and formatting.

The project contains Traditional Chinese documentation, command-line messages,
comments, templates, and test fixtures. Traditional Chinese full-width
punctuation is therefore valid project content.

## Enabled rule groups

The project enables rules for:

- Python syntax and correctness
- Import ordering
- Modern Python practices
- Common bug patterns
- Docstring requirements
- Ruff-specific quality checks

## Unicode policy

The following rules are intentionally ignored:

- `RUF001`: ambiguous Unicode characters in strings
- `RUF002`: ambiguous Unicode characters in docstrings
- `RUF003`: ambiguous Unicode characters in comments

These rules report normal Traditional Chinese punctuation such as:

- `，`
- `。`
- `：`
- `；`
- `（`
- `）`

Ignoring these rules allows OpenProjectLab to preserve natural Traditional
Chinese writing.

This exception does not permit visually ambiguous Unicode characters in Python
identifiers. Code identifiers should remain ASCII unless a future architecture
decision explicitly permits otherwise.

## Validation commands

```powershell
ruff check .
ruff format --check .
pre-commit run --all-files


最後一段 Markdown code fence 請確認完整關閉。

---

## 6. 更新 Repository Audit

在 `scripts/audit_repository.py` 的 `REQUIREMENTS` 加入：

```python
RepositoryRequirement("docs/ruff-policy.md"),
