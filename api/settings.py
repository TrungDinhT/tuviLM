from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from api.chat.storage.settings import MongoConversationHistorySettings


class StrengthWeaknessSettings(BaseModel):
    model: str = "openrouter:deepseek/deepseek-v4.1-flash"
    provider: str = "together"
    allow_fallbacks: bool = True
    provider_sort: Literal["latency", "throughput", "price"] = "latency"
    reasoning_effort: Literal[
        "none", "minimal", "low", "medium", "high", "xhigh"
    ] = "low"


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
    )

    strength_weakness: StrengthWeaknessSettings = Field(
        default_factory=StrengthWeaknessSettings
    )

    conversation_history_store: MongoConversationHistorySettings = Field(
        default_factory=MongoConversationHistorySettings
    )


@lru_cache
def get_settings() -> ApiSettings:
    return ApiSettings()
