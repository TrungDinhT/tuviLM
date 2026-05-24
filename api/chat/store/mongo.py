from __future__ import annotations

import datetime as dt
from dataclasses import asdict
from typing import Any

from beanie.operators import In
from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from api.chat.contracts import (
    BirthInfo,
    ChatTurnStart,
    ChartSessionCreated,
    ROOT_GREETING,
    SessionInfo,
    SessionRecord,
)
from api.chat.store.documents import (
    ChartProfileDocument,
    MessageDocument,
    MessageRole,
    MessageStatus,
    RecordStatus,
    SessionDocument,
    ToolEventDocument,
    ToolEventType,
)


class NotFoundError(ValueError):
    pass


class InvalidChatParentError(ValueError):
    pass


def _oid(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise NotFoundError("Invalid id")
    return ObjectId(value)


def _sid(value: ObjectId | None) -> str | None:
    return str(value) if value is not None else None


def _utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _birth_info_from_doc(profile_doc: ChartProfileDocument) -> BirthInfo:
    return BirthInfo(**profile_doc.birth_metadata)


class MongoChatStore:
    def __init__(self, db: AsyncDatabase[Any]):
        self.db = db

    async def ping(self) -> None:
        await self.db.client.admin.command("ping")

    async def mark_stale_streaming_messages_failed(self) -> int:
        result = await self.db.messages.update_many(
            {"role": MessageRole.ASSISTANT.value, "status": MessageStatus.STREAMING.value},
            {
                "$set": {
                    "status": MessageStatus.FAILED.value,
                    "error": "Server restarted before the assistant response completed.",
                    "updated_at": _utc_now(),
                }
            },
        )
        return int(result.modified_count)

    async def create_chart_session(
        self,
        *,
        client_id: str,
        display_name: str,
        birth_info: BirthInfo,
        root_greeting: str = ROOT_GREETING,
    ) -> ChartSessionCreated:
        now = _utc_now()
        profile_id = ObjectId()
        session_id = ObjectId()
        root_id = ObjectId()

        profile_doc = ChartProfileDocument(
            _id=profile_id,
            client_id=client_id,
            display_name=display_name,
            birth_metadata=asdict(birth_info),
            status=RecordStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
        root_message = MessageDocument(
            _id=root_id,
            session_id=session_id,
            parent_id=None,
            role=MessageRole.ASSISTANT,
            content=root_greeting,
            status=MessageStatus.CONFIRMED,
            created_at=now,
            updated_at=now,
        )
        session_doc = SessionDocument(
            _id=session_id,
            client_id=client_id,
            chart_profile_id=profile_id,
            active_leaf_id=root_id,
            status=RecordStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )

        async def _txn_callback(mongo_session):
            await profile_doc.insert(session=mongo_session)
            await root_message.insert(session=mongo_session)
            await session_doc.insert(session=mongo_session)

        async with self.db.client.start_session() as mongo_session:
            await mongo_session.with_transaction(_txn_callback)

        return ChartSessionCreated(
            chart_profile_id=str(profile_id),
            session_id=str(session_id),
            active_leaf_id=str(root_id),
        )

    async def get_session(self, *, client_id: str, session_id: str) -> SessionRecord:
        session_oid = _oid(session_id)
        session_doc = await SessionDocument.find_one(
            SessionDocument.id == session_oid,
            SessionDocument.client_id == client_id,
            SessionDocument.status == RecordStatus.ACTIVE,
        )
        if not session_doc:
            raise NotFoundError("Session not found")

        profile_doc = await ChartProfileDocument.find_one(
            ChartProfileDocument.id == session_doc.chart_profile_id,
            ChartProfileDocument.client_id == client_id,
            ChartProfileDocument.status == RecordStatus.ACTIVE,
        )
        if not profile_doc:
            raise NotFoundError("Chart profile not found")

        messages = await self._active_path(session_doc.active_leaf_id)
        return SessionRecord(
            session_id=str(session_doc.id),
            chart_profile_id=str(profile_doc.id),
            active_leaf_id=str(session_doc.active_leaf_id),
            birth_info=_birth_info_from_doc(profile_doc),
            display_name=profile_doc.display_name,
            messages=[doc.to_message() for doc in messages],
            has_more_before=False,
        )

    async def list_sessions(self, *, client_id: str) -> list[SessionInfo]:
        sessions = await SessionDocument.find(
            SessionDocument.client_id == client_id,
            SessionDocument.status == RecordStatus.ACTIVE,
        ).sort(-SessionDocument.updated_at).limit(100).to_list()

        if not sessions:
            return []

        profile_ids = [doc.chart_profile_id for doc in sessions]
        profiles: dict[ObjectId, ChartProfileDocument] = {}
        async for doc in ChartProfileDocument.find(
            In(ChartProfileDocument.id, profile_ids)
        ):
            profiles[doc.id] = doc

        leaf_ids = [doc.active_leaf_id for doc in sessions]
        leaves: dict[ObjectId, MessageDocument] = {}
        async for doc in MessageDocument.find(In(MessageDocument.id, leaf_ids)):
            leaves[doc.id] = doc

        summaries: list[SessionInfo] = []
        for doc in sessions:
            profile = profiles.get(doc.chart_profile_id)
            leaf = leaves.get(doc.active_leaf_id)
            message_count = await self.db.messages.count_documents(
                {"session_id": doc.id, "status": {"$ne": MessageStatus.DELETED.value}}
            )
            summaries.append(
                SessionInfo(
                    session_id=str(doc.id),
                    chart_profile_id=str(doc.chart_profile_id),
                    active_leaf_id=_sid(doc.active_leaf_id),
                    display_name=profile.display_name if profile else "Giấu tên",
                    birth_year=profile.birth_metadata.get("year") if profile else None,
                    last_message_preview=(leaf.content if leaf else "")[:120],
                    message_count=message_count,
                    updated_at=doc.updated_at,
                )
            )
        return summaries

    async def soft_delete_session(self, *, client_id: str, session_id: str) -> None:
        session_oid = _oid(session_id)
        now = _utc_now()

        async def _txn_callback(mongo_session):
            result = await self.db.sessions.update_one(
                {
                    "_id": session_oid,
                    "client_id": client_id,
                    "status": RecordStatus.ACTIVE.value,
                },
                {"$set": {"status": RecordStatus.DELETED.value, "updated_at": now}},
                session=mongo_session,
            )
            if result.matched_count == 0:
                raise NotFoundError("Session not found")
            await self.db.messages.update_many(
                {"session_id": session_oid, "status": {"$ne": MessageStatus.DELETED.value}},
                {"$set": {"status": MessageStatus.DELETED.value, "updated_at": now}},
                session=mongo_session,
            )

        async with self.db.client.start_session() as mongo_session:
            await mongo_session.with_transaction(_txn_callback)

    async def start_chat_turn(
        self,
        *,
        client_id: str,
        session_id: str,
        parent_id: str,
        content: str,
    ) -> ChatTurnStart:
        session_oid = _oid(session_id)
        parent_oid = _oid(parent_id)
        now = _utc_now()
        user_id = ObjectId()
        assistant_id = ObjectId()
        profile_doc: ChartProfileDocument | None = None

        async def _txn_callback(mongo_session):
            nonlocal profile_doc
            session_doc = await SessionDocument.find_one(
                SessionDocument.id == session_oid,
                SessionDocument.client_id == client_id,
                SessionDocument.status == RecordStatus.ACTIVE,
                session=mongo_session,
            )
            if not session_doc:
                raise NotFoundError("Session not found")
            if session_doc.active_leaf_id != parent_oid:
                raise InvalidChatParentError("Parent message is not the active leaf")

            parent_doc = await MessageDocument.find_one(
                MessageDocument.id == parent_oid,
                MessageDocument.session_id == session_oid,
                MessageDocument.status == MessageStatus.CONFIRMED,
                session=mongo_session,
            )
            if not parent_doc:
                raise InvalidChatParentError("Parent message is not confirmed")

            profile_doc = await ChartProfileDocument.find_one(
                ChartProfileDocument.id == session_doc.chart_profile_id,
                ChartProfileDocument.client_id == session_doc.client_id,
                ChartProfileDocument.status == RecordStatus.ACTIVE,
                session=mongo_session,
            )
            if not profile_doc:
                raise NotFoundError("Chart profile not found")

            await MessageDocument(
                _id=user_id,
                session_id=session_oid,
                parent_id=parent_oid,
                role=MessageRole.USER,
                content=content,
                status=MessageStatus.CONFIRMED,
                created_at=now,
                updated_at=now,
            ).insert(session=mongo_session)
            await MessageDocument(
                _id=assistant_id,
                session_id=session_oid,
                parent_id=user_id,
                role=MessageRole.ASSISTANT,
                content="",
                status=MessageStatus.STREAMING,
                created_at=now,
                updated_at=now,
            ).insert(session=mongo_session)

        async with self.db.client.start_session() as mongo_session:
            await mongo_session.with_transaction(_txn_callback)

        if profile_doc is None:
            raise NotFoundError("Chart profile not found")

        history_docs = await self._active_path(parent_oid)
        return ChatTurnStart(
            user_message_id=str(user_id),
            assistant_message_id=str(assistant_id),
            birth_info=_birth_info_from_doc(profile_doc),
            history=[doc.to_message() for doc in history_docs],
        )

    async def confirm_assistant_message(
        self,
        *,
        session_id: str,
        assistant_message_id: str,
        content: str,
    ) -> None:
        session_oid = _oid(session_id)
        assistant_oid = _oid(assistant_message_id)
        now = _utc_now()

        async def _txn_callback(mongo_session):
            # STEP 1: Touch the session first to match soft_delete_session's lock hierarchy
            session_check = await SessionDocument.find_one(
                SessionDocument.id == session_oid,
                SessionDocument.status == RecordStatus.ACTIVE,
                session=mongo_session,
            )
            if not session_check:
                raise NotFoundError("Active session not found")

            updated = await self.db.messages.find_one_and_update(
                {
                    "_id": assistant_oid,
                    "session_id": session_oid,
                    "role": MessageRole.ASSISTANT.value,
                    "status": MessageStatus.STREAMING.value,
                },
                {
                    "$set": {
                        "content": content,
                        "status": MessageStatus.CONFIRMED.value,
                        "updated_at": now,
                    }
                },
                return_document=ReturnDocument.AFTER,
                session=mongo_session,
            )
            if not updated:
                raise NotFoundError("Assistant message not found")

            result = await self.db.sessions.update_one(
                {"_id": session_oid, "status": RecordStatus.ACTIVE.value},
                {
                    "$set": {
                        "active_leaf_id": assistant_oid,
                        "updated_at": now,
                    }
                },
                session=mongo_session,
            )
            if result.matched_count == 0:
                raise NotFoundError("Session not found or was deleted during confirmation")

        async with self.db.client.start_session() as mongo_session:
            await mongo_session.with_transaction(_txn_callback)

    async def mark_assistant_message_failed(
        self,
        *,
        assistant_message_id: str,
        content: str,
        error: str,
    ) -> None:
        await self._mark_assistant_terminal(
            assistant_message_id=assistant_message_id,
            status=MessageStatus.FAILED,
            content=content,
            error=error,
        )

    async def mark_assistant_message_cancelled(
        self,
        *,
        assistant_message_id: str,
        content: str,
    ) -> None:
        await self._mark_assistant_terminal(
            assistant_message_id=assistant_message_id,
            status=MessageStatus.CANCELLED,
            content=content,
            error=None,
        )

    async def add_tool_event(
        self,
        *,
        session_id: str,
        message_id: str,
        event_type: str,
        tool_call_id: str | None,
        name: str | None,
        payload: Any,
    ) -> None:
        await ToolEventDocument(
            _id=ObjectId(),
            session_id=_oid(session_id),
            message_id=_oid(message_id),
            type=ToolEventType(event_type),
            tool_call_id=tool_call_id,
            name=name,
            payload=payload,
            created_at=_utc_now(),
        ).insert()

    async def _active_path(self, leaf_id: ObjectId) -> list[MessageDocument]:
        docs: list[MessageDocument] = []
        current: ObjectId | None = leaf_id
        while current is not None:
            doc = await MessageDocument.find_one(
                MessageDocument.id == current,
                MessageDocument.status != MessageStatus.DELETED,
            )
            if not doc:
                break
            docs.append(doc)
            current = doc.parent_id
        docs.reverse()
        return docs

    async def _mark_assistant_terminal(
        self,
        *,
        assistant_message_id: str,
        status: MessageStatus,
        content: str,
        error: str | None,
    ) -> None:
        now = _utc_now()
        update: dict[str, Any] = {
            "$set": {
                "content": content,
                "status": status.value,
                "updated_at": now,
            }
        }
        if error is not None:
            update["$set"]["error"] = error

        async def _txn_callback(mongo_session):
            updated = await self.db.messages.find_one_and_update(
                {
                    "_id": _oid(assistant_message_id),
                    "role": MessageRole.ASSISTANT.value,
                    "status": MessageStatus.STREAMING.value,
                },
                update,
                return_document=ReturnDocument.AFTER,
                session=mongo_session,
            )
            if not updated:
                raise NotFoundError("Assistant message not found")
            parent_id = updated.get("parent_id")
            if parent_id is None:
                raise InvalidChatParentError("Assistant message has no user parent")
            result = await self.db.sessions.update_one(
                {"_id": updated["session_id"], "status": RecordStatus.ACTIVE.value},
                {
                    "$set": {
                        "active_leaf_id": parent_id,
                        "updated_at": now,
                    }
                },
                session=mongo_session,
            )
            if result.matched_count == 0:
                raise NotFoundError("Session not found or was deleted during terminal update")

        async with self.db.client.start_session() as mongo_session:
            await mongo_session.with_transaction(_txn_callback)
