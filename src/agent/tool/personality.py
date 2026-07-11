from __future__ import annotations

import logging

from pydantic_ai import ModelRetry, RunContext

from src.agent.deps import TuviAgentDeps
from src.agent.tool.chart import _format_cung_at
from src.refactored.la_so import LaSo
from src.refactored.components.definitions.cung_role import Role
from src.refactored.components.definitions.sao import ChinhPhuTinh, TuanTriet
from src.refactored.model.elementary import CircleDirection, DiaChi, NguHanh
from src.refactored.model.layer import NATAL_LAYER_ID
from src.refactored.placement.transforms import (
    get_tam_hop as transform_tam_hop,
    get_xung_chieu as transform_xung_chieu,
)

_logger = logging.getLogger(__name__)


def _sao_ban_menh_relation(sao_ngu_hanh: NguHanh, ban_menh_ngu_hanh: NguHanh) -> str:
    if sao_ngu_hanh.sinh_xuat(ban_menh_ngu_hanh):
        return "sao sinh Bản Mệnh: phẩm chất sao dễ nâng đỡ đương số"
    if sao_ngu_hanh.dong_hanh(ban_menh_ngu_hanh):
        return "sao đồng hành Bản Mệnh: phẩm chất sao dễ hòa nhập"
    if ban_menh_ngu_hanh.sinh_xuat(sao_ngu_hanh):
        return "Bản Mệnh sinh sao: đương số phải xuất lực để dùng phẩm chất sao"
    if ban_menh_ngu_hanh.khac_xuat(sao_ngu_hanh):
        return "Bản Mệnh khắc sao: có xu hướng kiểm soát hoặc cưỡng dụng phẩm chất sao"
    if sao_ngu_hanh.khac_xuat(ban_menh_ngu_hanh):
        return "sao khắc Bản Mệnh: phẩm chất sao tạo áp lực hoặc khó tiếp nhận"
    return "không xác định"


def _main_star_lines(la_so: LaSo, position: DiaChi) -> list[str]:
    lines: list[str] = []
    for layered_component in la_so.cung_at(position).components:
        if layered_component.layer_id != NATAL_LAYER_ID:
            continue
        component = la_so.component(layered_component.component_id)
        if not isinstance(component, ChinhPhuTinh) or not component.is_chinh_tinh:
            continue
        status = _format_star_status(component.id, position)
        relation = _sao_ban_menh_relation(component.ngu_hanh, la_so.ban_menh.ngu_hanh)
        lines.append(
            f"- {component.name}: ngũ hành {component.ngu_hanh.value}, "
            f"trạng thái {status}, quan hệ với Bản Mệnh: {relation}"
        )
    return lines


def _format_position(la_so: LaSo, position: DiaChi) -> str:
    return la_so.catalog.get_dia_chi(position).name


def _main_star_block(la_so: LaSo, label: str, position: DiaChi) -> str:
    lines = _main_star_lines(la_so, position) or ["- Không có chính tinh."]
    return f"{label} ({_format_position(la_so, position)}):\n" + "\n".join(lines)


def _tuan_triet_line(la_so: LaSo, label: str, position: DiaChi) -> str:
    names: list[str] = []
    for layered_component in la_so.cung_at(position).components:
        if layered_component.layer_id != NATAL_LAYER_ID:
            continue
        component = la_so.component(layered_component.component_id)
        if isinstance(component, TuanTriet):
            names.append(component.name)
    value = ", ".join(names) if names else "Không có"
    return f"- {label} ({_format_position(la_so, position)}): {value}"


def _format_star_status(sao_id: str, position: DiaChi) -> str:
    from src.refactored.components.definitions.map_sao_status import MAP_SAO_STATUS

    return MAP_SAO_STATUS.get(sao_id, {}).get(position, "không rõ")


def get_tinh_cach_b3_b4_context(ctx: RunContext[TuviAgentDeps]) -> str:
    """Lấy dữ liệu nền cần thiết để luận tính cách theo B3-B4.

    Tool này gom Bản Mệnh/Cục, cung Mệnh, chính tinh Mệnh, chính tinh xung
    chiếu/tam hợp và Tuần/Triệt ở các cung liên quan.
    """
    _logger.info("Lấy context tính cách B3-B4")
    return build_tinh_cach_b3_b4_context(ctx.deps.require_la_so())


def build_tinh_cach_b3_b4_context(la_so: LaSo) -> str:
    """Build deterministic B3-B4 evidence from a natal chart."""
    menh_position = la_so.position_of(Role.MENH.value)
    if menh_position is None:
        raise ModelRetry("Không tìm thấy cung Mệnh trong lá số.")

    xung_position = transform_xung_chieu(menh_position)
    tam_hop_positions = (
        transform_tam_hop(menh_position, CircleDirection.CW),
        transform_tam_hop(menh_position, CircleDirection.CCW),
    )
    relation = la_so.menh_cuc_relation()
    main_star_lines = _main_star_lines(la_so, menh_position)
    if not main_star_lines:
        main_star_lines = [
            "- Mệnh Vô Chính Diệu: dùng chính tinh cung xung chiếu làm nền B3, "
            "rồi kiểm tam hợp và phụ tinh tại Mệnh."
        ]

    return "\n\n".join(
        [
            "Dữ liệu nền B3-B4",
            (
                f"Bản Mệnh: {la_so.ban_menh.name} ({la_so.ban_menh.ngu_hanh.value}).\n"
                f"Cục: {la_so.natal_context.cuc.name} "
                f"({la_so.natal_context.cuc.ngu_hanh.value}).\n"
                f"Quan hệ Mệnh-Cục: {relation.label} - {relation.description}."
            ),
            "Cung Mệnh:\n" + _format_cung_at(la_so, menh_position),
            "Chính tinh Mệnh và quan hệ với Bản Mệnh:\n" + "\n".join(main_star_lines),
            "Chính tinh xung chiếu Mệnh:\n"
            + _main_star_block(la_so, "Xung chiếu", xung_position),
            "Chính tinh tam hợp Mệnh:\n"
            + "\n\n".join(
                _main_star_block(la_so, "Tam hợp", position)
                for position in tam_hop_positions
            ),
            "Tuần/Triệt tại các cung liên quan:\n"
            + "\n".join(
                [
                    _tuan_triet_line(la_so, "Mệnh", menh_position),
                    _tuan_triet_line(la_so, "Xung chiếu", xung_position),
                    *(
                        _tuan_triet_line(la_so, "Tam hợp", position)
                        for position in tam_hop_positions
                    ),
                ]
            ),
            "Cung xung chiếu Mệnh:\n" + _format_cung_at(la_so, xung_position),
            "Cung tam hợp Mệnh:\n" + "\n\n".join(
                _format_cung_at(la_so, position) for position in tam_hop_positions
            ),
        ]
    )
