from __future__ import annotations

import asyncio
from datetime import timedelta
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, TypeAdapter
from pymongo import AsyncMongoClient

from api.chat.contracts import ConversationHistoryError, DuplicateStreamInProgressError, IdempotencyConflictError
from api.main import conversation_history_exception_handler
from api.background_runs import TERMINAL, RunSettings, now
from api.run_routes import router
from api.background_runs import RunService, Workflow, RunFinished
from api.chat.storage.store import MongoConversationHistoryStore

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def store():
    client = AsyncMongoClient("mongodb://localhost:27017", tz_aware=True, serverSelectionTimeoutMS=1000)
    database = client[f"tuvilm_runs_test_{uuid4().hex}"]
    try:
        await asyncio.wait_for(client.admin.command("ping"), timeout=3)
    except Exception as exc:
        await client.close()
        pytest.skip(f"Local MongoDB unavailable: {type(exc).__name__}")
    storage = MongoConversationHistoryStore(mongo_client=client, database_name=database.name)
    storage.services = []
    await storage._initialize_storage()
    try:
        yield storage
    finally:
        for runs in storage.services:
            await runs.close()
        await client.drop_database(database.name)
        await client.close()


class Inputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resource: str
    question: str = "Hello"


async def authorize(owner, inputs):
    return inputs.resource


async def echo(context, inputs):
    await context.progress("Thinking")
    await context.text(inputs.question)
    return {"answer": inputs.question}


def service(store, execute=echo, finalize=None, output=None, **settings):
    runs = RunService(store, {"echo": Workflow(Inputs, authorize, execute, finalize, output=output)},
                      RunSettings(poll_seconds=0.05, **settings))
    store.services.append(runs)
    return runs


async def submit(runs, key="one", resource="chart:1", owner="owner"):
    return await runs.submit(workflow="echo", inputs={"resource": resource},
                             owner_id=owner, idempotency_key=key)


async def wait_finished(runs, run):
    async with asyncio.timeout(4):
        while True:
            current = await runs.store.get_run(run.id, run.owner_id)
            if current.status in TERMINAL:
                return current
            await asyncio.sleep(0.01)


async def test_api_submission_ownership_validation_and_discovery(store):
    app = FastAPI()
    app.state.run_service = service(store)
    app.include_router(router)
    app.add_exception_handler(ConversationHistoryError, conversation_history_exception_handler)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://test") as client:
        headers = {"X-Anonymous-Owner-Id": "owner", "Idempotency-Key": "key"}
        body = {"workflow": "echo", "inputs": {"resource": "chart:1"}}
        response = await client.post("/api/v1/runs", headers=headers, json=body)
        assert response.status_code == 202
        run = response.json()
        assert "owner_id" not in run and "publishing" not in run
        replay = await client.post("/api/v1/runs", headers=headers, json=body)
        assert replay.json()["id"] == run["id"]
        conflict = await client.post("/api/v1/runs", headers=headers, json={**body, "inputs": {"resource": "other"}})
        assert conflict.status_code == 409
        for suffix, method in [("", "GET"), ("/cancel", "POST")]:
            denied = await client.request(method, f"/api/v1/runs/{run['id']}{suffix}", headers={"X-Anonymous-Owner-Id": "other"})
            assert denied.status_code == 404
        discovered = await client.get("/api/v1/runs?workflow=echo&resource_id=chart:1", headers=headers)
        assert discovered.json()[0]["id"] == run["id"]
        for invalid in [{"workflow": "unknown", "inputs": {}}, {"workflow": "echo", "inputs": {}}]:
            assert (await client.post("/api/v1/runs", headers=headers, json=invalid)).status_code == 422


async def test_concurrent_submissions_execute_only_once_even_across_api_instances(store):
    calls, release = [], asyncio.Event()

    async def blocked(context, inputs):
        calls.append(context.run.id)
        await release.wait()
        return await echo(context, inputs)

    first, second = service(store, blocked), service(store, blocked)
    results = await asyncio.gather(*(submit(first if i % 2 else second) for i in range(8)))
    assert len({run.id for run in results}) == 1
    with pytest.raises(DuplicateStreamInProgressError):
        await submit(first, key="different")
    with pytest.raises(IdempotencyConflictError):
        await submit(first, resource="different")
    release.set()
    assert (await wait_finished(first, results[0])).result == {"answer": "Hello"}
    assert calls == [results[0].id]
    assert (await submit(second)).id == results[0].id
    assert calls == [results[0].id]


