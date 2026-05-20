from __future__ import annotations

import datetime as dt
from dataclasses import asdict
from typing import Any

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING, ReturnDocument
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

    async def ensure_indexes(self) -> None:
        await self.db.chart_profiles.create_index(
            [("client_id", ASCENDING), ("status", ASCENDING), ("updated_at", DESCENDING)]
        )
        await self.db.sessions.create_index(
            [("client_id", ASCENDING), ("status", ASCENDING), ("updated_at", DESCENDING)]
        )
        await self.db.sessions.create_index([("chart_profile_id", ASCENDING)])
        await self.db.sessions.create_index([("active_leaf_id", ASCENDING)])
        await self.db.messages.create_index(
            [("session_id", ASCENDING), ("created_at", ASCENDING)]
        )
        await self.db.messages.create_index([("parent_id", ASCENDING)])
        await self.db.messages.create_index(
            [("session_id", ASCENDING), ("status", ASCENDING)]
        )
        await self.db.tool_events.create_index(
            [("session_id", ASCENDING), ("message_id", ASCENDING), ("created_at", ASCENDING)]
        )

    async def mark_stale_streaming_messages_failed(self) -> int:
        result = await self.db.messages.update_many(
            {"role": "assistant", "status": "streaming"},
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

        async with self.db.client.start_session() as mongo_session:
            async with await mongo_session.start_transaction():
                await self.db.chart_profiles.insert_one(
                    ChartProfileDocument(
                        _id=profile_id,
                        client_id=client_id,
                        display_name=display_name,
                        birth_metadata=asdict(birth_info),
                        status=RecordStatus.ACTIVE,
                        created_at=now,
                        updated_at=now,
                    ).to_mongo(),
                    session=mongo_session,
                )
                await self.db.messages.insert_one(
                    MessageDocument(
                        _id=root_id,
                        session_id=session_id,
                        parent_id=None,
                        role=MessageRole.ASSISTANT,
                        content=root_greeting,
                        status=MessageStatus.CONFIRMED,
                        created_at=now,
                        updated_at=now,
                    ).to_mongo(),
                    session=mongo_session,
                )
                await self.db.sessions.insert_one(
                    SessionDocument(
                        _id=session_id,
                        client_id=client_id,
                        chart_profile_id=profile_id,
                        active_leaf_id=root_id,
                        status=RecordStatus.ACTIVE,
                        created_at=now,
                        updated_at=now,
                    ).to_mongo(),
                    session=mongo_session,
                )

        return ChartSessionCreated(
            chart_profile_id=str(profile_id),
            session_id=str(session_id),
            active_leaf_id=str(root_id),
        )

    async def get_session(self, *, client_id: str, session_id: str) -> SessionRecord:
        session_oid = _oid(session_id)
        session_raw = await self.db.sessions.find_one(
            {"_id": session_oid, "client_id": client_id, "status": RecordStatus.ACTIVE.value}
        )
        if not session_raw:
            raise NotFoundError("Session not found")
        session_doc = SessionDocument.model_validate(session_raw)

        profile_raw = await self.db.chart_profiles.find_one(
            {
                "_id": session_doc.chart_profile_id,
                "client_id": client_id,
                "status": RecordStatus.ACTIVE.value,
            }
        )
        if not profile_raw:
            raise NotFoundError("Chart profile not found")
        profile_doc = ChartProfileDocument.model_validate(profile_raw)

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
        cursor = self.db.sessions.find(
            {"client_id": client_id, "status": RecordStatus.ACTIVE.value},
            sort=[("updated_at", DESCENDING)],
            limit=100,
        )
        sessions = [SessionDocument.model_validate(doc) async for doc in cursor]
        if not sessions:
            return []

        profile_ids = [doc.chart_profile_id for doc in sessions]
        profiles: dict[ObjectId, ChartProfileDocument] = {}
        async for doc in self.db.chart_profiles.find({"_id": {"$in": profile_ids}}):
            profile = ChartProfileDocument.model_validate(doc)
            profiles[profile.id] = profile

        leaf_ids = [doc.active_leaf_id for doc in sessions]
        leaves: dict[ObjectId, MessageDocument] = {}
        async for doc in self.db.messages.find({"_id": {"$in": leaf_ids}}):
            leaf = MessageDocument.model_validate(doc)
            leaves[leaf.id] = leaf

        summaries: list[SessionInfo] = []
        for doc in sessions:
            profile = profiles.get(doc.chart_profile_id)
            leaf = leaves.get(doc.active_leaf_id)
            summaries.append(
                SessionInfo(
                    session_id=str(doc.id),
                    chart_profile_id=str(doc.chart_profile_id),
                    active_leaf_id=_sid(doc.active_leaf_id),
                    display_name=profile.display_name if profile else "Giấu tên",
                    birth_year=profile.birth_metadata.get("year") if profile else None,
                    last_message_preview=(leaf.content if leaf else "")[:120],
                    message_count=await self.db.messages.count_documents(
                        {"session_id": doc.id, "status": {"$ne": MessageStatus.DELETED.value}}
                    ),
                    updated_at=doc.updated_at,
                )
            )
        return summaries

    async def soft_delete_session(self, *, client_id: str, session_id: str) -> None:
        session_oid = _oid(session_id)
        now = _utc_now()
        async with self.db.client.start_session() as mongo_session:
            async with await mongo_session.start_transaction():
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

        async with self.db.client.start_session() as mongo_session:
            async with await mongo_session.start_transaction():
                session_raw = await self.db.sessions.find_one(
                    {
                        "_id": session_oid,
                        "client_id": client_id,
                        "status": RecordStatus.ACTIVE.value,
                    },
                    session=mongo_session,
                )
                if not session_raw:
                    raise NotFoundError("Session not found")
                session_doc = SessionDocument.model_validate(session_raw)
                if session_doc.active_leaf_id != parent_oid:
                    raise InvalidChatParentError("Parent message is not the active leaf")

                parent_raw = await self.db.messages.find_one(
                    {
                        "_id": parent_oid,
                        "session_id": session_oid,
                        "status": MessageStatus.CONFIRMED.value,
                    },
                    session=mongo_session,
                )
                if not parent_raw:
                    raise InvalidChatParentError("Parent message is not confirmed")

                profile_raw = await self.db.chart_profiles.find_one(
                    {
                        "_id": session_doc.chart_profile_id,
                        "client_id": session_doc.client_id,
                        "status": RecordStatus.ACTIVE.value,
                    },
                    session=mongo_session,
                )
                if not profile_raw:
                    raise NotFoundError("Chart profile not found")
                profile_doc = ChartProfileDocument.model_validate(profile_raw)

                await self.db.messages.insert_one(
                    MessageDocument(
                        _id=user_id,
                        session_id=session_oid,
                        parent_id=parent_oid,
                        role=MessageRole.USER,
                        content=content,
                        status=MessageStatus.CONFIRMED,
                        created_at=now,
                        updated_at=now,
                    ).to_mongo(),
                    session=mongo_session,
                )
                await self.db.messages.insert_one(
                    MessageDocument(
                        _id=assistant_id,
                        session_id=session_oid,
                        parent_id=user_id,
                        role=MessageRole.ASSISTANT,
                        content="",
                        status=MessageStatus.STREAMING,
                        created_at=now,
                        updated_at=now,
                    ).to_mongo(),
                    session=mongo_session,
                )

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
        async with self.db.client.start_session() as mongo_session:
            async with await mongo_session.start_transaction():
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
                await self.db.sessions.update_one(
                    {"_id": session_oid, "status": RecordStatus.ACTIVE.value},
                    {
                        "$set": {
                            "active_leaf_id": assistant_oid,
                            "updated_at": now,
                        }
                    },
                    session=mongo_session,
                )

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
        await self.db.tool_events.insert_one(
            ToolEventDocument(
                _id=ObjectId(),
                session_id=_oid(session_id),
                message_id=_oid(message_id),
                type=ToolEventType(event_type),
                tool_call_id=tool_call_id,
                name=name,
                payload=payload,
                created_at=_utc_now(),
            ).to_mongo()
        )

    async def _active_path(self, leaf_id: ObjectId) -> list[MessageDocument]:
        docs: list[MessageDocument] = []
        current: ObjectId | None = leaf_id
        while current is not None:
            doc = await self.db.messages.find_one(
                {"_id": current, "status": {"$ne": MessageStatus.DELETED.value}}
            )
            if not doc:
                break
            message_doc = MessageDocument.model_validate(doc)
            docs.append(message_doc)
            current = message_doc.parent_id
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
        async with self.db.client.start_session() as mongo_session:
            async with await mongo_session.start_transaction():
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
                message_doc = MessageDocument.model_validate(updated)
                if message_doc.parent_id is None:
                    raise InvalidChatParentError("Assistant message has no user parent")
                await self.db.sessions.update_one(
                    {"_id": message_doc.session_id, "status": RecordStatus.ACTIVE.value},
                    {
                        "$set": {
                            "active_leaf_id": message_doc.parent_id,
                            "updated_at": now,
                        }
                    },
                    session=mongo_session,
                )
