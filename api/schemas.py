from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from api.chat.models import BirthInfo, ChatSession, ChatSessionSummary


class BuildLasoRequest(BirthInfo):
    pass


class PreviewLasoRequest(BirthInfo):
    # Cung Mệnh's chính tinh do not depend on gender, so the preview accepts
    # birth data before the user has picked one. The value is ignored.
    gender: Literal["M", "F"] | None = None


class PreviewLasoResponse(BaseModel):
    # Clean star names — no trạng thái suffix like "(Miếu)" — so clients can
    # key content and theming off them directly. Empty for vô chính diệu.
    chinh_tinh: list[str]
    menh_position: str


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


# Stable keys for the build response's foundation fields. These mirror the
# domain enums (`MenhCucRelationType`, `DiaChi`, `NguHanh`) and the agent
# tool's polarity relation, so clients key content off them rather than off
# the display labels.
MenhCucRelationKey = Literal[
    "sinh_xuat", "sinh_nhap", "khac_xuat", "khac_nhap", "binh_hoa"
]
AmDuongRelationKey = Literal["thuan_ly", "nghich_ly"]
DiaChiKey = Literal[
    "ty", "suu", "dan", "meo", "thin", "ti",
    "ngo", "mui", "than", "dau", "tuat", "hoi",
]
NguHanhKey = Literal["Kim", "Mộc", "Thủy", "Hỏa", "Thổ"]


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
    menh_cuc_relation: MenhCucRelationKey
    am_duong_relation: AmDuongRelationKey
    dia_chi_natal_year: DiaChiKey
    ban_menh_ngu_hanh: NguHanhKey
    cung_by_position: dict[str, CungPayload]


class BuildSaoLuuResponse(BaseModel):
    cung_by_position: dict[str, CungPayload]
