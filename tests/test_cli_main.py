from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

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


@pytest.mark.parametrize(
    ("arguments", "expected_model"),
    [
        (["--model", "openrouter:qwen/qwen3.8-flash", "run", "input.yaml"],
         "openrouter:qwen/qwen3.8-flash"),
        (["run", "input.yaml", "--model", "openrouter:deepseek/deepseek-v4.1-flash"],
         "openrouter:deepseek/deepseek-v4.1-flash"),
        (["--model", "global-model", "run", "input.yaml", "--model", "run-model"],
         "run-model"),
    ],
)
def test_main_forwards_model_to_workflow_parser(arguments, expected_model, monkeypatch):
    received = []

    def fake_run(argv):
        options = build_workflow_parser().parse_args(argv)
        received.append((options.input, options.model))
        return 0

    monkeypatch.setitem(cli.COMMANDS, "run", fake_run)
    assert cli.main(arguments) == 0
    assert received == [(Path("input.yaml"), expected_model)]


def test_main_rejects_model_for_view():
    with pytest.raises(SystemExit) as error:
        cli.main(["--model", "some-model", "view"])
    assert error.value.code == 2
