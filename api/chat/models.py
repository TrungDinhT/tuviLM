from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from src.refactored.calendar import lunar_month_length
from src.refactored.model.elementary import DiaChi


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
    calendar: Literal["solar", "lunar"] = "solar"
    year: int = Field(ge=1900, le=2099)
    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)
    hour: int | None = Field(default=None, ge=0, le=23)
    hour_in_dia_chi: DiaChi | None = None
    is_leap_month: bool = False
    gender: Literal["M", "F"]

    @model_validator(mode="after")
    def validate_calendar_fields(self) -> "BirthInfo":
        if self.calendar == "solar":
            if self.hour is None:
                raise ValueError("Vui lòng nhập giờ sinh dương lịch")
            if self.hour_in_dia_chi is not None:
                raise ValueError("Dương lịch không dùng giờ sinh theo Địa Chi")
            if self.is_leap_month:
                raise ValueError("Dương lịch không dùng tháng nhuận âm lịch")
            return self

        if self.hour is not None:
            raise ValueError("Âm lịch không dùng giờ sinh dương lịch")
        if self.hour_in_dia_chi is None:
            raise ValueError("Vui lòng chọn giờ sinh theo Địa Chi")

        month_length = lunar_month_length(
            self.year,
            self.month,
            self.is_leap_month,
        )
        if self.day > month_length:
            raise ValueError(
                f"Âm lịch năm {self.year} tháng {self.month} chỉ có "
                f"{month_length} ngày"
            )
        return self


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
