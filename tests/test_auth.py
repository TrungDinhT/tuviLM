"""Login, sessions and the account dependencies, against a throwaway MongoDB database."""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Annotated
from unittest.mock import AsyncMock
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

import httpx
import pytest
from bson import ObjectId
from fastapi import Depends, FastAPI
from pymongo import AsyncMongoClient
from pymongo.errors import ServerSelectionTimeoutError

from tuvi_api.auth import dependencies, google
from tuvi_api.auth import routes as auth_routes
from tuvi_api.auth.dependencies import (
    OAUTH_STATE_COOKIE,
    SESSION_COOKIE,
    Principal,
    get_auth_settings,
    require_admin,
    require_user,
)
from tuvi_api.auth.email import EmailMessage, reset_password_email, verification_email
from tuvi_api.auth.passwords import hash_token, verify_better_auth_password
from tuvi_api.auth.rate_limit import RateLimiter
from tuvi_api.auth.routes import router as auth_router
from tuvi_api.auth.settings import AuthSettings
from tuvi_api.auth.store import MongoAuthStore
from tuvi_api.chat.routes import router as chat_router
from tuvi_api.main import me

pytestmark = pytest.mark.anyio

BASE_URL = "http://testserver"
PASSWORD = "mật khẩu dài 2026"
# Made by Better Auth 1.6 (`hashPassword` from @better-auth/utils) for this password.
BETTER_AUTH_PASSWORD = "Mật khẩu cũ 2026"
BETTER_AUTH_HASH = (
    "9ee61e625fccceba83e97a0040525c48:01dae5c6765dde3bec4020017e7bbb1a9d5096c1ff711a83"
    "605bec84f6b49474bde2043c506e1a8bc1c521539153fc6c3bc104ccfe6528edad001278088f11f7"
)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture()
async def auth(monkeypatch):
    uri = os.environ.get("CONVERSATION_HISTORY_STORE__URI", "mongodb://localhost:27017")
    mongo = AsyncMongoClient(uri, serverSelectionTimeoutMS=300, tz_aware=True)
    try:
        await mongo.admin.command("ping")
    except ServerSelectionTimeoutError as exc:
        await mongo.close()
        pytest.skip(f"MongoDB is not available at {uri}: {exc}")

    database_name = f"tuvilm_auth_test_{uuid4().hex}"
    database = mongo[database_name]
    await MongoAuthStore(database).ensure_indexes()

    sent: list[EmailMessage] = []

    async def capture(settings, message: EmailMessage) -> None:
        sent.append(message)

    monkeypatch.setattr(auth_routes, "send_email_logged", capture)

    settings = AuthSettings(
        base_url=BASE_URL,
        google_client_id="google-client",
        google_client_secret="google-secret",
    )
    app = FastAPI()
    app.state.auth_database = database
    app.state.auth_rate_limiter = RateLimiter()
    chat_store = SimpleNamespace(list_chart_profiles=AsyncMock(return_value=[]))
    app.state.api_state = SimpleNamespace(conversation_history_store=chat_store)
    app.dependency_overrides[get_auth_settings] = lambda: settings
    app.include_router(auth_router)
    app.include_router(chat_router)
    app.add_api_route("/api/v1/me", me)

    @app.get("/private")
    async def private(user: Annotated[Principal, Depends(require_user)]):
        return user

    @app.get("/admin")
    async def admin(user: Annotated[Principal, Depends(require_admin)]):
        return {"user_id": user.user_id}

    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url=BASE_URL
        ) as client:
            yield SimpleNamespace(
                client=client,
                database=database,
                store=MongoAuthStore(database),
                sent=sent,
                settings=settings,
                chat_store=chat_store,
            )
    finally:
        await mongo.drop_database(database_name)
        await mongo.close()


def _link(message: EmailMessage) -> str:
    return next(word for word in message.text.split() if word.startswith(BASE_URL))


def _token(url: str) -> str:
    return parse_qs(urlsplit(url).query)["token"][0]


