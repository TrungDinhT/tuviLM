
from typing import Literal

from src.tuvi.constant import MAP_LOC_TON_POSITION, MAP_LUU_HA, MAP_THIEN_KHOI, MAP_THIEN_PHUC, MAP_THIEN_QUAN, MAP_THIEN_TRU, MAP_THIEN_VIET
from src.tuvi.element.types import LIST_DIA_CHI, TYPE_DIA_CHI, TYPE_THIEN_CAN


def get_loc_ton_position(thien_can: TYPE_THIEN_CAN) -> TYPE_DIA_CHI:
    return MAP_LOC_TON_POSITION[thien_can]

def get_bac_si_position(locton_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    return locton_position

def get_kinh_duong_position(locton_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    locton_index = LIST_DIA_CHI.index(locton_position)
    return LIST_DIA_CHI[(locton_index + 1) % 12]

def get_thanh_long_position(locton_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    locton_index = LIST_DIA_CHI.index(locton_position)
    return LIST_DIA_CHI[(locton_index + 2) % 12]

def get_tieu_hao_position(locton_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    locton_index = LIST_DIA_CHI.index(locton_position)
    return LIST_DIA_CHI[(locton_index + 3) % 12]

def get_ln_van_tinh_position(locton_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    locton_index = LIST_DIA_CHI.index(locton_position)
    return LIST_DIA_CHI[(locton_index + 3) % 12]

def get_tuong_quan_position(locton_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    locton_index = LIST_DIA_CHI.index(locton_position)
    return LIST_DIA_CHI[(locton_index + 4) % 12]

def get_tau_thu_position(locton_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    locton_index = LIST_DIA_CHI.index(locton_position)
    return LIST_DIA_CHI[(locton_index + 5) % 12]

def get_duong_phu_position(locton_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    locton_index = LIST_DIA_CHI.index(locton_position)
    return LIST_DIA_CHI[(locton_index + 5) % 12]

def get_phi_liem_position(locton_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    locton_index = LIST_DIA_CHI.index(locton_position)
    return LIST_DIA_CHI[(locton_index + 6) % 12]

def get_hy_than_position(locton_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    locton_index = LIST_DIA_CHI.index(locton_position)
    return LIST_DIA_CHI[(locton_index + 7) % 12]

def get_benh_phu_position(locton_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    locton_index = LIST_DIA_CHI.index(locton_position)
    return LIST_DIA_CHI[(locton_index + 8) % 12]

def get_quoc_an_position(locton_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    locton_index = LIST_DIA_CHI.index(locton_position)
    return LIST_DIA_CHI[(locton_index + 8) % 12]

def get_dai_hao_position(locton_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    locton_index = LIST_DIA_CHI.index(locton_position)
    return LIST_DIA_CHI[(locton_index + 9) % 12]

def get_phuc_binh_position(locton_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    locton_index = LIST_DIA_CHI.index(locton_position)
    return LIST_DIA_CHI[(locton_index + 10) % 12]

def get_da_la_position(locton_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    locton_index = LIST_DIA_CHI.index(locton_position)
    return LIST_DIA_CHI[(locton_index + 11) % 12]

def get_quan_phu_position(locton_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    locton_index = LIST_DIA_CHI.index(locton_position)
    return LIST_DIA_CHI[(locton_index + 11) % 12]

def get_luc_si_position(locton_position: TYPE_DIA_CHI, direction: Literal[1, -1]) -> TYPE_DIA_CHI:
    locton_index = LIST_DIA_CHI.index(locton_position)
    return LIST_DIA_CHI[(locton_index + int(direction)) % 12]

def get_luu_ha_position(thien_can: TYPE_THIEN_CAN) -> TYPE_DIA_CHI:
    return MAP_LUU_HA[thien_can]

def get_thien_tru_position(thien_can: TYPE_THIEN_CAN) -> TYPE_DIA_CHI:
    return MAP_THIEN_TRU[thien_can]

def get_thien_quan_position(thien_can: TYPE_THIEN_CAN) -> TYPE_DIA_CHI:
    return MAP_THIEN_QUAN[thien_can]

def get_thien_phuc_position(thien_can: TYPE_THIEN_CAN) -> TYPE_DIA_CHI:
    return MAP_THIEN_PHUC[thien_can]

def get_thien_khoi_position(thien_can: TYPE_THIEN_CAN) -> TYPE_DIA_CHI:
    return MAP_THIEN_KHOI[thien_can]

def get_thien_viet_position(thien_can: TYPE_THIEN_CAN) -> TYPE_DIA_CHI:
    return MAP_THIEN_VIET[thien_can]

def get_star_by_thien_can_position(thien_can: TYPE_THIEN_CAN, direction: Literal[1, -1]) -> list[tuple[str, TYPE_DIA_CHI]]:
    locton_position = get_loc_ton_position(thien_can)

    return [
        ("Lộc Tồn", locton_position),
        ("Bác Sĩ", get_bac_si_position(locton_position)),
        ("Kình Dương", get_kinh_duong_position(locton_position)),
        ("Thanh Long", get_thanh_long_position(locton_position)),
        ("Tiểu Hao", get_tieu_hao_position(locton_position)),
        ("LN Văn Tinh", get_ln_van_tinh_position(locton_position)),
        ("Tướng Quân", get_tuong_quan_position(locton_position)),
        ("Tấu Thư", get_tau_thu_position(locton_position)),
        ("Đường Phù", get_duong_phu_position(locton_position)),
        ("Phi Liêm", get_phi_liem_position(locton_position)),
        ("Hỷ Thần", get_hy_than_position(locton_position)),
        ("Bệnh Phù", get_benh_phu_position(locton_position)),
        ("Quốc Ấn", get_quoc_an_position(locton_position)),
        ("Đại Hao", get_dai_hao_position(locton_position)),
        ("Phục Binh", get_phuc_binh_position(locton_position)),
        ("Đà La", get_da_la_position(locton_position)),
        ("Quan Phủ", get_quan_phu_position(locton_position)),
        ("Lực Sĩ", get_luc_si_position(locton_position, direction)),
        ("Lưu Hà", get_luu_ha_position(thien_can)),
        ("Thiên Trù", get_thien_tru_position(thien_can)),
        ("Thiên Quan", get_thien_quan_position(thien_can)),
        ("Thiên Phúc", get_thien_phuc_position(thien_can)),
        ("Thiên Khôi", get_thien_khoi_position(thien_can)),
        ("Thiên Việt", get_thien_viet_position(thien_can)),
    ]
