import json
from pathlib import Path

from generator.cli.main import build_parser


def _invoke(arguments: list[str]) -> int:
    args = build_parser().parse_args(arguments)
    return args.command_handler(args)


def test_bundle_compatibility_reports_current_schema(tmp_path: Path, capsys) -> None:
    bundle = tmp_path / "bundle.json"
    bundle.write_text(json.dumps({"schema_version": "1"}), encoding="utf-8")
    result = _invoke(
        [
            "release-evidence",
            "bundle",
            "compatibility",
            "--bundle",
            str(bundle),
            "--format",
            "json",
        ]
    )
    assert result == 0
    assert json.loads(capsys.readouterr().out)["category"] == "CURRENT"


def test_bundle_compatibility_fails_closed_for_unknown_schema(tmp_path: Path, capsys) -> None:
    bundle = tmp_path / "bundle.json"
    bundle.write_text(json.dumps({"schema_version": "unknown"}), encoding="utf-8")
    result = _invoke(["release-evidence", "bundle", "compatibility", "--bundle", str(bundle)])
    assert result == 1
    assert "UNSUPPORTED" in capsys.readouterr().out


def test_bundle_migration_preview_never_writes_output(tmp_path: Path, capsys) -> None:
    bundle = tmp_path / "bundle.json"
    bundle.write_text(json.dumps({"schema_version": "0"}), encoding="utf-8")
    before = tuple(tmp_path.iterdir())
    result = _invoke(
        [
            "release-evidence",
            "bundle",
            "migrate",
            "--bundle",
            str(bundle),
            "--target",
            "1",
            "--preview",
            "--format",
            "json",
        ]
    )
    assert result == 0
    assert tuple(tmp_path.iterdir()) == before
    assert json.loads(capsys.readouterr().out)["steps"] == ["upgrade-0-to-1"]
