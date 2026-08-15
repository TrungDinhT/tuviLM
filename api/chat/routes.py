from __future__ import annotations

import asyncio
import json
import logging
import secrets
from datetime import datetime
from typing import Any, AsyncIterator

from fastapi import APIRouter, Header, Request, Response
from fastapi.encoders import jsonable_encoder
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
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, UserPromptPart

from api.chat.contracts import ConversationHistoryStore
from api.chat.models import (
    BirthInfo,
    ChartProfile,
    ChatMessage,
    ChatMessageStatus,
    ChatRole,
    CreateChartProfileInput,
    CreateSessionInput,
    MessageOperationStatus,
    ReservedMessagePair,
    SessionContext,
)
from api.schemas import (
    ChartProfilePayload,
    CreateAnonymousResponse,
    CreateChartProfileRequest,
    CreateChartProfileResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    GetSessionResponse,
    ListChartProfilesResponse,
    ListSessionsResponse,
    SessionChatStreamRequest,
    StrengthWeaknessRequest,
)
from src.agent.deps import TuviAgentDeps
from src.agent.workflow.strength_weakness import (
    StrengthWeaknessAssessment,
    run_strength_weakness_agent,
)
from src.refactored.la_so import LaSo
from src.refactored.model.prior import Gender, LaSoPrior


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")


@router.post("/anonymous", response_model=CreateAnonymousResponse)
def create_anonymous() -> CreateAnonymousResponse:
    return CreateAnonymousResponse(owner_id=f"anon_{secrets.token_urlsafe(24)}")


@router.post("/chart-profiles", response_model=CreateChartProfileResponse)
async def create_chart_profile(
    payload: CreateChartProfileRequest,
    request: Request,
    owner_id: str = Header(alias="X-Anonymous-Owner-Id"),
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1),
) -> CreateChartProfileResponse:
    profile = await _get_store(request).create_chart_profile(
        owner_id,
        CreateChartProfileInput(
            display_name=payload.display_name,
            birth_info=payload.birth_info,
        ),
        idempotency_key=idempotency_key,
    )
    return CreateChartProfileResponse(chart_profile=_chart_profile_payload(profile))


@router.get("/chart-profiles", response_model=ListChartProfilesResponse)
async def list_chart_profiles(
    request: Request,
    owner_id: str = Header(alias="X-Anonymous-Owner-Id"),
) -> ListChartProfilesResponse:
    profiles = await _get_store(request).list_chart_profiles(owner_id)
    return ListChartProfilesResponse(
        chart_profiles=[_chart_profile_payload(profile) for profile in profiles]
    )


@router.delete("/chart-profiles/{chart_profile_id}", status_code=204)
async def delete_chart_profile(
    chart_profile_id: str,
    request: Request,
    owner_id: str = Header(alias="X-Anonymous-Owner-Id"),
) -> Response:
    await _get_store(request).delete_chart_profile(owner_id, chart_profile_id)
    return Response(status_code=204)


@router.post(
    "/chart-profiles/{chart_profile_id}/sessions",
    response_model=CreateSessionResponse,
)
async def create_session(
    chart_profile_id: str,
    payload: CreateSessionRequest,
    request: Request,
    owner_id: str = Header(alias="X-Anonymous-Owner-Id"),
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1),
) -> CreateSessionResponse:
    session = await _get_store(request).create_session(
        owner_id,
        chart_profile_id,
        CreateSessionInput(title=payload.title),
        idempotency_key=idempotency_key,
    )
    return CreateSessionResponse(session=session)


@router.get(
    "/chart-profiles/{chart_profile_id}/sessions",
    response_model=ListSessionsResponse,
)
async def list_sessions(
    chart_profile_id: str,
    request: Request,
    owner_id: str = Header(alias="X-Anonymous-Owner-Id"),
) -> ListSessionsResponse:
    sessions = await _get_store(request).list_sessions(owner_id, chart_profile_id)
    return ListSessionsResponse(sessions=sessions)


@router.get("/sessions/{session_id}", response_model=GetSessionResponse)
async def get_session(
    session_id: str,
    request: Request,
    owner_id: str = Header(alias="X-Anonymous-Owner-Id"),
) -> GetSessionResponse:
    context = await _get_store(request).load_session_context(owner_id, session_id)
    return GetSessionResponse(session=context.session)


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(
    session_id: str,
    request: Request,
    owner_id: str = Header(alias="X-Anonymous-Owner-Id"),
) -> Response:
    await _get_store(request).delete_session(owner_id, session_id)
    return Response(status_code=204)


