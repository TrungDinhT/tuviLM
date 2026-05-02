from __future__ import annotations

import argparse
from pathlib import Path

from src.agent.main import DEFAULT_MODEL
from src.evals.dataset import DEFAULT_DATASET_PATH, load_dataset
from src.evals.tasks import build_tuvi_eval_task


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Tu Vi agent evals.")
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help="Path to eval dataset YAML.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Pydantic AI model name passed to the Tu Vi agent.",
    )
    parser.add_argument(
        "--case",
        action="append",
        dest="case_names",
        help="Run only the named case. Can be passed multiple times.",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=1,
        help="Maximum concurrent cases.",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Number of times to repeat each case.",
    )
    parser.add_argument(
        "--include-output",
        action="store_true",
        help="Print model outputs in the report.",
    )
    parser.add_argument(
        "--hide-reasons",
        action="store_true",
        help="Hide assertion names and reasons in the report.",
    )
    args = parser.parse_args()

    dataset = load_dataset(args.data)
    if args.case_names:
        wanted = set(args.case_names)
        dataset.cases = [case for case in dataset.cases if case.name in wanted]
        missing = wanted - {case.name for case in dataset.cases}
        if missing:
            raise SystemExit(f"Unknown case name(s): {', '.join(sorted(missing))}")

    task = build_tuvi_eval_task(model=args.model)
    report = dataset.evaluate_sync(
        task,
        max_concurrency=args.max_concurrency,
        repeat=args.repeat,
        task_name="tuvi_agent",
        metadata={"model": args.model},
    )
    report.print(
        include_input=True,
        include_output=args.include_output,
        include_reasons=not args.hide_reasons,
    )


if __name__ == "__main__":
    main()
