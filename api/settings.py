from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from api.chat.storage.settings import MongoConversationHistorySettings
from api.background_runs import RunSettings


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
    )

    conversation_history_store: MongoConversationHistorySettings = Field(
        default_factory=MongoConversationHistorySettings
    )
    runs: RunSettings = Field(default_factory=RunSettings)


@lru_cache
def get_settings() -> ApiSettings:
    return ApiSettings()
