import json
from pathlib import Path

from generator.cli.main import build_parser


def _invoke(arguments: list[str]) -> int:
    args = build_parser().parse_args(arguments)
    return args.command_handler(args)


def _write_legacy(path: Path) -> str:
    document = json.dumps(
        {
            "metadata": {},
            "report_document": "{}",
            "report_sha256": "1" * 64,
            "request_document": "{}",
            "request_sha256": "0" * 64,
            "schema_version": "0",
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    path.write_text(document, encoding="utf-8")
    return document


def test_execute_publishes_verified_distinct_output(tmp_path: Path, capsys) -> None:
    source = tmp_path / "source.json"
    output = tmp_path / "output.json"
    original = _write_legacy(source)
    result = _invoke(
        [
            "release-evidence",
            "bundle",
            "migrate",
            "--bundle",
            str(source),
            "--target",
            "1",
            "--output",
            str(output),
            "--execute",
            "--format",
            "json",
        ]
    )
    rendered = json.loads(capsys.readouterr().out)
    assert result == 0
    assert source.read_text(encoding="utf-8") == original
    assert json.loads(output.read_text(encoding="utf-8"))["schema_version"] == "1"
    assert rendered["receipt"]["output_sha256"] == rendered["output_sha256"]


def test_execute_refuses_same_or_existing_output(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    _write_legacy(source)
    arguments = [
        "release-evidence",
        "bundle",
        "migrate",
        "--bundle",
        str(source),
        "--target",
        "1",
        "--output",
        str(source),
        "--execute",
    ]
    assert _invoke(arguments) == 2
    output = tmp_path / "output.json"
    output.write_text("existing", encoding="utf-8")
    arguments[arguments.index(str(source), 6)] = str(output)
    assert _invoke(arguments) == 2
    assert output.read_text(encoding="utf-8") == "existing"


def test_preview_remains_non_mutating(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    _write_legacy(source)
    before = tuple(tmp_path.iterdir())
    assert (
        _invoke(
            [
                "release-evidence",
                "bundle",
                "migrate",
                "--bundle",
                str(source),
                "--target",
                "1",
                "--preview",
            ]
        )
        == 0
    )
    assert tuple(tmp_path.iterdir()) == before


def test_execute_requires_output(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    _write_legacy(source)
    assert (
        _invoke(
            [
                "release-evidence",
                "bundle",
                "migrate",
                "--bundle",
                str(source),
                "--target",
                "1",
                "--execute",
            ]
        )
        == 2
    )
