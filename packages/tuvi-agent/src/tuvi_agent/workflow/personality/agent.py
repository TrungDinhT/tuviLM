"""Configurable agent orchestration for the personality workflow."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage

from src.agent.deps import TuviAgentDeps
from src.agent.skills import read_book_tuvi_tan_bien
from src.agent.tool import (
    get_cung_by_position,
    get_cung_by_role,
    get_laso_foundation,
    get_list_cach_cuc,
    get_phu_tinh_tam_phuong_tu_chinh,
    get_tam_hop,
    get_tinh_cach_b3_b4_context,
    get_trang_sinh,
    get_vong_thai_tue,
    get_xung_chieu,
)
from src.agent.tool.tu_vi_tan_bien.tool import (
    get_star_description,
    get_star_role_interaction,
)
from src.agent.workflow.contracts import (
    WorkflowInputDefinition,
    WorkflowOutputInstruction,
)
from src.agent.workflow.personality.input.tanbien import (
    PersonalityEvidence,
    get_personality_evidence,
    luan_tinh_cach_skill,
)
from src.agent.workflow.personality.output import (
    SEVEN_FOUNDATION_QUESTIONS_INSTRUCTION,
)

_logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class PersonalityAgentConfig:
    """Input and output-instruction names bound when the agent is built."""

    input_name: str = "tanbien"
    output_instruction: str = "7_foundation_questions"


PERSONALITY_INPUT_REGISTRY: dict[str, WorkflowInputDefinition] = {}
PERSONALITY_OUTPUT_INSTRUCTION_REGISTRY: dict[str, WorkflowOutputInstruction] = {}

DEFAULT_PERSONALITY_CONFIG = PersonalityAgentConfig()


def register_personality_input(
    input_definition: WorkflowInputDefinition,
    *,
    replace: bool = False,
) -> None:
    """Register a tool-backed personality input under its stable name."""
    _register_definition(
        PERSONALITY_INPUT_REGISTRY,
        input_definition.name,
        input_definition,
        replace=replace,
    )


def register_personality_output_instruction(
    output_instruction: WorkflowOutputInstruction,
    *,
    replace: bool = False,
) -> None:
    """Register response instructions and their enforced output type."""
    _register_definition(
        PERSONALITY_OUTPUT_INSTRUCTION_REGISTRY,
        output_instruction.name,
        output_instruction,
        replace=replace,
    )


def _register_definition(
    registry: dict[str, Any],
    name: str,
    definition: Any,
    *,
    replace: bool,
) -> None:
    if not name:
        raise ValueError("Personality definition name must not be empty.")
    if name in registry and not replace:
        raise ValueError(f"Personality definition {name!r} is already registered.")
    registry[name] = definition


register_personality_input(
    WorkflowInputDefinition(
        name="tanbien",
        model=PersonalityEvidence,
        tool=get_personality_evidence,
        instructions=(
            luan_tinh_cach_skill(),
            read_book_tuvi_tan_bien(),
        ),
        supporting_tools=(
            get_laso_foundation,
            get_vong_thai_tue,
            get_cung_by_position,
            get_cung_by_role,
            get_list_cach_cuc,
            get_phu_tinh_tam_phuong_tu_chinh,
            get_trang_sinh,
            get_tam_hop,
            get_xung_chieu,
            get_tinh_cach_b3_b4_context,
            get_star_description,
            get_star_role_interaction,
        ),
    )
)
register_personality_output_instruction(
    WorkflowOutputInstruction(
        name="7_foundation_questions",
        instruction=SEVEN_FOUNDATION_QUESTIONS_INSTRUCTION,
        output_type=str,
    )
)


PERSONALITY_AGENT_BASE_INSTRUCTION = """
Bạn là một trợ lý luận giải tính cách một người thông qua lá số Tử Vi. Nhiệm vụ
của bạn là tổng hợp evidence đã được thu thập từ lá số để hiểu khí chất, cách
vận hành và chân dung con người.

## Kết cấu lá số cần hiểu

- Lá số có 12 cung; mỗi cung gồm các lớp như chính tinh, phụ tinh, Tuần/Triệt,
  Tứ Hóa và Tràng Sinh.
- Sao đồng cung hoặc tạo thành tổ hợp có thể quan trọng hơn việc đọc từng sao
  rời rạc.
- Vị trí sao, vai trò cung và trạng thái đắc/hãm luôn là điều kiện của diễn giải.

## Nguyên tắc bắt buộc

1. Chỉ kết luận từ evidence, tool hoặc nội dung sách đã thực sự đọc qua tool.
2. Không tự bịa sao, trạng thái, cách cục hay tổ hợp.
3. Nếu dữ liệu chưa đủ, không suy diễn để lấp chỗ trống.
4. Không coi diễn giải là chẩn đoán tâm lý hay sự thật khách quan; không hù dọa,
   định mệnh hóa hoặc suy rộng sang bệnh tật, tai họa, giàu nghèo hay hôn nhân.

