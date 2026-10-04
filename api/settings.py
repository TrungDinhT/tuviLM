from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from api.chat.storage.settings import MongoConversationHistorySettings


class AuthSettings(BaseModel):
    base_url: str = "http://localhost:3000"
    mongo_uri: str = "mongodb://localhost:27017"
    database_name: str = "tuvilm"

    @property
    def jwks_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/api/auth/jwks"


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
    )

    conversation_history_store: MongoConversationHistorySettings = Field(
        default_factory=MongoConversationHistorySettings
    )
    auth: AuthSettings = Field(default_factory=AuthSettings)


@lru_cache
def get_settings() -> ApiSettings:
    return ApiSettings()
