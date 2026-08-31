from pathlib import Path

from generator.cli.main import build_parser


def test_stable_request_validate_parser_is_exact() -> None:
    args = build_parser().parse_args(
        ["release-evidence", "request", "validate", "--request", "r.json", "--format", "json"]
    )
    assert args.command == "release-evidence"
    assert args.request_command == "validate"


def test_bilingual_manuals_share_stable_commands_and_boundaries() -> None:
    root = Path(__file__).resolve().parents[2]
    texts = [
        (root / "docs/user-guide/en/cli.md").read_text(encoding="utf-8"),
        (root / "docs/user-guide/zh-TW/cli.md").read_text(encoding="utf-8"),
    ]
    for text in texts:
        assert "release-evidence verify --request FILE --format json|text" in text
        assert "release-evidence request validate --request FILE --format json|text" in text
        assert "stdout" in text and "stderr" in text
