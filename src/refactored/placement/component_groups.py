"""Reusable placement component id groups.

These groups are not catalog data and are not rules by themselves. They name
sets of component ids that placement layers can choose to materialize.
"""

from typing import Literal, get_args

from src.refactored.component.cung_role import Role
from src.refactored.placement.registry import ComponentId


SAO_LUU_IDS: frozenset[ComponentId] = frozenset(
    {
        "thai_tue",
        "bach_ho",
        "tang_mon",
        "thien_ma",
        "loc_ton",
        "kinh_duong",
        "da_la",
        "thien_khoc",
        "thien_hu",
    }
)


TuHoaEntity = Literal["hoa_loc", "hoa_quyen", "hoa_khoa", "hoa_ky"]
TU_HOA_IDS: frozenset[TuHoaEntity] = frozenset(get_args(TuHoaEntity))


PERIOD_ROLE_IDS: frozenset[ComponentId] = frozenset(
    role.value for role in Role if role is not Role.CUNG_THAN
)
