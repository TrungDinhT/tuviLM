import pydantic

from src.tuvi.element.base import Element
from src.tuvi.element.sao import ChinhTinh, PhuTinh
from src.tuvi.element.types import AM_DUONG, NGU_HANH, ROLE_TYPE, TYPE_DIA_CHI
from src.tuvi.element.trangsinh import TypeTrangSinh
from src.tuvi.element.tuhoa import TypeTuHoa

class Cung(pydantic.BaseModel):

    element : NGU_HANH | None = None

    sign : AM_DUONG

    role : ROLE_TYPE | None = None

    chinhTinh : list[ChinhTinh] = pydantic.Field(default_factory=list)

    phuTinh : list[PhuTinh] = pydantic.Field(default_factory=list)

    trang_sinh : TypeTrangSinh | None = None

    tuhoa : list[TypeTuHoa] = pydantic.Field(default_factory=list)

    is_tuan : bool = False

    is_triet : bool = False

    is_cung_than : bool = False

    dia_chi : TYPE_DIA_CHI | None = None

    thien_can : str = ""

    @property
    def all_element(self) -> list[Element]:
        elements: list[Element] = [*self.chinhTinh, *self.phuTinh, *self.tuhoa]
        if self.trang_sinh is not None:
            elements.append(self.trang_sinh)
        return elements

    def __repr__(self) -> str:
        role_str = self.role if self.role else "Unknown"
        if self.is_cung_than:
            role_str = f"{role_str} - Than"
        return f"Cung(role={role_str}, dia_chi={self.dia_chi})"
