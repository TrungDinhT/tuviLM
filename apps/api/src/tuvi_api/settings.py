from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from tuvi_api.chat.storage.settings import MongoConversationHistorySettings


class StrengthWeaknessSettings(BaseModel):
    model: str = "openrouter:deepseek/deepseek-v4.1-flash"
    provider: str = "together"
    allow_fallbacks: bool = True
    provider_sort: Literal["latency", "throughput", "price"] = "latency"
    reasoning_effort: Literal[
        "none", "minimal", "low", "medium", "high", "xhigh"
    ] = "low"


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

    strength_weakness: StrengthWeaknessSettings = Field(
        default_factory=StrengthWeaknessSettings
    )

    conversation_history_store: MongoConversationHistorySettings = Field(
        default_factory=MongoConversationHistorySettings
    )
    auth: AuthSettings = Field(default_factory=AuthSettings)
    agent_model: str = "openrouter:qwen/qwen3.7-max"
    # The book files are not in git. Relative paths resolve from the working directory.
    book_root: Path = Path("data/tuvitanbien_chunking_compact/part_2")


@lru_cache
def get_settings() -> ApiSettings:
    return ApiSettings()
