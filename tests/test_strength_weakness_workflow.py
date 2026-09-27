from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError
from pydantic_ai import ModelRetry
from pydantic_ai.models.test import TestModel

from src.agent.book_index import SectionContent
from src.agent.deps import TuviAgentDeps
from src.agent.main import build_tuvi_agent
from src.agent.workflow.strength_weakness import (
    CapabilityProfile,
    StrengthFinding,
    build_strength_weakness_agent,
    build_strength_weakness_evidence,
    render_capability_profile,
    run_strength_weakness_agent,
)
from src.agent.workflow.strength_weakness.agent import run_strength_weakness_workflow
from src.agent.workflow.strength_weakness.input.tanbien import prepare_capability_input
from src.refactored.components.definitions.cung_role import Role
from src.refactored.la_so import LaSo
from tests.fixtures.laso_priors import FIXTURE_PRIOR_A


class RecordingBook:
    def __init__(self):
        self.reads = []

    def read_section(self, section_id):
        self.reads.append(section_id)
        return SectionContent(
            id=section_id, title="Tham chiếu", breadcrumb="Sách", content="Nội dung sách"
        )


def test_evidence_contains_foundation_and_supporting_palaces():
    chart = LaSo.from_prior(FIXTURE_PRIOR_A)
    evidence = build_strength_weakness_evidence(chart)
    positions = {palace.position for palace in evidence.palaces}
    menh = chart.tinh_ban.menh_position
    assert {menh, menh + 4, menh + 6, menh + 8, chart.tinh_ban.than_position} <= positions
    assert {Role.PHUC_DUC, Role.TAT_ACH} <= {palace.role for palace in evidence.palaces}
    assert evidence.tu_hoa
    assert all(item.target_star_id for item in evidence.tu_hoa)
    book = RecordingBook()
    prepared = prepare_capability_input(evidence, book)
    assert len(book.reads) == len(set(book.reads)) > 0
    assert set(prepared.book_sections) == set(book.reads)
    assert prepared.evidence == evidence


def test_profile_rejects_unknown_and_duplicate_capabilities():
    with pytest.raises(ValidationError):
        StrengthFinding(nang_luc_id="unknown", mo_ta="Mô tả", giai_thich="Giải thích")
    finding = StrengthFinding(nang_luc_id="quyet_doan", mo_ta="Mô tả", giai_thich="Giải thích")
    with pytest.raises(ValidationError, match="unique"):
        CapabilityProfile(tong_quan="Tổng quan", diem_manh=[finding, finding])
    assert finding.model_dump()["nang_luc"]


def test_agent_receives_prepared_evidence_and_book_before_running():
    profile = CapabilityProfile(tong_quan="Kết luận từ dữ kiện")
    book = RecordingBook()
    deps = TuviAgentDeps(la_so=LaSo.from_prior(FIXTURE_PRIOR_A), book=book)

    class RecordingAgent:
        async def run(self, prompt, **kwargs):
            assert book.reads
            payload = json.loads(prompt.split("(CapabilityInput)\n", 1)[1])
            assert payload["evidence"]["palaces"]
            assert set(payload["book_sections"]) == set(book.reads)
            assert kwargs["deps"] is deps
            assert kwargs["usage"] == "shared usage"
            return SimpleNamespace(output=profile)

    agent = RecordingAgent()
    result = asyncio.run(run_strength_weakness_agent(
        agent=agent, deps=deps, request="Phân tích năng lực", usage="shared usage"
    ))
    assert result is profile
    deps.strength_weakness_agent = agent
    rendered = asyncio.run(run_strength_weakness_workflow(
        SimpleNamespace(deps=deps, usage="shared usage"), "Phân tích năng lực"
    ))
    assert rendered == render_capability_profile(profile)
    assert "Chưa có đủ căn cứ" in rendered


def test_agents_build_without_credentials_and_workflow_is_registered():
    agent = build_tuvi_agent(TestModel())
    assert "run_strength_weakness_workflow" in agent._function_toolset.tools
    build_strength_weakness_agent(TestModel())
    with pytest.raises(ModelRetry, match="chưa được gán"):
        TuviAgentDeps().require_strength_weakness_agent()
