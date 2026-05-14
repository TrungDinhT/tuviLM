from src.tuvi.element.types import TYPE_DIA_CHI
from .tool import get_position_by_move


def get_ta_phu_position(month: int) -> TYPE_DIA_CHI:
    return get_position_by_move("Thìn", month - 1, 1)


def get_huu_bat_position(month: int) -> TYPE_DIA_CHI:
    return get_position_by_move("Tuất", month - 1, -1)


def get_tam_thai_position(ta_phu_position: TYPE_DIA_CHI, date: int) -> TYPE_DIA_CHI:
    return get_position_by_move(ta_phu_position, date - 1, 1)


def get_bat_toa_position(huu_bat_position: TYPE_DIA_CHI, date: int) -> TYPE_DIA_CHI:
    return get_position_by_move(huu_bat_position, date - 1, -1)


def get_thien_giai_position(month: int) -> TYPE_DIA_CHI:
    return get_position_by_move("Thân", month - 1, 1)


def get_dia_giai_position(month: int) -> TYPE_DIA_CHI:
    return get_position_by_move("Mùi", month - 1, 1)


def get_thien_hinh_position(month: int) -> TYPE_DIA_CHI:
    return get_position_by_move("Dậu", month - 1, 1)


def get_thien_dieu_position(month: int) -> TYPE_DIA_CHI:
    return get_position_by_move("Sửu", month - 1, 1)


def get_month_star_positions(month: int, date: int) -> list[tuple[str, TYPE_DIA_CHI]]:
    ta_phu_position = get_ta_phu_position(month)
    huu_bat_position = get_huu_bat_position(month)

    tam_thai_position = get_tam_thai_position(ta_phu_position, date)
    bat_toa_position = get_bat_toa_position(huu_bat_position, date)

    thien_giai_position = get_thien_giai_position(month)
    dia_giai_position = get_dia_giai_position(month)
    thien_hinh_position = get_thien_hinh_position(month)
    thien_dieu_position = get_thien_dieu_position(month)

    return [
        ("Tả Phù", ta_phu_position),
        ("Hữu Bật", huu_bat_position),
        ("Thiên Giải", thien_giai_position),
        ("Địa Giải", dia_giai_position),
        ("Thiên Hình", thien_hinh_position),
        ("Tam Thai", tam_thai_position),
        ("Bát Toạ", bat_toa_position),
        ("Thiên Diêu", thien_dieu_position),
        ("Thiên Y", thien_dieu_position),
    ]
