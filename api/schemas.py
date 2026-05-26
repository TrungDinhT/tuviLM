from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from api.chat.models import ChatMessageStatus, ChatRole


class BirthInfoPayload(BaseModel):
    calendar: Literal["solar"] = "solar"
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=1900, le=2099)
    day: int = Field(ge=1, le=31)
    hour: int = Field(ge=0, le=23)
    gender: Literal["M", "F"]


class BuildLasoRequest(BirthInfoPayload):
    pass


class BuildSaoLuuRequest(BaseModel):
    observation_time: BirthInfoPayload


class CreateAnonymousResponse(BaseModel):
    owner_id: str


class CreateChartProfileRequest(BaseModel):
    display_name: str
    birth_info: BirthInfoPayload


class ChartProfilePayload(BaseModel):
    id: str
    display_name: str
    birth_info: BirthInfoPayload
    created_at: datetime
    updated_at: datetime


class CreateChartProfileResponse(BaseModel):
    chart_profile: ChartProfilePayload


class ListChartProfilesResponse(BaseModel):
    chart_profiles: list[ChartProfilePayload]


class CreateSessionRequest(BaseModel):
    title: str | None = None


class ChatMessagePayload(BaseModel):
    id: str
    role: ChatRole
    content: str
    status: ChatMessageStatus
    created_at: datetime
    updated_at: datetime


class ChatSessionPayload(BaseModel):
    id: str
    chart_profile_id: str
    title: str | None = None
    messages: list[ChatMessagePayload]
    created_at: datetime
    updated_at: datetime


class CreateSessionResponse(BaseModel):
    session: ChatSessionPayload


class ChatSessionSummaryPayload(BaseModel):
    id: str
    chart_profile_id: str
    title: str | None = None
    message_count: int
    created_at: datetime
    updated_at: datetime


class ListSessionsResponse(BaseModel):
    sessions: list[ChatSessionSummaryPayload]


class GetSessionResponse(BaseModel):
    session: ChatSessionPayload


class SessionChatStreamRequest(BaseModel):
    content: str = Field(min_length=1)


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
    summary: str
    ban_menh_name: str
    cuc_name: str
    menh_cuc_relation_label: str
    cung_by_position: dict[str, CungPayload]


class BuildSaoLuuResponse(BaseModel):
    cung_by_position: dict[str, CungPayload]
