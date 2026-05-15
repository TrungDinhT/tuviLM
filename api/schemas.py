from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class TuviTimePayload(BaseModel):
    date: int = Field(ge=1, le=31)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=1900, le=2099)
    hour: int = Field(ge=0, le=23)
    gender: Literal["M", "F"]


class BuildLasoRequest(TuviTimePayload):
    pass


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
    summary: str
    ban_menh_name: str
    cuc_name: str
    menh_cuc_relation_label: str
    cung_by_position: dict[str, CungPayload]


class BuildSaoLuuResponse(BaseModel):
    cung_by_position: dict[str, CungPayload]


class ChatRequest(BaseModel):
    message: str


class ChatToolCall(BaseModel):
    id: str | None = None
    name: str
    arguments: Any


class ChatResponse(BaseModel):
    answer: str
    tool_calls: list[ChatToolCall] = Field(default_factory=list)
