from __future__ import annotations

import asyncio
from collections import Counter
from types import SimpleNamespace

import pytest
from pydantic import ValidationError
from pydantic_ai import ModelRetry
from pydantic_ai.messages import (
    ModelRequest, ModelResponse, TextPart, ToolCallPart, ToolReturnPart, UserPromptPart,
)
from pydantic_ai.models.function import FunctionModel

from src.agent.book_index import BookIndex
from src.agent.deps import TuviAgentDeps
from src.agent.tool.thai_tue import THAI_TUE_RING_STAR_IDS
from src.agent.workflow.personality_overview import (
    PERSONALITY_OVERVIEW_INPUT,
    PERSONALITY_OVERVIEW_OUTPUT,
    PersonalityOverview,
    build_personality_overview_agent,
    get_personality_overview_evidence,
    render_personality_overview,
    run_personality_overview_agent,
    run_personality_overview_workflow,
)
from src.agent.workflow.personality_overview.input.tanbien import (
    THAN_CU_CONTEXTS,
    get_personality_overview_meaning,
    get_personality_overview_tat_ach_evidence,
)
from src.agent.workflow.personality_overview.input.thai_tue import (
    THAI_TUE_GROUP_MEANINGS,
    THAI_TUE_STAR_MEANINGS,
)
from src.refactored.components.definitions.cung_role import Role
from src.refactored.components.definitions.sao import ChinhPhuTinh, TuanTriet
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import DiaChi
from src.refactored.model.layer import NATAL_LAYER_ID
from src.refactored.model.prior import Gender, LaSoPrior
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
    for hour in DiaChi:
        ctx = _ctx(LaSoPrior(hour=hour, date=1, month=1, year=1984, gender=Gender.MALE))
        la_so = ctx.deps.la_so
        evidence = get_personality_overview_evidence(ctx)
        seen_counts.add(len(evidence.menh.chinh_tinh))
        seen_than.add(evidence.than_cu.palace_role)
        seen_modifiers.update(s.name for s in evidence.menh.tuan_triet)
        seen_ring.add(evidence.thai_tue.star_id)
        assert evidence.menh.vo_chinh_dieu == (not evidence.menh.chinh_tinh)
        assert {p.position for p in evidence.tam_hop} == {
            evidence.menh.position + 4, evidence.menh.position + 8,
        }
        assert evidence.xung_chieu.position == evidence.menh.position + 6
        for palace in [evidence.menh, *evidence.tam_hop, evidence.xung_chieu]:
            components = [la_so.component(cid) for cid in
                          la_so.cung_at(palace.position).components_in_layer(NATAL_LAYER_ID)]
            assert {s.component_id for s in palace.chinh_tinh} == {
                c.id for c in components if isinstance(c, ChinhPhuTinh) and c.is_chinh_tinh
            }
            assert {s.component_id for s in palace.tuan_triet} == {
                c.id for c in components if isinstance(c, TuanTriet)
            }
            assert palace.role != Role.TAT_ACH
            assert "phu_tinh" not in palace.model_dump()
        assert set(evidence.than_cu.model_dump()) == {"palace_role", "application_context", "source"}
        assert "tat_ach" not in evidence.model_dump()
        assert "technical_support" not in evidence.thai_tue.model_dump()
        assert evidence.thai_tue.star_meaning.group_id == evidence.thai_tue.group_meaning.id
    assert seen_counts == {0, 1, 2}
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


def test_scoped_meaning_reads_exact_book_sections_and_reports_missing(tmp_path):
    # Synthetic source content tests retrieval, not the astrological interpretation.
    (tmp_path / "3_chung.md").write_text("3. Chung\nPARENT_OUT_OF_SCOPE", encoding="utf-8")
    (tmp_path / "3_14_pha-quan.md").write_text("3.14. Phá Quân\nGENERIC_TEST", encoding="utf-8")
    (tmp_path / "4_2_14_pha-quan.md").write_text("4.2.14. Phá Quân\nMENH_TEST", encoding="utf-8")
    (tmp_path / "3_2_liem-trinh.md").write_text("3.2. Liêm Trinh\nGENERIC_CHIEU_TEST", encoding="utf-8")
    ctx = _ctx(book=BookIndex(tmp_path))
    meaning = get_personality_overview_meaning(ctx, "pha_quan", Role.MENH)
    assert [(p.section_id, p.scope, p.content) for p in meaning.passages] == [
        ("3.14", "generic", "GENERIC_TEST"), ("4.2.14", "menh", "MENH_TEST"),
    ]
    chieu = get_personality_overview_meaning(ctx, "liem_trinh", Role.THIEN_DI)
    assert [(p.section_id, p.scope) for p in chieu.passages] == [("3.2", "generic")]
    missing_section = get_personality_overview_meaning(ctx, "that_sat", Role.TAI_BACH)
    assert not missing_section.passages and missing_section.missing
    missing_book = get_personality_overview_meaning(
        _ctx(book_root=tmp_path / "absent"), "pha_quan", Role.MENH,
    )
    assert not missing_book.passages and missing_book.missing
    modifier = get_personality_overview_meaning(ctx, "triet_1", Role.THIEN_DI)
    assert not modifier.passages and modifier.missing
    for component_id, role in [
        ("tue_pha", Role.MENH), ("thien_ma", Role.MENH),
        ("liem_trinh", Role.MENH), ("pha_quan", Role.TAT_ACH),
        ("pha_quan", Role.CUNG_THAN),
    ]:
        with pytest.raises(ModelRetry):
            get_personality_overview_meaning(ctx, component_id, role)