async def _register(auth, email: str = "an@example.com", password: str = PASSWORD) -> str:
    """Register and verify; returns the account id. The client keeps the session cookie."""
    response = await auth.client.post(
        "/api/v1/auth/register", json={"email": email, "password": password, "name": "An"}
    )
    assert response.status_code == 202
    verify = await auth.client.get(_link(auth.sent[-1]).removeprefix(BASE_URL))
    assert verify.status_code == 302
    user = await auth.store.find_by_email(email)
    assert user is not None
    return user.id


# Registration and email verification


async def test_register_sends_a_link_and_needs_verification_before_login(auth) -> None:
    response = await auth.client.post(
        "/api/v1/auth/register",
        json={"email": " An@Example.com ", "password": PASSWORD, "name": " An "},
    )

    assert response.status_code == 202
    assert SESSION_COOKIE not in response.cookies
    [message] = auth.sent
    assert message.to == "an@example.com"
    assert "Chào An," in message.text
    link = _link(message)
    assert link.startswith(f"{BASE_URL}/api/v1/auth/verify-email?token=")

    login = await auth.client.post(
        "/api/v1/auth/login", json={"email": "an@example.com", "password": PASSWORD}
    )
    assert login.status_code == 403

    verify = await auth.client.get(link.removeprefix(BASE_URL))
    assert verify.status_code == 302
    assert verify.headers["location"] == f"{BASE_URL}/login"
    assert verify.cookies.get(SESSION_COOKIE)

    session = await auth.client.get("/api/v1/auth/session")
    assert session.json()["user"]["email"] == "an@example.com"
    assert session.json()["user"]["name"] == "An"
    assert session.json()["google_enabled"] is True

    again = await auth.client.get(link.removeprefix(BASE_URL))
    assert again.headers["location"] == f"{BASE_URL}/login?error=INVALID_TOKEN"


async def test_new_account_starts_with_the_normal_plan_and_no_coins(auth) -> None:
    await _register(auth)

    response = await auth.client.get("/private")

    assert response.status_code == 200
    assert response.json()["plan"] == "normal"
    assert response.json()["balance"] == 0
    assert response.json()["role"] == "user"


async def test_duplicate_email_is_rejected_case_insensitively(auth) -> None:
    await _register(auth)

    response = await auth.client.post(
        "/api/v1/auth/register",
        json={"email": "AN@example.com", "password": PASSWORD, "name": "Other"},
    )

    assert response.status_code == 409


@pytest.mark.parametrize(
    "body",
    [
        {"email": "an@example.com", "password": "short", "name": "An"},
        {"email": "not-an-email", "password": PASSWORD, "name": "An"},
        {"email": "an@example.com", "password": PASSWORD, "name": " A "},
    ],
)
async def test_register_validates_input(auth, body) -> None:
    response = await auth.client.post("/api/v1/auth/register", json=body)

    assert response.status_code == 422
    assert auth.sent == []


async def test_expired_verification_link_is_rejected(auth) -> None:
    await auth.client.post(
        "/api/v1/auth/register",
        json={"email": "an@example.com", "password": PASSWORD, "name": "An"},
    )
    token = _token(_link(auth.sent[-1]))
    await auth.database["auth_tokens"].update_one(
        {"token_hash": hash_token(token)},
        {"$set": {"expires_at": datetime.now(UTC) - timedelta(seconds=1)}},
    )

    response = await auth.client.get(f"/api/v1/auth/verify-email?token={token}")

    assert response.headers["location"] == f"{BASE_URL}/login?error=INVALID_TOKEN"
    assert SESSION_COOKIE not in response.cookies


async def test_resend_verification_answers_the_same_for_unknown_emails(auth) -> None:
    await auth.client.post(
        "/api/v1/auth/register",
        json={"email": "an@example.com", "password": PASSWORD, "name": "An"},
    )
    first_link = _link(auth.sent[-1])

    unknown = await auth.client.post(
        "/api/v1/auth/verification-email", json={"email": "nobody@example.com"}
    )
    known = await auth.client.post(
        "/api/v1/auth/verification-email", json={"email": "an@example.com"}
    )

    assert unknown.status_code == known.status_code == 202
    assert len(auth.sent) == 2
    # The new link replaces the first one.
    old = await auth.client.get(first_link.removeprefix(BASE_URL))
    assert old.headers["location"].endswith("error=INVALID_TOKEN")
    new = await auth.client.get(_link(auth.sent[-1]).removeprefix(BASE_URL))
    assert new.headers["location"] == f"{BASE_URL}/login"


