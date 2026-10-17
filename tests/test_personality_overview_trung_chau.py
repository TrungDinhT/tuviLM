"""Check research fidelity and selection against every natal star arrangement."""

from pathlib import Path
import re

import pytest
from pydantic_ai import ModelRetry

from tuvi_agent.workflow.personality_overview import build_personality_overview_agent_instruction
from tuvi_agent.workflow.personality_overview.input.evidence import PalaceEvidence, StarEvidence
from tuvi_agent.workflow.personality_overview.input.trung_chau import (
    TRUNG_CHAU_STAR_SYSTEMS,
    _SYSTEM_BY_PLACEMENT,
    get_interpretation_basis,
)
from tuvi_engine.components.definitions.cung_role import Role
from tuvi_engine.context.natal import NatalContext
from tuvi_engine.model.elementary import DiaChi
from tuvi_engine.placement.compiler import (
    PlacementRuleCompiler, SpecializedAbsoluteSpec, SpecializedPlacementRules,
)
from tuvi_engine.placement.engine import PlacementEngine
from tuvi_engine.placement.rules.loader import load_rule_group
from tests.fixtures.laso_priors import FIXTURE_PRIOR_A


def test_all_records_match_merged_markdown():
    research = (Path(__file__).parents[1] / "packages/tuvi-agent/src/tuvi_agent/workflow/personality_overview"
                / "tuviLM_60_tinh_he_merged.md").read_text(encoding="utf-8")
    sections = re.findall(r"^### TH\d+ · ([^\n]+)\n(.*?)(?=^### |^## |\Z)", research, re.M | re.S)
    assert len(sections) == len(TRUNG_CHAU_STAR_SYSTEMS) == 60
    labels = {
        "axis_classical_vi": "Trục tính chất (Trung Châu, bản tiếng Việt)",
        "axis_interpretation": "Giải thích trục tính chất (diễn giải tuviLM)",
        "core_temperament": "Khí chất chủ đạo",
        "personality_mechanism": "Cơ chế (giả thuyết biên tập)",
        "observable_hypothesis": "Biểu hiện khả dĩ (có điều kiện)",
        "weakness": "Điểm yếu / dễ lệch",
    }
    records = {record.title: record for record in TRUNG_CHAU_STAR_SYSTEMS}
    assert len(records) == 60
    seen = set()
    for title, section in sections:
        system_id = re.search(r"\*\*System ID:\*\* `([^`]+)`", section)[1]
        record = records[title.strip()]
        seen.add(record.title)
        *members, branch_pair = system_id.split("__")
        assert record.chinh_tinh == frozenset(members)
        assert tuple(branch.value for branch in record.dia_chi) == tuple(
            "meo" if branch == "mao" else branch for branch in branch_pair.split("_")
        )
        for field, label in labels.items():
            value = re.search(r"\*\*" + re.escape(label) + r":\*\* (.+)", section)[1]
            assert getattr(record, field) == value.strip(), (system_id, field)
    assert seen == {record.title for record in TRUNG_CHAU_STAR_SYSTEMS}


def test_selection_covers_all_60_systems_and_vcd_without_borrowing():
    compiler = PlacementRuleCompiler()
    compiler.register_rules(load_rule_group("chinh_tinh"))
    rules = compiler.compile(NatalContext.from_prior(FIXTURE_PRIOR_A))
    seen, vcd_count = set(), 0
    for anchor in DiaChi:
        positions = PlacementEngine(SpecializedPlacementRules(specs={
            **rules.specs, "tu_vi": SpecializedAbsoluteSpec(lambda p=anchor: p),
        })).resolve_all()
        for position in DiaChi:
            menh = PalaceEvidence(
                role=Role.MENH, position=position,
                chinh_tinh=[StarEvidence(component_id=cid, name=cid)
                            for cid, pos in positions.items() if pos == position],
            )
            record = get_interpretation_basis(menh)
            if not menh.chinh_tinh:
                vcd_count += 1
                assert record is None
                continue
            assert record is not None
            seen.add(record.title)
            assert record.chinh_tinh == frozenset(s.component_id for s in menh.chinh_tinh)
            assert position in record.dia_chi
            menh.chinh_tinh.reverse()
            assert get_interpretation_basis(menh) == record
    assert vcd_count > 0
    assert seen == {record.title for record in TRUNG_CHAU_STAR_SYSTEMS}


def test_placement_keys_are_unique_and_cover_both_branches():
    assert len(_SYSTEM_BY_PLACEMENT) == 120
    for record in TRUNG_CHAU_STAR_SYSTEMS:
        assert len(set(record.dia_chi)) == 2
        assert all(_SYSTEM_BY_PLACEMENT[(record.chinh_tinh, branch)] is record
                   for branch in record.dia_chi)


def test_vcd_has_no_interpretation_and_unknown_star_system_is_rejected():
    menh = PalaceEvidence(role=Role.MENH, position=DiaChi.TY, chinh_tinh=[])
    invalid_menh = PalaceEvidence(
        role=Role.MENH, position=DiaChi.SUU,
        chinh_tinh=[StarEvidence(component_id="tu_vi", name="Tử Vi")],
    )
    assert get_interpretation_basis(menh) is None
    with pytest.raises(ModelRetry, match="Không tìm thấy tinh hệ Trung Châu"):
        get_interpretation_basis(invalid_menh)


def test_agent_receives_trung_chau_usage_boundaries():
    instruction = " ".join(build_personality_overview_agent_instruction().split())
    for requirement in (
        "menh.interpretation", "không tự chọn một cực", "không bê nguyên bản ghi đối cung",
        "Thân cư Mệnh không đếm hai lần", "không tự thêm Tứ Hóa",
    ):
        assert requirement in instruction
