from __future__ import annotations

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.profiles.openai import OpenAIModelProfile
from pydantic_ai.providers.openrouter import OpenRouterProvider

QWEN_MODEL_NAME = "qwen/qwen3.7-max"


def build_qwen_openrouter_model() -> OpenAIChatModel:
    """Build Qwen with its OpenRouter features and Alibaba-compatible tool choice."""
    provider = OpenRouterProvider()
    provider_profile = provider.model_profile(QWEN_MODEL_NAME)
    profile = OpenAIModelProfile(
        openai_supports_tool_choice_required=False,
    ).update(provider_profile)
    return OpenAIChatModel(
        QWEN_MODEL_NAME,
        provider=provider,
        profile=profile,
    )
