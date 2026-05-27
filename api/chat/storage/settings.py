from __future__ import annotations

from pydantic import BaseModel


class MongoConversationHistorySettings(BaseModel):
    uri: str
    database_name: str = "tuvilm"
    tz_aware: bool = True
