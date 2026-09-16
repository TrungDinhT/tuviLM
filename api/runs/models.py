from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

RunStatus = Literal["queued", "running", "succeeded", "failed", "cancelled"]
TERMINAL = {"succeeded", "failed", "cancelled"}


def now() -> datetime:
    return datetime.now(UTC)


class RunSettings(BaseModel):
    concurrency: int = Field(default=2, ge=1, le=32)
    poll_seconds: float = Field(default=0.5, ge=0.05)
    timeout_seconds: float = Field(default=900, ge=1)


class RunState(BaseModel):
    text: str = ""
    progress: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RunSnapshot(BaseModel):
    id: str
    workflow: str
    resource_id: str
    inputs: dict[str, Any]
    status: RunStatus = "queued"
    state: RunState = Field(default_factory=RunState)
    result: Any = None
    error: str | None = None
    seq: int = 0
    cancel_requested: bool = False
    created_at: datetime
    updated_at: datetime


class RunRecord(RunSnapshot):
    owner_id: str
    idempotency_key: str
    fingerprint: str
    active: bool = True
    publishing: bool = False
    # A fixed timeout prevents abandoned records from blocking a resource forever.
    # Expired runs are failed, never restarted.
    expires_at: datetime | None = None

    def snapshot(self) -> RunSnapshot:
        return RunSnapshot.model_validate(self.model_dump())
