"""Configurable agent orchestration for the personality workflow."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from src.agent.deps import TuviAgentDeps
from src.agent.skills import luan_tinh_cach_skill, read_book_tuvi_tan_bien
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
from src.agent.workflow.personality.input.tanbien import (
    PersonalityEvidence,
    collect_personality_evidence,
    get_personality_evidence,
)
from src.agent.workflow.personality.output import (
    SEVEN_FOUNDATION_QUESTIONS_PROMPT,
)
from src.refactored.la_so import LaSo


_logger = logging.getLogger(__name__)

EvidenceCollector = Callable[[LaSo], BaseModel]
EvidenceTool = Callable[[RunContext[TuviAgentDeps]], BaseModel]


@dataclass(frozen=True, slots=True)
class PersonalityEvidenceSchema:
    """One selectable evidence contract and its deterministic collector."""

    name: str
    model: type[BaseModel]
    collector: EvidenceCollector
    tool: EvidenceTool


@dataclass(frozen=True, slots=True)
class PersonalityOutputSchema:
    """One selectable prompt that owns the complete response format."""

    name: str
    prompt: str


@dataclass(frozen=True, slots=True)
class PersonalityAgentConfig:
    """Names of the evidence and prompt-output schemas used by an agent."""

    evidence_schema: str = "tanbien"
    output_schema: str = "7_foundation_questions"


PERSONALITY_EVIDENCE_REGISTRY: dict[str, PersonalityEvidenceSchema] = {}
PERSONALITY_OUTPUT_REGISTRY: dict[str, PersonalityOutputSchema] = {}

DEFAULT_PERSONALITY_CONFIG = PersonalityAgentConfig()


def register_personality_evidence_schema(
    schema: PersonalityEvidenceSchema,
    *,
    replace: bool = False,
) -> None:
    """Register an evidence schema under its stable configuration name."""
    _register_schema(
        PERSONALITY_EVIDENCE_REGISTRY,
        schema.name,
        schema,
        replace=replace,
    )


def register_personality_output_schema(
    schema: PersonalityOutputSchema,
    *,
    replace: bool = False,
) -> None:
    """Register a prompt-only output schema under its stable configuration name."""
    _register_schema(
        PERSONALITY_OUTPUT_REGISTRY,
        schema.name,
        schema,
        replace=replace,
    )


def _register_schema(
    registry: dict[str, Any],
    name: str,
    schema: Any,
    *,
    replace: bool,
) -> None:
    if not name:
        raise ValueError("Personality schema name must not be empty.")
    if name in registry and not replace:
        raise ValueError(f"Personality schema {name!r} is already registered.")
    registry[name] = schema


register_personality_evidence_schema(
    PersonalityEvidenceSchema(
        name="tanbien",
        model=PersonalityEvidence,
        collector=collect_personality_evidence,
        tool=get_personality_evidence,
    )
)
register_personality_output_schema(
    PersonalityOutputSchema(
        name="7_foundation_questions",
        prompt=SEVEN_FOUNDATION_QUESTIONS_PROMPT,
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
4. Khi nguồn trái chiều, giữ chúng thành các lớp biểu hiện và xét thứ tự ưu tiên:
   chính tinh > Tuần/Triệt > Tứ Hóa > phụ tinh > Tràng Sinh. Cách cục có
   priority cao dùng làm khung tổng hợp.
5. Không coi diễn giải là chẩn đoán tâm lý hay sự thật khách quan; không hù dọa,
   định mệnh hóa hoặc suy rộng sang bệnh tật, tai họa, giàu nghèo hay hôn nhân.

Có hai chế độ chạy:

- Nếu prompt có khối evidence, application code đã thu thập đủ dữ liệu. Dùng
  trực tiếp khối này và không gọi lại tool dữ liệu lá số.
- Nếu prompt không có evidence, đây là lần chạy độc lập. Luôn gọi {evidence_tool} trước
  để thu thập evidence bằng code deterministic. Chỉ gọi tool lá số riêng lẻ khi
  cần kiểm tra hoặc bổ sung ngoài payload tổng hợp.

Skill luận tính cách bên dưới chỉ quy định cách đọc evidence và cách tư duy.
Prompt output schema ở cuối chỉ dẫn toàn bộ cách cấu trúc và diễn đạt câu trả lời.
""".strip()


def get_personality_evidence_schema(name: str) -> PersonalityEvidenceSchema:
    """Resolve one registered evidence schema or fail with available names."""
    return _resolve_schema(PERSONALITY_EVIDENCE_REGISTRY, name, "evidence")


def get_personality_output_schema(name: str) -> PersonalityOutputSchema:
    """Resolve one registered output schema or fail with available names."""
    return _resolve_schema(PERSONALITY_OUTPUT_REGISTRY, name, "output")


