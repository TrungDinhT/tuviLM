from src.refactored.placement.registry import ComponentId
from typing import Literal, get_args


LIST_SAO_LUU: frozenset[ComponentId] = frozenset({
    "thai_tue",
    "bach_ho",
    "tang_mon",
    "thien_ma",
    "loc_ton",
    "kinh_duong",
    "da_la",
    "thien_khoc",
    "thien_hu",
})


TuHoaEntity = Literal["hoa_loc", "hoa_quyen", "hoa_khoa", "hoa_ky"]
TU_HOA_IDS: frozenset[TuHoaEntity] = frozenset(get_args(TuHoaEntity))
