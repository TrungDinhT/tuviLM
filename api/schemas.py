from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from api.chat.models import BirthInfo, ChatSession, ChatSessionSummary


class BuildLasoRequest(BirthInfo):
    pass


class BuildSaoLuuRequest(BaseModel):
    observation_time: BirthInfo


class CreateAnonymousResponse(BaseModel):
    owner_id: str


class CreateChartProfileRequest(BaseModel):
    display_name: str
    birth_info: BirthInfo


class ChartProfilePayload(BaseModel):
    id: str
    display_name: str
    birth_info: BirthInfo
    created_at: datetime
    updated_at: datetime


class CreateChartProfileResponse(BaseModel):
    chart_profile: ChartProfilePayload


class ListChartProfilesResponse(BaseModel):
    chart_profiles: list[ChartProfilePayload]


class CreateSessionRequest(BaseModel):
    title: str | None = None


class CreateSessionResponse(BaseModel):
    session: ChatSession


class ListSessionsResponse(BaseModel):
    sessions: list[ChatSessionSummary]


class GetSessionResponse(BaseModel):
    session: ChatSession


class SessionChatStreamRequest(BaseModel):
    content: str = Field(min_length=1)


class StarPayload(BaseModel):
    name: str
    display: str
    element: str
    sao_type: list[str] = Field(default_factory=list)


# TODO : Need to adapt with new view
class CungPayload(BaseModel):
    position: str
    role: str | None = None
    chinh_tinh: list[str]
    phu_tinh: list[StarPayload]
    tuhoa: list[StarPayload]
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
