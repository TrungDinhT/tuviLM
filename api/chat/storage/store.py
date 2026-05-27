from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from hashlib import sha256
from typing import Self
from uuid import uuid4

from beanie import PydanticObjectId, init_beanie
from beanie.odm.operators.find.array import ElemMatch
from beanie.odm.operators.find.logical import Not
from beanie.odm.operators.update.array import Push
from beanie.odm.operators.update.general import Set
from beanie.odm.queries.update import UpdateResponse
from pydantic import BaseModel
from pymongo import AsyncMongoClient
from pymongo.errors import DuplicateKeyError

from api.chat.contracts import (
    DuplicateStreamInProgressError,
    IdempotencyConflictError,
    MissingOwnerIdError,
    NotFoundError,
)
from api.chat.models import (
    ChartProfile,
    ChatMessage,
    ChatMessageStatus,
    ChatRole,
    ChatSession,
    ChatSessionSummary,
    CreateChartProfileInput,
    CreateSessionInput,
    MessageOperationStatus,
    ReservedMessagePair,
    SessionContext,
)
from api.chat.storage.documents import (
    ChartProfileDocument,
    ChatSessionDocument,
    MessageOperationDocument,
    utc_now,
)
from api.chat.storage.mappers import (
    chart_profile_from_document,
    chat_message_from_document,
    chat_session_from_document,
    chat_session_summary_from_document,
)
from api.chat.storage.settings import MongoConversationHistorySettings


class MongoConversationHistoryStore:
    def __init__(
        self,
        *,
        mongo_client: AsyncMongoClient,
        database_name: str,
        stale_pending_after: timedelta = timedelta(minutes=15),
    ) -> None:
        self._mongo_client = mongo_client
        self._database_name = database_name
        self._stale_pending_after = stale_pending_after

    @classmethod
    async def connect(
        cls,
        settings: MongoConversationHistorySettings,
    ) -> Self:
        mongo_client = AsyncMongoClient(settings.uri, tz_aware=settings.tz_aware)
        store = cls(
            mongo_client=mongo_client,
            database_name=settings.database_name,
            stale_pending_after=timedelta(
                seconds=settings.stale_pending_after_seconds
            ),
        )
        await store._initialize_storage()
        return store

    async def _initialize_storage(self) -> None:
        await init_beanie(
            database=self._mongo_client[self._database_name],
            document_models=[ChartProfileDocument, ChatSessionDocument],
        )

    async def close(self) -> None:
        await self._mongo_client.close()

    async def create_chart_profile(
        self,
        owner_id: str | None,
        payload: CreateChartProfileInput,
        *,
        idempotency_key: str,
    ) -> ChartProfile:
        if not owner_id:
            raise MissingOwnerIdError

        fingerprint = _compute_fingerprint(payload)
        document = ChartProfileDocument(
            owner_id=owner_id,
            display_name=payload.display_name,
            birth_info=payload.birth_info,
            creation_idempotency_key=idempotency_key,
            creation_request_fingerprint=fingerprint,
        )

        try:
            await document.insert()
        except DuplicateKeyError:
            existing = await ChartProfileDocument.find_one(
                ChartProfileDocument.owner_id == owner_id,
                ChartProfileDocument.creation_idempotency_key == idempotency_key,
            )
            if existing is None:
                raise
            if existing.creation_request_fingerprint != fingerprint:
                raise IdempotencyConflictError
            return chart_profile_from_document(existing)

        return chart_profile_from_document(document)

    async def list_chart_profiles(self, owner_id: str) -> list[ChartProfile]:
        documents = await ChartProfileDocument.find(
            ChartProfileDocument.owner_id == owner_id
        ).to_list()
        return [chart_profile_from_document(document) for document in documents]

    async def delete_chart_profile(self, owner_id: str, chart_profile_id: str) -> None:
        profile = await _require_chart_profile(owner_id, chart_profile_id)
        await profile.delete()
        async for session in ChatSessionDocument.find(
            ChatSessionDocument.chart_profile_id == chart_profile_id
        ):
            await session.delete()

    async def create_session(
        self,
        owner_id: str,
        chart_profile_id: str,
        payload: CreateSessionInput,
        *,
        idempotency_key: str,
    ) -> ChatSession:
        await _require_chart_profile(owner_id, chart_profile_id)

        fingerprint = _compute_fingerprint(payload)
        document = ChatSessionDocument(
            chart_profile_id=chart_profile_id,
            title=payload.title,
            creation_idempotency_key=idempotency_key,
            creation_request_fingerprint=fingerprint,
        )

        try:
            await document.insert()
        except DuplicateKeyError:
            existing = await ChatSessionDocument.find_one(
                ChatSessionDocument.chart_profile_id == chart_profile_id,
                ChatSessionDocument.creation_idempotency_key == idempotency_key,
            )
            if existing is None:
                raise
            if existing.creation_request_fingerprint != fingerprint:
                raise IdempotencyConflictError
            return chat_session_from_document(existing)

        return chat_session_from_document(document)

    async def list_sessions(
        self, owner_id: str, chart_profile_id: str
    ) -> list[ChatSessionSummary]:
        await _require_chart_profile(owner_id, chart_profile_id)
        documents = await ChatSessionDocument.find(
            ChatSessionDocument.chart_profile_id == chart_profile_id
        ).to_list()
        return [chat_session_summary_from_document(document) for document in documents]

    async def delete_session(self, owner_id: str, session_id: str) -> None:
        session = await _get_session_for_owner(owner_id, session_id)
        await session.delete()

    async def load_session_context(self, owner_id: str, session_id: str) -> SessionContext:
        await _cleanup_stale_pending_messages(
            owner_id=owner_id,
            session_id=session_id,
            stale_pending_after=self._stale_pending_after,
        )
        session = await _get_session(session_id)
        profile = await _require_chart_profile(owner_id, session.chart_profile_id)
        return SessionContext(
            chart_profile=chart_profile_from_document(profile),
            session=chat_session_from_document(session),
        )

    async def reserve_message_pair(
        self,
        owner_id: str,
        session_id: str,
        *,
        user_content: str,
        idempotency_key: str,
    ) -> ReservedMessagePair:
        await _cleanup_stale_pending_messages(
            owner_id=owner_id,
            session_id=session_id,
            stale_pending_after=self._stale_pending_after,
        )
        session = await _get_session_for_owner(owner_id, session_id)
        fingerprint = _compute_fingerprint(user_content)
        existing_operation = _find_message_operation(session, idempotency_key)
        if existing_operation is None:
            return await _reserve_new_message_pair(
                session,
                user_content=user_content,
                idempotency_key=idempotency_key,
                fingerprint=fingerprint,
            )
        return _replay_reserved_message_pair(
            session,
            existing_operation,
            fingerprint=fingerprint,
        )

    async def finalize_assistant_message(
        self,
        owner_id: str,
        session_id: str,
        assistant_message_id: str,
        *,
        content: str,
        status: ChatMessageStatus,
    ) -> ChatMessage:
        session = await _get_session_for_owner(owner_id, session_id)
        update_fields, array_filters = _build_assistant_finalization_update(
            assistant_message_id,
            content=content,
            status=status,
        )
        updated_session = await ChatSessionDocument.find_one(
            ChatSessionDocument.id == session.id,
            _pending_assistant_message_filter(assistant_message_id),
        ).update(
            Set(update_fields),
            array_filters=array_filters,
            response_type=UpdateResponse.NEW_DOCUMENT,
        )
        if updated_session is None:
            updated_session = await _get_session_for_owner(owner_id, session_id)

        return _require_assistant_message(
            updated_session,
            assistant_message_id,
        )


