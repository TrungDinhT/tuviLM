from __future__ import annotations

from pydantic_ai import RunContext

from src.refactored.components.definitions.cung_role import Role

from .constant import get_sao_section_id
from src.agent.book_index import SectionContent
from src.agent.deps import TuviAgentDeps
from src.agent.tool.tu_vi_tan_bien.constant import MAP_ROLE_SECTION_ID_FUNC


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
