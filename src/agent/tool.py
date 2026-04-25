from __future__ import annotations
import logging

from pydantic_ai import ModelRetry, RunContext
from src.agent.book_index import ListSectionsResult, SearchSectionsResult, SectionContent, SectionMeta
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


def list_sections(
    ctx: RunContext[TuviAgentDeps],
    parent_id: str | None = None,
) -> ListSectionsResult:
    """
    List immediate child sections in the structured book.

    Use parent_id=None to list top-level sections in the default book part.
    Returned ids can be used directly by get_section and read_section.
    """
    _logger.info(f"Liệt kê mục sách: parent_id={parent_id}")
    try:
        book = ctx.deps.require_book()
        sections = book.list_sections(parent_id=parent_id)
        return ListSectionsResult(
            sections=[book.get_meta(section.id) for section in sections]
        )
    except ValueError as exc:
        raise ModelRetry(str(exc)) from exc


def get_section(ctx: RunContext[TuviAgentDeps], section_id: str) -> SectionMeta:
    """
    Get metadata for one book section, including breadcrumb, summary, parent,
    and immediate children.

    Use ids such as "1.1" or "11.2.14#hoa-linh". The default book part is
    already selected by the index.
    """
    _logger.info(f"Lấy metadata mục sách: {section_id}")
    try:
        return ctx.deps.require_book().get_meta(section_id)
    except ValueError as exc:
        raise ModelRetry(str(exc)) from exc



def read_section(
    ctx: RunContext[TuviAgentDeps],
    section_id: str,
    include_children: bool = False,
    max_chars: int | None = 8000,
) -> SectionContent:
    """
    Read the content of one book section.

    Set include_children=True to append immediate child subsection content.
    Use max_chars to keep long sections bounded.
    """
    _logger.info(
        "Đọc mục sách: section_id=%s, include_children=%s, max_chars=%s",
        section_id,
        include_children,
        max_chars,
    )
    try:
        return ctx.deps.require_book().read_section(
            section_id,
            include_children=include_children,
            max_chars=max_chars,
        )
    except ValueError as exc:
        raise ModelRetry(str(exc)) from exc


def search_sections(
    ctx: RunContext[TuviAgentDeps],
    query: str,
    top_k: int = 5,
) -> SearchSectionsResult:
    """
    Search section ids, titles, summaries, and partial content in the book.

    This is the best first tool when the user asks about a doctrine, rule,
    star combination, or section title from Tử Vi Tân Biên.
    """
    bounded_top_k = max(1, min(top_k, 20))
    _logger.info(f"Tìm kiếm mục sách: query={query}, top_k={bounded_top_k}")
    return SearchSectionsResult(
        hits=ctx.deps.require_book().search_sections(query, top_k=bounded_top_k)
    )


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
