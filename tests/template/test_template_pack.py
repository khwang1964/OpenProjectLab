from __future__ import annotations

from pathlib import Path


def test_template_pack_required_files_exist() -> None:
    project_root = Path(__file__).resolve().parents[2]

    expected = {
        "templates/manifest.yaml",
        "templates/README.md",
        "docs/template-system.md",
        "tests/template/conftest.py",
        "tests/template/test_template_manifest.py",
        "tests/template/test_template_compile.py",
        "tests/template/test_template_render.py",
        "tests/template/test_template_paths.py",
        "tests/template/test_template_contract.py",
        "examples/template-contexts/modern-java.yaml",
        ".github/workflows/template-tests.yml",
        "README.md",
        "README-INSTALL.md",
        "CHANGELOG.md",
        "CODE_REVIEW_CHECKLIST.md",
    }

    missing = [relative for relative in sorted(expected) if not (project_root / relative).is_file()]
    assert missing == []
