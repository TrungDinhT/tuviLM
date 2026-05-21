from __future__ import annotations

import asyncio
import datetime as dt

import pytest
from bson import ObjectId
from dataclasses import asdict
from fastapi import HTTPException
from pydantic_ai import messages as pai_messages

from api.main import _la_so_from_birth_info, _start_turn_or_404, _to_model_history, chat_dummy
from api.schemas import ChatRequest
from api.chat.contracts import BirthInfo, ChatTurnStart, Message
from api.chat.store.mongo import InvalidChatParentError, MongoChatStore
from api.chat.store.documents import (
    ChartProfileDocument,
    MessageRole,
    MessageDocument,
    MessageStatus,
    RecordStatus,
    SessionDocument,
)
from src.refactored.la_so import LaSo


def _utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def test_laso_rebuilds_from_solar_birth_info() -> None:
    la_so = _la_so_from_birth_info(
        BirthInfo(
            calendar="solar",
            date=4,
            month=4,
            year=1998,
            hour=8,
            minute=30,
            gender="M",
        )
    )

    assert isinstance(la_so, LaSo)


def test_laso_rejects_lunar_birth_info_until_supported() -> None:
    with pytest.raises(HTTPException) as exc:
        _la_so_from_birth_info(
            BirthInfo(
                calendar="lunar",
                date=4,
                month=4,
                year=1998,
                hour=8,
                minute=30,
                gender="M",
            )
        )

    assert exc.value.status_code == 422


def test_model_history_uses_only_confirmed_messages() -> None:
    history = _to_model_history(
        [
            Message(
                id="root",
                parent_id=None,
                sender="assistant",
                body="Xin chào",
                status="confirmed",
            ),
            Message(
                id="u1",
                parent_id="root",
                sender="user",
                body="Hỏi cung Mệnh",
                status="confirmed",
            ),
            Message(
                id="a1",
                parent_id="u1",
                sender="assistant",
                body="Đang dở",
                status="failed",
            ),
        ]
    )

    assert len(history) == 1
    assert isinstance(history[0], pai_messages.ModelRequest)


def test_storage_document_models_make_required_lifecycle_fields_explicit() -> None:
    now = _utc_now()
    birth_info = BirthInfo(
        calendar="solar",
        date=4,
        month=4,
        year=1998,
        hour=8,
        minute=30,
        gender="M",
    )
    profile_id = ObjectId()
    session_id = ObjectId()
    message_id = ObjectId()

    profile_doc = ChartProfileDocument(
        _id=profile_id,
        client_id="client-1",
        display_name="Test",
        birth_metadata=asdict(birth_info),
        status=RecordStatus.ACTIVE,
        created_at=now,
        updated_at=now,
    ).to_mongo()
    session_doc = SessionDocument(
        _id=session_id,
        client_id="client-1",
        chart_profile_id=profile_id,
        active_leaf_id=message_id,
        status=RecordStatus.ACTIVE,
        created_at=now,
        updated_at=now,
    ).to_mongo()
    message_doc = MessageDocument(
        _id=message_id,
        session_id=session_id,
        parent_id=None,
        role=MessageRole.ASSISTANT,
        content="Xin chào",
        status=MessageStatus.CONFIRMED,
        created_at=now,
        updated_at=now,
    ).to_mongo()

    assert profile_doc["status"] == "active"
    assert profile_doc["updated_at"] == now
    assert session_doc["active_leaf_id"] == message_id
    assert message_doc["status"] == "confirmed"


def test_message_document_converts_to_domain_message() -> None:
    now = _utc_now()
    doc = MessageDocument(
        _id=ObjectId(),
        session_id=ObjectId(),
        parent_id=None,
        role=MessageRole.ASSISTANT,
        content="Xin chào",
        status=MessageStatus.STREAMING,
        created_at=now,
        updated_at=now,
    )

    msg = doc.to_message()

    assert msg.sender == "assistant"
    assert msg.body == "Xin chào"
    assert msg.status == "streaming"


