"""Narrow natal evidence and scoped book retrieval for personality overview."""

from __future__ import annotations

import logging

from pydantic import BaseModel, Field, computed_field
from pydantic_ai import ModelRetry, RunContext

from src.agent.deps import TuviAgentDeps
from src.agent.tool.tu_vi_tan_bien.constant import (
    get_menh_than_section_id,
    get_sao_section_id,
)
from src.agent.workflow.personality_overview.input.thai_tue import (
    ThaiTueEvidence,
    build_overview_thai_tue,
)
from src.refactored.components.definitions.cung_role import Role
from src.refactored.components.definitions.map_sao_status import MAP_SAO_STATUS
from src.refactored.components.definitions.sao import ChinhPhuTinh, TuanTriet
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import DiaChi
from src.refactored.model.layer import NATAL_LAYER_ID

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
    status: str | None = None


class TuanTrietEvidence(BaseModel):
    component_id: str
    name: str


class PalaceEvidence(BaseModel):
    role: Role
    position: DiaChi
    chinh_tinh: list[StarEvidence]
    tuan_triet: list[TuanTrietEvidence]

    @computed_field
    @property
    def vo_chinh_dieu(self) -> bool:
        return not self.chinh_tinh


class ThanCuEvidence(BaseModel):
    palace_role: Role
    application_context: str
    palace: PalaceEvidence
    source: str = "Khung Thể–Dụng giản lược do người dùng cung cấp"


class MeaningPassage(BaseModel):
    source: str = "Tử Vi Đẩu Số Tân Biên"
    section_id: str
    scope: str
    breadcrumb: str
    content: str
    additional_context: str


class OverviewMeaning(BaseModel):
    component_id: str
    palace_role: Role
    passages: list[MeaningPassage] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)


class PersonalityOverviewEvidence(BaseModel):
    menh: PalaceEvidence
    tam_hop: list[PalaceEvidence] = Field(min_length=2, max_length=2)
    xung_chieu: PalaceEvidence
    thai_tue: ThaiTueEvidence
    than_cu: ThanCuEvidence
    meanings: list[OverviewMeaning] = Field(default_factory=list)


class TatAchEvidence(BaseModel):
    reason: str
    palace: PalaceEvidence
    meanings: list[OverviewMeaning]
    interpretation_note: str = (
        "Góc khám phá nội tâm thử nghiệm theo đề xuất của người dùng. Các đoạn sách "
        "chỉ là nghĩa chung của chính tinh, không xác nhận cách diễn giải nội tâm "
        "tại Tật Ách. Chưa có nguồn diễn giải chuyên biệt được duyệt. Không suy từ "
        "bệnh tật sang tâm lý; nếu không có căn cứ phù hợp, bỏ qua dữ kiện bổ sung."
    )


def _build_palace(
    la_so: LaSo, role: Role, *, include_tuan_triet: bool = True,
) -> PalaceEvidence:
    position = la_so.position_of(role.value, NATAL_LAYER_ID)
    if position is None:
        raise ModelRetry(f"Không tìm thấy cung {role.value}; không thể coi dữ liệu thiếu là Vô Chính Diệu.")
    cung = la_so.cung_at(position)
    if cung.natal_role != role:
        raise ModelRetry(f"Dữ liệu vị trí cung {role.value} không nhất quán.")
    stars = []
    modifiers = []
    for component_id in sorted(cung.components_in_layer(NATAL_LAYER_ID)):
        component = la_so.component(component_id)
        if isinstance(component, ChinhPhuTinh) and component.is_chinh_tinh:
            status = MAP_SAO_STATUS.get(component_id, {}).get(position)
            stars.append(StarEvidence(
                component_id=component_id,
                name=component.name,
                status=status.value if status else None,
            ))
        elif include_tuan_triet and isinstance(component, TuanTriet):
            modifiers.append(TuanTrietEvidence(component_id=component_id, name=component.name))
    return PalaceEvidence(role=role, position=position, chinh_tinh=stars, tuan_triet=modifiers)


def _build_than_cu(la_so: LaSo) -> ThanCuEvidence:
    than_position = la_so.position_of(Role.CUNG_THAN.value, NATAL_LAYER_ID)
    if than_position is None:
        raise ModelRetry("Không tìm thấy vị trí Thân cư.")
    than_role = la_so.cung_at(than_position).natal_role
    if than_role not in THAN_CU_CONTEXTS:
        raise ModelRetry("Thân cư không thuộc sáu cung được hỗ trợ.")
    return ThanCuEvidence(
        palace_role=than_role, application_context=THAN_CU_CONTEXTS[than_role],
        palace=_build_palace(la_so, than_role),
    )


