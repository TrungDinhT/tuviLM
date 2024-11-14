import pydantic

from src.tuvi.cung import Cung
from src.tuvi.birth import BirthTime
from src.tuvi.types import LIST_DIA_CHI, TYPE_DIA_CHI

class TinhBan(pydantic.BaseModel):

    map_cung : dict[TYPE_DIA_CHI, Cung]

    cuc : str | None = None

    @classmethod
    def from_birthtime(cls, birthTime : BirthTime):

        pass


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
