"""Stream complete, validated findings from the model's accumulating JSON text."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Iterator
from typing import Any

from pydantic import ValidationError
from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelRetry, UnexpectedModelBehavior
from pydantic_ai.messages import TextPart

from src.agent.deps import TuviAgentDeps

from .input import build_strength_weakness_evidence, prepare_capability_input
from .output.capability_profile import (
    CapabilityProfile,
    StrengthFinding,
    WeaknessFinding,
)


def complete_values(text: str) -> Iterator[tuple[str, int, Any]]:
    """Walk root fields in order; never emit a half-written string or object.

    Raw JSON decoding handles escaped quotes/braces and nested values. Partial
    validation alone would accept a finding with a truncated explanation.
    """
    decoder = json.JSONDecoder()
    start = text.find("{")
    if start < 0:
        return
    pos = start + 1

    def skip(index: int) -> int:
        while index < len(text) and text[index].isspace():
            index += 1
        return index

    try:
        while True:
            pos = skip(pos)
            if pos >= len(text) or text[pos] == "}":
                return
            key, pos = decoder.raw_decode(text, pos)
            pos = skip(pos)
            if not isinstance(key, str) or pos >= len(text) or text[pos] != ":":
                return
            pos = skip(pos + 1)
            if key in ("diem_manh", "diem_yeu"):
                if pos >= len(text) or text[pos] != "[":
                    return
                pos = skip(pos + 1)
                index = 0
                while pos < len(text) and text[pos] != "]":
                    value, pos = decoder.raw_decode(text, pos)
                    yield key, index, value
                    index += 1
                    pos = skip(pos)
                    if pos >= len(text):
                        return
                    if text[pos] == ",":
                        pos = skip(pos + 1)
                    elif text[pos] != "]":
                        return
                if pos >= len(text):
                    return
                pos += 1
            else:
                value, pos = decoder.raw_decode(text, pos)
                if key == "tong_quan" and isinstance(value, str) and value.strip():
                    yield key, 0, value
            pos = skip(pos)
            if pos >= len(text) or text[pos] != ",":
                return
            pos += 1
    except json.JSONDecodeError:
        return


def _prompt(deps: TuviAgentDeps, request: str) -> str:
    evidence = build_strength_weakness_evidence(deps.require_la_so())
    prepared = prepare_capability_input(evidence, deps.require_book())
    return f"{request}\n\n## Dữ liệu đầu vào (CapabilityInput)\n{prepared.model_dump_json()}"


async def stream_strength_weakness(
    *, agent: Agent, deps: TuviAgentDeps, request: str,
) -> AsyncIterator[dict[str, Any]]:
    """Draft events are replaced by reset on retry and reconciled by done.

    Streaming output validation cannot rely on Agent.run's retry loop. Make
    at most three attempts, matching the agent's two output retries. Transport
    failures propagate to the API; only invalid output triggers a new attempt.
    """
    yield {"type": "started", "attempt": 0}
    prompt = await asyncio.to_thread(_prompt, deps, request)
    for attempt in range(3):
        if attempt:
            yield {"type": "reset", "attempt": attempt}
        seen: set[tuple[str, int]] = set()
        strength_ids: set[str] = set()
        try:
            async with agent.run_stream(prompt, deps=deps) as result:
                async for response, _last in result.stream_responses(debounce_by=0.1):
                    text = "".join(part.content for part in response.parts if isinstance(part, TextPart))
                    for key, index, value in complete_values(text):
                        if (key, index) in seen:
                            continue
                        if key == "tong_quan":
                            yield {"type": "overview", "attempt": attempt, "text": value}
                        else:
                            if index >= 6:
                                break
                            schema = StrengthFinding if key == "diem_manh" else WeaknessFinding
                            try:
                                finding = schema.model_validate(value)
                            except ValidationError:
                                break
                            if isinstance(finding, StrengthFinding):
                                if finding.nang_luc_id in strength_ids:
                                    break
                                strength_ids.add(finding.nang_luc_id)
                            yield {
                                "type": "finding", "attempt": attempt,
                                "kind": "strength" if key == "diem_manh" else "weakness",
                                "id": f"{key}:{index}", "index": index,
                                "finding": finding.model_dump(mode="json"),
                            }
                        seen.add((key, index))
                profile = CapabilityProfile.model_validate(await result.get_output())
            yield {"type": "done", "attempt": attempt, "profile": profile.model_dump(mode="json")}
            return
        except (ValidationError, ModelRetry, UnexpectedModelBehavior):
            if attempt == 2:
                raise
            prompt += "\n\nKết quả trước không hợp lệ. Trả lại toàn bộ CapabilityProfile JSON đúng schema, không trùng năng lực."
