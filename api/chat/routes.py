from __future__ import annotations

import json
import logging
import secrets
from datetime import datetime
from typing import Any, AsyncIterator, Awaitable, Callable

import anyio
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
from starlette.types import Receive, Scope, Send

from api.accounts.billing import CHAT_MESSAGE_COST, reserve_chat_coins, settle_chat_coins
from api.auth.dependencies import CurrentUser, ReconciledUser
from api.chat.contracts import ConversationHistoryStore, NotFoundError
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
    UpdateChartProfileRequest,
)
from src.agent.deps import TuviAgentDeps
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
    user: CurrentUser,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1),
) -> CreateChartProfileResponse:
    profile = await _get_store(request).create_chart_profile(
        user.user_id,
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
    user: CurrentUser,
) -> ListChartProfilesResponse:
    profiles = await _get_store(request).list_chart_profiles(user.user_id)
    return ListChartProfilesResponse(
        chart_profiles=[_chart_profile_payload(profile) for profile in profiles]
    )


@router.patch(
    "/chart-profiles/{chart_profile_id}", response_model=CreateChartProfileResponse
)
async def rename_chart_profile(
    chart_profile_id: str,
    payload: UpdateChartProfileRequest,
    request: Request,
    user: CurrentUser,
) -> CreateChartProfileResponse:
    profile = await _get_store(request).rename_chart_profile(
        user.user_id, chart_profile_id, payload.display_name
    )
    return CreateChartProfileResponse(chart_profile=_chart_profile_payload(profile))


@router.delete("/chart-profiles/{chart_profile_id}", status_code=204)
async def delete_chart_profile(
    chart_profile_id: str,
    request: Request,
    user: CurrentUser,
) -> Response:
    await _get_store(request).delete_chart_profile(user.user_id, chart_profile_id)
    return Response(status_code=204)


@router.post(
    "/chart-profiles/{chart_profile_id}/sessions",
    response_model=CreateSessionResponse,
)
async def create_session(
    chart_profile_id: str,
    payload: CreateSessionRequest,
    request: Request,
    user: CurrentUser,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1),
) -> CreateSessionResponse:
    session = await _get_store(request).create_session(
        user.user_id,
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
    user: CurrentUser,
) -> ListSessionsResponse:
    sessions = await _get_store(request).list_sessions(user.user_id, chart_profile_id)
    return ListSessionsResponse(sessions=sessions)


@router.get("/sessions/{session_id}", response_model=GetSessionResponse)
async def get_session(
    session_id: str,
    request: Request,
    user: CurrentUser,
) -> GetSessionResponse:
    context = await _get_store(request).load_session_context(user.user_id, session_id)
    return GetSessionResponse(session=context.session)


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(
    session_id: str,
    request: Request,
    user: CurrentUser,
) -> Response:
    await _get_store(request).delete_session(user.user_id, session_id)
    return Response(status_code=204)


