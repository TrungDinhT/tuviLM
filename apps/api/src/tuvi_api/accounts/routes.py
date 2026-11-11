from __future__ import annotations

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError
from pymongo import ReturnDocument
from pymongo.errors import PyMongoError

from api.accounts.models import AccountAccess, AccountAccessUpdate
from api.auth.dependencies import require_admin


router = APIRouter(prefix="/api/v1/admin/users", dependencies=[Depends(require_admin)])


@router.patch("/{user_id}/access", response_model=AccountAccess)
async def update_account_access(
    user_id: str, payload: AccountAccessUpdate, request: Request
) -> AccountAccess:
    if not ObjectId.is_valid(user_id):
        raise HTTPException(404, "User not found.")

    query = {"_id": ObjectId(user_id)}
    if "balance" in payload.model_fields_set:
        query["$or"] = [
            {"chat_holds": {"$exists": False}},
            {"chat_holds": {}},
        ]
    try:
        user = await request.app.state.auth_database["user"].find_one_and_update(
            query,
            {"$set": payload.model_dump(exclude_unset=True)},
            projection={"plan": 1, "balance": 1},
            return_document=ReturnDocument.AFTER,
        )
        if user is None and await request.app.state.auth_database["user"].find_one(
            {"_id": ObjectId(user_id)}, {"_id": 1}
        ):
            raise HTTPException(
                409, "Cannot change balance while chat coins are reserved."
            )
    except PyMongoError as exc:
        raise HTTPException(503, "Account service unavailable.") from exc

    if user is None:
        raise HTTPException(404, "User not found.")
    try:
        return AccountAccess.model_validate(user)
    except ValidationError as exc:
        raise HTTPException(503, "Account data unavailable.") from exc
