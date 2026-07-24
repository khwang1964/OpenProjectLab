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


docs/
│
├── README.md                 ← 文件首頁
├── getting-started.md        ← 5 分鐘快速開始
├── installation.md           ← 安裝
├── configuration.md          ← 設定檔（已完成）
├── cli.md                    ← CLI 使用說明
├── generators.md             ← Generator Framework
├── templates.md              ← Template Engine
├── plugins.md                ← Plugin System
├── architecture.md           ← 系統架構
├── developer-guide.md        ← Developer Guide
├── testing.md                ← Testing Guide
├── coding-style.md           ← Coding Style
├── roadmap.md                ← Development Roadmap
└── release-notes.md          ← Release Notes

下一個里程碑（v0.6）

目前專案已經有了：

✅ Config
✅ Registry
✅ CLI
✅ Tests

接下來，我建議把重心放在架構穩定化，而不是急著增加功能。

Milestone v0.6：Foundation Complete

Design

完成 Generator Framework
完成 Template Engine API
完成 Plugin API

Documentation

完成 docs/ 第一版
為所有公開 API 撰寫文件
建立 Architecture Decision Records (ADR)

Automation

GitHub Actions：Lint + Test + Coverage
自動產生 API 文件
自動檢查 Markdown 連結與格式

Quality

測試覆蓋率達 90%+
ruff、black、mypy 全數通過
每個新功能都附帶文件、測試與 Code Review Checklist

這樣完成後，OpenProjectLab 就會從「一個能運作的專案」提升為「一個具有專業開源專案基礎設施的框架」。