def _resolve_schema(registry: dict[str, Any], name: str, kind: str) -> Any:
    try:
        return registry[name]
    except KeyError as exc:
        available = ", ".join(sorted(registry)) or "(none)"
        raise ValueError(
            f"Unknown personality {kind} schema {name!r}. Available: {available}."
        ) from exc


def resolve_personality_config(
    config: PersonalityAgentConfig | None = None,
    *,
    evidence_schema: str | None = None,
    output_schema: str | None = None,
) -> PersonalityAgentConfig:
    """Resolve explicit overrides on top of a config or the defaults."""
    base = config or DEFAULT_PERSONALITY_CONFIG
    resolved = PersonalityAgentConfig(
        evidence_schema=(
            evidence_schema
            if evidence_schema is not None
            else base.evidence_schema
        ),
        output_schema=(
            output_schema if output_schema is not None else base.output_schema
        ),
    )
    get_personality_evidence_schema(resolved.evidence_schema)
    get_personality_output_schema(resolved.output_schema)
    return resolved


def build_personality_agent_instruction(
    config: PersonalityAgentConfig | None = None,
    *,
    evidence_schema: str | None = None,
    output_schema: str | None = None,
) -> str:
    """Compose reasoning instructions with the selected prompt output schema."""
    resolved = resolve_personality_config(
        config,
        evidence_schema=evidence_schema,
        output_schema=output_schema,
    )
    evidence = get_personality_evidence_schema(resolved.evidence_schema)
    output = get_personality_output_schema(resolved.output_schema)
    return "\n\n".join(
        [
            PERSONALITY_AGENT_BASE_INSTRUCTION.format(
                evidence_tool=evidence.tool.__name__
            ),
            luan_tinh_cach_skill(),
            read_book_tuvi_tan_bien(),
            output.prompt,
        ]
    )


PERSONALITY_AGENT_INSTRUCTION = build_personality_agent_instruction()


def build_personality_agent(
    model: str,
    *,
    config: PersonalityAgentConfig | None = None,
    evidence_schema: str | None = None,
    output_schema: str | None = None,
) -> Agent:
    """Build a synthesis agent from registered evidence and output schemas."""
    resolved = resolve_personality_config(
        config,
        evidence_schema=evidence_schema,
        output_schema=output_schema,
    )
    evidence = get_personality_evidence_schema(resolved.evidence_schema)
    agent = Agent(
        model=model,
        name="tinh_cach_agent",
        deps_type=TuviAgentDeps,
        output_type=str,
        instructions=build_personality_agent_instruction(resolved),
        tool_retries=2,
        output_retries=2,
        tools=[
            evidence.tool,
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
        ],
    )
    agent._personality_workflow_config = resolved
    return agent


async def run_personality_workflow(
    *,
    agent: Agent,
    deps: TuviAgentDeps,
    request: str,
    usage: Any = None,
    evidence_schema: str | None = None,
) -> str:
    """Collect configured evidence and execute exactly one text synthesis run."""
    config = getattr(agent, "_personality_workflow_config", None)
    resolved = resolve_personality_config(
        config if isinstance(config, PersonalityAgentConfig) else None,
        evidence_schema=evidence_schema,
    )
    evidence_definition = get_personality_evidence_schema(
        resolved.evidence_schema
    )

    _logger.info(
        "Chạy personality workflow: request_chars=%d, evidence_schema=%s, "
        "output_schema=%s",
        len(request),
        resolved.evidence_schema,
        resolved.output_schema,
    )
    evidence = evidence_definition.collector(deps.require_la_so())
    if not isinstance(evidence, evidence_definition.model):
        raise TypeError(
            f"Collector for {resolved.evidence_schema!r} returned "
            f"{type(evidence).__name__}; expected "
            f"{evidence_definition.model.__name__}."
        )
    prompt = json.dumps(
        {
            "user_request": request,
            "evidence_schema": resolved.evidence_schema,
            "evidence": evidence.model_dump(mode="json", exclude_none=True),
        },
        ensure_ascii=False,
    )
    result = await agent.run(prompt, deps=deps, usage=usage)
    _logger.info(
        "Personality workflow hoàn tất: output_chars=%d",
        len(result.output),
    )
    return result.output


async def run_tinh_cach_workflow(
    ctx: RunContext[TuviAgentDeps],
    request: str,
) -> str:
    """Luận tính cách bằng evidence và output schema đã cấu hình.

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
    )
    _logger.info(
        "Tool run_tinh_cach_workflow hoàn tất: output_chars=%d",
        len(analysis),
    )
    return analysis
