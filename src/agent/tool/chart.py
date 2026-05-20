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
