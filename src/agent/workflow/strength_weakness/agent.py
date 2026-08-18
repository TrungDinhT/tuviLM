"""Agent orchestration for the capability strength/weakness workflow."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from pydantic_ai import Agent, PromptedOutput, RunContext
from pydantic_ai.messages import ModelMessage

from src.agent.deps import TuviAgentDeps
from src.agent.workflow.contracts import (
    WorkflowInputDefinition,
    WorkflowOutputInstruction,
)
from src.agent.workflow.strength_weakness.input import (
    STRENGTH_WEAKNESS_REASONING_INSTRUCTION,
    CapabilityEvidence,
    get_capability_meaning,
    get_capability_palace_evidence,
    get_strength_weakness_evidence,
)
from src.agent.workflow.strength_weakness.ontology import (
    build_capability_ontology_instruction,
)
from src.agent.workflow.strength_weakness.output import (
    CAPABILITY_PROFILE_OUTPUT,
    CapabilityProfile,
    render_capability_profile,
)


_logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class StrengthWeaknessAgentConfig:
    input_name: str = "tanbien"
    output_instruction: str = "capability_profile"


STRENGTH_WEAKNESS_INPUT_REGISTRY: dict[str, WorkflowInputDefinition] = {}
STRENGTH_WEAKNESS_OUTPUT_INSTRUCTION_REGISTRY: dict[
    str, WorkflowOutputInstruction
] = {}


DEFAULT_STRENGTH_WEAKNESS_CONFIG = StrengthWeaknessAgentConfig()


def _register_definition(
    registry: dict[str, Any],
    name: str,
    definition: Any,
    *,
    replace: bool,
) -> None:
    if not name:
        raise ValueError("Strength/weakness definition name must not be empty.")
    if name in registry and not replace:
        raise ValueError(
            f"Strength/weakness definition {name!r} is already registered."
        )
    registry[name] = definition


def register_strength_weakness_input(
    input_definition: WorkflowInputDefinition,
    *,
    replace: bool = False,
) -> None:
    _register_definition(
        STRENGTH_WEAKNESS_INPUT_REGISTRY,
        input_definition.name,
        input_definition,
        replace=replace,
    )


def register_strength_weakness_output_instruction(
    output_instruction: WorkflowOutputInstruction,
    *,
    replace: bool = False,
) -> None:
    _register_definition(
        STRENGTH_WEAKNESS_OUTPUT_INSTRUCTION_REGISTRY,
        output_instruction.name,
        output_instruction,
        replace=replace,
    )


register_strength_weakness_input(
    WorkflowInputDefinition(
        name="tanbien",
        model=CapabilityEvidence,
        tool=get_strength_weakness_evidence,
        instructions=(
            STRENGTH_WEAKNESS_REASONING_INSTRUCTION,
            build_capability_ontology_instruction(),
        ),
        supporting_tools=(
            get_capability_meaning,
            get_capability_palace_evidence,
        ),
    )
)
register_strength_weakness_output_instruction(CAPABILITY_PROFILE_OUTPUT)


STRENGTH_WEAKNESS_AGENT_BASE_INSTRUCTION = """
Bạn là sub-agent chuyên khám phá những năng lực nổi bật nhất và những hạn chế,
mặt quá đà hoặc xung đột đáng chú ý nhất trong cách một người sử dụng năng lực
của mình từ lá số Tử Vi.

## Boundary bắt buộc

- Chỉ kết luận từ evidence, cách cục và nội dung sách đã thực sự nhận qua tool.
- Không dùng kiến thức Tử Vi ẩn hoặc fixed mapping sao → skill.
- Không biến outcome truyền thống thành capability của bản thân.
- Không chấm điểm danh sách kỹ năng cố định và không cố phủ hết ontology.
- Không chẩn đoán tâm lý, định mệnh hóa hoặc phán chắc.

