from __future__ import annotations

import asyncio
from collections import Counter
import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError
from pydantic_ai import ModelRetry
from pydantic_ai.messages import (
    ModelRequest, ModelResponse, TextPart, UserPromptPart,
)
from pydantic_ai.models.function import FunctionModel

from tuvi_agent.deps import TuviAgentDeps
from tuvi_agent.tool.thai_tue import THAI_TUE_RING_STAR_IDS
from tuvi_agent.workflow.personality_overview import (
    PERSONALITY_OVERVIEW_INPUT,
    PERSONALITY_OVERVIEW_OUTPUT,
    PersonalityOverview,
    build_personality_overview_agent,
    build_personality_overview_agent_instruction,
    get_personality_overview_evidence,
    render_personality_overview,
    run_personality_overview_agent,
    run_personality_overview_workflow,
)
from tuvi_agent.workflow.personality_overview.input.evidence import (
    THAN_CU_CONTEXTS, PersonalityOverviewEvidence,
)
from tuvi_agent.workflow.personality_overview.input.thai_tue import (
    THAI_TUE_GROUP_MEANINGS,
    THAI_TUE_STAR_MEANINGS,
)
from tuvi_engine.components.definitions.cung_role import Role
from tuvi_engine.components.definitions.map_sao_status import MAP_SAO_STATUS
from tuvi_engine.components.definitions.sao import ChinhPhuTinh, TuanTriet
from tuvi_engine.la_so import LaSo
from tuvi_engine.model.elementary import DiaChi
from tuvi_engine.model.layer import NATAL_LAYER_ID
from tuvi_engine.model.prior import Gender, LaSoPrior
from tests.fixtures.laso_priors import FIXTURE_PRIOR_A


def _ctx(prior=FIXTURE_PRIOR_A, **kwargs):
    return SimpleNamespace(deps=TuviAgentDeps(la_so=LaSo.from_prior(prior), **kwargs))


def _profile():
    return PersonalityOverview(
        net_chu_dao="Bạn có xu hướng xem xét điều chưa hợp lý trước khi quyết định phản ứng.",
        bieu_hien_thuong_thay=[
            "Khi kế hoạch thay đổi, bạn thường muốn hiểu lý do trước khi làm tiếp.",
            "Trong trao đổi, bạn có thể quay lại điểm chưa rõ dù mọi người đã chuyển chủ đề.",
        ],
        mat_con_lai="Nhu cầu làm rõ có thể khiến khó dừng ở một phương án tạm đủ dùng.",
        mot_dieu_dang_de_y="Hãy để ý khi nào việc được tự chọn bước tiếp theo giúp bạn bớt cần làm rõ mọi chi tiết.",
    )


