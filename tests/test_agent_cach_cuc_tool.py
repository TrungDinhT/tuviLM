from __future__ import annotations

import json

from pydantic import BaseModel, TypeAdapter
from pydantic_ai import Agent
from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
)
from pydantic_ai.models.function import AgentInfo, FunctionModel

from src.agent.deps import TuviAgentDeps
from src.agent.tool.cach_cuc.tool import get_list_cach_cuc
from src.agent.tool.json_compatible import JsonCompatible
from src.refactored.components.definitions.cung_role import Role
from src.refactored.la_so import LaSo
from tests.fixtures.laso_priors import FIXTURE_PRIOR_A


class _StructuredToolInput(BaseModel):
    roles: list[Role]


def test_json_compatible_decodes_double_encoded_structured_input() -> None:
    adapter = TypeAdapter(JsonCompatible[_StructuredToolInput])
    encoded_input = json.dumps(json.dumps({"roles": ["menh"]}))

    assert adapter.validate_python(encoded_input) == _StructuredToolInput(
        roles=[Role.MENH]
    )


def _run_cach_cuc_tool(filtered_roles: object) -> object:
    tool_results: list[object] = []

    def call_tool(messages, _info: AgentInfo) -> ModelResponse:
        returned_parts = [
            part
            for message in messages
            if isinstance(message, ModelRequest)
            for part in message.parts
            if isinstance(part, ToolReturnPart)
        ]
        if returned_parts:
            tool_results.append(returned_parts[-1].content)
            return ModelResponse(parts=[TextPart("done")])
        return ModelResponse(
            parts=[
                ToolCallPart(
                    "get_list_cach_cuc",
                    {"filtered_roles": filtered_roles},
                )
            ]
        )

    agent = Agent(FunctionModel(call_tool), tools=[get_list_cach_cuc])
    deps = TuviAgentDeps(la_so=LaSo.from_prior(FIXTURE_PRIOR_A))
    agent.run_sync("Liệt kê cách cục cung Mệnh.", deps=deps)
    return tool_results[0]


def test_agent_accepts_json_encoded_filtered_roles() -> None:
    assert _run_cach_cuc_tool(json.dumps(["menh"])) == _run_cach_cuc_tool(
        [Role.MENH]
    )


def test_agent_accepts_double_json_encoded_filtered_roles() -> None:
    encoded_roles = json.dumps(json.dumps(["menh"]))

    assert _run_cach_cuc_tool(encoded_roles) == _run_cach_cuc_tool([Role.MENH])


def test_agent_accepts_native_filtered_roles() -> None:
    assert _run_cach_cuc_tool([Role.MENH])
