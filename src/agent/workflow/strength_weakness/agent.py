"""Configurable orchestration for the strength/weakness workflow."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage

from src.agent.deps import TuviAgentDeps
from src.agent.tool.strength_weakness import get_strength_weakness_cung_bo_sung
from src.agent.tool.tu_vi_tan_bien.tool import (
    get_star_role_interaction,
    search_star_info,
)
from src.agent.workflow.contracts import (
    WorkflowInputDefinition,
    WorkflowOutputInstruction,
)
from src.agent.workflow.strength_weakness.input import (
    STRENGTH_WEAKNESS_REASONING_INSTRUCTION,
    StrengthWeaknessEvidence,
    get_strength_weakness_evidence,
)
from src.agent.workflow.strength_weakness.output import (
    RADAR_OUTPUT_INSTRUCTION,
    StrengthWeaknessAssessment,
)

_logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class StrengthWeaknessAgentConfig:
    """Input and output contracts fixed when the sub-agent is built."""

    input_name: str = "default"
    output_instruction: str = "radar"


STRENGTH_WEAKNESS_INPUT_REGISTRY: dict[str, WorkflowInputDefinition] = {}
STRENGTH_WEAKNESS_OUTPUT_INSTRUCTION_REGISTRY: dict[str, WorkflowOutputInstruction] = {}

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
        name="default",
        model=StrengthWeaknessEvidence,
        tool=get_strength_weakness_evidence,
        instructions=(STRENGTH_WEAKNESS_REASONING_INSTRUCTION,),
        supporting_tools=(
            get_strength_weakness_cung_bo_sung,
            search_star_info,
            get_star_role_interaction,
        ),
    )
)
register_strength_weakness_output_instruction(
    WorkflowOutputInstruction(
        name="radar",
        instruction=RADAR_OUTPUT_INSTRUCTION,
        output_type=StrengthWeaknessAssessment,
    )
)


STRENGTH_WEAKNESS_AGENT_BASE_INSTRUCTION = """
Bạn là sub-agent chuyên đánh giá điểm mạnh và điểm yếu về năng lực từ lá số Tử
Vi. Kết quả của bạn là dữ liệu có cấu trúc cho radar, không phải một bài chat tự
do và không phải dự đoán outcome.

Luôn gọi {input_tool} trước khi suy luận. Đây là đường duy nhất dựng primary
input contract. Không tự thu thập lại cùng evidence bằng supporting tools.

Ngay sau primary input, `search_star_info` là phase bắt buộc thứ hai. Không được
chọn score hoặc phát `StrengthWeaknessAssessment` trước khi đã tra hết
`sao_can_tra_cuu`. Mục đích của phase này là lấy ý nghĩa trừu tượng của từng
chính tinh và phụ tinh để hiểu cả bộ sao, không phải tìm thêm sao hoặc lấy một
con số cộng/trừ.

Chỉ dùng supporting tools theo instruction của input: cung bổ sung phải lazy và
có lý do material; tool sách chỉ tra đúng sao đã xuất hiện trong evidence.
Không tự bịa sao, vị trí, trạng thái, tinh hệ hoặc nguồn reinforcement.

Scoring là trách nhiệm 100% của model. Tool và code chỉ cung cấp facts, tuyệt đối
không giả định có điểm cộng/trừ ẩn trong evidence models.
""".strip()


def get_strength_weakness_input(name: str) -> WorkflowInputDefinition:
    return _resolve_definition(
        STRENGTH_WEAKNESS_INPUT_REGISTRY,
        name,
        "input",
    )


def get_strength_weakness_output_instruction(
    name: str,
) -> WorkflowOutputInstruction:
    return _resolve_definition(
        STRENGTH_WEAKNESS_OUTPUT_INSTRUCTION_REGISTRY,
        name,
        "output instruction",
    )


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


STRENGTH_WEAKNESS_AGENT_INSTRUCTION = build_strength_weakness_agent_instruction()


def build_strength_weakness_agent(
    model: str,
    *,
    config: StrengthWeaknessAgentConfig | None = None,
) -> Agent:
    """Build one immutable structured-output strength/weakness agent."""
    resolved = resolve_strength_weakness_config(config)
    input_definition = get_strength_weakness_input(resolved.input_name)
    output_instruction = get_strength_weakness_output_instruction(
        resolved.output_instruction
    )
    return Agent(
        model=model,
        name="strength_weakness_agent",
        deps_type=TuviAgentDeps,
        output_type=output_instruction.output_type,
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
) -> StrengthWeaknessAssessment:
    """Run the configured sub-agent without rebuilding its evidence."""
    _logger.info("Chạy strength/weakness agent: request_chars=%d", len(request))
    result = await agent.run(
        request,
        deps=deps,
        usage=usage,
        message_history=message_history,
    )
    _logger.info("Strength/weakness agent hoàn tất")
    return result.output


async def run_strength_weakness_workflow(
    ctx: RunContext[TuviAgentDeps],
    request: str,
) -> StrengthWeaknessAssessment:
    """Đánh giá điểm mạnh/điểm yếu và trả structured radar data.

    Truyền nguyên văn yêu cầu của người dùng. Kết quả là contract cuối của
    workflow; caller không tự chấm lại hoặc biến đổi ngầm thành văn bản.
    """
    return await run_strength_weakness_agent(
        agent=ctx.deps.require_strength_weakness_agent(),
        deps=ctx.deps,
        request=request,
        usage=ctx.usage,
        message_history=ctx.deps.message_history,
    )
