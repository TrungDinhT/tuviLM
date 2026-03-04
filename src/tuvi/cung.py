import pydantic

from src.tuvi.element.base import Element
from src.tuvi.element.sao import ChinhTinh, PhuTinh
from src.tuvi.element.types import AM_DUONG, NGU_HANH, ROLE_TYPE, TYPE_DIA_CHI
from src.tuvi.element.trangsinh import TypeTrangSinh
from src.tuvi.element.tuhoa import TypeTuHoa

class Cung(pydantic.BaseModel):

    element : NGU_HANH | None = None
    "Ngũ hành của cung"

    sign : AM_DUONG
    "Âm hoặc Dương"

    role : ROLE_TYPE | None = None
    "Vai trò của cung, ví dụ: Mệnh, Phụ Mẫu, Phúc Đức,..."

    chinhTinh : list[ChinhTinh] = pydantic.Field(default_factory=list)
    "Danh sách chính tinh trong cung"

    phuTinh : list[PhuTinh] = pydantic.Field(default_factory=list)
    "Danh sách phụ tinh trong cung"

    trang_sinh : TypeTrangSinh | None = None
    "Trạng thái Tràng Sinh của cung"

    tuhoa : list[TypeTuHoa] = pydantic.Field(default_factory=list)
    "Danh sách Tứ Hỏa trong cung"

    is_tuan : bool = False
    "Cung có bị Tuần"

    is_triet : bool = False
    "Cung có bị Triệt"

    is_cung_than : bool = False
    "Cung có phải là Cung Thân"

    dia_chi : TYPE_DIA_CHI | None = None
    "Địa chi của cung"

    thien_can : str = ""
    "Thiên can của cung"

    age_daivan : int | None = None
    "Tuổi đại vận của cung"

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
        return f"Cung(role={role_str}, dia_chi={self.dia_chi}, age_daivan={self.age_daivan})"
