
from src.tuvi.element.types import NGU_HANH, STAR_STATUS, TYPE_DIA_CHI
from src.tuvi.element.base import Element
from .map_star_status import MAP_START_STATUS

STATUS_SHORT_LABEL: dict[str, str] = {
    "Hãm": "H",
    "Bình": "B",
    "Đắc": "D",
    "Vượng": "V",
    "Miếu": "M",
}


class Sao(Element):

    description : str | None = None

    elemental : NGU_HANH

    have_luu: bool = False

    def get_status(self, position : TYPE_DIA_CHI) -> STAR_STATUS:
        if self.name not in MAP_START_STATUS:
            return None
        return MAP_START_STATUS[self.name].get(position, None)

    def star_name_with_status(
        self,
        position : TYPE_DIA_CHI,
        with_short_name : bool = False
    ) -> str:
        if with_short_name:
            name_str = self.__str__()
        else:
            name_str = self.name

        if status := self.get_status(position):
            return f"{name_str} ({status})"
        return name_str

    def __str__(self):
        if self.short_names:
            return f"{self.name} (Thường được gọi là {', '.join(self.short_names)})"
        return self.name

class ChinhTinh(Sao):

    pass

class PhuTinh(Sao):

    pass
