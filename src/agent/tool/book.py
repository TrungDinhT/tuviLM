from __future__ import annotations

import logging

from pydantic_ai import ModelRetry, RunContext

from src.agent.book_index import SectionContent
from src.agent.deps import TuviAgentDeps


_logger = logging.getLogger(__name__)


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
    _logger.info("Đọc mục sách: section_id=%s", section_id)
    try:
        return ctx.deps.require_book().read_section(section_id)
    except ValueError as exc:
        raise ModelRetry(f"Failed to read section {section_id}") from exc
