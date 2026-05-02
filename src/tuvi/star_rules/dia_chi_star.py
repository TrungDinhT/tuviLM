from src.tuvi.element.types import LIST_DIA_CHI, TYPE_DIA_CHI
from src.tuvi.transform import get_xung_chieu
from .tool import get_position_by_move

def get_thien_hi_position(dia_chi: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    dia_chi_index = LIST_DIA_CHI.index(dia_chi)
    return get_position_by_move("Dậu", dia_chi_index, -1)


def get_hong_loan_position(dia_chi: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    thien_hi_position = get_thien_hi_position(dia_chi)
    return get_xung_chieu(thien_hi_position)


def get_giai_than_position(dia_chi: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    dia_chi_index = LIST_DIA_CHI.index(dia_chi)
    return get_position_by_move("Tuất", dia_chi_index, -1)


def get_thien_khoc_position(dia_chi: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    dia_chi_index = LIST_DIA_CHI.index(dia_chi)
    return get_position_by_move("Ngọ", dia_chi_index, -1)


def get_thien_ma_position(dia_chi: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    match LIST_DIA_CHI.index(dia_chi) % 4:
        case 0:
            return "Dần"
        case 1:
            return "Hợi"
        case 2:
            return "Thân"
        case 3:
            return "Tị"


def get_hoa_cai_position(dia_chi: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    match LIST_DIA_CHI.index(dia_chi) % 4:
        case 0:
            return "Thìn"
        case 1:
            return "Sửu"
        case 2:
            return "Tuất"
        case 3:
            return "Mùi"


def get_dao_hoa_position(dia_chi: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    match LIST_DIA_CHI.index(dia_chi) % 4:
        case 0:
            return "Dậu"
        case 1:
            return "Ngọ"
        case 2:
            return "Mão"
        case 3:
            return "Tý"


def get_kiep_sat_position(dia_chi: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    match LIST_DIA_CHI.index(dia_chi) % 4:
        case 0:
            return "Tị"
        case 1:
            return "Dần"
        case 2:
            return "Hợi"
        case 3:
            return "Thân"


def get_pha_toai_position(dia_chi: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    match LIST_DIA_CHI.index(dia_chi) % 3:
        case 0:
            return "Tị"
        case 1:
            return "Sửu"
        case 2:
            return "Dậu"

def get_phuong_cac_position(giai_than_position: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    return giai_than_position

def get_co_than_position(dia_chi: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    if dia_chi in ["Dần", "Mão", "Thìn"]:
        return "Tị"
    if dia_chi in ["Tị", "Ngọ", "Mùi"]:
        return "Thân"
    if dia_chi in ["Thân", "Dậu", "Tuất"]:
        return "Hợi"
    if dia_chi in ["Hợi", "Tý", "Sửu"]:
        return "Mùi"

def get_qua_tu_position(dia_chi: TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    if dia_chi in ["Dần", "Mão", "Thìn"]:
        return "Sửu"
    if dia_chi in ["Tị", "Ngọ", "Mùi"]:
        return "Thìn"
    if dia_chi in ["Thân", "Dậu", "Tuất"]:
        return "Dần"
    if dia_chi in ["Hợi", "Tý", "Sửu"]:
        return "Tuất"

def get_star_by_dia_chi_position(dia_chi: TYPE_DIA_CHI) -> list[tuple[str, TYPE_DIA_CHI]]:
    thien_hi_position = get_thien_hi_position(dia_chi)
    giai_than_position = get_giai_than_position(dia_chi)

    return [
        ("Thiên Hỉ", thien_hi_position),
        ("Hồng Loan", get_hong_loan_position(dia_chi)),
        ("Thiên Mã", get_thien_ma_position(dia_chi)),
        ("Giải Thần", giai_than_position),
        ("Phượng Các", get_phuong_cac_position(giai_than_position)),
        ("Phá Toái", get_pha_toai_position(dia_chi)),
        ("Hoa Cái", get_hoa_cai_position(dia_chi)),
        ("Đào Hoa", get_dao_hoa_position(dia_chi)),
        ("Thiên Khốc", get_thien_khoc_position(dia_chi)),
        ("Kiếp Sát", get_kiep_sat_position(dia_chi)),
        ("Cô Thần", get_co_than_position(dia_chi)),
        ("Quả Tú", get_qua_tu_position(dia_chi)),
    ]
