"""Tử Vi Tân Biên evidence contract for the personality workflow."""

from __future__ import annotations

import logging

from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai import RunContext

from src.agent.deps import TuviAgentDeps
from src.agent.tool.ban_menh.laso_foundation import build_laso_foundation_payload
from src.agent.tool.cach_cuc.matcher import get_cach_cuc_tool_results
from src.agent.tool.cach_cuc.models import CachCucToolResult
from src.agent.tool.personality import build_tinh_cach_b3_b4_context
from src.agent.tool.phu_tinh.tool import (
    PhuTinhGroupedResult,
    TrangSinhResult,
    build_phu_tinh_tam_phuong_tu_chinh,
    build_trang_sinh,
)
from src.agent.tool.thai_tue.vong_thai_tue import build_vong_thai_tue_payload
from src.refactored.components.definitions.cung_role import Role
from src.refactored.la_so import LaSo


_logger = logging.getLogger(__name__)


class AmDuongEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relation: str
    environment_alignment: str
    thinking_consistency: str
    action_style: str
    resilience_pattern: str
    development_focus: str


class BanMenhMeaningEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    aliases: list[str] = Field(default_factory=list)
    symbol: str
    keywords: list[str]
    nature: str
    reading_hint: str


class BanMenhEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    ngu_hanh: str
    meaning: BanMenhMeaningEvidence


class CucEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    ngu_hanh: str


class MenhCucEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relation: str
    meaning: str


class FoundationEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    am_duong_thuan_nghich: AmDuongEvidence
    ban_menh: BanMenhEvidence
    cuc: CucEvidence
    menh_cuc_relation: MenhCucEvidence


class ComponentEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    ngu_hanh: str | None = None


class ThaiTueGroupEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    archetype: str
    overview: str
    reading_lens: str
    trap: str


class ThaiTueStarMeaningEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keywords: list[str]
    at_menh: str
    shadow: str
    reading_hint: str


class ThaiTueMenhEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    position: ComponentEvidence
    thai_tue_star: ComponentEvidence
    group: ThaiTueGroupEvidence
    star_meaning: ThaiTueStarMeaningEvidence


class ThienMaLensEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    element: str
    will_style: str


class ThienMaEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    available: bool
    reason: str | None = None
    star: ComponentEvidence | None = None
    position: ComponentEvidence | None = None
    at_menh: bool | None = None
    lens: ThienMaLensEvidence | None = None
    tuan_triet: list[ComponentEvidence] = Field(default_factory=list)


class SatTinhEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stars: list[ComponentEvidence]


class ThaiTueTechnicalEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ego_and_collaboration_note: str | None = None
    thien_ma: ThienMaEvidence | None = None
    thai_tue_sat_tinh_at_menh: SatTinhEvidence | None = None


class VongThaiTueEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    menh: ThaiTueMenhEvidence
    technical_support: ThaiTueTechnicalEvidence


class PersonalityEvidence(BaseModel):
    """Complete deterministic Tân Biên evidence required by the B1-B6 workflow."""

    model_config = ConfigDict(extra="forbid")

    foundation: FoundationEvidence
    vong_thai_tue: VongThaiTueEvidence
    b3_b4_context: str
    cach_cuc: list[CachCucToolResult]
    phu_tinh: PhuTinhGroupedResult
    trang_sinh_menh: TrangSinhResult
    trang_sinh_than: TrangSinhResult


def collect_personality_evidence(la_so: LaSo) -> PersonalityEvidence:
    """Collect the Tân Biên B1-B6 evidence without model-selected tool calls."""
    _logger.info("Thu thập evidence tính cách B1-B6")
    evidence = PersonalityEvidence(
        foundation=FoundationEvidence.model_validate(
            build_laso_foundation_payload(la_so)
        ),
        vong_thai_tue=VongThaiTueEvidence.model_validate(
            build_vong_thai_tue_payload(la_so)
        ),
        b3_b4_context=build_tinh_cach_b3_b4_context(la_so),
        cach_cuc=get_cach_cuc_tool_results(la_so, filtered_roles=[Role.MENH]),
        phu_tinh=build_phu_tinh_tam_phuong_tu_chinh(la_so, Role.MENH),
        trang_sinh_menh=build_trang_sinh(la_so, Role.MENH),
        trang_sinh_than=build_trang_sinh(la_so, Role.CUNG_THAN),
    )
    _logger.info(
        "Đã thu thập evidence tính cách B1-B6: cach_cuc=%d, phu_tinh=%d, "
        "trang_sinh_menh=%s, trang_sinh_than=%s",
        len(evidence.cach_cuc),
        sum(len(group.stars) for group in evidence.phu_tinh.groups)
        + len(evidence.phu_tinh.khac),
        evidence.trang_sinh_menh.star,
        evidence.trang_sinh_than.star,
    )
    return evidence


def get_personality_evidence(
    ctx: RunContext[TuviAgentDeps],
) -> PersonalityEvidence:
    """Thu thập đầy đủ evidence Tân Biên B1-B6 cho một lần luận độc lập.

    Luôn gọi tool này trước khi luận nếu prompt chưa cung cấp sẵn evidence.
    """
    _logger.info("Tool get_personality_evidence bắt đầu")
    result = collect_personality_evidence(ctx.deps.require_la_so())
    _logger.info("Tool get_personality_evidence hoàn tất")
    return result