def test_chat_request_requires_client_id() -> None:
    payload = ChatRequest(
        client_id="client-1",
        session_id=str(ObjectId()),
        parent_id=str(ObjectId()),
        content="Hỏi cung Mệnh",
    )

    assert payload.client_id == "client-1"


def test_start_turn_forwards_client_id_to_store() -> None:
    class Store:
        def __init__(self) -> None:
            self.seen: dict[str, str] | None = None

        async def start_chat_turn(
            self,
            *,
            client_id: str,
            session_id: str,
            parent_id: str,
            content: str,
        ) -> ChatTurnStart:
            self.seen = {
                "client_id": client_id,
                "session_id": session_id,
                "parent_id": parent_id,
                "content": content,
            }
            return ChatTurnStart(
                user_message_id="u1",
                assistant_message_id="a1",
                birth_info=BirthInfo(
                    calendar="solar",
                    date=4,
                    month=4,
                    year=1998,
                    hour=8,
                    minute=30,
                    gender="M",
                ),
                history=[],
            )

    store = Store()
    payload = ChatRequest(
        client_id="client-1",
        session_id="session-1",
        parent_id="parent-1",
        content="Hỏi cung Mệnh",
    )

    asyncio.run(_start_turn_or_404(store, payload))  # type: ignore[arg-type]

    assert store.seen == {
        "client_id": "client-1",
        "session_id": "session-1",
        "parent_id": "parent-1",
        "content": "Hỏi cung Mệnh",
    }


def test_start_turn_maps_stale_parent_to_conflict() -> None:
    class Store:
        async def start_chat_turn(self, **_: str) -> ChatTurnStart:
            raise InvalidChatParentError("Parent message is not the active leaf")

    payload = ChatRequest(
        client_id="client-1",
        session_id="session-1",
        parent_id="stale-parent",
        content="Hỏi tiếp",
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(_start_turn_or_404(Store(), payload))  # type: ignore[arg-type]

    assert exc.value.status_code == 409


def test_non_stream_chat_endpoint_is_deprecated() -> None:
    payload = ChatRequest(
        client_id="client-1",
        session_id="session-1",
        parent_id="parent-1",
        content="Hỏi cung Mệnh",
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(chat_dummy(payload, object()))  # type: ignore[arg-type]

    assert exc.value.status_code == 410


def test_terminal_failed_assistant_moves_session_leaf_to_user_parent() -> None:
    session_id = ObjectId()
    user_id = ObjectId()
    assistant_id = ObjectId()

    class Transaction:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class Session:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def start_transaction(self):
            return Transaction()

    class Client:
        def start_session(self):
            return Session()

    class Messages:
        async def find_one_and_update(self, query, update, *, return_document, session):
            assert query == {
                "_id": assistant_id,
                "role": "assistant",
                "status": "streaming",
            }
            assert update["$set"]["status"] == "failed"
            assert update["$set"]["content"] == "partial"
            assert update["$set"]["error"] == "boom"
            return MessageDocument(
                _id=assistant_id,
                session_id=session_id,
                parent_id=user_id,
                role=MessageRole.ASSISTANT,
                content="partial",
                status=MessageStatus.FAILED,
                created_at=_utc_now(),
                updated_at=_utc_now(),
            ).to_mongo()

    class Sessions:
        def __init__(self) -> None:
            self.update = None

        async def update_one(self, query, update, *, session):
            self.update = (query, update)

    class Db:
        def __init__(self) -> None:
            self.client = Client()
            self.messages = Messages()
            self.sessions = Sessions()

    db = Db()
    store = MongoChatStore(db)  # type: ignore[arg-type]

    asyncio.run(
        store.mark_assistant_message_failed(
            assistant_message_id=str(assistant_id),
            content="partial",
            error="boom",
        )
    )

    query, update = db.sessions.update
    assert query == {"_id": session_id, "status": "active"}
    assert update["$set"]["active_leaf_id"] == user_id
    assert isinstance(update["$set"]["updated_at"], dt.datetime)
