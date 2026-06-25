from __future__ import annotations
import logging
from typing_extensions import assert_never

from pydantic_ai import ModelRetry, RunContext
from src.agent.book_index import (
    SectionContent,
)
from src.agent.constant import MAP_STR_TO_DIACHI
from src.agent.deps import TuviAgentDeps
from src.agent.prompt.skill_analyze_cung import (
    CUNG_DIEN_TRACH_INSTRUCTION,
    CUNG_HUYNH_DE_INSTRUCTION,
    CUNG_MENH_INSTRUCTION,
    CUNG_NO_BOC_INSTRUCTION,
    CUNG_PHU_MAU_INSTRUCTION,
    CUNG_PHU_THE_INSTRUCTION,
    CUNG_PHUC_DUC_INSTRUCTION,
    CUNG_QUAN_LOC_INSTRUCTION,
    CUNG_TAI_BACH_INSTRUCTION,
    CUNG_TAT_ACH_INSTRUCTION,
    CUNG_THIEN_DI_INSTRUCTION,
    CUNG_TU_TUC_INSTRUCTION,
)
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import (
    CircleDirection,
    DiaChi,
    LuongNghi,
    ThienCan,
)
from src.refactored.model.menh_cuc_relation import MenhCucRelationType
from src.refactored.model.prior import Gender


_logger = logging.getLogger(__name__)


def get_laso(ctx: RunContext[TuviAgentDeps]) -> LaSo:
    """Lấy toàn bộ cấu trúc LaSo hiện có trong deps."""
    return ctx.deps.require_la_so()


def get_laso_foundation(ctx: RunContext[TuviAgentDeps]) -> dict[str, object]:
    """Lấy phần gốc của lá số trước khi luận chi tiết.

    Tool này trả về các nền tảng phải xét trước khi luận một lá số: Thiên Can
    năm sinh, Địa Chi năm sinh, âm/dương nam/nữ, hướng thuận-nghịch, Bản Mệnh,
    Cục, quan hệ Mệnh-Cục, thuận/nghịch giữa năm sinh và cung Mệnh, cùng bảng
    Đại hạn khởi từ số Cục.

    Dùng tool này trước khi luận tổng quan lá số, luận cung Mệnh, hoặc khi cần
    cân nhắc nền mạnh/yếu của toàn cục. Không dùng tool này thay thế cho
    get_list_cach_cuc hay get_cung_by_role; nó chỉ là lớp nền để định khung
    luận giải.
    """
    _logger.info("Lấy gốc lá số")
    return build_laso_foundation_payload(ctx.deps.require_la_so())


def build_laso_foundation_payload(la_so: LaSo) -> dict[str, object]:
    """Return a plain payload derived from the existing refactored chart model."""
    prior = la_so.prior
    context = la_so.natal_context
    thien_can_entity = la_so.catalog.get_thien_can(prior.thien_can)
    dia_chi_entity = la_so.catalog.get_dia_chi(prior.dia_chi)
    menh_entity = la_so.catalog.get_dia_chi(context.menh_position)
    relation = la_so.menh_cuc_relation()
    year_am_duong = _am_duong_name(context.am_duong)

    return {
        "birth_year": prior.year,
        "lunar_year": f"{thien_can_entity.name} {dia_chi_entity.name}",
        "gender": prior.gender.value,
        "thien_can_year": {
            "id": prior.thien_can.value,
            "name": thien_can_entity.name,
            "am_duong": _am_duong_name(_am_duong_of_thien_can(prior.thien_can)),
            "ngu_hanh": thien_can_entity.ngu_hanh.value,
        },
        "dia_chi_year": {
            "id": prior.dia_chi.value,
            "name": dia_chi_entity.name,
            "am_duong": _am_duong_name(_am_duong_of_dia_chi(prior.dia_chi)),
            "ngu_hanh": dia_chi_entity.ngu_hanh.value,
        },
        "year_am_duong": year_am_duong,
        "gender_polarity": f"{year_am_duong} {_gender_name(prior.gender)}",
        "van_direction": _van_direction_label(context.van_direction),
        "van_direction_detail": _van_direction_detail(context.van_direction),
        "menh_position": {
            "id": context.menh_position.value,
            "name": menh_entity.name,
            "am_duong": _am_duong_name(_am_duong_of_dia_chi(context.menh_position)),
            "ngu_hanh": menh_entity.ngu_hanh.value,
            "year_menh_polarity_relation": _year_menh_polarity_relation(
                prior.dia_chi,
                context.menh_position,
            ),
            "year_menh_polarity_note": (
                "Năm sinh và cung an Mệnh cùng âm/dương thì thuận lý; "
                "khác âm/dương thì nghịch lý."
            ),
        },
        "ban_menh": {
            "id": la_so.ban_menh.id,
            "name": la_so.ban_menh.name,
            "ngu_hanh": la_so.ban_menh.ngu_hanh.value,
            "description": la_so.ban_menh.description,
        },
        "cuc": {
            "id": context.cuc.id,
            "name": context.cuc.name,
            "number": context.cuc.number,
            "ngu_hanh": context.cuc.ngu_hanh.value,
            "derivation": (
                "Cục được lập từ Thiên Can năm sinh và vị trí an Mệnh; "
                "số cục cũng là tuổi khởi Đại hạn đầu tiên."
            ),
        },
        "menh_cuc_relation": {
            "label": relation.label,
            "relation_type": relation.relation_type.value,
            "direction": relation.direction,
            "description": relation.description,
            "interpretation": _menh_cuc_interpretation(relation.relation_type),
        },
        "dai_han_ranges": _build_dai_han_ranges(la_so),
        "foundation_effects": list(_FOUNDATION_EFFECTS),
        "interpretation_order": list(_INTERPRETATION_ORDER),
        "source_notes": list(_SOURCE_NOTES),
    }


