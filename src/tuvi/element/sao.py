from streamlit import status
from src.tuvi.element.types import NGU_HANH, STAR_STATUS, TYPE_DIA_CHI
from src.tuvi.element.base import Element
from .map_star_status import MAP_START_STATUS

class Sao(Element):

    description : str | None = None

    elemental : NGU_HANH

    def get_status(self, position : TYPE_DIA_CHI) -> STAR_STATUS:
        if self.name not in MAP_START_STATUS:
            return None
        return MAP_START_STATUS[self.name].get(position, None)

    def star_name_with_status(self, position : TYPE_DIA_CHI) -> str:
        if status := self.get_status(position):
            return f"{self.name} ({status})"
        return self.name


class ChinhTinh(Sao):

    pass

class PhuTinh(Sao):

    pass
