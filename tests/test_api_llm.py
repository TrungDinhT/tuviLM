from pydantic_ai.models import ModelRequestParameters
from pydantic_ai.profiles.openai import OpenAIModelProfile
from pydantic_ai.tools import ToolDefinition

from api.llm import build_qwen_openrouter_model


def test_qwen_thinking_uses_auto_tool_choice(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    model = build_qwen_openrouter_model()

    profile = OpenAIModelProfile.from_profile(model.profile)
    assert profile.openai_supports_tool_choice_required is False
    assert profile.openai_chat_thinking_field == "reasoning"

    request_parameters = ModelRequestParameters(
        function_tools=[ToolDefinition(name="get_strength_weakness_evidence")],
        output_mode="tool",
        output_tools=[ToolDefinition(name="final_result")],
        allow_text_output=False,
    )

    tools, tool_choice = model._get_tool_choice({}, request_parameters)

    assert {tool["function"]["name"] for tool in tools} == {
        "get_strength_weakness_evidence",
        "final_result",
    }
    assert tool_choice == "auto"


def test_qwen_thinking_does_not_force_single_output_tool(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    model = build_qwen_openrouter_model()
    request_parameters = ModelRequestParameters(
        output_mode="tool",
        output_tools=[ToolDefinition(name="final_result")],
        allow_text_output=False,
    )

    tools, tool_choice = model._get_tool_choice({}, request_parameters)

    assert [tool["function"]["name"] for tool in tools] == ["final_result"]
    assert tool_choice == "auto"
