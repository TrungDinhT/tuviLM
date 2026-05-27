from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from api.chat.storage.settings import MongoConversationHistorySettings


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
    )

    conversation_history_store: MongoConversationHistorySettings


@lru_cache
def get_settings() -> ApiSettings:
    return ApiSettings()