Luôn gọi {input_tool} trước khi suy luận. Tool này là đường duy nhất
dựng input contract đã chọn. Chỉ gọi tool hỗ trợ riêng lẻ khi cần kiểm tra
hoặc bổ sung cho yêu cầu ngoài payload tổng hợp.

Instruction suy luận của input bên dưới chỉ bổ sung những quy tắc chưa
có trong payload. Output instruction ở cuối chỉ dẫn cách cấu trúc và diễn
đạt câu trả lời.
""".strip()


def get_personality_input(name: str) -> WorkflowInputDefinition:
    """Resolve one registered input or fail with available names."""
    return _resolve_definition(PERSONALITY_INPUT_REGISTRY, name, "input")


def get_personality_output_instruction(name: str) -> WorkflowOutputInstruction:
    """Resolve one registered output instruction or fail with available names."""
    return _resolve_definition(
        PERSONALITY_OUTPUT_INSTRUCTION_REGISTRY,
        name,
        "output instruction",
    )


def _resolve_definition(registry: dict[str, Any], name: str, kind: str) -> Any:
    try:
        return registry[name]
    except KeyError as exc:
        available = ", ".join(sorted(registry)) or "(none)"
        raise ValueError(
            f"Unknown personality {kind} {name!r}. Available: {available}."
        ) from exc


def resolve_personality_config(
    config: PersonalityAgentConfig | None = None,
) -> PersonalityAgentConfig:
    """Validate one immutable build-time configuration."""
    resolved = config or DEFAULT_PERSONALITY_CONFIG
    get_personality_input(resolved.input_name)
    get_personality_output_instruction(resolved.output_instruction)
    return resolved


def build_personality_agent_instruction(
    config: PersonalityAgentConfig | None = None,
) -> str:
    """Compose the selected input and output instructions."""
    resolved = resolve_personality_config(config)
    input_definition = get_personality_input(resolved.input_name)
    output_instruction = get_personality_output_instruction(resolved.output_instruction)
    return "\n\n".join(
        [
            PERSONALITY_AGENT_BASE_INSTRUCTION.format(
                input_tool=input_definition.tool.__name__
            ),
            *input_definition.instructions,
            output_instruction.instruction,
        ]
    )


PERSONALITY_AGENT_INSTRUCTION = build_personality_agent_instruction()


def build_personality_agent(
    model: str,
    *,
    config: PersonalityAgentConfig | None = None,
) -> Agent:
    """Build a synthesis agent from one immutable workflow configuration."""
    resolved = resolve_personality_config(config)
    input_definition = get_personality_input(resolved.input_name)
    output_instruction = get_personality_output_instruction(resolved.output_instruction)
    return Agent(
        model=model,
        name="tinh_cach_agent",
        deps_type=TuviAgentDeps,
        output_type=output_instruction.output_type,
        instructions=build_personality_agent_instruction(resolved),
        tool_retries=2,
        output_retries=2,
        tools=[
            input_definition.tool,
            *input_definition.supporting_tools,
        ],
    )


async def run_personality_workflow(
    *,
    agent: Agent,
    deps: TuviAgentDeps,
    request: str,
    usage: Any = None,
    message_history: Sequence[ModelMessage] | None = None,
) -> str:
    """Run the configured agent; its input tool builds evidence exactly once."""
    _logger.info("Chạy personality workflow: request_chars=%d", len(request))
    result = await agent.run(
        request,
        deps=deps,
        usage=usage,
        message_history=message_history,
    )
    _logger.info(
        "Personality workflow hoàn tất: output_chars=%d",
        len(result.output),
    )
    return result.output


async def run_tinh_cach_workflow(
    ctx: RunContext[TuviAgentDeps],
    request: str,
) -> str:
    """Luận tính cách bằng input và output instruction đã cấu hình.

    Truyền nguyên văn yêu cầu của người dùng. Kết quả đã là câu trả lời cuối;
    trả lại nguyên văn và không tự luận thêm bằng các tool riêng.
    """
    _logger.info(
        "Tool run_tinh_cach_workflow bắt đầu: request_chars=%d",
        len(request),
    )
    analysis = await run_personality_workflow(
        agent=ctx.deps.require_personality_agent(),
        deps=ctx.deps,
        request=request,
        usage=ctx.usage,
        message_history=ctx.deps.message_history,
    )
    _logger.info(
        "Tool run_tinh_cach_workflow hoàn tất: output_chars=%d",
        len(analysis),
    )
    return analysis
