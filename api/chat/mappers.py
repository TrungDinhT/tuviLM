from __future__ import annotations

from api.chat.contracts import BirthInfo, Message, SessionInfo, SessionRecord
from api.schemas import (
    BirthMetadata,
    CalendarKind,
    ChatMessageDTO,
    ChatMessageStatus,
    ChartProfileDTO,
    GenderCode,
    SessionDetailResponse,
    SessionRef,
    SessionSummary,
    BuildLasoResponse,
)


def birth_info_to_metadata(birth_info: BirthInfo) -> BirthMetadata:
    return BirthMetadata(
        calendar=CalendarKind(birth_info.calendar),
        date=birth_info.date,
        month=birth_info.month,
        year=birth_info.year,
        hour=birth_info.hour,
        minute=birth_info.minute,
        gender=GenderCode(birth_info.gender),
    )


def birth_metadata_to_info(birth: BirthMetadata) -> BirthInfo:
    return BirthInfo(
        calendar=birth.calendar.value,
        date=birth.date,
        month=birth.month,
        year=birth.year,
        hour=birth.hour,
        minute=birth.minute,
        gender=birth.gender.value,
    )


def message_to_dto(message: Message) -> ChatMessageDTO:
    return ChatMessageDTO(
        id=message.id,
        parent_id=message.parent_id,
        sender=message.sender,
        body=message.body,
        status=ChatMessageStatus(message.status),
        created_at=message.created_at,
    )


def session_info_to_summary(si: SessionInfo) -> SessionSummary:
    return SessionSummary(
        session_id=si.session_id,
        chart_profile_id=si.chart_profile_id,
        active_leaf_id=si.active_leaf_id,
        display_name=si.display_name,
        birth_year=si.birth_year,
        last_message_preview=si.last_message_preview,
        message_count=si.message_count,
        updated_at=si.updated_at,
    )


def record_to_detail(
    record: SessionRecord,
    laso: BuildLasoResponse,
    client_id: str,
) -> SessionDetailResponse:
    return SessionDetailResponse(
        session=SessionRef(
            id=record.session_id,
            chart_profile_id=record.chart_profile_id,
            active_leaf_id=record.active_leaf_id,
        ),
        chart_profile=ChartProfileDTO(
            id=record.chart_profile_id,
            client_id=client_id,
            display_name=record.display_name,
            birth_metadata=birth_info_to_metadata(record.birth_info),
        ),
        laso=laso,
        messages=[message_to_dto(m) for m in record.messages],
        has_more_before=record.has_more_before,
    )
