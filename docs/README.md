# OpenProjectLab

OpenProjectLab (OPL) is an extensible project generation framework designed for
building software projects, teaching materials, documentation, and reusable
project templates.

The project follows three core principles:

- Design First
- Documentation First
- Automation First

---

# Features

Current features

- YAML-based configuration
- Generator registry
- Template rendering
- CLI framework
- Plugin architecture (under development)

Future features

- Project scaffolding
- Course generator
- Documentation generator
- Plugin marketplace
- AI-assisted template generation

---

# Installation

Clone the repository

```bash
git clone https://github.com/your-org/OpenProjectLab.git
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate it

Windows

```powershell
.venv\Scripts\activate
```

Install

```bash
pip install -e .
```

---

# Quick Start

List available generators

```bash
opl list
```

Bootstrap a project

```bash
opl bootstrap
```

Generate a course

```bash
opl course
```

---

# Documentation

See the documentation in

```
docs/
```

especially

- getting-started.md
- configuration.md
- architecture.md

---

# Project Structure

```text
OpenProjectLab/
│
├── config/
├── docs/
├── generator/
├── templates/
├── tests/
└── pyproject.toml
```

---

# Development

Run tests

```bash
pytest
```

or

```bash
pytest -v
```

---

# License

MIT License