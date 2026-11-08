"""Lifecycle tests use isolated DBs; the controlled provider never makes paid calls."""

from __future__ import annotations

import asyncio
import os
from datetime import timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import fakeredis.aioredis
import pytest
from bson import ObjectId
from fastapi import HTTPException, Request
from pymongo import AsyncMongoClient
from pymongo.errors import ServerSelectionTimeoutError
from redis.asyncio import Redis

from api.chat.contracts import IdempotencyConflictError, NotFoundError
from api.chat.models import (
    BirthInfo,
    ChatMessageStatus,
    CreateChartProfileInput,
    CreateSessionInput,
)
from api.chat.runtime import ConversationRunLifecycle
from api.chat.storage.store import MongoConversationHistoryStore
from api.runtime.cache import LostOwnership, RedisRunCache
from api.runtime.models import FrozenResult, Run, RunStatus, SubmitRun, now
from api.runtime.routes import observe
from api.runtime.service import WorkflowRuntime
from api.runtime.settings import RuntimeSettings
from api.runtime.store import MongoRunStore
from api.runtime.worker import WorkflowWorker

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def runtime():
    client = AsyncMongoClient(
        os.getenv("CONVERSATION_HISTORY_STORE__URI", "mongodb://127.0.0.1:27017"),
        serverSelectionTimeoutMS=500,
        tz_aware=True,
    )
    try:
        await client.admin.command("ping")
    except ServerSelectionTimeoutError:
        await client.close()
        pytest.skip("MongoDB integration server unavailable")
    name = f"tuvilm_runtime_test_{uuid4().hex}"
    history = MongoConversationHistoryStore(
        mongo_client=client,
        database_name=name,
        stale_pending_after=timedelta(milliseconds=1),
    )
    await history._initialize_storage()
    settings = RuntimeSettings(
        namespace=f"test:{uuid4()}",
        concurrency=100,
        queue_limit=200,
        owner_limit=200,
        lease_seconds=5,
        heartbeat_seconds=0.2,
        flush_seconds=0.01,
        cancel_poll_seconds=0.01,
        recovery_seconds=0.1,
        publications_per_second=100,
    )
    url = os.getenv("RUNTIME_TEST_REDIS_URL")
    redis = (
        Redis.from_url(url, decode_responses=True, max_connections=512)
        if url
        else fakeredis.aioredis.FakeRedis(decode_responses=True)
    )
    cache = RedisRunCache(redis, settings)
    store = MongoRunStore(history.database)
    await store.initialize()
    await cache.ensure_group()
    service = WorkflowRuntime(
        store,
        cache,
        history,
        settings,
        lifecycle=ConversationRunLifecycle(history, history.database),
    )
    try:
        yield service
    finally:
        keys = [key async for key in redis.scan_iter(match=f"{cache.prefix}:*")]
        if keys:
            await redis.delete(*keys)
        await cache.close()
        await client.drop_database(name)
        await history.close()


async def resource(runtime, *, balance=6, owner=None):
    owner = owner or str(ObjectId())
    await runtime.lifecycle.database["user"].update_one(
        {"_id": ObjectId(owner)},
        {"$set": {"balance": balance, "plan": "normal"}},
        upsert=True,
    )
    profile = await runtime.history.create_chart_profile(
        owner,
        CreateChartProfileInput(
            display_name=f"Chart {uuid4()}",
            birth_info=BirthInfo(year=1996, month=4, day=15, hour=10, gender="M"),
        ),
        idempotency_key=str(uuid4()),
    )
    session = await runtime.history.create_session(
        owner, profile.id, CreateSessionInput(), idempotency_key=str(uuid4())
    )
    return owner, profile.id, session.id


async def submit(
    runtime, owner, session, *, key="question", content="Tell me about my career"
):
    return await runtime.submit(
        owner, SubmitRun(session_id=session, content=content), key
    )


async def account(runtime, owner):
    return await runtime.lifecycle.database["user"].find_one({"_id": ObjectId(owner)})


async def deliver(worker, run):
    delivery = await worker.cache.redis.xadd(worker.cache.jobs, {"run_id": run.id})
    # Register the delivery in the pending entries list before the heartbeat XCLAIM.
    await worker.cache.redis.xreadgroup(
        worker.cache.group, worker.consumer, {worker.cache.jobs: ">"}, count=1000
    )
    await worker.handle(delivery, run.id)