@dataclass(frozen=True)
class _MessageReservation:
    user_message: ChatMessage
    assistant_message: ChatMessage
    operation: MessageOperationDocument


def _find_message_operation(
    session: ChatSessionDocument,
    idempotency_key: str,
) -> MessageOperationDocument | None:
    return next(
        (
            operation
            for operation in session.message_operations
            if operation.idempotency_key == idempotency_key
        ),
        None,
    )


def _require_assistant_message(
    session: ChatSessionDocument,
    assistant_message_id: str,
) -> ChatMessage:
    for message in session.messages:
        if message.id == assistant_message_id and message.role == ChatRole.ASSISTANT:
            return chat_message_from_document(message)
    raise NotFoundError


async def _cleanup_stale_pending_messages(
    *,
    owner_id: str,
    session_id: str,
    stale_pending_after: timedelta,
) -> None:
    session = await _get_session_for_owner(owner_id, session_id)
    cutoff = utc_now() - stale_pending_after
    stale_message_ids = [
        message.id
        for message in session.messages
        if message.role == ChatRole.ASSISTANT
        and message.status == ChatMessageStatus.PENDING
        and message.updated_at <= cutoff
    ]
    if not stale_message_ids:
        return

    update_fields, array_filters = _build_stale_pending_cleanup_update(
        stale_message_ids,
        cutoff=cutoff,
    )
    await ChatSessionDocument.find_one(
        ChatSessionDocument.id == session.id,
        _stale_pending_assistant_messages_filter(stale_message_ids, cutoff=cutoff),
    ).update(
        Set(update_fields),
        array_filters=array_filters,
    )


