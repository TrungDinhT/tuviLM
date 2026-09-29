from __future__ import annotations

import asyncio
import datetime as dt
from pathlib import Path
from typing import Any

import yaml
import pytest
from pydantic import BaseModel, ValidationError

from src.agent.deps import TuviAgentDeps
from src.cli.workflow import (
    ProfileGender,
    WorkflowDefinition,
    build_parser,
    default_output_path,
    load_profiles,
    run_workflow_batch,
)


class FakeStructuredOutput(BaseModel):
    summary: str
    score: int


def test_workflow_cli_only_accepts_profile_input_not_a_request():
    assert "--request" not in build_parser().format_help()


def test_load_profiles_accepts_integer_birth_hours(
    tmp_path: Path,
):
    input_path = tmp_path / "profiles.yaml"
    input_path.write_text(
        """
- name: Khanh
  birth_date: 04-04-1998
  birth_time: 8
  gender: male
- name: Dung
  birth_date: 17-9-1995
  birth_time: 14
  gender: M
- name: Trung
  birth_date: 19-12-1996
  birth_time: 6
  gender: nam
""".strip(),
        encoding="utf-8",
    )

    profiles = load_profiles(input_path)

    assert [profile.name for profile in profiles] == ["Khanh", "Dung", "Trung"]
    assert [profile.birth_date for profile in profiles] == [
        dt.date(1998, 4, 4),
        dt.date(1995, 9, 17),
        dt.date(1996, 12, 19),
    ]
    assert [profile.birth_time for profile in profiles] == [8, 14, 6]
    assert all(profile.gender is ProfileGender.MALE for profile in profiles)


def test_load_profiles_rejects_non_integer_birth_time(tmp_path: Path):
    input_path = tmp_path / "profiles.yaml"
    input_path.write_text(
        """
- name: Khanh
  birth_date: 04-04-1998
  birth_time: "8"
  gender: male
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="birth_time"):
        load_profiles(input_path)


def test_default_output_path_uses_workflow_date_and_time():
    timestamp = dt.datetime(2026, 8, 25, 14, 5, 9)

    path = default_output_path(
        "personality",
        timestamp=timestamp,
        output_dir=Path("results"),
    )

    assert path == Path("results/cli__personality_2026-08-25__14-05-09.yaml")


def test_batch_preserves_structured_workflow_output_and_checkpoints_failures(
    tmp_path: Path,
):
    input_path = tmp_path / "profiles.yaml"
    input_path.write_text(
        """
- name: Khanh
  birth_date: 04-04-1998
  birth_time: 8
  gender: male
- name: Dung
  birth_date: 17-09-1995
  birth_time: 14
  gender: male
""".strip(),
        encoding="utf-8",
    )
    profiles = load_profiles(input_path)
    calls: list[str] = []

    def build_agent(model: str) -> object:
        assert model == "test:model"
        return object()

    async def run(
        agent: Any,
        deps: TuviAgentDeps,
    ) -> FakeStructuredOutput:
        del agent
        assert deps.la_so is not None
        name = profiles[len(calls)].name
        calls.append(name)
        if name == "Dung":
            raise RuntimeError("model unavailable")
        return FakeStructuredOutput(summary=f"Result for {name}", score=7)

    definition = WorkflowDefinition(
        name="fake_workflow",
        description="Fake",
        build_agent=build_agent,
        run=run,
    )
    output_path = tmp_path / "result.yaml"

    summary = asyncio.run(
        run_workflow_batch(
            definition=definition,
            profiles=profiles,
            model="test:model",
            output_path=output_path,
            status=None,
        )
    )

    saved = yaml.safe_load(output_path.read_text(encoding="utf-8"))
    assert summary.succeeded == 1
    assert summary.failed == 1
    assert saved["results"][0]["output"] == {
        "summary": "Result for Khanh",
        "score": 7,
    }
    assert saved["results"][0]["profile"]["birth_time"] == 8
    assert saved["results"][1]["error"] == {
        "type": "RuntimeError",
        "message": "model unavailable",
    }
    assert saved["summary"] == {"succeeded": 1, "failed": 1}
    assert "request" not in saved
    assert "started_at" not in saved
    assert "input_file" not in saved
