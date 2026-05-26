from __future__ import annotations

from typing import Protocol

from api.chat.models import (
    ChartProfile,
    ChatMessage,
    ChatMessageStatus,
    ChatSession,
    ChatSessionSummary,
    CreateChartProfileInput,
    CreateSessionInput,
    ReservedMessagePair,
    SessionContext,
)


class ConversationHistoryError(Exception):
    """Base exception for conversation history store failures."""


class MissingOwnerIdError(ConversationHistoryError):
    """Raised when an operation requires an anonymous owner id."""


class IdempotencyConflictError(ConversationHistoryError):
    """Raised when an idempotency key is reused with a different payload."""


class DuplicateStreamInProgressError(ConversationHistoryError):
    """Raised when a session already has an active pending stream."""


class NotFoundError(ConversationHistoryError):
    """Raised when a requested conversation history resource does not exist."""


class ConversationHistoryStore(Protocol):
    async def create_chart_profile(
        self,
        owner_id: str | None,
        payload: CreateChartProfileInput,
        *,
        idempotency_key: str,
    ) -> ChartProfile: ...

    async def list_chart_profiles(self, owner_id: str) -> list[ChartProfile]: ...

    async def delete_chart_profile(self, owner_id: str, chart_profile_id: str) -> None: ...

    async def create_session(
        self,
        owner_id: str,
        chart_profile_id: str,
        payload: CreateSessionInput,
        *,
        idempotency_key: str,
    ) -> ChatSession: ...

    async def list_sessions(
        self, owner_id: str, chart_profile_id: str
    ) -> list[ChatSessionSummary]: ...

    async def load_session_context(self, owner_id: str, session_id: str) -> SessionContext: ...

    async def delete_session(self, owner_id: str, session_id: str) -> None: ...

    async def reserve_message_pair(
        self,
        owner_id: str,
        session_id: str,
        *,
        user_content: str,
        idempotency_key: str,
    ) -> ReservedMessagePair: ...

    async def finalize_assistant_message(
        self,
        owner_id: str,
        session_id: str,
        assistant_message_id: str,
        *,
        content: str,
        status: ChatMessageStatus,
    ) -> ChatMessage: ...