async def successful(run):
    for text in ("A ", "complete ", "answer"):
        yield {"type": "text", "delta": text}
        await asyncio.sleep(0.02)


async def wait_status(runtime, owner, run_id, status, *, text=None):
    async with asyncio.timeout(5):
        while True:
            snap = await runtime.snapshot(owner, run_id)
            if snap.status == status and (text is None or snap.text == text):
                return snap
            await asyncio.sleep(0.01)


async def test_duplicate_submissions_reserve_once_and_exclude_own_prompt(runtime):
    owner, _, session = await resource(runtime, balance=3)
    runs = await asyncio.gather(*[submit(runtime, owner, session) for _ in range(25)])
    assert len({run.id for run in runs}) == 1
    run = await runtime.store.get(runs[0].id)
    assert run.status == RunStatus.QUEUED and run.history == []
    context = await runtime.history.load_session_context(owner, session)
    assert len(context.session.messages) == 2
    assert context.session.messages[-1].status == ChatMessageStatus.PENDING
    assert context.session.messages[-1].content == ""
    user = await account(runtime, owner)
    assert user["balance"] == 0 and len(user["chat_holds"]) == 1
    with pytest.raises(IdempotencyConflictError):
        await submit(runtime, owner, session, content="different")


async def test_disconnect_detaches_and_only_full_answer_is_saved(runtime):
    owner, _, session = await resource(runtime)
    run = await submit(runtime, owner, session)
    gate = asyncio.Event()

    async def provider(run):
        yield {"type": "text", "delta": "First "}
        await gate.wait()
        yield {"type": "text", "delta": "last"}

    runtime.history.finalize_assistant_message = AsyncMock(
        wraps=runtime.history.finalize_assistant_message
    )
    worker = WorkflowWorker(runtime, provider)
    task = asyncio.create_task(deliver(worker, run))
    snap = await wait_status(runtime, owner, run.id, RunStatus.RUNNING, text="First ")
    assert (
        await runtime.history.load_session_context(owner, session)
    ).session.messages[-1].content == ""
    observer = observe(runtime, owner, snap)
    await anext(observer)
    await anext(observer)
    await observer.aclose()
    assert not task.done()
    gate.set()
    await task
    final = await runtime.snapshot(owner, run.id)
    assert (
        final.status == RunStatus.SUCCEEDED
        and final.text == "First last"
        and final.persisted
    )
    assert runtime.history.finalize_assistant_message.await_count == 1
    assert (await account(runtime, owner))["balance"] == 3
    assert (await submit(runtime, owner, session)).id == run.id


async def test_stop_saves_partial_cancelled_and_refunds_once(runtime):
    owner, _, session = await resource(runtime, balance=3)
    run = await submit(runtime, owner, session)

    async def provider(run):
        yield {"type": "text", "delta": "Partial"}
        await asyncio.Event().wait()

    worker = WorkflowWorker(runtime, provider)
    task = asyncio.create_task(deliver(worker, run))
    await wait_status(runtime, owner, run.id, RunStatus.RUNNING, text="Partial")
    await runtime.cancel(owner, run.id)
    await asyncio.wait_for(task, 5)
    snap = await runtime.snapshot(owner, run.id)
    assert snap.status == RunStatus.CANCELLED and snap.text == "Partial"
    assert (await account(runtime, owner))["balance"] == 3
    await runtime.publish(await runtime.store.get(run.id))
    assert (await account(runtime, owner))["balance"] == 3


async def test_provider_error_is_failed_with_partial_text(runtime):
    owner, _, session = await resource(runtime)
    run = await submit(runtime, owner, session)

    async def provider(run):
        yield {"type": "text", "delta": "Partial"}
        raise RuntimeError("provider unavailable")

    await deliver(WorkflowWorker(runtime, provider), run)
    snap = await runtime.snapshot(owner, run.id)
    assert snap.status == RunStatus.FAILED and snap.text == "Partial"
    assert snap.error_code == "provider_error"
    assert (await account(runtime, owner))["balance"] == 6


