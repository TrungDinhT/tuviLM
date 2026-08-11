from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic_ai.messages import ModelRequest, UserPromptPart
from src.agent.deps import TuviAgentDeps
from src.agent.main import build_tuvi_agent
from src.agent.workflow.personality import (
    DEFAULT_PERSONALITY_CONFIG,
    PERSONALITY_AGENT_INSTRUCTION,
    PERSONALITY_INPUT_REGISTRY,
    PERSONALITY_OUTPUT_INSTRUCTION_REGISTRY,
    PersonalityAgentConfig,
    build_personality_agent,
    build_personality_agent_instruction,
    get_personality_evidence,
    luan_tinh_cach_skill,
    run_personality_workflow,
    run_tinh_cach_workflow,
)
from src.agent.workflow.personality.input.tanbien import (
    BanMenhEvidence,
    PersonalityEvidence,
)
from src.agent.workflow.personality.output import (
    OPTIONAL_AVOID_EVIDENCE_INSTRUCTION,
)
from src.refactored.la_so import LaSo
from tests.fixtures.laso_priors import FIXTURE_PRIOR_A


pytestmark = pytest.mark.anyio


def _analysis() -> str:
    return "## Chân dung tính cách\nBài luận tự nhiên do model viết."


def test_composite_input_tool_builds_complete_contract():
    ctx = SimpleNamespace(
        deps=TuviAgentDeps(la_so=LaSo.from_prior(FIXTURE_PRIOR_A))
    )
    evidence = get_personality_evidence(ctx)

    assert evidence.foundation.ban_menh.name
    assert evidence.vong_thai_tue.menh.thai_tue_star.id == "tue_pha"
    assert "Chính tinh Mệnh" in evidence.b3_b4_context
    assert all(
        left.priority >= right.priority
        for left, right in zip(evidence.cach_cuc, evidence.cach_cuc[1:])
    )
    assert evidence.phu_tinh.anchor == "Mệnh"
    assert evidence.trang_sinh_menh.palace == "Mệnh"
    assert evidence.trang_sinh_than.palace == "Thân"


def test_input_contract_intentionally_projects_shared_tool_payload():
    evidence = BanMenhEvidence.model_validate(
        {
            "id": "example",
            "name": "Example",
            "ngu_hanh": "Mộc",
            "meaning": {"shared_tool_only": True},
        }
    )

    assert evidence.model_dump() == {
        "id": "example",
        "name": "Example",
        "ngu_hanh": "Mộc",
    }


def test_personality_workflow_registers_input_and_output_instruction():
    input_definition = PERSONALITY_INPUT_REGISTRY["tanbien"]
    output_instruction = PERSONALITY_OUTPUT_INSTRUCTION_REGISTRY[
        "7_foundation_questions"
    ]

    assert DEFAULT_PERSONALITY_CONFIG == PersonalityAgentConfig(
        input_name="tanbien",
        output_instruction="7_foundation_questions",
    )
    assert input_definition.model is PersonalityEvidence
    assert input_definition.tool is get_personality_evidence
    assert luan_tinh_cach_skill() in input_definition.instructions
    assert "## Bước" not in "\n".join(input_definition.instructions)
    assert output_instruction.output_type is str
    assert (
        "Bạn tự nhiên dễ phản ứng theo hướng nào?"
        in output_instruction.instruction
    )
    assert "Người này" not in output_instruction.instruction
    assert "Họ đang" not in output_instruction.instruction
    assert "Chân dung kể chuyện" in output_instruction.instruction


def test_output_instruction_is_selected_when_agent_instruction_is_built():
    instruction = build_personality_agent_instruction(
        PersonalityAgentConfig(output_instruction="7_foundation_questions")
    )

    assert "Phần 1 - Bảy câu hỏi nền tảng" in instruction
    assert "Phần 2 - Chân dung kể chuyện" in instruction
    assert "## Bước" not in instruction
    assert "B1-B6" not in instruction
    assert OPTIONAL_AVOID_EVIDENCE_INSTRUCTION not in instruction


def test_unknown_build_time_input_is_rejected():
    with pytest.raises(ValueError, match="Unknown personality input 'missing'"):
        build_personality_agent_instruction(
            PersonalityAgentConfig(input_name="missing")
        )


async def test_run_personality_workflow_makes_one_plain_text_synthesis_call():
    class FakeAgent:
        async def run(
            self,
            prompt,
            *,
            deps,
            usage=None,
            message_history=None,
        ):
            self.calls = getattr(self, "calls", 0) + 1
            self.prompt = prompt
            self.deps = deps
            self.usage = usage
            self.message_history = message_history
            return SimpleNamespace(output=_analysis())

    agent = FakeAgent()
    deps = TuviAgentDeps(la_so=LaSo.from_prior(FIXTURE_PRIOR_A))
    history = [
        ModelRequest(parts=[UserPromptPart(content="Câu hỏi trước.")])
    ]

    result = await run_personality_workflow(
        agent=agent,
        deps=deps,
        request="Hãy luận tính cách của tôi.",
        usage="shared-usage",
        message_history=history,
    )

    assert agent.calls == 1
    assert agent.deps is deps
    assert agent.usage == "shared-usage"
    assert agent.prompt == "Hãy luận tính cách của tôi."
    assert agent.message_history is history
    assert result == _analysis()


async def test_workflow_tool_returns_model_text_unchanged():
    class FakeAgent:
        async def run(
            self,
            prompt,
            *,
            deps,
            usage=None,
            message_history=None,
        ):
            self.message_history = message_history
            return SimpleNamespace(output=_analysis())

    history = [
        ModelRequest(parts=[UserPromptPart(content="Câu hỏi trước.")])
    ]
    personality_agent = FakeAgent()
    deps = TuviAgentDeps(
        personality_agent=personality_agent,
        la_so=LaSo.from_prior(FIXTURE_PRIOR_A),
        message_history=history,
    )
    ctx = SimpleNamespace(deps=deps, usage="usage")

    rendered = await run_tinh_cach_workflow(ctx, "Luận tính cách")

    assert rendered == _analysis()
    assert personality_agent.message_history is history


def test_general_agent_exposes_only_the_composite_personality_skill():
    tools = build_tuvi_agent("test").toolsets[0].tools

    assert "run_tinh_cach_workflow" in tools
    assert "luan_tinh_cach_b1_b2" not in tools
    assert "luan_tinh_cach_b3_b4" not in tools
    assert "luan_tinh_cach_b5_b6_skill" not in tools


def test_personality_agent_can_run_standalone_with_full_toolset():
    agent = build_personality_agent("test")
    tools = agent.toolsets[0].tools
    expected = {
        "get_personality_evidence",
        "get_laso_foundation",
        "get_vong_thai_tue",
        "get_cung_by_position",
        "get_cung_by_role",
        "get_list_cach_cuc",
        "get_phu_tinh_tam_phuong_tu_chinh",
        "get_trang_sinh",
        "get_tam_hop",
        "get_xung_chieu",
        "get_tinh_cach_b3_b4_context",
        "get_star_description",
        "get_star_role_interaction",
    }

    assert expected == set(tools)
    assert agent.output_type is str
    assert "Luôn gọi get_personality_evidence trước" in PERSONALITY_AGENT_INSTRUCTION
    assert "không trả JSON" in PERSONALITY_AGENT_INSTRUCTION
