from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import httpx
import pytest
from beanie import PydanticObjectId
from pymongo import AsyncMongoClient
from pymongo.errors import ServerSelectionTimeoutError
from pydantic_ai import PartStartEvent, TextPart

from api.chat.contracts import (
    ConversationHistoryStore,
    DuplicateStreamInProgressError,
    IdempotencyConflictError,
    MissingOwnerIdError,
    NotFoundError,
)
from api.chat.models import (
    BirthInfo,
    ChartProfile,
    ChatMessageStatus,
    ChatMessage,
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
)
from api.chat.storage.mappers import chart_profile_from_document
from api.chat.storage.store import MongoConversationHistoryStore
from api.main import ApiState, app
from src.agent.deps import TuviAgentDeps


pytestmark = pytest.mark.anyio

MONGODB_URI = os.environ.get(
    "CONVERSATION_HISTORY_STORE__URI",
    "mongodb://localhost:27017",
)
MONGODB_TEST_DB = os.environ.get(
    "CONVERSATION_HISTORY_STORE_TEST_DATABASE_NAME",
    "tuvilm_test",
)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture()
async def api_client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        yield client


@pytest.fixture()
async def mongo_store():
    client = AsyncMongoClient(MONGODB_URI, serverSelectionTimeoutMS=300, tz_aware=True)
    try:
        await client.admin.command("ping")
    except ServerSelectionTimeoutError as exc:
        await client.close()
        pytest.skip(f"MongoDB is not available at {MONGODB_URI}: {exc}")

    database = client[MONGODB_TEST_DB]
    await database.drop_collection(ChartProfileDocument.Settings.name)
    await database.drop_collection(ChatSessionDocument.Settings.name)
    store = MongoConversationHistoryStore(
        mongo_client=client,
        database_name=MONGODB_TEST_DB,
    )
    await store._initialize_storage()

    previous_api_state = getattr(app.state, "api_state", None)
    app.state.api_state = ApiState(
        agent_deps=getattr(previous_api_state, "agent_deps", TuviAgentDeps(book_root="")),
        conversation_history_store=store,
    )
    try:
        yield store
    finally:
        if previous_api_state is not None:
            app.state.api_state = previous_api_state
        elif hasattr(app.state, "api_state"):
            del app.state.api_state
        if hasattr(app.state, "session_chat_streamer"):
            del app.state.session_chat_streamer
        await database.drop_collection(ChartProfileDocument.Settings.name)
        await database.drop_collection(ChatSessionDocument.Settings.name)
        await store.close()


@pytest.fixture()
async def fake_store():
    store = FakeConversationHistoryStore()
    previous_api_state = getattr(app.state, "api_state", None)
    app.state.api_state = ApiState(
        agent_deps=getattr(previous_api_state, "agent_deps", TuviAgentDeps(book_root="")),
        conversation_history_store=store,
    )
    try:
        yield store
    finally:
        if previous_api_state is not None:
            app.state.api_state = previous_api_state
        elif hasattr(app.state, "api_state"):
            del app.state.api_state
        if hasattr(app.state, "session_chat_streamer"):
            del app.state.session_chat_streamer


async def test_build_laso_accepts_birth_info_day_field(api_client) -> None:
    app.state.api_state = ApiState(
        agent_deps=TuviAgentDeps(book_root=""),
        conversation_history_store=FakeConversationHistoryStore(),
    )

    response = await api_client.post(
        "/api/v1/laso/build",
        json={
            "calendar": "solar",
            "year": 1996,
            "month": 4,
            "day": 15,
            "hour": 10,
            "gender": "M",
        },
    )

    assert response.status_code == 200
    assert response.json()["summary"] == "Sinh dương lịch: 15/04/1996 10:00"


async def test_create_anonymous_owner_returns_owner_id(api_client) -> None:
    response = await api_client.post("/api/v1/anonymous")

    assert response.status_code == 200
    assert response.json()["owner_id"].startswith("anon_")