async def test_queued_stop_does_not_call_provider(runtime):
    owner, _, session = await resource(runtime)
    run = await submit(runtime, owner, session)
    await runtime.cancel(owner, run.id)
    calls = []

    async def provider(run):
        calls.append(run.id)
        yield {"type": "text", "delta": "must not run"}

    await deliver(WorkflowWorker(runtime, provider), run)
    assert calls == []
    assert (await runtime.snapshot(owner, run.id)).status == RunStatus.CANCELLED


async def test_publication_failure_retries_frozen_answer_without_model(runtime):
    owner, _, session = await resource(runtime)
    run = await submit(runtime, owner, session)
    original = runtime.history.finalize_assistant_message
    runtime.history.finalize_assistant_message = AsyncMock(
        side_effect=RuntimeError("Mongo temporarily unavailable")
    )
    calls = []

    async def provider(run):
        calls.append(run.id)
        async for event in successful(run):
            yield event

    worker = WorkflowWorker(runtime, provider)
    await deliver(worker, run)
    staged = await runtime.store.get(run.id)
    assert (
        staged.status == RunStatus.PUBLISHING
        and staged.publication.text == "A complete answer"
    )
    assert await runtime.cache.redis.ttl(runtime.cache.keys(run.id)[0]) == -1
    with pytest.raises(HTTPException) as late:
        await runtime.cancel(owner, run.id)
    assert late.value.status_code == 409
    runtime.history.finalize_assistant_message = original
    await worker.handle("9999999999999-1", run.id)
    assert len(calls) == 1
    assert (await runtime.snapshot(owner, run.id)).status == RunStatus.SUCCEEDED


async def test_crash_recovery_preserves_partial_and_never_regenerates(runtime):
    owner, _, session = await resource(runtime)
    run = await submit(runtime, owner, session)
    claimed = await runtime.store.claim_execution(run.id, "9999999999999-2")
    await runtime.cache.activate(claimed)
    await runtime.cache.event(claimed, {"type": "text", "delta": "Before crash"})
    await runtime.cache.redis.delete(runtime.cache.keys(run.id)[4])
    await runtime.store.collection.update_one(
        {"_id": run.id}, {"$set": {"started_at": now() - timedelta(seconds=10)}}
    )
    worker = WorkflowWorker(runtime, successful)
    await worker.reconcile()
    staged = await runtime.store.get(run.id)
    assert (
        staged.status == RunStatus.PUBLISHING and staged.publication.outcome == "failed"
    )
    await worker.handle("9999999999999-3", run.id)
    assert (await runtime.snapshot(owner, run.id)).text == "Before crash"
    assert (await account(runtime, owner))["balance"] == 6
    with pytest.raises(LostOwnership):
        await runtime.cache.event(claimed, {"type": "text", "delta": "stale writer"})


async def test_frozen_completion_survives_crash_before_mongo_stage(runtime):
    owner, _, session = await resource(runtime)
    run = await submit(runtime, owner, session)
    claimed = await runtime.store.claim_execution(run.id, "9999999999999-2")
    await runtime.cache.activate(claimed)
    await runtime.cache.event(claimed, {"type": "text", "delta": "Finished"})
    await runtime.cache.freeze(
        claimed, FrozenResult(outcome="succeeded", text="Finished")
    )
    await runtime.cache.redis.delete(runtime.cache.keys(run.id)[4])
    await runtime.store.collection.update_one(
        {"_id": run.id}, {"$set": {"started_at": now() - timedelta(seconds=10)}}
    )
    worker = WorkflowWorker(runtime, successful)
    await worker.reconcile()
    await worker.handle("9999999999999-3", run.id)
    assert (await runtime.snapshot(owner, run.id)).status == RunStatus.SUCCEEDED
    assert (await account(runtime, owner))["balance"] == 3


async def test_failed_admission_compensates_and_capacity_is_reusable(runtime):
    owner, _, session = await resource(runtime, balance=0)
    with pytest.raises(HTTPException) as rejected:
        await submit(runtime, owner, session)
    assert rejected.value.status_code == 402
    assert (
        await runtime.history.load_session_context(owner, session)
    ).session.messages == []
    assert (await runtime.store.capacity.find_one({"_id": "global"}))["runs"] == {}
    assert (await account(runtime, owner))["balance"] == 0
    await runtime.lifecycle.database["user"].update_one(
        {"_id": ObjectId(owner)}, {"$set": {"balance": 3}}
    )
    retried = await submit(runtime, owner, session)
    assert retried.status == RunStatus.QUEUED
    assert (
        len(
            (
                await runtime.history.load_session_context(owner, session)
            ).session.messages
        )
        == 2
    )