def get_personality_overview_evidence(
    ctx: RunContext[TuviAgentDeps],
) -> PersonalityOverviewEvidence:
    """Lấy chính tinh/trạng thái ở Mệnh và hội chiếu, Thái Tuế tại Mệnh, dữ kiện Thân.

    Tuần/Triệt chỉ lấy tại Mệnh và Thân. Không lấy tam phương/Thái Tuế của
    Thân hoặc cung Tật Ách. Đọc sách cho chính tinh Mệnh/Thân; chỉ đọc
    chính tinh hội chiếu khi Mệnh Vô Chính Diệu.
    """
    la_so = ctx.deps.require_la_so()
    menh = _build_palace(la_so, Role.MENH)
    result = PersonalityOverviewEvidence(
        menh=menh,
        tam_hop=[_build_palace(la_so, role, include_tuan_triet=False)
                 for role in (Role.TAI_BACH, Role.QUAN_LOC)],
        xung_chieu=_build_palace(la_so, Role.THIEN_DI, include_tuan_triet=False),
        thai_tue=build_overview_thai_tue(la_so),
        than_cu=_build_than_cu(la_so),
    )

    if menh.vo_chinh_dieu:
        readings = [
            (palace, "Tam hợp với mệnh vô chính diệu") for palace in result.tam_hop
        ]
        readings.append((result.xung_chieu, "Xung chiếu với mệnh vô chính diệu"))
    else:
        readings = [(menh, "Tọa tại mệnh")]
    readings.append((result.than_cu.palace, "Tọa tại cung thân"))

    # One natal palace can serve multiple roles; retain all contexts without
    # reading or returning the same star's passages again for each role.
    palaces: dict[Role, PalaceEvidence] = {}
    contexts: dict[Role, list[str]] = {}
    for palace, context in readings:
        palaces[palace.role] = palace
        contexts.setdefault(palace.role, []).append(context)
    result.meanings = [
        _read_meaning(
            ctx, star, role,
            at_than=role == result.than_cu.palace_role,
            additional_context="; ".join(contexts[role]),
        )
        for role, palace in palaces.items()
        for star in palace.chinh_tinh
    ]

    _logger.info("Personality overview evidence: vo_chinh_dieu=%s than_cu=%s",
                 menh.vo_chinh_dieu, result.than_cu.palace_role)
    return result


def _read_meaning(
    ctx: RunContext[TuviAgentDeps],
    star: StarEvidence,
    role: Role,
    *,
    at_than: bool = False,
    additional_context: str = "",
) -> OverviewMeaning:
    result = OverviewMeaning(component_id=star.component_id, palace_role=role)
    references = [(get_sao_section_id(star.name), "generic")]
    # The shared Mệnh/Thân chapter applies only to an actual occupant of either.
    # Never retrieve career/wealth/illness outcome chapters for this overview.
    if role == Role.MENH:
        references.append((get_menh_than_section_id(star.name), "menh"))
    elif at_than:
        references.append((get_menh_than_section_id(star.name), "than"))
    available = [(section_id, scope) for section_id, scope in references if section_id]
    if not available:
        result.missing.append(f"Chưa có mục sách được ánh xạ cho {star.name} trong phạm vi này.")
        return result
    try:
        book = ctx.deps.require_book()
    except ModelRetry:
        result.missing.append("Chưa có nguồn sách Tân Biên để tra cứu; không tự bù ý nghĩa.")
        return result
    for section_id, scope in available:
        try:
            # Read the exact section, not unrelated parent text or child indexes.
            record = book.get_record(section_id)
        except ValueError:
            result.missing.append(f"Không tìm thấy mục {section_id} của {star.name}.")
            continue
        if not record.content.strip():
            result.missing.append(f"Mục {section_id} chưa có nội dung trực tiếp.")
            continue
        result.passages.append(MeaningPassage(
            section_id=record.id, scope=scope,
            breadcrumb=book.breadcrumb(record.id), content=record.content,
            additional_context=additional_context,
        ))
    return result


def get_personality_overview_tat_ach_evidence(
    ctx: RunContext[TuviAgentDeps], reason: str,
) -> TatAchEvidence:
    """Chỉ gọi khi tension nền còn chưa rõ và góc nội tâm có thể giúp làm rõ.

    reason nêu ngắn gọn tension chưa giải thích được và giá trị mong đợi sau
    khi đã xem lại evidence nền. Không gọi mặc định để hoàn tất checklist.
    Chỉ lấy chính tinh, trạng thái, Tuần/Triệt tại Tật Ách và nghĩa sao chung.
    """
    reason = reason.strip()
    if not reason:
        raise ModelRetry("Cần nêu tension chưa rõ và lý do dữ kiện Tật Ách có thể hữu ích.")
    palace = _build_palace(ctx.deps.require_la_so(), Role.TAT_ACH)
    _logger.info("Truy xuất Tật Ách thử nghiệm: reason=%s", reason)
    return TatAchEvidence(
        reason=reason, palace=palace,
        meanings=[_read_meaning(ctx, star, Role.TAT_ACH) for star in palace.chinh_tinh],
    )
