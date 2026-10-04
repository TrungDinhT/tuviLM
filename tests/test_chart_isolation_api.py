from __future__ import annotations

import asyncio
from datetime import datetime

import httpx
import pytest

from api._parse import to_cung_payload_map
from api.main import ApiState, app
from src.agent.deps import TuviAgentDeps
from src.refactored.cau_phu import get_cau_phu
from src.refactored.la_so import LaSo
from src.refactored.model.prior import Gender, LaSoPrior
from src.refactored.view.builder import build_laso_view
from tests.test_conversation_history_api import FakeConversationHistoryStore


pytestmark = pytest.mark.anyio

BIRTH_A = {"year": 1996, "month": 4, "day": 15, "hour": 10, "gender": "M"}
BIRTH_B = {"year": 1996, "month": 1, "day": 1, "hour": 6, "gender": "F"}
OBSERVATION = {"year": 2026, "month": 10, "day": 3, "hour": 10, "gender": "M"}


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture()
async def api_client(monkeypatch):
    state = ApiState(
        agent_deps=TuviAgentDeps(book_root="", la_so=_domain_chart(BIRTH_B)),
        conversation_history_store=FakeConversationHistoryStore(),
    )
    monkeypatch.setattr(app.state, "api_state", state, raising=False)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        yield client


def _domain_chart(birth: dict) -> LaSo:
    return LaSo.from_prior(
        LaSoPrior.from_solar_day(
            datetime(birth["year"], birth["month"], birth["day"], birth["hour"]),
            Gender.MALE if birth["gender"] == "M" else Gender.FEMALE,
        )
    )


def _request_payload(path: str, birth: dict) -> dict:
    if path.endswith("cau-phu"):
        return birth
    return {"birth_info": birth, "observation_time": OBSERVATION}


def _assert_matches_birth(path: str, response: httpx.Response, birth: dict) -> None:
    assert response.status_code == 200
    chart = _domain_chart(birth)
    if path.endswith("cau-phu"):
        expected = get_cau_phu(chart)
        assert response.json()["cau_phu"] == expected.cau_phu
        assert response.json()["vi_tri"] == expected.vi_tri
    else:
        view = build_laso_view(chart, study_year=OBSERVATION["year"])
        expected_map = to_cung_payload_map(view)
        assert response.json()["cung_by_position"] == {
            position: payload.model_dump(mode="json")
            for position, payload in expected_map.items()
        }


@pytest.mark.parametrize(
    "path", ["/api/v1/laso/cau-phu", "/api/v1/laso/build_sao_luu"]
)
async def test_chart_details_use_birth_without_an_earlier_build(api_client, path) -> None:
    app.state.api_state.agent_deps.la_so = None
    response = await api_client.post(path, json=_request_payload(path, BIRTH_A))

    _assert_matches_birth(path, response, BIRTH_A)
    assert app.state.api_state.agent_deps.la_so is None


@pytest.mark.parametrize(
    "path", ["/api/v1/laso/cau-phu", "/api/v1/laso/build_sao_luu"]
)
async def test_concurrent_chart_details_are_isolated(api_client, path) -> None:
    shared_chart = app.state.api_state.agent_deps.la_so
    births = (BIRTH_A, BIRTH_B, BIRTH_A, BIRTH_B)
    responses = await asyncio.gather(
        *(api_client.post(path, json=_request_payload(path, birth)) for birth in births)
    )

    for response, birth in zip(responses, births):
        _assert_matches_birth(path, response, birth)
    assert responses[0].json() != responses[1].json()
    assert app.state.api_state.agent_deps.la_so is shared_chart


@pytest.mark.parametrize(
    "path", ["/api/v1/laso/cau-phu", "/api/v1/laso/build_sao_luu"]
)
async def test_chart_details_require_birth_data(api_client, path) -> None:
    response = await api_client.post(path, json={})

    assert response.status_code == 422


async def test_sao_luu_rejects_invalid_observation_date(api_client) -> None:
    response = await api_client.post(
        "/api/v1/laso/build_sao_luu",
        json={
            "birth_info": BIRTH_A,
            "observation_time": {**OBSERVATION, "month": 2, "day": 31},
        },
    )

    assert response.status_code == 422
