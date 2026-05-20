from __future__ import annotations

import datetime as dt
from enum import StrEnum
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_serializer

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


class MongoDocument(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    id: ObjectId = Field(alias="_id")

    def to_mongo(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True)

    @field_serializer("*")
    def _serialize_str_enum(self, value: Any) -> Any:
        if isinstance(value, StrEnum):
            return value.value
        return value


class ChartProfileDocument(MongoDocument):
    client_id: str
    display_name: str
    birth_metadata: dict[str, Any]
    status: RecordStatus
    created_at: dt.datetime
    updated_at: dt.datetime


class SessionDocument(MongoDocument):
    client_id: str
    chart_profile_id: ObjectId
    active_leaf_id: ObjectId
    status: RecordStatus
    created_at: dt.datetime
    updated_at: dt.datetime


class MessageDocument(MongoDocument):
    session_id: ObjectId
    parent_id: ObjectId | None
    role: MessageRole
    content: str
    status: MessageStatus
    created_at: dt.datetime
    updated_at: dt.datetime

    def to_message(self) -> Message:
        return Message(
            id=str(self.id),
            parent_id=str(self.parent_id) if self.parent_id is not None else None,
            sender=self.role.value,
            body=self.content,
            status=self.status.value,
            streaming=self.status == MessageStatus.STREAMING,
            created_at=self.created_at,
        )


class ToolEventDocument(MongoDocument):
    session_id: ObjectId
    message_id: ObjectId
    type: ToolEventType
    tool_call_id: str | None
    name: str | None
    payload: Any
    created_at: dt.datetime