def test_natal_projection_covers_vcd_pairs_modifiers_and_all_than_cu():
    seen_counts, seen_than, seen_modifiers, seen_ring = set(), set(), set(), set()
    seen_than_counts, seen_than_modifiers = set(), set()
    for hour in DiaChi:
        ctx = _ctx(LaSoPrior(hour=hour, date=1, month=1, year=1984, gender=Gender.MALE))
        la_so = ctx.deps.la_so
        evidence = get_personality_overview_evidence(ctx)
        menh, than = evidence.menh, evidence.than.palace
        thai_tue = evidence.thai_tue.knowledge
        seen_counts.add(len(menh.chinh_tinh))
        seen_than_counts.add(len(than.chinh_tinh))
        seen_than.add(evidence.than.palace_role)
        seen_modifiers.update(s.name for s in evidence.tuan_triet.menh.placements)
        seen_than_modifiers.update(s.name for s in evidence.tuan_triet.than.placements)
        seen_ring.add(thai_tue.star_id)
        assert menh.vo_chinh_dieu == (not menh.chinh_tinh)
        assert than.role == evidence.than.palace_role
        assert than.position == la_so.position_of(Role.CUNG_THAN.value, NATAL_LAYER_ID)
        assert evidence.than.same_as_menh == (than.position == menh.position)
        assert evidence.than.application_context == THAN_CU_CONTEXTS[than.role]
        assert evidence.than.basic_combination_id == (
            "__".join(sorted(s.component_id for s in than.chinh_tinh)) or None
        )
        assert "knowledge" not in evidence.than.model_dump()
        assert evidence.thai_tue.position == menh.position
        assert "technical_support" not in thai_tue.model_dump()
        assert thai_tue.star_meaning.group_id == thai_tue.group_meaning.id
        assert menh.xung_chieu.position == menh.position + 6
        assert {p.position for p in menh.tam_hop} == {menh.position + 4, menh.position + 8}
        assert len(menh.tam_hop) == 2
        assert "interpretation" not in menh.xung_chieu.model_dump()
        assert "knowledge" not in menh.model_dump()
        assert "vcd_support" not in menh.model_dump()
        palaces = [menh, than, menh.xung_chieu, *menh.tam_hop]
        if menh.vo_chinh_dieu:
            assert menh.interpretation is None
        else:
            assert menh.interpretation.chinh_tinh == frozenset(s.component_id for s in menh.chinh_tinh)
            assert menh.position in menh.interpretation.dia_chi
        for palace in palaces:
            components = [la_so.component(cid) for cid in
                          la_so.cung_at(palace.position).components_in_layer(NATAL_LAYER_ID)]
            assert {s.component_id for s in palace.chinh_tinh} == {
                c.id for c in components if isinstance(c, ChinhPhuTinh) and c.is_chinh_tinh
            }
            assert "tuan_triet" not in palace.model_dump()
        for layer, palace in (("menh", menh), ("than", than)):
            constraint = getattr(evidence.tuan_triet, layer)
            assert constraint.role == palace.role
            assert constraint.position == palace.position
            assert constraint.applicable_constraints == []
            assert {s.component_id for s in constraint.placements} == {
                cid for cid in la_so.cung_at(palace.position).components_in_layer(NATAL_LAYER_ID)
                if isinstance(la_so.component(cid), TuanTriet)
            }
        if evidence.than.same_as_menh:
            assert than.chinh_tinh == menh.chinh_tinh
            assert evidence.tuan_triet.than == evidence.tuan_triet.menh
        context = json.loads(evidence.model_dump_json())
        assert list(context) == ["menh", "thai_tue", "than", "tuan_triet"]
        assert PersonalityOverviewEvidence.model_validate_json(evidence.model_dump_json()) == evidence
        for key in ("status", "tu_hoa", "technical_support", "tat_ach", "gender", "phu_tinh"):
            assert f'"{key}"' not in json.dumps(context)
    assert seen_counts == {0, 1, 2}
    assert seen_than_counts == {0, 1, 2}
    assert seen_than_modifiers == {"Tuần", "Triệt"}
    assert seen_than == set(THAN_CU_CONTEXTS)
    assert seen_modifiers == {"Tuần", "Triệt"}
    assert seen_ring == set(THAI_TUE_RING_STAR_IDS)
    assert set(THAI_TUE_STAR_MEANINGS) == seen_ring
    assert Counter(s.group_id for s in THAI_TUE_STAR_MEANINGS.values()) == {
        group_id: 3 for group_id in THAI_TUE_GROUP_MEANINGS
    }


def test_missing_menh_is_not_vcd(monkeypatch):
    ctx = _ctx()
    original = type(ctx.deps.la_so).position_of

    def missing_menh(self, component_id, *args, **kwargs):
        return None if component_id == Role.MENH.value else original(self, component_id, *args, **kwargs)

    monkeypatch.setattr(type(ctx.deps.la_so), "position_of", missing_menh)
    with pytest.raises(ModelRetry, match="không thể coi dữ liệu thiếu"):
        get_personality_overview_evidence(ctx)


@pytest.mark.parametrize("hour", list(DiaChi))
def test_evidence_returns_chart_facts_without_reading_books(hour, monkeypatch, tmp_path):
    def forbid_book(self):
        pytest.fail("Personality Overview must not request a book")

    monkeypatch.setattr(TuviAgentDeps, "require_book", forbid_book)
    ctx = _ctx(LaSoPrior(hour=hour, date=1, month=1, year=1984, gender=Gender.MALE),
               book_root=tmp_path / "absent")
    evidence = get_personality_overview_evidence(ctx)
    assert "structural_knowledge" not in evidence.model_dump()
    assert "meanings" not in evidence.model_dump()
    assert "tat_ach" not in evidence.model_dump()
    assert ctx.deps.book is None


def test_evidence_does_not_include_gender():
    prior = FIXTURE_PRIOR_A.model_copy(update={"gender": Gender.FEMALE})
    assert "gender" not in get_personality_overview_evidence(_ctx(prior)).model_dump()