@pytest.mark.parametrize("partial", ["", "Partial "])
async def test_disconnect_during_thinking_or_partial_answer_keeps_execution(store, partial):
    started, release = asyncio.Event(), asyncio.Event()

    async def thinking(context, inputs):
        await context.progress("Thinking")
        await context.text(partial)
        started.set()
        await release.wait()
        await context.text("answer")
        return {"answer": partial + "answer"}

    runs = service(store, thinking)
    app = FastAPI()
    app.state.run_service = runs
    app.include_router(router)
    headers = {"X-Anonymous-Owner-Id": "owner", "Idempotency-Key": "one"}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://test") as client:
        response = await client.post("/api/v1/runs", headers=headers,
                                     json={"workflow": "echo", "inputs": {"resource": "chart:1"}})
        assert response.status_code == 202
        run_id = response.json()["id"]
        await asyncio.wait_for(started.wait(), 3)
        progress = await client.get(f"/api/v1/runs/{run_id}", headers=headers)
        assert progress.json()["state"]["text"] == partial
        assert progress.json()["status"] == "running"
    # The client closes while generation is still waiting. Execution needs no observer.
    release.set()
    run = await store.get_run(run_id, "owner")
    completed = await wait_finished(runs, run)
    assert completed.status == "succeeded" and completed.result == {"answer": partial + "answer"}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://test") as reopened:
        saved = await reopened.get(f"/api/v1/runs/{run_id}", headers=headers)
        assert saved.json()["state"]["text"] == partial + "answer"
        assert saved.json()["result"] == {"answer": partial + "answer"}


async def test_closing_request_after_insert_still_schedules_generation(store, monkeypatch):
    inserted, release = asyncio.Event(), asyncio.Event()
    original = store.insert_run

    async def delayed_insert(run):
        saved = await original(run)
        inserted.set()
        await release.wait()
        return saved

    monkeypatch.setattr(store, "insert_run", delayed_insert)
    runs = service(store)
    request = asyncio.create_task(submit(runs))
    await asyncio.wait_for(inserted.wait(), 3)
    request.cancel()
    with pytest.raises(asyncio.CancelledError):
        await request
    release.set()
    run = await store.latest_run("owner", "echo", "chart:1")
    assert (await wait_finished(runs, run)).status == "succeeded"


async def test_explicit_cancel_from_another_api_instance_stops_generation(store):
    started, stopped = asyncio.Event(), asyncio.Event()

    async def blocked(context, inputs):
        await context.text("Partial")
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            stopped.set()

    runs = service(store, blocked)
    run = await submit(runs)
    await asyncio.wait_for(started.wait(), 3)
    await MongoConversationHistoryStore(mongo_client=store._mongo_client, database_name=store._database_name).cancel_run(run.id, "owner")
    finished = await wait_finished(runs, run)
    assert stopped.is_set()
    assert finished.status == "cancelled" and finished.state.text == "Partial"


async def test_queued_request_can_be_cancelled_without_executing(store):
    started = asyncio.Event()
    executed = []

    async def blocked(context, inputs):
        executed.append(inputs.resource)
        started.set()
        await asyncio.Event().wait()

    runs = service(store, blocked, concurrency=1)
    await submit(runs, resource="first")
    await asyncio.wait_for(started.wait(), 3)
    queued = await submit(runs, key="second")
    await store.cancel_run(queued.id, "owner")
    assert (await wait_finished(runs, queued)).status == "cancelled"
    assert executed == ["first"]


async def test_api_shutdown_stops_tasks_without_requeue_or_restart(store):
    started = asyncio.Event()
    calls = []

    async def blocked(context, inputs):
        calls.append(context.run.id)
        started.set()
        await asyncio.Event().wait()

    runs = service(store, blocked)
    run = await submit(runs)
    await asyncio.wait_for(started.wait(), 3)
    await runs.close()
    assert (await store.get_run(run.id, "owner")).status == "cancelled"
    new_api = service(store, blocked)
    assert (await submit(new_api)).id == run.id
    assert len(calls) == 1


