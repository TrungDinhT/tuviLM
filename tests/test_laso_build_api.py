from __future__ import annotations

import datetime as dt
from datetime import datetime

import httpx
import pytest

from api._parse import to_cung_payload_map
from api.main import ApiState, app
from api.schemas import BuildLasoResponse
from src.agent.deps import TuviAgentDeps
from src.refactored.la_so import LaSo
from src.refactored.model.prior import Gender, LaSoPrior
from src.refactored.view.builder import build_laso_view
from tests.test_conversation_history_api import FakeConversationHistoryStore


pytestmark = pytest.mark.anyio


MENH_CUC_RELATIONS = {"sinh_xuat", "sinh_nhap", "khac_xuat", "khac_nhap", "binh_hoa"}
AM_DUONG_RELATIONS = {"thuan_ly", "nghich_ly"}
DIA_CHI_SLUGS = {
    "ty", "suu", "dan", "meo", "thin", "ti",
    "ngo", "mui", "than", "dau", "tuat", "hoi",
}
NGU_HANH = {"Kim", "Mộc", "Thủy", "Hỏa", "Thổ"}

# (year, month, day, hour, gender) — a handful of charts exercising different
# relations and polarities.
BIRTHS = [
    (1996, 4, 15, 10, "M"),
    (1996, 1, 1, 6, "F"),
    (1990, 11, 23, 22, "M"),
]


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


def _build_domain(year: int, month: int, day: int, hour: int, gender: str):
    """Recompute the chart the way the endpoint does, for comparison."""
    prior = LaSoPrior.from_solar_day(
        dt.datetime(year, month, day, hour),
        Gender.MALE if gender == "M" else Gender.FEMALE,
    )
    la_so = LaSo.from_prior(prior)
    la_so_view = build_laso_view(la_so, study_year=datetime.now().year)
    return la_so, la_so_view


@pytest.mark.parametrize("year,month,day,hour,gender", BIRTHS)
async def test_build_returns_foundation_fields(
    api_client, fresh_api_state, year, month, day, hour, gender
) -> None:
    response = await api_client.post(
        "/api/v1/laso/build",
        json={
            "calendar": "solar",
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "gender": gender,
        },
    )

    assert response.status_code == 200
    body = response.json()

    # All four fields present with enumerated values (the response model
    # rejects anything else; assert the sets explicitly for clarity).
    assert body["menh_cuc_relation"] in MENH_CUC_RELATIONS
    assert body["am_duong_relation"] in AM_DUONG_RELATIONS
    assert body["dia_chi_natal_year"] in DIA_CHI_SLUGS
    assert body["ban_menh_ngu_hanh"] in NGU_HANH

    la_so, la_so_view = _build_domain(year, month, day, hour, gender)

    # Each field agrees with the value the domain already computes.
    assert body["ban_menh_name"] == la_so.ban_menh.name
    assert body["ban_menh_ngu_hanh"] == la_so.ban_menh.ngu_hanh.value
    assert body["menh_cuc_relation_label"] == la_so.menh_cuc_relation().label
    assert body["menh_cuc_relation"] == la_so.menh_cuc_relation().relation_type.value
    assert body["dia_chi_natal_year"] == la_so_view.dia_chi_natal_year.value

    # Polarity matches natal-chi / Mệnh-position parity.
    same_parity = (
        la_so.prior.dia_chi.index % 2 == la_so.natal_context.menh_position.index % 2
    )
    assert body["am_duong_relation"] == ("thuan_ly" if same_parity else "nghich_ly")


@pytest.mark.parametrize("year,month,day,hour,gender", BIRTHS)
async def test_build_existing_fields_unchanged(
    api_client, fresh_api_state, year, month, day, hour, gender
) -> None:
    response = await api_client.post(
        "/api/v1/laso/build",
        json={
            "calendar": "solar",
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "gender": gender,
        },
    )

    assert response.status_code == 200
    parsed = BuildLasoResponse.model_validate(response.json())

    _, la_so_view = _build_domain(year, month, day, hour, gender)

    assert parsed.id == f"{year:04d}{month:02d}{day:02d}{hour:02d}{gender}"
    assert parsed.summary == (
        f"Sinh dương lịch: {day:02d}/{month:02d}/{year} {hour:02d}:00"
    )
    assert parsed.ban_menh_name == la_so_view.ban_menh_name
    assert parsed.cuc_name == la_so_view.cuc_name
    assert parsed.menh_cuc_relation_label == la_so_view.menh_cuc_relation_label
    assert parsed.cung_by_position == to_cung_payload_map(la_so_view)


async def test_build_id_is_stable(api_client, fresh_api_state) -> None:
    payload = {
        "calendar": "solar",
        "year": 1996,
        "month": 4,
        "day": 15,
        "hour": 10,
        "gender": "M",
    }
    first = await api_client.post("/api/v1/laso/build", json=payload)
    second = await api_client.post("/api/v1/laso/build", json=payload)

    assert first.status_code == second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