def _am_duong_of_thien_can(thien_can: ThienCan) -> LuongNghi:
    return LuongNghi(thien_can.index % 2)


def _am_duong_of_dia_chi(dia_chi: DiaChi) -> LuongNghi:
    return LuongNghi(dia_chi.index % 2)


def _am_duong_name(am_duong: LuongNghi) -> str:
    return "Dương" if am_duong is LuongNghi.DUONG else "Âm"


def _gender_name(gender: Gender) -> str:
    return "Nam" if gender is Gender.MALE else "Nữ"


def _van_direction_label(van_direction: CircleDirection) -> str:
    return "thuận" if van_direction is CircleDirection.CW else "nghịch"


def _van_direction_detail(van_direction: CircleDirection) -> str:
    if van_direction is CircleDirection.CW:
        return "Dương nam hoặc Âm nữ: an vận theo chiều thuận từ cung Mệnh."
    return "Âm nam hoặc Dương nữ: an vận theo chiều nghịch từ cung Mệnh."


def _year_menh_polarity_relation(
    natal_year_dia_chi: DiaChi,
    menh_position: DiaChi,
) -> str:
    if _am_duong_of_dia_chi(natal_year_dia_chi) is _am_duong_of_dia_chi(menh_position):
        return "thuận lý"
    return "nghịch lý"


def _menh_cuc_interpretation(relation_type: MenhCucRelationType) -> str:
    return {
        MenhCucRelationType.SINH_XUAT: (
            "Thuận: Bản Mệnh sinh Cục, được xem là nền tốt nhất trong quan hệ mệnh-cục."
        ),
        MenhCucRelationType.SINH_NHAP: (
            "Thuận: Cục sinh Bản Mệnh, vẫn là tương sinh tốt đẹp nhưng kém hơn "
            "chiều Bản Mệnh sinh Cục."
        ),
        MenhCucRelationType.KHAC_XUAT: (
            "Nghịch: Bản Mệnh khắc Cục; sách nhấn mạnh trường hợp này làm giảm "
            "độ số dù toàn cục có nhiều điểm tốt."
        ),
        MenhCucRelationType.KHAC_NHAP: (
            "Nghịch: Cục khắc Bản Mệnh; cần đọc thận trọng vì mệnh-cục thuộc "
            "quan hệ tương khắc."
        ),
        MenhCucRelationType.BINH_HOA: (
            "Bình hòa: Mệnh và Cục cùng hành, không tạo thêm lực sinh hay khắc."
        ),
    }[relation_type]


def _build_dai_han_ranges(la_so: LaSo) -> list[dict[str, object]]:
    focus_map = la_so.dai_han_focus_map()
    ranges: list[dict[str, object]] = []
    for age_range, focus_position in sorted(
        focus_map.by_range.items(),
        key=lambda item: item[0].start_age,
    ):
        focus_entity = la_so.catalog.get_dia_chi(focus_position)
        ranges.append(
            {
                "start_age": age_range.start_age,
                "end_age": age_range.end_age,
                "focus_position_id": focus_position.value,
                "focus_position_name": focus_entity.name,
            }
        )
    return ranges


