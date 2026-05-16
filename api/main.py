from __future__ import annotations

import datetime as dt
import json
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic_ai import (
    AgentRunResultEvent,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    PartDeltaEvent,
    PartStartEvent,
    TextPart,
    TextPartDelta,
)

from api._parse import to_cung_payload_map
from api.schemas import (
    BuildLasoRequest,
    BuildLasoResponse,
    BuildSaoLuuRequest,
    BuildSaoLuuResponse,
    ChatRequest,
    ChatResponse,
    ChatToolCall,
)
from src.agent.deps import TuviAgentDeps
from src.agent.main import build_tuvi_agent
from src.refactored.la_so import LaSo
from src.refactored.model.prior import Gender, LaSoPrior
from src.refactored.view.builder import build_laso_view


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
    force=True,
)


@dataclass(slots=True)
class ApiState:
    agent_deps: TuviAgentDeps

    @property
    def has_la_so(self) -> bool:
        return self.agent_deps.la_so is not None

    def set_la_so(self, la_so: LaSo) -> None:
        self.agent_deps.la_so = la_so

    def require_la_so(self) -> LaSo:
        return self.agent_deps.require_la_so()


@asynccontextmanager
async def lifespan(app: FastAPI):
    agent_deps = TuviAgentDeps(book_root="./data/tuvitanbien_chunking_compact/part_2")
    agent_deps.agent = build_tuvi_agent(model="openai:gpt-5.4-mini")
    app.state.api_state = ApiState(
        agent_deps=agent_deps,
    )
    yield


app = FastAPI(title="TuviLM API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_api_state(request: Request) -> ApiState:
    return request.app.state.api_state


def _json_safe(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    try:
        return jsonable_encoder(value)
    except Exception:
        return repr(value)


def _get_field(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(name, default)
    return getattr(value, name, default)


def _get_tool_args(part: Any) -> Any:
    args_as_dict = getattr(part, "args_as_dict", None)
    if callable(args_as_dict):
        try:
            return args_as_dict()
        except Exception:
            pass

    args_as_json_str = getattr(part, "args_as_json_str", None)
    if callable(args_as_json_str):
        try:
            return args_as_json_str()
        except Exception:
            pass

    return _get_field(part, "args")


def _extract_tool_calls(result: Any) -> list[ChatToolCall]:
    get_messages = getattr(result, "new_messages", None)
    if not callable(get_messages):
        get_messages = getattr(result, "all_messages", None)

    messages = get_messages() if callable(get_messages) else []
    tool_calls: list[ChatToolCall] = []

    for message in messages:
        for part in _get_field(message, "parts", []):
            part_kind = _get_field(part, "part_kind") or _get_field(part, "kind")
            tool_name = _get_field(part, "tool_name")
            args = _get_tool_args(part)

            if not tool_name:
                continue
            if part_kind and part_kind not in {"tool-call", "tool_call"}:
                continue
            if args is None:
                continue

            tool_calls.append(
                ChatToolCall(
                    id=_get_field(part, "tool_call_id"),
                    name=tool_name,
                    arguments=_json_safe(args),
                )
            )

    return tool_calls


@app.get("/api/v1/health")
def health(request: Request) -> dict[str, str | bool]:
    api_state = get_api_state(request)
    return {
        "status": "ok",
        "la_so_created": api_state.has_la_so,
    }


@app.post("/api/v1/laso/build", response_model=BuildLasoResponse)
def build_laso(payload: BuildLasoRequest, request: Request) -> BuildLasoResponse:
    try:
        solar_dt = dt.datetime(
            year=payload.year,
            month=payload.month,
            day=payload.date,
            hour=payload.hour,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    prior = LaSoPrior.from_solar_day(
        solar_dt, Gender.MALE if payload.gender == "M" else Gender.FEMALE
    )

    # TODO : This is inefficient as we are building the LaSo and LaSoView again in the agent deps.
    # We should refactor to build it only once and reuse.
    la_so = LaSo.from_prior(prior)
    la_so_view = build_laso_view(la_so, study_year=datetime.now().year)
    get_api_state(request).set_la_so(la_so)

    cung_by_position = to_cung_payload_map(la_so_view)

    # TODO : How to use view to extract general summary about the LaSo?
    summary = f"Sinh dương lịch: {payload.date:02d}/{payload.month:02d}/{payload.year} {payload.hour:02d}:00"

    response_id = f"{payload.year:04d}{payload.month:02d}{payload.date:02d}{payload.hour:02d}{payload.gender}"

    return BuildLasoResponse(
        id=response_id,
        summary=summary,
        cung_by_position=cung_by_position,
    )


@app.post("/api/v1/laso/build_sao_luu", response_model=BuildSaoLuuResponse)
def build_sao_luu(payload: BuildSaoLuuRequest, request: Request) -> BuildSaoLuuResponse:
    try:
        observed_solar_dt = dt.datetime(
            year=payload.observation_time.year,
            month=payload.observation_time.month,
            day=payload.observation_time.date,
            hour=payload.observation_time.hour,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    la_so = get_api_state(request).require_la_so()
    la_so_view = build_laso_view(la_so, study_year=observed_solar_dt.year)

    return BuildSaoLuuResponse(
        cung_by_position=to_cung_payload_map(la_so_view),
    )


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_dummy(payload: ChatRequest, request: Request) -> ChatResponse:
    api_state = get_api_state(request)
    if not api_state.has_la_so:
        return ChatResponse(
            answer="TinhBan chưa được tạo trong state.",
        )

    agent = api_state.agent_deps.require_agent()
    result = await agent.run(payload.message, deps=api_state.agent_deps)
    return ChatResponse(
        answer=result.output,
        tool_calls=_extract_tool_calls(result),
    )


def _sse(event: dict[str, Any]) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False, default=str)}\n\n"


@app.post("/api/v1/chat/stream")
async def chat_stream(payload: ChatRequest, request: Request) -> StreamingResponse:
    api_state = get_api_state(request)

    async def gen():
        if not api_state.has_la_so:
            yield _sse({"type": "error", "message": "Chưa lập lá số."})
            yield _sse({"type": "done"})
            return

        agent = api_state.agent_deps.require_agent()
        try:
            async with agent.run_stream_events(
                payload.message, deps=api_state.agent_deps
            ) as stream:
                async for event in stream:
                    msg = _serialize_event(event)
                    if msg is not None:
                        yield _sse(msg)
        except Exception as exc:
            yield _sse({"type": "error", "message": str(exc)})
        yield _sse({"type": "done"})

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _serialize_event(event: Any) -> dict[str, Any] | None:
    match event:
        case PartStartEvent(part=TextPart(content=content)):
            return {"type": "text", "delta": content}
        case PartDeltaEvent(delta=TextPartDelta(content_delta=delta)):
            return {"type": "text", "delta": delta}
        case FunctionToolCallEvent(part=part):
            return {
                "type": "tool_call",
                "id": part.tool_call_id,
                "name": part.tool_name,
                "arguments": _json_safe(_get_tool_args(part)),
            }
        case FunctionToolResultEvent(part=part):
            return {
                "type": "tool_result",
                "id": event.tool_call_id,
                "name": getattr(part, "tool_name", None),
                "content": _json_safe(getattr(part, "content", None)),
            }
        case AgentRunResultEvent(result=result):
            return {"type": "result", "output": getattr(result, "output", None)}
        case _:
            return None