async def test_cross_owner_and_deleted_runs_are_inaccessible(runtime):
    owner, _, session = await resource(runtime)
    run = await submit(runtime, owner, session)
    for operation in (runtime.snapshot, runtime.cancel):
        with pytest.raises(NotFoundError):
            await operation(str(ObjectId()), run.id)
    await runtime.history.delete_session(owner, session)
    await runtime.deleted(owner, session)
    await deliver(WorkflowWorker(runtime, successful), run)
    assert (await account(runtime, owner))["balance"] == 3
    with pytest.raises(NotFoundError):
        await runtime.snapshot(owner, run.id)
    assert await runtime.store.list(owner, "chat", session) == []


async def test_cache_eviction_falls_back_to_mongo_and_no_lease_finishes_failed(runtime):
    owner, _, session = await resource(runtime)
    run = await submit(runtime, owner, session)
    claimed = await runtime.store.claim_execution(run.id, "9999999999999-4")
    await runtime.cache.activate(claimed)
    await runtime.cache.redis.delete(*runtime.cache.keys(run.id))
    await runtime.store.collection.update_one(
        {"_id": run.id}, {"$set": {"started_at": now() - timedelta(seconds=10)}}
    )
    worker = WorkflowWorker(runtime, successful)
    await worker.reconcile()
    await worker.handle("9999999999999-3", run.id)
    assert (await runtime.store.get(run.id)).status == RunStatus.FAILED
    await runtime.cache.redis.delete(*runtime.cache.keys(run.id))
    assert (await runtime.snapshot(owner, run.id)).persisted


@pytest.mark.parametrize("count", [100, 150])
async def test_concurrent_mixed_workflows_and_burst_queue(runtime, count):
    resources = [await resource(runtime) for _ in range(count)]
    requests = [
        SubmitRun(session_id=session, content="Question")
        if i % 2 == 0
        else SubmitRun(
            workflow="personality",
            chart_profile_id=profile,
        )
        for i, (_, profile, session) in enumerate(resources)
    ]
    runs = await asyncio.gather(
        *[
            runtime.submit(owner, request, str(uuid4()))
            for (owner, _, _), request in zip(resources, requests)
        ]
    )
    active = peak = 0
    calls = []
    gate = asyncio.Event()

    async def provider(run):
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        calls.append(run.id)
        try:
            if active == 100:
                gate.set()
            await asyncio.wait_for(gate.wait(), 5)
            yield {"type": "text", "delta": "complete"}
            yield {
                "type": "artifact",
                "workflow": run.workflow,
                "result": {"validated": True},
            }
            yield {"type": "result", "output": {"validated": True}}
        finally:
            active -= 1

    worker = WorkflowWorker(runtime, provider)
    task = asyncio.create_task(worker.run())
    try:
        async with asyncio.timeout(30):
            while await runtime.store.collection.count_documents(
                {
                    "$or": [
                        {"status": {"$ne": "succeeded"}},
                        {"terminal_cleanup_pending": True},
                    ]
                }
            ):
                await asyncio.sleep(0.05)
        assert peak == 100 and len(calls) == count and len(set(calls)) == count
        assert (await runtime.store.capacity.find_one({"_id": "global"}))["runs"] == {}
        for run in runs:
            final = await runtime.store.get(run.id)
            assert (
                final.publication.text == "complete"
                and final.publication.result == {"validated": True}
            )
            assert len(final.publication.artifacts) == 1
    finally:
        worker.stopping.set()
        await asyncio.wait_for(task, 5)


