from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import json
from types import SimpleNamespace

import httpx
from starlette.requests import Request
from pydantic_ai.messages import ModelResponse, TextPart

from api import main
from src.agent.deps import TuviAgentDeps
from src.agent.workflow.strength_weakness.output import CapabilityProfile
from src.agent.workflow.strength_weakness.stream import complete_values, stream_strength_weakness


FINDING = {"nang_luc_id": "lap_luan_logic", "mo_ta": "Bạn cân nhắc kỹ.", "giai_thich": 'Sách nói "{đối chiếu}".'}
PROFILE = {"tong_quan": "Tổng quan", "diem_manh": [FINDING], "diem_yeu": []}


def test_parser_waits_for_complete_finding_and_handles_braces_and_unicode():
    text = json.dumps(PROFILE, ensure_ascii=False)
    boundary = text.index('}],') + 1
    # The explanation is a valid partial string to partial JSON validators;
    # it must never be sent until its enclosing finding has closed.
    cut = text.index('đối chiếu') + 2
    assert list(complete_values(text[:cut])) == [("tong_quan", 0, "Tổng quan")]
    assert list(complete_values(text[:boundary]))[-1] == ("diem_manh", 0, FINDING)
    assert list(complete_values('```json\n' + text + '\n```'))[-1] == ("diem_manh", 0, FINDING)


class FakeAgent:
    def __init__(self, invalid_first=False):
        self.calls = 0
        self.invalid_first = invalid_first
        self.closed = 0

    @asynccontextmanager
    async def run_stream(self, prompt, **kwargs):
        self.calls += 1
        current = self.calls
        owner = self

        class Result:
            async def stream_responses(self, **kwargs):
                text = json.dumps(PROFILE, ensure_ascii=False)
                # Repeated snapshots must not emit duplicate findings.
                for i in range(0, len(text) + 8, 8):
                    yield ModelResponse(parts=[TextPart(text[:i])]), False

            async def get_output(self):
                if owner.invalid_first and current == 1:
                    return CapabilityProfile.model_validate({})
                return CapabilityProfile.model_validate(PROFILE)

        try:
            yield Result()
        finally:
            self.closed += 1


def test_stream_emits_findings_before_done_and_resets_invalid_attempt(monkeypatch):
    monkeypatch.setattr("src.agent.workflow.strength_weakness.stream._prompt", lambda *_: "prepared evidence")
    agent = FakeAgent(invalid_first=True)

    async def collect():
        return [event async for event in stream_strength_weakness(agent=agent, deps=TuviAgentDeps(), request="test")]

    events = asyncio.run(collect())
    assert [event["type"] for event in events] == ["started", "overview", "finding", "reset", "overview", "finding", "done"]
    assert events[-1]["attempt"] == 1
    assert events[-1]["profile"]["diem_manh"][0]["nang_luc"]
    assert agent.closed == 2


def test_stream_closes_model_when_consumer_stops(monkeypatch):
    monkeypatch.setattr("src.agent.workflow.strength_weakness.stream._prompt", lambda *_: "prepared evidence")
    agent = FakeAgent()

    async def consume():
        stream = stream_strength_weakness(agent=agent, deps=TuviAgentDeps(), request="test")
        while (event := await anext(stream))["type"] != "finding":
            pass
        await stream.aclose()

    asyncio.run(consume())
    assert agent.closed == 1


def test_api_stream_keeps_contract_and_reports_failures(monkeypatch):
    class Base:
        book = None
        book_root = "unused"
        def require_strength_weakness_agent(self):
            return object()

    monkeypatch.setattr(main, "get_api_state", lambda _: SimpleNamespace(agent_deps=Base()))

    async def fake_stream(**kwargs):
        assert kwargs["deps"].la_so is not None
        yield {"type": "started", "attempt": 0}
        yield {"type": "finding", "attempt": 0, "kind": "strength", "id": "diem_manh:0", "index": 0, "finding": FINDING}
        raise RuntimeError("secret upstream detail")

    monkeypatch.setattr(main, "stream_strength_weakness", fake_stream)

    async def request():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app), base_url="http://test") as client:
            return await client.post("/api/v1/laso/strength-weakness/stream", json={"calendar": "solar", "year": 1998, "month": 4, "day": 4, "hour": 8, "gender": "M"})

    response = asyncio.run(request())
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.headers["x-accel-buffering"] == "no"
    events = [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")]
    assert [event["type"] for event in events] == ["started", "finding", "error"]
    assert "secret upstream" not in response.text


def test_api_disconnect_cancels_source_in_its_own_task(monkeypatch):
    class Base:
        book = None
        book_root = "unused"

        def require_strength_weakness_agent(self):
            return object()

    monkeypatch.setattr(main, "get_api_state", lambda _: SimpleNamespace(agent_deps=Base()))
    closed = []

    async def fake_stream(**kwargs):
        owner = asyncio.current_task()
        try:
            yield {"type": "started", "attempt": 0}
            await asyncio.Event().wait()
        finally:
            assert asyncio.current_task() is owner
            closed.append(True)

    monkeypatch.setattr(main, "stream_strength_weakness", fake_stream)

    async def consume():
        response = await main.analyze_strength_weakness_stream(
            main.BuildLasoRequest(year=1998, month=4, day=4, hour=8, gender="M"),
            Request({"type": "http"}),
        )
        assert '"started"' in await anext(response.body_iterator)
        await response.body_iterator.aclose()

    asyncio.run(consume())
    assert closed == [True]
