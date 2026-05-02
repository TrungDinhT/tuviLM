from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic_evals import Case, Dataset

from src.evals.evaluators import TuviAgentQuality
from src.evals.schema import AgentResult, TuviEvalExpected, TuviEvalInput



def load_dataset(path: str | Path) -> Dataset[TuviEvalInput, AgentResult, dict]:
    data = _load_yaml(path)
    cases = [
        Case(
            name=case.get("name"),
            inputs=TuviEvalInput.model_validate(case["inputs"]),
            expected_output=TuviEvalExpected.model_validate(
                case.get("expected_output") or {}
            ),
            metadata=case.get("metadata") or {},
        )
        for case in data.get("cases", [])
    ]
    return Dataset(
        name=data.get("name") or "tuvi_agent_eval",
        cases=cases,
        evaluators=[TuviAgentQuality()],
    )


def _load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Dataset file must contain a mapping: {path}")
    if "cases" not in data:
        raise ValueError(f"Dataset file must contain a 'cases' list: {path}")
    return data
