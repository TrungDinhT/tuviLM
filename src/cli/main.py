"""Top-level ``tuvilm`` command dispatcher."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence

CommandRunner = Callable[[Sequence[str]], int]


def _run_workflow(argv: Sequence[str]) -> int:
    from src.cli.workflow import main as workflow_main

    return workflow_main(argv, prog="tuvilm run")


def _view_report(argv: Sequence[str]) -> int:
    from src.cli.view import cli_main as view_main

    return view_main(argv, prog="tuvilm view")


COMMANDS: dict[str, CommandRunner] = {
    "run": _run_workflow,
    "view": _view_report,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tuvilm",
        description="Run Tử Vi workflows and view their YAML reports.",
    )
    parser.add_argument(
        "--model",
        metavar="PROVIDER:MODEL",
        help=(
            "Model for the run command, e.g. openrouter:qwen/qwen3.8-flash. "
            "May also be passed after run. Defaults to the workflow model setting."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.add_parser(
        "run",
        add_help=False,
        help="Run one workflow over YAML birth profiles.",
    )
    subparsers.add_parser(
        "view",
        add_help=False,
        help="Compare strength/weakness reports and diversity in Streamlit.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    if not args or args[0] in {"-h", "--help"}:
        parser.print_help()
        return 0

    options, command_args = parser.parse_known_args(args)
    if options.command is None:
        parser.error("a command is required: run or view")
    if options.model is not None:
        if options.command != "run":
            parser.error("--model is only supported with the run command")
        # A model explicitly supplied after run overrides this global default.
        command_args = ["--model", options.model, *command_args]
    return COMMANDS[options.command](command_args)


if __name__ == "__main__":
    raise SystemExit(main())
