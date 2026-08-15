from __future__ import annotations

import datetime as dt
import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError
from pydantic_ai.messages import ModelRequest, UserPromptPart

from src.agent.deps import TuviAgentDeps
from src.agent.main import build_tuvi_agent
from src.agent.tool.strength_weakness import (
    TINH_HE_DEFINITIONS,
    TinhHeScope,
    build_cung_bo_sung_evidence,
    build_menh_than_evidence,
    build_tinh_he_evidence,
)
from src.agent.workflow.strength_weakness import (
    DEFAULT_STRENGTH_WEAKNESS_CONFIG,
    STRENGTH_WEAKNESS_AGENT_INSTRUCTION,
    STRENGTH_WEAKNESS_INPUT_REGISTRY,
    STRENGTH_WEAKNESS_OUTPUT_INSTRUCTION_REGISTRY,
    StrengthWeaknessAgentConfig,
    StrengthWeaknessAssessment,
    StrengthWeaknessBases,
    StrengthWeaknessBasis,
    StrengthWeaknessDimension,
    StrengthWeaknessEvidence,
    StrengthWeaknessExplanation,
    StrengthWeaknessLevel,
    StrengthWeaknessScores,
    build_strength_weakness_agent,
    build_strength_weakness_agent_instruction,
    get_strength_weakness_evidence,
    run_strength_weakness_agent,
    run_strength_weakness_workflow,
)
from src.refactored.components.definitions.cung_role import Role
from src.refactored.la_so import LaSo
from src.refactored.model.prior import Gender, LaSoPrior
from tests.fixtures.laso_priors import FIXTURE_PRIOR_A


pytestmark = pytest.mark.anyio


def _all_scores(level: StrengthWeaknessLevel) -> StrengthWeaknessScores:
    return StrengthWeaknessScores(
        **{dimension.value: level for dimension in StrengthWeaknessDimension}
    )


def _all_bases(basis: StrengthWeaknessBasis) -> StrengthWeaknessBases:
    return StrengthWeaknessBases(
        **{dimension.value: basis for dimension in StrengthWeaknessDimension}
    )


def _assessment() -> StrengthWeaknessAssessment:
    return StrengthWeaknessAssessment(
        scores=_all_scores(StrengthWeaknessLevel.NORMAL),
        score_bases=_all_bases(StrengthWeaknessBasis.INSUFFICIENT_EVIDENCE),
        overview=(
            "Chưa có tín hiệu đủ mạnh để profile lệch khỏi vùng bình thường."
        ),
    )


def test_composite_input_builds_only_declared_strength_weakness_evidence():
    ctx = SimpleNamespace(
        deps=TuviAgentDeps(la_so=LaSo.from_prior(FIXTURE_PRIOR_A))
    )

    evidence = get_strength_weakness_evidence(ctx)

    assert isinstance(evidence, StrengthWeaknessEvidence)
    assert [item.cung_goc for item in evidence.menh_than] == [
        Role.MENH,
        Role.CUNG_THAN,
    ]
    assert len(evidence.tu_hoa) == 4
    assert {item.tu_hoa_id for item in evidence.tu_hoa} == {
        "hoa_loc",
        "hoa_quyen",
        "hoa_khoa",
        "hoa_ky",
    }
    assert evidence.sao_can_tra_cuu
    assert {
        item.ten
        for item in evidence.phu_tinh_tuan_triet
        if item.loai.value == "phu_tinh"
    } <= set(evidence.sao_can_tra_cuu)
    assert "foundation" not in type(evidence).model_fields
    assert "cach_cuc" not in type(evidence).model_fields


def test_evidence_schema_uses_tu_vi_domain_vocabulary():
    schema = StrengthWeaknessEvidence.model_json_schema()
    schema_text = json.dumps(schema)

    assert set(schema["properties"]) == {
        "menh_than",
        "tinh_he",
        "tu_hoa",
        "phu_tinh_tuan_triet",
        "sao_can_tra_cuu",
    }
    assert "TuHoaEvidence" in schema["$defs"]
    assert "TinhHeEvidence" in schema["$defs"]
    assert "transformation" not in schema_text.lower()
    assert "pattern" not in schema_text.lower()
    assert "palace" not in schema_text.lower()


