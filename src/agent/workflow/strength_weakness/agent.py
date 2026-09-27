"""Agent orchestration for the capability strength/weakness workflow."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

from pydantic_ai import Agent, PromptedOutput, RunContext
from pydantic_ai.messages import ModelMessage

from src.agent.deps import TuviAgentDeps
from src.agent.workflow.strength_weakness.input import (
    STRENGTH_WEAKNESS_REASONING_INSTRUCTION,
    build_strength_weakness_evidence,
    prepare_capability_input,
)
from src.agent.workflow.strength_weakness.ontology import (
    build_capability_ontology_instruction,
)
from src.agent.workflow.strength_weakness.output import (
    CAPABILITY_PROFILE_OUTPUT_INSTRUCTION,
    CapabilityProfile,
    render_capability_profile,
)

_logger = logging.getLogger(__name__)


STRENGTH_WEAKNESS_AGENT_BASE_INSTRUCTION = """
Bạn là sub-agent chuyên khám phá những năng lực nổi bật nhất và những hạn chế,
mặt quá đà hoặc xung đột đáng chú ý nhất trong cách một người sử dụng năng lực
của mình từ lá số Tử Vi.

## Boundary bắt buộc

- Chỉ kết luận từ `evidence` và `book_sections` được workflow cung cấp.
- Không dùng kiến thức Tử Vi ẩn hoặc fixed mapping sao → skill.
- Không biến outcome truyền thống thành capability của bản thân.
- Không chấm điểm danh sách kỹ năng cố định và không cố phủ hết ontology.
- Không chẩn đoán tâm lý, định mệnh hóa hoặc phán chắc.

Workflow đã cung cấp dữ kiện lá số trong `evidence` và nội dung sách tham chiếu
trong `book_sections`. Phân biệt dữ kiện với kiến thức sách khi tổng hợp.
Input luôn có Mệnh/Thân, tam phương tứ chính Mệnh, Phúc Đức và Tật Ách,
cùng nội dung sách tương ứng. Tổng hợp trực tiếp từ dữ liệu này để trả
`CapabilityProfile`; không cần chọn hoặc gọi tool lấy thêm cung.
""".strip()


def build_strength_weakness_agent_instruction() -> str:
    return f"{STRENGTH_WEAKNESS_AGENT_BASE_INSTRUCTION}\n\n{STRENGTH_WEAKNESS_REASONING_INSTRUCTION}\n\n{build_capability_ontology_instruction()}\n\n{CAPABILITY_PROFILE_OUTPUT_INSTRUCTION}"


STRENGTH_WEAKNESS_AGENT_INSTRUCTION = build_strength_weakness_agent_instruction()


def build_strength_weakness_agent(model: str) -> Agent:
    return Agent(
        model=model,
        name="diem_manh_diem_yeu_agent",
        deps_type=TuviAgentDeps,
        # Qwen thinking models reject the `tool_choice=required` request that
        # Pydantic AI's default ToolOutput mode emits for BaseModel outputs.
        # PromptedOutput validates the JSON text response without requiring
        # an output-tool call.
        output_type=PromptedOutput(CapabilityProfile),
        instructions=STRENGTH_WEAKNESS_AGENT_INSTRUCTION,
        output_retries=2,
    )


async def run_strength_weakness_agent(
    *,
    agent: Agent,
    deps: TuviAgentDeps,
    request: str,
    usage: Any = None,
    message_history: Sequence[ModelMessage] | None = None,
) -> CapabilityProfile:
    """Prepare chart evidence and book knowledge before the first model request."""
    evidence = build_strength_weakness_evidence(deps.require_la_so())
    prepared_input = prepare_capability_input(evidence, deps.require_book())
    prompt = f"{request}\n\n## Dữ liệu đầu vào (CapabilityInput)\n{prepared_input.model_dump_json()}"
    _logger.info("Chạy strength/weakness agent: request_chars=%d", len(request))
    result = await agent.run(
        prompt,
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
    "STRENGTH_WEAKNESS_AGENT_BASE_INSTRUCTION",
    "STRENGTH_WEAKNESS_AGENT_INSTRUCTION",
    "build_strength_weakness_agent",
    "build_strength_weakness_agent_instruction",
    "run_strength_weakness_agent",
    "run_strength_weakness_workflow",
]