@router.post(
    "/sessions/{session_id}/strength-weakness",
    response_model=StrengthWeaknessAssessment,
)
async def session_strength_weakness(
    session_id: str,
    payload: StrengthWeaknessRequest,
    request: Request,
    owner_id: str = Header(alias="X-Anonymous-Owner-Id"),
) -> StrengthWeaknessAssessment:
    """Run the structured strength/weakness workflow for one saved chart."""
    context = await _get_store(request).load_session_context(owner_id, session_id)
    history = _visible_messages_to_model_history(context.session.messages)
    base_deps = request.app.state.api_state.agent_deps
    deps = TuviAgentDeps(
        agent=base_deps.agent,
        personality_agent=base_deps.personality_agent,
        strength_weakness_agent=base_deps.strength_weakness_agent,
        la_so=_build_la_so(context.chart_profile.birth_info),
        book=base_deps.book,
        book_root=base_deps.book_root,
        message_history=history,
    )
    return await run_strength_weakness_agent(
        agent=deps.require_strength_weakness_agent(),
        deps=deps,
        request=payload.content,
        message_history=history,
    )


@router.post("/sessions/{session_id}/chat/stream")
async def session_chat_stream(
    session_id: str,
    payload: SessionChatStreamRequest,
    request: Request,
    owner_id: str = Header(alias="X-Anonymous-Owner-Id"),
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1),
) -> StreamingResponse:
    store = _get_store(request)
    context, history_messages, pair = await _reserve_session_chat_stream(
        store=store,
        owner_id=owner_id,
        session_id=session_id,
        content=payload.content,
        idempotency_key=idempotency_key,
    )

    if pair.replayed:
        if pair.operation_status == MessageOperationStatus.IN_PROGRESS:
            return _streaming_response(_duplicate_in_progress_stream(pair))
        return _streaming_response(_terminal_replay_stream(pair))

    return _streaming_response(
        _new_session_chat_stream(
            request=request,
            store=store,
            owner_id=owner_id,
            session_id=session_id,
            context=context,
            history_messages=history_messages,
            pair=pair,
            content=payload.content,
        )
    )


async def _reserve_session_chat_stream(
    *,
    store: ConversationHistoryStore,
    owner_id: str,
    session_id: str,
    content: str,
    idempotency_key: str,
) -> tuple[SessionContext, list[ChatMessage], ReservedMessagePair]:
    context = await store.load_session_context(owner_id, session_id)
    history_messages = list(context.session.messages)
    pair = await store.reserve_message_pair(
        owner_id,
        session_id,
        user_content=content,
        idempotency_key=idempotency_key,
    )
    return context, history_messages, pair


async def _duplicate_in_progress_stream(
    pair: ReservedMessagePair,
) -> AsyncIterator[str]:
    yield _sse(
        {
            "type": "duplicate_in_progress",
            "user_message_id": pair.user_message.id,
            "assistant_message_id": pair.assistant_message.id,
            "status": pair.assistant_message.status,
        }
    )
    yield _sse({"type": "done", "status": "duplicate_in_progress"})


async def _terminal_replay_stream(pair: ReservedMessagePair) -> AsyncIterator[str]:
    yield _sse(
        {
            "type": "ids",
            "user_message_id": pair.user_message.id,
            "assistant_message_id": pair.assistant_message.id,
        }
    )
    if pair.assistant_message.content:
        yield _sse({"type": "text", "delta": pair.assistant_message.content})
    yield _sse({"type": "done", "status": pair.assistant_message.status})