async def test_timeout_and_abandoned_records_fail_without_retrying(store):
    started = asyncio.Event()

    async def blocked(context, inputs):
        started.set()
        await asyncio.Event().wait()

    runs = service(store, blocked, timeout_seconds=1)
    run = await submit(runs)
    assert (await wait_finished(runs, run)).status == "failed"
    second = await submit(runs, key="second")
    await store.workflow_runs.update_one({"_id": second.id}, {"$set": {"expires_at": now() - timedelta(seconds=1)}})
    assert (await store.get_run(second.id, "owner")).status == "failed"
    with pytest.raises(RunFinished):
        await store.update_run(second, {"status": "succeeded"})


async def test_publication_failure_fails_once_instead_of_rerunning_model(store):
    calls, publications = [], []

    async def model(context, inputs):
        calls.append(context.run.id)
        return await echo(context, inputs)

    async def publish(context, inputs):
        publications.append(context.run.id)
        raise RuntimeError("history storage unavailable")

    runs = service(store, model, publish)
    run = await submit(runs)
    finished = await wait_finished(runs, run)
    assert finished.status == "failed"
    assert len(calls) == len(publications) == 1
    assert (await submit(runs)).id == run.id


async def test_api_lifespan_starts_tasks_without_a_worker_process(store, monkeypatch):
    import api.main as api_main
    from api.settings import ApiSettings

    closed = []

    async def close():
        closed.append(True)

    async def connect(settings):
        return store

    monkeypatch.setattr(store, "close", close)

    monkeypatch.setattr(api_main.MongoConversationHistoryStore, "connect", connect)
    monkeypatch.setattr(api_main, "get_settings", lambda: ApiSettings(runs=RunSettings(poll_seconds=0.05)))
    monkeypatch.setattr(api_main, "build_tuvi_agent", lambda **kwargs: object())
    monkeypatch.setattr(api_main, "build_personality_agent", lambda **kwargs: object())
    monkeypatch.setattr(api_main, "registered_workflows", lambda app: {"echo": Workflow(Inputs, authorize, echo)})
    app = FastAPI()
    async with api_main.lifespan(app):
        run = await submit(app.state.run_service)
        assert (await wait_finished(app.state.run_service, run)).status == "succeeded"
    assert closed == [True]


