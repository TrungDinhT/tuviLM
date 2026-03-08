from src.tuvi.element.types import LIST_DIA_CHI, TYPE_DIA_CHI

def get_thai_tue_position(dia_chi: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    return dia_chi

def get_thieu_duong_position(thai_tue_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    thai_tue_index = LIST_DIA_CHI.index(thai_tue_position)
    return LIST_DIA_CHI[(thai_tue_index + 1) % 12]

def get_thien_khong_position(thai_tue_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    thai_tue_index = LIST_DIA_CHI.index(thai_tue_position)
    return LIST_DIA_CHI[(thai_tue_index + 1) % 12]

def get_tang_mon_position(thai_tue_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    thai_tue_index = LIST_DIA_CHI.index(thai_tue_position)
    return LIST_DIA_CHI[(thai_tue_index + 2) % 12]

def get_thieu_am_position(thai_tue_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    thai_tue_index = LIST_DIA_CHI.index(thai_tue_position)
    return LIST_DIA_CHI[(thai_tue_index + 3) % 12]

def get_quan_phu_position(thai_tue_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    thai_tue_index = LIST_DIA_CHI.index(thai_tue_position)
    return LIST_DIA_CHI[(thai_tue_index + 4) % 12]

def get_long_tri_position(thai_tue_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    thai_tue_index = LIST_DIA_CHI.index(thai_tue_position)
    return LIST_DIA_CHI[(thai_tue_index + 4) % 12]

def get_tu_phu_position(thai_tue_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    thai_tue_index = LIST_DIA_CHI.index(thai_tue_position)
    return LIST_DIA_CHI[(thai_tue_index + 5) % 12]

def get_nguyet_duc_position(thai_tue_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    thai_tue_index = LIST_DIA_CHI.index(thai_tue_position)
    return LIST_DIA_CHI[(thai_tue_index + 5) % 12]

def get_tue_pha_position(thai_tue_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    thai_tue_index = LIST_DIA_CHI.index(thai_tue_position)
    return LIST_DIA_CHI[(thai_tue_index + 6) % 12]

def get_thien_hu_position(thai_tue_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    thai_tue_index = LIST_DIA_CHI.index(thai_tue_position)
    return LIST_DIA_CHI[(thai_tue_index + 6) % 12]

def get_long_duc_position(thai_tue_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    thai_tue_index = LIST_DIA_CHI.index(thai_tue_position)
    return LIST_DIA_CHI[(thai_tue_index + 7) % 12]

def get_bach_ho_position(thai_tue_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    thai_tue_index = LIST_DIA_CHI.index(thai_tue_position)
    return LIST_DIA_CHI[(thai_tue_index + 8) % 12]

def get_phuc_duc_position(thai_tue_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    thai_tue_index = LIST_DIA_CHI.index(thai_tue_position)
    return LIST_DIA_CHI[(thai_tue_index + 9) % 12]

def get_thien_duc_position(thai_tue_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    thai_tue_index = LIST_DIA_CHI.index(thai_tue_position)
    return LIST_DIA_CHI[(thai_tue_index + 9) % 12]

def get_dieu_khach_position(thai_tue_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    thai_tue_index = LIST_DIA_CHI.index(thai_tue_position)
    return LIST_DIA_CHI[(thai_tue_index + 10) % 12]

def get_truc_phu_position(thai_tue_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    thai_tue_index = LIST_DIA_CHI.index(thai_tue_position)
    return LIST_DIA_CHI[(thai_tue_index + 11) % 12]

def get_vong_thai_tue_positions(
    dia_chi: TYPE_DIA_CHI
) -> list[tuple[str, TYPE_DIA_CHI]]:
    thai_tue_position = get_thai_tue_position(dia_chi)

    return [
        ("Thái Tuế", thai_tue_position),
        ("Thiếu Dương", get_thieu_duong_position(thai_tue_position)),
        ("Thiên Không", get_thien_khong_position(thai_tue_position)),
        ("Tang Môn", get_tang_mon_position(thai_tue_position)),
        ("Thiếu Âm", get_thieu_am_position(thai_tue_position)),
        ("Quan Phù", get_quan_phu_position(thai_tue_position)),
        ("Long Trì", get_long_tri_position(thai_tue_position)),
        ("Tử Phù", get_tu_phu_position(thai_tue_position)),
        ("Nguyệt Đức", get_nguyet_duc_position(thai_tue_position)),
        ("Tuế Phá", get_tue_pha_position(thai_tue_position)),
        ("Thiên Hư", get_thien_hu_position(thai_tue_position)),
        ("Long Đức", get_long_duc_position(thai_tue_position)),
        ("Bạch Hổ", get_bach_ho_position(thai_tue_position)),
        ("Phúc Đức", get_phuc_duc_position(thai_tue_position)),
        ("Thiên Đức", get_thien_duc_position(thai_tue_position)),
        ("Điếu Khách", get_dieu_khach_position(thai_tue_position)),
        ("Trực Phù", get_truc_phu_position(thai_tue_position))
    ]
