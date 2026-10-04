from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Request
from pymongo import AsyncMongoClient

from api.auth.dependencies import Principal, require_user
from api.chat.contracts import ConversationHistoryError
from api.chat.models import CreateSessionInput
from api.chat.routes import router
from api.chat.storage import store as store_module
from api.chat.storage.store import MongoConversationHistoryStore
from api.main import conversation_history_exception_handler


pytestmark = pytest.mark.anyio
HEADERS = {"Authorization": "Bearer owner", "Idempotency-Key": "birth-profile"}
CREATE_BODY = {
    "display_name": "Me",
    "birth_info": {"year": 1996, "month": 4, "day": 15, "hour": 10, "gender": "M"},
}


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture()
async def rename_context():
    uri = os.environ.get("CONVERSATION_HISTORY_STORE__URI", "mongodb://localhost:27017")
    mongo = AsyncMongoClient(uri, serverSelectionTimeoutMS=500, tz_aware=True)
    database_name = f"tuvilm_chart_rename_test_{uuid4().hex}"
    database = mongo[database_name]
    store = MongoConversationHistoryStore(mongo_client=mongo, database_name=database_name)

    async def test_user(request: Request) -> Principal:
        token = request.headers.get("Authorization", "")
        if not token.startswith("Bearer ") or not token[7:].strip():
            raise HTTPException(401, "Authentication required.")
        return Principal(user_id=token[7:])

    app = FastAPI()
    app.include_router(router)
    app.add_exception_handler(ConversationHistoryError, conversation_history_exception_handler)
    app.dependency_overrides[require_user] = test_user
    app.state.api_state = SimpleNamespace(conversation_history_store=store)
    try:
        await store._initialize_storage()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            response = await client.post("/api/v1/chart-profiles", headers=HEADERS, json=CREATE_BODY)
            assert response.status_code == 200
            yield client, database, store, response.json()["chart_profile"]
    finally:
        try:
            await mongo.drop_database(database_name)
        finally:
            await store.close()


async def test_rename_requires_login_and_owned_live_profile(rename_context):
    client, database, store, profile = rename_context
    path = f"/api/v1/chart-profiles/{profile['id']}"
    for headers, status in [({}, 401), ({"Authorization": "Bearer other"}, 404)]:
        response = await client.patch(path, headers=headers, json={"display_name": "Changed"})
        assert response.status_code == status
    for missing_id in ("invalid-id", str(ObjectId())):
        response = await client.patch(
            f"/api/v1/chart-profiles/{missing_id}", headers=HEADERS,
            json={"display_name": "Changed"},
        )
        assert response.status_code == 404
    assert (await database["chart_profiles"].find_one({"_id": ObjectId(profile["id"])}))["display_name"] == "Me"
    await store.delete_chart_profile("owner", profile["id"])
    assert (await client.patch(path, headers=HEADERS, json={"display_name": "Changed"})).status_code == 404


async def test_rename_rejects_empty_long_and_unexpected_fields(rename_context):
    client, database, _, profile = rename_context
    path = f"/api/v1/chart-profiles/{profile['id']}"
    before = await database["chart_profiles"].find_one({"_id": ObjectId(profile["id"])})
    for payload in [
        {}, {"display_name": " \t "}, {"display_name": "a" * 81},
        {"display_name": "Changed", "birth_info": CREATE_BODY["birth_info"]},
    ]:
        assert (await client.patch(path, headers=HEADERS, json=payload)).status_code == 422
    assert await database["chart_profiles"].find_one({"_id": before["_id"]}) == before


async def test_rename_persists_without_changing_birth_sessions_or_recast(rename_context):
    client, database, store, profile = rename_context
    profile_id = ObjectId(profile["id"])
    await database["chart_profiles"].update_one(
        {"_id": profile_id}, {"$set": {"updated_at": datetime.now(UTC) - timedelta(days=1)}}
    )
    before = await database["chart_profiles"].find_one({"_id": profile_id})
    session = await store.create_session(
        "owner", profile["id"], CreateSessionInput(title="Existing conversation"),
        idempotency_key="session",
    )
    session_before = await database["sessions"].find_one({"_id": ObjectId(session.id)})
    response = await client.patch(
        f"/api/v1/chart-profiles/{profile['id']}", headers=HEADERS,
        json={"display_name": "  Family chart  "},
    )
    assert response.status_code == 200
    renamed = response.json()["chart_profile"]
    assert renamed["display_name"] == "Family chart"
    after = await database["chart_profiles"].find_one({"_id": profile_id})
    assert after["updated_at"] > before["updated_at"]
    assert after | {
        "display_name": before["display_name"], "name_key": before["name_key"],
        "updated_at": before["updated_at"],
    } == before
    assert await database["sessions"].find_one({"_id": ObjectId(session.id)}) == session_before
    listed = await client.get("/api/v1/chart-profiles", headers=HEADERS)
    assert listed.json()["chart_profiles"] == [renamed]
    recast = await client.post("/api/v1/chart-profiles", headers=HEADERS, json=CREATE_BODY)
    assert recast.status_code == 200
    assert recast.json()["chart_profile"] == renamed


async def test_rename_does_not_restore_a_profile_deleted_after_owner_check(rename_context, monkeypatch):
    client, database, _, profile = rename_context
    original = store_module._require_chart_profile

    async def delete_after_owner_check(owner_id, chart_profile_id):
        document = await original(owner_id, chart_profile_id)
        await document.delete()
        return document

    monkeypatch.setattr(store_module, "_require_chart_profile", delete_after_owner_check)
    response = await client.patch(
        f"/api/v1/chart-profiles/{profile['id']}", headers=HEADERS,
        json={"display_name": "Changed"},
    )
    assert response.status_code == 404
    document = await database["chart_profiles"].find_one({"_id": ObjectId(profile["id"])})
    assert document["display_name"] == "Me" and document["deleted_at"] is not None


