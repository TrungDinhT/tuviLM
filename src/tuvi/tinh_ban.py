from typing import Literal
import pydantic

from src.tuvi.cung import Cung
from src.tuvi.birth import BirthTime
from src.tuvi.element.types import AM_DUONG, LIST_DIA_CHI, TYPE_DIA_CHI, TYPE_GENDER
from src.tuvi.cuc import Cuc

class TinhBan(pydantic.BaseModel):

    map_cung : dict[TYPE_DIA_CHI, Cung]

    cuc : Cuc | None = None

    direction : Literal[1, -1] | None = None

    gender : TYPE_GENDER | None = None

    am_duong : AM_DUONG | None = None

    cung_than : TYPE_DIA_CHI | None = None

    @classmethod
    def init_empty_plate(cls):

        return cls(
            map_cung={
                dia_chi : Cung(
                    sign="Am" if idx % 2 == 1 else "Duong"
                ) for idx, dia_chi in enumerate(LIST_DIA_CHI)}
        )

    @property
    def menh_position(self):
        for dia_chi, cung in self.map_cung.items():
            if cung.role == "Menh":
                return dia_chi

        raise ValueError("Non role tinh ban")
