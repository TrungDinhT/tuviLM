from __future__ import annotations
import logging
from typing_extensions import assert_never

from pydantic_ai import ModelRetry, RunContext
from src.agent.book_index import (
    SectionContent,
)
from src.agent.cach_cuc.matcher import get_cach_cuc_tool_results
from src.agent.cach_cuc.models import CachCucToolResult, Role, SourceKind
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


_logger = logging.getLogger(__name__)


def get_laso(ctx: RunContext[TuviAgentDeps]) -> LaSo:
    """Lấy toàn bộ cấu trúc LaSo hiện có trong deps."""
    return ctx.deps.require_la_so()


def get_cung_by_position(ctx: RunContext[TuviAgentDeps], position: str) -> str:
    """Lấy cung theo vị trí địa chi, ví dụ: Tý, Sửu, Dần."""
    _logger.info(f"Lấy cung theo vị trí: {position}")
    return ctx.deps.get_cung_by_position(position)


def get_cung_by_role(ctx: RunContext[TuviAgentDeps], role: str) -> str:
    """Lấy cung theo vai trò, ví dụ: Mệnh, Phụ Mẫu, Quan Lộc."""
    _logger.info(f"Lấy cung theo vai trò: {role}")
    return ctx.deps.get_cung_by_role(role)


def get_list_cach_cuc(
    ctx: RunContext[TuviAgentDeps],
    source_kind: SourceKind = SourceKind.TUVITANBIEN,
    filtered_roles: list[Role] | None = None,
) -> list[CachCucToolResult]:
    """Lấy các cách cục đang ứng với lá số hiện tại.

    Dùng tool này khi cần kiểm tra riêng các cách cục xuất hiện trong lá số,
    không dùng để đọc toàn bộ tinh bàn hay phân tích một cung.

    source_kind hiện chỉ hỗ trợ "tuvitanbien".

    filtered_roles là danh sách role id như menh, quan_loc, tai_bach.
    Chỉ truyền filtered_roles khi muốn nhắm vào một hoặc vài cung cụ thể, ví dụ
    khi người dùng đang hỏi về Mệnh, Quan Lộc, Tài Bạch. Khi có filtered_roles,
    tool trả về các cách cục có related_roles giao với các role đó, đồng thời vẫn giữ
    các cách cục tổng quát có related_roles rỗng. Nếu người dùng không nhắm vào
    một cung cụ thể, không truyền filtered_roles để lấy tất cả cách cục.

    Kết quả được sắp xếp theo priority giảm dần. Khi đọc kết quả, ưu tiên
    cách cục có priority cao hơn làm khung luận chính; cách cục priority thấp
    hơn dùng làm bổ trợ.

    Kết quả chỉ gồm id, tên, ý nghĩa, trang, priority và related_roles; không trả
    về điều kiện nội bộ.
    """
    _logger.info(
        "Lấy danh sách cách cục: source_kind=%s, filtered_roles=%s",
        source_kind,
        filtered_roles,
    )
    return get_cach_cuc_tool_results(
        ctx.deps.require_la_so(),
        source_kind=source_kind,
        filtered_roles=filtered_roles,
    )


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
