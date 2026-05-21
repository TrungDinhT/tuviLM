from __future__ import annotations

import datetime as dt
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class GenderCode(StrEnum):
    MALE = "M"
    FEMALE = "F"


class CalendarKind(StrEnum):
    SOLAR = "solar"
    LUNAR = "lunar"


class ChatMessageStatus(StrEnum):
    CONFIRMED = "confirmed"
    STREAMING = "streaming"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DELETED = "deleted"


class TuviTimePayload(BaseModel):
    date: int = Field(ge=1, le=31)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=1900, le=2099)
    hour: int = Field(ge=0, le=23)
    gender: GenderCode


class BirthMetadata(TuviTimePayload):
    minute: int = Field(ge=0, le=59)
    calendar: CalendarKind = CalendarKind.SOLAR


class BuildLasoRequest(BirthMetadata):
    client_id: str = Field(min_length=1)
    display_name: str = ""


class BuildSaoLuuRequest(BaseModel):
    observation_time: TuviTimePayload


class StarPayload(BaseModel):
    name: str
    display: str
    element: str


# TODO : Need to adapt with new view
class CungPayload(BaseModel):
    position: str
    role: str | None = None
    chinh_tinh: list[str]
    phu_tinh: list[StarPayload]
    tuhoa: list[str]
    trang_sinh: str | None = None
    is_tuan: bool = False
    is_triet: bool = False
    is_cung_than: bool = False
    age_daivan: int | None = None
    saoLuu: list[StarPayload]


class BuildLasoResponse(BaseModel):
    id: str
    chart_profile_id: str
    session_id: str
    active_leaf_id: str
    summary: str
    ban_menh_name: str
    cuc_name: str
    menh_cuc_relation_label: str
    cung_by_position: dict[str, CungPayload]


class BuildSaoLuuResponse(BaseModel):
    cung_by_position: dict[str, CungPayload]


class ChatRequest(BaseModel):
    client_id: str = Field(min_length=1)
    session_id: str
    parent_id: str
    content: str = Field(min_length=1)


class ChatToolCall(BaseModel):
    id: str | None = None
    name: str
    arguments: Any


class ChatResponse(BaseModel):
    answer: str
    tool_calls: list[ChatToolCall] = Field(default_factory=list)


class ChatMessageDTO(BaseModel):
    id: str
    parent_id: str | None = None
    sender: str
    body: str
    status: ChatMessageStatus = ChatMessageStatus.CONFIRMED
    created_at: dt.datetime | None = None


class SessionRef(BaseModel):
    id: str
    chart_profile_id: str
    active_leaf_id: str


class ChartProfileDTO(BaseModel):
    id: str
    client_id: str
    display_name: str
    birth_metadata: BirthMetadata


class SessionDetailResponse(BaseModel):
    session: SessionRef
    chart_profile: ChartProfileDTO
    laso: BuildLasoResponse
    messages: list[ChatMessageDTO]
    has_more_before: bool = False


class SessionSummary(BaseModel):
    session_id: str
    chart_profile_id: str
    active_leaf_id: str | None = None
    display_name: str
    birth_year: int | None = None
    last_message_preview: str = ""
    message_count: int = 0
    updated_at: dt.datetime | None = None


class SessionListResponse(BaseModel):
    sessions: list[SessionSummary]