@router.post("/sessions/{session_id}/chat/stream")
async def session_chat_stream(
    session_id: str,
    payload: SessionChatStreamRequest,
    request: Request,
    user: ReconciledUser,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1),
) -> StreamingResponse:
    store = _get_store(request)
    context, history_messages, pair = await _reserve_session_chat_stream(
        store=store,
        owner_id=user.user_id,
        session_id=session_id,
        content=payload.content,
        idempotency_key=idempotency_key,
        allow_new=user.plan == "full_unlock" or user.balance >= CHAT_MESSAGE_COST,
    )

    if pair.replayed:
        if pair.operation_status == MessageOperationStatus.IN_PROGRESS:
            return _streaming_response(_duplicate_in_progress_stream(pair))
        return _streaming_response(_terminal_replay_stream(pair))

    assistant_content: list[str] = []
    finished = False
    terminal_status: ChatMessageStatus | None = None

    async def finalize(status: ChatMessageStatus) -> ChatMessage:
        nonlocal finished, terminal_status
        try:
            message = await store.finalize_assistant_message(
                user.user_id,
                session_id,
                pair.assistant_message.id,
                content="".join(assistant_content),
                status=status,
            )
        except NotFoundError:
            # Deleting the session does not refund the chat charge.
            terminal_status = ChatMessageStatus.CONFIRMED
            raise
        terminal_status = message.status
        await settle_chat_coins(
            request.app.state.auth_database,
            user.user_id,
            pair.assistant_message.id,
            confirmed=terminal_status == ChatMessageStatus.CONFIRMED,
        )
        finished = True
        return message

    async def cleanup(status: ChatMessageStatus = ChatMessageStatus.CANCELLED) -> None:
        if finished:
            return
        try:
            await finalize(status)
        except Exception:
            logger.exception(
                "Failed to finalize session chat: owner_id=%s session_id=%s",
                user.user_id,
                session_id,
            )
            try:
                await settle_chat_coins(
                    request.app.state.auth_database,
                    user.user_id,
                    pair.assistant_message.id,
                    confirmed=terminal_status == ChatMessageStatus.CONFIRMED,
                )
            except Exception:
                logger.exception(
                    "Failed to settle chat coins; pending hold will be reconciled."
                )

    try:
        await reserve_chat_coins(
            request.app.state.auth_database,
            user.user_id,
            session_id,
            pair.assistant_message.id,
        )
    except BaseException:
        with anyio.move_on_after(5, shield=True):
            try:
                await store.discard_message_pair(user.user_id, session_id, pair)
            except Exception:
                logger.exception("Failed to discard a rejected chat message pair.")
            try:
                await settle_chat_coins(
                    request.app.state.auth_database,
                    user.user_id,
                    pair.assistant_message.id,
                    confirmed=False,
                )
            except Exception:
                logger.exception("Failed to refund rejected chat; hold will be reconciled.")
        raise

    return _ChatStreamingResponse(
        _new_session_chat_stream(
            request=request,
            owner_id=user.user_id,
            session_id=session_id,
            context=context,
            history_messages=history_messages,
            pair=pair,
            content=payload.content,
            assistant_content=assistant_content,
            finalize=finalize,
        ),
        cleanup,
    )


async def _reserve_session_chat_stream(
    *,
    store: ConversationHistoryStore,
    owner_id: str,
    session_id: str,
    content: str,
    idempotency_key: str,
    allow_new: bool,
) -> tuple[SessionContext, list[ChatMessage], ReservedMessagePair]:
    context = await store.load_session_context(owner_id, session_id)
    history_messages = list(context.session.messages)
    pair = await store.reserve_message_pair(
        owner_id,
        session_id,
        user_content=content,
        idempotency_key=idempotency_key,
        allow_new=allow_new,
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
    owner_id: str,
    session_id: str,
    context: SessionContext,
    history_messages: list[ChatMessage],
    pair: ReservedMessagePair,
    content: str,
    assistant_content: list[str],
    finalize: Callable[[ChatMessageStatus], Awaitable[ChatMessage]],
) -> AsyncIterator[str]:
    try:
        yield _sse(
            {
                "type": "ids",
                "user_message_id": pair.user_message.id,
                "assistant_message_id": pair.assistant_message.id,
            }
        )
        async for event in _stream_session_chat_events(
            request=request,
            context=context,
            content=content,
            history_messages=history_messages,
        ):
            if event.get("type") == "text":
                assistant_content.append(str(event.get("delta", "")))
            yield _sse(event)

        message = await finalize(ChatMessageStatus.CONFIRMED)
        yield _sse({"type": "done", "status": message.status})
    except Exception as exc:
        logger.exception(
            "Session chat stream failed: owner_id=%s session_id=%s assistant_message_id=%s",
            owner_id,
            session_id,
            pair.assistant_message.id,
        )
        message = await finalize(ChatMessageStatus.FAILED)
        yield _sse({"type": "error", "message": str(exc)})
        yield _sse({"type": "done", "status": message.status})


class _ChatStreamingResponse(StreamingResponse):
    def __init__(
        self,
        stream: AsyncIterator[str],
        cleanup: Callable[[], Awaitable[None]],
    ) -> None:
        super().__init__(
            stream,
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
        self._stream = stream
        self._cleanup = cleanup

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            await super().__call__(scope, receive, send)
        finally:
            # Disconnects can interrupt sending while the generator is suspended.
            with anyio.CancelScope(shield=True):
                try:
                    with anyio.move_on_after(5):
                        await self._cleanup()
                finally:
                    await self._stream.aclose()


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
