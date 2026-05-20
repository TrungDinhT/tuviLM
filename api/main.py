from __future__ import annotations

import datetime as dt
import asyncio
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
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
from pydantic_ai import messages as pai_messages, Agent
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
    BirthMetadata,
    BuildLasoRequest,
    BuildLasoResponse,
    BuildSaoLuuRequest,
    BuildSaoLuuResponse,
    CalendarKind,
    ChatRequest,
    ChatResponse,
    ChatToolCall,
    GenderCode,
    SessionDetailResponse,
    SessionListResponse,
)
from api.chat.contracts import BirthInfo, ChatStore
from api.chat.mappers import (
    birth_metadata_to_info,
    record_to_detail,
    session_info_to_summary,
)
from api.chat.store.mongo import InvalidChatParentError, MongoChatStore, NotFoundError
from api.settings import ApiSettings
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
    settings: ApiSettings
    store: ChatStore
    agent: Agent

    def agent_deps_for(self, la_so: LaSo) -> TuviAgentDeps:
        return TuviAgentDeps(
            agent=self.agent,
            la_so=la_so,
            book_root=self.settings.book_root,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    from pymongo.asynchronous.mongo_client import AsyncMongoClient

    settings = ApiSettings.from_env()
    mongo_client = AsyncMongoClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=settings.mongodb_timeout_ms,
    )
    try:
        await mongo_client.admin.command("ping")
    except ServerSelectionTimeoutError:
        logging.exception(
            "MongoDB is unavailable. Start local Mongo with `docker compose up -d mongodb` "
            "or set MONGODB_URI to a reachable replica set."
        )
        raise
    store = MongoChatStore(mongo_client[settings.mongodb_db])
    await store.ensure_indexes()
    stale_count = await store.mark_stale_streaming_messages_failed()
    if stale_count:
        logging.info("Marked %s stale streaming messages as failed", stale_count)

    app.state.api_state = ApiState(
        settings=settings,
        store=store,
        agent=build_tuvi_agent(model=settings.model_name),
    )
    try:
        yield
    finally:
        await mongo_client.close()


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
async def health(request: Request) -> dict[str, str | bool]:
    api_state = get_api_state(request)
    try:
        await api_state.store.ping()
    except PyMongoError:
        return {
            "status": "degraded",
            "mongo_connected": False,
            "database": api_state.settings.mongodb_db,
        }
    return {
        "status": "ok",
        "mongo_connected": True,
        "database": api_state.settings.mongodb_db,
    }


def _la_so_from_birth_info(birth_info: BirthInfo) -> LaSo:
    if birth_info.calendar != CalendarKind.SOLAR.value:
        raise HTTPException(
            status_code=422,
            detail="Lịch âm chưa được hỗ trợ trong phiên bản này. Vui lòng chọn Dương.",
        )
    try:
        solar_dt = dt.datetime(
            year=birth_info.year,
            month=birth_info.month,
            day=birth_info.date,
            hour=birth_info.hour,
            minute=birth_info.minute,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    prior = LaSoPrior.from_solar_day(
        solar_dt, Gender.MALE if birth_info.gender == GenderCode.MALE.value else Gender.FEMALE
    )
    return LaSo.from_prior(prior)


def _build_laso_payload(
    *,
    birth_info: BirthInfo,
    chart_profile_id: str,
    session_id: str,
    active_leaf_id: str,
) -> BuildLasoResponse:
    la_so = _la_so_from_birth_info(birth_info)
    la_so_view = build_laso_view(la_so, study_year=datetime.now().year)
    summary = (
        f"Sinh dương lịch: {birth_info.date:02d}/{birth_info.month:02d}/{birth_info.year} "
        f"{birth_info.hour:02d}:{birth_info.minute:02d}"
    )
    return BuildLasoResponse(
        id=chart_profile_id,
        chart_profile_id=chart_profile_id,
        session_id=session_id,
        active_leaf_id=active_leaf_id,
        summary=summary,
        ban_menh_name=la_so_view.ban_menh_name,
        cuc_name=la_so_view.cuc_name,
        menh_cuc_relation_label=la_so_view.menh_cuc_relation_label,
        cung_by_position=to_cung_payload_map(la_so_view),
    )


@app.post("/api/v1/laso/build", response_model=BuildLasoResponse)
async def build_laso(payload: BuildLasoRequest, request: Request) -> BuildLasoResponse:
    birth = BirthMetadata.model_validate(payload.model_dump())
    birth_info = birth_metadata_to_info(birth)
    created = await get_api_state(request).store.create_chart_session(
        client_id=payload.client_id,
        display_name=payload.display_name,
        birth_info=birth_info,
    )
    return _build_laso_payload(
        birth_info=birth_info,
        chart_profile_id=created.chart_profile_id,
        session_id=created.session_id,
        active_leaf_id=created.active_leaf_id,
    )


@app.post("/api/v1/laso/build_sao_luu", response_model=BuildSaoLuuResponse)
def build_sao_luu(payload: BuildSaoLuuRequest, request: Request) -> BuildSaoLuuResponse:
    del payload, request
    raise HTTPException(
        status_code=410,
        detail="/api/v1/laso/build_sao_luu must be migrated to session-backed chart state.",
    )


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_dummy(payload: ChatRequest, request: Request) -> ChatResponse:
    del payload, request
    raise HTTPException(
        status_code=410,
        detail="/api/v1/chat is deprecated. Use /api/v1/chat/stream instead.",
    )


def _sse(event: dict[str, Any]) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False, default=str)}\n\n"


