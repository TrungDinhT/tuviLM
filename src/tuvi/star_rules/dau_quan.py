from src.tuvi.birth import TuviTime
from src.tuvi.element.types import TYPE_DIA_CHI, LIST_DIA_CHI
from .tool import get_position_by_move

def get_dau_quan_position(time: TuviTime) -> TYPE_DIA_CHI:
    month_position = get_position_by_move(time.dia_chi, time.month -1, -1)

    return get_position_by_move(month_position, LIST_DIA_CHI.index(time.hour), 1)