def test_tat_ach_requires_reason_and_only_reads_generic_meanings(tmp_path):
    ctx = _ctx(book_root=tmp_path / "absent")
    with pytest.raises(ModelRetry, match="Cần nêu tension"):
        get_personality_overview_tat_ach_evidence(ctx, "  ")
    result = get_personality_overview_tat_ach_evidence(
        ctx, "Khoảng cách giữa muốn đổi cách làm và chần chừ vẫn chưa rõ; xem thêm phản ứng bên trong.",
    )
    assert result.palace.role == Role.TAT_ACH
    assert "Chưa có nguồn diễn giải chuyên biệt" in result.interpretation_note
    assert all(not m.passages and m.missing for m in result.meanings)
    assert {m.component_id for m in result.meanings} == {
        s.component_id for s in result.palace.chinh_tinh
    }
    # Even when a medical section exists, the tool must not expose it.
    for star in result.palace.chinh_tinh:
        from src.agent.tool.tu_vi_tan_bien.constant import get_sao_section_id, get_tat_ach_section_id
        for section_id, content in [
            (get_sao_section_id(star.name), "GENERIC_TEST"),
            (get_tat_ach_section_id(star.name), "MEDICAL_OUT_OF_SCOPE"),
        ]:
            if section_id:
                (tmp_path / f"{section_id.replace('.', '_')}_test.md").write_text(
                    f"{section_id}. Test\n{content}", encoding="utf-8",
                )
    ctx.deps.book = BookIndex(tmp_path)
    result = get_personality_overview_tat_ach_evidence(ctx, "Làm rõ tension bằng góc nhìn nội tâm.")
    assert all(p.scope == "generic" for m in result.meanings for p in m.passages)
    assert "MEDICAL_OUT_OF_SCOPE" not in result.model_dump_json()


@pytest.mark.parametrize("use_tat_ach", [False, True])
def test_real_agent_tool_roundtrip_json_retry_and_optional_tat_ach(use_tat_ach, tmp_path):
    calls, returned_tools = [], set()

    def model(messages, info):
        calls.append(messages)
        returned_tools.update(
            p.tool_name for m in messages for p in m.parts if isinstance(p, ToolReturnPart)
        )
        if "get_personality_overview_evidence" not in returned_tools:
            return ModelResponse(parts=[ToolCallPart("get_personality_overview_evidence", {})])
        if use_tat_ach and "get_personality_overview_tat_ach_evidence" not in returned_tools:
            return ModelResponse(parts=[ToolCallPart("get_personality_overview_tat_ach_evidence", {
                "reason": "Tension chưa rõ giữa suy nghĩ và hành động; xem thêm góc phản ứng bên trong.",
            })])
        # Exercise actual prompted JSON validation/retry, not only a fake runner.
        if len(calls) == 2 + int(use_tat_ach):
            return ModelResponse(parts=[TextPart('{"net_chu_dao": "Chưa đủ field"}')])
        return ModelResponse(parts=[TextPart(_profile().model_dump_json())])

    agent = build_personality_overview_agent(FunctionModel(model))
    assert agent.output_type.outputs is PERSONALITY_OVERVIEW_OUTPUT.output_type
    assert set(agent.toolsets[0].tools) == {
        PERSONALITY_OVERVIEW_INPUT.tool.__name__,
        *(tool.__name__ for tool in PERSONALITY_OVERVIEW_INPUT.supporting_tools),
    }
    profile = asyncio.run(run_personality_overview_agent(
        agent=agent, deps=_ctx(book_root=tmp_path / "absent").deps, request="Luận nét chủ đạo.",
    ))
    assert profile == _profile()
    assert len(calls) == 3 + int(use_tat_ach)
    assert ("get_personality_overview_tat_ach_evidence" in returned_tools) == use_tat_ach


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
    for changes in [
        {"bieu_hien_thuong_thay": ["Chỉ một biểu hiện"]},
        {"bieu_hien_thuong_thay": ["a", "b", "c", "d"]},
        {"net_chu_dao": "  "},
        {"bieu_hien_thuong_thay": ["Hợp lệ", "  "]},
    ]:
        with pytest.raises(ValidationError):
            PersonalityOverview.model_validate({**profile.model_dump(), **changes})
