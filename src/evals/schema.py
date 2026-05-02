from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field

from src.tuvi.birth import TuviTime


class TuviEvalInput(BaseModel):
    """Input for one Tu Vi agent evaluation case."""

    tuvi_time: TuviTime
    query: str


class TuviEvalExpected(BaseModel):
    """Deterministic expectations for one evaluation case."""

    required_substrings: list[str] = Field(default_factory=list)
    forbidden_substrings: list[str] = Field(default_factory=list)
    required_tools: list[str] = Field(default_factory=list)
    min_output_chars: int = 80


class AgentResult(BaseModel):
    """Structured output returned by the eval task."""

    output: str
    tools_used: list[str] = Field(default_factory=list)
    usage: dict[str, Any] | None = None
    messages: list[dict[str, Any]] = Field(default_factory=list)

    @classmethod
    def from_run_result(cls, run_result: Any) -> "AgentResult":
        messages = _extract_messages(run_result)
        return cls(
            output=str(getattr(run_result, "output", "")),
            tools_used=_extract_tool_names(messages),
            usage=_extract_usage(run_result),
            messages=messages,
        )


def _extract_usage(run_result: Any) -> dict[str, Any] | None:
    usage = getattr(run_result, "usage", None)
    if callable(usage):
        usage = usage()
    if usage is None:
        return None
    if hasattr(usage, "model_dump"):
        return usage.model_dump(mode="json")
    if isinstance(usage, dict):
        return usage
    return {"value": str(usage)}


def _extract_messages(run_result: Any) -> list[dict[str, Any]]:
    for method_name in ("all_messages", "new_messages"):
        method = getattr(run_result, method_name, None)
        if callable(method):
            messages = method()
            return [_to_jsonable(message) for message in messages]

    for method_name in ("all_messages_json", "new_messages_json"):
        method = getattr(run_result, method_name, None)
        if callable(method):
            raw = method()
            if isinstance(raw, bytes):
                raw = raw.decode()
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, list) else [parsed]

    return []


def _to_jsonable(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        dumped = value.model_dump(mode="json")
    elif hasattr(value, "dict"):
        dumped = value.dict()
    elif isinstance(value, dict):
        dumped = value
    else:
        dumped = {"value": str(value)}
    return dumped if isinstance(dumped, dict) else {"value": dumped}


def _extract_tool_names(messages: list[dict[str, Any]]) -> list[str]:
    names: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            maybe_name = value.get("tool_name") or value.get("function_name")
            if isinstance(maybe_name, str):
                names.append(maybe_name)
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(messages)
    return list(dict.fromkeys(names))