async def test_chat_and_personality_share_the_run_service(store, monkeypatch):
    from api.chat.models import BirthInfo, CreateChartProfileInput, CreateSessionInput
    from api.chat.storage.store import MongoConversationHistoryStore
    from api.main import ApiState
    from api.workflows import registered_workflows
    from src.agent.deps import TuviAgentDeps
    import api.chat.routes as chat_routes
    import src.agent.workflow.personality.agent as personality_module

    history = MongoConversationHistoryStore(
        mongo_client=store.workflow_runs.database.client, database_name=store.workflow_runs.database.name,
    )
    await history._initialize_storage()
    profile = await history.create_chart_profile("owner", CreateChartProfileInput(
        display_name="Test", birth_info=BirthInfo(year=1996, month=4, day=15, hour=10, gender="M"),
    ), idempotency_key="profile")
    session = await history.create_session("owner", profile.id, CreateSessionInput(), idempotency_key="session")
    app = FastAPI()
    app.state.api_state = ApiState(TuviAgentDeps(personality_agent=object()), history)
    calls = []

    async def fake_chat(**kwargs):
        calls.append("chat")
        yield {"type": "tool_call", "name": "run_tinh_cach_workflow"}
        yield {"type": "text", "delta": "Chat answer"}

    async def fake_personality(**kwargs):
        calls.append("personality")
        return "Personality answer"

    app.state.session_chat_streamer = fake_chat
    monkeypatch.setattr(chat_routes, "_build_la_so", lambda birth: object())
    monkeypatch.setattr(personality_module, "run_personality_workflow", fake_personality)
    runs = RunService(store, registered_workflows(app), RunSettings(poll_seconds=0.05))
    store.services.append(runs)
    app.state.run_service = runs
    app.include_router(router)
    app.add_exception_handler(ConversationHistoryError, conversation_history_exception_handler)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://test") as client:
        chat = await client.post("/api/v1/runs",
            json={"workflow": "chat", "inputs": {"session_id": session.id, "content": "Question"}}, headers={"X-Anonymous-Owner-Id": "owner", "Idempotency-Key": "chat"})
        assert chat.status_code == 202
        # Queued and running turns are held by the run service, not a stale
        # pending placeholder in conversation history.
        chat_run = await wait_finished(runs, await store.get_run(chat.json()["id"], "owner"))
        assert chat_run.status == "succeeded"
        messages = (await history.load_session_context("owner", session.id)).session.messages
        assert [m.content for m in messages] == ["Question", "Chat answer"]
        assert chat_run.state.metadata["assistant_message_id"] == messages[-1].id
        replay = await client.post("/api/v1/runs",
            json={"workflow": "chat", "inputs": {"session_id": session.id, "content": "Question"}}, headers={"X-Anonymous-Owner-Id": "owner", "Idempotency-Key": "chat"})
        assert replay.json()["id"] == chat_run.id
        personality = await client.post("/api/v1/runs",
            json={"workflow": "personality", "inputs": {"chart_profile_id": profile.id}}, headers={"X-Anonymous-Owner-Id": "owner", "Idempotency-Key": "personality"})
        assert personality.status_code == 202
        result = await wait_finished(runs, await store.get_run(personality.json()["id"], "owner"))
        assert result.result == {"answer": "Personality answer"}
        assert calls == ["chat", "personality"]
        denied = await client.post("/api/v1/runs",
            json={"workflow": "personality", "inputs": {"chart_profile_id": profile.id}}, headers={"X-Anonymous-Owner-Id": "other", "Idempotency-Key": "denied"})
        assert denied.status_code == 404


class ReportRow(BaseModel):
    category: str
    score: float


class StructuredReport(BaseModel):
    summary: str
    rows: list[ReportRow]
    recommendations: list[str]


@pytest.mark.parametrize("root_list", [False, True])
async def test_structured_results_are_independent_of_chat_and_personality(store, root_list):
    rows = [{"category": "career", "score": 0.8}, {"category": "relationships", "score": 0.6}]
    expected = rows if root_list else {
        "summary": "Structured analysis", "rows": rows, "recommendations": ["Explore options"],
    }
    output_schema = TypeAdapter(list[ReportRow]) if root_list else StructuredReport

    async def structured(context, inputs):
        await context.progress("Computing scores")
        return expected

    runs = service(store, structured, output=output_schema)
    queued = await submit(runs)
    finished = await wait_finished(runs, queued)
    assert finished.status == "succeeded"
    assert finished.state.text == ""  # No chat text or `answer` field is required.
    assert finished.result == expected
    restored = await MongoConversationHistoryStore(mongo_client=store._mongo_client, database_name=store._database_name).get_run(queued.id, "owner")
    assert restored.result == expected
    assert restored.snapshot().model_dump(mode="json")["result"] == expected


async def test_invalid_structured_result_fails_before_publication(store):
    published = []

    async def invalid(context, inputs):
        return {"summary": "missing required rows and recommendations"}

    async def finalize(context, inputs):
        published.append(context.status)

    runs = service(store, invalid, finalize, output=StructuredReport)
    queued = await submit(runs)
    result = await wait_finished(runs, queued)
    assert result.status == "failed" and result.result is None
    assert published == ["failed"]


async def test_existing_store_owns_run_storage_and_initializes_it(store):
    from api.chat.storage.store import MongoConversationHistoryStore

    history = MongoConversationHistoryStore(
        mongo_client=store.workflow_runs.database.client, database_name=store.workflow_runs.database.name,
    )
    await history._initialize_storage()
    assert history.workflow_runs.database.client is history._mongo_client
    runs = service(store)
    runs.store = history
    queued = await submit(runs)
    assert (await wait_finished(runs, queued)).status == "succeeded"
    assert (await store.get_run(queued.id, "owner")).result == {"answer": "Hello"}
