from __future__ import annotations

import logging

from pydantic_ai import ModelRetry, RunContext

from src.agent.book_index import SectionContent, SectionSearchHit
from src.agent.deps import TuviAgentDeps
from src.agent.tool.tu_vi_tan_bien.constant import MAP_ROLE_SECTION_ID_FUNC
from src.agent.tool.tu_vi_tan_bien.models import (
    SaoInfoSearchResult,
    SaoInfoSection,
)
from src.refactored.components.definitions.cung_role import Role

from .constant import get_sao_section_id

_logger = logging.getLogger(__name__)
_MAX_STAR_INFO_NAMES = 12


def search_star_info(
    ctx: RunContext[TuviAgentDeps],
    star_names: list[str],
) -> SaoInfoSearchResult:
    """Tra ý nghĩa nhiều chính tinh và phụ tinh trong một lần gọi.

    Tên sao phải lấy nguyên văn từ evidence của lá số. Tool ưu tiên catalog sao
    có cấu trúc; các tên chưa khớp chỉ trả gợi ý tìm kiếm để reasoning layer
    không tự gán nhầm ý nghĩa. Các sao dùng chung một mục sách được gom lại để
    tránh lặp nội dung.

    Args:
        star_names: Từ 1 đến 12 tên chính tinh hoặc phụ tinh có trong evidence.
    """
    unique_names = list(
        dict.fromkeys(name.strip() for name in star_names if name.strip())
    )
    if not unique_names:
        raise ModelRetry("Cần ít nhất một tên sao để tra cứu.")
    if len(unique_names) > _MAX_STAR_INFO_NAMES:
        raise ModelRetry(
            "Mỗi lần chỉ tra tối đa 12 sao; hãy chia danh sách thành nhiều lần gọi."
        )

    book = ctx.deps.require_book()
    names_by_section: dict[str, list[str]] = {}
    not_found: list[str] = []
    suggestions: dict[str, list[SectionSearchHit]] = {}
    for star_name in unique_names:
        section_id = get_sao_section_id(star_name)
        if section_id is None:
            not_found.append(star_name)
            suggestions[star_name] = book.search_sections(star_name, top_k=3)
            continue
        names_by_section.setdefault(section_id, []).append(star_name)

    sections = [
        SaoInfoSection(
            star_names=section_star_names,
            section=book.read_section(section_id),
        )
        for section_id, section_star_names in names_by_section.items()
    ]
    _logger.info(
        "Đã tra ý nghĩa sao: requested=%d sections=%d not_found=%d",
        len(unique_names),
        len(sections),
        len(not_found),
    )
    return SaoInfoSearchResult(
        requested_star_names=unique_names,
        sections=sections,
        not_found=not_found,
        suggestions=suggestions,
    )


def get_star_description(
    ctx: RunContext[TuviAgentDeps], star_name: str
) -> str | SectionContent:
    """Lấy mô tả chi tiết về một sao cụ thể trong Tử Vi Tân Biên.

    Args:
        star_name (str): Tên của sao cần lấy mô tả. Tên này được lấy chính xác trong lá số : Viết hoa chữ đầu tiên và có dấu nếu có.
        Không chỉ là tên chính tinh phụ tinh mà còn có thể là tứ hóa, tràng sinh, Tuần và Triệt
        Ví dụ: "Thái Dương", "Vũ Khúc"

    Returns:
        str | SectionContent: Mô tả chi tiết của sao hoặc thông báo nếu không tìm thấy.
    """

    section_id = get_sao_section_id(star_name)
    if section_id is None:
        return "Không tìm thấy mô tả cho sao này."
    return ctx.deps.require_book().read_section(section_id)


def get_star_role_interaction(
    ctx: RunContext[TuviAgentDeps], star_name: str, role: Role
) -> str | SectionContent:
    """Lấy mô tả về cách một sao cụ thể tương tác với một cung có vai trò nhất định.

    Args:
        star_name (str): Tên của sao cần lấy mô tả. Tên này được lấy chính xác trong lá số : Viết hoa chữ đầu tiên và có dấu nếu có.
        role (str): Vai trò của cung cần xem xét, ví dụ: "Mệnh", "Phụ Mẫu", "Quan Lộc", v.v.

    Returns:
        str | SectionContent: Mô tả về tương tác giữa sao và cung hoặc thông báo nếu không tìm thấy.
    """

    if role not in MAP_ROLE_SECTION_ID_FUNC:
        return f"Vai trò '{role}' không hợp lệ. Vui lòng chọn một trong các vai trò sau: {', '.join(MAP_ROLE_SECTION_ID_FUNC.keys())}."
    section_id_func = MAP_ROLE_SECTION_ID_FUNC[role]
    section_id = section_id_func(star_name)
    if section_id is None:
        return f"Không tìm thấy mô tả cho sao '{star_name}' trong vai trò '{role}'."
    return ctx.deps.require_book().read_section(section_id)
