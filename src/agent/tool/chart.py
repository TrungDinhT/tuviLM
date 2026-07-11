from __future__ import annotations

import logging

from pydantic_ai import ModelRetry, RunContext

from src.agent.deps import TuviAgentDeps
from src.agent.helper.cung_formatter import format_cung_detail
from src.refactored.components.definitions.cung_role import Role
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import CircleDirection, DiaChi
from src.refactored.placement.transforms import (
    get_tam_hop as transform_tam_hop,
    get_xung_chieu as transform_xung_chieu,
)
from src.refactored.view.builder import build_cung_view


_logger = logging.getLogger(__name__)


def _format_position(la_so: LaSo, position: DiaChi) -> str:
    return la_so.catalog.get_dia_chi(position).name


def _format_cung_at(la_so: LaSo, position: DiaChi) -> str:
    cung = la_so.cung_at(position)
    return format_cung_detail(build_cung_view(la_so=la_so, cung=cung))


def _format_related_cung_details(
    la_so: LaSo,
    source_position: DiaChi,
    relation_name: str,
    related_positions: tuple[DiaChi, ...],
) -> str:
    source_name = _format_position(la_so, source_position)
    details: list[str] = []

    for related_position in related_positions:
        related_name = _format_position(la_so, related_position)
        details.append(
            f"Cung {relation_name} của {source_name} là {related_name}."
            + _format_cung_at(la_so, related_position)
        )

    return "\n".join(details)


def get_laso(ctx: RunContext[TuviAgentDeps]) -> LaSo:
    """Lấy toàn bộ cấu trúc LaSo hiện có trong deps."""
    return ctx.deps.require_la_so()


def get_cung_by_position(ctx: RunContext[TuviAgentDeps], position: DiaChi) -> str:
    """Lấy cung theo vị trí địa chi bằng mã DiaChi nội bộ."""
    _logger.info("Lấy cung theo vị trí: %s", position)
    la_so = get_laso(ctx)
    return _format_cung_at(la_so, position)


def get_cung_by_role(ctx: RunContext[TuviAgentDeps], role: Role) -> str:
    """Lấy cung theo vai trò bằng mã Role nội bộ.

    Lưu ý: với cung Thân, dùng cung_than
    """
    _logger.info("Lấy cung theo vai trò: %s", role)
    la_so = get_laso(ctx)
    position = la_so.position_of(role.value)
    if position is None:
        raise ModelRetry(f"Không tìm thấy cung với vai trò '{role.value}'.")

    return _format_cung_at(la_so, position)


def get_tam_hop(ctx: RunContext[TuviAgentDeps], position: DiaChi) -> str:
    """Lấy các cung tam hợp của một cung theo mã DiaChi nội bộ."""
    _logger.info("Lấy cung tam hợp theo vị trí: %s", position)
    la_so = get_laso(ctx)
    tam_hop_positions = (
        transform_tam_hop(position, CircleDirection.CW),
        transform_tam_hop(position, CircleDirection.CCW),
    )
    return _format_related_cung_details(la_so, position, "tam hợp", tam_hop_positions)


def get_xung_chieu(ctx: RunContext[TuviAgentDeps], position: DiaChi) -> str:
    """Lấy cung xung chiếu của một cung theo mã DiaChi nội bộ."""
    _logger.info("Lấy cung xung chiếu theo vị trí: %s", position)
    la_so = get_laso(ctx)
    xung_chieu_position = transform_xung_chieu(position)
    return _format_related_cung_details(
        la_so,
        position,
        "xung chiếu",
        (xung_chieu_position,),
    )
