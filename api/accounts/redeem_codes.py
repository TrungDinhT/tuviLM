from __future__ import annotations

import secrets
from datetime import UTC, datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError
from pymongo import ReturnDocument
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import PyMongoError
from pymongo.write_concern import WriteConcern

from api.accounts.models import (
    AccountAccess,
    RedeemCode,
    RedeemCodeCreate,
    RedeemCodeInput,
    RedeemCodeResult,
)
from api.auth.dependencies import CurrentUser, require_admin


router = APIRouter(prefix="/api/v1")


async def ensure_redeem_code_indexes(database: AsyncDatabase) -> None:
    await database["redeem_codes"].create_index("expires_at", expireAfterSeconds=0)


@router.post(
    "/admin/redeem-codes",
    status_code=201,
    response_model=RedeemCode,
    dependencies=[Depends(require_admin)],
)
async def create_redeem_code(payload: RedeemCodeCreate, request: Request) -> RedeemCode:
    code = RedeemCode(code=secrets.token_hex(12).upper(), **payload.model_dump())
    document = code.model_dump(exclude={"code"})
    document.update(_id=code.code, created_at=datetime.now(UTC), redeemed_by=[])
    try:
        await request.app.state.auth_database["redeem_codes"].insert_one(document)
    except PyMongoError as exc:
        raise HTTPException(503, "Account service unavailable.") from exc
    return code


@router.post("/account/redeem-code", response_model=RedeemCodeResult)
async def redeem_code(
    payload: RedeemCodeInput, request: Request, user: CurrentUser
) -> RedeemCodeResult:
    database = request.app.state.auth_database

    async def apply(session: AsyncClientSession) -> RedeemCodeResult:
        now = datetime.now(UTC)
        code = await database["redeem_codes"].find_one_and_update(
            {
                "_id": payload.code,
                "expires_at": {"$gt": now},
                "redeemed_by": {"$ne": user.user_id},
                "$or": [
                    {"kind": "per_account"},
                    {"kind": "single_use", "redeemed_by": {"$size": 0}},
                ],
            },
            {"$push": {"redeemed_by": user.user_id}},
            return_document=ReturnDocument.AFTER,
            session=session,
        )
        if code is None:
            exists = await database["redeem_codes"].find_one(
                {"_id": payload.code, "expires_at": {"$gt": now}},
                {"_id": 1},
                session=session,
            )
            if exists:
                raise HTTPException(409, "Code already redeemed.")
            raise HTTPException(404, "Code is invalid or expired.")

        reward = RedeemCodeResult(coins=code["coins"])
        account = await database["user"].find_one(
            {"_id": ObjectId(user.user_id)},
            {"plan": 1, "balance": 1, "chat_holds": 1},
            session=session,
        )
        if account is None:
            raise HTTPException(401, "Authentication required or session expired.")
        access = AccountAccess.model_validate(account)
        if account.get("chat_holds"):
            raise HTTPException(
                409, "Chat coins are reserved. Try again when the reply finishes."
            )
        if access.balance > 9_007_199_254_740_991 - reward.coins:
            raise HTTPException(409, "Balance limit exceeded.")
        await database["user"].update_one(
            {"_id": account["_id"]},
            {"$inc": {"balance": reward.coins}},
            session=session,
        )
        return reward

    try:
        async with database.client.start_session() as session:
            return await session.with_transaction(
                apply, write_concern=WriteConcern("majority")
            )
    except (PyMongoError, ValidationError) as exc:
        raise HTTPException(503, "Account service unavailable.") from exc
