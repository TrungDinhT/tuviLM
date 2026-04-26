from __future__ import annotations
import logging

from pydantic_ai import ModelRetry, RunContext
from src.agent.book_index import (
    SectionContent,
)
from src.agent.deps import TuviAgentDeps
from src.tuvi.cung import Cung
from src.tuvi.element.types import LIST_DIA_CHI, ROLE_TYPE, TYPE_DIA_CHI
from src.tuvi.tinh_ban import TinhBan


_logger = logging.getLogger(__name__)

def get_tinh_ban(ctx: RunContext[TuviAgentDeps]) -> TinhBan:
    """Lấy toàn bộ cấu trúc TinhBan hiện có trong deps."""
    return ctx.deps.require_tinh_ban()


def get_cung_by_position(
    ctx: RunContext[TuviAgentDeps],
    position: TYPE_DIA_CHI
) -> Cung:
    """Lấy cung theo vị trí địa chi, ví dụ: Tý, Sửu, Dần."""
    _logger.info(f"Lấy cung theo vị trí: {position}")
    return ctx.deps.get_cung_by_position(position)


def get_cung_by_role(
    ctx: RunContext[TuviAgentDeps],
    role: ROLE_TYPE
) -> Cung:
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
    such as "1.1" or "11.2.14#hoa-linh" to browse only that branch. Increase
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
    max_chars: int | None = 8000,
) -> SectionContent:
    """
    Read the content of one book section.

    section_id must be a valid id such as "3", "3.4", "3.4.5", or "8.11".
    """
    _logger.info(
        f"Đọc mục sách: section_id={section_id}, max_chars={max_chars}",
    )
    try:
        return ctx.deps.require_book().read_section(
            section_id,
            max_chars=max_chars,
        )
    except ValueError as exc:
        raise ModelRetry(str(exc)) from exc



def get_tam_hop(
    ctx: RunContext[TuviAgentDeps],
    position: TYPE_DIA_CHI
) -> str:
    """Lấy cung tam hợp của một cung cụ thể."""
    index = LIST_DIA_CHI.index(position)
    tam_hop_index = ((index + 4) % 12, (index + 8) % 12)
    tam_hop_position = (LIST_DIA_CHI[tam_hop_index[0]], LIST_DIA_CHI[tam_hop_index[1]])
    info = ""
    info += f"Cung tam hợp của {position} là {tam_hop_position[0]}."
    info += get_cung_by_position(ctx, tam_hop_position[0])
    info += f"\nCung tam hợp còn lại của {position} là {tam_hop_position[1]}."
    info += get_cung_by_position(ctx, tam_hop_position[1])
    return info



def get_xung_chieu(
    ctx: RunContext[TuviAgentDeps],
    position: TYPE_DIA_CHI
) -> str:
    """Lấy cung xung chiếu của một cung cụ thể."""
    index = LIST_DIA_CHI.index(position)
    xung_chieu_index = (index + 6) % 12
    xung_chieu_position = LIST_DIA_CHI[xung_chieu_index]
    info = f"Cung xung chiếu của {position} là {xung_chieu_position}."
    info += get_cung_by_position(ctx, xung_chieu_position)
    return info