@app.post("/api/v1/chat/stream")
async def chat_stream(payload: ChatRequest, request: Request) -> StreamingResponse:
    api_state = get_api_state(request)
    try:
        turn = await _start_turn_or_404(api_state.store, payload)
    except PyMongoError as exc:
        logging.exception("MongoDB failed while starting chat turn")
        raise
    la_so = _la_so_from_birth_info(turn.birth_info)
    deps = api_state.agent_deps_for(la_so)
    history = _to_model_history(turn.history)

    async def gen():
        yield _sse(
            {
                "type": "ids",
                "user_message_id": turn.user_message_id,
                "assistant_message_id": turn.assistant_message_id,
            }
        )
        assistant_content = ""
        try:
            async with api_state.agent.run_stream_events(
                payload.content,
                deps=deps,
                message_history=history,
                conversation_id=payload.session_id,
            ) as stream:
                async for event in stream:
                    if isinstance(event, AgentRunResultEvent):
                        output = getattr(event.result, "output", None)
                        if isinstance(output, str):
                            assistant_content = output
                        continue
                    msg = _serialize_event(event)
                    if msg is not None:
                        if msg["type"] == "text":
                            assistant_content += msg.get("delta", "")
                        elif msg["type"] in {"tool_call", "tool_result"}:
                            await _record_tool_event(
                                api_state.store,
                                session_id=payload.session_id,
                                assistant_message_id=turn.assistant_message_id,
                                msg=msg,
                            )
                        yield _sse(msg)
            await api_state.store.confirm_assistant_message(
                session_id=payload.session_id,
                assistant_message_id=turn.assistant_message_id,
                content=assistant_content,
            )
            yield _sse({"type": "done", "status": "confirmed"})
        except asyncio.CancelledError:
            try:
                await api_state.store.mark_assistant_message_cancelled(
                    assistant_message_id=turn.assistant_message_id,
                    content=assistant_content,
                )
            except PyMongoError:
                logging.exception("MongoDB failed while marking assistant message cancelled")
            raise
        except Exception as exc:
            try:
                await api_state.store.mark_assistant_message_failed(
                    assistant_message_id=turn.assistant_message_id,
                    content=assistant_content,
                    error=str(exc),
                )
            except PyMongoError:
                logging.exception("MongoDB failed while marking assistant message failed")
            yield _sse(
                {
                    "type": "failed",
                    "assistant_message_id": turn.assistant_message_id,
                    "status": "failed",
                    "message": str(exc),
                }
            )

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
        case _:
            return None


@app.get("/api/v1/sessions", response_model=SessionListResponse)
async def list_sessions(client_id: str, request: Request) -> SessionListResponse:
    sessions = await get_api_state(request).store.list_sessions(client_id=client_id)
    return SessionListResponse(
        sessions=[session_info_to_summary(s) for s in sessions]
    )


@app.get("/api/v1/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str, client_id: str, request: Request
) -> SessionDetailResponse:
    try:
        record = await get_api_state(request).store.get_session(
            client_id=client_id,
            session_id=session_id,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    laso = _build_laso_payload(
        birth_info=record.birth_info,
        chart_profile_id=record.chart_profile_id,
        session_id=record.session_id,
        active_leaf_id=record.active_leaf_id,
    )
    return record_to_detail(record, laso, client_id)


@app.delete("/api/v1/sessions/{session_id}", status_code=204)
async def delete_session(session_id: str, client_id: str, request: Request) -> None:
    try:
        await get_api_state(request).store.soft_delete_session(
            client_id=client_id,
            session_id=session_id,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


async def _start_turn_or_404(store: ChatStore, payload: ChatRequest):
    try:
        return await store.start_chat_turn(
            client_id=payload.client_id,
            session_id=payload.session_id,
            parent_id=payload.parent_id,
            content=payload.content,
        )
    except InvalidChatParentError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _to_model_history(
    messages: list[Any],
) -> list[pai_messages.ModelRequest | pai_messages.ModelResponse]:
    history: list[pai_messages.ModelRequest | pai_messages.ModelResponse] = []
    has_user_message = False
    for message in messages:
        if getattr(message, "status", "confirmed") != "confirmed":
            continue
        if message.sender == "user":
            has_user_message = True
            history.append(
                pai_messages.ModelRequest(
                    parts=[pai_messages.UserPromptPart(content=message.body)]
                )
            )
        else:
            if not has_user_message:
                continue
            history.append(
                pai_messages.ModelResponse(
                    parts=[pai_messages.TextPart(content=message.body)]
                )
            )
    return history


async def _record_tool_event(
    store: ChatStore,
    *,
    session_id: str,
    assistant_message_id: str,
    msg: dict[str, Any],
) -> None:
    try:
        await store.add_tool_event(
            session_id=session_id,
            message_id=assistant_message_id,
            event_type=msg["type"],
            tool_call_id=msg.get("id"),
            name=msg.get("name"),
            payload=msg.get("arguments") if msg["type"] == "tool_call" else msg.get("content"),
        )
    except Exception:
        logging.exception("Failed to record tool event")
