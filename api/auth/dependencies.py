from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated, Literal

import jwt
from bson import ObjectId
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError, PyJWKClientConnectionError, PyJWKClientError
from pydantic import ValidationError
from pymongo.errors import PyMongoError

from api.accounts.billing import reconcile_chat_coins
from api.accounts.models import AccountAccess, Balance, Plan
from api.settings import get_settings


@dataclass(frozen=True)
class Principal:
    user_id: str
    role: Literal["user", "admin"] = "user"
    plan: Plan = "normal"
    balance: Balance = 0


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Authentication required or session expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _verify_token(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(HTTPBearer(auto_error=False))
    ],
) -> dict[str, str]:
    if credentials is None:
        raise _unauthorized()

    try:
        key = request.app.state.auth_jwks.get_signing_key_from_jwt(credentials.credentials)
        claims = jwt.decode(
            credentials.credentials,
            key.key,
            algorithms=["EdDSA"],
            issuer=get_settings().auth.base_url.rstrip("/"),
            audience="tuvilm-api",
            options={"require": ["sub", "sid", "exp", "iss", "aud", "iat"]},
        )
    except PyJWKClientConnectionError as exc:
        raise HTTPException(503, "Authentication service unavailable.") from exc
    except (InvalidTokenError, PyJWKClientError) as exc:
        raise _unauthorized() from exc

    user_id, session_id = claims["sub"], claims["sid"]
    if not all(
        isinstance(value, str) and ObjectId.is_valid(value)
        for value in (user_id, session_id)
    ):
        raise _unauthorized()
    return {"sub": user_id, "sid": session_id}


async def require_user(
    request: Request,
    claims: Annotated[dict[str, str], Depends(_verify_token)],
) -> Principal:
    database = request.app.state.auth_database
    try:
        session = await database["session"].find_one(
            {
                "_id": ObjectId(claims["sid"]),
                "userId": ObjectId(claims["sub"]),
                "expiresAt": {"$gt": datetime.now(UTC)},
            },
            {"_id": 1},
        )
        if session is None:
            raise _unauthorized()
        user = await database["user"].find_one(
            {"_id": ObjectId(claims["sub"])},
            {"role": 1, "plan": 1, "balance": 1, "chat_holds": 1},
        )
        if user is None:
            raise _unauthorized()
        access = AccountAccess.model_validate(user)
        if user.get("chat_holds"):
            await reconcile_chat_coins(
                database,
                claims["sub"],
                user["chat_holds"],
                request.app.state.api_state.conversation_history_store,
            )
            user = await database["user"].find_one(
                {"_id": ObjectId(claims["sub"])}, {"role": 1, "plan": 1, "balance": 1}
            )
            if user is None:
                raise _unauthorized()
            access = AccountAccess.model_validate(user)
    except PyMongoError as exc:
        raise HTTPException(503, "Authentication service unavailable.") from exc
    except ValidationError as exc:
        raise HTTPException(503, "Account data unavailable.") from exc
    return Principal(
        user_id=claims["sub"],
        role="admin" if user.get("role") == "admin" else "user",
        plan=access.plan,
        balance=access.balance,
    )


CurrentUser = Annotated[Principal, Depends(require_user)]


def require_admin(user: CurrentUser) -> Principal:
    if user.role != "admin":
        raise HTTPException(403, "Administrator access required.")
    return user