_FOUNDATION_EFFECTS: tuple[str, ...] = (
    "Thiên Can năm sinh cho âm/dương, ngũ hành can, là đầu vào lập Cục "
    "và nhiều phép an sao theo can như Lộc Tồn, Triệt, Tứ Hóa.",
    "Địa Chi năm sinh cho âm/dương, ngũ hành chi, là mốc của Thái Tuế, "
    "Tuần, tiểu hạn và các nhóm sao/hạn theo chi.",
    "Âm/Dương Nam/Nữ quyết định chiều thuận-nghịch khi an Đại hạn và "
    "các vòng sao đi theo vận chiều.",
    "Ngũ hành Bản Mệnh là nền để so với Cục, cung Mệnh, chính tinh, "
    "mùa sinh và giờ sinh.",
    "Ngũ hành Cục và số Cục được lập từ can năm sinh với cung an Mệnh; "
    "số Cục dùng để an Tử Vi, vòng Tràng Sinh và khởi Đại hạn.",
)

_INTERPRETATION_ORDER: tuple[str, ...] = (
    "Xác định can-chi năm sinh và âm/dương của năm.",
    "Xác định Âm/Dương Nam/Nữ để biết chiều vận.",
    "Xác định Bản Mệnh, Cục và quan hệ Mệnh-Cục.",
    "Đánh giá thuận/nghịch giữa năm sinh và cung an Mệnh.",
    "Sau đó mới dùng cách cục, chính tinh, phụ tinh, tam hợp, xung chiếu "
    "để luận chi tiết.",
)

_SOURCE_NOTES: tuple[dict[str, str], ...] = (
    {
        "id": "tuvitanbien_2_tim_ban_menh",
        "title": "Tử Vi Tân Biên - 2. Tìm Bản Mệnh",
        "summary": "Bản Mệnh lấy từ hàng Can-Chi năm sinh và thuộc một trong năm hành.",
        "path": "book/tuvitanbien_chunking/part_1/2_tim-ban-menh.md",
    },
    {
        "id": "tuvitanbien_3_phan_am_duong",
        "title": "Tử Vi Tân Biên - 3. Phân Âm Dương",
        "summary": (
            "Nam/nữ được phân thành Âm Nam, Dương Nam, Âm Nữ, Dương Nữ "
            "theo âm dương của tuổi."
        ),
        "path": "book/tuvitanbien_chunking/part_1/3_phan-am-duong.md",
    },
    {
        "id": "tuvitanbien_7_lap_cuc",
        "title": "Tử Vi Tân Biên - 7. Lập Cục",
        "summary": "Cục được lập từ Can tuổi và cung an Mệnh.",
        "path": "book/tuvitanbien_chunking/part_1/7_lap-cuc.md",
    },
    {
        "id": "tuvitanbien_10_khoi_han",
        "title": "Tử Vi Tân Biên - 10.1. Đại hạn",
        "summary": (
            "Số Cục khởi Đại hạn; Dương Nam/Âm Nữ đi thuận, Âm Nam/Dương Nữ đi nghịch."
        ),
        "path": "data/tuvitanbien/page_020.md",
    },
    {
        "id": "tuvitanbien_11_ngu_hanh",
        "title": "Tử Vi Tân Biên - 11.1. Ngũ Hành",
        "summary": "Ngũ hành có tương sinh và tương khắc.",
        "path": "book/tuvitanbien_chunking/part_1/11_1_ngu-hanh.md",
    },
    {
        "id": "tuvitanbien_1_4_ban_menh_cuc",
        "title": "Tử Vi Tân Biên - 1.4. Bản Mệnh - Cục",
        "summary": (
            "Quan hệ Bản Mệnh và Cục là nền thuận/nghịch quan trọng khi luận toàn cục."
        ),
        "path": "book/tuvitanbien_chunking/part_2/1_4_ban-menh-cuc.md",
    },
    {
        "id": "tuvitanbien_1_5_nam_sinh_cung_menh",
        "title": "Tử Vi Tân Biên - 1.5. Năm sinh - Cung Mệnh",
        "summary": "Năm sinh và cung an Mệnh cùng âm/dương là thuận lý.",
        "path": "book/tuvitanbien_chunking/part_2/1_5_nam-sinh-cung-menh.md",
    },
)


def get_cung_by_position(ctx: RunContext[TuviAgentDeps], position: str) -> str:
    """Lấy cung theo vị trí địa chi, ví dụ: Tý, Sửu, Dần."""
    _logger.info(f"Lấy cung theo vị trí: {position}")
    return ctx.deps.get_cung_by_position(position)


