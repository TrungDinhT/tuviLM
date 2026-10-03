from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Annotated
from unittest.mock import AsyncMock, Mock

import jwt
import pytest
from bson import ObjectId
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from api.auth import dependencies
from api.auth.dependencies import Principal, require_admin, require_user
from api.chat.routes import router as chat_router


ISSUER = "http://localhost:3000"
USER_ID = ObjectId()
SESSION_ID = ObjectId()


class AuthCollection:
    def __init__(self, document: dict | None):
        self.document = document
        self.queries: list[dict] = []

    async def find_one(self, query: dict, projection=None):
        self.queries.append(query)
        if self.document is None:
            return None
        for field, expected in query.items():
            actual = self.document.get(field)
            if isinstance(expected, dict):
                if actual is None or actual <= expected["$gt"]:
                    return None
            elif actual != expected:
                return None
        return self.document.copy()


@pytest.fixture()
def auth_context(monkeypatch):
    private_key = Ed25519PrivateKey.generate()
    signing_key = jwt.PyJWK.from_dict(
        json.loads(jwt.algorithms.OKPAlgorithm.to_jwk(private_key.public_key()))
    )
    jwks = Mock(spec=jwt.PyJWKClient)
    jwks.get_signing_key_from_jwt.return_value = signing_key
    now = datetime.now(UTC)
    database = {
        "session": AuthCollection(
            {
                "_id": SESSION_ID,
                "userId": USER_ID,
                "expiresAt": now + timedelta(days=1),
            }
        ),
        "user": AuthCollection({"_id": USER_ID}),
    }
    monkeypatch.setattr(
        dependencies,
        "get_settings",
        lambda: SimpleNamespace(auth=SimpleNamespace(base_url=ISSUER)),
    )
    app = FastAPI()
    app.state.auth_jwks = jwks
    app.state.auth_database = database
    store = SimpleNamespace(list_chart_profiles=AsyncMock(return_value=[]))
    app.state.api_state = SimpleNamespace(conversation_history_store=store)
    app.include_router(chat_router)

    @app.get("/private")
    async def private(user: Annotated[Principal, Depends(require_user)]):
        return {"user_id": user.user_id, "role": user.role}

    @app.get("/admin")
    async def admin(user: Annotated[Principal, Depends(require_admin)]):
        return {"user_id": user.user_id}

    with TestClient(app) as client:
        yield SimpleNamespace(
            client=client,
            private_key=private_key,
            jwks=jwks,
            database=database,
            store=store,
            claims={
                "sub": str(USER_ID),
                "sid": str(SESSION_ID),
                "iss": ISSUER,
                "aud": "tuvilm-api",
                "iat": int(now.timestamp()),
                "exp": int((now + timedelta(minutes=5)).timestamp()),
            },
        )


def bearer(auth_context) -> dict[str, str]:
    token = jwt.encode(
        auth_context.claims,
        auth_context.private_key,
        algorithm="EdDSA",
        headers={"kid": "test-key"},
    )
    return {"Authorization": f"Bearer {token}"}


def test_valid_token_resolves_current_user_and_session(auth_context) -> None:
    response = auth_context.client.get("/private", headers=bearer(auth_context))

    assert response.status_code == 200
    assert response.json() == {"user_id": str(USER_ID), "role": "user"}
    assert auth_context.database["session"].queries[0]["_id"] == SESSION_ID
    assert auth_context.database["session"].queries[0]["userId"] == USER_ID
    assert auth_context.database["user"].queries == [{"_id": USER_ID}]


def test_missing_token_and_anonymous_owner_are_unauthorized(auth_context) -> None:
    response = auth_context.client.get(
        "/api/v1/chart-profiles", headers={"X-Anonymous-Owner-Id": str(USER_ID)}
    )

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert auth_context.database["session"].queries == []
    auth_context.store.list_chart_profiles.assert_not_awaited()


def test_expired_token_is_unauthorized(auth_context) -> None:
    auth_context.claims["exp"] = 1

    response = auth_context.client.get("/private", headers=bearer(auth_context))

    assert response.status_code == 401
    assert auth_context.database["session"].queries == []


def test_forged_signature_is_unauthorized(auth_context) -> None:
    auth_context.private_key = Ed25519PrivateKey.generate()

    response = auth_context.client.get("/private", headers=bearer(auth_context))

    assert response.status_code == 401
    assert auth_context.database["session"].queries == []


@pytest.mark.parametrize("failure", ["revoked", "wrong_owner"])
def test_session_must_be_active_and_belong_to_user(auth_context, failure) -> None:
    if failure == "revoked":
        auth_context.database["session"].document = None
    else:
        auth_context.database["session"].document["userId"] = ObjectId()

    response = auth_context.client.get("/private", headers=bearer(auth_context))

    assert response.status_code == 401


def test_admin_guard_uses_live_role_not_token_role(auth_context) -> None:
    auth_context.claims["role"] = "admin"
    headers = bearer(auth_context)

    assert auth_context.client.get("/admin", headers=headers).status_code == 403
    auth_context.database["user"].document["role"] = "admin"
    assert auth_context.client.get("/admin", headers=headers).status_code == 200
    auth_context.database["user"].document["role"] = "user"
    assert auth_context.client.get("/admin", headers=headers).status_code == 403
