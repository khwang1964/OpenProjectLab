# Contributing to OpenProjectLab

Thank you for your interest in contributing to **OpenProjectLab (OPL)**.

OpenProjectLab is an open-source framework for building high-quality educational content, project scaffolding, and automation tools. We welcome contributions of all sizes, including bug fixes, documentation improvements, new generators, templates, tests, and architectural enhancements.

---

# Project Principles

All contributions should follow the core principles of OpenProjectLab:

* **Design First**
* **Documentation First**
* **Automation First**
* **Testing First**
* **Maintainability First**

Every feature should be accompanied by:

* Architecture updates (if applicable)
* Documentation
* Unit or integration tests
* Code review checklist updates (when required)

---

# Development Environment

Recommended environment:

* Python 3.14 or newer
* Git
* Virtual Environment (`.venv`)
* pre-commit
* Ruff
* pytest

Install the project in editable mode:

```powershell
python -m pip install -e .
```

Install development dependencies:

```powershell
python -m pip install -r requirements-dev.txt
```

---

# Coding Standards

Python source code should follow:

* PEP 8
* Type hints
* Google-style docstrings
* Ruff formatting and linting rules

Public modules should include:

* Module docstring
* Public class docstrings
* Public function docstrings

---

# Quality Checks

Before submitting a Pull Request, run:

```powershell
pre-commit run --all-files

ruff check .

ruff format --check .

python -m pytest

python scripts/audit_repository.py
```

All commands must complete successfully.

---

# Pull Requests

A Pull Request should:

* Have a clear title.
* Describe the purpose of the change.
* Reference related issues when applicable.
* Include tests for new functionality.
* Update documentation when behavior changes.

Please keep Pull Requests focused on a single logical change.

---

# Repository Governance

The repository includes automated quality gates.

Examples include:

* Ruff
* pre-commit
* pytest
* Repository Audit
* GitHub Actions

These checks must pass before changes are merged.

---

# Documentation

Documentation is considered part of the source code.

When adding or modifying functionality, update the relevant documentation.

Project documentation includes:

* README
* Architecture
* Configuration
* Development Guides
* Testing Guides
* Code Review Checklist

---

# Reporting Issues

Bug reports should include:

* Operating system
* Python version
* Steps to reproduce
* Expected behavior
* Actual behavior
* Error messages
* Relevant logs

A minimal reproducible example is highly appreciated.

---

# Additional References

Please refer to the following documents:

* `docs/development/python-coding-standard.md`
* `docs/development/testing.md`
* `docs/development/code-review-checklist.md`
* `SECURITY.md`
* `CODE_OF_CONDUCT.md`

Thank you for helping improve OpenProjectLab.