def _build_stale_pending_cleanup_update(
    assistant_message_ids: list[str],
    *,
    cutoff,
):
    now = utc_now()
    update_fields = {
        "messages.$[message].status": ChatMessageStatus.FAILED,
        "messages.$[message].updated_at": now,
        "message_operations.$[operation].status": MessageOperationStatus.FAILED,
        "message_operations.$[operation].updated_at": now,
        "updated_at": now,
    }
    array_filters = [
        _stale_pending_assistant_message_array_filter(
            assistant_message_ids,
            cutoff=cutoff,
        ),
        _in_progress_message_operation_array_filter(assistant_message_ids),
    ]
    return update_fields, array_filters


def _build_assistant_finalization_update(
    assistant_message_id: str,
    *,
    content: str,
    status: ChatMessageStatus,
):
    now = utc_now()
    update_fields = {
        "messages.$[message].content": content,
        "messages.$[message].status": status,
        "messages.$[message].updated_at": now,
        "updated_at": now,
    }
    array_filters = [_pending_assistant_message_array_filter(assistant_message_id)]

    operation_status = _message_operation_status_for(status)
    if operation_status is not None:
        update_fields.update(
            {
                "message_operations.$[operation].status": operation_status,
                "message_operations.$[operation].updated_at": now,
            }
        )
        array_filters.append({"operation.assistant_message_id": assistant_message_id})

    return update_fields, array_filters


def _message_operation_status_for(
    message_status: ChatMessageStatus,
) -> MessageOperationStatus | None:
    return {
        ChatMessageStatus.CONFIRMED: MessageOperationStatus.COMPLETED,
        ChatMessageStatus.FAILED: MessageOperationStatus.FAILED,
        ChatMessageStatus.CANCELLED: MessageOperationStatus.CANCELLED,
    }.get(message_status)


def _pending_assistant_message_filter(assistant_message_id: str):
    return ElemMatch(
        ChatSessionDocument.messages,
        {
            "id": assistant_message_id,
            "role": ChatRole.ASSISTANT,
            "status": ChatMessageStatus.PENDING,
        },
    )


def _pending_assistant_message_array_filter(assistant_message_id: str):
    return {
        "message.id": assistant_message_id,
        "message.role": ChatRole.ASSISTANT,
        "message.status": ChatMessageStatus.PENDING,
    }


def _stale_pending_assistant_messages_filter(
    assistant_message_ids: list[str],
    *,
    cutoff,
):
    return ElemMatch(
        ChatSessionDocument.messages,
        {
            "id": {"$in": assistant_message_ids},
            "role": ChatRole.ASSISTANT,
            "status": ChatMessageStatus.PENDING,
            "updated_at": {"$lte": cutoff},
        },
    )


def _stale_pending_assistant_message_array_filter(
    assistant_message_ids: list[str],
    *,
    cutoff,
):
    return {
        "message.id": {"$in": assistant_message_ids},
        "message.role": ChatRole.ASSISTANT,
        "message.status": ChatMessageStatus.PENDING,
        "message.updated_at": {"$lte": cutoff},
    }


def _in_progress_message_operation_array_filter(assistant_message_ids: list[str]):
    return {
        "operation.assistant_message_id": {"$in": assistant_message_ids},
        "operation.status": MessageOperationStatus.IN_PROGRESS,
    }


def _replay_reserved_message_pair(
    session: ChatSessionDocument,
    operation: MessageOperationDocument,
    *,
    fingerprint: str,
) -> ReservedMessagePair:
    if operation.request_fingerprint != fingerprint:
        raise IdempotencyConflictError
    user_message, assistant_message = _find_message_pair(
        session,
        user_message_id=operation.user_message_id,
        assistant_message_id=operation.assistant_message_id,
    )
    return ReservedMessagePair(
        user_message=chat_message_from_document(user_message),
        assistant_message=chat_message_from_document(assistant_message),
        operation_status=operation.status,
        replayed=True,
    )


def _find_message_pair(
    session: ChatSessionDocument,
    *,
    user_message_id: str,
    assistant_message_id: str,
) -> tuple[ChatMessage, ChatMessage]:
    user_message: ChatMessage | None = None
    assistant_message: ChatMessage | None = None

    for message in reversed(session.messages):
        if message.id == user_message_id:
            user_message = message
        elif message.id == assistant_message_id:
            assistant_message = message

        if user_message is not None and assistant_message is not None:
            return user_message, assistant_message

    raise NotFoundError


async def _reserve_new_message_pair(
    session: ChatSessionDocument,
    *,
    user_content: str,
    idempotency_key: str,
    fingerprint: str,
) -> ReservedMessagePair:
    reservation = _new_message_reservation(
        user_content=user_content,
        idempotency_key=idempotency_key,
        fingerprint=fingerprint,
    )
    updated_session = await _append_message_reservation(session, reservation)
    if updated_session is None:
        return await _replay_or_reject_after_reservation_miss(
            str(session.id),
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
        )

    return ReservedMessagePair(
        user_message=chat_message_from_document(reservation.user_message),
        assistant_message=chat_message_from_document(reservation.assistant_message),
    )