# Login and logout


async def test_wrong_password_and_unknown_email_give_the_same_error(auth) -> None:
    await _register(auth)
    auth.client.cookies.clear()

    wrong = await auth.client.post(
        "/api/v1/auth/login", json={"email": "an@example.com", "password": "wrong password"}
    )
    unknown = await auth.client.post(
        "/api/v1/auth/login", json={"email": "nobody@example.com", "password": PASSWORD}
    )

    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


async def test_login_then_logout_ends_the_session(auth) -> None:
    await _register(auth)
    auth.client.cookies.clear()

    login = await auth.client.post(
        "/api/v1/auth/login", json={"email": "AN@example.com", "password": PASSWORD}
    )
    assert login.status_code == 200
    assert login.json()["user"]["email"] == "an@example.com"
    cookie = login.cookies[SESSION_COOKIE]
    assert (await auth.client.get("/private")).status_code == 200

    logout = await auth.client.post("/api/v1/auth/logout")
    assert logout.status_code == 204
    assert (await auth.client.get("/api/v1/auth/session")).json()["user"] is None

    # The old cookie no longer works, even if a client kept it.
    auth.client.cookies.set(SESSION_COOKIE, cookie)
    assert (await auth.client.get("/private")).status_code == 401


async def test_login_is_rate_limited_per_email(auth) -> None:
    for _ in range(10):
        await auth.client.post(
            "/api/v1/auth/login", json={"email": "an@example.com", "password": "wrong"}
        )

    response = await auth.client.post(
        "/api/v1/auth/login", json={"email": "an@example.com", "password": "wrong"}
    )
    other = await auth.client.post(
        "/api/v1/auth/login", json={"email": "binh@example.com", "password": "wrong"}
    )

    assert response.status_code == 429
    assert other.status_code == 401


async def test_better_auth_password_still_works_and_is_rehashed(auth) -> None:
    user_id = ObjectId()
    await auth.database["user"].insert_one(
        {
            "_id": user_id,
            "email": "cu@example.com",
            "name": "Cũ",
            "emailVerified": True,
            "role": "admin",
            "plan": "full_unlock",
            "balance": 12,
        }
    )
    await auth.database["account"].insert_one(
        {"userId": user_id, "providerId": "credential", "password": BETTER_AUTH_HASH}
    )

    wrong = await auth.client.post(
        "/api/v1/auth/login", json={"email": "cu@example.com", "password": PASSWORD}
    )
    right = await auth.client.post(
        "/api/v1/auth/login",
        json={"email": "cu@example.com", "password": BETTER_AUTH_PASSWORD},
    )

    assert wrong.status_code == 401
    assert right.status_code == 200
    account = await auth.database["user"].find_one({"_id": user_id})
    assert account["password_hash"].startswith("$argon2")
    assert (account["role"], account["plan"], account["balance"]) == ("admin", "full_unlock", 12)
    principal = await auth.client.get("/private")
    assert principal.json() == {
        "user_id": str(user_id),
        "role": "admin",
        "plan": "full_unlock",
        "balance": 12,
    }


def test_better_auth_hash_check() -> None:
    assert verify_better_auth_password(BETTER_AUTH_PASSWORD, BETTER_AUTH_HASH)
    assert not verify_better_auth_password(PASSWORD, BETTER_AUTH_HASH)
    assert not verify_better_auth_password(PASSWORD, "not-a-hash")


# Password reset


