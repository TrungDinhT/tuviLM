from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from bson import ObjectId
from fastapi import HTTPException
from pydantic import ValidationError
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import DuplicateKeyError, PyMongoError

from api.accounts.models import AccountAccess
from api.chat.models import BirthInfo
from src.agent.workflow.strength_weakness.output import CapabilityProfile


CAPABILITY_REPORT_COST = 10
# A hold this old belongs to a request that died mid-analysis; a retry takes it
# over instead of charging again.
STALE_HOLD_AFTER = timedelta(minutes=10)
_REPORTS = "capability_reports"


def capability_chart_key(birth: BirthInfo) -> str:
    return f"{birth.calendar}_{birth.year}_{birth.month}_{birth.day}_{birth.hour}_{birth.gender}"


async def ensure_capability_report_indexes(database: AsyncDatabase) -> None:
    await database[_REPORTS].create_index(
        [("user_id", 1), ("chart_key", 1)], unique=True
    )


async def find_capability_report(
    database: AsyncDatabase, user_id: str, chart_key: str
) -> CapabilityProfile | None:
    try:
        document = await database[_REPORTS].find_one(
            {"user_id": ObjectId(user_id), "chart_key": chart_key}, {"report": 1}
        )
    except PyMongoError as exc:
        raise HTTPException(503, "Account service unavailable.") from exc
    if document is None:
        return None
    return CapabilityProfile.model_validate(document["report"])


async def save_capability_report(
    database: AsyncDatabase, user_id: str, chart_key: str, report: CapabilityProfile
) -> None:
    try:
        await database[_REPORTS].update_one(
            {"user_id": ObjectId(user_id), "chart_key": chart_key},
            {
                "$setOnInsert": {
                    "report": report.model_dump(mode="json"),
                    "created_at": datetime.now(UTC),
                }
            },
            upsert=True,
        )
    except DuplicateKeyError:
        # A concurrent full_unlock request saved this chart's report first.
        return
    except PyMongoError as exc:
        raise HTTPException(503, "Account service unavailable.") from exc


async def reserve_capability_coins(
    database: AsyncDatabase, user_id: str, chart_key: str
) -> str | None:
    """Hold the report's coins. Returns the hold's attempt id, or None when free."""
    hold_path = f"capability_holds.{chart_key}"
    attempt = uuid4().hex
    now = datetime.now(UTC)
    try:
        result = await database["user"].update_one(
            {
                "_id": ObjectId(user_id),
                "$or": [{"plan": "normal"}, {"plan": {"$exists": False}}],
                "balance": {
                    "$type": ["int", "long"],
                    "$gte": CAPABILITY_REPORT_COST,
                    "$lte": 9_007_199_254_740_991,
                },
                hold_path: {"$exists": False},
            },
            {
                "$inc": {"balance": -CAPABILITY_REPORT_COST},
                "$set": {
                    hold_path: {
                        "amount": CAPABILITY_REPORT_COST,
                        "attempt": attempt,
                        "started_at": now,
                    }
                },
            },
        )
        if result.matched_count:
            return attempt
        result = await database["user"].update_one(
            {
                "_id": ObjectId(user_id),
                f"{hold_path}.started_at": {"$lt": now - STALE_HOLD_AFTER},
            },
            {"$set": {f"{hold_path}.attempt": attempt, f"{hold_path}.started_at": now}},
        )
        if result.matched_count:
            return attempt
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
    if access.plan == "full_unlock":
        return None
    if chart_key in user.get("capability_holds", {}):
        raise HTTPException(409, "Capability analysis already in progress for this chart.")
    raise HTTPException(
        402, f"Not enough coins. Capability analysis costs {CAPABILITY_REPORT_COST} coins."
    )


async def settle_capability_coins(
    database: AsyncDatabase,
    user_id: str,
    chart_key: str,
    attempt: str,
    *,
    confirmed: bool,
) -> None:
    hold_path = f"capability_holds.{chart_key}"
    update: dict[str, Any] = {"$unset": {hold_path: ""}}
    if not confirmed:
        update["$inc"] = {"balance": CAPABILITY_REPORT_COST}
    try:
        await database["user"].update_one(
            {
                "_id": ObjectId(user_id),
                f"{hold_path}.attempt": attempt,
                f"{hold_path}.amount": CAPABILITY_REPORT_COST,
            },
            update,
        )
    except PyMongoError as exc:
        raise HTTPException(503, "Account service unavailable.") from exc
