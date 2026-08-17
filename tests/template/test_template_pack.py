from __future__ import annotations

from pathlib import Path

from generator.resources import package_template_root


def test_template_pack_runtime_resources_exist() -> None:
    """Require the canonical package-owned Template Pack metadata."""
    template_root = package_template_root()

    assert (template_root / "manifest.yaml").is_file()
    assert (template_root / "README.md").is_file()


def test_template_pack_repository_support_files_exist() -> None:
    """Keep development/support files separate from runtime resource ownership."""
    project_root = Path(__file__).resolve().parents[2]

    expected = {
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
