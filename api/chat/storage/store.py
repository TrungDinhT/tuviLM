from __future__ import annotations

from hashlib import sha256
from typing import Self
from uuid import uuid4

from beanie import PydanticObjectId, init_beanie
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


class MongoConversationHistoryStore:
    def __init__(
        self,
        *,
        mongo_client: AsyncMongoClient,
        database_name: str,
    ) -> None:
        self._mongo_client = mongo_client
        self._database_name = database_name

    @classmethod
    async def connect(
        cls,
        *,
        database_name: str,
        mongodb_uri: str,
        **client_kwargs,
    ) -> Self:
        mongo_client = AsyncMongoClient(mongodb_uri, **client_kwargs)
        store = cls(
            mongo_client=mongo_client,
            database_name=database_name,
        )
        await init_beanie(
            database=mongo_client[database_name],
            document_models=[ChartProfileDocument, ChatSessionDocument],
        )
        return store

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
                {
                    "owner_id": owner_id,
                    "creation_idempotency_key": idempotency_key,
                }
            )
            if existing is None:
                raise
            if existing.creation_request_fingerprint != fingerprint:
                raise IdempotencyConflictError
            return chart_profile_from_document(existing)

        return chart_profile_from_document(document)

    async def list_chart_profiles(self, owner_id: str) -> list[ChartProfile]:
        documents = await ChartProfileDocument.find({"owner_id": owner_id}).to_list()
        return [chart_profile_from_document(document) for document in documents]

    async def delete_chart_profile(self, owner_id: str, chart_profile_id: str) -> None:
        profile = await _require_chart_profile(owner_id, chart_profile_id)
        await profile.delete()
        async for session in ChatSessionDocument.find(
            {"chart_profile_id": chart_profile_id}
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
                {
                    "chart_profile_id": chart_profile_id,
                    "creation_idempotency_key": idempotency_key,
                }
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
            {"chart_profile_id": chart_profile_id}
        ).to_list()
        return [chat_session_summary_from_document(document) for document in documents]

    async def delete_session(self, owner_id: str, session_id: str) -> None:
        session = await _get_session_for_owner(owner_id, session_id)
        await session.delete()

    async def load_session_context(self, owner_id: str, session_id: str) -> SessionContext:
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

        for message in session.messages:
            if message.id != assistant_message_id or message.role != ChatRole.ASSISTANT:
                continue

            now = utc_now()
            message.content = content
            message.status = status
            message.updated_at = now
            session.updated_at = now

            operation_status = {
                ChatMessageStatus.CONFIRMED: MessageOperationStatus.COMPLETED,
                ChatMessageStatus.FAILED: MessageOperationStatus.FAILED,
                ChatMessageStatus.CANCELLED: MessageOperationStatus.CANCELLED,
            }.get(status)
            if operation_status is not None:
                for operation in session.message_operations:
                    if operation.assistant_message_id == assistant_message_id:
                        operation.status = operation_status
                        operation.updated_at = now
                        break

            await session.save()
            return chat_message_from_document(message)

        raise NotFoundError


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
    if any(
        message.role == ChatRole.ASSISTANT
        and message.status == ChatMessageStatus.PENDING
        for message in session.messages
    ):
        raise DuplicateStreamInProgressError

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
    session.messages.extend([user_message, assistant_message])
    session.message_operations.append(
        MessageOperationDocument(
            idempotency_key=idempotency_key,
            request_fingerprint=fingerprint,
            user_message_id=user_message.id,
            assistant_message_id=assistant_message.id,
            status=MessageOperationStatus.IN_PROGRESS,
            created_at=now,
            updated_at=now,
        )
    )
    session.updated_at = now
    await session.save()
    return ReservedMessagePair(
        user_message=chat_message_from_document(user_message),
        assistant_message=chat_message_from_document(assistant_message),
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
        {"_id": chart_profile_object_id, "owner_id": owner_id}
    )
    if profile is None:
        raise NotFoundError

    return profile


async def _get_session(session_id: str) -> ChatSessionDocument:
    session_object_id = _object_id(session_id)
    if session_object_id is None:
        raise NotFoundError

    session = await ChatSessionDocument.find_one({"_id": session_object_id})
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
