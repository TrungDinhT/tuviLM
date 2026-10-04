from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import httpx
import pytest
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Request
from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.errors import PyMongoError

from api.accounts.redeem_codes import ensure_redeem_code_indexes, router
from api.auth.dependencies import Principal, require_user


pytestmark = pytest.mark.anyio
ADMIN_HEADERS = {"Authorization": "Bearer admin"}
CREATE_PATH = "/api/v1/admin/redeem-codes"
REDEEM_PATH = "/api/v1/account/redeem-code"
USER_IDS = (ObjectId(), ObjectId())


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture()
async def redeem_client():
    uri = os.environ.get("CONVERSATION_HISTORY_STORE__URI", "mongodb://localhost:27017")
    mongo = AsyncMongoClient(uri, serverSelectionTimeoutMS=500, tz_aware=True)
    database_name = f"tuvilm_redeem_codes_test_{uuid4().hex}"
    database = mongo[database_name]

    async def test_user(request: Request) -> Principal:
        token = request.headers.get("Authorization", "")
        if token == "Bearer admin":
            return Principal(user_id=str(ObjectId()), role="admin")
        if token.startswith("Bearer ") and token[7:] in [str(user_id) for user_id in USER_IDS]:
            return Principal(user_id=token[7:])
        raise HTTPException(401, "Authentication required.")

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[require_user] = test_user
    app.state.auth_database = database
    try:
        hello = await mongo.admin.command("hello")
        assert hello.get("setName"), "Redemption tests require a MongoDB replica set."
        await ensure_redeem_code_indexes(database)
        await database["user"].insert_many([{"_id": user_id} for user_id in USER_IDS])
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            yield client, database
    finally:
        try:
            await mongo.drop_database(database_name)
        finally:
            await mongo.close()


async def create_code(client, kind="per_account"):
    response = await client.post(
        CREATE_PATH,
        headers=ADMIN_HEADERS,
        json={
            "coins": 30,
            "kind": kind,
            "expires_at": (datetime.now(UTC) + timedelta(days=3)).isoformat(),
        },
    )
    assert response.status_code == 201
    return response.json()


async def redeem(client, code, user_id=USER_IDS[0]):
    return await client.post(
        REDEEM_PATH,
        headers={"Authorization": f"Bearer {user_id}"},
        json={"code": code},
    )


async def test_creation_requires_admin_and_redemption_requires_login(redeem_client):
    client, database = redeem_client
    for headers, status in [({}, 401), ({"Authorization": f"Bearer {USER_IDS[0]}"}, 403)]:
        response = await client.post(CREATE_PATH, headers=headers, json={})
        assert response.status_code == status
    response = await client.post(REDEEM_PATH, json={"code": "UNKNOWN"})
    assert response.status_code == 401
    assert await database["redeem_codes"].count_documents({}) == 0


async def test_creation_validates_rewards_and_expiry_and_installs_ttl(redeem_client):
    client, database = redeem_client
    created = await create_code(client)
    assert set(created) == {"code", "coins", "kind", "expires_at"}
    assert created["coins"] == 30 and created["kind"] == "per_account"
    assert created["code"] == created["code"].upper()
    assert datetime.fromisoformat(created["expires_at"]) > datetime.now(UTC)
    indexes = await database["redeem_codes"].index_information()
    assert any(
        index["key"] == [("expires_at", 1)] and index.get("expireAfterSeconds") == 0
        for index in indexes.values()
    )
    payload = {key: value for key, value in created.items() if key != "code"}
    for invalid in [
        {"coins": 0},
        {"coins": True},
        {"coins": 9_007_199_254_740_992},
        {"kind": "unknown"},
        {"code": "CUSTOM"},
        {"expires_at": (datetime.now(UTC) - timedelta(days=1)).isoformat()},
        {"expires_at": (datetime.now() + timedelta(days=1)).isoformat()},
    ]:
        response = await client.post(
            CREATE_PATH, headers=ADMIN_HEADERS, json=payload | invalid
        )
        assert response.status_code == 422
    assert await database["redeem_codes"].count_documents({}) == 1


async def test_per_account_code_credits_each_account_once_under_concurrency(redeem_client):
    client, database = redeem_client
    code = (await create_code(client))["code"]
    responses = await asyncio.gather(
        redeem(client, f" {code.lower()} "), redeem(client, code)
    )
    assert sorted(response.status_code for response in responses) == [200, 409]
    success = next(response for response in responses if response.status_code == 200)
    assert success.json() == {"coins": 30}
    assert (await redeem(client, code, USER_IDS[1])).status_code == 200
    assert (await redeem(client, code, USER_IDS[1])).status_code == 409
    for user_id in USER_IDS:
        assert (await database["user"].find_one({"_id": user_id}))["balance"] == 30


async def test_single_use_code_has_only_one_winner_across_accounts(redeem_client):
    client, database = redeem_client
    code = (await create_code(client, "single_use"))["code"]
    responses = await asyncio.gather(
        *(redeem(client, code, user_id) for user_id in USER_IDS)
    )
    assert sorted(response.status_code for response in responses) == [200, 409]
    for user_id, response in zip(USER_IDS, responses):
        balance = (await database["user"].find_one({"_id": user_id})).get("balance", 0)
        assert balance == (30 if response.status_code == 200 else 0)
        assert (await redeem(client, code, user_id)).status_code == 409


async def test_missing_and_expired_codes_cannot_credit_coins(redeem_client):
    client, database = redeem_client
    code = (await create_code(client))["code"]
    await database["redeem_codes"].update_one(
        {"_id": code}, {"$set": {"expires_at": datetime.now(UTC) - timedelta(seconds=1)}}
    )
    for token in ("UNKNOWN", code):
        assert (await redeem(client, token)).status_code == 404
    assert (await database["user"].find_one({"_id": USER_IDS[0]})).get("balance", 0) == 0


async def test_failed_credit_rolls_back_code_claim_and_can_be_retried(redeem_client):
    client, database = redeem_client
    for access in [
        {"balance": 9_007_199_254_740_990, "chat_holds": {}},
        {"balance": 0, "chat_holds": {"reply": {"amount": 3, "session_id": "session"}}},
    ]:
        await database["user"].update_one({"_id": USER_IDS[0]}, {"$set": access})
        code = (await create_code(client, "single_use"))["code"]
        response = await redeem(client, code)
        assert response.status_code == 409
        if access["chat_holds"]:
            assert response.json()["detail"] == "Chat coins are reserved. Try again when the reply finishes."
        account = await database["user"].find_one({"_id": USER_IDS[0]})
        document = await database["redeem_codes"].find_one({"_id": code})
        assert account["balance"] == access["balance"]
        assert document["redeemed_by"] == []
        await database["user"].update_one(
            {"_id": USER_IDS[0]}, {"$set": {"balance": 0, "chat_holds": {}}}
        )
        assert (await redeem(client, code)).status_code == 200


async def test_database_failure_does_not_credit_or_consume_code(redeem_client, monkeypatch):
    client, database = redeem_client
    code = (await create_code(client, "single_use"))["code"]
    monkeypatch.setattr(
        AsyncCollection, "find_one_and_update", AsyncMock(side_effect=PyMongoError("Unavailable"))
    )
    assert (await redeem(client, code)).status_code == 503
    assert (await database["user"].find_one({"_id": USER_IDS[0]})).get("balance", 0) == 0
    assert (await database["redeem_codes"].find_one({"_id": code}))["redeemed_by"] == []