def test_evidence_does_not_depend_on_star_status(monkeypatch):
    monkeypatch.delitem(MAP_SAO_STATUS, "pha_quan")
    evidence = get_personality_overview_evidence(_ctx())
    assert '"status"' not in evidence.model_dump_json()


def test_missing_than_is_not_silently_omitted(monkeypatch):
    ctx = _ctx()
    original = type(ctx.deps.la_so).position_of

    def missing_than(self, component_id, *args, **kwargs):
        return None if component_id == Role.CUNG_THAN.value else original(self, component_id, *args, **kwargs)

    monkeypatch.setattr(type(ctx.deps.la_so), "position_of", missing_than)
    with pytest.raises(ModelRetry, match="Không tìm thấy vị trí Thân cư"):
        get_personality_overview_evidence(ctx)


def test_synthesis_instructions_preserve_scoped_interpretation():
    instruction = " ".join(build_personality_overview_agent_instruction().split())
    for requirement in [
        "không tự gán dữ kiện còn thiếu", "Mệnh Vô Chính Diệu",
        "Thân (Dụng) là phương thức", "Tuần/Triệt tại Thân",
        "Không sử dụng Tật Ách trong Personality Overview",
        "không tự chọn một cực", "Sáu trường cùng một tinh hệ",
        "không lặp hoặc nhân đôi độ chắc chắn", "không viết hai chân dung rời rạc",
        "không tự ghép nghĩa từng sao", "Thân cư Mệnh không đếm hai lần",
        "không gán sao chiếu thành sao tọa Mệnh", "không tạo một khí chất giả",
        "applicable_constraints rỗng không có nghĩa là không có ảnh hưởng",
        "Được vận dụng kiến thức Tử Vi để suy luận ảnh hưởng",
        "không tự suy yếu toàn bộ Mệnh",
        "không đảo cực trục", "không chấm sức mạnh sao",
        "Không dùng Tứ Hóa",
        "Không đánh giá Miếu/Vượng/Đắc/Bình/Hãm như lớp độc lập",
        "Gọi tên khi giúp giải thích", "không tóm tắt lại bài", "khoảng 20–40 từ",
        "Câu hỏi phân tích trong nguồn không phải thói quen tự vấn",
        "không tự chứng minh quan hệ nhân quả hay trình tự trước–sau",
        "không nhất thiết là khuyết điểm", "không tự chế một nhược điểm nhẹ hơn",
    ]:
        assert requirement in instruction
    stages = [instruction.index(f"## {stage}.") for stage in "ABCDE"]
    assert stages == sorted(stages)
    assert "Tự vận dụng kiến thức Tử Vi" not in instruction
    assert "get_personality_overview_tat_ach_evidence" not in instruction
    assert "đoạn sách" not in instruction
    assert set(PersonalityOverview.model_fields) == {
        "net_chu_dao", "bieu_hien_thuong_thay", "mat_con_lai", "mot_dieu_dang_de_y",
    }


@pytest.mark.parametrize("retry_output", [False, True])
def test_real_agent_preloaded_context_without_tools_and_json_retry(retry_output):
    calls = []
    invalid_sent = False
    ctx = _ctx(
        LaSoPrior(hour=DiaChi.SUU, date=1, month=1, year=1984, gender=Gender.MALE),
    )
    expected_context = get_personality_overview_evidence(ctx).model_dump(mode="json")

    def model(messages, info):
        nonlocal invalid_sent
        calls.append(messages)
        assert info.function_tools == []
        context = json.loads(info.instructions.split('\n\n')[-1])
        assert context == expected_context
        if retry_output and not invalid_sent:
            invalid_sent = True
            return ModelResponse(parts=[TextPart('{"net_chu_dao": "Chưa đủ field"}')])
        return ModelResponse(parts=[TextPart(_profile().model_dump_json())])

    agent = build_personality_overview_agent(FunctionModel(model))
    assert agent.output_type.outputs is PERSONALITY_OVERVIEW_OUTPUT.output_type
    assert PERSONALITY_OVERVIEW_INPUT.supporting_tools == ()
    profile = asyncio.run(run_personality_overview_agent(
        agent=agent, deps=ctx.deps, request="Luận nét chủ đạo.",
    ))
    assert profile == _profile()
    assert len(calls) == 1 + retry_output
    assert ctx.deps.book is None