async def test_cache_snapshot_cursor_and_fence_are_atomic_without_mongo():
    cache = RedisRunCache(
        fakeredis.aioredis.FakeRedis(decode_responses=True), RuntimeSettings()
    )
    run = Run(
        owner_id="owner",
        workflow="personality",
        resource_id="chart",
        chart_profile_id="chart",
        idempotency_key="key",
        fingerprint="fp",
        birth_info=BirthInfo(year=1996, month=4, day=15, hour=10, gender="M"),
        status=RunStatus.RUNNING,
        token="token",
    )
    try:
        assert await cache.activate(run)
        await cache.event(run, {"type": "text", "delta": "Unicode ☀"})
        _, snapshot, _ = await cache.snapshot(run.id)
        assert snapshot.text == "Unicode ☀" and snapshot.cursor != "0-0"
        await cache.freeze(run, FrozenResult(outcome="succeeded", text=snapshot.text))
        with pytest.raises(LostOwnership):
            await cache.event(run, {"type": "text", "delta": "too late"})
        assert await cache.redis.ttl(cache.keys(run.id)[0]) == -1
    finally:
        await cache.close()


async def test_provider_budget_includes_multiple_agents_without_mongo():
    from pydantic_ai import Agent
    from pydantic_ai.messages import ModelResponse, TextPart
    from pydantic_ai.models.function import FunctionModel

    from api.runtime.provider import BudgetedModel

    cache = RedisRunCache(
        fakeredis.aioredis.FakeRedis(decode_responses=True),
        RuntimeSettings(provider_concurrency=3),
    )
    active = peak = 0

    async def provider(messages, info):
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        try:
            await asyncio.sleep(0.02)
            return ModelResponse(parts=[TextPart("complete")])
        finally:
            active -= 1

    agents = [Agent(BudgetedModel(FunctionModel(provider), cache)) for _ in range(2)]
    try:
        replies = await asyncio.gather(
            *[agents[i % 2].run("question") for i in range(12)]
        )
        assert peak == 3 and all(reply.output == "complete" for reply in replies)
        assert await cache.redis.zcard(f"{cache.prefix}:provider") == 0
    finally:
        await cache.close()


async def test_stop_wins_before_mongo_publication_and_cache_uses_chosen_outcome(
    runtime,
):
    owner, _, session = await resource(runtime)
    run = await submit(runtime, owner, session)
    claimed = await runtime.store.claim_execution(run.id, "9999999999999-1")
    await runtime.cache.activate(claimed)
    await runtime.cache.event(claimed, {"type": "text", "delta": "response"})
    frozen = await runtime.cache.freeze(
        claimed, FrozenResult(outcome="succeeded", text="response")
    )
    await runtime.cancel(owner, run.id)
    staged = await runtime.store.stage(claimed, frozen)
    assert staged.publication.outcome == "cancelled"
    await runtime.publish(staged)
    assert (await runtime.snapshot(owner, run.id)).outcome == "cancelled"
    assert (await account(runtime, owner))["balance"] == 6


async def test_commit_cache_failure_releases_capacity_and_recovers_terminal_cleanup(
    runtime,
):
    owner, _, session = await resource(runtime)
    run = await submit(runtime, owner, session)
    original = runtime.cache.complete
    runtime.cache.complete = AsyncMock(
        side_effect=RuntimeError("Redis completion unavailable")
    )
    await deliver(WorkflowWorker(runtime, successful), run)
    committed = await runtime.store.get(run.id)
    assert (
        committed.status == RunStatus.SUCCEEDED and committed.terminal_cleanup_pending
    )
    assert (await runtime.store.capacity.find_one({"_id": "global"}))["runs"] == {}
    runtime.cache.complete = original
    await WorkflowWorker(runtime, successful).reconcile()
    assert not (await runtime.store.get(run.id)).terminal_cleanup_pending
    assert (await runtime.snapshot(owner, run.id)).persisted


async def test_preparation_crash_after_coin_hold_recovers_same_pair_without_double_debit(
    runtime,
):
    owner, profile, session = await resource(runtime, balance=3)
    request = SubmitRun(session_id=session, content="question")
    run = Run(
        owner_id=owner,
        workflow="chat",
        session_id=session,
        resource_id=session,
        chart_profile_id=profile,
        birth_info=BirthInfo(year=1996, month=4, day=15, hour=10, gender="M"),
        content=request.content,
        idempotency_key="key",
        fingerprint=request.fingerprint,
    )
    run.user_message_id, run.assistant_message_id = run.message_ids()
    await runtime.store.insert(run)
    from api.accounts.billing import reserve_chat_coins

    await runtime.history.reserve_message_pair(
        owner,
        session,
        user_content=run.content,
        idempotency_key="key",
        runtime_run_id=run.id,
    )
    await reserve_chat_coins(
        runtime.lifecycle.database, owner, session, run.assistant_message_id
    )
    recovered = await runtime.submit(owner, request, "key")
    assert (
        recovered.id == run.id
        and recovered.status == RunStatus.QUEUED
        and recovered.history == []
    )
    assert (await account(runtime, owner))["balance"] == 0


