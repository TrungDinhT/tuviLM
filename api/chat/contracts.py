from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any, Literal, Protocol


ToolEventKind = Literal["tool_call", "tool_result"]


ROOT_GREETING = (
    "Chào con. Thầy vừa xem qua lá số của con — một lá số không tầm thường. "
    "Con muốn thầy nói sâu về điều gì trước?"
)


@dataclass(frozen=True, slots=True)
class BirthInfo:
    calendar: str
    date: int
    month: int
    year: int
    hour: int
    minute: int
    gender: str


@dataclass(frozen=True, slots=True)
class Message:
    id: str
    parent_id: str | None
    sender: str  # "user" | "assistant"
    body: str
    status: str  # "confirmed" | "streaming" | "failed" | "cancelled" | "deleted"
    streaming: bool = False
    created_at: dt.datetime | None = None


@dataclass(frozen=True, slots=True)
class SessionInfo:
    session_id: str
    chart_profile_id: str
    active_leaf_id: str | None
    display_name: str
    birth_year: int | None
    last_message_preview: str
    message_count: int
    updated_at: dt.datetime | None = None


@dataclass(frozen=True, slots=True)
class ChartSessionCreated:
    chart_profile_id: str
    session_id: str
    active_leaf_id: str


@dataclass(frozen=True, slots=True)
class SessionRecord:
    session_id: str
    chart_profile_id: str
    active_leaf_id: str
    birth_info: BirthInfo
    display_name: str
    messages: list[Message]
    has_more_before: bool = False


@dataclass(frozen=True, slots=True)
class ChatTurnStart:
    user_message_id: str
    assistant_message_id: str
    birth_info: BirthInfo
    history: list[Message]


class ChatStore(Protocol):
    async def ping(self) -> None: ...

    async def ensure_indexes(self) -> None: ...

    async def mark_stale_streaming_messages_failed(self) -> int: ...

    async def create_chart_session(
        self,
        *,
        client_id: str,
        display_name: str,
        birth_info: BirthInfo,
        root_greeting: str = ROOT_GREETING,
    ) -> ChartSessionCreated: ...

    async def get_session(
        self,
        *,
        client_id: str,
        session_id: str,
    ) -> SessionRecord: ...

    async def list_sessions(self, *, client_id: str) -> list[SessionInfo]: ...

    async def soft_delete_session(self, *, client_id: str, session_id: str) -> None: ...

    async def start_chat_turn(
        self,
        *,
        client_id: str,
        session_id: str,
        parent_id: str,
        content: str,
    ) -> ChatTurnStart: ...

    async def confirm_assistant_message(
        self,
        *,
        session_id: str,
        assistant_message_id: str,
        content: str,
    ) -> None: ...

    async def mark_assistant_message_failed(
        self,
        *,
        assistant_message_id: str,
        content: str,
        error: str,
    ) -> None: ...

    async def mark_assistant_message_cancelled(
        self,
        *,
        assistant_message_id: str,
        content: str,
    ) -> None: ...

    async def add_tool_event(
        self,
        *,
        session_id: str,
        message_id: str,
        event_type: ToolEventKind,
        tool_call_id: str | None,
        name: str | None,
        payload: Any,
    ) -> None: ...