async def _new_session_chat_stream(
    *,
    request: Request,
    store: ConversationHistoryStore,
    owner_id: str,
    session_id: str,
    context: SessionContext,
    history_messages: list[ChatMessage],
    pair: ReservedMessagePair,
    content: str,
) -> AsyncIterator[str]:
    assistant_content: list[str] = []
    yield _sse(
        {
            "type": "ids",
            "user_message_id": pair.user_message.id,
            "assistant_message_id": pair.assistant_message.id,
        }
    )

    try:
        async for event in _stream_session_chat_events(
            request=request,
            context=context,
            content=content,
            history_messages=history_messages,
        ):
            if event.get("type") == "text":
                assistant_content.append(str(event.get("delta", "")))
            yield _sse(event)

        await store.finalize_assistant_message(
            owner_id,
            session_id,
            pair.assistant_message.id,
            content="".join(assistant_content),
            status=ChatMessageStatus.CONFIRMED,
        )
        yield _sse({"type": "done", "status": ChatMessageStatus.CONFIRMED})
    except asyncio.CancelledError:
        logger.info(
            "Session chat stream cancelled: owner_id=%s session_id=%s assistant_message_id=%s",
            owner_id,
            session_id,
            pair.assistant_message.id,
        )
        try:
            await asyncio.wait_for(
                asyncio.shield(
                    store.finalize_assistant_message(
                        owner_id,
                        session_id,
                        pair.assistant_message.id,
                        content="".join(assistant_content),
                        status=ChatMessageStatus.CANCELLED,
                    )
                ),
                timeout=2,
            )
        except Exception:
            logger.exception(
                "Failed to finalize cancelled session chat stream: "
                "owner_id=%s session_id=%s assistant_message_id=%s",
                owner_id,
                session_id,
                pair.assistant_message.id,
            )
        raise
    except Exception as exc:
        logger.exception(
            "Session chat stream failed: owner_id=%s session_id=%s assistant_message_id=%s",
            owner_id,
            session_id,
            pair.assistant_message.id,
        )
        await store.finalize_assistant_message(
            owner_id,
            session_id,
            pair.assistant_message.id,
            content="".join(assistant_content),
            status=ChatMessageStatus.FAILED,
        )
        yield _sse({"type": "error", "message": str(exc)})
        yield _sse({"type": "done", "status": ChatMessageStatus.FAILED})


def _streaming_response(stream: AsyncIterator[str]) -> StreamingResponse:
    return StreamingResponse(
        stream,
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _get_store(request: Request) -> ConversationHistoryStore:
    return request.app.state.api_state.conversation_history_store


def _sse(event: dict[str, Any]) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False, default=str)}\n\n"


async def _stream_session_chat_events(
    *,
    request: Request,
    context: SessionContext,
    content: str,
    history_messages: list[ChatMessage],
):
    streamer = getattr(request.app.state, "session_chat_streamer", None)
    if streamer is not None:
        async for event in streamer(request=request, context=context, content=content):
            yield event
        return

    api_state = request.app.state.api_state
    base_deps = api_state.agent_deps
    message_history = _visible_messages_to_model_history(history_messages)
    agent_deps = TuviAgentDeps(
        agent=base_deps.agent,
        personality_agent=base_deps.personality_agent,
        strength_weakness_agent=base_deps.strength_weakness_agent,
        la_so=_build_la_so(context.chart_profile.birth_info),
        book=base_deps.book,
        book_root=base_deps.book_root,
        message_history=message_history,
    )
    agent = agent_deps.require_agent()
    async with agent.run_stream_events(
        content,
        deps=agent_deps,
        message_history=message_history,
    ) as stream:
        async for event in stream:
            msg = _serialize_agent_event(event)
            if msg is not None:
                yield msg
def _build_la_so(birth_info: BirthInfo) -> LaSo:
    solar_dt = datetime(
        year=birth_info.year,
        month=birth_info.month,
        day=birth_info.day,
        hour=birth_info.hour,
    )
    prior = LaSoPrior.from_solar_day(
        solar_dt,
        Gender.MALE if birth_info.gender == "M" else Gender.FEMALE,
    )
    return LaSo.from_prior(prior)


def _visible_messages_to_model_history(
    messages: list[ChatMessage],
) -> list[ModelMessage]:
    history: list[ModelMessage] = []
    for message in messages:
        if message.status != ChatMessageStatus.CONFIRMED:
            continue
        if message.role == ChatRole.USER:
            history.append(
                ModelRequest(
                    parts=[UserPromptPart(content=message.content)],
                    timestamp=message.created_at,
                )
            )
        else:
            history.append(
                ModelResponse(
                    parts=[TextPart(content=message.content)],
                    timestamp=message.created_at,
                )
            )
    return history


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


def _serialize_agent_event(event: Any) -> dict[str, Any] | None:
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
                "id": getattr(event, "tool_call_id", None),
                "name": getattr(part, "tool_name", None),
                "content": _json_safe(getattr(part, "content", None)),
            }
        case AgentRunResultEvent(result=result):
            return {"type": "result", "output": getattr(result, "output", None)}
        case _:
            return None


def _chart_profile_payload(profile: ChartProfile) -> ChartProfilePayload:
    return ChartProfilePayload(
        id=profile.id,
        display_name=profile.display_name,
        birth_info=profile.birth_info,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )
