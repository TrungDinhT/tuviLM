from __future__ import annotations

import httpx
import pytest

from api.main import ApiState, app
from src.agent.deps import TuviAgentDeps
from tests.test_conversation_history_api import FakeConversationHistoryStore


pytestmark = pytest.mark.anyio


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
def fresh_api_state():
    app.state.api_state = ApiState(
        agent_deps=TuviAgentDeps(book_root=""),
        conversation_history_store=FakeConversationHistoryStore(),
    )
    yield
    del app.state.api_state


async def test_preview_without_gender_returns_menh_chinh_tinh(
    api_client, fresh_api_state
) -> None:
    response = await api_client.post(
        "/api/v1/laso/preview",
        json={"calendar": "solar", "year": 1996, "month": 4, "day": 15, "hour": 10},
    )

    assert response.status_code == 200
    body = response.json()
    assert body == {"chinh_tinh": ["Thái Dương"], "menh_position": "Tuất"}
    # Names are clean — the CungPayload trạng thái suffix is stripped.
    assert all("(" not in name for name in body["chinh_tinh"])


async def test_preview_vo_chinh_dieu_returns_empty_list(
    api_client, fresh_api_state
) -> None:
    response = await api_client.post(
        "/api/v1/laso/preview",
        json={"calendar": "solar", "year": 1996, "month": 1, "day": 1, "hour": 6},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["chinh_tinh"] == []
    assert body["menh_position"] == "Dậu"


async def test_preview_rejects_invalid_calendar_date(
    api_client, fresh_api_state
) -> None:
    response = await api_client.post(
        "/api/v1/laso/preview",
        json={"calendar": "solar", "year": 2000, "month": 2, "day": 31, "hour": 8},
    )

    assert response.status_code == 422


async def test_preview_does_not_touch_la_so_state(api_client, fresh_api_state) -> None:
    await api_client.post(
        "/api/v1/laso/preview",
        json={"calendar": "solar", "year": 1996, "month": 4, "day": 15, "hour": 10},
    )

    health = await api_client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["la_so_created"] is False


async def test_preview_needs_no_identity_headers(api_client, fresh_api_state) -> None:
    # The httpx client sends no X-Anonymous-Owner-Id / Idempotency-Key here.
    response = await api_client.post(
        "/api/v1/laso/preview",
        json={"calendar": "solar", "year": 1996, "month": 4, "day": 15, "hour": 10},
    )

    assert response.status_code == 200
