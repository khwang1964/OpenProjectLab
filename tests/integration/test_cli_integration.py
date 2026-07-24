from generator.cli.main import main


def test_cli_list(capsys):
    assert main(["list"]) == 0
    assert "course" in capsys.readouterr().out


def test_cli_doctor(capsys):
    from generator.cli.main import main

    assert main(["doctor"]) == 0
    output = capsys.readouterr().out
    assert "[OK] config" in output
    assert "[OK] templates" in output
