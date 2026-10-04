from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import httpx
import pytest
from bson import ObjectId
from fastapi import HTTPException, Request
from pymongo import AsyncMongoClient
from pymongo.errors import ServerSelectionTimeoutError

from api.accounts.billing import (
    CHAT_MESSAGE_COST,
    reconcile_chat_coins,
    reserve_chat_coins,
)
from api.auth.dependencies import Principal, require_user
from api.chat.models import (
    BirthInfo,
    ChatMessageStatus,
    CreateChartProfileInput,
    CreateSessionInput,
)
from api.chat.storage.store import MongoConversationHistoryStore
from api.chat.routes import session_chat_stream
from api.main import ApiState, app
from api.schemas import SessionChatStreamRequest
from src.agent.deps import TuviAgentDeps


pytestmark = pytest.mark.anyio


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture()
async def billing_context(monkeypatch):
    uri = os.environ.get("CONVERSATION_HISTORY_STORE__URI", "mongodb://localhost:27017")
    mongo = AsyncMongoClient(uri, serverSelectionTimeoutMS=300, tz_aware=True)
    try:
        await mongo.admin.command("ping")
    except ServerSelectionTimeoutError as exc:
        await mongo.close()
        pytest.skip(f"MongoDB is not available at {uri}: {exc}")

    database_name = f"tuvilm_chat_billing_test_{uuid4().hex}"
    database = mongo[database_name]
    store = MongoConversationHistoryStore(mongo_client=mongo, database_name=database_name)
    await store._initialize_storage()
    user_id = str(ObjectId())
    await database["user"].insert_one(
        {"_id": ObjectId(user_id), "plan": "normal", "balance": 6}
    )
    session_id = await _create_session(store, user_id)

    async def test_user(request: Request) -> Principal:
        authorization = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            raise HTTPException(401, "Authentication required.")
        account = await _account(database, authorization[7:])
        return Principal(
            user_id=authorization[7:], plan=account["plan"], balance=account["balance"]
        )

    async def successful_streamer(**kwargs):
        yield {"type": "text", "delta": "A complete answer."}

    monkeypatch.setattr(
        app.state,
        "api_state",
        ApiState(agent_deps=TuviAgentDeps(book_root=""), conversation_history_store=store),
        raising=False,
    )
    monkeypatch.setattr(app.state, "auth_database", database, raising=False)
    monkeypatch.setattr(
        app.state, "session_chat_streamer", successful_streamer, raising=False
    )
    monkeypatch.setitem(app.dependency_overrides, require_user, test_user)
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            yield client, database, store, user_id, session_id
    finally:
        await mongo.drop_database(database_name)
        await store.close()


async def test_normal_chat_costs_three_coins_after_success(billing_context) -> None:
    client, database, store, user_id, session_id = billing_context

    response = await _chat(client, user_id, session_id)

    assert response.status_code == 200
    assert '"type": "done", "status": "confirmed"' in response.text
    assert CHAT_MESSAGE_COST == 3
    await _assert_balance(database, user_id, 3)
    context = await store.load_session_context(user_id, session_id)
    assert context.session.messages[-1].status == ChatMessageStatus.CONFIRMED


async def test_full_unlock_chat_is_free_with_zero_balance(billing_context) -> None:
    client, database, _, user_id, session_id = billing_context
    await _set_access(database, user_id, plan="full_unlock", balance=0)

    response = await _chat(client, user_id, session_id)

    assert response.status_code == 200
    assert '"status": "confirmed"' in response.text
    await _assert_balance(database, user_id, 0)


async def test_insufficient_balance_does_not_start_ai(billing_context) -> None:
    client, database, store, user_id, session_id = billing_context
    await _chat(client, user_id, session_id, idempotency_key="previous")
    previous = (await store.load_session_context(user_id, session_id)).session.messages
    await _set_access(database, user_id, balance=2)

    successful_streamer = app.state.session_chat_streamer
    app.state.session_chat_streamer = _never_generate
    response = await _chat(client, user_id, session_id)

    assert response.status_code == 402
    await _assert_balance(database, user_id, 2)
    context = await store.load_session_context(user_id, session_id)
    assert context.session.messages == previous

    with pytest.raises(HTTPException) as caught:
        await session_chat_stream(
            session_id, SessionChatStreamRequest(content="Question?"),
            Request({"type": "http", "app": app}), Principal(user_id=user_id, balance=100),
            idempotency_key="message-1",
        )
    assert caught.value.status_code == 402
    assert (await store.load_session_context(user_id, session_id)).session.messages == previous
    await _assert_balance(database, user_id, 2)

    await _set_access(database, user_id, balance=3)
    app.state.session_chat_streamer = successful_streamer
    assert (await _chat(client, user_id, session_id)).status_code == 200
    context = await store.load_session_context(user_id, session_id)
    assert context.session.messages[:2] == previous
    assert len(context.session.messages) == 4
    await _assert_balance(database, user_id, 0)


async def test_failed_ai_refunds_once_and_failed_replay_is_free(billing_context) -> None:
    client, database, store, user_id, session_id = billing_context
    calls = 0

    async def failing_streamer(**kwargs):
        nonlocal calls
        calls += 1
        yield {"type": "text", "delta": "Partial answer."}
        raise RuntimeError("AI unavailable.")

    app.state.session_chat_streamer = failing_streamer
    for _ in range(2):
        response = await _chat(client, user_id, session_id)
        assert response.status_code == 200
        assert '"status": "failed"' in response.text

    assert calls == 1
    await _assert_balance(database, user_id, 6)
    context = await store.load_session_context(user_id, session_id)
    assert context.session.messages[-1].status == ChatMessageStatus.FAILED