def get_cung_by_role(ctx: RunContext[TuviAgentDeps], role: str) -> str:
    """Lấy cung theo vai trò, ví dụ: Mệnh, Phụ Mẫu, Quan Lộc."""
    _logger.info(f"Lấy cung theo vai trò: {role}")
    return ctx.deps.get_cung_by_role(role)


def read_catalog(
    ctx: RunContext[TuviAgentDeps],
    section_id: str | None = None,
    depth: int | None = 3,
) -> str:
    """
    Read the Tử Vi Tân Biên catalog as a plain-text tree.

    Use section_id=None to browse the book from the root. Pass a section_id
    such as "1.1" or "11.2.14" to browse only that branch. Increase
    depth when more descendant levels are needed; pass None to read all levels.
    """
    _logger.info(
        "Đọc catalog sách: section_id=%s, depth=%s",
        section_id,
        depth,
    )
    try:
        bounded_depth = None if depth is None else max(1, min(depth, 8))
        return ctx.deps.require_book().get_catalog(
            section_id=section_id,
            depth=bounded_depth,
        )
    except ValueError as exc:
        raise ModelRetry(str(exc)) from exc


def read_section(
    ctx: RunContext[TuviAgentDeps],
    section_id: str,
) -> SectionContent:
    """
    Read the content of one book section.

    section_id must be a valid id such as "3", "3.4", "3.4.5", or "8.11".
    """
    _logger.info(
        f"Đọc mục sách: section_id={section_id}",
    )
    try:
        return ctx.deps.require_book().read_section(
            section_id,
        )
    except ValueError as exc:
        raise ModelRetry(f"Failed to read section {section_id}") from exc


def get_tam_hop(ctx: RunContext[TuviAgentDeps], position: str) -> str:
    """Lấy cung tam hợp của một cung cụ thể.

    position phải là một trong các giá trị sau: Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi.
    """
    dia_chi = MAP_STR_TO_DIACHI.get(position)
    tam_hop_position = dia_chi + 4, dia_chi + 8
    info = ""
    info += f"Cung tam hợp của {position} là {tam_hop_position[0]}."
    info += get_cung_by_position(ctx, tam_hop_position[0])
    info += f"\nCung tam hợp còn lại của {position} là {tam_hop_position[1]}."
    info += get_cung_by_position(ctx, tam_hop_position[1])
    return info


def get_xung_chieu(ctx: RunContext[TuviAgentDeps], position: str) -> str:
    """Lấy cung xung chiếu của một cung cụ thể."""
    dia_chi = MAP_STR_TO_DIACHI.get(position)
    xung_chieu_position = dia_chi + 6
    info = f"Cung xung chiếu của {position} là {xung_chieu_position}."
    info += get_cung_by_position(ctx, xung_chieu_position)
    return info


_ROLE_INSTRUCTION_MAP: dict[str, str] = {
    "Mệnh": CUNG_MENH_INSTRUCTION,
    "Quan Lộc": CUNG_QUAN_LOC_INSTRUCTION,
    "Tài Bạch": CUNG_TAI_BACH_INSTRUCTION,
    "Phụ Mẫu": CUNG_PHU_MAU_INSTRUCTION,
    "Huynh Đệ": CUNG_HUYNH_DE_INSTRUCTION,
    "Nô Bộc": CUNG_NO_BOC_INSTRUCTION,
    "Phu Thê": CUNG_PHU_THE_INSTRUCTION,
    "Phúc Đức": CUNG_PHUC_DUC_INSTRUCTION,
    "Thiên Di": CUNG_THIEN_DI_INSTRUCTION,
    "Tật Ách": CUNG_TAT_ACH_INSTRUCTION,
    "Tử Tức": CUNG_TU_TUC_INSTRUCTION,
    "Điền Trạch": CUNG_DIEN_TRACH_INSTRUCTION,
}


def get_role_instruction(role: str) -> str:
    """Lấy hướng dẫn phân tích cho một cung dựa trên vai trò của nó.

    role phải là một trong các giá trị sau: Mệnh, Phụ Mẫu, Phúc Đức, Điền Trạch, Quan Lộc, Nô Bộc, Thiên Di, Tật Ách, Tài Bạch, Tử Tức, Phu Thê, Huynh Đệ.
    """
    if role not in _ROLE_INSTRUCTION_MAP:
        assert_never(role)
    return _ROLE_INSTRUCTION_MAP[role]
