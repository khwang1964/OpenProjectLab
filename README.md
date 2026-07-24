# OpenProjectLab v0.6 Framework

OpenProjectLab（OPL）是以 **Design First、Documentation First、Automation First** 為原則的開源教育內容產生框架。

## v0.6 功能

- YAML 組態系統
- Jinja2 模板引擎
- Generator SDK 與標準生命週期
- 外掛發現與註冊機制
- `opl` CLI
- `opl doctor` 專案健康檢查
- Generator Manifest（YAML）
- Bootstrap、Course、Week Generator
- MkDocs 文件網站
- pytest、Ruff、mypy、GitHub Actions

## 安裝與測試

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev,docs]"
pytest
ruff check .
```

## CLI

```bash
opl list
opl doctor
opl bootstrap --output DemoOPL --project-name "Demo OPL"
opl course --output courses/python --course-id python --title "Python 程式設計"
opl week --output courses/python/week-01 --week 1 --title "課程介紹"
```

git clone <repo>

cd OpenProjectLab

python -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

python -m pip install -e .

python -m pytest

opl list