async def test_chart_profile_endpoints_use_store(api_client, fake_store) -> None:
    await fake_store.create_chart_profile(
        "other_owner",
        CreateChartProfileInput(
            display_name="Other",
            birth_info=BirthInfo(year=1997, month=5, day=16, hour=11, gender="F"),
        ),
        idempotency_key="other",
    )

    create_response = await api_client.post(
        "/api/v1/chart-profiles",
        headers={
            "X-Anonymous-Owner-Id": "anon_owner",
            "Idempotency-Key": "create-profile-1",
        },
        json={
            "display_name": "Me",
            "birth_info": {
                "calendar": "solar",
                "year": 1996,
                "month": 4,
                "day": 15,
                "hour": 10,
                "gender": "M",
            },
        },
    )
    list_response = await api_client.get(
        "/api/v1/chart-profiles",
        headers={"X-Anonymous-Owner-Id": "anon_owner"},
    )

    assert create_response.status_code == 200
    assert create_response.json()["chart_profile"]["display_name"] == "Me"
    assert [profile["display_name"] for profile in list_response.json()["chart_profiles"]] == [
        "Me"
    ]


async def test_create_chart_profile_rejects_blank_owner_id(
    api_client,
    fake_store,
) -> None:
    response = await api_client.post(
        "/api/v1/chart-profiles",
        headers={
            "X-Anonymous-Owner-Id": "",
            "Idempotency-Key": "create-profile-1",
        },
        json={
            "display_name": "Me",
            "birth_info": {
                "calendar": "solar",
                "year": 1996,
                "month": 4,
                "day": 15,
                "hour": 10,
                "gender": "M",
            },
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Anonymous owner id is required."


async def test_mutating_routes_reject_blank_idempotency_key(
    api_client,
    fake_store,
) -> None:
    profile = await _create_profile(fake_store)
    session = await _create_session(fake_store, profile.id)
    headers = {
        "X-Anonymous-Owner-Id": "anon_owner",
        "Idempotency-Key": "",
    }

    profile_response = await api_client.post(
        "/api/v1/chart-profiles",
        headers=headers,
        json={
            "display_name": "Me",
            "birth_info": {
                "calendar": "solar",
                "year": 1996,
                "month": 4,
                "day": 15,
                "hour": 10,
                "gender": "M",
            },
        },
    )
    session_response = await api_client.post(
        f"/api/v1/chart-profiles/{profile.id}/sessions",
        headers=headers,
        json={"title": "Career"},
    )
    stream_response = await api_client.post(
        f"/api/v1/sessions/{session.id}/chat/stream",
        headers=headers,
        json={"content": "Tell me about career."},
    )

    assert profile_response.status_code == 422
    assert session_response.status_code == 422
    assert stream_response.status_code == 422


async def test_session_endpoints_use_store(api_client, fake_store) -> None:
    profile = await _create_profile(fake_store)

    create_response = await api_client.post(
        f"/api/v1/chart-profiles/{profile.id}/sessions",
        headers={
            "X-Anonymous-Owner-Id": "anon_owner",
            "Idempotency-Key": "create-session-1",
        },
        json={"title": "Career"},
    )
    session = create_response.json()["session"]
    list_response = await api_client.get(
        f"/api/v1/chart-profiles/{profile.id}/sessions",
        headers={"X-Anonymous-Owner-Id": "anon_owner"},
    )
    get_response = await api_client.get(
        f"/api/v1/sessions/{session['id']}",
        headers={"X-Anonymous-Owner-Id": "anon_owner"},
    )

    assert create_response.status_code == 200
    assert session["chart_profile_id"] == profile.id
    assert session["messages"] == []
    assert list_response.json()["sessions"][0]["message_count"] == 0
    assert get_response.json()["session"]["id"] == session["id"]


async def test_delete_session_route_returns_no_content(
    api_client,
    fake_store,
) -> None:
    profile = await _create_profile(fake_store)
    session = await _create_session(fake_store, profile.id)

    delete_response = await api_client.delete(
        f"/api/v1/sessions/{session.id}",
        headers={"X-Anonymous-Owner-Id": "anon_owner"},
    )

    assert delete_response.status_code == 204
    assert fake_store.deleted_session_ids == [session.id]


async def test_delete_chart_profile_route_returns_no_content(
    api_client,
    fake_store,
) -> None:
    profile = await _create_profile(fake_store)

    delete_response = await api_client.delete(
        f"/api/v1/chart-profiles/{profile.id}",
        headers={"X-Anonymous-Owner-Id": "anon_owner"},
    )

    assert delete_response.status_code == 204
    assert fake_store.deleted_chart_profile_ids == [profile.id]


async def test_create_chart_profile_requires_owner_id(mongo_store) -> None:
    with pytest.raises(MissingOwnerIdError):
        await mongo_store.create_chart_profile(
            None,
            CreateChartProfileInput(
                display_name="Me",
                birth_info=BirthInfo(year=1996, month=4, day=15, hour=10, gender="M"),
            ),
            idempotency_key="create-profile-1",
        )


async def test_create_chart_profile_is_idempotent_for_same_key(mongo_store) -> None:
    payload = CreateChartProfileInput(
        display_name="Me",
        birth_info=BirthInfo(year=1996, month=4, day=15, hour=10, gender="M"),
    )

    first = await mongo_store.create_chart_profile(
        "anon_owner",
        payload,
        idempotency_key="create-profile-1",
    )
    second = await mongo_store.create_chart_profile(
        "anon_owner",
        payload,
        idempotency_key="create-profile-1",
    )

    assert second == first


async def test_create_chart_profile_rejects_same_key_with_different_payload(
    mongo_store,
) -> None:
    await _create_profile(mongo_store, idempotency_key="create-profile-1")

    with pytest.raises(IdempotencyConflictError):
        await mongo_store.create_chart_profile(
            "anon_owner",
            CreateChartProfileInput(
                display_name="Someone else",
                birth_info=BirthInfo(year=1997, month=5, day=16, hour=11, gender="F"),
            ),
            idempotency_key="create-profile-1",
        )


async def test_reserve_message_pair_and_finalize_assistant_message(mongo_store) -> None:
    profile = await _create_profile(mongo_store)
    session = await _create_session(mongo_store, profile.id)

    pair = await mongo_store.reserve_message_pair(
        "anon_owner",
        session.id,
        user_content="Tell me about career.",
        idempotency_key="message-1",
    )
    assistant = await mongo_store.finalize_assistant_message(
        "anon_owner",
        session.id,
        pair.assistant_message.id,
        content="Career looks strong.",
        status=ChatMessageStatus.CONFIRMED,
    )
    context = await mongo_store.load_session_context("anon_owner", session.id)

    assert pair.user_message.status == ChatMessageStatus.CONFIRMED
    assert pair.assistant_message.status == ChatMessageStatus.PENDING
    assert assistant.content == "Career looks strong."
    assert assistant.status == ChatMessageStatus.CONFIRMED
    assert [message.role for message in context.session.messages] == [
        ChatRole.USER,
        ChatRole.ASSISTANT,
    ]
    assert context.session.messages[-1].content == "Career looks strong."


async def test_finalize_assistant_message_does_not_overwrite_terminal_message(
    mongo_store,
) -> None:
    profile = await _create_profile(mongo_store)
    session = await _create_session(mongo_store, profile.id)
    pair = await mongo_store.reserve_message_pair(
        "anon_owner",
        session.id,
        user_content="Tell me about career.",
        idempotency_key="message-1",
    )

    first = await mongo_store.finalize_assistant_message(
        "anon_owner",
        session.id,
        pair.assistant_message.id,
        content="Career looks strong.",
        status=ChatMessageStatus.CONFIRMED,
    )
    second = await mongo_store.finalize_assistant_message(
        "anon_owner",
        session.id,
        pair.assistant_message.id,
        content="Partial answer before failure.",
        status=ChatMessageStatus.FAILED,
    )
    context = await mongo_store.load_session_context("anon_owner", session.id)
    document = await ChatSessionDocument.find_one(
        ChatSessionDocument.id == PydanticObjectId(session.id)
    )

    assert first.content == "Career looks strong."
    assert second.content == "Career looks strong."
    assert second.status == ChatMessageStatus.CONFIRMED
    assert context.session.messages[-1].content == "Career looks strong."
    assert context.session.messages[-1].status == ChatMessageStatus.CONFIRMED
    assert document is not None
    assert document.message_operations[-1].status == MessageOperationStatus.COMPLETED


async def test_reserve_message_pair_rejects_second_pending_stream(mongo_store) -> None:
    profile = await _create_profile(mongo_store)
    session = await _create_session(mongo_store, profile.id)

    await mongo_store.reserve_message_pair(
        "anon_owner",
        session.id,
        user_content="Tell me about career.",
        idempotency_key="message-1",
    )

    with pytest.raises(DuplicateStreamInProgressError):
        await mongo_store.reserve_message_pair(
            "anon_owner",
            session.id,
            user_content="Tell me about love.",
            idempotency_key="message-2",
        )


async def test_stale_pending_message_is_failed_and_allows_new_reservation(
    mongo_store,
) -> None:
    profile = await _create_profile(mongo_store)
    session = await _create_session(mongo_store, profile.id)
    pair = await mongo_store.reserve_message_pair(
        "anon_owner",
        session.id,
        user_content="Tell me about career.",
        idempotency_key="message-1",
    )
    document = await ChatSessionDocument.find_one(
        ChatSessionDocument.id == PydanticObjectId(session.id)
    )
    assert document is not None
    stale_time = datetime.now(UTC) - timedelta(minutes=16)
    document.messages[-1].updated_at = stale_time
    document.message_operations[-1].updated_at = stale_time
    await document.save()

    cleaned_context = await mongo_store.load_session_context("anon_owner", session.id)
    new_pair = await mongo_store.reserve_message_pair(
        "anon_owner",
        session.id,
        user_content="Tell me about love.",
        idempotency_key="message-2",
    )
    final_context = await mongo_store.load_session_context("anon_owner", session.id)
    updated_document = await ChatSessionDocument.find_one(
        ChatSessionDocument.id == PydanticObjectId(session.id)
    )

    assert cleaned_context.session.messages[-1].id == pair.assistant_message.id
    assert cleaned_context.session.messages[-1].status == ChatMessageStatus.FAILED
    assert new_pair.assistant_message.status == ChatMessageStatus.PENDING
    assert len(final_context.session.messages) == 4
    assert final_context.session.messages[-1].id == new_pair.assistant_message.id
    assert final_context.session.messages[-1].status == ChatMessageStatus.PENDING
    assert updated_document is not None
    assert updated_document.message_operations[0].status == MessageOperationStatus.FAILED
    assert updated_document.message_operations[1].status == MessageOperationStatus.IN_PROGRESS


async def test_stale_pending_message_is_cleaned_before_reservation(
    mongo_store,
) -> None:
    profile = await _create_profile(mongo_store)
    session = await _create_session(mongo_store, profile.id)
    old_pair = await mongo_store.reserve_message_pair(
        "anon_owner",
        session.id,
        user_content="Tell me about career.",
        idempotency_key="message-1",
    )
    document = await ChatSessionDocument.find_one(
        ChatSessionDocument.id == PydanticObjectId(session.id)
    )
    assert document is not None
    stale_time = datetime.now(UTC) - timedelta(minutes=16)
    document.messages[-1].updated_at = stale_time
    document.message_operations[-1].updated_at = stale_time
    await document.save()

    new_pair = await mongo_store.reserve_message_pair(
        "anon_owner",
        session.id,
        user_content="Tell me about love.",
        idempotency_key="message-2",
    )
    context = await mongo_store.load_session_context("anon_owner", session.id)

    assert context.session.messages[1].id == old_pair.assistant_message.id
    assert context.session.messages[1].status == ChatMessageStatus.FAILED
    assert context.session.messages[-1].id == new_pair.assistant_message.id
    assert context.session.messages[-1].status == ChatMessageStatus.PENDING


async def test_reserve_message_pair_concurrent_same_key_replays_one_pair(
    mongo_store,
) -> None:
    profile = await _create_profile(mongo_store)
    session = await _create_session(mongo_store, profile.id)

    first, second = await asyncio.gather(
        mongo_store.reserve_message_pair(
            "anon_owner",
            session.id,
            user_content="Tell me about career.",
            idempotency_key="message-1",
        ),
        mongo_store.reserve_message_pair(
            "anon_owner",
            session.id,
            user_content="Tell me about career.",
            idempotency_key="message-1",
        ),
    )
    context = await mongo_store.load_session_context("anon_owner", session.id)

    assert first.user_message.id == second.user_message.id
    assert first.assistant_message.id == second.assistant_message.id
    assert len(context.session.messages) == 2


async def test_reserve_message_pair_concurrent_different_keys_allows_one_stream(
    mongo_store,
) -> None:
    profile = await _create_profile(mongo_store)
    session = await _create_session(mongo_store, profile.id)

    results = await asyncio.gather(
        mongo_store.reserve_message_pair(
            "anon_owner",
            session.id,
            user_content="Tell me about career.",
            idempotency_key="message-1",
        ),
        mongo_store.reserve_message_pair(
            "anon_owner",
            session.id,
            user_content="Tell me about love.",
            idempotency_key="message-2",
        ),
        return_exceptions=True,
    )
    context = await mongo_store.load_session_context("anon_owner", session.id)

    assert sum(isinstance(result, ReservedMessagePair) for result in results) == 1
    assert sum(isinstance(result, DuplicateStreamInProgressError) for result in results) == 1
    assert len(context.session.messages) == 2
    assert context.session.messages[-1].status == ChatMessageStatus.PENDING


async def test_mongo_delete_session_hides_it_from_session_list(mongo_store) -> None:
    profile = await _create_profile(mongo_store)
    session = await _create_session(mongo_store, profile.id)

    await mongo_store.delete_session("anon_owner", session.id)

    assert await mongo_store.list_sessions("anon_owner", profile.id) == []


async def test_mongo_delete_chart_profile_hides_profile_and_child_session(
    mongo_store,
) -> None:
    profile = await _create_profile(mongo_store)
    session = await _create_session(mongo_store, profile.id)

    await mongo_store.delete_chart_profile("anon_owner", profile.id)

    assert await mongo_store.list_chart_profiles("anon_owner") == []
    with pytest.raises(NotFoundError):
        await mongo_store.load_session_context("anon_owner", session.id)


async def test_session_chat_stream_persists_confirmed_assistant_message(
    api_client,
    fake_store,
) -> None:
    async def fake_streamer(*args, **kwargs):
        yield {"type": "text", "delta": "Career "}
        yield {"type": "text", "delta": "looks strong."}

    app.state.session_chat_streamer = fake_streamer
    profile = await _create_profile(fake_store)
    session = await _create_session(fake_store, profile.id)

    response = await api_client.post(
        f"/api/v1/sessions/{session.id}/chat/stream",
        headers={
            "X-Anonymous-Owner-Id": "anon_owner",
            "Idempotency-Key": "message-1",
        },
        json={"content": "Tell me about career."},
    )
    context = await fake_store.load_session_context("anon_owner", session.id)

    assert response.status_code == 200
    assert '"type": "ids"' in response.text
    assert '"type": "done", "status": "confirmed"' in response.text
    assert context.session.messages[-1].content == "Career looks strong."
    assert context.session.messages[-1].status == ChatMessageStatus.CONFIRMED


async def test_session_chat_stream_cancellation_marks_assistant_cancelled(
    api_client,
    fake_store,
) -> None:
    async def cancelled_streamer(*args, **kwargs):
        yield {"type": "text", "delta": "Partial answer."}
        raise asyncio.CancelledError

    app.state.session_chat_streamer = cancelled_streamer
    profile = await _create_profile(fake_store)
    session = await _create_session(fake_store, profile.id)

    with pytest.raises((asyncio.CancelledError, AssertionError)):
        await api_client.post(
            f"/api/v1/sessions/{session.id}/chat/stream",
            headers={
                "X-Anonymous-Owner-Id": "anon_owner",
                "Idempotency-Key": "message-1",
            },
            json={"content": "Tell me about career."},
        )
    context = await fake_store.load_session_context("anon_owner", session.id)

    assert context.session.messages[-1].content == "Partial answer."
    assert context.session.messages[-1].status == ChatMessageStatus.CANCELLED


async def test_session_chat_stream_default_runner_reconstructs_agent_context(
    api_client,
    fake_store,
) -> None:
    if hasattr(app.state, "session_chat_streamer"):
        del app.state.session_chat_streamer

    class FakeStream:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def __aiter__(self):
            yield PartStartEvent(index=0, part=TextPart(content="New answer."))

    class FakeAgent:
        def run_stream_events(self, user_prompt, *, deps, message_history=None, **kwargs):
            self.user_prompt = user_prompt
            self.deps = deps
            self.message_history = message_history
            return FakeStream()

    fake_agent = FakeAgent()
    app.state.api_state = ApiState(
        agent_deps=TuviAgentDeps(agent=fake_agent, book_root=""),
        conversation_history_store=fake_store,
    )
    profile = await _create_profile(fake_store)
    session = fake_store.add_session(
        profile.id,
        messages=[
            _chat_message(
                role=ChatRole.USER,
                content="Previous question.",
                status=ChatMessageStatus.CONFIRMED,
            ),
            _chat_message(
                role=ChatRole.ASSISTANT,
                content="Previous answer.",
                status=ChatMessageStatus.CONFIRMED,
            ),
        ],
    )

    response = await api_client.post(
        f"/api/v1/sessions/{session.id}/chat/stream",
        headers={
            "X-Anonymous-Owner-Id": "anon_owner",
            "Idempotency-Key": "message-1",
        },
        json={"content": "New question."},
    )

    assert response.status_code == 200
    assert fake_agent.user_prompt == "New question."
    assert fake_agent.deps.la_so is not None
    assert len(fake_agent.message_history) == 2
    assert '"type": "text", "delta": "New answer."' in response.text


async def test_session_chat_stream_duplicate_pending_request_does_not_start_generation(
    api_client,
    fake_store,
) -> None:
    async def fail_if_called(*args, **kwargs):
        raise AssertionError("duplicate pending stream should not start generation")
        yield {}

    app.state.session_chat_streamer = fail_if_called
    profile = await _create_profile(fake_store)
    session = await _create_session(fake_store, profile.id)
    pair = _reserved_pair(
        user_content="Tell me about career.",
        replayed=True,
        operation_status=MessageOperationStatus.IN_PROGRESS,
    )
    fake_store.reserve_result = pair

    response = await api_client.post(
        f"/api/v1/sessions/{session.id}/chat/stream",
        headers={
            "X-Anonymous-Owner-Id": "anon_owner",
            "Idempotency-Key": "message-1",
        },
        json={"content": "Tell me about career."},
    )

    assert response.status_code == 200
    assert '"type": "duplicate_in_progress"' in response.text
    assert pair.assistant_message.id in response.text
    assert '"type": "done", "status": "duplicate_in_progress"' in response.text


async def test_session_chat_stream_completed_replay_does_not_start_generation(
    api_client,
    fake_store,
) -> None:
    async def fail_if_called(*args, **kwargs):
        raise AssertionError("completed replay should not start generation")
        yield {}

    app.state.session_chat_streamer = fail_if_called
    profile = await _create_profile(fake_store)
    session = await _create_session(fake_store, profile.id)
    pair = _reserved_pair(
        user_content="Tell me about career.",
        replayed=True,
        operation_status=MessageOperationStatus.COMPLETED,
    )
    pair.assistant_message.content = "Career looks strong."
    pair.assistant_message.status = ChatMessageStatus.CONFIRMED
    fake_store.reserve_result = pair

    response = await api_client.post(
        f"/api/v1/sessions/{session.id}/chat/stream",
        headers={
            "X-Anonymous-Owner-Id": "anon_owner",
            "Idempotency-Key": "message-1",
        },
        json={"content": "Tell me about career."},
    )

    assert response.status_code == 200
    assert '"type": "ids"' in response.text
    assert '"type": "text", "delta": "Career looks strong."' in response.text
    assert '"type": "done", "status": "confirmed"' in response.text


async def test_create_chart_profile_endpoint_returns_conflict_for_idempotency_mismatch(
    api_client,
    fake_store,
) -> None:
    fake_store.create_chart_profile_errors = [None, IdempotencyConflictError()]
    headers = {
        "X-Anonymous-Owner-Id": "anon_owner",
        "Idempotency-Key": "create-profile-1",
    }

    first_response = await api_client.post(
        "/api/v1/chart-profiles",
        headers=headers,
        json={
            "display_name": "Me",
            "birth_info": {
                "calendar": "solar",
                "year": 1996,
                "month": 4,
                "day": 15,
                "hour": 10,
                "gender": "M",
            },
        },
    )
    second_response = await api_client.post(
        "/api/v1/chart-profiles",
        headers=headers,
        json={
            "display_name": "Someone else",
            "birth_info": {
                "calendar": "solar",
                "year": 1997,
                "month": 5,
                "day": 16,
                "hour": 11,
                "gender": "F",
            },
        },
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409


async def test_chart_profile_document_maps_to_domain_dto() -> None:
    profile = ChartProfileDocument.model_construct(
        id="profile_id",
        owner_id="anon_owner",
        display_name="Me",
        birth_info=BirthInfo(
            calendar="solar",
            year=1996,
            month=4,
            day=15,
            hour=10,
            gender="M",
        ),
        creation_idempotency_key="create-profile-1",
        creation_request_fingerprint="fingerprint",
    )

    dto = chart_profile_from_document(profile)

    assert dto.id
    assert dto.owner_id == "anon_owner"
    assert dto.birth_info.day == 15


class FakeConversationHistoryStore:
    def __init__(self) -> None:
        self.profiles: dict[str, ChartProfile] = {}
        self.sessions: dict[str, ChatSession] = {}
        self.create_chart_profile_errors: list[Exception | None] = []
        self.reserve_result: ReservedMessagePair | None = None
        self.deleted_chart_profile_ids: list[str] = []
        self.deleted_session_ids: list[str] = []

    def add_profile(
        self,
        *,
        owner_id: str = "anon_owner",
        display_name: str = "Me",
        birth_info: BirthInfo | None = None,
    ) -> ChartProfile:
        now = _now()
        profile = ChartProfile(
            id=str(uuid4()),
            owner_id=owner_id,
            display_name=display_name,
            birth_info=birth_info
            or BirthInfo(year=1996, month=4, day=15, hour=10, gender="M"),
            created_at=now,
            updated_at=now,
        )
        self.profiles[profile.id] = profile
        return profile

    def add_session(
        self,
        chart_profile_id: str,
        *,
        title: str | None = "Career",
        messages: list[ChatMessage] | None = None,
    ) -> ChatSession:
        now = _now()
        session = ChatSession(
            id=str(uuid4()),
            chart_profile_id=chart_profile_id,
            title=title,
            messages=list(messages or []),
            created_at=now,
            updated_at=now,
        )
        self.sessions[session.id] = session
        return session

    async def create_chart_profile(
        self,
        owner_id: str | None,
        payload: CreateChartProfileInput,
        *,
        idempotency_key: str,
    ) -> ChartProfile:
        if not owner_id:
            raise MissingOwnerIdError

        if self.create_chart_profile_errors:
            error = self.create_chart_profile_errors.pop(0)
            if error is not None:
                raise error

        return self.add_profile(
            owner_id=owner_id,
            display_name=payload.display_name,
            birth_info=payload.birth_info,
        )

    async def list_chart_profiles(self, owner_id: str) -> list[ChartProfile]:
        return [
            profile for profile in self.profiles.values() if profile.owner_id == owner_id
        ]

    async def delete_chart_profile(self, owner_id: str, chart_profile_id: str) -> None:
        profile = self.profiles.get(chart_profile_id)
        if profile is None or profile.owner_id != owner_id:
            raise NotFoundError
        self.deleted_chart_profile_ids.append(chart_profile_id)
        del self.profiles[chart_profile_id]

    async def create_session(
        self,
        owner_id: str,
        chart_profile_id: str,
        payload: CreateSessionInput,
        *,
        idempotency_key: str,
    ) -> ChatSession:
        await self._require_profile(owner_id, chart_profile_id)
        return self.add_session(chart_profile_id, title=payload.title)

    async def list_sessions(
        self, owner_id: str, chart_profile_id: str
    ) -> list[ChatSessionSummary]:
        await self._require_profile(owner_id, chart_profile_id)
        return [
            ChatSessionSummary(
                id=session.id,
                chart_profile_id=session.chart_profile_id,
                title=session.title,
                message_count=len(session.messages),
                created_at=session.created_at,
                updated_at=session.updated_at,
            )
            for session in self.sessions.values()
            if session.chart_profile_id == chart_profile_id
        ]

    async def load_session_context(self, owner_id: str, session_id: str) -> SessionContext:
        session = self._get_session(session_id)
        profile = await self._require_profile(owner_id, session.chart_profile_id)
        return SessionContext(chart_profile=profile, session=session)

    async def delete_session(self, owner_id: str, session_id: str) -> None:
        session = self._get_session(session_id)
        await self._require_profile(owner_id, session.chart_profile_id)
        self.deleted_session_ids.append(session_id)
        del self.sessions[session_id]

    async def reserve_message_pair(
        self,
        owner_id: str,
        session_id: str,
        *,
        user_content: str,
        idempotency_key: str,
    ) -> ReservedMessagePair:
        if self.reserve_result is not None:
            return self.reserve_result

        session = self._get_session(session_id)
        await self._require_profile(owner_id, session.chart_profile_id)

        user_message = ChatMessage(
            id=str(uuid4()),
            role=ChatRole.USER,
            content=user_content,
            status=ChatMessageStatus.CONFIRMED,
            created_at=_now(),
            updated_at=_now(),
        )
        assistant_message = ChatMessage(
            id=str(uuid4()),
            role=ChatRole.ASSISTANT,
            content="",
            status=ChatMessageStatus.PENDING,
            created_at=_now(),
            updated_at=_now(),
        )
        session.messages.extend([user_message, assistant_message])
        session.updated_at = _now()
        return ReservedMessagePair(
            user_message=user_message,
            assistant_message=assistant_message,
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
        session = self._get_session(session_id)
        await self._require_profile(owner_id, session.chart_profile_id)

        for message in session.messages:
            if message.id != assistant_message_id or message.role != ChatRole.ASSISTANT:
                continue
            now = _now()
            message.content = content
            message.status = status
            message.updated_at = now
            session.updated_at = now
            return message

        raise NotFoundError

    async def _require_profile(
        self, owner_id: str, chart_profile_id: str
    ) -> ChartProfile:
        profile = self.profiles.get(chart_profile_id)
        if profile is None or profile.owner_id != owner_id:
            raise NotFoundError
        return profile

    def _get_session(self, session_id: str) -> ChatSession:
        session = self.sessions.get(session_id)
        if session is None:
            raise NotFoundError
        return session


def _now() -> datetime:
    return datetime.now(UTC)


def _chat_message(
    *,
    role: ChatRole,
    content: str,
    status: ChatMessageStatus,
) -> ChatMessage:
    now = _now()
    return ChatMessage(
        id=str(uuid4()),
        role=role,
        content=content,
        status=status,
        created_at=now,
        updated_at=now,
    )


def _reserved_pair(
    *,
    user_content: str,
    replayed: bool = False,
    operation_status: MessageOperationStatus = MessageOperationStatus.IN_PROGRESS,
) -> ReservedMessagePair:
    return ReservedMessagePair(
        user_message=_chat_message(
            role=ChatRole.USER,
            content=user_content,
            status=ChatMessageStatus.CONFIRMED,
        ),
        assistant_message=_chat_message(
            role=ChatRole.ASSISTANT,
            content="",
            status=ChatMessageStatus.PENDING,
        ),
        operation_status=operation_status,
        replayed=replayed,
    )


async def _create_profile(
    store: ConversationHistoryStore,
    *,
    idempotency_key: str = "profile",
):
    return await store.create_chart_profile(
        "anon_owner",
        CreateChartProfileInput(
            display_name="Me",
            birth_info=BirthInfo(year=1996, month=4, day=15, hour=10, gender="M"),
        ),
        idempotency_key=idempotency_key,
    )


async def _create_session(store: ConversationHistoryStore, profile_id: str):
    return await store.create_session(
        "anon_owner",
        profile_id,
        payload=CreateSessionInput(title="Career"),
        idempotency_key="session",
    )
