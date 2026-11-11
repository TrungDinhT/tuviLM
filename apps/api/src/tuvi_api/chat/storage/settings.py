from __future__ import annotations

from pydantic import BaseModel, Field


class MongoConversationHistorySettings(BaseModel):
    uri: str = "mongodb://localhost:27017"
    database_name: str = "tuvilm"
    tz_aware: bool = True
    stale_pending_after_seconds: int = Field(default=900, gt=0)
