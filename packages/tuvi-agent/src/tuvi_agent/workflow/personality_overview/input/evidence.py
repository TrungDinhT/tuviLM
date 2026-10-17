"""Natal chart facts and Thái Tuế meaning for personality overview."""

from __future__ import annotations

import logging

from pydantic import BaseModel, Field, computed_field
from pydantic_ai import ModelRetry, RunContext

from tuvi_agent.deps import TuviAgentDeps
from tuvi_agent.workflow.personality_overview.input.thai_tue import (
    ThaiTueEvidence,
    build_overview_thai_tue,
)
from tuvi_engine.components.definitions.cung_role import Role
from tuvi_engine.components.definitions.sao import ChinhPhuTinh, TuanTriet
from tuvi_engine.la_so import LaSo
from tuvi_engine.model.elementary import DiaChi
from tuvi_engine.model.layer import NATAL_LAYER_ID

from . import trung_chau

_logger = logging.getLogger(__name__)

# Application contexts from the user's framework, not inferred accomplishments.
THAN_CU_CONTEXTS = {
    Role.MENH: "Phát triển và thể hiện bản thân",
    Role.QUAN_LOC: "Công việc, thành tựu, trách nhiệm",
    Role.TAI_BACH: "Nguồn lực, tài chính, sự tự chủ vật chất",
    Role.THIEN_DI: "Môi trường bên ngoài, xã hội, trải nghiệm",
    Role.PHU_THE: "Quan hệ gắn bó, đồng hành, cam kết",
    Role.PHUC_DUC: "Đời sống tinh thần, giá trị cá nhân, sự bình ổn nội tâm",
}


class StarEvidence(BaseModel):
    component_id: str
    name: str


class TuanTrietEvidence(BaseModel):
    component_id: str
    name: str


class PalaceEvidence(BaseModel):
    role: Role
    position: DiaChi
    chinh_tinh: list[StarEvidence]

    @computed_field
    @property
    def vo_chinh_dieu(self) -> bool:
        return not self.chinh_tinh


class MenhEvidence(PalaceEvidence):
    interpretation: trung_chau.InterpretationBasis | None
    xung_chieu: PalaceEvidence
    tam_hop: list[PalaceEvidence] = Field(min_length=2, max_length=2)


class ThaiTueContextEvidence(BaseModel):
    position: DiaChi
    knowledge: ThaiTueEvidence | None


class ThanCuEvidence(BaseModel):
    palace_role: Role
    application_context: str
    palace: PalaceEvidence
    basic_combination_id: str | None
    same_as_menh: bool
    source: str = "Khung Thể–Dụng giản lược do người dùng cung cấp"


class TuanTrietPalaceEvidence(BaseModel):
    role: Role
    position: DiaChi
    placements: list[TuanTrietEvidence]
    # shortcut: no matched rules in current evidence; populate when supported rules are supplied.
    applicable_constraints: list[str] = Field(default_factory=list)


class TuanTrietContextEvidence(BaseModel):
    menh: TuanTrietPalaceEvidence
    than: TuanTrietPalaceEvidence


class PersonalityOverviewEvidence(BaseModel):
    menh: MenhEvidence
    thai_tue: ThaiTueContextEvidence
    than: ThanCuEvidence
    tuan_triet: TuanTrietContextEvidence


def _build_palace(la_so: LaSo, role: Role) -> PalaceEvidence:
    position = la_so.position_of(role.value, NATAL_LAYER_ID)
    if position is None:
        raise ModelRetry(f"Không tìm thấy cung {role.value}; không thể coi dữ liệu thiếu là Vô Chính Diệu.")
    cung = la_so.cung_at(position)
    if cung.natal_role != role:
        raise ModelRetry(f"Dữ liệu vị trí cung {role.value} không nhất quán.")
    stars = []
    for component_id in sorted(cung.components_in_layer(NATAL_LAYER_ID)):
        component = la_so.component(component_id)
        if isinstance(component, ChinhPhuTinh) and component.is_chinh_tinh:
            stars.append(StarEvidence(
                component_id=component_id,
                name=component.name,
            ))
    return PalaceEvidence(role=role, position=position, chinh_tinh=stars)


def _build_than_palace(la_so: LaSo) -> PalaceEvidence:
    than_position = la_so.position_of(Role.CUNG_THAN.value, NATAL_LAYER_ID)
    if than_position is None:
        raise ModelRetry("Không tìm thấy vị trí Thân cư.")
    than_role = la_so.cung_at(than_position).natal_role
    if than_role not in THAN_CU_CONTEXTS:
        raise ModelRetry("Thân cư không thuộc sáu cung được hỗ trợ.")
    return _build_palace(la_so, than_role)


def _build_tuan_triet(la_so: LaSo, palace: PalaceEvidence) -> TuanTrietPalaceEvidence:
    placements = []
    for component_id in sorted(la_so.cung_at(palace.position).components_in_layer(NATAL_LAYER_ID)):
        component = la_so.component(component_id)
        if isinstance(component, TuanTriet):
            placements.append(TuanTrietEvidence(component_id=component_id, name=component.name))
    return TuanTrietPalaceEvidence(
        role=palace.role, position=palace.position, placements=placements,
    )


def get_personality_overview_evidence(
    ctx: RunContext[TuviAgentDeps],
) -> PersonalityOverviewEvidence:
    """Lấy dữ kiện nền Mệnh, Thân, Thái Tuế và Trung Châu, không lấy Tật Ách."""
    la_so = ctx.deps.require_la_so()
    menh = _build_palace(la_so, Role.MENH)
    than = _build_than_palace(la_so)
    result = PersonalityOverviewEvidence(
        menh=MenhEvidence(
            role=menh.role, position=menh.position, chinh_tinh=menh.chinh_tinh,
            interpretation=trung_chau.get_interpretation_basis(menh),
            xung_chieu=_build_palace(la_so, Role.THIEN_DI),
            tam_hop=[_build_palace(la_so, role) for role in (Role.TAI_BACH, Role.QUAN_LOC)],
        ),
        thai_tue=ThaiTueContextEvidence(
            position=menh.position, knowledge=build_overview_thai_tue(la_so),
        ),
        than=ThanCuEvidence(
            palace_role=than.role, application_context=THAN_CU_CONTEXTS[than.role],
            palace=than,
            basic_combination_id=(
                "__".join(sorted(star.component_id for star in than.chinh_tinh)) or None
            ),
            same_as_menh=menh.position == than.position,
        ),
        tuan_triet=TuanTrietContextEvidence(
            menh=_build_tuan_triet(la_so, menh), than=_build_tuan_triet(la_so, than),
        ),
    )

    _logger.info("Personality overview evidence: vo_chinh_dieu=%s than_cu=%s",
                 menh.vo_chinh_dieu, result.than.palace_role)
    return result
