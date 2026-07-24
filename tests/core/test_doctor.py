from pathlib import Path

from generator.core.doctor import run_doctor


def test_doctor_reports_expected_project_directories(tmp_path: Path) -> None:
    (tmp_path / "templates").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "tests").mkdir()
    config = tmp_path / "default.yaml"
    config.write_text("paths:\n  templates: templates\n", encoding="utf-8")

    checks = run_doctor(config, tmp_path)

    assert checks
    assert all(check.ok for check in checks)


def test_doctor_stops_after_invalid_config(tmp_path: Path) -> None:
    checks = run_doctor(tmp_path / "missing.yaml", tmp_path)
    assert len(checks) == 1
    assert checks[0].name == "config"
    assert not checks[0].ok