def test_tinh_he_uses_narrowest_scope_for_each_anchor_and_entry():
    la_so = LaSo.from_prior(FIXTURE_PRIOR_A)

    menh_tinh_he = {
        item.tinh_he_id: item
        for item in build_tinh_he_evidence(
            la_so,
            anchors=(Role.MENH,),
        )
    }
    than_tinh_he = {
        item.tinh_he_id: item
        for item in build_tinh_he_evidence(
            la_so,
            anchors=(Role.CUNG_THAN,),
        )
    }
    phuc_tinh_he = {
        item.tinh_he_id: item
        for item in build_tinh_he_evidence(
            la_so,
            anchors=(Role.PHUC_DUC,),
        )
    }

    assert (
        menh_tinh_he["sat_pha_liem_tham"].pham_vi
        is TinhHeScope.TAM_PHUONG_TU_CHINH
    )
    assert (
        than_tinh_he["tu_phu_vu_tuong"].pham_vi
        is TinhHeScope.TAM_PHUONG
    )
    assert phuc_tinh_he["tu_phu"].pham_vi is TinhHeScope.DONG_CUNG


def test_tinh_he_catalog_is_workflow_owned_and_limited_to_declared_entries():
    assert [definition.id for definition in TINH_HE_DEFINITIONS] == [
        "tu_phu_vu_tuong",
        "sat_pha_tham",
        "sat_pha_liem_tham",
        "co_nguyet_dong_luong",
        "cu_nhat",
        "co_cu",
        "co_luong",
        "tu_phu",
        "phu_tuong",
        "vu_tuong",
        "nhat_nguyet",
    ]


def test_menh_and_than_are_separate_when_than_menh_dong_cung():
    prior = LaSoPrior.from_solar_day(
        dt.datetime(1990, 5, 15, 0),
        Gender.MALE,
    )
    structures = build_menh_than_evidence(LaSo.from_prior(prior))

    assert structures[0].dia_chi == structures[1].dia_chi
    assert structures[0].cung_goc is Role.MENH
    assert structures[1].cung_goc is Role.CUNG_THAN


def test_context_tool_is_restricted_and_typed():
    la_so = LaSo.from_prior(FIXTURE_PRIOR_A)

    context = build_cung_bo_sung_evidence(la_so, "phuc_duc")

    assert context.cau_truc_cung.cung_goc is Role.PHUC_DUC
    assert any(item.tinh_he_id == "tu_phu" for item in context.tinh_he)
    with pytest.raises(ValueError, match="Cung bổ sung"):
        build_cung_bo_sung_evidence(la_so, "quan_loc")  # type: ignore[arg-type]


def test_output_contract_distinguishes_normal_score_bases():
    assessment = _assessment()

    assert assessment.scores.analysis_reasoning is StrengthWeaknessLevel.NORMAL
    assert (
        assessment.score_bases.analysis_reasoning
        is StrengthWeaknessBasis.INSUFFICIENT_EVIDENCE
    )


def test_balanced_conflict_requires_a_matching_explanation():
    bases = _all_bases(StrengthWeaknessBasis.INSUFFICIENT_EVIDENCE)
    bases.decision_making = StrengthWeaknessBasis.BALANCED_CONFLICT

    with pytest.raises(ValidationError, match="requires an explanation"):
        StrengthWeaknessAssessment(
            scores=_all_scores(StrengthWeaknessLevel.NORMAL),
            score_bases=bases,
            overview="Có một giằng co đáng chú ý.",
        )

    assessment = StrengthWeaknessAssessment(
        scores=_all_scores(StrengthWeaknessLevel.NORMAL),
        score_bases=bases,
        overview="Có một giằng co đáng chú ý.",
        notable_dimensions=[
            StrengthWeaknessExplanation(
                dimension=StrengthWeaknessDimension.DECISION_MAKING,
                level=StrengthWeaknessLevel.NORMAL,
                summary="Bạn cân nhắc tốt nhưng thận trọng khi chốt.",
                reasoning="Hai nhóm evidence trực tiếp kéo theo hai hướng.",
            )
        ],
    )

    assert (
        assessment.notable_dimensions[0].dimension
        is StrengthWeaknessDimension.DECISION_MAKING
    )


def test_non_normal_score_requires_supported_basis():
    scores = _all_scores(StrengthWeaknessLevel.NORMAL)
    scores.analysis_reasoning = StrengthWeaknessLevel.GOOD

    with pytest.raises(ValidationError, match="must be supported"):
        StrengthWeaknessAssessment(
            scores=scores,
            score_bases=_all_bases(
                StrengthWeaknessBasis.INSUFFICIENT_EVIDENCE
            ),
            overview="Phân tích nổi bật.",
        )


