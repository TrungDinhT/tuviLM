"""Run one agent workflow over a YAML list of birth profiles."""

from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import os
import sys
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from src.agent.deps import TuviAgentDeps
from src.agent.workflow.personality import (
    build_personality_agent,
    run_personality_workflow,
)
from src.agent.workflow.strength_weakness import (
    build_strength_weakness_agent,
    run_strength_weakness_agent,
)
from src.refactored.la_so import LaSo
from src.refactored.model.prior import Gender, LaSoPrior

DEFAULT_MODEL = "openrouter:qwen/qwen3.7-max"
DEFAULT_BOOK_ROOT = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "tuvitanbien_chunking_compact"
    / "part_2"
)


class ProfileGender(StrEnum):
    MALE = "male"
    FEMALE = "female"


class ProfileInput(BaseModel):
    """One solar-calendar profile accepted by the batch CLI."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1)
    birth_date: dt.date
    birth_time: int = Field(ge=0, le=23, strict=True)
    gender: ProfileGender

    @field_validator("birth_date", mode="before")
    @classmethod
    def _parse_birth_date(cls, value: object) -> object:
        if isinstance(value, dt.datetime):
            return value.date()
        if isinstance(value, dt.date):
            return value
        if not isinstance(value, str):
            return value

        for date_format in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
            try:
                return dt.datetime.strptime(value.strip(), date_format).date()
            except ValueError:
                pass
        raise ValueError("birth_date must use YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY")

    @field_validator("gender", mode="before")
    @classmethod
    def _parse_gender(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        normalized = value.strip().casefold()
        aliases = {
            "m": ProfileGender.MALE,
            "male": ProfileGender.MALE,
            "nam": ProfileGender.MALE,
            "f": ProfileGender.FEMALE,
            "female": ProfileGender.FEMALE,
            "nu": ProfileGender.FEMALE,
            "nữ": ProfileGender.FEMALE,
        }
        return aliases.get(normalized, value)

    def as_payload(self) -> dict[str, str | int]:
        return {
            "name": self.name,
            "birth_date": self.birth_date.isoformat(),
            "birth_time": self.birth_time,
            "gender": self.gender.value,
        }

    def build_la_so(self) -> LaSo:
        solar_time = dt.datetime.combine(
            self.birth_date,
            dt.time(hour=self.birth_time),
        )
        gender = Gender.MALE if self.gender is ProfileGender.MALE else Gender.FEMALE
        return LaSo.from_prior(LaSoPrior.from_solar_day(solar_time, gender))


WorkflowRunner = Callable[[Any, TuviAgentDeps], Awaitable[Any]]

_PERSONALITY_PROMPT = "Hãy luận giải tính cách và chân dung con người của tôi."
_STRENGTH_WEAKNESS_PROMPT = (
    "Hãy khám phá những điểm mạnh, điểm yếu và mặt trái nổi bật nhất "
    "trong cách tôi sử dụng năng lực của mình."
)


@dataclass(frozen=True, slots=True)
class WorkflowDefinition:
    name: str
    description: str
    build_agent: Callable[[str], Any]
    run: WorkflowRunner


async def _run_personality(agent: Any, deps: TuviAgentDeps) -> str:
    return await run_personality_workflow(
        agent=agent,
        deps=deps,
        request=_PERSONALITY_PROMPT,
    )


async def _run_strength_weakness(
    agent: Any,
    deps: TuviAgentDeps,
) -> BaseModel:
    return await run_strength_weakness_agent(
        agent=agent,
        deps=deps,
        request=_STRENGTH_WEAKNESS_PROMPT,
    )


WORKFLOWS: dict[str, WorkflowDefinition] = {
    "personality": WorkflowDefinition(
        name="personality",
        description="Luận tính cách theo bảy câu hỏi nền tảng",
        build_agent=build_personality_agent,
        run=_run_personality,
    ),
    "strength_weakness": WorkflowDefinition(
        name="strength_weakness",
        description="Khám phá điểm mạnh, điểm yếu và mặt trái năng lực",
        build_agent=build_strength_weakness_agent,
        run=_run_strength_weakness,
    ),
}


@dataclass(frozen=True, slots=True)
class BatchRunSummary:
    output_path: Path
    succeeded: int
    failed: int


def load_profiles(input_path: Path) -> list[ProfileInput]:
    """Load and validate a non-empty top-level YAML list."""
    raw = yaml.safe_load(input_path.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not raw:
        raise ValueError("Input YAML must be a non-empty top-level list of profiles.")
    return [ProfileInput.model_validate(item) for item in raw]


def default_output_path(
    workflow_name: str,
    *,
    timestamp: dt.datetime | None = None,
    output_dir: Path = Path.cwd(),  # noqa: B008
) -> Path:
    timestamp = timestamp or dt.datetime.now().astimezone()
    filename = f"cli__{workflow_name}_{timestamp:%Y-%m-%d}__{timestamp:%H-%M-%S}.yaml"
    return output_dir / filename


def _serialize_workflow_output(output: Any) -> Any:
    if isinstance(output, BaseModel):
        return output.model_dump(mode="json")
    return output


def _write_output(output_path: Path, document: Mapping[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_name(f".{output_path.name}.tmp")
    with temporary_path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(
            dict(document),
            file,
            allow_unicode=True,
            sort_keys=False,
            width=100,
        )
    os.replace(temporary_path, output_path)


async def run_workflow_batch(
    *,
    definition: WorkflowDefinition,
    profiles: Sequence[ProfileInput],
    model: str,
    output_path: Path,
    book_root: Path = DEFAULT_BOOK_ROOT,
    status: Callable[[str], None] | None = print,
) -> BatchRunSummary:
    """Run profiles sequentially and checkpoint the result after each profile."""
    document: dict[str, Any] = {
        "workflow": definition.name,
        "model": model,
        "results": [],
    }
    _write_output(output_path, document)

    agent = definition.build_agent(model)
    succeeded = 0
    failed = 0
    results: list[dict[str, Any]] = document["results"]

    for index, profile in enumerate(profiles, start=1):
        if status is not None:
            status(f"[{index}/{len(profiles)}] Running {profile.name}...")
        result: dict[str, Any] = {"profile": profile.as_payload()}
        try:
            deps = TuviAgentDeps(
                la_so=profile.build_la_so(),
                book_root=book_root,
            )
            workflow_output = await definition.run(agent, deps)
            result["output"] = _serialize_workflow_output(workflow_output)
            succeeded += 1
        except Exception as exc:  # Preserve other profiles after one model failure.
            result["error"] = {
                "type": type(exc).__name__,
                "message": str(exc),
            }
            failed += 1
            if status is not None:
                status(f"[{index}/{len(profiles)}] Failed {profile.name}: {exc}")
        results.append(result)
        _write_output(output_path, document)

    document["completed_at"] = (
        dt.datetime.now().astimezone().isoformat(timespec="seconds")
    )
    document["summary"] = {"succeeded": succeeded, "failed": failed}
    _write_output(output_path, document)
    return BatchRunSummary(
        output_path=output_path,
        succeeded=succeeded,
        failed=failed,
    )


def choose_workflow(
    workflows: Mapping[str, WorkflowDefinition] = WORKFLOWS,
) -> WorkflowDefinition:
    definitions = list(workflows.values())
    print("Available workflows:")
    for index, definition in enumerate(definitions, start=1):
        print(f"  {index}. {definition.name} - {definition.description}")

    while True:
        try:
            choice = input("Choose a workflow by number or name: ").strip()
        except EOFError as exc:
            raise ValueError(
                "No workflow selected. Pass --workflow in non-interactive use."
            ) from exc
        if choice in workflows:
            return workflows[choice]
        if choice.isdigit() and 1 <= int(choice) <= len(definitions):
            return definitions[int(choice) - 1]
        print("Invalid selection; try again.")


def build_parser(*, prog: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        description="Run one Tử Vi agent workflow for every profile in a YAML file."
    )
    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        help="YAML file containing a top-level list of profiles.",
    )
    parser.add_argument(
        "--workflow",
        choices=tuple(WORKFLOWS),
        help="Workflow to run. Omit to choose interactively.",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("TUVILM_WORKFLOW_MODEL", DEFAULT_MODEL),
        help=(
            "Pydantic AI model name. Default: TUVILM_WORKFLOW_MODEL or "
            f"{DEFAULT_MODEL}."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output YAML path. Defaults to cli__<workflow>_<date>__<time>.yaml.",
    )
    parser.add_argument(
        "--book-root",
        type=Path,
        default=DEFAULT_BOOK_ROOT,
        help=f"Book chunk directory. Default: {DEFAULT_BOOK_ROOT}",
    )
    parser.add_argument(
        "--list-workflows",
        action="store_true",
        help="List available workflows and exit.",
    )
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    prog: str | None = None,
) -> int:
    parser = build_parser(prog=prog)
    args = parser.parse_args(argv)

    if args.list_workflows:
        for definition in WORKFLOWS.values():
            print(f"{definition.name}: {definition.description}")
        return 0
    if args.input is None:
        parser.error("an input YAML file is required")

    try:
        profiles = load_profiles(args.input)
        definition = WORKFLOWS[args.workflow] if args.workflow else choose_workflow()
    except (OSError, ValueError, ValidationError, yaml.YAMLError) as exc:
        parser.exit(2, f"error: {exc}\n")

    output_path = args.output or default_output_path(definition.name)
    try:
        summary = asyncio.run(
            run_workflow_batch(
                definition=definition,
                profiles=profiles,
                model=args.model,
                output_path=output_path,
                book_root=args.book_root,
            )
        )
    except KeyboardInterrupt:
        print(f"Interrupted. Completed results remain in {output_path}.")
        return 130
    except Exception as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        if output_path.exists():
            print(f"Partial results remain in {output_path}.", file=sys.stderr)
        return 1

    print(
        f"Saved {summary.succeeded} successful and {summary.failed} failed "
        f"result(s) to {summary.output_path}."
    )
    return 1 if summary.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