@pytest.mark.parametrize("missing", ["star", "group"])
def test_missing_thai_tue_knowledge_keeps_pipeline_working(missing, monkeypatch):
    ctx = _ctx()
    thai_tue = get_personality_overview_evidence(ctx).thai_tue.knowledge
    if missing == "star":
        monkeypatch.delitem(THAI_TUE_STAR_MEANINGS, thai_tue.star_id)
    else:
        monkeypatch.delitem(THAI_TUE_GROUP_MEANINGS, thai_tue.star_meaning.group_id)

    def model(messages, info):
        context = json.loads(info.instructions.split('\n\n')[-1])
        assert context["thai_tue"]["knowledge"] is None
        assert context["menh"]["interpretation"] is not None
        return ModelResponse(parts=[TextPart(_profile().model_dump_json())])

    agent = build_personality_overview_agent(FunctionModel(model))
    assert asyncio.run(run_personality_overview_agent(
        agent=agent, deps=ctx.deps, request="Luận nét chủ đạo.",
    )) == _profile()


def test_context_is_rebuilt_for_current_chart_when_history_is_reused():
    first, second = _ctx(), _ctx(LaSoPrior(
        hour=DiaChi.SUU, date=1, month=1, year=1984, gender=Gender.MALE,
    ))
    expected = [get_personality_overview_evidence(ctx).model_dump(mode="json") for ctx in (first, second)]
    assert expected[0] != expected[1]
    received = []

    def model(messages, info):
        received.append(json.loads(info.instructions.split('\n\n')[-1]))
        return ModelResponse(parts=[TextPart(_profile().model_dump_json())])

    async def run():
        agent = build_personality_overview_agent(FunctionModel(model))
        result = await agent.run("Luận nét chủ đạo.", deps=first.deps)
        await agent.run("Luận lá số mới.", deps=second.deps, message_history=result.all_messages())

    asyncio.run(run())
    assert received == expected


def test_base_evidence_does_not_access_tat_ach(monkeypatch):
    ctx = _ctx()
    original = type(ctx.deps.la_so).position_of

    def missing_tat_ach(self, component_id, *args, **kwargs):
        if component_id == Role.TAT_ACH.value:
            pytest.fail("Personality Overview must not access Tật Ách")
        return original(self, component_id, *args, **kwargs)

    monkeypatch.setattr(type(ctx.deps.la_so), "position_of", missing_tat_ach)
    assert "tat_ach" not in get_personality_overview_evidence(ctx).model_dump()
    assert '"tat_ach"' not in get_personality_overview_evidence(ctx).model_dump_json()


def test_rendering_and_runner_preserve_profile_usage_history():
    profile = _profile()
    deps = _ctx().deps
    history = [ModelRequest(parts=[UserPromptPart(content="Ngữ cảnh trước.")])]
    calls = []

    class FakeAgent:
        async def run(self, prompt, **kwargs):
            calls.append((prompt, kwargs))
            return SimpleNamespace(output=profile)

    result = asyncio.run(run_personality_overview_workflow(
        agent=FakeAgent(), deps=deps, request="Luận nét chủ đạo.",
        usage="shared", message_history=history,
    ))
    assert calls == [("Luận nét chủ đạo.", {
        "deps": deps, "usage": "shared", "message_history": history,
    })]
    assert result == render_personality_overview(profile)
    assert [line for line in result.splitlines() if line.startswith("### ")] == [
        "### Nét chủ đạo", "### Biểu hiện thường thấy", "### Mặt còn lại", "### Một điều đáng để ý",
    ]
    assert result.endswith(profile.mot_dieu_dang_de_y)
    assert PersonalityOverview.model_validate({
        **profile.model_dump(), "bieu_hien_thuong_thay": ["Một biểu hiện đủ căn cứ"],
    }).bieu_hien_thuong_thay == ["Một biểu hiện đủ căn cứ"]
    for changes in [
        {"bieu_hien_thuong_thay": []},
        {"bieu_hien_thuong_thay": ["a", "b", "c"]},
        {"bieu_hien_thuong_thay": ["a", "b", "c", "d"]},
        {"net_chu_dao": "  "},
        {"bieu_hien_thuong_thay": ["Hợp lệ", "  "]},
    ]:
        with pytest.raises(ValidationError):
            PersonalityOverview.model_validate({**profile.model_dump(), **changes})
