from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BuildLasoRequest(BaseModel):
    date: int = Field(ge=1, le=31)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=1900, le=2099)
    hour: int = Field(ge=0, le=23)
    gender: Literal["M", "F"]


class StarPayload(BaseModel):
    name: str
    display: str
    element: str


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


class BuildLasoResponse(BaseModel):
    id: str
    summary: str
    cung_by_position: dict[str, CungPayload]


class AnalyzeCungRequest(BaseModel):
    date: int = Field(ge=1, le=31)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=1900, le=2099)
    hour: int = Field(ge=0, le=23)
    gender: Literal["M", "F"]
    position: str
    model: str = "gpt-4.1-mini"


class AnalyzeCungResponse(BaseModel):
    position: str
    role: str | None = None
    analysis: str


class DummyChatRequest(BaseModel):
    message: str


class DummyChatResponse(BaseModel):
    answer: str
