from __future__ import annotations

from typing import Any, Protocol

from pymongo import ASCENDING, DESCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError

from api.chat.contracts import DuplicateStreamInProgressError, IdempotencyConflictError, NotFoundError
from api.runs.models import RunRecord, now


class RunFinished(Exception):
    """An expired or completed run cannot accept more writes."""


class RunStore(Protocol):
    async def insert(self, run: RunRecord) -> RunRecord: ...
    async def get(self, run_id: str, owner_id: str) -> RunRecord: ...
    async def latest(self, owner_id: str, workflow: str, resource_id: str) -> RunRecord | None: ...
    async def write(self, run: RunRecord, changes: dict[str, Any]) -> RunRecord: ...
    async def cancel(self, run_id: str, owner_id: str) -> RunRecord: ...


class MongoRunStore:
    """Saved snapshots let any client reconnect without owning execution."""

    def __init__(self, database):
        self.collection = database["workflow_runs"]

    async def initialize(self) -> None:
        await self.collection.create_index(
            [("owner_id", ASCENDING), ("idempotency_key", ASCENDING)], unique=True,
        )
        await self.collection.create_index(
            [("owner_id", ASCENDING), ("resource_id", ASCENDING)],
            unique=True, partialFilterExpression={"active": True},
        )
        await self.collection.create_index([
            ("owner_id", ASCENDING), ("workflow", ASCENDING),
            ("resource_id", ASCENDING), ("created_at", DESCENDING),
        ])

    async def _expire(self, scope: dict) -> None:
        await self.collection.update_many(
            {**scope, "active": True, "$or": [
                {"expires_at": {"$lte": now()}},
                {"expires_at": None},  # Records from the removed worker implementation.
            ]},
            {"$set": {"active": False, "status": "failed", "updated_at": now(),
                      "error": "Workflow was interrupted or exceeded its time limit"},
             "$inc": {"seq": 1}},
        )

    @staticmethod
    def _record(document: dict | None) -> RunRecord:
        if document is None:
            raise NotFoundError
        return RunRecord.model_validate(document)

    async def insert(self, run: RunRecord) -> RunRecord:
        await self._expire({"owner_id": run.owner_id, "resource_id": run.resource_id})
        try:
            await self.collection.insert_one({"_id": run.id, **run.model_dump()})
            return run
        except DuplicateKeyError:
            existing = await self.collection.find_one({
                "owner_id": run.owner_id, "idempotency_key": run.idempotency_key,
            })
            if existing is None:
                raise DuplicateStreamInProgressError from None
            if existing["fingerprint"] != run.fingerprint:
                raise IdempotencyConflictError from None
            return self._record(existing)

    async def get(self, run_id: str, owner_id: str) -> RunRecord:
        scope = {"_id": run_id, "owner_id": owner_id}
        await self._expire(scope)
        return self._record(await self.collection.find_one(scope))

    async def latest(self, owner_id: str, workflow: str, resource_id: str) -> RunRecord | None:
        scope = {"owner_id": owner_id, "workflow": workflow, "resource_id": resource_id}
        await self._expire(scope)
        doc = await self.collection.find_one(scope, sort=[("created_at", DESCENDING), ("_id", DESCENDING)])
        return self._record(doc) if doc else None

    async def write(self, run: RunRecord, changes: dict[str, Any]) -> RunRecord:
        doc = await self.collection.find_one_and_update(
            {"_id": run.id, "owner_id": run.owner_id, "active": True, "expires_at": {"$gt": now()}},
            {"$set": {**changes, "updated_at": now()}, "$inc": {"seq": 1}},
            return_document=ReturnDocument.AFTER,
        )
        if doc is None:
            raise RunFinished
        return self._record(doc)

    async def cancel(self, run_id: str, owner_id: str) -> RunRecord:
        await self.collection.update_one(
            {"_id": run_id, "owner_id": owner_id, "active": True, "publishing": False},
            {"$set": {"cancel_requested": True, "updated_at": now()}, "$inc": {"seq": 1}},
        )
        return await self.get(run_id, owner_id)
