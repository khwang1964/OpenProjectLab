from generator.cli.main import build_parser


def test_bundle_commands_are_registered() -> None:
    parser = build_parser()
    create = parser.parse_args(
        [
            "release-evidence",
            "bundle",
            "create",
            "--request",
            "r.json",
            "--report",
            "p.json",
            "--output",
            "b.json",
        ]
    )
    inspect = parser.parse_args(["release-evidence", "bundle", "inspect", "--bundle", "b.json"])
    validate = parser.parse_args(["release-evidence", "bundle", "validate", "--bundle", "b.json"])
    assert create.command_handler.__name__ == "_handle_bundle_create"
    assert inspect.command_handler.__name__ == "_handle_bundle_inspect"
    assert validate.command_handler.__name__ == "_handle_bundle_validate"
