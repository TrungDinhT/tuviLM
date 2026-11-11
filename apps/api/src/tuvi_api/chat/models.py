from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class ChatRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessageStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessageOperationStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BirthInfo(BaseModel):
    calendar: Literal["solar"] = "solar"
    year: int = Field(ge=1900, le=2099)
    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)
    hour: int = Field(ge=0, le=23)
    gender: Literal["M", "F"]


class ChartProfile(BaseModel):
    id: str
    owner_id: str
    display_name: str
    birth_info: BirthInfo
    created_at: datetime
    updated_at: datetime


class CreateChartProfileInput(BaseModel):
    display_name: str
    birth_info: BirthInfo


class ChatMessage(BaseModel):
    id: str
    role: ChatRole
    content: str
    status: ChatMessageStatus
    created_at: datetime
    updated_at: datetime


class ChatSession(BaseModel):
    id: str
    chart_profile_id: str
    title: str | None = None
    messages: list[ChatMessage]
    created_at: datetime
    updated_at: datetime


class CreateSessionInput(BaseModel):
    title: str | None = None


class ChatSessionSummary(BaseModel):
    id: str
    chart_profile_id: str
    title: str | None = None
    message_count: int
    created_at: datetime
    updated_at: datetime


class SessionContext(BaseModel):
    chart_profile: ChartProfile
    session: ChatSession


class ReservedMessagePair(BaseModel):
    user_message: ChatMessage
    assistant_message: ChatMessage
    operation_status: MessageOperationStatus = MessageOperationStatus.IN_PROGRESS
    replayed: bool = False
