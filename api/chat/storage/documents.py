from __future__ import annotations

from datetime import UTC, datetime

from beanie import DocumentWithSoftDelete
from pydantic import BaseModel, Field
from pymongo import ASCENDING, IndexModel

from api.chat.models import BirthInfo, ChatMessage, MessageOperationStatus


def utc_now() -> datetime:
    now = datetime.now(UTC)
    return now.replace(microsecond=(now.microsecond // 1000) * 1000)


class ChartProfileDocument(DocumentWithSoftDelete):
    owner_id: str
    creation_idempotency_key: str
    creation_request_fingerprint: str

    display_name: str
    birth_info: BirthInfo
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "chart_profiles"
        indexes = [
            IndexModel([("owner_id", ASCENDING)]),
            IndexModel(
                [
                    ("owner_id", ASCENDING),
                    ("creation_idempotency_key", ASCENDING),
                ],
                unique=True,
            ),
        ]


class MessageOperationDocument(BaseModel):
    idempotency_key: str
    request_fingerprint: str

    user_message_id: str
    assistant_message_id: str
    status: MessageOperationStatus
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ChatSessionDocument(DocumentWithSoftDelete):
    chart_profile_id: str
    creation_idempotency_key: str
    creation_request_fingerprint: str

    title: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    messages: list[ChatMessage] = Field(default_factory=list)
    message_operations: list[MessageOperationDocument] = Field(default_factory=list)

    class Settings:
        name = "sessions"
        indexes = [
            IndexModel([("chart_profile_id", ASCENDING)]),
            IndexModel(
                [
                    ("chart_profile_id", ASCENDING),
                    ("creation_idempotency_key", ASCENDING),
                ],
                unique=True,
            ),
        ]
