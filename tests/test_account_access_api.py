from __future__ import annotations

import os
from unittest.mock import AsyncMock
from uuid import uuid4

import httpx
import pytest
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from pymongo import AsyncMongoClient
from pymongo.errors import ServerSelectionTimeoutError

from api.accounts.routes import router
from api.auth.dependencies import Principal, require_user


ADMIN_HEADERS = {"Authorization": "Bearer admin"}
USER_ID = ObjectId()
ACCESS_PATH = f"/api/v1/admin/users/{USER_ID}/access"


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture()
def account_app():
    async def test_user(request: Request) -> Principal:
        token = request.headers.get("Authorization")
        if token == "Bearer admin":
            return Principal(user_id=str(ObjectId()), role="admin")
        if token == "Bearer user":
            return Principal(user_id=str(ObjectId()))
        raise HTTPException(401, "Authentication required.")

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[require_user] = test_user
    app.state.auth_database = {"user": AsyncMock(find_one_and_update=AsyncMock())}
    return app


@pytest.fixture()
async def account_client(account_app):
    uri = os.environ.get("CONVERSATION_HISTORY_STORE__URI", "mongodb://localhost:27017")
    mongo = AsyncMongoClient(uri, serverSelectionTimeoutMS=300)
    try:
        await mongo.admin.command("ping")
    except ServerSelectionTimeoutError as exc:
        await mongo.close()
        pytest.skip(f"MongoDB is not available at {uri}: {exc}")

    database_name = f"tuvilm_account_access_test_{uuid4().hex}"
    database = mongo[database_name]
    account_app.state.auth_database = database
    transport = httpx.ASGITransport(app=account_app)
    try:
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            yield client, database
    finally:
        await mongo.drop_database(database_name)
        await mongo.close()


@pytest.mark.parametrize(
    ("headers", "status"),
    [({}, 401), ({"Authorization": "Bearer user"}, 403)],
)
def test_access_update_requires_an_administrator(account_app, headers, status) -> None:
    with TestClient(account_app) as client:
        response = client.patch(ACCESS_PATH, headers=headers, json={"balance": 10})

    assert response.status_code == status
    account_app.state.auth_database["user"].find_one_and_update.assert_not_awaited()


def test_negative_balance_is_rejected_without_writing(account_app) -> None:
    with TestClient(account_app) as client:
        response = client.patch(ACCESS_PATH, headers=ADMIN_HEADERS, json={"balance": -1})

    assert response.status_code == 422
    account_app.state.auth_database["user"].find_one_and_update.assert_not_awaited()


@pytest.mark.anyio
async def test_partial_updates_preserve_other_account_fields(account_client) -> None:
    client, database = account_client
    await database["user"].insert_one(
        {"_id": USER_ID, "role": "user", "email": "user@example.test", "balance": 20}
    )

    response = await client.patch(
        ACCESS_PATH, headers=ADMIN_HEADERS, json={"plan": "full_unlock"}
    )
    assert response.status_code == 200
    assert response.json() == {"plan": "full_unlock", "balance": 20}

    response = await client.patch(ACCESS_PATH, headers=ADMIN_HEADERS, json={"balance": 5})
    assert response.status_code == 200
    assert response.json() == {"plan": "full_unlock", "balance": 5}
    assert await database["user"].find_one({"_id": USER_ID}) == {
        "_id": USER_ID,
        "role": "user",
        "email": "user@example.test",
        "plan": "full_unlock",
        "balance": 5,
    }


@pytest.mark.anyio
async def test_repeating_an_absolute_update_does_not_add_balance(account_client) -> None:
    client, database = account_client
    await database["user"].insert_one({"_id": USER_ID, "plan": "normal", "balance": 2})

    for _ in range(2):
        response = await client.patch(
            ACCESS_PATH,
            headers=ADMIN_HEADERS,
            json={"plan": "full_unlock", "balance": 37},
        )
        assert response.status_code == 200
        assert response.json() == {"plan": "full_unlock", "balance": 37}

    document = await database["user"].find_one({"_id": USER_ID})
    assert document["balance"] == 37


@pytest.mark.anyio
async def test_balance_update_is_blocked_during_chat_but_plan_update_is_allowed(
    account_client,
) -> None:
    client, database = account_client
    holds = {"assistant-id": {"amount": 3, "session_id": "session-id"}}
    await database["user"].insert_one(
        {"_id": USER_ID, "plan": "normal", "balance": 7, "chat_holds": holds}
    )

    response = await client.patch(
        ACCESS_PATH, headers=ADMIN_HEADERS, json={"balance": 100}
    )
    assert response.status_code == 409
    document = await database["user"].find_one({"_id": USER_ID})
    assert document["balance"] == 7
    assert document["chat_holds"] == holds

    response = await client.patch(
        ACCESS_PATH, headers=ADMIN_HEADERS, json={"plan": "full_unlock"}
    )
    assert response.status_code == 200
    assert response.json() == {"plan": "full_unlock", "balance": 7}


@pytest.mark.anyio
async def test_balance_update_is_allowed_after_chat_holds_are_cleared(
    account_client,
) -> None:
    client, database = account_client
    await database["user"].insert_one({"_id": USER_ID, "balance": 7, "chat_holds": {}})

    response = await client.patch(ACCESS_PATH, headers=ADMIN_HEADERS, json={"balance": 10})

    assert response.status_code == 200
    assert response.json() == {"plan": "normal", "balance": 10}


@pytest.mark.anyio
async def test_unknown_user_does_not_create_an_account(account_client) -> None:
    client, database = account_client

    response = await client.patch(
        ACCESS_PATH,
        headers=ADMIN_HEADERS,
        json={"balance": 10},
    )

    assert response.status_code == 404
    assert await database["user"].count_documents({}) == 0
