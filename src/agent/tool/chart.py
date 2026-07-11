from __future__ import annotations

import logging

from pydantic_ai import ModelRetry, RunContext

from src.agent.constant import MAP_STR_TO_DIACHI, MAP_STR_TO_ROLE
from src.agent.deps import TuviAgentDeps
from src.agent.helper.cung_formatter import format_cung_detail
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import DiaChi
from src.refactored.view.builder import build_cung_view


_logger = logging.getLogger(__name__)
_MAP_DIACHI_TO_STR = {value: key for key, value in MAP_STR_TO_DIACHI.items()}


def _parse_position(position: str) -> DiaChi:
    dia_chi = MAP_STR_TO_DIACHI.get(position)
    if dia_chi is None:
        raise ModelRetry(
            f"Không tìm thấy cung tại vị trí '{position}'. "
            f"Các vị trí hợp lệ là: {', '.join(MAP_STR_TO_DIACHI.keys())}."
        )
    return dia_chi


def _format_position(position: DiaChi) -> str:
    return _MAP_DIACHI_TO_STR.get(position, position.value)


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


def get_cung_by_position(ctx: RunContext[TuviAgentDeps], position: str) -> str:
    """Lấy cung theo vị trí địa chi, ví dụ: Tý, Sửu, Dần."""
    _logger.info("Lấy cung theo vị trí: %s", position)
    la_so = ctx.deps.require_la_so()
    dia_chi = _parse_position(position)
    cung = la_so.cung_at(dia_chi)
    return format_cung_detail(build_cung_view(la_so=la_so, cung=cung))


def get_cung_by_role(ctx: RunContext[TuviAgentDeps], role: str) -> str:
    """Lấy cung theo vai trò, ví dụ: Mệnh, Phụ Mẫu, Quan Lộc."""
    _logger.info("Lấy cung theo vai trò: %s", role)
    la_so = ctx.deps.require_la_so()
    role_enum = MAP_STR_TO_ROLE.get(role)
    if role_enum is None:
        raise ModelRetry(
            f"Vai trò '{role}' không hợp lệ. "
            f"Các vai trò hợp lệ là: {', '.join(MAP_STR_TO_ROLE.keys())}."
        )

    for position, cung_id in la_so.tinh_ban.cung_ids.items():
        if cung_id.natal_role == role_enum:
            cung = la_so.cung_at(position)
            return format_cung_detail(build_cung_view(la_so=la_so, cung=cung))

    raise ModelRetry(f"Không tìm thấy cung với vai trò '{role}'.")


def get_tam_hop(ctx: RunContext[TuviAgentDeps], position: str) -> str:
    """Lấy cung tam hợp của một cung cụ thể.

    position phải là một trong các giá trị sau: Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi.
    """
    dia_chi = _parse_position(position)
    tam_hop_positions = dia_chi + 4, dia_chi + 8

    info = ""
    for tam_hop_position in tam_hop_positions:
        display_position = _format_position(tam_hop_position)
        info += f"Cung tam hợp của {position} là {display_position}."
        info += get_cung_by_position(ctx, display_position)
        info += "\n"
    return info.strip()


def get_xung_chieu(ctx: RunContext[TuviAgentDeps], position: str) -> str:
    """Lấy cung xung chiếu của một cung cụ thể."""
    dia_chi = _parse_position(position)
    xung_chieu_position = dia_chi + 6
    display_position = _format_position(xung_chieu_position)

    info = f"Cung xung chiếu của {position} là {display_position}."
    info += get_cung_by_position(ctx, display_position)
    return info
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
    return _format_related_cung_details(
        la_so, 
        position, 
        "tam hợp", 
        tam_hop_positions
    )


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
