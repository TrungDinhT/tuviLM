from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import AgentRunResult
import pydantic_ai

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
    required_read_sections: set[str] = Field(default_factory=set)
    min_output_chars: int = 80


class AgentResult(BaseModel):
    """Structured output returned by the eval task."""

    output: str
    tools_used: set[str] = Field(default_factory=set)
    usage: dict[str, Any] | None = None
    read_sections: set[str] = Field(default_factory=set)
    messages: list[dict[str, Any]] = Field(default_factory=list)

    @classmethod
    def from_run_result(cls, run_result: AgentRunResult[str]) -> "AgentResult":
        messages = _extract_messages(run_result)
        tools_calls = _extract_tool_call(run_result)
        return cls(
            output=str(getattr(run_result, "output", "")),
            tools_used=set(call["tool_name"] for call in tools_calls),
            usage=_extract_usage(run_result),
            read_sections=_extract_read_sections(tools_calls),
            messages=messages,
        )


def _extract_usage(run_result: AgentRunResult[str]) -> dict[str, Any] | None:
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


def _extract_messages(run_result: AgentRunResult[str]) -> list[dict[str, Any]]:
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


def _args_as_dict(part: pydantic_ai.ToolCallPart) -> dict[str, Any]:
    try:
        return part.args_as_dict()
    except Exception:  # noqa: BLE001
        return {}


def _extract_tool_call(result: AgentRunResult[str]) -> list[dict[str, Any]]:
    tool_calls: list[dict[str, Any]] = []

    for message in result.new_messages():
        if not isinstance(message, pydantic_ai.ModelResponse):
            continue

        for part in message.parts:
            if not isinstance(part, pydantic_ai.ToolCallPart):
                continue

            tool_calls.append({
                "tool_name": part.tool_name,
                "args": _args_as_dict(part),
                "tool_call_id": part.tool_call_id,
            })

    return tool_calls



def _extract_read_sections(tool_calls: list[dict[str, Any]]) -> set[str]:
    sections: set[str] = set()

    for call in tool_calls:
        if call["tool_name"] == "read_section":
            args = call.get("args", {})
            section = args.get("section_id")
            if isinstance(section, str):
                sections.add(section)

    return sections
