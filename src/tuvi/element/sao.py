from src.tuvi.element.types import NGU_HANH, STAR_STATUS, TYPE_DIA_CHI
from src.tuvi.element.base import Element


class Sao(Element):

    description : str | None = None

    elemental : NGU_HANH

    def get_status(position : TYPE_DIA_CHI) -> STAR_STATUS:
        return None


class ChinhTinh(Sao):

    pass

class PhuTinh(Sao):

    pass