async def test_completed_replay_is_free_even_after_balance_reaches_zero(
    billing_context,
) -> None:
    client, database, _, user_id, session_id = billing_context
    await _set_access(database, user_id, balance=3)
    calls = 0

    async def streamer(**kwargs):
        nonlocal calls
        calls += 1
        yield {"type": "text", "delta": "An answer."}

    app.state.session_chat_streamer = streamer
    for _ in range(2):
        response = await _chat(client, user_id, session_id)
        assert response.status_code == 200
        assert '"status": "confirmed"' in response.text

    assert calls == 1
    await _assert_balance(database, user_id, 0)


async def test_pending_duplicate_does_not_reserve_coins_again(billing_context) -> None:
    client, database, store, user_id, session_id = billing_context
    await _reserve_pair(database, store, user_id, session_id)

    app.state.session_chat_streamer = _never_generate
    response = await _chat(client, user_id, session_id)

    assert response.status_code == 200
    assert '"type": "duplicate_in_progress"' in response.text
    await _assert_balance(database, user_id, 3, hold_count=1)


async def test_foreign_session_is_rejected_before_charging(billing_context) -> None:
    client, database, _, user_id, session_id = billing_context
    foreign_id = str(ObjectId())
    await database["user"].insert_one(
        {"_id": ObjectId(foreign_id), "plan": "normal", "balance": 6}
    )

    response = await _chat(client, foreign_id, session_id)

    assert response.status_code == 404
    for account_id in (user_id, foreign_id):
        await _assert_balance(database, account_id, 6)


async def test_stale_pending_message_refunds_a_durable_hold(billing_context) -> None:
    _, database, store, user_id, session_id = billing_context
    await _reserve_pair(database, store, user_id, session_id)
    await database["sessions"].update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"messages.1.updated_at": datetime.now(UTC) - timedelta(minutes=16)}},
    )
    account = await _account(database, user_id)

    for _ in range(2):
        await reconcile_chat_coins(database, user_id, account["chat_holds"], store)

    await _assert_balance(database, user_id, 6)
    context = await store.load_session_context(user_id, session_id)
    assert context.session.messages[-1].status == ChatMessageStatus.FAILED


async def test_concurrent_chats_in_different_sessions_allow_only_one_payment(
    billing_context,
) -> None:
    client, database, store, user_id, session_id = billing_context
    second_session_id = await _create_session(store, user_id)
    await _set_access(database, user_id, balance=3)

    responses = await asyncio.gather(
        _chat(client, user_id, session_id),
        _chat(client, user_id, second_session_id),
    )

    assert sorted(response.status_code for response in responses) == [200, 402]
    await _assert_balance(database, user_id, 0)
    for response, target in zip(responses, (session_id, second_session_id)):
        context = await store.load_session_context(user_id, target)
        assert len(context.session.messages) == (2 if response.status_code == 200 else 0)


async def test_disconnect_event_while_ai_is_blocked_refunds(billing_context) -> None:
    client, database, store, user_id, session_id = billing_context
    started = asyncio.Event()

    async def blocked_streamer(**kwargs):
        started.set()
        await asyncio.Future()
        yield {}

    app.state.session_chat_streamer = blocked_streamer
    scope = {"type": "http", "app": app, "asgi": {"spec_version": "2.3"}}
    response = await session_chat_stream(
        session_id,
        SessionChatStreamRequest(content="Question?"),
        Request(scope),
        Principal(user_id=user_id, balance=6),
        idempotency_key="message-1",
    )

    async def receive():
        await started.wait()
        return {"type": "http.disconnect"}

    async def send(message):
        return None

    await asyncio.wait_for(response(scope, receive, send), timeout=2)

    await _assert_balance(database, user_id, 6)
    context = await store.load_session_context(user_id, session_id)
    assert context.session.messages[-1].status == ChatMessageStatus.CANCELLED

    app.state.session_chat_streamer = _never_generate
    replay = await _chat(client, user_id, session_id)
    assert replay.status_code == 200
    assert '"status": "cancelled"' in replay.text
    await _assert_balance(database, user_id, 6)


async def _create_session(store, user_id: str) -> str:
    profile = await store.create_chart_profile(
        user_id,
        CreateChartProfileInput(
            display_name="Me",
            birth_info=BirthInfo(year=1996, month=4, day=15, hour=10, gender="M"),
        ),
        idempotency_key=str(uuid4()),
    )
    session = await store.create_session(
        user_id, profile.id, CreateSessionInput(title="Career"), idempotency_key=str(uuid4())
    )
    return session.id


async def _chat(client, user_id: str, session_id: str, *, idempotency_key="message-1"):
    return await client.post(
        f"/api/v1/sessions/{session_id}/chat/stream",
        headers={"Authorization": f"Bearer {user_id}", "Idempotency-Key": idempotency_key},
        json={"content": "Question?"},
    )


async def _account(database, user_id: str):
    return await database["user"].find_one({"_id": ObjectId(user_id)})


async def _set_access(database, user_id: str, **fields) -> None:
    await database["user"].update_one({"_id": ObjectId(user_id)}, {"$set": fields})


async def _assert_balance(database, user_id: str, balance: int, hold_count: int = 0) -> None:
    account = await _account(database, user_id)
    assert account["balance"] == balance
    assert len(account.get("chat_holds", {})) == hold_count


async def _reserve_pair(database, store, user_id: str, session_id: str) -> None:
    pair = await store.reserve_message_pair(
        user_id, session_id, user_content="Question?", idempotency_key="message-1"
    )
    await reserve_chat_coins(database, user_id, session_id, pair.assistant_message.id)


async def _never_generate(**kwargs):
    raise AssertionError("Generation must not start for this request.")
    yield {}