async def test_run_http_contracts_and_terminal_sse(runtime):
    from types import SimpleNamespace

    import httpx
    from fastapi import FastAPI

    from api.auth.dependencies import Principal, require_reconciled_user, require_user
    from api.chat.contracts import ConversationHistoryError
    from api.chat.routes import router as chat_router
    from api.main import conversation_history_exception_handler
    from api.runtime.routes import router

    owner, _, session = await resource(runtime)
    app = FastAPI()
    app.include_router(router)
    app.include_router(chat_router)
    app.add_exception_handler(
        ConversationHistoryError, conversation_history_exception_handler
    )
    app.state.workflow_runtime = runtime
    app.state.api_state = SimpleNamespace(conversation_history_store=runtime.history)

    async def user(request: Request):
        identity = request.headers.get("Authorization", "").removeprefix("Bearer ")
        if not identity:
            raise HTTPException(401, "Authentication required")
        return Principal(user_id=identity, plan="normal", balance=6)

    app.dependency_overrides[require_user] = user
    app.dependency_overrides[require_reconciled_user] = user
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        body = {"workflow": "chat", "session_id": session, "content": "question"}
        assert (
            await client.post(
                "/api/v1/runs", json=body, headers={"Idempotency-Key": "key"}
            )
        ).status_code == 401
        headers = {"Authorization": f"Bearer {owner}", "Idempotency-Key": "key"}
        first = await client.post("/api/v1/runs", json=body, headers=headers)
        assert first.status_code == 202
        run_id = first.json()["run"]["id"]
        replay = await client.post("/api/v1/runs", json=body, headers=headers)
        assert replay.json()["run"]["id"] == run_id
        assert (
            await client.get(
                f"/api/v1/runs/{run_id}",
                headers={"Authorization": f"Bearer {ObjectId()}"},
            )
        ).status_code == 404
        await deliver(
            WorkflowWorker(runtime, successful), await runtime.store.get(run_id)
        )
        events = await client.get(f"/api/v1/runs/{run_id}/events", headers=headers)
        assert events.status_code == 200
        assert '"type": "snapshot"' in events.text and '"type": "done"' in events.text
        assert "A complete answer" in events.text
        listed = await client.get(
            f"/api/v1/runs?workflow=chat&resource_id={session}", headers=headers
        )
        assert listed.json()["runs"][0]["status"] == "succeeded"
        old_route = await client.post(
            f"/api/v1/sessions/{session}/chat/stream",
            json={"content": "question"},
            headers=headers,
        )
        assert "A complete answer" in old_route.text


async def test_completed_cache_oom_falls_back_to_db(runtime):
    from redis.exceptions import OutOfMemoryError

    owner, _, session = await resource(runtime)
    run = await submit(runtime, owner, session)
    error = OutOfMemoryError("command not allowed when used memory > maxmemory")
    runtime.cache.freeze = AsyncMock(side_effect=error)
    runtime.cache._complete = AsyncMock(side_effect=error)
    await deliver(WorkflowWorker(runtime, successful), run)
    assert (await runtime.store.get(run.id)).status == RunStatus.SUCCEEDED
    assert (await runtime.snapshot(owner, run.id)).text == "A complete answer"
    assert await runtime.cache.redis.exists(runtime.cache.keys(run.id)[0]) == 0


async def test_terminal_replay_after_cache_expiration_has_ttl(runtime):
    owner, _, session = await resource(runtime)
    run = await submit(runtime, owner, session)
    await deliver(WorkflowWorker(runtime, successful), run)
    await runtime.cache.redis.delete(*runtime.cache.keys(run.id))
    replay = await submit(runtime, owner, session)
    assert replay.id == run.id
    assert await runtime.cache.redis.ttl(runtime.cache.keys(run.id)[0]) > 0


