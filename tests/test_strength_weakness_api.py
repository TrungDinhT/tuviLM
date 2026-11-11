from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import httpx
import pytest
from bson import ObjectId
from fastapi import HTTPException, Request
from pymongo import AsyncMongoClient
from pymongo.errors import ServerSelectionTimeoutError

from tuvi_api import main as routes
from tuvi_api.accounts.capability import (
    CAPABILITY_REPORT_COST,
    STALE_HOLD_AFTER,
    capability_chart_key,
    ensure_capability_report_indexes,
)
from tuvi_api.auth.dependencies import Principal, require_user
from tuvi_api.chat.models import BirthInfo
from tuvi_agent.deps import TuviAgentDeps
from tuvi_agent.workflow.strength_weakness import CapabilityProfile, StrengthFinding


pytestmark = pytest.mark.anyio

URL = "/api/v1/laso/strength-weakness"
BIRTH = {"calendar": "solar", "year": 1990, "month": 5, "day": 15, "hour": 10, "gender": "M"}
PROFILE = CapabilityProfile(
    tong_quan="Tổng quan",
    diem_manh=[StrengthFinding(nang_luc_id="quyet_doan", mo_ta="Mô tả", giai_thich="Giải thích")],
)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture()
async def analysis(monkeypatch):
    uri = os.environ.get("CONVERSATION_HISTORY_STORE__URI", "mongodb://localhost:27017")
    mongo = AsyncMongoClient(uri, serverSelectionTimeoutMS=300)
    try:
        await mongo.admin.command("ping")
    except ServerSelectionTimeoutError as exc:
        await mongo.close()
        pytest.skip(f"MongoDB is not available at {uri}: {exc}")

    database_name = f"tuvilm_capability_test_{uuid4().hex}"
    database = mongo[database_name]
    await ensure_capability_report_indexes(database)
    user_id = str(ObjectId())
    await database["user"].insert_one(
        {"_id": ObjectId(user_id), "plan": "normal", "balance": CAPABILITY_REPORT_COST}
    )

    async def test_user(request: Request) -> Principal:
        authorization = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            raise HTTPException(401, "Authentication required.")
        return Principal(user_id=authorization[7:])

    workflow_agent = object()
    base_deps = TuviAgentDeps(strength_weakness_agent=workflow_agent)
    run = AsyncMock(return_value=PROFILE)
    monkeypatch.setattr(routes, "run_strength_weakness_agent", run)
    monkeypatch.setattr(
        routes.app.state, "api_state", SimpleNamespace(agent_deps=base_deps), raising=False
    )
    monkeypatch.setattr(routes.app.state, "auth_database", database, raising=False)
    monkeypatch.setitem(routes.app.dependency_overrides, require_user, test_user)
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=routes.app),
            base_url="http://testserver",
            headers={"Authorization": f"Bearer {user_id}"},
        ) as client:
            yield SimpleNamespace(
                client=client,
                database=database,
                user_id=user_id,
                run=run,
                agent=workflow_agent,
                base_deps=base_deps,
            )
    finally:
        await mongo.drop_database(database_name)
        await mongo.close()


@pytest.mark.parametrize("birth", [BIRTH, {**BIRTH, "year": 1995, "month": 8, "day": 12, "hour": 14, "gender": "F"}])
async def test_analysis_charges_once_per_chart_and_reuses_the_saved_report(analysis, birth):
    first = await analysis.client.post(URL, json=birth)
    second = await analysis.client.post(URL, json=birth)

    assert first.status_code == second.status_code == 200
    assert first.json() == second.json() == PROFILE.model_dump(mode="json")
    assert first.json()["diem_manh"][0]["nang_luc"]
    analysis.run.assert_awaited_once()
    args = analysis.run.call_args.kwargs
    expected = routes._build_la_so(routes.BuildLasoRequest.model_validate(birth))
    assert args["agent"] is analysis.agent
    assert args["deps"] is not analysis.base_deps
    assert args["deps"].la_so.prior == expected.prior
    assert analysis.base_deps.la_so is None
    assert await _account(analysis) == {"balance": 0, "holds": {}}


async def test_new_chart_without_enough_coins_is_rejected_before_ai_runs(analysis):
    await analysis.client.post(URL, json=BIRTH)

    response = await analysis.client.post(URL, json={**BIRTH, "gender": "F"})

    assert response.status_code == 402
    analysis.run.assert_awaited_once()
    assert await _account(analysis) == {"balance": 0, "holds": {}}


async def test_failed_analysis_refunds_the_coins(analysis):
    analysis.run.side_effect = RuntimeError("model failed")

    with pytest.raises(RuntimeError):
        await analysis.client.post(URL, json=BIRTH)

    assert await _account(analysis) == {"balance": CAPABILITY_REPORT_COST, "holds": {}}
    assert await analysis.database["capability_reports"].count_documents({}) == 0


async def test_full_unlock_gets_the_analysis_without_coins(analysis):
    await analysis.database["user"].update_one(
        {"_id": ObjectId(analysis.user_id)}, {"$set": {"plan": "full_unlock", "balance": 0}}
    )

    response = await analysis.client.post(URL, json=BIRTH)

    assert response.status_code == 200
    assert await _account(analysis) == {"balance": 0, "holds": {}}


async def test_analysis_requires_sign_in(analysis):
    response = await analysis.client.post(URL, json=BIRTH, headers={"Authorization": ""})

    assert response.status_code == 401
    analysis.run.assert_not_called()


async def test_invalid_date_is_rejected_before_charging(analysis):
    response = await analysis.client.post(URL, json={**BIRTH, "month": 2, "day": 31})

    assert response.status_code == 422
    analysis.run.assert_not_called()
    assert await _account(analysis) == {"balance": CAPABILITY_REPORT_COST, "holds": {}}


async def test_running_analysis_blocks_a_second_charge_until_its_hold_is_stale(analysis):
    hold_path = f"capability_holds.{capability_chart_key(BirthInfo.model_validate(BIRTH))}"
    await analysis.database["user"].update_one(
        {"_id": ObjectId(analysis.user_id)},
        {
            "$set": {
                "balance": 0,
                hold_path: {
                    "amount": CAPABILITY_REPORT_COST,
                    "attempt": "earlier",
                    "started_at": datetime.now(UTC),
                },
            }
        },
    )

    busy = await analysis.client.post(URL, json=BIRTH)

    assert busy.status_code == 409
    analysis.run.assert_not_called()

    await analysis.database["user"].update_one(
        {"_id": ObjectId(analysis.user_id)},
        {
            "$set": {
                f"{hold_path}.started_at": datetime.now(UTC)
                - STALE_HOLD_AFTER
                - timedelta(minutes=1)
            }
        },
    )

    resumed = await analysis.client.post(URL, json=BIRTH)

    assert resumed.status_code == 200
    assert await _account(analysis) == {"balance": 0, "holds": {}}


async def _account(analysis) -> dict:
    account = await analysis.database["user"].find_one(
        {"_id": ObjectId(analysis.user_id)}, {"balance": 1, "capability_holds": 1}
    )
    return {"balance": account["balance"], "holds": account.get("capability_holds", {})}
