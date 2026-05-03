from __future__ import annotations

from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter
from pydantic_evals.reporting import EvaluationReportAdapter

from src.evals.dataset import load_dataset
from src.evals.tasks import build_tuvi_eval_task



app = App(help="Run and render Tu Vi agent evals.")


@app.command
def run(
    data: Annotated[
        Path,
        Parameter(help="Path to eval dataset YAML."),
    ],
    model: Annotated[
        str,
        Parameter(help="Pydantic AI model name passed to the Tu Vi agent."),
    ] = "openai:gpt-4.1-mini",
    book_root: Annotated[
        str,
        Parameter(help="Path to the root of the book data used by the agent."),
    ] = "./data/tuvitanbien_chunking_compact/part_2",
    case_names: Annotated[
        list[str] | None,
        Parameter(name="--case", help="Run only the named case. Can be passed multiple times."),
    ] = None,
    max_concurrency: Annotated[
        int,
        Parameter(help="Maximum concurrent cases."),
    ] = 1,
    repeat: Annotated[
        int,
        Parameter(help="Number of times to repeat each case."),
    ] = 1,
    include_output: Annotated[
        bool,
        Parameter(help="Print model outputs in the report."),
    ] = False,
    output: Annotated[
        Path | None,
        Parameter(alias="-o", help="Save the evaluation report to this JSON file."),
    ] = None,
    hide_reasons: Annotated[
        bool,
        Parameter(help="Hide assertion names and reasons in the report."),
    ] = False,
) -> None:
    """Run the eval dataset and optionally save the report."""

    dataset = load_dataset(data)
    if case_names:
        wanted = set(case_names)
        dataset.cases = [case for case in dataset.cases if case.name in wanted]
        missing = wanted - {case.name for case in dataset.cases}
        if missing:
            raise SystemExit(f"Unknown case name(s): {', '.join(sorted(missing))}")

    task = build_tuvi_eval_task(model=model, book_root=book_root)
    report = dataset.evaluate_sync(
        task,
        max_concurrency=max_concurrency,
        repeat=repeat,
        task_name="tuvi_agent",
        metadata={"model": model},
    )
    if output:
        _save_report(report, output)

    _print_report(
        report,
        include_output=include_output,
        include_reasons=not hide_reasons,
    )


@app.command
def render(
    report_file: Annotated[
        Path,
        Parameter(help="Path to a JSON report produced by the run command."),
    ],
    include_output: Annotated[
        bool,
        Parameter(help="Print model outputs in the report."),
    ] = False,
    hide_reasons: Annotated[
        bool,
        Parameter(help="Hide assertion names and reasons in the report."),
    ] = False,
    include_input: Annotated[
        bool,
        Parameter(help="Print eval inputs in the report."),
    ] = True,
) -> None:
    """Render a saved eval report."""

    report = EvaluationReportAdapter.validate_json(report_file.read_bytes())
    _print_report(
        report,
        include_input=include_input,
        include_output=include_output,
        include_reasons=not hide_reasons,
    )


def _save_report(report: object, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(EvaluationReportAdapter.dump_json(report, indent=2))
    print(f"Saved evaluation report to {output}")


def _print_report(
    report: object,
    *,
    include_input: bool = True,
    include_output: bool = False,
    include_reasons: bool = True,
) -> None:
    report.print(
        include_input=include_input,
        include_output=include_output,
        include_reasons=include_reasons,
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
