from __future__ import annotations

from api.chat.models import (
    ChartProfile,
    ChatMessage,
    ChatSession,
    ChatSessionSummary,
)
from api.chat.storage.documents import (
    ChartProfileDocument,
    ChatSessionDocument,
)


def chart_profile_from_document(document: ChartProfileDocument) -> ChartProfile:
    return ChartProfile(
        id=str(document.id),
        owner_id=document.owner_id,
        display_name=document.display_name,
        birth_info=document.birth_info.model_copy(),
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


def chat_session_from_document(document: ChatSessionDocument) -> ChatSession:
    return ChatSession(
        id=str(document.id),
        chart_profile_id=document.chart_profile_id,
        title=document.title,
        messages=[chat_message_from_document(message) for message in document.messages],
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


def chat_message_from_document(document: ChatMessage) -> ChatMessage:
    return document.model_copy()


def chat_session_summary_from_document(
    document: ChatSessionDocument,
) -> ChatSessionSummary:
    return ChatSessionSummary(
        id=str(document.id),
        chart_profile_id=document.chart_profile_id,
        title=document.title,
        message_count=len(document.messages),
        created_at=document.created_at,
        updated_at=document.updated_at,
    )