def test_workflow_registry_and_prompt_enforce_llm_scoring():
    input_definition = STRENGTH_WEAKNESS_INPUT_REGISTRY["default"]
    output_instruction = STRENGTH_WEAKNESS_OUTPUT_INSTRUCTION_REGISTRY["radar"]

    assert DEFAULT_STRENGTH_WEAKNESS_CONFIG == StrengthWeaknessAgentConfig()
    assert input_definition.model is StrengthWeaknessEvidence
    assert input_definition.tool is get_strength_weakness_evidence
    assert output_instruction.output_type is StrengthWeaknessAssessment
    assert (
        "Scoring là trách nhiệm 100% của model"
        in STRENGTH_WEAKNESS_AGENT_INSTRUCTION
    )
    assert "Bắt buộc gọi `search_star_info`" in STRENGTH_WEAKNESS_AGENT_INSTRUCTION
    assert "`sao_can_tra_cuu`" in STRENGTH_WEAKNESS_AGENT_INSTRUCTION
    assert "Completion gate" in STRENGTH_WEAKNESS_AGENT_INSTRUCTION
    assert "không dùng output tool" in STRENGTH_WEAKNESS_AGENT_INSTRUCTION
    assert "ý nghĩa trừu tượng của từng" in STRENGTH_WEAKNESS_AGENT_INSTRUCTION
    assert "không ánh xạ từng sao" in STRENGTH_WEAKNESS_AGENT_INSTRUCTION
    assert (
        "Bắt đầu cả 11 dimension ở NORMAL"
        not in STRENGTH_WEAKNESS_AGENT_INSTRUCTION
    )
    assert "action_execution" in STRENGTH_WEAKNESS_AGENT_INSTRUCTION
    assert "action_completion" not in STRENGTH_WEAKNESS_AGENT_INSTRUCTION


def test_strength_weakness_level_scale_has_nine_ordered_choices():
    assert [level.value for level in StrengthWeaknessLevel] == [
        "nearly_absent",
        "very_weak",
        "weak",
        "improvable",
        "normal",
        "above_normal",
        "good",
        "very_good",
        "excellent",
    ]
    for level in StrengthWeaknessLevel:
        assert f"`{level.value}`" in STRENGTH_WEAKNESS_AGENT_INSTRUCTION


def test_unknown_build_time_input_is_rejected():
    with pytest.raises(ValueError, match="Unknown strength/weakness input"):
        build_strength_weakness_agent_instruction(
            StrengthWeaknessAgentConfig(input_name="missing")
        )


async def test_runner_preserves_structured_output_and_forwards_context():
    expected = _assessment()

    class FakeAgent:
        async def run(
            self,
            prompt,
            *,
            deps,
            usage=None,
            message_history=None,
        ):
            self.prompt = prompt
            self.deps = deps
            self.usage = usage
            self.message_history = message_history
            return SimpleNamespace(output=expected)

    agent = FakeAgent()
    deps = TuviAgentDeps(la_so=LaSo.from_prior(FIXTURE_PRIOR_A))
    history = [ModelRequest(parts=[UserPromptPart(content="Câu trước")])]

    result = await run_strength_weakness_agent(
        agent=agent,
        deps=deps,
        request="Đánh giá điểm mạnh điểm yếu",
        usage="shared-usage",
        message_history=history,
    )

    assert result is expected
    assert agent.deps is deps
    assert agent.usage == "shared-usage"
    assert agent.message_history is history


async def test_composite_workflow_tool_returns_structured_output_unchanged():
    expected = _assessment()

    class FakeAgent:
        async def run(self, prompt, **kwargs):
            self.prompt = prompt
            self.kwargs = kwargs
            return SimpleNamespace(output=expected)

    history = [ModelRequest(parts=[UserPromptPart(content="Câu trước")])]
    sub_agent = FakeAgent()
    deps = TuviAgentDeps(
        strength_weakness_agent=sub_agent,
        la_so=LaSo.from_prior(FIXTURE_PRIOR_A),
        message_history=history,
    )

    result = await run_strength_weakness_workflow(
        SimpleNamespace(deps=deps, usage="usage"),
        "Điểm mạnh điểm yếu của tôi",
    )

    assert result is expected
    assert sub_agent.prompt == "Điểm mạnh điểm yếu của tôi"
    assert sub_agent.kwargs["message_history"] is history


def test_agent_tool_placement_matches_workflow_contract():
    main_tools = build_tuvi_agent("test").toolsets[0].tools
    sub_agent = build_strength_weakness_agent("test")
    sub_tools = sub_agent.toolsets[0].tools

    assert "run_strength_weakness_workflow" in main_tools
    assert set(sub_tools) == {
        "get_strength_weakness_evidence",
        "get_strength_weakness_cung_bo_sung",
        "search_star_info",
        "get_star_role_interaction",
    }
    assert sub_agent.output_type is StrengthWeaknessAssessment
