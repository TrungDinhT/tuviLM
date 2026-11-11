"""Who is calling: the account behind the session cookie."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Annotated, Literal

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, Response
from pydantic import ValidationError
from pymongo.errors import PyMongoError

from tuvi_api.accounts.billing import reconcile_chat_coins
from tuvi_api.accounts.models import AccountAccess, Balance, Plan
from tuvi_api.auth.passwords import hash_token
from tuvi_api.auth.rate_limit import RateLimiter
from tuvi_api.auth.settings import AuthSettings
from tuvi_api.auth.store import MongoAuthStore
from tuvi_api.settings import get_settings

SESSION_COOKIE = "tuvi_session"
OAUTH_STATE_COOKIE = "tuvi_oauth_state"


@dataclass(frozen=True)
class Principal:
    user_id: str
    role: Literal["user", "admin"] = "user"
    plan: Plan = "normal"
    balance: Balance = 0


def get_auth_settings() -> AuthSettings:
    return get_settings().auth


def get_auth_store(request: Request) -> MongoAuthStore:
    return MongoAuthStore(request.app.state.auth_database)


def get_rate_limiter(request: Request) -> RateLimiter:
    return request.app.state.auth_rate_limiter


def _unauthorized() -> HTTPException:
    return HTTPException(status_code=401, detail="Authentication required or session expired.")


async def current_user_id(request: Request) -> str | None:
    """The account id behind the session cookie, or None for a guest."""
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    try:
        return await get_auth_store(request).session_user_id(
            hash_token(token), now=datetime.now(UTC)
        )
    except PyMongoError as exc:
        raise HTTPException(503, "Authentication service unavailable.") from exc


async def require_user(
    request: Request,
    user_id: Annotated[str | None, Depends(current_user_id)],
) -> Principal:
    if user_id is None:
        raise _unauthorized()
    database = request.app.state.auth_database
    try:
        user = await database["user"].find_one(
            {"_id": ObjectId(user_id)}, {"role": 1, "plan": 1, "balance": 1}
        )
        if user is None:
            raise _unauthorized()
        access = AccountAccess.model_validate(user)
    except PyMongoError as exc:
        raise HTTPException(503, "Authentication service unavailable.") from exc
    except ValidationError as exc:
        raise HTTPException(503, "Account data unavailable.") from exc
    return Principal(
        user_id=user_id,
        role="admin" if user.get("role") == "admin" else "user",
        plan=access.plan,
        balance=access.balance,
    )


CurrentUser = Annotated[Principal, Depends(require_user)]


async def require_reconciled_user(request: Request, user: CurrentUser) -> Principal:
    """Settle finished chat holds first, for routes that show or spend coins."""
    database = request.app.state.auth_database
    try:
        account = await database["user"].find_one(
            {"_id": ObjectId(user.user_id)}, {"chat_holds": 1}
        )
        if account is None:
            raise _unauthorized()
        if not account.get("chat_holds"):
            return user
        await reconcile_chat_coins(
            database,
            user.user_id,
            account["chat_holds"],
            request.app.state.api_state.conversation_history_store,
        )
        account = await database["user"].find_one(
            {"_id": ObjectId(user.user_id)}, {"plan": 1, "balance": 1}
        )
        if account is None:
            raise _unauthorized()
        access = AccountAccess.model_validate(account)
    except PyMongoError as exc:
        raise HTTPException(503, "Authentication service unavailable.") from exc
    except ValidationError as exc:
        raise HTTPException(503, "Account data unavailable.") from exc
    return replace(user, plan=access.plan, balance=access.balance)


ReconciledUser = Annotated[Principal, Depends(require_reconciled_user)]


def require_admin(user: CurrentUser) -> Principal:
    if user.role != "admin":
        raise HTTPException(403, "Administrator access required.")
    return user


def set_session_cookie(response: Response, token: str, settings: AuthSettings) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=settings.session_days * 24 * 3600,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


def clear_session_cookie(response: Response, settings: AuthSettings) -> None:
    response.delete_cookie(
        SESSION_COOKIE,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