async def test_password_reset_sets_a_new_password_and_ends_old_sessions(auth) -> None:
    await _register(auth)
    old_cookie = auth.client.cookies[SESSION_COOKIE]
    auth.client.cookies.clear()

    unknown = await auth.client.post(
        "/api/v1/auth/forgot-password", json={"email": "nobody@example.com"}
    )
    known = await auth.client.post(
        "/api/v1/auth/forgot-password", json={"email": "an@example.com"}
    )
    assert unknown.status_code == known.status_code == 202
    link = _link(auth.sent[-1])
    assert link.startswith(f"{BASE_URL}/reset-password?token=")
    assert auth.sent[-1].subject.startswith("Đặt lại mật khẩu")

    reset = await auth.client.post(
        "/api/v1/auth/reset-password",
        json={"token": _token(link), "password": "mật khẩu mới 2026"},
    )
    assert reset.status_code == 204

    reused = await auth.client.post(
        "/api/v1/auth/reset-password",
        json={"token": _token(link), "password": "another password"},
    )
    assert reused.status_code == 400
    assert reused.json() == {"detail": "INVALID_TOKEN"}

    auth.client.cookies.set(SESSION_COOKIE, old_cookie)
    assert (await auth.client.get("/private")).status_code == 401
    old = await auth.client.post(
        "/api/v1/auth/login", json={"email": "an@example.com", "password": PASSWORD}
    )
    new = await auth.client.post(
        "/api/v1/auth/login", json={"email": "an@example.com", "password": "mật khẩu mới 2026"}
    )
    assert old.status_code == 401
    assert new.status_code == 200


async def test_password_reset_verifies_the_email(auth) -> None:
    await auth.client.post(
        "/api/v1/auth/register",
        json={"email": "an@example.com", "password": PASSWORD, "name": "An"},
    )
    await auth.client.post("/api/v1/auth/forgot-password", json={"email": "an@example.com"})

    await auth.client.post(
        "/api/v1/auth/reset-password",
        json={"token": _token(_link(auth.sent[-1])), "password": PASSWORD},
    )
    login = await auth.client.post(
        "/api/v1/auth/login", json={"email": "an@example.com", "password": PASSWORD}
    )

    assert login.status_code == 200


async def test_forgot_password_is_rate_limited_per_email(auth) -> None:
    statuses = [
        (
            await auth.client.post(
                "/api/v1/auth/forgot-password", json={"email": "an@example.com"}
            )
        ).status_code
        for _ in range(4)
    ]

    assert statuses == [202, 202, 202, 429]


# Google sign-in


async def test_google_callback_signs_in_and_checks_the_state(auth, monkeypatch) -> None:
    monkeypatch.setattr(
        google,
        "exchange_code",
        AsyncMock(
            return_value=google.GoogleIdentity(
                sub="google-1", email="An@Example.com", display_name="An Google"
            )
        ),
    )
    start = await auth.client.get("/api/v1/auth/google/start")
    assert start.status_code == 302
    state = parse_qs(urlsplit(start.headers["location"]).query)["state"][0]

    forged = await auth.client.get(
        "/api/v1/auth/google/callback", params={"code": "c", "state": "forged"}
    )
    assert forged.headers["location"] == f"{BASE_URL}/login?error=google"

    response = await auth.client.get(
        "/api/v1/auth/google/callback", params={"code": "c", "state": state}
    )
    assert response.headers["location"] == f"{BASE_URL}/login"
    session = await auth.client.get("/api/v1/auth/session")
    assert session.json()["user"]["email"] == "an@example.com"
    assert session.json()["user"]["name"] == "An Google"
    assert OAUTH_STATE_COOKIE not in auth.client.cookies


async def test_google_takes_over_an_unverified_account_without_its_password(auth) -> None:
    await auth.client.post(
        "/api/v1/auth/register",
        json={"email": "an@example.com", "password": PASSWORD, "name": "Squatter"},
    )

    user = await auth.store.upsert_google_user(
        google_sub="google-1", email="an@example.com", name="An"
    )

    assert user.email_verified
    assert user.password_hash is None
    login = await auth.client.post(
        "/api/v1/auth/login", json={"email": "an@example.com", "password": PASSWORD}
    )
    assert login.status_code == 401


async def test_google_links_a_verified_account_and_keeps_its_password(auth) -> None:
    user_id = await _register(auth)

    user = await auth.store.upsert_google_user(
        google_sub="google-1", email="an@example.com", name="An"
    )
    again = await auth.store.upsert_google_user(
        google_sub="google-1", email="changed@example.com", name="An"
    )

    assert user.id == again.id == user_id
    assert user.password_hash is not None


# The account dependencies


