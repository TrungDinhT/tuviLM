from typing import Literal

from src.tuvi.birth import TuviTime
from src.tuvi.element.types import TYPE_DIA_CHI, LIST_DIA_CHI
from .hour_star import get_position_by_move


def get_linhtinh_position(time: TuviTime, direction: Literal[1, -1]) -> TYPE_DIA_CHI:
    index_diachi = LIST_DIA_CHI.index(time.dia_chi)
    hour_index = LIST_DIA_CHI.index(time.hour)

    # source : http://tuvi.cohoc.net/sao-linh-tinh-hoa-tinh-y-nghia-tai-menh-va-cung-khac-nid-6978.html
    match index_diachi % 4:
        case 0:
            linhtinh_cung_khoi = "Tuất"
        case 1:
            linhtinh_cung_khoi = "Tuất"
        case 2:
            linhtinh_cung_khoi = "Mão"
        case 3:
            linhtinh_cung_khoi = "Tuất"

    linhinh_position = get_position_by_move(linhtinh_cung_khoi, hour_index, (-1) * direction)
    return linhinh_position


def get_hoatinh_position(time: TuviTime, direction: Literal[1, -1]) -> TYPE_DIA_CHI:
    index_diachi = LIST_DIA_CHI.index(time.dia_chi)
    hour_index = LIST_DIA_CHI.index(time.hour)

    # source : http://tuvi.cohoc.net/sao-linh-tinh-hoa-tinh-y-nghia-tai-menh-va-cung-khac-nid-6978.html
    match index_diachi % 4:
        case 0:
            hoatinh_cung_khoi = "Dần"
        case 1:
            hoatinh_cung_khoi = "Mão"
        case 2:
            hoatinh_cung_khoi = "Sửu"
        case 3:
            hoatinh_cung_khoi = "Dậu"

    hoatinh_position = get_position_by_move(hoatinh_cung_khoi, hour_index , direction)
    return hoatinh_position
