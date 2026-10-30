"""Placement relationships in the four natal palaces, without star meanings."""

from __future__ import annotations

from itertools import combinations
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel

if TYPE_CHECKING:
    from .tanbien import PalaceEvidence


# Placement invariants, not psychological archetypes or additional evidence.
_FIXED_TRINES = {
    "Sát Phá Tham": ("that_sat", "pha_quan", "tham_lang"),
    "Tử Vũ Liêm": ("tu_vi", "vu_khuc", "liem_trinh"),
    "Phủ Tướng": ("thien_phu", "thien_tuong"),
    "Cơ Đồng": ("thien_co", "thien_dong"),
    "Âm Lương": ("thai_am", "thien_luong"),
}
_FIXED_OPPOSITIONS = {
    frozenset(("thien_phu", "that_sat")),
    frozenset(("thien_tuong", "pha_quan")),
}
_CONDITIONAL_GROUPS = {
    "Cơ Nguyệt Đồng Lương": ("thien_co", "thai_am", "thien_dong", "thien_luong"),
    "Tử Phủ Vũ Tướng": ("tu_vi", "thien_phu", "vu_khuc", "thien_tuong"),
}


class StarRelation(BaseModel):
    component_ids: tuple[str, str]
    relation: Literal["dong_cung", "tam_hop", "xung_chieu"]
    fixed_by_placement: bool


class StructuralGroup(BaseModel):
    name: str
    component_ids: tuple[str, ...]
    formation: Literal["tam_hop_co_dinh", "hoi_hop_co_dieu_kien"]


class TinhHeEvidence(BaseModel):
    menh_component_ids: list[str]
    relations: list[StarRelation]
    groups: list[StructuralGroup]
    scope_note: str = (
        "Chỉ mô tả cấu trúc chính tinh trong Mệnh–Tài Bạch–Quan Lộc–Thiên Di. "
        "Bộ hội hợp có điều kiện chỉ được ghi khi đủ các sao trong bốn cung này; "
        "không xác nhận cách cục, cát/hung hay ý nghĩa tâm lý. Các quan hệ và bộ "
        "chồng lấp là cách nhìn cùng dữ kiện, không phải bằng chứng độc lập."
    )


def build_tinh_he(menh: PalaceEvidence, supporting: list[PalaceEvidence]) -> TinhHeEvidence:
    # Use actual positions; never fill in an unseen star from a placement rule.
    positions = {
        star.component_id: palace.position
        for palace in [menh, *supporting]
        for star in palace.chinh_tinh
    }
    relations = []
    for left, right in combinations(sorted(positions), 2):
        distance = positions[right] - positions[left]
        relation = {0: "dong_cung", 4: "tam_hop", 8: "tam_hop", 6: "xung_chieu"}.get(distance)
        if relation is None:
            continue
        pair = frozenset((left, right))
        fixed = (
            relation == "tam_hop" and any(pair <= set(ids) for ids in _FIXED_TRINES.values())
        ) or (relation == "xung_chieu" and pair in _FIXED_OPPOSITIONS)
        relations.append(StarRelation(
            component_ids=(left, right), relation=relation, fixed_by_placement=fixed,
        ))

    groups = []
    for name, ids in _FIXED_TRINES.items():
        if set(ids) <= positions.keys() and all(
            positions[right] - positions[left] in (4, 8)
            for left, right in combinations(ids, 2)
        ):
            groups.append(StructuralGroup(
                name=name, component_ids=ids, formation="tam_hop_co_dinh",
            ))
    for name, ids in _CONDITIONAL_GROUPS.items():
        if set(ids) <= positions.keys() and all(
            positions[star_id] - menh.position in (0, 4, 8, 6) for star_id in ids
        ):
            groups.append(StructuralGroup(
                name=name, component_ids=ids, formation="hoi_hop_co_dieu_kien",
            ))
    return TinhHeEvidence(
        menh_component_ids=[star.component_id for star in menh.chinh_tinh],
        relations=relations, groups=groups,
    )
