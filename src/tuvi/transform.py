from typing import Tuple
from src.tuvi.element.types import LIST_DIA_CHI, TYPE_DIA_CHI


def get_xung_chieu(position : TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    return LIST_DIA_CHI[(LIST_DIA_CHI.index(position) + 6) % 12]

def get_nhi_hop(position : TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    index = LIST_DIA_CHI.index(position)

    return LIST_DIA_CHI[(13 - index) % 12]

def get_luc_hai(position : TYPE_DIA_CHI) -> TYPE_DIA_CHI:
    index = LIST_DIA_CHI.index(position)

    return LIST_DIA_CHI[(7 - index) % 12]

def get_tam_hop(position : TYPE_DIA_CHI) -> Tuple[TYPE_DIA_CHI, TYPE_DIA_CHI]:
    index = LIST_DIA_CHI.index(position)

    return LIST_DIA_CHI[(index + 4) % 12], LIST_DIA_CHI[(index - 4) % 12]