Luôn gọi `{input_tool}` trước khi suy luận. Đây là đường duy nhất dựng input
contract ban đầu. Sau đó chỉ dùng supporting tools khi cần meaning hoặc context
có khả năng thay đổi một finding quan trọng.
""".strip()


def _resolve_definition(
    registry: dict[str, Any],
    name: str,
    kind: str,
) -> Any:
    try:
        return registry[name]
    except KeyError as exc:
        available = ", ".join(sorted(registry)) or "(none)"
        raise ValueError(
            f"Unknown strength/weakness {kind} {name!r}. Available: {available}."
        ) from exc


def get_strength_weakness_input(name: str) -> WorkflowInputDefinition:
    return _resolve_definition(STRENGTH_WEAKNESS_INPUT_REGISTRY, name, "input")


def get_strength_weakness_output_instruction(
    name: str,
) -> WorkflowOutputInstruction:
    return _resolve_definition(
        STRENGTH_WEAKNESS_OUTPUT_INSTRUCTION_REGISTRY,
        name,
        "output instruction",
    )


def resolve_strength_weakness_config(
    config: StrengthWeaknessAgentConfig | None = None,
) -> StrengthWeaknessAgentConfig:
    resolved = config or DEFAULT_STRENGTH_WEAKNESS_CONFIG
    get_strength_weakness_input(resolved.input_name)
    get_strength_weakness_output_instruction(resolved.output_instruction)
    return resolved


def build_strength_weakness_agent_instruction(
    config: StrengthWeaknessAgentConfig | None = None,
) -> str:
    resolved = resolve_strength_weakness_config(config)
    input_definition = get_strength_weakness_input(resolved.input_name)
    output_instruction = get_strength_weakness_output_instruction(
        resolved.output_instruction
    )
    return "\n\n".join(
        [
            STRENGTH_WEAKNESS_AGENT_BASE_INSTRUCTION.format(
                input_tool=input_definition.tool.__name__
            ),
            *input_definition.instructions,
            output_instruction.instruction,
        ]
    )


STRENGTH_WEAKNESS_AGENT_INSTRUCTION = (
    build_strength_weakness_agent_instruction()
)


def build_strength_weakness_agent(
    model: str,
    *,
    config: StrengthWeaknessAgentConfig | None = None,
) -> Agent:
    resolved = resolve_strength_weakness_config(config)
    input_definition = get_strength_weakness_input(resolved.input_name)
    output_instruction = get_strength_weakness_output_instruction(
        resolved.output_instruction
    )
    return Agent(
        model=model,
        name="diem_manh_diem_yeu_agent",
        deps_type=TuviAgentDeps,
        # Qwen thinking models reject the `tool_choice=required` request that
        # Pydantic AI's default ToolOutput mode emits for BaseModel outputs.
        # PromptedOutput keeps schema validation while allowing normal tool
        # calls followed by a JSON text response (`tool_choice=auto`).
        output_type=PromptedOutput(output_instruction.output_type),
        instructions=build_strength_weakness_agent_instruction(resolved),
        tool_retries=2,
        output_retries=2,
        tools=[
            input_definition.tool,
            *input_definition.supporting_tools,
        ],
    )


async def run_strength_weakness_agent(
    *,
    agent: Agent,
    deps: TuviAgentDeps,
    request: str,
    usage: Any = None,
    message_history: Sequence[ModelMessage] | None = None,
) -> CapabilityProfile:
    """Run the configured sub-agent and preserve its structured output."""
    _logger.info("Chạy strength/weakness agent: request_chars=%d", len(request))
    result = await agent.run(
        request,
        deps=deps,
        usage=usage,
        message_history=message_history,
    )
    return result.output


async def run_strength_weakness_workflow(
    ctx: RunContext[TuviAgentDeps],
    request: str,
) -> str:
    """Composite main-agent tool with deterministic rendering and no re-analysis."""
    profile = await run_strength_weakness_agent(
        agent=ctx.deps.require_strength_weakness_agent(),
        deps=ctx.deps,
        request=request,
        usage=ctx.usage,
        message_history=ctx.deps.message_history,
    )
    rendered = render_capability_profile(profile)
    _logger.info(
        "Strength/weakness workflow hoàn tất: strengths=%d weaknesses=%d chars=%d",
        len(profile.diem_manh),
        len(profile.diem_yeu),
        len(rendered),
    )
    return rendered


__all__ = [
    "DEFAULT_STRENGTH_WEAKNESS_CONFIG",
    "STRENGTH_WEAKNESS_AGENT_BASE_INSTRUCTION",
    "STRENGTH_WEAKNESS_AGENT_INSTRUCTION",
    "STRENGTH_WEAKNESS_INPUT_REGISTRY",
    "STRENGTH_WEAKNESS_OUTPUT_INSTRUCTION_REGISTRY",
    "StrengthWeaknessAgentConfig",
    "build_strength_weakness_agent",
    "build_strength_weakness_agent_instruction",
    "get_strength_weakness_input",
    "get_strength_weakness_output_instruction",
    "register_strength_weakness_input",
    "register_strength_weakness_output_instruction",
    "resolve_strength_weakness_config",
    "run_strength_weakness_agent",
    "run_strength_weakness_workflow",
]
