from __future__ import annotations

from collections.abc import Sequence

import pytest

from src.cli import main as cli
from src.cli.view import build_cli_parser
from src.cli.workflow import build_parser as build_workflow_parser


@pytest.mark.parametrize("command", ["run", "view"])
def test_top_level_cli_dispatches_subcommand_arguments(
    command: str,
    monkeypatch: pytest.MonkeyPatch,
):
    received: list[str] = []

    def fake_runner(argv: Sequence[str]) -> int:
        received.extend(argv)
        return 7

    monkeypatch.setitem(cli.COMMANDS, command, fake_runner)

    exit_code = cli.main([command, "input.yaml", "--example"])

    assert exit_code == 7
    assert received == ["input.yaml", "--example"]


def test_top_level_cli_help_lists_run_and_view(capsys: pytest.CaptureFixture[str]):
    assert cli.main(["--help"]) == 0

    output = capsys.readouterr().out
    assert "tuvilm" in output
    assert "run" in output
    assert "view" in output


def test_subcommand_parsers_use_composed_program_names():
    assert build_workflow_parser(prog="tuvilm run").prog == "tuvilm run"
    assert build_cli_parser(prog="tuvilm view").prog == "tuvilm view"


def test_top_level_cli_rejects_unknown_command():
    with pytest.raises(SystemExit) as error:
        cli.main(["missing"])

    assert error.value.code == 2
