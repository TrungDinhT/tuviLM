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
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.add_parser(
        "run",
        add_help=False,
        help="Run one workflow over YAML birth profiles.",
    )
    subparsers.add_parser(
        "view",
        add_help=False,
        help="Open a YAML workflow report in Streamlit.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    if not args or args[0] in {"-h", "--help"}:
        parser.print_help()
        return 0

    command = args[0]
    try:
        runner = COMMANDS[command]
    except KeyError:
        parser.error(f"unknown command: {command}")
    return runner(args[1:])


if __name__ == "__main__":
    raise SystemExit(main())