async def test_legacy_names_are_backfilled_once_without_changing_chart_data(rename_context, monkeypatch):
    client, database, store, profile = rename_context
    source = await database["chart_profiles"].find_one({"_id": ObjectId(profile["id"])})
    legacy_names = ["Lá số 1", "Family", "family", "Family (2)", " 15/04/1996 ", " mai   ", "mai "]
    documents = [source | {"_id": ObjectId(), "display_name": name, "creation_idempotency_key": f"legacy-{index}"}
                 for index, name in enumerate(legacy_names)]
    for document in documents:
        document.pop("name_key")
    documents[5]["name_key"] = "mai"
    documents[0]["deleted_at"] = source["updated_at"]
    await database["chart_profiles"].insert_many(documents)
    await store._initialize_storage()
    expected = ["Lá số 1", "Family", "family (3)", "Family (2)", "Lá số 2", "mai", "mai (2)"]
    for before, name in zip(documents, expected):
        after = await database["chart_profiles"].find_one({"_id": before["_id"]})
        assert after["display_name"] == name
        assert after["name_key"] == store_module._name_key(name)
        assert after | {"display_name": before["display_name"]} == before | {"name_key": after["name_key"]}
    snapshot = await database["chart_profiles"].find({}).to_list()
    await store._initialize_storage()
    assert await database["chart_profiles"].find({}).to_list() == snapshot
    assert store_module._name_key("  CAFE\u0301   Nhà ") == "café nhà"
    original = store_module._require_chart_profile

    async def rename_after_lookup(owner_id, chart_profile_id):
        stale = await original(owner_id, chart_profile_id)
        await database["chart_profiles"].update_one(
            {"_id": stale.id}, {"$set": {"display_name": "Renamed", "name_key": "renamed"}}
        )
        response = await client.post("/api/v1/chart-profiles", headers=HEADERS | {"Idempotency-Key": "reuse-name"}, json=CREATE_BODY)
        assert response.status_code == 200 and response.json()["chart_profile"]["display_name"] == "Me"
        return stale

    monkeypatch.setattr(store_module, "_require_chart_profile", rename_after_lookup)
    await store.delete_chart_profile("owner", profile["id"])
    deleted = await database["chart_profiles"].find_one({"_id": source["_id"]})
    assert deleted["deleted_at"] is not None and deleted["display_name"] == "Renamed"


async def test_concurrent_numbered_creates_and_long_renames_preserve_recast_and_restore(rename_context):
    client, database, store, profile = rename_context
    payloads = [{"display_name": f"{day:02d}/04/1996", "birth_info": CREATE_BODY["birth_info"] | {"day": day}}
                for day in (16, 17)]
    headers = [HEADERS | {"Idempotency-Key": f"default-{index}"} for index in range(2)]
    created = await asyncio.gather(*(client.post("/api/v1/chart-profiles", headers=auth, json=payload)
                                    for auth, payload in zip(headers, payloads)))
    assert all(response.status_code == 200 for response in created)
    defaults = [response.json()["chart_profile"] for response in created]
    assert {item["display_name"] for item in defaults} == {"Lá số 1", "Lá số 2"}
    profiles = [profile, *defaults]
    long_name = "a" * 80
    renamed = await asyncio.gather(*(client.patch(f"/api/v1/chart-profiles/{item['id']}", headers=HEADERS,
                                                  json={"display_name": long_name}) for item in profiles))
    assert all(response.status_code == 200 for response in renamed)
    names = [response.json()["chart_profile"]["display_name"] for response in renamed]
    assert set(names) == {long_name, "a" * 76 + " (2)", "a" * 76 + " (3)"}
    winner = names.index(long_name)
    winner_id = profiles[winner]["id"]
    await store.delete_chart_profile("owner", winner_id)
    other_id = profiles[(winner + 1) % len(profiles)]["id"]
    response = await client.patch(f"/api/v1/chart-profiles/{other_id}", headers=HEADERS, json={"display_name": long_name})
    assert response.status_code == 200 and response.json()["chart_profile"]["display_name"] != long_name
    for _ in range(2):
        restored = await client.post("/api/v1/chart-profiles", headers=[HEADERS, *headers][winner],
                                     json=[CREATE_BODY, *payloads][winner])
        assert restored.status_code == 200
        assert restored.json()["chart_profile"]["id"] == winner_id
        assert restored.json()["chart_profile"]["display_name"] == long_name
    for name in ("mai", "mai ", "mai   "):
        response = await client.patch(f"/api/v1/chart-profiles/{winner_id}", headers=HEADERS,
                                      json={"display_name": name})
        assert response.status_code == 200 and response.json()["chart_profile"]["display_name"] == "mai"
        stored = await database["chart_profiles"].find_one({"_id": ObjectId(winner_id)})
        assert stored["display_name"] == stored["name_key"] == "mai"
    duplicate = await client.patch(f"/api/v1/chart-profiles/{other_id}", headers=HEADERS,
                                   json={"display_name": "mai   "})
    assert duplicate.status_code == 200 and duplicate.json()["chart_profile"]["display_name"] == "mai (2)"
    assert await database["chart_profiles"].count_documents({}) == 3
