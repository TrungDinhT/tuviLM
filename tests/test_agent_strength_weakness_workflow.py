from __future__ import annotations

import asyncio
import json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.usage import RunUsage

from src.agent.book_index import BookIndex, SectionContent
from src.agent.deps import TuviAgentDeps
from src.agent.workflow.strength_weakness import (
    CapabilityEvidence,
    CapabilityProfile,
    StrengthFinding,
    build_strength_weakness_agent,
    render_capability_profile,
    run_strength_weakness_agent,
    run_strength_weakness_workflow,
)
from src.agent.workflow.strength_weakness import agent as workflow_module
from src.agent.workflow.strength_weakness.input import (
    CapabilityInput,
    build_strength_weakness_evidence,
    prepare_capability_input,
)
from src.refactored.components.definitions.cung_role import Role
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import DiaChi
from src.refactored.model.layer import NATAL_LAYER_ID
from tests.fixtures.laso_priors import FIXTURE_PRIOR_A


def _referenced_sections(value):
    """Collect references from serialized evidence, independently of its layout."""
    if isinstance(value, dict):
        return [ref['section_id'] for ref in value.get('meaning_references', [])] + [
            section_id for nested in value.values() for section_id in _referenced_sections(nested)
        ]
    if isinstance(value, list):
        return [section_id for item in value for section_id in _referenced_sections(item)]
    return []


@pytest.mark.parametrize('chat', [False, True], ids=['structured', 'chat'])
def test_workflow_preloads_separate_book_sections(chat, monkeypatch):
    profile = CapabilityProfile(
        tong_quan='Hồ sơ năng lực mẫu.',
        diem_manh=[StrengthFinding(
            nang_luc_id='quan_sat_chi_tiet',
            mo_ta='Bạn nhận ra những chi tiết nhỏ.',
            giai_thich='Luận giải mẫu dựa trên evidence.',
        )],
    )
    sections_read = []
    expected_reads = Counter()
    step = 0
    evidence_builds = []
    build_evidence = workflow_module.build_strength_weakness_evidence

    def record_evidence_build(la_so):
        evidence = build_evidence(la_so)
        evidence_builds.append(evidence)
        return evidence

    monkeypatch.setattr(workflow_module, 'build_strength_weakness_evidence', record_evidence_build)

    def read_book_section(section_id):
        sections_read.append(section_id)
        return SectionContent(
            id=section_id,
            title='Mục sách mẫu',
            breadcrumb=f'Tân Biên > {section_id}',
            content=f'Nội dung mục {section_id}',
        )

    def check_books(prepared):
        section_ids = set(_referenced_sections(prepared.evidence.model_dump()))
        assert section_ids
        assert set(prepared.book_sections) == section_ids
        for section_id, section in prepared.book_sections.items():
            assert section.id == section_id
            assert section.title == 'Mục sách mẫu'
            assert section.breadcrumb == f'Tân Biên > {section_id}'
            assert section.content == f'Nội dung mục {section_id}'
        expected_reads.update(section_ids)
        assert Counter(sections_read) == expected_reads

    def respond(messages, info):
        nonlocal step
        step += 1
        assert step == 1
        assert not info.function_tools
        assert len(evidence_builds) == 1
        prompt = next(
            part.content
            for message in messages if isinstance(message, ModelRequest)
            for part in message.parts if isinstance(part, UserPromptPart)
        )
        request, payload = prompt.split('\n\n## Dữ liệu đầu vào (CapabilityInput)\n', 1)
        assert request == 'Phân tích năng lực'
        assert set(json.loads(payload)) == {'evidence', 'book_sections'}
        prepared = CapabilityInput.model_validate_json(payload)
        assert isinstance(prepared.evidence, CapabilityEvidence)
        assert prepared.evidence == evidence_builds[0]
        assert {Role.PHUC_DUC, Role.TAT_ACH} <= {p.role for p in prepared.evidence.palaces}
        refs = _referenced_sections(prepared.evidence.model_dump())
        assert len(refs) > len(set(refs))  # Fixture exercises duplicate references.
        check_books(prepared)
        return ModelResponse(parts=[TextPart(profile.model_dump_json(exclude_computed_fields=True))])

    agent = build_strength_weakness_agent('test')
    deps = TuviAgentDeps(
        strength_weakness_agent=agent,
        la_so=LaSo.from_prior(FIXTURE_PRIOR_A),
        book=SimpleNamespace(read_section=read_book_section),
    )
    usage = RunUsage()
    with agent.override(model=FunctionModel(respond)):
        if chat:
            result = asyncio.run(run_strength_weakness_workflow(
                SimpleNamespace(deps=deps, usage=usage), 'Phân tích năng lực',
            ))
            assert result == render_capability_profile(profile)
        else:
            result = asyncio.run(run_strength_weakness_agent(
                agent=agent, deps=deps, request='Phân tích năng lực', usage=usage,
            ))
            assert result == profile
    assert len(evidence_builds) == 1
    assert step == usage.requests == 1


def test_missing_book_section_fails_before_model_request():
    def missing_section(section_id):
        raise ValueError(f'Unknown section id: {section_id}')

    agent = SimpleNamespace(run=AsyncMock())
    deps = TuviAgentDeps(
        la_so=LaSo.from_prior(FIXTURE_PRIOR_A),
        book=SimpleNamespace(read_section=missing_section),
    )
    with pytest.raises(ValueError, match='Unknown section id:'):
        asyncio.run(run_strength_weakness_agent(agent=agent, deps=deps, request='Phân tích năng lực'))
    agent.run.assert_not_called()


@pytest.fixture(scope="module")
def capability_book():
    return BookIndex(Path(__file__).resolve().parents[1] / "data/tuvitanbien_chunking_compact/part_2")


@pytest.mark.parametrize("hour", list(DiaChi))
def test_fixed_palaces_and_books_are_complete_without_duplicate_palaces(hour, capability_book):
    chart = LaSo.from_prior(FIXTURE_PRIOR_A.model_copy(update={"hour": hour}))
    evidence = build_strength_weakness_evidence(chart)
    menh = chart.tinh_ban.menh_position
    than = chart.tinh_ban.than_position
    expected_positions = {
        menh, than, menh + 4, menh + 8, menh + 6,
        chart.position_of(Role.PHUC_DUC.value, NATAL_LAYER_ID),
        chart.position_of(Role.TAT_ACH.value, NATAL_LAYER_ID),
    }
    positions = [palace.position for palace in evidence.palaces]
    assert set(positions) == expected_positions
    assert len(positions) == len(expected_positions)
    assert {Role.PHUC_DUC, Role.TAT_ACH} <= {palace.role for palace in evidence.palaces}
    assert next(palace for palace in evidence.palaces if palace.position == than).is_cung_than
    assert len({item.evidence_id for item in evidence.cach_cuc}) == len(evidence.cach_cuc)

    prepared = prepare_capability_input(evidence, capability_book)
    assert prepared.evidence == evidence
    assert set(prepared.book_sections) == set(_referenced_sections(evidence.model_dump()))
    for role in (Role.PHUC_DUC, Role.TAT_ACH):
        palace = next(palace for palace in evidence.palaces if palace.role == role)
        refs = _referenced_sections(palace.model_dump())
        assert refs
        assert all(prepared.book_sections[section_id].content for section_id in refs)
