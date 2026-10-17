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
_BASE_ROLES = (Role.MENH, Role.TAI_BACH, Role.QUAN_LOC, Role.THIEN_DI)

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
    source: str = "Khung Thể–Dụng giản lược do người dùng cung cấp"


class PersonalityOverviewEvidence(BaseModel):
    menh: PalaceEvidence
    tam_hop: list[PalaceEvidence] = Field(min_length=2, max_length=2)
    xung_chieu: PalaceEvidence
    thai_tue: ThaiTueEvidence
    than_cu: ThanCuEvidence


class MeaningPassage(BaseModel):
    source: str = "Tử Vi Đẩu Số Tân Biên"
    section_id: str
    scope: str
    breadcrumb: str
    content: str


class OverviewMeaning(BaseModel):
    component_id: str
    palace_role: Role
    passages: list[MeaningPassage] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)


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


def _build_palace(la_so: LaSo, role: Role) -> PalaceEvidence:
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
        elif isinstance(component, TuanTriet):
            modifiers.append(TuanTrietEvidence(component_id=component_id, name=component.name))
    return PalaceEvidence(role=role, position=position, chinh_tinh=stars, tuan_triet=modifiers)


def get_personality_overview_evidence(
    ctx: RunContext[TuviAgentDeps],
) -> PersonalityOverviewEvidence:
    """Lấy input nền: bốn cung chiếu Mệnh, Thái Tuế mới và vị trí Thân cư.

    Không lấy cung Tật Ách hoặc đọc sách ở bước này.
    """
    la_so = ctx.deps.require_la_so()
    menh = _build_palace(la_so, Role.MENH)
    than_position = la_so.position_of(Role.CUNG_THAN.value, NATAL_LAYER_ID)
    if than_position is None:
        raise ModelRetry("Không tìm thấy vị trí Thân cư.")
    than_role = la_so.cung_at(than_position).natal_role
    if than_role not in THAN_CU_CONTEXTS:
        raise ModelRetry("Thân cư không thuộc sáu cung được hỗ trợ.")
    result = PersonalityOverviewEvidence(
        menh=menh,
        tam_hop=[_build_palace(la_so, role) for role in (Role.TAI_BACH, Role.QUAN_LOC)],
        xung_chieu=_build_palace(la_so, Role.THIEN_DI),
        thai_tue=build_overview_thai_tue(la_so),
        than_cu=ThanCuEvidence(
            palace_role=than_role, application_context=THAN_CU_CONTEXTS[than_role],
        ),
    )
    _logger.info("Personality overview evidence: vo_chinh_dieu=%s than_cu=%s", menh.vo_chinh_dieu, than_role)
    return result


def _read_meaning(
    ctx: RunContext[TuviAgentDeps],
    star: StarEvidence | TuanTrietEvidence,
    role: Role,
) -> OverviewMeaning:
    result = OverviewMeaning(component_id=star.component_id, palace_role=role)
    references = [(get_sao_section_id(star.name), "generic")]
    # A star shining toward Mệnh is never treated as occupying Mệnh. Do not
    # retrieve career/wealth/illness outcome chapters for a personality overview.
    if role == Role.MENH:
        references.append((get_menh_than_section_id(star.name), "menh"))
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
        ))
    return result


def get_personality_overview_meaning(
    ctx: RunContext[TuviAgentDeps], component_id: str, palace_role: Role,
) -> OverviewMeaning:
    """Tra nghĩa chính tinh/Tuần/Triệt thực sự có trong bốn cung nền.

    Chỉ tra nghĩa chung và nghĩa tại Mệnh khi sao thực sự ở Mệnh. Không tra
    nghĩa phụ tinh, Thái Tuế truyền thống, cung Thân hoặc chương bệnh tật.
    """
    if palace_role not in _BASE_ROLES:
        raise ModelRetry("Chỉ tra nghĩa trong Mệnh, Tài Bạch, Quan Lộc và Thiên Di.")
    palace = _build_palace(ctx.deps.require_la_so(), palace_role)
    star = next((item for item in [*palace.chinh_tinh, *palace.tuan_triet]
                 if item.component_id == component_id), None)
    if star is None:
        raise ModelRetry("Yếu tố không có trong evidence chính tinh/Tuần/Triệt của cung được chọn.")
    return _read_meaning(ctx, star, palace_role)


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
