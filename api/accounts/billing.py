from __future__ import annotations

from typing import Any

from bson import ObjectId
from fastapi import HTTPException
from pydantic import ValidationError
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import PyMongoError

from api.accounts.models import AccountAccess
from api.chat.contracts import ConversationHistoryStore, NotFoundError
from api.chat.models import ChatMessageStatus


CHAT_MESSAGE_COST = 3


async def reserve_chat_coins(
    database: AsyncDatabase,
    user_id: str,
    session_id: str,
    assistant_message_id: str,
) -> None:
    hold_path = f"chat_holds.{assistant_message_id}"
    try:
        result = await database["user"].update_one(
            {
                "_id": ObjectId(user_id),
                "$or": [{"plan": "normal"}, {"plan": {"$exists": False}}],
                "balance": {
                    "$type": ["int", "long"],
                    "$gte": CHAT_MESSAGE_COST,
                    "$lte": 9_007_199_254_740_991,
                },
                hold_path: {"$exists": False},
            },
            {
                "$inc": {"balance": -CHAT_MESSAGE_COST},
                "$set": {
                    hold_path: {
                        "amount": CHAT_MESSAGE_COST,
                        "session_id": session_id,
                    }
                },
            },
        )
        if result.matched_count:
            return
        user = await database["user"].find_one(
            {"_id": ObjectId(user_id)}, {"plan": 1, "balance": 1, hold_path: 1}
        )
    except PyMongoError as exc:
        raise HTTPException(503, "Account service unavailable.") from exc
    if user is None:
        raise HTTPException(401, "Authentication required or session expired.")
    try:
        access = AccountAccess.model_validate(user)
    except ValidationError as exc:
        raise HTTPException(503, "Account data unavailable.") from exc
    if access.plan == "full_unlock" or assistant_message_id in user.get("chat_holds", {}):
        return
    raise HTTPException(402, "Not enough coins. AI chat costs 3 coins per message.")


async def settle_chat_coins(
    database: AsyncDatabase,
    user_id: str,
    assistant_message_id: str,
    *,
    confirmed: bool,
) -> None:
    hold_path = f"chat_holds.{assistant_message_id}"
    update: dict[str, Any] = {"$unset": {hold_path: ""}}
    if not confirmed:
        update["$inc"] = {"balance": CHAT_MESSAGE_COST}
    try:
        await database["user"].update_one(
            {"_id": ObjectId(user_id), f"{hold_path}.amount": CHAT_MESSAGE_COST},
            update,
        )
    except PyMongoError as exc:
        raise HTTPException(503, "Account service unavailable.") from exc


async def reconcile_chat_coins(
    database: AsyncDatabase,
    user_id: str,
    holds: dict[str, dict[str, Any]],
    store: ConversationHistoryStore,
) -> None:
    try:
        for assistant_message_id, hold in holds.items():
            try:
                context = await store.load_session_context(user_id, hold["session_id"])
            except NotFoundError:
                # Deleting the session does not refund the chat charge.
                confirmed = True
            else:
                message = next(
                    (
                        message
                        for message in context.session.messages
                        if message.id == assistant_message_id
                    ),
                    None,
                )
                if message is not None and message.status == ChatMessageStatus.PENDING:
                    continue
                confirmed = (
                    message is not None and message.status == ChatMessageStatus.CONFIRMED
                )
            await settle_chat_coins(
                database, user_id, assistant_message_id, confirmed=confirmed
            )
    except PyMongoError as exc:
        raise HTTPException(503, "Account service unavailable.") from exc
