from __future__ import annotations

import logging

from pydantic import BaseModel, Field
from pydantic_ai import ModelRetry, RunContext

from src.agent.deps import TuviAgentDeps
from src.agent.tool.cach_cuc.evaluator.scopes import positions_for_scope
from src.agent.tool.phu_tinh.groups import (
    PHU_TINH_GROUP_LABELS,
    build_group_of_star,
    load_phu_tinh_groups,
)
from src.refactored.la_so import LaSo
from src.refactored.components.definitions.cung_role import Role
from src.refactored.components.definitions.map_sao_status import MAP_SAO_STATUS
from src.refactored.components.definitions.sao import (
    ChinhPhuTinh,
    TuHoa,
    VongTrangSinh,
)
from src.refactored.model.elementary import DiaChi
from src.refactored.model.layer import NATAL_LAYER_ID

_logger = logging.getLogger(__name__)


class PhuTinhHit(BaseModel):
    star: str
    star_id: str
    status: str = ""
    palace: str
    scope: str


class PhuTinhGroup(BaseModel):
    group: str
    stars: list[PhuTinhHit] = Field(default_factory=list)


class PhuTinhGroupedResult(BaseModel):
    anchor: str
    groups: list[PhuTinhGroup] = Field(default_factory=list)
    khac: list[PhuTinhHit] = Field(default_factory=list)


class TrangSinhResult(BaseModel):
    palace: str
    star: str | None


def _status_label(star_id: str, position: DiaChi) -> str:
    status = MAP_SAO_STATUS.get(star_id, {}).get(position)
    return status.value if status else ""


def _scope_label(position: DiaChi, anchor: DiaChi) -> str:
    if position == anchor:
        return "đồng cung"
    if position == anchor + 6:
        return "xung chiếu"
    return "tam hợp"


def _ordered_tam_phuong(anchor: DiaChi) -> tuple[DiaChi, ...]:
    """Tam phương tứ chính chiếu về anchor, thứ tự ổn định cho output.

    Bản cung, hai cung tam hợp, rồi cung xung chiếu. Tập hợp trùng khớp với
    positions_for_scope(anchor, "hoi_hop"); ở đây chỉ cố định thứ tự.
    """
    ordered = (anchor, anchor + 4, anchor + 8, anchor + 6)
    assert set(ordered) == positions_for_scope(anchor, "hoi_hop")
    return ordered


def get_phu_tinh_tam_phuong_tu_chinh(
    ctx: RunContext[TuviAgentDeps],
    role: Role = Role.MENH,
) -> PhuTinhGroupedResult:
    """Gom phụ tinh chiếu về một cung theo tam phương tứ chính và phân nhóm."""
    _logger.info("Gom phụ tinh theo nhóm: role=%s", role)
    result = build_phu_tinh_tam_phuong_tu_chinh(ctx.deps.require_la_so(), role)
    grouped_count = sum(len(group.stars) for group in result.groups)
    _logger.info(
        "Đã gom phụ tinh theo nhóm: role=%s, grouped=%d, other=%d",
        role,
        grouped_count,
        len(result.khac),
    )
    return result


def build_phu_tinh_tam_phuong_tu_chinh(
    la_so: LaSo,
    role: Role = Role.MENH,
) -> PhuTinhGroupedResult:
    """Build grouped phụ-tinh evidence directly from a natal chart."""
    anchor = la_so.position_of(role.value, NATAL_LAYER_ID)
    if anchor is None:
        raise ModelRetry(f"Không tìm thấy vị trí cung '{role.value}'.")

    group_stars = load_phu_tinh_groups()
    group_of_star = build_group_of_star(group_stars)
    grouped: dict[str, list[PhuTinhHit]] = {gid: [] for gid, _ in PHU_TINH_GROUP_LABELS}
    khac: list[PhuTinhHit] = []

    for position in _ordered_tam_phuong(anchor):
        cung = la_so.cung_at(position)
        palace = la_so.component(cung.natal_role.value).name
        scope = _scope_label(position, anchor)
        for component_id in cung.components_in_layer(NATAL_LAYER_ID):
            component = la_so.component(component_id)
            if isinstance(component, ChinhPhuTinh) and component.is_chinh_tinh:
                continue
            if not isinstance(component, (ChinhPhuTinh, TuHoa)):
                continue
            hit = PhuTinhHit(
                star=component.name,
                star_id=component_id,
                status=_status_label(component_id, position),
                palace=palace,
                scope=scope,
            )
            group_id = group_of_star.get(component_id)
            if group_id is None:
                khac.append(hit)
            else:
                grouped[group_id].append(hit)

    groups = [
        PhuTinhGroup(group=label, stars=grouped[gid])
        for gid, label in PHU_TINH_GROUP_LABELS
    ]
    return PhuTinhGroupedResult(
        anchor=la_so.component(role.value).name,
        groups=groups,
        khac=khac,
    )


def get_trang_sinh(
    ctx: RunContext[TuviAgentDeps],
    role: Role = Role.MENH,
) -> TrangSinhResult:
    """Lấy sao vòng Tràng Sinh đóng tại một cung (mặc định Mệnh)."""
    _logger.info("Lấy Tràng Sinh: role=%s", role)
    result = build_trang_sinh(ctx.deps.require_la_so(), role)
    _logger.info("Đã lấy Tràng Sinh: role=%s, star=%s", role, result.star)
    return result


def build_trang_sinh(
    la_so: LaSo,
    role: Role = Role.MENH,
) -> TrangSinhResult:
    """Build Tràng-Sinh evidence directly from a natal chart."""
    position = la_so.position_of(role.value, NATAL_LAYER_ID)
    if position is None:
        raise ModelRetry(f"Không tìm thấy vị trí cung '{role.value}'.")

    cung = la_so.cung_at(position)
    star: str | None = None
    for component_id in cung.components_in_layer(NATAL_LAYER_ID):
        component = la_so.component(component_id)
        if isinstance(component, VongTrangSinh):
            star = component.name
            break

    return TrangSinhResult(palace=la_so.component(role.value).name, star=star)
