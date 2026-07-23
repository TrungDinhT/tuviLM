from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from src.agent.deps import TuviAgentDeps
from src.agent.main import build_tuvi_agent
from src.agent.workflow.personality import (
    DEFAULT_PERSONALITY_CONFIG,
    PERSONALITY_AGENT_INSTRUCTION,
    PERSONALITY_EVIDENCE_REGISTRY,
    PERSONALITY_OUTPUT_REGISTRY,
    PersonalityAgentConfig,
    build_personality_agent,
    build_personality_agent_instruction,
    collect_personality_evidence,
    get_personality_evidence,
    run_personality_workflow,
    run_tinh_cach_workflow,
)
from src.agent.workflow.personality.input.tanbien import PersonalityEvidence
from src.refactored.la_so import LaSo
from tests.fixtures.laso_priors import FIXTURE_PRIOR_A


pytestmark = pytest.mark.anyio


def _analysis() -> str:
    return "## Chân dung tính cách\nBài luận tự nhiên do model viết."


def test_collect_personality_evidence_contains_complete_b1_b6_contract():
    evidence = collect_personality_evidence(LaSo.from_prior(FIXTURE_PRIOR_A))

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


def test_personality_workflow_registers_input_and_prompt_output_schemas():
    evidence_schema = PERSONALITY_EVIDENCE_REGISTRY["tanbien"]
    output_schema = PERSONALITY_OUTPUT_REGISTRY["7_foundation_questions"]

    assert DEFAULT_PERSONALITY_CONFIG == PersonalityAgentConfig(
        evidence_schema="tanbien",
        output_schema="7_foundation_questions",
    )
    assert evidence_schema.model is PersonalityEvidence
    assert evidence_schema.collector is collect_personality_evidence
    assert "Người này tự nhiên dễ phản ứng theo hướng nào?" in output_schema.prompt
    assert "Chân dung kể chuyện" in output_schema.prompt


def test_output_schema_is_selected_when_agent_instruction_is_built():
    instruction = build_personality_agent_instruction(
        output_schema="7_foundation_questions"
    )

    assert "Phần 1 - Bảy câu hỏi nền tảng" in instruction
    assert "Phần 2 - Chân dung kể chuyện" in instruction


def test_composite_evidence_tool_matches_the_deterministic_collector():
    la_so = LaSo.from_prior(FIXTURE_PRIOR_A)
    ctx = SimpleNamespace(deps=TuviAgentDeps(la_so=la_so))

    assert get_personality_evidence(ctx) == collect_personality_evidence(la_so)


async def test_run_personality_workflow_makes_one_plain_text_synthesis_call():
    class FakeAgent:
        async def run(self, prompt, *, deps, usage=None):
            self.calls = getattr(self, "calls", 0) + 1
            self.prompt = prompt
            self.deps = deps
            self.usage = usage
            return SimpleNamespace(output=_analysis())

    agent = FakeAgent()
    deps = TuviAgentDeps(la_so=LaSo.from_prior(FIXTURE_PRIOR_A))

    result = await run_personality_workflow(
        agent=agent,
        deps=deps,
        request="Hãy luận tính cách của tôi.",
        usage="shared-usage",
    )

    payload = json.loads(agent.prompt)
    assert agent.calls == 1
    assert agent.deps is deps
    assert agent.usage == "shared-usage"
    assert payload["user_request"] == "Hãy luận tính cách của tôi."
    assert set(payload["evidence"]) == {
        "foundation",
        "vong_thai_tue",
        "b3_b4_context",
        "cach_cuc",
        "phu_tinh",
        "trang_sinh_menh",
        "trang_sinh_than",
    }
    assert result == _analysis()


async def test_workflow_tool_returns_model_text_unchanged():
    class FakeAgent:
        async def run(self, prompt, *, deps, usage=None):
            return SimpleNamespace(output=_analysis())

    deps = TuviAgentDeps(
        personality_agent=FakeAgent(),
        la_so=LaSo.from_prior(FIXTURE_PRIOR_A),
    )
    ctx = SimpleNamespace(deps=deps, usage="usage")

    rendered = await run_tinh_cach_workflow(ctx, "Luận tính cách")

    assert rendered == _analysis()


def test_general_agent_exposes_only_the_composite_personality_skill():
    tools = build_tuvi_agent("test")._function_toolset.tools

    assert "run_tinh_cach_workflow" in tools
    assert "luan_tinh_cach_b1_b2" not in tools
    assert "luan_tinh_cach_b3_b4" not in tools
    assert "luan_tinh_cach_b5_b6_skill" not in tools


def test_personality_agent_can_run_standalone_with_full_toolset():
    agent = build_personality_agent("test")
    tools = agent._function_toolset.tools
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
    assert agent._output_schema.mode == "text"
    assert "Nếu prompt không có evidence" in PERSONALITY_AGENT_INSTRUCTION
    assert "Luôn gọi get_personality_evidence trước" in PERSONALITY_AGENT_INSTRUCTION
    assert "không trả JSON" in PERSONALITY_AGENT_INSTRUCTION
