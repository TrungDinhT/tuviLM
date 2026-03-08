from src.tuvi.element.types import LIST_DIA_CHI, TYPE_DIA_CHI
from .tool import get_position_by_move

def get_dia_khong_position(hour: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    birth_hour_index = LIST_DIA_CHI.index(hour)
    return get_position_by_move(11, birth_hour_index, -1)


def get_dia_kiep_position(hour: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    birth_hour_index = LIST_DIA_CHI.index(hour)
    return get_position_by_move(11, birth_hour_index, 1)


def get_van_xuong_position(hour: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    birth_hour_index = LIST_DIA_CHI.index(hour)
    return get_position_by_move(10, birth_hour_index, -1)


def get_van_khuc_position(hour: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    birth_hour_index = LIST_DIA_CHI.index(hour)
    return get_position_by_move(4, birth_hour_index, 1)


def get_an_quang_position(van_xuong_position: TYPE_DIA_CHI, date: int) -> TYPE_DIA_CHI:
    return get_position_by_move(van_xuong_position, date - 2, 1)


def get_thien_quy_position(van_khuc_position: TYPE_DIA_CHI, date: int) -> TYPE_DIA_CHI:
    return get_position_by_move(van_khuc_position, date - 2, -1)


def get_thai_phu_position(hour: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    birth_hour_index = LIST_DIA_CHI.index(hour)
    return get_position_by_move("Ngọ", birth_hour_index, 1)


def get_phong_cao_position(hour: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    birth_hour_index = LIST_DIA_CHI.index(hour)
    return get_position_by_move("Dần", birth_hour_index, 1)


def get_hour_star_positions(hour: TYPE_DIA_CHI, date: int) -> list[tuple[str, TYPE_DIA_CHI]]:
    van_xuong_position = get_van_xuong_position(hour)
    van_khuc_position = get_van_khuc_position(hour)

    an_quang_position = get_an_quang_position(van_xuong_position, date)
    thien_quy_position = get_thien_quy_position(van_khuc_position, date)

    return [
        ("Địa Không", get_dia_khong_position(hour)),
        ("Địa Kiếp", get_dia_kiep_position(hour)),
        ("Văn Xương", van_xuong_position),
        ("Văn Khúc", van_khuc_position),
        ("Ân Quang", an_quang_position),
        ("Thiên Quý", thien_quy_position),
        ("Thai Phụ", get_thai_phu_position(hour)),
        ("Phong Cáo", get_phong_cao_position(hour)),
    ]
