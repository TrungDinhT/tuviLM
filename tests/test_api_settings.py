from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from api.settings import ApiSettings


def test_strength_weakness_defaults_to_deepseek_on_openrouter(monkeypatch) -> None:
    for name in (
        "STRENGTH_WEAKNESS__MODEL", "STRENGTH_WEAKNESS__PROVIDER",
        "STRENGTH_WEAKNESS__ALLOW_FALLBACKS", "STRENGTH_WEAKNESS__PROVIDER_SORT",
        "STRENGTH_WEAKNESS__REASONING_EFFORT",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = ApiSettings(_env_file=None)
    assert settings.strength_weakness.model == "openrouter:deepseek/deepseek-v4.1-flash"
    assert settings.strength_weakness.provider == "together"
    assert settings.strength_weakness.allow_fallbacks is True
    assert settings.strength_weakness.provider_sort == "latency"
    assert settings.strength_weakness.reasoning_effort == "low"


def test_strength_weakness_model_can_be_overridden_in_env_or_dotenv(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("STRENGTH_WEAKNESS__MODEL", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("STRENGTH_WEAKNESS__MODEL=openrouter:qwen/qwen3.7-max\n")
    settings = ApiSettings(_env_file=env_file)
    assert settings.strength_weakness.model == "openrouter:qwen/qwen3.7-max"
    assert settings.strength_weakness.provider == "together"
    assert settings.strength_weakness.allow_fallbacks is True

    monkeypatch.setenv("STRENGTH_WEAKNESS__MODEL", "openrouter:qwen/qwen3.8-flash")
    assert ApiSettings(_env_file=env_file).strength_weakness.model == "openrouter:qwen/qwen3.8-flash"


def test_strength_weakness_routing_can_be_overridden_in_env_or_dotenv(monkeypatch, tmp_path) -> None:
    for suffix in ("PROVIDER", "ALLOW_FALLBACKS", "PROVIDER_SORT", "REASONING_EFFORT"):
        monkeypatch.delenv(f"STRENGTH_WEAKNESS__{suffix}", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "STRENGTH_WEAKNESS__PROVIDER=deepinfra\n"
        "STRENGTH_WEAKNESS__ALLOW_FALLBACKS=false\n"
        "STRENGTH_WEAKNESS__PROVIDER_SORT=throughput\n"
        "STRENGTH_WEAKNESS__REASONING_EFFORT=high\n"
    )
    settings = ApiSettings(_env_file=env_file)
    assert settings.strength_weakness.provider == "deepinfra"
    assert settings.strength_weakness.allow_fallbacks is False
    assert settings.strength_weakness.provider_sort == "throughput"
    assert settings.strength_weakness.reasoning_effort == "high"

    monkeypatch.setenv("STRENGTH_WEAKNESS__PROVIDER", "together")
    monkeypatch.setenv("STRENGTH_WEAKNESS__ALLOW_FALLBACKS", "true")
    monkeypatch.setenv("STRENGTH_WEAKNESS__PROVIDER_SORT", "latency")
    monkeypatch.setenv("STRENGTH_WEAKNESS__REASONING_EFFORT", "low")
    settings = ApiSettings(_env_file=env_file)
    assert settings.strength_weakness.provider == "together"
    assert settings.strength_weakness.allow_fallbacks is True
    assert settings.strength_weakness.provider_sort == "latency"
    assert settings.strength_weakness.reasoning_effort == "low"


@pytest.mark.parametrize("model_name,provider,effort,allow_fallbacks,sort", [
    ("deepseek/deepseek-v4.1-flash", "together", "low", True, "latency"),
    ("qwen/qwen3.7-max", "alibaba", "high", False, "throughput"),
])
def test_api_uses_strength_weakness_routing_settings(
    monkeypatch, model_name, provider, effort, allow_fallbacks, sort,
) -> None:
    from api import main

    monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")
    settings = ApiSettings(
        _env_file=None,
        strength_weakness={
            "model": f"openrouter:{model_name}",
            "provider": provider,
            "reasoning_effort": effort,
            "allow_fallbacks": allow_fallbacks,
            "provider_sort": sort,
        },
    )
    monkeypatch.setattr(main, "get_settings", lambda: settings)
    store = SimpleNamespace(close=AsyncMock())
    monkeypatch.setattr(main.MongoConversationHistoryStore, "connect", AsyncMock(return_value=store))
    app = SimpleNamespace(state=SimpleNamespace())

    async def initialize():
        async with main.lifespan(app):
            deps = app.state.api_state.agent_deps
            agent = deps.require_strength_weakness_agent()
            model = agent.model
            assert model.system == "openrouter"
            assert model.model_name == model_name
            assert model.base_url == "https://openrouter.ai/api/v1/"
            assert agent.model_settings["openrouter_provider"] == {
                "order": [provider], "allow_fallbacks": allow_fallbacks, "sort": sort,
            }
            assert agent.model_settings["openrouter_reasoning"] == {"effort": effort}
            assert deps.require_agent().model.system == "openrouter"
            assert deps.require_personality_agent().model.system == "openrouter"
            assert not deps.require_agent().model_settings
            assert not deps.require_personality_agent().model_settings

    asyncio.run(initialize())
    store.close.assert_awaited_once()


def test_api_settings_uses_default_conversation_history_store_when_env_omits_it(
    monkeypatch,
) -> None:
    for name in (
        "CONVERSATION_HISTORY_STORE__URI",
        "CONVERSATION_HISTORY_STORE__DATABASE_NAME",
        "CONVERSATION_HISTORY_STORE__TZ_AWARE",
        "CONVERSATION_HISTORY_STORE__STALE_PENDING_AFTER_SECONDS",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = ApiSettings(_env_file=None)

    assert settings.conversation_history_store.uri == "mongodb://localhost:27017"
    assert settings.conversation_history_store.database_name == "tuvilm"
    assert settings.conversation_history_store.tz_aware is True
    assert settings.conversation_history_store.stale_pending_after_seconds == 900
