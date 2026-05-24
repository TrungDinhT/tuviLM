from __future__ import annotations

import datetime as dt
from enum import StrEnum
from typing import Any

from beanie import Document
from bson import ObjectId
from pydantic import ConfigDict, Field
from pymongo import ASCENDING, DESCENDING

from api.chat.contracts import Message


class RecordStatus(StrEnum):
    ACTIVE = "active"
    DELETED = "deleted"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class MessageStatus(StrEnum):
    CONFIRMED = "confirmed"
    STREAMING = "streaming"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DELETED = "deleted"


class ToolEventType(StrEnum):
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"


# Beanie's Document model_config does not set arbitrary_types_allowed=True by default,
# but we need it for bson.ObjectId fields.
_document_config = ConfigDict(**Document.model_config, arbitrary_types_allowed=True)


class ChartProfileDocument(Document):
    model_config = _document_config

    id: ObjectId = Field(alias="_id")
    client_id: str
    display_name: str
    birth_metadata: dict[str, Any]
    status: RecordStatus
    created_at: dt.datetime
    updated_at: dt.datetime

    class Settings:
        name = "chart_profiles"
        indexes = [
            [("client_id", ASCENDING), ("status", ASCENDING), ("updated_at", DESCENDING)],
        ]


class SessionDocument(Document):
    model_config = _document_config

    id: ObjectId = Field(alias="_id")
    client_id: str
    chart_profile_id: ObjectId
    active_leaf_id: ObjectId
    status: RecordStatus
    created_at: dt.datetime
    updated_at: dt.datetime

    class Settings:
        name = "sessions"
        indexes = [
            [("client_id", ASCENDING), ("status", ASCENDING), ("updated_at", DESCENDING)],
            [("chart_profile_id", ASCENDING)],
            [("active_leaf_id", ASCENDING)],
        ]


class MessageDocument(Document):
    model_config = _document_config

    id: ObjectId = Field(alias="_id")
    session_id: ObjectId
    parent_id: ObjectId | None
    role: MessageRole
    content: str
    status: MessageStatus
    created_at: dt.datetime
    updated_at: dt.datetime

    class Settings:
        name = "messages"
        indexes = [
            [("session_id", ASCENDING), ("created_at", ASCENDING)],
            [("parent_id", ASCENDING)],
            [("session_id", ASCENDING), ("status", ASCENDING)],
        ]

    def to_message(self) -> Message:
        return Message(
            id=str(self.id),
            parent_id=str(self.parent_id) if self.parent_id is not None else None,
            sender=self.role.value,
            body=self.content,
            status=self.status.value,
            created_at=self.created_at,
        )


class ToolEventDocument(Document):
    model_config = _document_config

    id: ObjectId = Field(alias="_id")
    session_id: ObjectId
    message_id: ObjectId
    type: ToolEventType
    tool_call_id: str | None
    name: str | None
    payload: Any
    created_at: dt.datetime

    class Settings:
        name = "tool_events"
        indexes = [
            [("session_id", ASCENDING), ("message_id", ASCENDING), ("created_at", ASCENDING)],
        ]
