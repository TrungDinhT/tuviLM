from __future__ import annotations

from pydantic import BaseModel


class MongoConversationHistorySettings(BaseModel):
    uri: str = "mongodb://localhost:27017"
    database_name: str = "tuvilm"
    tz_aware: bool = True