@pytest.mark.parametrize("workflow", ["chat", "personality"])
async def test_agent_executor_uses_real_sdk_adapters_without_paid_provider(workflow):
    from pydantic_ai.models.test import TestModel

    from api.runtime.execution import AgentExecutor
    from api.runtime.provider import BudgetedModel

    cache = RedisRunCache(
        fakeredis.aioredis.FakeRedis(decode_responses=True),
        RuntimeSettings(model="test"),
    )
    executor = AgentExecutor(cache)
    run = Run(
        owner_id="owner",
        workflow=workflow,
        resource_id="resource",
        chart_profile_id="chart",
        session_id="session" if workflow == "chat" else None,
        content="question",
        idempotency_key="key",
        fingerprint="fp",
        birth_info=BirthInfo(year=1996, month=4, day=15, hour=10, gender="M"),
    )
    output = "Final response"
    model = BudgetedModel(TestModel(call_tools=[], custom_output_text=output), cache)
    agent = {
        "chat": executor.base.agent,
        "personality": executor.base.personality_agent,
    }[workflow]
    try:
        with agent.override(model=model):
            events = [event async for event in executor(run)]
        assert any(event["type"] == "text" for event in events)
        if workflow != "chat":
            assert any(
                event["type"] == "artifact" and event["workflow"] == workflow
                for event in events
            )
    finally:
        await cache.close()


async def test_nested_workflow_does_not_deadlock_single_provider_slot():
    from pydantic_ai.messages import ModelResponse, TextPart, ToolReturnPart
    from pydantic_ai.models.function import DeltaToolCall, FunctionModel

    from api.runtime.execution import AgentExecutor
    from api.runtime.provider import BudgetedModel

    cache = RedisRunCache(
        fakeredis.aioredis.FakeRedis(decode_responses=True),
        RuntimeSettings(model="test", provider_concurrency=1),
    )
    executor = AgentExecutor(cache)

    async def parent_stream(messages, info):
        if any(
            isinstance(part, ToolReturnPart)
            for message in messages
            for part in message.parts
        ):
            yield "Final parent response"
        else:
            yield {
                0: DeltaToolCall(
                    name="run_tinh_cach_workflow",
                    json_args='{"request":"personality"}',
                    tool_call_id="nested",
                )
            }

    async def child_response(messages, info):
        return ModelResponse(parts=[TextPart("Validated child response")])

    parent = BudgetedModel(FunctionModel(stream_function=parent_stream), cache)
    child = BudgetedModel(FunctionModel(child_response), cache)
    run = Run(
        owner_id="owner",
        workflow="chat",
        resource_id="session",
        chart_profile_id="chart",
        session_id="session",
        content="personality",
        idempotency_key="key",
        fingerprint="fp",
        birth_info=BirthInfo(year=1996, month=4, day=15, hour=10, gender="M"),
    )
    try:
        async with asyncio.timeout(5):
            with (
                executor.base.agent.override(model=parent),
                executor.base.personality_agent.override(model=child),
            ):
                events = [event async for event in executor(run)]
        assert any(
            event["type"] == "artifact"
            and event["result"]["text"] == "Validated child response"
            for event in events
        )
        assert (
            "".join(event["delta"] for event in events if event["type"] == "text")
            == "Final parent response"
        )
        assert await cache.redis.zcard(f"{cache.prefix}:provider") == 0
    finally:
        await cache.close()


async def test_worker_recreates_lost_job_group_without_regenerating_active_run(runtime):
    owner, _, session = await resource(runtime)
    run = await submit(runtime, owner, session)
    calls = []
    gate = asyncio.Event()

    async def provider(run):
        calls.append(run.id)
        yield {"type": "text", "delta": "Before "}
        await gate.wait()
        yield {"type": "text", "delta": "after"}

    worker = WorkflowWorker(runtime, provider)
    task = asyncio.create_task(worker.run())
    try:
        await wait_status(runtime, owner, run.id, RunStatus.RUNNING, text="Before ")
        await runtime.cache.redis.delete(runtime.cache.jobs)
        async with asyncio.timeout(5):
            while not await runtime.cache.redis.exists(runtime.cache.jobs):
                await asyncio.sleep(0.05)
        gate.set()
        await wait_status(
            runtime, owner, run.id, RunStatus.SUCCEEDED, text="Before after"
        )
        assert calls == [run.id]
    finally:
        worker.stopping.set()
        await asyncio.wait_for(task, 5)


