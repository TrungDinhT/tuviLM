from src.tuvi.element.types import LIST_DIA_CHI, TYPE_DIA_CHI
from src.tuvi.transform import get_luc_hai, get_nhi_hop, get_xung_chieu


def get_thien_phu_position(tuvi_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    tuvi_index = LIST_DIA_CHI.index(tuvi_position)
    thien_phu_index = (2 - (tuvi_index - 2)) % 12
    return LIST_DIA_CHI[thien_phu_index]


def get_thai_duong_position(thien_phu_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    return get_nhi_hop(thien_phu_position)


def get_vu_khuc_position(tuvi_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    tuvi_index = LIST_DIA_CHI.index(tuvi_position)
    return LIST_DIA_CHI[(tuvi_index - 4) % 12]


def get_liem_trinh_position(tuvi_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    tuvi_index = LIST_DIA_CHI.index(tuvi_position)
    return LIST_DIA_CHI[(tuvi_index + 4) % 12]


def get_that_sat_position(thien_phu_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    return get_xung_chieu(thien_phu_position)


def get_tham_lang_position(that_sat_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    that_sat_index = LIST_DIA_CHI.index(that_sat_position)
    return LIST_DIA_CHI[(that_sat_index - 4) % 12]


def get_pha_quan_position(that_sat_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    that_sat_index = LIST_DIA_CHI.index(that_sat_position)
    return LIST_DIA_CHI[(that_sat_index + 4) % 12]


def get_thien_dong_position(tham_lang_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    return get_nhi_hop(tham_lang_position)


def get_thien_co_position(pha_quan_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    return get_nhi_hop(pha_quan_position)


def get_thai_am_position(vu_khuc_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    return get_nhi_hop(vu_khuc_position)


def get_thien_luong_position(liem_trinh_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    return get_nhi_hop(liem_trinh_position)


def get_cu_mon_position(tuvi_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    return get_luc_hai(tuvi_position)


def get_thien_tuong_position(pha_quan_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    return get_xung_chieu(pha_quan_position)


def get_chinh_tinh_positions(tuvi_position: TYPE_DIA_CHI) -> list[tuple[str, TYPE_DIA_CHI]]:
    thien_phu_position = get_thien_phu_position(tuvi_position)
    thai_duong_position = get_thai_duong_position(thien_phu_position)
    vu_khuc_position = get_vu_khuc_position(tuvi_position)
    liem_trinh_position = get_liem_trinh_position(tuvi_position)

    that_sat_position = get_that_sat_position(thien_phu_position)
    tham_lang_position = get_tham_lang_position(that_sat_position)
    pha_quan_position = get_pha_quan_position(that_sat_position)

    thien_dong_position = get_thien_dong_position(tham_lang_position)
    thien_co_position = get_thien_co_position(pha_quan_position)
    thai_am_position = get_thai_am_position(vu_khuc_position)
    thien_luong_position = get_thien_luong_position(liem_trinh_position)

    cu_mon_position = get_cu_mon_position(tuvi_position)
    thien_tuong_position = get_thien_tuong_position(pha_quan_position)

    return [
        ("Tử Vi", tuvi_position),
        ("Thiên Phủ", thien_phu_position),
        ("Thái Dương", thai_duong_position),
        ("Vũ Khúc", vu_khuc_position),
        ("Liêm Trinh", liem_trinh_position),
        ("Thất Sát", that_sat_position),
        ("Tham Lang", tham_lang_position),
        ("Phá Quân", pha_quan_position),
        ("Thiên Đồng", thien_dong_position),
        ("Thiên Cơ", thien_co_position),
        ("Thái Âm", thai_am_position),
        ("Thiên Lương", thien_luong_position),
        ("Cự Môn", cu_mon_position),
        ("Thiên Tướng", thien_tuong_position),
    ]
