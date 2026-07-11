from __future__ import annotations

from api.settings import ApiSettings


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