async def test_runtime_uses_application_hooks_without_account_dependency(runtime):
    owner, _, session = await resource(runtime)
    database = runtime.lifecycle.database
    await database["user"].delete_one({"_id": ObjectId(owner)})
    calls = []

    class ApplicationLifecycle:
        retryable_rejections = frozenset()

        async def admit(self, run):
            calls.append(("admit", run.id))
            return {}

        async def rollback(self, run):
            calls.append(("rollback", run.id))

        async def publish(self, run):
            calls.append(("publish", run.publication.text))
            return True

    runtime.lifecycle = ApplicationLifecycle()
    run = await submit(runtime, owner, session)
    await deliver(WorkflowWorker(runtime, successful), run)
    final = await runtime.store.get(run.id)
    assert final.status == RunStatus.SUCCEEDED
    assert calls == [("admit", run.id), ("publish", "A complete answer")]
    assert await database["user"].find_one({"_id": ObjectId(owner)}) is None


async def test_external_workflow_output_is_observed_without_workflow_changes():
    from pydantic_ai import Agent
    from pydantic_ai.models.test import TestModel

    from api.runtime.execution import AgentExecutor
    from api.runtime.provider import BudgetedModel

    cache = RedisRunCache(
        fakeredis.aioredis.FakeRedis(decode_responses=True),
        RuntimeSettings(model="test"),
    )
    executor = AgentExecutor(
        cache, workflow_tools={"independent_report": "external_report"}
    )
    output = {"summary": "Validated report", "ratings": [1, 2, 3]}
    calls = []

    async def independent_report() -> dict:
        calls.append("workflow")
        return output

    executor.base.agent = Agent(
        model=BudgetedModel(TestModel(custom_output_text="Final response"), cache),
        tools=[independent_report],
    )
    run = Run(
        owner_id="owner",
        workflow="chat",
        resource_id="session",
        chart_profile_id="chart",
        session_id="session",
        content="question",
        idempotency_key="key",
        fingerprint="fp",
        birth_info=BirthInfo(year=1996, month=4, day=15, hour=10, gender="M"),
    )
    try:
        events = [event async for event in executor(run)]
        artifacts = [event for event in events if event["type"] == "artifact"]
        assert calls == ["workflow"]
        assert artifacts == [
            {
                "type": "artifact",
                "workflow": "external_report",
                "result": output,
            }
        ]
    finally:
        await cache.close()


async def test_duplicate_queue_deliveries_generate_once(runtime):
    owner, _, session = await resource(runtime)
    run = await submit(runtime, owner, session)
    await runtime.cache.enqueue(run.id)
    await runtime.cache.enqueue(run.id)
    calls = []

    async def provider(run):
        calls.append(run.id)
        yield {"type": "text", "delta": "answer"}

    worker = WorkflowWorker(runtime, provider)
    deliveries = []
    for _ in range(3):
        deliveries.extend(await runtime.cache.read_job(worker.consumer))
    await asyncio.gather(
        *[worker.handle(delivery, fields["run_id"]) for delivery, fields in deliveries]
    )
    assert len(deliveries) == 3 and calls == [run.id]
    assert (await runtime.store.get(run.id)).status == RunStatus.SUCCEEDED


async def test_worker_closes_executor_when_artifact_save_fails(runtime):
    owner, _, session = await resource(runtime)
    run = await submit(runtime, owner, session)
    closed = asyncio.Event()

    async def provider():
        try:
            yield {
                "type": "artifact",
                "workflow": "report",
                "result": {"text": "answer"},
            }
        finally:
            closed.set()

    generator = provider()
    worker = WorkflowWorker(runtime, lambda run: generator)
    runtime.cache.event = AsyncMock(side_effect=RuntimeError("cache write failed"))
    try:
        await deliver(worker, run)
        assert closed.is_set()
        assert (await runtime.store.get(run.id)).status == RunStatus.FAILED
    finally:
        await generator.aclose()
