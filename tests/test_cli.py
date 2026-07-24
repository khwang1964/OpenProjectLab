from generator.cli.main import main


def test_list_command(capsys):
    assert main(["list"]) == 0
    output = capsys.readouterr().out
    assert "bootstrap" in output
    assert "course" in output
    assert "week" in output


def test_legacy_list_option(capsys):
    assert main(["--list"]) == 0
    output = capsys.readouterr().out
    assert "bootstrap" in output
    assert "course" in output
    assert "week" in output