def _new_message_reservation(
    *,
    user_content: str,
    idempotency_key: str,
    fingerprint: str,
) -> _MessageReservation:
    now = utc_now()
    user_message = ChatMessage(
        id=str(uuid4()),
        role=ChatRole.USER,
        content=user_content,
        status=ChatMessageStatus.CONFIRMED,
        created_at=now,
        updated_at=now,
    )
    assistant_message = ChatMessage(
        id=str(uuid4()),
        role=ChatRole.ASSISTANT,
        content="",
        status=ChatMessageStatus.PENDING,
        created_at=now,
        updated_at=now,
    )
    operation=MessageOperationDocument(
        idempotency_key=idempotency_key,
        request_fingerprint=fingerprint,
        user_message_id=user_message.id,
        assistant_message_id=assistant_message.id,
        status=MessageOperationStatus.IN_PROGRESS,
        created_at=now,
        updated_at=now,
    )
    return _MessageReservation(
        user_message=user_message,
        assistant_message=assistant_message,
        operation=operation,
    )


async def _append_message_reservation(
    session: ChatSessionDocument,
    reservation: _MessageReservation,
) -> ChatSessionDocument | None:
    return await ChatSessionDocument.find_one(
        ChatSessionDocument.id == session.id,
        _no_message_operation_filter(reservation.operation.idempotency_key),
        _no_pending_assistant_message_filter(),
    ).update(
        Push(
            {
                ChatSessionDocument.messages: {
                    "$each": [
                        reservation.user_message.model_dump(mode="python"),
                        reservation.assistant_message.model_dump(mode="python"),
                    ]
                },
                ChatSessionDocument.message_operations: (
                    reservation.operation.model_dump(mode="python")
                ),
            }
        ),
        Set({ChatSessionDocument.updated_at: reservation.user_message.updated_at}),
        response_type=UpdateResponse.NEW_DOCUMENT,
    )


def _no_message_operation_filter(idempotency_key: str):
    return Not(
        ElemMatch(
            ChatSessionDocument.message_operations,
            {"idempotency_key": idempotency_key},
        )
    )


def _no_pending_assistant_message_filter():
    return Not(
        ElemMatch(
            ChatSessionDocument.messages,
            {
                "role": ChatRole.ASSISTANT,
                "status": ChatMessageStatus.PENDING,
            },
        )
    )


async def _replay_or_reject_after_reservation_miss(
    session_id: str,
    *,
    idempotency_key: str,
    fingerprint: str,
) -> ReservedMessagePair:
    current_session = await _get_session(session_id)
    existing_operation = _find_message_operation(current_session, idempotency_key)
    if existing_operation is not None:
        return _replay_reserved_message_pair(
            current_session,
            existing_operation,
            fingerprint=fingerprint,
        )
    if _has_pending_assistant_message(current_session):
        raise DuplicateStreamInProgressError
    raise NotFoundError


def _has_pending_assistant_message(session: ChatSessionDocument) -> bool:
    return any(
        message.role == ChatRole.ASSISTANT
        and message.status == ChatMessageStatus.PENDING
        for message in session.messages
    )


def _object_id(value: str) -> PydanticObjectId | None:
    try:
        return PydanticObjectId(value)
    except (TypeError, ValueError):
        return None


async def _require_chart_profile(
    owner_id: str, chart_profile_id: str
) -> ChartProfileDocument:
    chart_profile_object_id = _object_id(chart_profile_id)
    if chart_profile_object_id is None:
        raise NotFoundError

    profile = await ChartProfileDocument.find_one(
        ChartProfileDocument.id == chart_profile_object_id,
        ChartProfileDocument.owner_id == owner_id,
    )
    if profile is None:
        raise NotFoundError

    return profile


async def _get_session(session_id: str) -> ChatSessionDocument:
    session_object_id = _object_id(session_id)
    if session_object_id is None:
        raise NotFoundError

    session = await ChatSessionDocument.find_one(
        ChatSessionDocument.id == session_object_id
    )
    if session is None:
        raise NotFoundError

    return session


async def _get_session_for_owner(owner_id: str, session_id: str) -> ChatSessionDocument:
    session = await _get_session(session_id)
    await _require_chart_profile(owner_id, session.chart_profile_id)
    return session


def _compute_fingerprint(value: BaseModel | str) -> str:
    if isinstance(value, BaseModel):
        payload = value.model_dump_json()
    else:
        payload = value
    return sha256(payload.encode("utf-8")).hexdigest()