async def test_account_access_uses_live_values(auth) -> None:
    user_id = await _register(auth)

    await auth.database["user"].update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"plan": "full_unlock", "balance": 40}}
    )
    response = await auth.client.get("/api/v1/me")

    assert response.json() == {
        "user_id": user_id,
        "role": "user",
        "plan": "full_unlock",
        "balance": 40,
    }


async def test_invalid_persisted_account_access_is_unavailable(auth) -> None:
    user_id = await _register(auth)
    await auth.database["user"].update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"balance": -1}}
    )

    response = await auth.client.get("/api/v1/me")

    assert response.status_code == 503
    assert response.json() == {"detail": "Account data unavailable."}


async def test_me_reconciles_coin_holds_and_returns_updated_balance(auth, monkeypatch) -> None:
    user_id = await _register(auth)
    holds = {"assistant-id": {"amount": 3, "session_id": "session-id"}}
    await auth.database["user"].update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"chat_holds": holds}}
    )

    async def reconcile(database, owner_id, found_holds, store):
        await database["user"].update_one(
            {"_id": ObjectId(owner_id)}, {"$set": {"balance": 3, "chat_holds": {}}}
        )

    reconciler = AsyncMock(side_effect=reconcile)
    monkeypatch.setattr(dependencies, "reconcile_chat_coins", reconciler)

    response = await auth.client.get("/api/v1/me")

    assert response.status_code == 200
    assert response.json()["balance"] == 3
    reconciler.assert_awaited_once_with(auth.database, user_id, holds, auth.chat_store)


async def test_routes_without_coins_do_not_reconcile_coin_holds(auth, monkeypatch) -> None:
    user_id = await _register(auth)
    await auth.database["user"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"chat_holds": {"assistant-id": {"amount": 3, "session_id": "s"}}}},
    )
    reconciler = AsyncMock()
    monkeypatch.setattr(dependencies, "reconcile_chat_coins", reconciler)

    response = await auth.client.get("/private")

    assert response.status_code == 200
    reconciler.assert_not_awaited()


async def test_missing_cookie_and_anonymous_owner_are_unauthorized(auth) -> None:
    response = await auth.client.get(
        "/api/v1/chart-profiles", headers={"X-Anonymous-Owner-Id": str(ObjectId())}
    )

    assert response.status_code == 401
    auth.chat_store.list_chart_profiles.assert_not_awaited()


async def test_expired_session_is_unauthorized(auth) -> None:
    await _register(auth)
    await auth.database["auth_sessions"].update_many(
        {}, {"$set": {"expires_at": datetime.now(UTC) - timedelta(seconds=1)}}
    )

    assert (await auth.client.get("/private")).status_code == 401
    assert (await auth.client.get("/api/v1/auth/session")).json()["user"] is None


async def test_unknown_session_token_is_unauthorized(auth) -> None:
    auth.client.cookies.set(SESSION_COOKIE, "made-up")

    assert (await auth.client.get("/private")).status_code == 401


async def test_admin_guard_uses_the_live_role(auth) -> None:
    user_id = await _register(auth)
    users = auth.database["user"]

    assert (await auth.client.get("/admin")).status_code == 403
    await users.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": "admin"}})
    assert (await auth.client.get("/admin")).status_code == 200
    await users.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": "user"}})
    assert (await auth.client.get("/admin")).status_code == 403


# Email content


def test_emails_escape_the_name_and_carry_the_link() -> None:
    url = "https://thienhac.example/reset-password?token=abc&x=1"
    message = reset_password_email(to="an@example.com", name="<b>An</b>", url=url)

    assert f"Đặt lại mật khẩu: {url}" in message.text
    assert "Chào <b>An</b>," in message.text
    assert "&lt;b&gt;An&lt;/b&gt;" in message.html
    assert "<b>An</b>" not in message.html
    assert 'href="https://thienhac.example/reset-password?token=abc&amp;x=1"' in message.html
    assert "https://thienhac.example/assets/icons/android-chrome-192x192.png" in message.html


def test_email_without_a_name_greets_generically() -> None:
    message = verification_email(to="an@example.com", name="  ", url="https://x.example/v")

    assert message.text.startswith("Chào bạn,")
